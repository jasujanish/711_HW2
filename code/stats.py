import os
import numpy as np

directory = "text_outputs"
files = [f for f in os.listdir(directory) if f.endswith(".txt")]
word_counts = []

for file in files:
    with open(os.path.join(directory, file), "r", encoding="utf-8") as f:
        text = f.read()
        word_counts.append(len(text.split()))

total_words = sum(word_counts)
print("Total word count:", total_words)
print("File count:", len(word_counts))
print("Mean:", np.mean(word_counts))
print("Median:", np.median(word_counts))
print("Min:", np.min(word_counts))
print("Max:", np.max(word_counts))