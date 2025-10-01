import requests
from bs4 import BeautifulSoup, Tag

'''
Headers = {"User-Agent": "HW_Project/1.0 (+https://github.com/njasuja/11711_HW2; njasuja@andrew.cmu.edu)"}
url = "https://www.britannica.com/place/Pittsburgh"
response = requests.get(url, headers=Headers, timeout=20)
html_content = response.text
with open("britannica_pittsburgh_history.html", "w", encoding="utf-8") as f:
    f.write(html_content)
'''
with open("britannica_pittsburgh_history.html", "r", encoding="utf-8") as f:
    response = f.read()
soup = BeautifulSoup(response, 'html.parser')


def parse_sections(soup):
    sections = []
    data = soup.find_all("section", attrs={"data-level": "1"})
    if not data:
        return sections

    for data_section in data:
        all_elements = data_section.find_all()
        current_heading = "summary"
        current_paragraphs = []

        for element in all_elements:
            element_classes = element.get('class', [])
            if 'h1' in element_classes:
                current_heading = element.get_text(strip=True).replace("[edit]", "")
            elif 'topic-paragraph' in element_classes:
                current_paragraphs.append(element.get_text(" ", strip=True))

        if len(current_paragraphs) > 0:
            sections.append({
                'heading': current_heading,
                'paragraphs': current_paragraphs
            })
    return sections

main_text = parse_sections(soup)
with open("pittsburgh_history_britannica.txt", "w", encoding="utf-8") as f:
    for sect in main_text:
        f.write(f"Pittsburgh ({sect['heading']})\n")
        for para in sect['paragraphs']:
            f.write(f"{para}\n")
    f.write("jasujazmudzinski\n")

with open("britannica.txt", "w", encoding="utf-8") as f:
    f.write(str(soup.prettify()))
    f.write("\njasujazmudzinski\n")
# '''