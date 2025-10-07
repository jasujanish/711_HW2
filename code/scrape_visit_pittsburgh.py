import requests
from bs4 import BeautifulSoup, Tag
import os 

# Gets HTML data via requests
def download_data():
    Headers = {"User-Agent": "HW_Project/1.0 (+https://github.com/njasuja/11711_HW2; njasuja@andrew.cmu.edu)"}
    url = "https://www.visitpittsburgh.com/things-to-do/family-fun/?hitsPerPage=96"
    response = requests.get(url, headers=Headers, timeout=20)
    html_content = response.text
    with open("visitpittsburgh_things_to_do.html", "w", encoding="utf-8") as f:
        f.write(html_content)

# gets all links on the HTML page & downloads them to the things_to_do directory
def get_all_pages(soup):
    links = soup.find_all('a', class_='card__link btn btn--alt')
    print(len(links))
    href_list = [link.get('href') for link in links]

    Headers = {"User-Agent": "HW_Project/1.0 (+https://github.com/njasuja/11711_HW2; njasuja@andrew.cmu.edu)"}
    
    for href in href_list:
        url = "https://www.visitpittsburgh.com"+href
        response = requests.get(url, headers=Headers, timeout=20)
        html_content = response.text
        with open(f"things_to_do{href[10:-1]}.html", "w", encoding="utf-8") as f:
            f.write(html_content)
    
    return ""

# Parses through the things_to_do directory, gets all data
# Simple semantic chunking, group every 5 activities in a chunk
def parse_pages(dir='things_to_do'):
    files = [f for f in os.listdir(dir) if f.endswith('.html')]
    output_list = []
    i = 0
    for f in files:
        i+=1
        path = os.path.join(dir, f)
        with open(path, 'r', encoding="utf-8") as f:
            response = f.read()
        curr_soup = BeautifulSoup(response, 'html.parser')
        header = curr_soup.find(class_='detail__heading')
        description = curr_soup.find('div', class_='detail__summary')
        output_list.append(f'Pittsburgh event ({header.get_text(strip=True)}): {description.get_text(' ', strip=True)}\n')
        if(i%5 == 0):
            output_list.append("jasujazmudzinski\n")

    return output_list

# writes the chunked activities to one .txt file
res = parse_pages()
with open('things_to_do/things_to_do.txt', 'w') as f:
    for r in res:
        f.write(r)