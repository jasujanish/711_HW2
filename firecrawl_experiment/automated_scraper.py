import os
import requests
import json
import time
from dotenv import load_dotenv
import random
import re
import sys
from firecrawl import Firecrawl
import markdown

LINKS_FILE = "links.txt"
OUTPUTS_DIR = "firecrawl_outputs"
load_dotenv()


def read_urls(filename):
    """
    Get's urls from links.txt
    """
    urls, seen = [], set()
    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            url = line.strip()
            if url and url not in seen:
                seen.add(url)
                urls.append(url)
    print(f"Successfully read {len(urls)} urls")
    return urls

def _markdown_to_text(md):
    """
    Markdown --> text
    """
    s = md

    # Remove code fences and inline code markers
    s = re.sub(r"```.*?```", "", s, flags=re.S)
    s = s.replace("`", "")

    # Images: ![alt](url) -> alt
    s = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", s)

    # Links: [text](url) -> text
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)

    # Headings/quotes/list markers
    s = re.sub(r"^\s{0,3}#{1,6}\s*", "", s, flags=re.M)
    s = re.sub(r"^\s*>\s?", "", s, flags=re.M)
    s = re.sub(r"^\s*([-*+]\s|\d+\.\s)", "", s, flags=re.M)

    # Emphasis
    s = s.replace("*", "").replace("_", "")

    # Collapse extra whitespace
    s = re.sub(r"[ \t]+\n", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()

def _markdown_to_text_2(md):
    """
    Markdown --> text using mardkown library
    """
    html = markdown.markdown(md)
    text = re.sub(r'<[^>]+>', '', html)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def add_semantic_chunks(md_content):
    """
    Splits markdown content into chunks with keyword jasujazumdinski
        1. A new section starts AND the current chunk has at least 200 words.
        2. The current chunk exceeds 800 words.
    """
    MIN_WORDS = 200
    MAX_WORDS = 800
    CHUNK_KEYWORD = "jasujazumdinski"
    
    final_chunks = []
    curr_chunk = []

    # Split by headings via regex
    sections = re.split(r'(^#{1,6}\s.*$)', md_content, flags=re.MULTILINE)
    if sections and not sections[0].strip():
        sections.pop(0)

    grouped_sections = []
    for i in range(0, len(sections), 2):
        if i + 1 < len(sections):
            grouped_sections.append(sections[i] + sections[i+1])
        else:
            grouped_sections.append(sections[i])

    for section in grouped_sections:
        # If the current chunk is not empty and min/max constraints are met --> finalize
        # Else --> append to curr chunk
        current_text = _markdown_to_text_2("".join(curr_chunk))
        current_word_count = len(current_text.split())
        if curr_chunk and (current_word_count >= MIN_WORDS or (current_word_count + len(section.split()) > MAX_WORDS)):
            final_chunks.append(f"{current_text}\n\n{CHUNK_KEYWORD}")
            curr_chunk = [section]
        else:
            curr_chunk.append(section)

    # get last chunk
    if curr_chunk:
        last_chunk_text = _markdown_to_text_2("".join(curr_chunk))
        final_chunks.append(f"{last_chunk_text}\n\n{CHUNK_KEYWORD}")
        
    return "\n".join(final_chunks)

def main():
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        print("set FIRECRAWL_API_KEY")
        return 1

    urls = read_urls(LINKS_FILE)
    if not urls:
        print("No URLs")
        return 1

    fc = Firecrawl(api_key=api_key)
    i = 0
    for url in urls:
        print(url)
        doc = fc.scrape(url, formats=["markdown"])
        print(doc)

        md = doc.markdown
        with open(f'{OUTPUTS_DIR}/markdown{i}.md', "w", encoding="utf-8") as f:
            f.write(md if md.endswith("\n") else md + "\n")
        text = _markdown_to_text(md).rstrip() + "\n"
        with open(f'{OUTPUTS_DIR}/text{i}.txt', "w", encoding="utf-8") as f:
            f.write(text)
        text_2 = add_semantic_chunks(md)
        with open(f'{OUTPUTS_DIR}/text_chunked{i}.txt', "w", encoding="utf-8") as f:
            f.write(text_2)
        time.sleep(random.uniform(1, 3))
        i+=1
    return 0

if __name__ == "__main__":
    main()
