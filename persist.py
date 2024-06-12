import os
import shutil
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.document_loaders import TextLoader, DirectoryLoader
import time
from langchain.document_loaders.text import TextLoader
from langchain_community.vectorstores.faiss import FAISS
import numpy as np


def get_logs(folder_name):
    loader = DirectoryLoader(folder_name, glob="**/*.*", loader_cls=TextLoader, recursive=True, use_multithreading=True)
    sources = loader.load()
    source_chunks = []
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=250)
    source_chunks = splitter.split_documents(sources)
    print("Logs Successfully Read from File")
    return source_chunks

def process_shard(shard):
    print(f'Starting process_shard of {len(shard)} chunks.')
    st = time.time()
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    result = FAISS.from_documents(shard, embeddings)
    et = time.time() - st
    print(f'Shard completed in {et} seconds.')
    return result

def persist_data(folder_name,db_shards,FAISS_INDEX_PATH):
    if os.path.exists(FAISS_INDEX_PATH):
      shutil.rmtree(FAISS_INDEX_PATH)
      print("Deleting FAISS Path")
   
    # Stage one: read all the docs, split them into chunks. 
    st = time.time() 
    chunks = get_logs(folder_name)
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
    for i in range(1,db_shards):
        db.merge_from(results[i])
    et = time.time() - st
    print(f'Merged in {et} seconds.') 

    st = time.time()
    print('Saving faiss index')
    db.save_local(FAISS_INDEX_PATH)
    et = time.time() - st
    print(f'Saved in: {et} seconds.')
    