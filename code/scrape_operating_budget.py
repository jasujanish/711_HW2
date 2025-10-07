import pdfplumber
import re
import pymupdf4llm
import markdown
def v1():
    pdf_path = "2025-operating-budget.pdf"
    output_path = "output_pdf1.txt"

    pages_text = []
    with pdfplumber.open(pdf_path) as pdf:
        i = 0
        for page in pdf.pages:
            t = page.extract_text() or ""
            t = re.sub(r"[ \t]+\n", "\n", t)
            t = re.sub(r"\n{3,}", "\n\n", t)
            pages_text.append(t.strip())
            i+=1
            print(f'page {i} done')
    text = "\n\n".join(pages_text)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text.strip())

def v2():
    pdf_path = "2025-operating-budget.pdf"
    output_path = "output_pdf2.txt"
    MAX_WORDS_PER_CHUNK = 600
    KEYWORD = "jasujazumdinski"
    pages_text = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            for i, page in enumerate(pdf.pages):
                t = page.extract_text(x_tolerance=1) or ""
                
                t = re.sub(r"[ \t]+\n", "\n", t)
                t = re.sub(r"\n{3,}", "\n\n", t)
                
                pages_text.append(t.strip())
                print(f'Page {i + 1}/{total_pages} processed.')

    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return

    full_text = "\n\n".join(pages_text)
    full_text = re.sub(r"\n{3,}", "\n\n", full_text).strip()

    paragraphs = full_text.split('\n\n')

    chunks = []
    current_chunk_paragraphs = []
    current_word_count = 0

    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        paragraph_word_count = len(paragraph.split())

        if current_word_count + paragraph_word_count > MAX_WORDS_PER_CHUNK and current_chunk_paragraphs:
            chunk_text = "\n\n".join(current_chunk_paragraphs)
            chunk_text += f" {KEYWORD}"
            chunks.append(chunk_text)

            current_chunk_paragraphs = [paragraph]
            current_word_count = paragraph_word_count
        else:
            current_chunk_paragraphs.append(paragraph)
            current_word_count += paragraph_word_count

    if current_chunk_paragraphs:
        chunk_text = "\n\n".join(current_chunk_paragraphs)
        chunk_text += f" {KEYWORD}"
        chunks.append(chunk_text)

    print(f"{len(chunks)} chunks")

    final_text = "\n\n".join(chunks)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_text)
    except Exception as e:
        print(f"Error: {e}")


def md_to_text(md):
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

    if not md_content or not md_content.strip():
        return ""

    # Get headers via regex
    heading_iter = list(re.finditer(r'(?m)^(#{1,6}\s.*)$', md_content))
    sections = []

    # Case 1: no headers, split on words
    if not heading_iter:
        words = md_content.split()
        for i in range(0, len(words), MAX_WORDS):
            chunk_md = " ".join(words[i:i + MAX_WORDS])
            sections.append(chunk_md)
    # Case 2: split into sections based on headers
    else:
        first_heading_start = heading_iter[0].start()
        if first_heading_start > 0:
            pre = md_content[:first_heading_start].strip()
            if pre:
                sections.append(pre)

        for idx, m in enumerate(heading_iter):
            start = m.start()
            end = heading_iter[idx + 1].start() if idx + 1 < len(heading_iter) else len(md_content)
            sec = md_content[start:end].strip()
            if sec:
                sections.append(sec)

    final_chunks = []
    curr_chunk_parts = []

    def finalize_current():
        if not curr_chunk_parts:
            return
        chunk_md = "\n\n".join(curr_chunk_parts).strip()
        if not chunk_md:
            return
        final_chunks.append(f"{chunk_md}\n\n{CHUNK_KEYWORD}")
        curr_chunk_parts.clear()
    
    # Group sections on min/max constraints
    for section in sections:
        section_text = md_to_text(section)
        section_words = len(section_text.split())

        curr_md = "\n\n".join(curr_chunk_parts) if curr_chunk_parts else ""
        curr_text = md_to_text(curr_md) if curr_md else ""
        curr_words = len(curr_text.split()) if curr_text else 0

        if not curr_chunk_parts:
            if section_words > MAX_WORDS:
                words = section.split()
                for i in range(0, len(words), MAX_WORDS):
                    subchunk = " ".join(words[i:i + MAX_WORDS])
                    final_chunks.append(f"{subchunk}\n\n{CHUNK_KEYWORD}")
                continue
            curr_chunk_parts.append(section)
            continue

        if curr_words >= MIN_WORDS:
            finalize_current()
            curr_chunk_parts.append(section)
            continue

        if curr_words + section_words > MAX_WORDS:
            finalize_current()
            curr_chunk_parts.append(section)
            continue

        curr_chunk_parts.append(section)

    # finalize what's left
    finalize_current()

    return "\n\n".join(final_chunks)

def v3():
    md_text = pymupdf4llm.to_markdown("2025-operating-budget.pdf")
    print('pymupdf scraping DONE')
    md_chunked = add_semantic_chunks(md_text)
    text_chunked = md_to_text(md_chunked)
    with open(f'output_pdf3.txt', "w", encoding="utf-8") as f:
        f.write(text_chunked)

if __name__ == "__main__":
    v2()
    v3()

