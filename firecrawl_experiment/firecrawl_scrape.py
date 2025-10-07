from firecrawl import Firecrawl
import os
from dotenv import load_dotenv
import time
import markdown
import re 
import html
load_dotenv()

def read_urls(filename):
    """
    Get's urls from filename
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

# Bad Patterns, to remove
LINE_JUNK_PATTERNS= [
    r"^\s*Skip to main content\s*$",
    r"^\s*instagram\s*$",
    r"^\s*facebook\s*$",
    r"^\s*view profile\s*$",
    r"^\s*view more on instagram\s*$",
    r"^\s*visit instagram\s*$",
    r"^\s*open in app\s*$",
    r"^\s*like\s+comment\s+share\s+save\s*$",
    r"^\s*add a comment.*$",
    r"^\s*this site uses cookies.*$",
    r"^\s*accept\s*$",
    r"^\s*about \d+\s+years? ago\s*$",
    r"^\s*\d{1,3}(?:,\d{3})*\s+posts\s+·\s+\d{1,3}(?:,\d{3})*\s+followers\s*$",
    r"^\s*\d+\s+likes\s*$",
    r"^\s*view more\s*$",
    r"^\s*show more\s*$",
    r"^\s*show less\s*$",
    r"^\s*author\s*$",
    r"^\s*enthusiastic pittsburgher\s*$",
    r"^\s*walters_pgh\s*$",
    r"^\s*wilsons_bbq412\s*$",
    r"^\s*asyayanyo\s*$",
    r"^\s*mitchsbbq\s*$",
    r"^\s*cobrapgh\s*$",
    r"^\s*yelppittsburgh\s*$",
    r"^\s*table of contents\s*$",
    r"^\s*privacy policy.*$",
    r"^\s*subscribe.*$",
    r"^\s*sign in.*$",
    r"^\s*sign up.*$",
]

INLINE_JUNK_PATTERNS = [
    r"\b\|\s*---\s*\|\s*---\s*\|\s*---\s*\|",  
    r"&nbsp;",
    r"\bLike Comment Share Save\b",
    r"\bView more on Instagram\b",
    r"\bOpen in Instagram\b",
    r"\bOpen in Facebook\b",
    r"\bThe link to this photo or video may be broken.*",
]

BLOCK_JUNK_PATTERNS = [
    (r"^\s*instagram\s*$", r"^\s*$"),
    (r"^\s*facebook\s*$", r"^\s*$"),
    (r"^\s*\|\s*.*\|\s*$", r"^\s*$"),
]

# Cleaner functions for firecrawl data
def unescape_and_normalize(text: str) -> str:
    s = html.unescape(text)
    s = s.replace("\u200b", "")  
    s = re.sub(r"\\\s*\\\s*", "\n", s)
    s = re.sub(r"\s+\n", "\n", s)
    return s

def remove_block_junk(lines):
    keep = [True] * len(lines)
    for start_pat, end_pat in BLOCK_JUNK_PATTERNS:
        start_re = re.compile(start_pat, flags=re.I)
        end_re   = re.compile(end_pat,   flags=re.I)
        i = 0
        while i < len(lines):
            if keep[i] and start_re.search(lines[i]):
                j = i
                found_end = False
                j += 1
                while j < len(lines):
                    if end_re.search(lines[j]):
                        found_end = True
                        keep[j] = False
                        break
                    keep[j] = False
                    j += 1
                keep[i] = False
                i = j + 1 if found_end else j
            else:
                i += 1
    return [ln for ln, k in zip(lines, keep) if k]

def remove_line_junk(lines):
    compiled = [re.compile(p, flags=re.I) for p in LINE_JUNK_PATTERNS]
    out = []
    for ln in lines:
        stripped = ln.strip()
        if any(rx.search(stripped) for rx in compiled):
            continue
        if stripped.startswith("|") or re.fullmatch(r"^-{3,}$", stripped):
            continue
        if stripped.lower() in {"instagram", "facebook"}:
            continue
        out.append(ln)
    return out

def remove_inline_junk(text: str) -> str:
    for pat in INLINE_JUNK_PATTERNS:
        text = re.sub(pat, "", text, flags=re.I)
    return text

def collapse_noise(text: str) -> str:
    lines = text.splitlines()
    dedup = []
    prev = None
    for ln in lines:
        if prev is not None and ln.strip() == prev.strip():
            continue
        dedup.append(ln)
        prev = ln
    s = "\n".join(dedup)
    s = re.sub(r"\n{3,}", "\n\n", s)
    s = "\n".join([ln for ln in s.splitlines() if not re.fullmatch(r"[\|\-\s]{1,}$", ln)])
    return s.strip()

def clean_text(text: str) -> str:
    s = unescape_and_normalize(text)
    s = remove_inline_junk(s)
    lines = s.splitlines()
    lines = remove_block_junk(lines)
    lines = remove_line_junk(lines)
    s = "\n".join(lines)
    s = remove_inline_junk(s) 
    s = collapse_noise(s)
    return s

if __name__ == '__main__':
    # section 1, scrape md files with firecrawl
    scrape_md = False
    if scrape_md:
        input_path = "firecrawl_inputs/inputs.txt"
        outputs_dir = "firecrawl_scrape_outputs"
        file_paths = read_urls(input_path)
        curr_key = 0
        # Rotate through API keys to avoid rate limiting
        api_key_list = ["FIRECRAWL_API_KEY_2","FIRECRAWL_API_KEY_3","FIRECRAWL_API_KEY_4","FIRECRAWL_API_KEY_5","FIRECRAWL_API_KEY_6"]
        for i in range(813, 2000):
            if(i%7 == 0):
                curr_key+=1
                curr_key%=len(api_key_list)
            api_key = os.getenv(api_key_list[curr_key])
            fc = Firecrawl(api_key=api_key)

            url = file_paths[i]
            print(f'{i}: {url}', end= " ")
            doc = fc.scrape(url, formats=["markdown"])
            md = doc.markdown
            print('(:')
            start = ""
            if url.startswith("https://www.cmu.edu"):
                start+="cmu"
            elif url.startswith("https://www.pittsburghpa"):
                start+="pittsburghpagov"
            elif url.startswith("https://www.visitpittsburgh"):
                start+="visitpittsburgh"
            else:
                start+="museum"
            with open(f'{outputs_dir}/{start}_{i}.md', "w", encoding="utf-8") as f:
                f.write(md if md.endswith("\n") else md + "\n")
                time.sleep(1)
    # section 2: clean up the md files, output txt files
    process_md = False
    if process_md:
        input_path = "firecrawl_scrape_outputs"
        outputs_dir = "firecrawl_text_outputs"
        file_paths = sorted(os.listdir(input_path))
        for i in range((len(file_paths))):
            path = os.path.join(input_path, file_paths[i])
            with open(path, "r", encoding="utf-8") as file:
                md = file.read()
                md_chunked = add_semantic_chunks(md)
                text_chunked = md_to_text(md_chunked)

                text_clean = text_chunked.replace('''|     |     |
| --- | --- |
|  |  |''', "")
            name = file_paths[i][:-3]
            with open(os.path.join(outputs_dir, f'{name}.txt'), 'w') as f:
                f.write(text_clean)
                print(f'{name}.txt')
            text_regex = clean_text(text_clean)
            with open(os.path.join(outputs_dir, f'{name}_regex.txt'), 'w') as f:
                f.write(text_regex)
                print(f'{name}.txt')
    # section 3: aggregate txt files into one final output file
    aggregate_txt = True
    if aggregate_txt:
        input_dir = "firecrawl_text_outputs"
        file_paths = sorted(os.listdir(input_dir))
        file_paths = [f for f in file_paths if f.endswith('regex.txt')]
        with open('firecrawl.txt', 'w') as file:
            for f in file_paths:
                with open(os.path.join(input_dir, f), 'r') as f:
                    file.write(f.read())
                    file.write('\n')



