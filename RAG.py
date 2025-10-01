import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer
from typing import List, Tuple
import os
import re

embed_model = SentenceTransformer('sentence-transformer/all-MiniLM-L6-v2')

lm_model_name = "google/flan-t5-small"  # other options "t5-small" or "facebook/bart-base"
tokenizer = AutoTokenizer.from_pretrained(lm_model_name)
lm_model = AutoModelForSeq2SeqLM.from_pretrained(lm_model_name)
lm_model.eval() 

tokenizer.pad_token = tokenizer.eos_token

documents = []
#folder path needs to be path to folder containing all scraped .txt files
folder_path = '/path/to/folder/'
for filename in os.listdir(folder_path):
    if filename.endswith('.txt'):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            documents.append(text)


def chunk_text(text, chunk_size, overlap):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i+chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks

def semantic_chunk_text(text, chunk_size, overlap, keyword=None):
    if keyword:
        sub_docs = [s.strip() for s in re.split(re.escpae(keyword), text) if s.strip()]
    else:
        sub_docs = [text]
    chunks = []
    for sub_doc in sub_docs:
        words = sub_doc.split()
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i+chunk_size])
            if chunk:
                chunks.append(chunk)
    return chunks

all_chunks = []
c_size = 200
c_overlap = c_size // 10
c_keyword = 'jasujazmudzinski'
for doc in documents:
    chunks = semantic_chunk_text(doc, chunk_size = c_size, overlap = c_overlap, keyword = c_keyword)
    all_chunks.extend(chunks)

chunk_embeddings = embed_model.encode(all_chunks, prompt_name='query')

def dense_retrieve(query: str, mode: str = 'top', k: int = 3, threshold: float = 0.7, metric: str='cosine', normalize: bool = True) -> List[Tuple[str, float]]:
    query_embedding = embed_model.encode([query], prompt_name="query")[0]
    if normalize:
        query_embedding_norm = query_embedding / np.linalg.norm(query_embedding)
        chunk_embeddings_norm = chunk_embeddings / np.linalg.norm(chunk_embeddings, axis = 1, keepdims=True)
    else:
        chunk_embeddings_norm = chunk_embeddings
        query_embedding_norm = query_embedding
    if metric == 'cosine':
        scores = np.dot(chunk_embeddings_norm, query_embedding_norm)
    elif metric == 'euclidean':
        differences = chunk_embeddings_norm - query_embedding_norm
        scores = np.linalg.norm(differences, axis = 1)
    else:
        raise ValueError("metric must be 'cosine' or 'euclidean'")

    results: List[Tuple[str, float]] = []
    if mode == 'top':
        if metric == 'cosine':
            top_indices = np.argsort(scores)[-k:][::-1]
        else:
            top_indices = np.argsort(scores)[:k]
        results = [(all_chunks[i], scores[i]) for i in top_indices]
    
    elif mode == 'threshold':
        if metric == "cosine":
            indices = np.where(scores >= threshold)[0]
        else:  
            indices = np.where(scores <= threshold)[0]
        if metric == 'cosine':
            indices = indices[np.argsort(scores[indices])[::-1]]
        else:
            indices = indices[np.argsort(scores[indices])]
        results = [(all_chunks[i], scores[i]) for i in top_indices]
    else:
        raise ValueError("mode must be 'top' or 'threshold'")



#hybrid can use reranking after we rank once already