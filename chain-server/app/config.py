from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

PERSISTENT_DIRECTORY = 'chrome_db'
COLLECTION_NAME_EXT = 'chroma_external_content'
COLLECTION_NAME_INT = 'chroma_internal_content'

#Simple LLAMA PROMPT FOR DEBUGGING TEST
LLAMA_PROMPT_TEMPLATE = (
 "<s>[INST] <<SYS>>"
 "Use and stick only to the following context to answer the user's question and nothing else. If you don't know the answer, just say that you don't know, don't try to make up an answer."
 "<</SYS>>"
 "[/INST] {context} </s><s>[INST] {question} Only return the helpful answer below and nothing else. Answer in the same language as the one use in the question. Helpful answer: [/INST]"
)

QUESTION_TEMPLATE= """Given the following conversation and a follow up message, rephrase the follow up message to be a standalone message in its original language.  Provide directly and only the standalone message. Do not add any more text. Do not make any repetition. Do not try to continue the conversation. Be concise. Do not add '\n' after your answer. Remember, the standalone message must be a rephrasing of the follow up message based on the conversation. Do not change the meaning of the message, it should be the same in the follow up and the standalone.

Conversation :
{chat_history}

Follow Up Message: {question}

The standalone message is : """


QUESTION_TEMPLATE_FIRST_VERSION = """Given the following conversation and a follow up message, rephrase the follow up message to be a standalone message, in its original language.  Provide directly and only the standalone message. Do not add any more text. Do not make any repetition. Do not try to continue the conversation. Remember, the standalone message must be a rephrasing of the follow up message based on the conversation.

Conversation :
{chat_history}

Follow Up Message: {question}

The standalone message is : """
CONDENSE_QUESTION_PROMPT = ChatPromptTemplate.from_template(QUESTION_TEMPLATE)


ANSWER_TEMPLATE = """You're a helpful AI assistant named orgAInize. Given a question and some external documents content, answer the question in its original language. Use and stick only to this prompt and the documents contents.  If none of the documents content or this prompt answer the question, just say that you don't know, in the question original language, don't try to make up an answer.

External Documents content:
{external}

Question: {question}

Only return  the helpful answer below, and nothing else. Answer in the same language as the one use in the question.

"""
ANSWER_PROMPT = ChatPromptTemplate.from_template(ANSWER_TEMPLATE)


ANSWER_TEMPLATE_PRO = """You're a helpful AI assistant named orgAInize. Given a question, some internal documents content and some external documents content, answer the question in its original language. Use and stick only to this prompt and the documents contents.  If none of the documents content or this prompt answer the question, just say that you don't know, in the question original language, don't try to make up an answer.

Internal Documents content:
{internal}

External Documents content:
{external}

Question: {question}

Only return  the helpful answer below, and nothing else. Answer in the same language as the one use in the question.

"""
ANSWER_PROMPT_PRO = ChatPromptTemplate.from_template(ANSWER_TEMPLATE_PRO)



