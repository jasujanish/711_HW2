import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer
from typing import List, Tuple
import os
import re
import faiss
import spacy
from rank_bm25 import BM25Okapi
import json
import shutil


embed_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

lm_model_name = "meta-llama/Llama-2-7b-chat"  
  
tokenizer = AutoTokenizer.from_pretrained(lm_model_name, use_fast=False, trust_remote_code =True)
lm_model = AutoModelForCausalLM.from_pretrained(lm_model_name, torch_dtype = torch.float32)
lm_model.eval() 

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

documents = []
#folder path needs to be path to folder containing all scraped .txt files
folder_path = 'text_outputs'
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

chunk_embeddings = embed_model.encode(all_chunks, convert_to_numpy=True)

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
    query_embedding = embed_model.encode([query], convert_to_numpy=True, normalize_embeddings=False).astype("float32")
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
bm25 = BM25Okapi(tokenized_corpus)

def BM25_rank_retrive(query: str, k: int = 5):
    doc = nlp(query.lower())
    tokenized_query = [token.lemma_ for token in doc if not token.is_punct and not token.is_space]
    scores = bm25.get_scores(tokenized_query)
    top_indices = np.argsort(scores)[::-1][:k]
    results = [(all_chunks[i], float(scores[i])) for i in top_indices]
    return results

def min_max_normalize(results):
    scores = np.array([score for _, score in results], dtype=float)
    min_s, max_s = scores.min(), scores.max()
    norm_scores = (scores-min_s) / (max_s - min_s)
    return [(doc, score) for (doc, _), score in zip(results, norm_scores)]

def max_normalize(results):
    scores = np.array([score for _, score in results], dtype=float)
    max_s = scores.max()
    norm_scores = scores / max_s
    return [(doc, score) for (doc, _), score in zip(results, norm_scores)]

def z_score_normalize(results):
    scores = np.array([score for _, score in results], dtype=float)
    mean_s = np.mean(scores)
    std_s = np.std(scores)
    norm_scores = (scores - mean_s) / std_s
    return [(doc, score) for (doc, _), score in zip(results, norm_scores)]

def rank_based_normalize(results):
    scores = np.array([score for _, score in results], dtype=float)
    ranks = np.argsort(np.argsort(scores))
    norm_scores = 1 - (ranks / (len(scores) - 1))
    return [(doc, score) for (doc, _), score in zip(results, norm_scores)]

#hybrid that normalizes first, we can esperiment with the noramlizer
def weighted_average_hybrid(query: str, top_k: int = 5, alpha: float = 0.5, dense_normalizer: str = "min-max", sparse_normalizer: str = "min-max"):
    dense_results = faiss_retrieve(query, k=top_k)
    sparse_results = BM25_rank_retrive(query, k=top_k)

    normalizers = {"min-max": min_max_normalize, "z-score": z_score_normalize, "rank": rank_based_normalize, "max": max_normalize}

    dense_results = normalizers[dense_normalizer](dense_results)
    sparse_results = normalizers[sparse_normalizer](sparse_results)

    all_docs = list(set([d for d, _ in dense_results] + [d for d, _ in sparse_results]))
    doc_idx = {doc: i for i, doc in enumerate(all_docs)}
    scores_dense = np.zeros(len(all_docs))
    scores_sparse = np.zeros(len(all_docs))

    for doc, score in dense_results:
        scores_dense[doc_idx[doc]] = score
    for doc, score in sparse_results:
        scores_sparse[doc_idx[doc]] = score
    combined_scores = alpha * scores_dense + (1 - alpha) * scores_sparse
    top_indices = np.argsort(combined_scores)[::-1][:top_k]
    return [(all_docs[i], combined_scores[i]) for i in top_indices]

def llama2_prompt(system_msg: str, user_msg: str) -> str:
    return f"<s>[INST] <<SYS>>\n{system_msg}\n<</SYS>>\n\n{user_msg} [/INST]"

def gpt2_prompt(system_msg: str, user_msg: str) -> str:
    return f"{system_msg}\n\nUser: {user_msg}\nAssistant:"

def qwen_prompt(system_msg: str, user_msg: str) -> str:
    return f"{system_msg}\n{user_msg}"

def generate_with_context(query: str, context_chunks: List[str], max_new_tokens: int = 100) -> str:
    context = "\n".join([f"- {chunk}" for chunk in context_chunks])
    system_msg = "You are a helpful assistant answering questions about Pittsburgh and Carnegie Mellon University (CMU). Use ONLY the provided context to answer questions. Be concise and accurate."
    user_msg = f"Here is some context:\n{context}\n\nQuestion: {query}\nAnswer:"
    prompt = llama2_prompt(system_msg, user_msg)
    inputs = tokenizer(prompt, return_tensors="pt").to(lm_model.device)

    with torch.no_grad():
        outputs = lm_model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.2,
            top_p=0.95,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    answer = response[len(prompt):].strip()
    return answer


def generate_without_context(query: str, max_new_tokens: int = 100) -> str:
    system_msg = "You are a helpful assistant. Be concise and accurate."
    user_msg = f"Question: {query}\nAnswer:"

    prompt = llama2_prompt(system_msg, user_msg)

    inputs = tokenizer(prompt, return_tensors="pt").to(lm_model.device)

    with torch.no_grad():
        outputs = lm_model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.5,
            top_p=0.95,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    answer = response[len(prompt):].strip()
    return answer

def rag(query: str, k: int = 3) -> str:
    #hybrid can take the additional arguements  alpha: float dense_normalizer: str sparse_normalizer: str
    results = weighted_average_hybrid(query, top_k=k)
    context_chunks = [chunk for chunk, _ in results]
    answer = generate_with_context(query, context_chunks)
    return answer, results

def non_rag(query: str) -> str:
    answer = generate_without_context(query)
    return answer

def evaluate_rag(q_file: str, a_file: str, rag_func):
    with open(q_file, 'r', encoding = 'utf-8') as f:
        questions = [line.strip() for line in f if line.strip()]

    with open(a_file, 'r', encoding ='utf-8') as f:
        answers = json.load(f)
    
    results = []

    for q in questions:
        rag_answer, chunks = rag_func(q, k=3)
    
        ref_answer = answers.get(q)
        #exact match, need to change to similarity
        rag_correct = answer_with_context.strip().lower() == ref_answer.strip().lower() if ref_answer else None

        results.append({"question":q, "reference": ref_answer, "rag_answer": rag_answer, "rag_correct": rag_correct, "chunks": chunks})

    total = len(results)
    rag_correct_count = sum(r['rag_correct'] for r in results if r['rag_correct'] is not None)
    print(f"RAG Accuracy: {rag_correct_count}/{total} = {rag_correct_count/total:.2f}")

    return results
'''
if __name__ == "__main__":
    query = "How much are the fees at Frick Pittsburgh?"
    answer, results = rag(query, k=3)

    for i, (chunk,score) in enumerate(results,1):
        print(f"{i}. {chunk[:100]}... (score={score:.4f})")

    print("\nAnswer (with context):")
    print(answer)

    print("\nAnswer (without context):")
    print(non_rag(query))
'''  

if __name__ == "__main__":
    questions_file = "questions_natan.txt"
    reference_file = "reference_answer_natan.json"
    results = evaluate_rag(questions_file, reference_file, rag_func=rag)


