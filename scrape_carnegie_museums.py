import requests
from bs4 import BeautifulSoup
websites = ["https://carnegiemuseums.org/our-museums/carnegie-museum-of-natural-history/", "https://carnegiemuseums.org/our-museums/kamin-science-center/", "https://carnegiemuseums.org/our-museums/the-andy-warhol-museum/", "https://carnegiemuseums.org/our-museums/carnegie-museum-of-art/"]
titles = ["carnegie_museum_naturalhistory", "carnegie_museum_kaminscience", "carnegie_museum_warhol", "carnegie_museum_moa"]
names = ["Carnegie Museum of Natural History", "Kamin Science Center", "The Andy Warhol Museum", "Carnegie Museum of Art"]

'''

Headers = {"User-Agent": "HW_Project/1.0 (+https://github.com/njasuja/11711_HW2; njasuja@andrew.cmu.edu)"}
for i in range(len(titles)):
    response = requests.get(websites[i], headers=Headers, timeout=20)
    html_content = response.text
    with open(f"{titles[i]}.html", "w", encoding="utf-8") as f:
        f.write(html_content)
'''

def parse_moma(soup, k):
    sections = []
    content = soup.find('div', class_='entry-content')
    if not content:
        return sections
    museum_details = content.find('div', id='museum-details')
    events_exhibitions = content.find_all('div', class_='event-element link-box')
    image_tags = content.find_all('div', class_='wp-block-column link-box is-layout-flow wp-block-column-is-layout-flow')
    
    res = museum_details.get_text(" ", strip=True)
    res += '\n\n'
    i = 0
    for i in range(len(events_exhibitions)):
        res+=(f'{names[k]} event/exhibition {i+1}: {events_exhibitions[i].get_text(" ", strip=True)}\n')
    res += '\n'
    for x in image_tags:
        res+= f"{names[k]} card title: {x.h3.get_text(" ", strip=True)}\ncorresponding text: {x.p.get_text()}\n"
    return res

for i in range(len(titles)):
    with open(f"{titles[i]}.html", "r", encoding="utf-8") as f:
        response = f.read()
    soup = BeautifulSoup(response, 'html.parser')
    main_text = parse_moma(soup, i)
    with open(f"{titles[i]}.txt", "w", encoding="utf-8") as f:
        f.write(main_text)
        f.write("jasujazmudzinski\n\n")
