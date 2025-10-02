import requests
from bs4 import BeautifulSoup, Tag
from scrape_pittsburgh_sports_wikipedia import parse_sections
'''
Headers = {"User-Agent": "HW_Project/1.0 (+https://github.com/njasuja/11711_HW2; njasuja@andrew.cmu.edu)"}
url = "https://en.wikipedia.org/wiki/History_of_Pittsburgh"
response = requests.get(url, headers=Headers, timeout=20)
html_content = response.text
with open("wikipedia_pittsburgh_history.html", "w", encoding="utf-8") as f:
    f.write(html_content)
'''

files = ["wikipedia_pittsburgh_history", "wikipedia_pittsburgh"]
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
            if(len(sect['paragraphs'])>0):
                f.write("jasujazmudzinski\n\n")
