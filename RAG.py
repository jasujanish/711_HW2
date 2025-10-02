import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer
from typing import List, Tuple
import os
import re
import faiss
import spacy
from rank_bm25 import BM250kapi

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
        sub_docs = [s.strip() for s in re.split(re.escape(keyword), text) if s.strip()]
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

#dense retrieval function
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
        results = [(all_chunks[i], scores[i]) for i in indices]
    else:
        raise ValueError("mode must be 'top' or 'threshold'")
    return results

#matrix required for FAISS
xb = np.array(chunk_embeddings, dtype=np.float32)
d = xb.shape[1]
#normalize for cosine sim
faiss.normalize_L2(xb)
index = faiss.IndexFlatIP(d)
index.add(xb)

def faiss_retrieve(query: str, mode: str = 'top', k: int =3, threshold: float = 0.7):
    query_embedding = embed_model.encode([query], prompt_name="query").astype("float32")
    faiss.normalize_L2(query_embedding)
    scores, indices = index.search(query_embedding, k)
    if mode == 'top':
        results = [(all_chunks[i], float(scores[0][j])) for j, i in enumerate(indices[0])]
    
    elif mode == 'threshold':
        #we can adjust max_k based off of data set size
        max_k = min(len(all_chunks), 1000)
        scores, indices = index.search(query_embedding, max_k)
        mask = scores[0] >= threshold
        results = [(all_chunks[i], float(s)) for i, s in zip(indices[0][mask], scores[0][mask])]

    else:
        raise ValueError("mode must be 'top' or 'threshold'")

    return results

nlp = spacy.load("en_core_web_sm")

tokenized_corpus = [[token.lemma_.lower() for token in nlp(doc) if not token.is_punct and not token.is_space] for doc in all_chunks]
bm25 = BM250kapi(tokenized_corpus)

def BM25_rank_retrive(query: str, k: int = 5):
    doc = nlp(query.lower())
    tokenized_query = [token.lemma_ for token in doc if not token.is_punct and not token.is_space]
    scores = bm25.get_scores(tokenized_query)
    top_indices = np.argsort(scores)[::-1][:k]
    results = [(all_chunks[i], float(scores[i])) for i in top_indices]
    return results

#hybrid can use reranking after we rank once already