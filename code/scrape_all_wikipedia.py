import requests
from bs4 import BeautifulSoup, Tag
import re
import os

urls = ["https://en.wikipedia.org/wiki/List_of_Carnegie_Mellon_University_people", "https://en.wikipedia.org/wiki/Carnegie_Mellon_University", "https://en.wikipedia.org/wiki/Carnegie_Mellon_College_of_Fine_Arts", "https://en.wikipedia.org/wiki/Carnegie_Mellon_CyLab", "https://en.wikipedia.org/wiki/Carnegie_Mellon_School_of_Art", "https://en.wikipedia.org/wiki/Carnegie_Mellon_School_of_Computer_Science", "https://en.wikipedia.org/wiki/Carnegie_Mellon_School_of_Drama", "https://en.wikipedia.org/wiki/Carnegie_Mellon_University_Computational_Biology_Department", "https://en.wikipedia.org/wiki/Carnegie_Mellon_University_Usable_Privacy_and_Security_Laboratory", "https://en.wikipedia.org/wiki/Carnegie_Mellon_University,_Australia", "https://en.wikipedia.org/wiki/Carnegie_Mellon_School_of_Design", "https://en.wikipedia.org/wiki/Dietrich_College_of_Humanities_and_Social_Sciences", "https://en.wikipedia.org/wiki/Heinz_College", "https://en.wikipedia.org/wiki/Human%E2%80%93Computer_Interaction_Institute", "https://en.wikipedia.org/wiki/Information_Networking_Institute", "https://en.wikipedia.org/wiki/Integrated_Innovation_Institute", "https://en.wikipedia.org/wiki/Language_Technologies_Institute", "https://en.wikipedia.org/wiki/Margaret_Morrison_Carnegie_College", "https://en.wikipedia.org/wiki/Mellon_College_of_Science", "https://en.wikipedia.org/wiki/Mellon_Institute_of_Industrial_Research", "https://en.wikipedia.org/wiki/Carnegie_Mellon_School_of_Music", "https://en.wikipedia.org/wiki/Pittsburgh_Science_of_Learning_Center", "https://en.wikipedia.org/wiki/Robotics_Institute", "https://en.wikipedia.org/wiki/Social_and_Decision_Sciences_(Carnegie_Mellon_University)", "https://en.wikipedia.org/wiki/Swartz_Center_for_Entrepreneurship", "https://en.wikipedia.org/wiki/Tepper_School_of_Business", "https://en.wikipedia.org/wiki/Pittsburgh_Pirates", "https://en.wikipedia.org/wiki/Pittsburgh_Steelers", "https://en.wikipedia.org/wiki/Pittsburgh_Penguins", "https://en.wikipedia.org/wiki/History_of_Pittsburgh", "https://en.wikipedia.org/wiki/Pittsburgh", "https://en.wikipedia.org/wiki/Government_of_Pittsburgh", "https://en.wikipedia.org/wiki/Culture_of_Pittsburgh", "https://en.wikipedia.org/wiki/The_Andy_Warhol_Museum", "https://en.wikipedia.org/wiki/Carnegie_Museum_of_Art", "https://en.wikipedia.org/wiki/Carnegie_Museum_of_Natural_History", "https://en.wikipedia.org/wiki/Carnegie_Science_Center", "https://en.wikipedia.org/wiki/Heinz_History_Center", "https://en.wikipedia.org/wiki/The_Frick_Pittsburgh", "https://en.wikipedia.org/wiki/Pittsburgh_Symphony_Orchestra", "https://en.wikipedia.org/wiki/Pittsburgh_Opera", "https://en.wikipedia.org/wiki/Pittsburgh_Cultural_Trust", "https://en.wikipedia.org/wiki/Picklesburgh"]
def download_pages():
    Headers = {"User-Agent": "HW_Project/1.0 (+https://github.com/njasuja/11711_HW2; njasuja@andrew.cmu.edu)"}
    for i in range(len(urls)):
        url = urls[i]
        response = requests.get(url, headers=Headers, timeout=20)
        html_content = response.text
        with open(f"wikipedia_inputs/page{i}.html", "w", encoding="utf-8") as f:
            f.write(html_content)
    return i

_CITATION_PAT = re.compile(
    r"""
    \s*                           # optional leading whitespace
    \[                            # opening bracket
      \s*(
        \d+(?:\s*[--]\s*\d+)?     # a number, maybe a range like 12-14
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

def parse_sections(soup, min_chunk):
    sections = []
    content = soup.find('div', class_='mw-content-ltr mw-parser-output')
    if not content:
        return sections
    
    all_elements = content.find_all()
    heading_classes = ["mw-heading3", "mw-heading2"]
    skip_titles = ("references", "external links", "see also", "notes", "further reading", "bibliography", "primary sources")
    
    current_heading = "Summary"
    current_paragraphs = []
    current_len = 0

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
                if(current_len >= min_chunk):
                    current_len = 0
                    sections.append({
                        'heading': "jasujazmudzinski",
                        'paragraphs': "jasujazmudzinski"
                    })
            current_heading = element.get_text(strip=True).replace("[edit]", "")
            current_paragraphs = []

        elif element.name == 'p':
            text = _clean_citations(element.get_text(" ", strip=True))
            current_len += len(text.split(" "))
            current_paragraphs.append(text)
        elif subheading:
            text = _clean_citations(element.get_text(strip=True).replace("[edit]", ""))
            current_len += len(text.split(" "))
            current_paragraphs.append(text)
        elif element.name == 'figure':
            continue
        elif element.name == 'table' and current_heading != "Summary":
            table_data = []
            rows = element.find_all('tr')

            for row in rows:
                headers = row.find_all('th')
                if headers:
                    curr_data = [_clean_citations(h.get_text(" ", strip=True)) for h in headers]
                    for d in curr_data:
                        current_len += len(d.split(" "))
                    table_data.append(curr_data)
                
                cells = row.find_all('td')
                if cells:
                    curr_data = [_clean_citations(c.get_text(" ", strip=True)) for c in cells]
                    for d in curr_data:
                        current_len += len(d.split(" "))
                    table_data.append(curr_data)            
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
                    text = _clean_citations(item.get_text(" ", strip=True))
                    current_len+=len(text.split(" "))
                    list_items.append(text)
            if list_items:
                current_paragraphs.append(list_items)

    if current_heading is not None and not any(t in current_heading.lower() for t in skip_titles):
        sections.append({
            'heading': current_heading,
            'paragraphs': current_paragraphs
        })
    return sections

num_pages = 43
chunk_min = 200
to_download = True
dir = "wikipedia_inputs"
if to_download:
    num_pages = download_pages()+1

files = []
for i in range(num_pages):
    files.append(f'page{i}.html')

for i in range(len(files)):
    f = files[i]
    print(f,i,urls[i])
    path = os.path.join(dir, f)
    with open(path, 'r', encoding="utf-8") as f:
        response = f.read()
    curr_soup = BeautifulSoup(response, 'html.parser')
    main_text = parse_sections(curr_soup, chunk_min)
    with open(f"text_outputs/wikipedia{i}.txt", "w", encoding="utf-8") as f:
        for sect in main_text:
            if(sect['heading'] == "jasujazmudzinski"):
                f.write("jasujazmudzinski\n\n")
            else:
                f.write(f"Title: {sect['heading']}\n")
                for para in sect['paragraphs']:
                    f.write(f"{para}\n")
        f.write("jasujazmudzinski\n\n")
