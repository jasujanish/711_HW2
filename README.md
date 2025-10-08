The main file for this project is the ANLPHW2.ipynb. The notebook was ran on Colab using a T4 GPU and high RAM.
The cells are in logical order, starting with a github repo clone (all the scraped data and testing data is pulled in that way). Then necessary packages are installed.
The next cell loads the llama-3-8b-instruct model from Meta. This is a gated repo on huggingface that requires the user to agree to the Meta user agreement.
The next cell takes all the scraped text file and creates a list containing all of them.
That list of documents is then chunked. We wrote two chunking algorithms. The first was a basic chunking algorithm. The second we called 'semantic_chunk_text'. Our version of semantic chunk keeps the chunk from growing past the keyword 'jasujazmudzinski'.
During scraping, if we believed paragraphs within the same document talked about different ideas, we placed the keyword in between them so to embed distinct ideas in our chunks.
The next cell loads the sentence transformer model all-MiniLM-L6-v2, chunks the documents, and embeds them.
We used faiss for our dense retrieval, and set it up in the next cell.
For our sparse retrival we used spacy's en_core_web_sm to tokenize our corpus of chunks and BM25_rank_retrieve for sparse retreival.
We defined multiple different normalizers for expirementation purposes.
Our hybrid retrival system is a weighted average of the faiss and BM25, with the option to change how the results from each our normalized.
Next we have a generate with context cell and a generate without context cell.
The nexct two cells build the pipeline for both rag and non-rag query response.
The next cells are testing cells where we could test both the rag and non-rag on a single query or the rag system on the entire test set.
Additionally, there are two cleaning functions that prepare the answers as well as clean the answers.
