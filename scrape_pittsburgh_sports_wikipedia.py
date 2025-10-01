import requests
from bs4 import BeautifulSoup, Tag
'''
Headers = {"User-Agent": "HW_Project/1.0 (+https://github.com/njasuja/11711_HW2; njasuja@andrew.cmu.edu)"}
url_dict = {"https://en.wikipedia.org/wiki/Pittsburgh_Pirates" : "wikipeda_pittsburgh_pirates",  "https://en.wikipedia.org/wiki/Pittsburgh_Steelers" : "wikipeda_pittsburgh_steelers", "https://en.wikipedia.org/wiki/Pittsburgh_Penguins":  "wikipeda_pittsburgh_penguins"}
for url in url_dict:
    response = requests.get(url, headers=Headers, timeout=20)
    html_content = response.text
    with open(f"{url_dict[url]}.html", "w", encoding="utf-8") as f:
        f.write(html_content)
'''
import re

_CITATION_PAT = re.compile(
    r"""
    \s*                           # optional leading whitespace
    \[                            # opening bracket
      \s*(
        \d+(?:\s*[--]\s*\d+)?     # a number, maybe a range like 12–14
        (?:\s*,\s*\d+)*           # optional list: , 15, 18
        (?:\s*;\s*\d+)*           # sometimes semicolons too
        |
        [a-z]                     # single letter citations like [a], [b]
        |
        citation\ needed          # [citation needed]
        |
        dead\ link                # [dead link]
        |
        broken\ link              # [broken link]
      )\s*
    \]                            # closing bracket
    """,
    re.IGNORECASE | re.VERBOSE
)
# Optional: remove empty leftover brackets like [] if they appear
_EMPTY_BRACKETS_PAT = re.compile(r'\s*\[\s*\]')

# Whitespace tidy (e.g., remove double spaces, space before commas/periods)
def _tidy_spaces(s: str) -> str:
    s = re.sub(r'\s{2,}', ' ', s)
    s = re.sub(r'\s+([,.;:?!])', r'\1', s)  # no space before punctuation
    return s.strip()

def _clean_citations(text: str) -> str:
    if not text:
        return text
    cleaned = _CITATION_PAT.sub('', text)
    cleaned = _EMPTY_BRACKETS_PAT.sub('', cleaned)
    return _tidy_spaces(cleaned)

def parse_sections(soup):
    sections = []
    content = soup.find('div', class_='mw-content-ltr mw-parser-output')
    if not content:
        return sections
    
    all_elements = content.find_all()
    heading_classes = ["mw-heading3", "mw-heading2"]
    skip_titles = ("references", "external links", "see also", "notes", "further reading", "bibliography", "primary sources")
    
    current_heading = None
    current_paragraphs = []
    for element in all_elements:
        element_classes = element.get('class', [])

        heading = False
        subheading = False
        for h in heading_classes:
            if element_classes is not None and h in element_classes:
                heading = True
            if element_classes is not None and "mw-heading4" in element_classes:
                subheading = True
        
        if heading:
            if current_heading is not None and not any(t in current_heading.lower() for t in skip_titles):
                sections.append({
                    'heading': current_heading,
                    'paragraphs': current_paragraphs
                })
            
            current_heading = element.get_text(strip=True).replace("[edit]", "")
            current_paragraphs = []
            
        elif element.name == 'p' and current_heading is not None:
            current_paragraphs.append(_clean_citations(element.get_text(" ", strip=True)))
        elif subheading and current_heading is not None:
            current_paragraphs.append(_clean_citations(element.get_text(strip=True).replace("[edit]", "")))
        elif element.name == 'figure' and current_heading is not None:
            continue
        elif element.name == 'table' and current_heading is not None:
            table_data = []
            rows = element.find_all('tr')
            
            for row in rows:
                headers = row.find_all('th')
                if headers:
                    table_data.append([_clean_citations(h.get_text(" ", strip=True)) for h in headers])
                
                cells = row.find_all('td')
                if cells:
                    table_data.append([_clean_citations(c.get_text(" ", strip=True)) for c in cells])
            
            if table_data:
                current_paragraphs.append(table_data)
        elif element.name in ['ul', 'ol'] and current_heading is not None:
            list_items = []
            items = element.find_all('li', recursive=False)
            
            for item in items:
                figures = item.find_all('figure')
                if figures:
                    continue
                else:
                    list_items.append(_clean_citations(item.get_text(" ", strip=True)))
            
            if list_items:
                current_paragraphs.append(list_items)

    if current_heading is not None and not any(t in current_heading.lower() for t in skip_titles):
        sections.append({
            'heading': current_heading,
            'paragraphs': current_paragraphs
        })
    
    return sections

files = ["wikipeda_pittsburgh_pirates", "wikipeda_pittsburgh_steelers", "wikipeda_pittsburgh_penguins"]
for file in files:
    with open(f"{file}.html", "r", encoding="utf-8") as f:
        response = f.read()

    soup = BeautifulSoup(response, 'html.parser')
    main_text = parse_sections(soup)
    with open(f"{file}.txt", "w", encoding="utf-8") as f:
        for sect in main_text:
            f.write(f"Title: {sect['heading']}\n")
            for para in sect['paragraphs']:
                f.write(f"{para}\n")
            f.write("\n")
