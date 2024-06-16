from ray import serve
import ray
from langchain.vectorstores import FAISS
from transformers import pipeline
import torch
import time
from kserve import Model, ModelServer
from langchain_community.embeddings import SentenceTransformerEmbeddings

@serve.deployment(name="qa-model", num_replicas=1)
class QADeployment(Model):
    def __init__(self):

        self.name = "qa-model"
        super().__init__(self.name)
        self.load()
    
    def load(self):
        # Load the data from faiss. No change from Part 1
        st = time.time()
        self.embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        self.db = FAISS.load_local("faiss_index_fast", self.embeddings, allow_dangerous_deserialization=True )
        et = time.time() - st

        print(f"Loading FAISS database took {et} seconds.")
        
        st = time.time()

        self.pipe = pipeline("text-generation", model="HuggingFaceH4/zephyr-7b-beta", torch_dtype=torch.bfloat16, device_map="auto")
       
        et = time.time() - st
        print(f"Loading HF model took {et} seconds.")
    

    def predict(self, question):
        retriever = self.db.as_retriever(search_kwargs={"k": 4}, search_type="mmr")
        context_docs = retriever.invoke(question)
        context = " ".join([doc.page_content for doc in context_docs])

        print(f"Results from db are: {context}")

        messages = [
        {
            "role": "system",
            "content": "You are an advanced Wikipedia Assistant, an information chatbot who has answers to every question. Now with the given context, your task is to answer with confident and great detail\n: ",
        },
        {"role": "user", "content": f'Question: {question}, context: {context}\n'},
        ]   

        prompt = self.pipe.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        outputs = self.pipe(prompt, max_new_tokens=256, do_sample=True, temperature=0.7, top_k=50, top_p=0.95)
        
        return {"predictions": outputs[0]["generated_text"]}


if __name__ == "__main__":
    ray.init(num_cpus=2, num_gpus=1)
    ModelServer().start([QADeployment()])