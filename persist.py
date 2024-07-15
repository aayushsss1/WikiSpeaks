import os
import shutil
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
import time
from langchain_community.vectorstores.faiss import FAISS
from langchain.schema.document import Document
import numpy as np
from data_source import get_wikipedia_content

FAISS_INDEX_PATH = os.path.dirname(os.path.realpath(__file__)) + "/faiss_index"

db_shards = 5

def get_text_chunks_langchain(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    docs = [Document(page_content=x) for x in text_splitter.split_text(text)]
    return docs

def process_shard(shard):
    print(f'Starting process_shard of {len(shard)} chunks.')
    st = time.time()
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    result = FAISS.from_documents(shard, embeddings)
    et = time.time() - st
    print(f'Shard completed in {et} seconds.')
    return result

def persist_data(context):
    if os.path.exists(FAISS_INDEX_PATH):
      shutil.rmtree(FAISS_INDEX_PATH)
      print("Deleting FAISS Path")
   
    # Stage one: read all the docs, split them into chunks. 
    st = time.time() 
    page_content = get_wikipedia_content(context)
    print(page_content)
    chunks = get_text_chunks_langchain(page_content)
    et = time.time() - st
    print(f'Time taken: {et} seconds. {len(chunks)} chunks generated') 

    #Stage two: embed the docs. 
    print(f'Loading chunks into vector store ... using {db_shards} shards') 
    st = time.time()
    shards = np.array_split(chunks, db_shards)
    results = [process_shard(shards[i]) for i in range(db_shards)]
    et = time.time() - st
    print(f'Shard processing complete. Time taken: {et} seconds.')

    st = time.time()
    print('Merging shards ...')
    # Straight serial merge of others into results[0]
    db = results[0]
    for i in range(1, db_shards):
        db.merge_from(results[i])
    et = time.time() - st
    print(f'Merged in {et} seconds.') 

    st = time.time()
    print('Saving faiss index')
    db.save_local(FAISS_INDEX_PATH)
    et = time.time() - st
    print(f'Saved in: {et} seconds.')
    