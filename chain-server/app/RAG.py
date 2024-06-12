from config import *
from utils import *
from langchain_community.document_loaders import WebBaseLoader
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_nvidia_trt.llms import TritonTensorRTLLM

import io

from contextlib import redirect_stdout
from langchain_huggingface import HuggingFaceEmbeddings


from operator import itemgetter
from typing import List, Dict, Tuple, Any

from fastapi import FastAPI
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate, format_document
from langchain_core.runnables import RunnableMap, RunnablePassthrough

from langserve.pydantic_v1 import BaseModel, Field


# User input
class ChatHistory(BaseModel):
    """Chat history with the bot."""

    chat_history: List[Tuple[str, str]] = Field(
        ...,
        extra={"widget": {"type": "chat", "input": "question"}},
    )
    question: str



triton_url = "localhost:8001"
pload = {
            'tokens':300,
            'server_url': triton_url,
            'model_name': "ensemble",
            'temperature':1.0,
            'top_k':1,
            'top_p':0,
            'beam_width':1,
            'repetition_penalty':1.0,
            'length_penalty':1.0
}
client = TritonTensorRTLLM(**pload)


text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20,add_start_index=True,separators=['\n\n', '\n', '(?<=\. )', ' ', ''])


model_name = "intfloat/multilingual-e5-base" #We take the multilingual too be sure to answer in french and english. Other possibility : intfloat/e5-large-v2"

model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}
hf = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

chroma_db_ext = Chroma(persist_directory=PERSISTENT_DIRECTORY, collection_name=COLLECTION_NAME_EXT,embedding_function=hf)
chroma_db_int = Chroma(persist_directory=PERSISTENT_DIRECTORY, collection_name=COLLECTION_NAME_INT,embedding_function=hf)

def deindexing_file(name: str, access: str):
        # Utilisez les métadonnées pour trouver les vecteurs associés et les supprimer
        collection = chroma_db_ext
        if access == "interne":
            collection = chroma_db_int
            
        # Get all documents in the collection
        db_data = collection.get()

        # Extract metadata
        metadatas = db_data['metadatas']
        ids = db_data['ids']

        # Find document IDs with matching filename
        ids_to_delete = [id for id, metadata in zip(ids, metadatas) if metadata.get('nom') == name]

        if ids_to_delete:
            # Delete the documents by IDs
            collection.delete(ids=ids_to_delete)
 
def deindexing_formation(name: str, access: str):
    collection = chroma_db_ext if access == 'externe' else chroma_db_int

    # Get all documents in the collection
    db_data = collection.get()

    # Extract metadata
    metadatas = db_data['metadatas']
    ids = db_data['ids']

    # Find document IDs with matching filename
    ids_to_delete = [id for id, metadata in zip(ids, metadatas) if metadata.get('nom') == name]

    if ids_to_delete:
        # Delete the documents by IDs
        collection.delete(ids=ids_to_delete)
            

def format_chat_history(chat_history: List[Tuple]) -> str:
    """Format chat history into a string."""
    buffer = ""
    for dialogue_turn in chat_history:
        human = "Human: " + dialogue_turn[0]
        ai = "orgAInize: " + dialogue_turn[1]
        buffer += "\n" + "\n".join([human, ai])
    return buffer


def format_docs_xml(docs: List[Document]) -> str:
    formatted = []
    for i, doc in enumerate(docs):
        metadata_str = ""
        for key, value in doc.metadata.items():
            # Convert the key to a valid XML tag name (e.g., replace spaces with underscores)
            tag = key.replace(" ", "_")
            metadata_str += f"<{tag}>{value}</{tag}>\n"
        
        doc_str = f"""\
        <source id="{i}">
            {metadata_str}
            <contenu>{doc.page_content}</contenu>
        </source>"""
        formatted.append(doc_str)
    return "\n<sources>" + "\n".join(formatted) + "</sources>\nWhen you use documents content to answer the question, provide as well the 'nom', the 'niveau_acces' and if possible the 'fichier_name' of each documents you used." if len(docs) > 0 else ""
 
def indexing_file(file_path: str, access: str, metadata: dict):
    text = pdf_to_text(file_path)
    text = "Document de nom :" + metadata['nom'] + text
    # Split
    all_splits = text_splitter.split_text(text)
    print(all_splits)

    # Add to persistent vectorDB Internal or External depending on access value
    if access == "interne":
        print("interne only")
        chroma_db_int.add_texts(all_splits, metadatas=[metadata]*len(all_splits))
    else:
        chroma_db_ext.add_texts(all_splits, metadatas=[metadata]*len(all_splits))

def indexing_formation(file_path: str,texte_formation: str, metadata: dict):
    syllabus_text = ""
    if file_path is not None :
        syllabus_text = pdf_to_text(temp_file_path)
    
    full_text = texte_formation + " " + syllabus_text
    chroma_db_ext.add_texts([full_text], metadatas=[metadata])

