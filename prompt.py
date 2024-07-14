import os
from langchain_openai import OpenAI
from langchain_community.retrievers import WikipediaRetriever
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate

SERVICE_HOSTNAME = os.environ["SERVICE_HOSTNAME"]
INGRESS_HOST = os.environ["INGRESS_HOST"]
INGRESS_PORT = os.environ["INGRESS_PORT"]
FAISS_INDEX_PATH = os.path.dirname(os.path.realpath(__file__)) + "/faiss_index_fast"

PROMPT = '''
You are an advanced Wikipedia Assistant, an information chatbot who has answers to every question. Now with the given context, your task is to answer the question with confident and great detail\n: 
Context: {context} \n
Question: {question}
'''

base_url = f"http://{INGRESS_HOST}:{INGRESS_PORT}/v1/"
api_key = "null"

def prompt(question):

    retriever = WikipediaRetriever(top_k_results = 1)

    client = OpenAI(
        base_url=base_url,
        api_key=api_key,
        default_headers={
            "Host": SERVICE_HOSTNAME,
        },
        model="meta-llama/Llama-2-7b-chat-hf",
        temperature=0.4,
        top_p=1
    )
    
    qaprompt = PromptTemplate(input_variables=["context", "question"], template=PROMPT)

    qa = RetrievalQA.from_chain_type(llm=client, chain_type="stuff", retriever=retriever, chain_type_kwargs={'prompt': qaprompt})

    answer = qa.invoke(question)

    return answer["result"]