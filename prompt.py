
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from transformers import AutoTokenizer, pipeline
from langchain_huggingface.llms import HuggingFacePipeline
from langchain_community.vectorstores.faiss import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
import os
import torch

FAISS_INDEX_PATH = os.path.dirname(os.path.realpath(__file__)) + "/faiss_index_fast"

PROMPT = '''
You are an advanced Wikipedia Assistant, an information chatbot who has answers to every question. Now with the given context, your task is to answer the question with confident and great detail\n: 
Context: {context} \n
Question: {question}
'''

def prompt(question):

    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    db = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True )
    retriever = db.as_retriever(search_kwargs={"k": 4}, search_type="mmr")
    context_docs = retriever.invoke(question)

    context = " ".join([doc.page_content for doc in context_docs])
    
    pipe = pipeline("text-generation", model="HuggingFaceH4/zephyr-7b-beta", torch_dtype=torch.bfloat16, device_map="auto")

    messages = [
    {
        "role": "system",
        "content": "You are an advanced Wikipedia Assistant, an information chatbot who has answers to every question. Now with the given context, your task is to answer with confident and great detail\n: ",
    },
    {"role": "user", "content": f'Question: {question}, context: {context}\n'},
    ]   

    prompt = pipe.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    outputs = pipe(prompt, max_new_tokens=256, do_sample=True, temperature=0.7, top_k=50, top_p=0.95)

    return outputs[0]["generated_text"]