def get_answer(request: Dict[str, Any]) -> str:
    # Extract data from the request
    message = request['question']
    chat_history = request['chat_history']
    access = request['access']
         
    retriever = chroma_db_ext.as_retriever(search_type="similarity_score_threshold", search_kwargs={"k": 5, "score_threshold":0.75})
    
    external_context = {
            "external": itemgetter("standalone_question") | retriever | format_docs_xml,
            "question" : lambda x: x["standalone_question"],
            "internal" : lambda x: x.get("internal", ""),
    }
    
    inputs = RunnableMap(
        standalone_question=RunnablePassthrough.assign(
            chat_history=lambda x: format_chat_history(x["chat_history"])
        )
        | CONDENSE_QUESTION_PROMPT
        | client
        | StrOutputParser()
    )
    
    inputs_simple = RunnableMap(
        standalone_question=RunnablePassthrough.assign(
            chat_history=lambda x: format_chat_history(x["chat_history"])
        )
        | CONDENSE_QUESTION_PROMPT
    )

    if access == 'interne':
        retriever_int = chroma_db_int.as_retriever(search_type="similarity_score_threshold", search_kwargs={"k": 5, "score_threshold":0.75})
        
        
        internal_context = {
            "internal": itemgetter("standalone_question") | retriever_int | format_docs_xml,
            "standalone_question" : lambda x: x["standalone_question"],
        }

        conversational_qa_chain = (
            inputs
            | internal_context
            | external_context
            | ANSWER_PROMPT_PRO
            | client
            | StrOutputParser()
        )

        result_parallel = (
            inputs
            | internal_context
            | external_context
            | ANSWER_PROMPT_PRO
        )
    else:
        conversational_qa_chain = (
            inputs
            | external_context
            | ANSWER_PROMPT
            | client
            | StrOutputParser()
        )

        result_parallel = (
            inputs
            | external_context
            | ANSWER_PROMPT
        )
    
    chain = conversational_qa_chain.with_types(input_type=ChatHistory)
    
    f = io.StringIO()
    # Exécution de la chaîne RAG

    # Exécuter la partie de la chaîne jusqu'à LLAMA_PROMPT
    print("Simple requete : ")
    res1 = inputs_simple.invoke(request)
    print(res1)
    print("Standalone Question reformulé : ")
    result= inputs.invoke(request)

    print("Semi Full : ")
    result = result_parallel.invoke(request)
    print(result)



    #with redirect_stdout(f):
    result = chain.invoke(request)
    return result

def format_chat_history(chat_history: List[Dict[str, str]]) -> str:
    formatted_history = "\n".join([f"{msg['sender']}: {msg['text']}" for msg in chat_history])
    return formatted_history
    

    
#FOR DEBUGGING TEST
def make_simple_message(request : str) :

    retriever =  chroma_db_ext.as_retriever(search_type="similarity_score_threshold", search_kwargs={"k": 5, "score_threshold":0.7})

    LLAMA_PROMPT = PromptTemplate.from_template(LLAMA_PROMPT_TEMPLATE)


    # RAG chain
    chain = (
        RunnableParallel({"context":retriever, "question": RunnablePassthrough()})
        | LLAMA_PROMPT
        | client
        | StrOutputParser()
    )

    f = io.StringIO()
    
    # Exécution de la chaîne RAG
    with redirect_stdout(f):
        # Exécuter la partie de la chaîne jusqu'à LLAMA_PROMPT
        result_parallel = RunnableParallel({"context": retriever, "question": RunnablePassthrough()}) | LLAMA_PROMPT
        result = result_parallel.invoke(request)

    # Affichage du résultat de RunnableParallel | LLAMA_PROMPT
    print("Résultat de RunnableParallel | LLAMA_PROMPT :", result)


    with redirect_stdout(f):
        result = chain.invoke(request)
    print(result)
    return result



def check_working():
    print("Check work")
    indexing_file("/home/ciclarion/Bureau/workspace/documents_bigdata/EC09-MSII-BigData-LabsSession_Project_2.pdf","internal")
    print("Indexing done")
    make_simple_message("Qui est l'enseignant de Big Data ?")
    print("------Next Question -----")
    make_simple_message("Who is the Lecturer for Big Data ?")
    print("------Next Question -----")
    make_simple_message("Qu'est ce que le Survival Bias ?")
    print("------Next Question -----")
    make_simple_message("Pour le Lab session 3 de Big Data, partie Image Classfication. Quel est le dataset ?")
    
def whole_test():
    make_simple_message("Quand commence la formation DS8 ?")
    make_simple_message("Qui est l'enseignant de Big Data à l'Icam ?")
    make_simple_message("Pour le Lab session 3 de Big Data, partie Image Classfication. Quel est le dataset ?")
    make_simple_message("Quel est l'adresse de l'entreprise Chicken Root ?")
    make_simple_message("Quel est l'adresse de l'entreprise LLAM GOOD ?")


    db_data = chroma_db_ext.get()

    # Extract metadata
    metadatas = db_data['metadatas']
    ids = db_data['ids']

    # Display all source file names present in the collection
    print("Source file names present inside the collection:")
    source_file_names = set(metadata.get('nom') for metadata in metadatas)
    for source_file_name in source_file_names:
        print("- " + source_file_name)

    # Get the filename from the user
    filename = "invoice llam"

    # Find document IDs with matching filename
    ids_to_delete = [id for id, metadata in zip(ids, metadatas) if metadata.get('nom') == filename]


#whole_test()


