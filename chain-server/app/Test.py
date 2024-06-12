from config import *
from utils import *
from langchain_community.chat_models import ChatOllama
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_nvidia_trt.llms import TritonTensorRTLLM
import time
import random
import numpy as np

uint32_value = np.uint32(1)  # Une valeur au-dessus de l'int32 positif maximum
int32_value = uint32_value.astype(np.int32)


triton_url = "localhost:8001"
pload = {
            'tokens':300,
            'server_url': triton_url,
            'model_name': "ensemble",
            'temperature':1.0,
            'top_k':1.0,
            'top_p':0,
            'beam_width':1,
            'repetition_penalty':1.0,
            'length_penalty':1.0
}
llm = TritonTensorRTLLM(**pload)
res = llm.invoke("HI")



  
LLAMA_PROMPT_TEMPLATE = (
 "<s>[INST] <<SYS>>"
 "{system_prompt}"
 "<</SYS>>"
 "[/INST] {context} </s><s>[INST] {question} [/INST]"
)
system_prompt = "You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. Please ensure that your responses are positive in nature."
context=""
question='What is the fastest land animal?'
prompt = LLAMA_PROMPT_TEMPLATE.format(system_prompt=system_prompt, context=context, question=question)


    
start_time = time.time()
tokens_generated = 0


for val in client.stream(prompt):
    tokens_generated += 1
    print(val, end="", flush=True)

total_time = time.time() - start_time
print(f"\n--- Generated {tokens_generated} tokens in {total_time} seconds ---")
print(f"--- {tokens_generated/total_time} tokens/sec")


pour debug 

# Wrapper pour capturer et afficher le rendu
class PromptTemplateWrapper:
    def __init__(self, prompt_template):
        self.prompt_template = prompt_template

    def __call__(self, inputs):
        rendered_prompt = self.prompt_template.format(**inputs)
        # Afficher le rendu
        print("Rendered Prompt:")
        print(rendered_prompt)
        # Retourner le rendu pour la chaîne
        return rendered_prompt


def _make_message(request : str) :

    retriever =  chroma_db.as_retriever(search_type="similarity_score_threshold", search_kwargs={"k": 5, "score_threshold":0.6})

    LLAMA_PROMPT = PromptTemplate.from_template(LLAMA_PROMPT_TEMPLATE)


    # RAG chain
    chain = (
        RunnableParallel({"context":retriever, "question": RunnablePassthrough()})
        | PromptTemplateWrapper(LLAMA_PROMPT)
        | client
        | StrOutputParser()
    )
