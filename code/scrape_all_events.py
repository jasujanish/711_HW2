import requests
from bs4 import BeautifulSoup

urls = ["https://pittsburgh.events/january/", "https://pittsburgh.events/february/", "https://pittsburgh.events/march/", "https://pittsburgh.events/april/", "https://pittsburgh.events/may/", "https://pittsburgh.events/june/", "https://pittsburgh.events/july/", "https://pittsburgh.events/august/", "https://pittsburgh.events/september/", "https://pittsburgh.events/october/", "https://pittsburgh.events/november/", "https://pittsburgh.events/december/"]
def download_pittsburghevents_pages():
    Headers = {"User-Agent": "HW_Project/1.0 (+https://github.com/njasuja/11711_HW2; njasuja@andrew.cmu.edu)"}
    for i in range(len(urls)):
        url = urls[i]
        response = requests.get(url, headers=Headers, timeout=20)
        html_content = response.text
        with open(f"events_inputs/pittsburgh_events_{urls[i][26:-1]}.html", "w", encoding="utf-8") as f:
            f.write(html_content)
    return i
download_pittsburghevents = False
if download_pittsburghevents:
    download_pittsburghevents()

def parse_pittsburghevents_page(soup):
    content = soup.find_all('li', class_='date-row')
    res = "Here are a list of some events happening in Pittsburgh"
    length = 0
    min_chunk_size = 200

    for i in range(len(content)):
        c = content[i]
        month = c.find('div', class_='month')
        day = c.find('div', class_='day')
        year = c.find('div', class_='year')
        time = c.find('div', class_='time')
        event = c.find('div', class_='venue')
        avilability = c.find('div', class_='from-price')

        tmp = f'\nEvent: {event.get_text(" ",strip= True)} \n Time: {month.get_text()} {day.get_text()}, {year.get_text()} {time.get_text(" ",strip= True)} \n Availbility: {avilability.get_text(" ",strip= True)}\n'
        if(length > min_chunk_size):
            res+="njasujazmudzinski\n\nHere are a list of some events happening in Pittsburgh"
            length = 0
        length+=len(tmp.split(" "))
        res+=tmp
    res+="njasujazmudzinski\n"
    return res

parse_pittsburghevents = True
if parse_pittsburghevents:
    for i in range(len(urls)):
        with open(f"events_inputs/pittsburgh_events_{urls[i][26:-1]}.html", "r", encoding="utf-8") as f:
            response = f.read()
        soup = BeautifulSoup(response, 'html.parser')
        main_text = parse_pittsburghevents_page(soup)
        with open("text_outputs/pittsburgh_events.txt", "a", encoding="utf-8") as f:
            f.write(main_text)
