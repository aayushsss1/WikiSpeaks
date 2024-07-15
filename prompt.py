import os
from langchain_openai import OpenAI
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores.faiss import FAISS
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

SERVICE_HOSTNAME = os.environ["SERVICE_HOSTNAME"]
INGRESS_HOST = os.environ["INGRESS_HOST"]
INGRESS_PORT = os.environ["INGRESS_PORT"]
FAISS_INDEX_PATH = os.path.dirname(os.path.realpath(__file__)) + "/faiss_index"

PROMPT = '''
You are an advanced Wikipedia Assistant, an information chatbot who has answers to every question. Given the context answer the following - \n: 
Context: {context} \n
Question: {question}
'''

base_url = f"http://{INGRESS_HOST}:{INGRESS_PORT}/v1/"
api_key = "null"

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def prompt(question):

    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    # Load
    db = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True )

    retriever = db.as_retriever(search_kwargs={"k": 4}, search_type="mmr")

    client = OpenAI(
        base_url=base_url,
        api_key=api_key,
        default_headers={
            "Host": SERVICE_HOSTNAME,
        },
        model="meta-llama/Llama-2-7b-chat-hf",
        temperature=0.8,
        top_p=1,
    )
    
    qaprompt = PromptTemplate(input_variables=["context", "question"], template=PROMPT)

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | qaprompt
        | client
        | StrOutputParser()
    )

    return rag_chain.stream(question)