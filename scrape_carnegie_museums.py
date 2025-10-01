import json
import requests
from bs4 import BeautifulSoup, Tag
import pprint 
websites = ["https://carnegiemuseums.org/our-museums/carnegie-museum-of-natural-history/", "https://carnegiemuseums.org/our-museums/kamin-science-center/", "https://carnegiemuseums.org/our-museums/the-andy-warhol-museum/", "https://carnegiemuseums.org/our-museums/carnegie-museum-of-art/"]
titles = ["carnegie_museum_naturalhistory", "carnegie_museum_kaminscience", "carnegie_museum_warhol", "carnegie_museum_moa"]
'''

Headers = {"User-Agent": "HW_Project/1.0 (+https://github.com/njasuja/11711_HW2; njasuja@andrew.cmu.edu)"}
for i in range(len(titles)):
    response = requests.get(websites[i], headers=Headers, timeout=20)
    html_content = response.text
    with open(f"{titles[i]}.html", "w", encoding="utf-8") as f:
        f.write(html_content)
'''

def parse_moma(soup):
    sections = []
    content = soup.find('div', class_='entry-content')
    with open('tmp.txt', 'w') as f:
        f.write(content.prettify())
    if not content:
        return sections
    all_elements = content.find_all()
    for element in all_elements:
        print(element.get_text(" ", strip=True))

for i in range(1):
    with open(f"{titles[i]}.html", "r", encoding="utf-8") as f:
        response = f.read()
    soup = BeautifulSoup(response, 'html.parser')
    main_text = parse_moma(soup)
    pprint.pprint(main_text)
