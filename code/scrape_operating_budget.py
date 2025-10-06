import pdfplumber
import re
import pymupdf

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
import pdfplumber
import re

def v2():
    """
    Main function to extract, clean, chunk, and save text from a PDF.
    """
    pdf_path = "2025-operating-budget.pdf"
    output_path = "output_pdf2.txt"
    MAX_WORDS_PER_CHUNK = 800
    KEYWORD = "jasujazumdinski"
    pages_text = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            for i, page in enumerate(pdf.pages):
                # Extract text from the page. x_tolerance helps with layout preservation.
                t = page.extract_text(x_tolerance=1) or ""
                
                # --- Text Cleaning ---
                # Remove extra spaces or tabs just before a newline
                t = re.sub(r"[ \t]+\n", "\n", t)
                # Collapse three or more newlines into exactly two
                t = re.sub(r"\n{3,}", "\n\n", t)
                
                pages_text.append(t.strip())
                print(f'Page {i + 1}/{total_pages} processed.')

    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return

    # --- Text Aggregation ---
    # Join all page texts into a single string, then perform a final cleanup.
    full_text = "\n\n".join(pages_text)
    full_text = re.sub(r"\n{3,}", "\n\n", full_text).strip()

    # --- Semantic Chunking ---
    # Split the text by paragraphs (approximated by double newlines).
    paragraphs = full_text.split('\n\n')

    chunks = []
    current_chunk_paragraphs = []
    current_word_count = 0

    print("\nStarting semantic chunking process...")

    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        # Skip empty paragraphs that might result from splitting
        if not paragraph:
            continue

        paragraph_word_count = len(paragraph.split())

        # If adding the current paragraph would exceed the word limit,
        # and the current chunk isn't empty, finalize the current chunk.
        if current_word_count + paragraph_word_count > MAX_WORDS_PER_CHUNK and current_chunk_paragraphs:
            # Join the collected paragraphs to form the chunk content.
            chunk_text = "\n\n".join(current_chunk_paragraphs)
            # Append the specified keyword.
            chunk_text += f" {KEYWORD}"
            chunks.append(chunk_text)

            # Start a new chunk with the current paragraph.
            current_chunk_paragraphs = [paragraph]
            current_word_count = paragraph_word_count
        else:
            # Otherwise, add the paragraph to the current chunk.
            current_chunk_paragraphs.append(paragraph)
            current_word_count += paragraph_word_count

    # Add the last remaining chunk after the loop finishes.
    if current_chunk_paragraphs:
        chunk_text = "\n\n".join(current_chunk_paragraphs)
        chunk_text += f" {KEYWORD}"
        chunks.append(chunk_text)

    print(f"Text divided into {len(chunks)} chunks.")

    # --- File Output ---
    # Join all processed chunks with a clear separator.
    final_text = "\n\n".join(chunks)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_text)
        print(f"\nSuccessfully saved chunked text to: {output_path}")
    except Exception as e:
        print(f"Error writing to output file: {e}")

def v3():
    pdf_path = "2025-operating-budget.pdf"
    output_path = "output_pdf3.txt"
    MAX_WORDS = 800
    KEYWORD = "jasujazumdinski"

    # Step 1: Extract text from PDF
    def extract_text_from_pdf(path):
        text_pages = []
        with pymupdf.open(path) as doc:
            for i, page in enumerate(doc):
                text = page.get_text("text")
                text_pages.append(text)
                print(f"Page {i+1}/{len(doc)} done")
        return "\n".join(text_pages)

    # Step 2: Clean text
    def clean_text(text):
        text = re.sub(r"[ \t]+\n", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"-\n", "", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    # Step 3: Chunk text semantically
    def chunk_text(text, max_words=MAX_WORDS, keyword=KEYWORD):
        paragraphs = re.split(r"\n{2,}", text)
        chunks, current_chunk = [], []
        word_count = 0

        def flush():
            if current_chunk:
                chunks.append(" ".join(current_chunk).strip() + f"\n\n{keyword}\n\n")

        for para in paragraphs:
            words = para.split()
            if not words:
                continue
            if word_count + len(words) > max_words:
                flush()
                current_chunk, word_count = [], 0
            current_chunk.append(para)
            word_count += len(words)
        flush()
        return chunks

    # --- Run pipeline ---
    raw_text = extract_text_from_pdf(pdf_path)
    cleaned = clean_text(raw_text)
    chunks = chunk_text(cleaned)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(chunks))

    print(f"Processed paragraphs: {len(re.split(r'\\n{2,}', cleaned))}")
    print(f"Generated chunks: {len(chunks)}")
    print(f"Output saved to {output_path}")

if __name__ == "__main__":
    v3()
