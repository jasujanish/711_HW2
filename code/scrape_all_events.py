import requests
from bs4 import BeautifulSoup
import re 

# Download the pittsburgh events html data
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

# Clean the pittsburgh events html data
def parse_pittsburghevents_page(soup):
    content = soup.find_all('li', class_='date-row')
    res = "Here are a list of some events happening in Pittsburgh"
    curr_len = 0
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
        if(curr_len > min_chunk_size):
            res+="jasujazmudzinski\n\nHere are a list of some events happening in Pittsburgh"
            curr_len = 0
        curr_len+=len(tmp.split(" "))
        res+=tmp
    res+="jasujazmudzinski\n"
    return res

parse_pittsburghevents = False
if parse_pittsburghevents:
    for i in range(len(urls)):
        with open(f"events_inputs/pittsburgh_events_{urls[i][26:-1]}.html", "r", encoding="utf-8") as f:
            response = f.read()
        soup = BeautifulSoup(response, 'html.parser')
        main_text = parse_pittsburghevents_page(soup)
        with open("text_outputs/pittsburgh_events.txt", "a", encoding="utf-8") as f:
            f.write(main_text)

# Clean the cmu calendar html data (data downloaded manually)
def parse_cmucalendar_page(soup):
    res = "Here are a list of a few CMU events"
    data = soup.find('div', id="lw_cal_events")

    curr_len = 0 
    min_chunk_size = 200

    all_elements = data.find_all()

    for element in all_elements:
        element_class = element.get('class', [])
        if element.name == 'h3':
            if(curr_len > min_chunk_size):
                res+='jasujazmudzinski\n\nHere is a list of a few CMU events'
                curr_len=0
            tmp = f'\n{element.get_text('', strip=True)}\n'
            curr_len+=len(tmp.split(" "))
            res+=tmp
        elif "lw_events_location" in element_class:
            tmp = element.get_text(strip=True)
            if(tmp):
                curr_len+=len(tmp.split(" "))
                res+=f"Location: {tmp}\n"
        elif "lw_events_title" in element_class:
            tmp = element.get_text(strip=True)
            if(tmp):
                curr_len+=len(tmp.split(" "))
                res+=f"Title: {tmp}\n"
        elif "lw_events_time" in element_class:
            tmp = element.get_text(strip=True)
            if(tmp):
                curr_len+=len(tmp.split(" "))
                res+=f"Time: {tmp}\n"
        elif "lw_events_summary" in element_class:
            tmp = element.get_text(strip=True)
            if(tmp):
                curr_len+=len(tmp.split(" "))
                res+=f"Summary: {tmp}\n"
    res+='\njasujazmudzinski\n'
    return res

parse_cmucalendar = False
if parse_cmucalendar:
        with open(f"events_inputs/cmu_calendar.html", "r", encoding="utf-8") as f:
            response = f.read()
        soup = BeautifulSoup(response, 'html.parser')
        main_text = parse_cmucalendar_page(soup)
        with open("text_outputs/cmu_calendar.txt", "w", encoding="utf-8") as f:
            f.write(main_text)
            #: a bit of manual addition (no worries)
            f.write('''Here are CMU's signature events
Spring Carnival: For more than 100 years, Spring Carnival has been one of the most anticipated weekends of the year. Tartans from around the world return to campus to carry on events like Booth, Buggy, MOBOT, Scotch’n’Soda performances and much more.
Homecoming Weekend: Each fall, the CMU community puts on their best Tartan for a weekend of family-friendly activities like the annual CMU Alumni Awards, campus tours, Buggy previews and the tailgate and football game.
Reunion Weekend: During Spring Carnival, Tartans celebrating their Reunion year join exclusive events, opportunities to connect — and reconnect — with peers and create new memories at CMU.
Alumni Awards: Each year, Carnegie Mellon honors a group of exceptional alumni who have made an impact on their industries, their communities, their alma mater and lives around the world at this special event during Homecoming Weekend.
Tartans on the Rise: Every year, we celebrate the recent alumni who are making an impact in their organizations and in their communities, across the nation and around the world through leadership, innovation and career achievements.
Online Events: Just as the reach of Carnegie Mellon extends around the globe, you can engage with the university and fellow Tartan alumni through a variety of online events from anywhere in the world.
CMU 125: Make plans to attend Homecoming Weekend, Nov. 6-8, to celebrate 125 years of Carnegie Mellon University. In addition to traditional festivities like Spirit Day and the football game, CMU125 at Homecoming Weekend features special events and opportunities for Tartans of all ages to celebrate this remarkable moment in CMU history.
Presidential Tours: President Farnam Jahanian visits different cities throughout the year to meet Tartans across the country and share Carnegie Mellon’s inspiring vision for the future. Faculty members share cutting-edge research and alumni have a chance to network with each other and university leadership.
jasujazmudzinski''')
            
# Clean the downtown pittsburgh events html data (data downloaded manually)
def parse_downtownpittsburghevents_page(soup):
    content = soup.find_all('div', class_='eventitem')
    curr_len = 0
    min_chunk_size = 200
    res = "Here is a list of a few events in downtown Pittsburgh"
    for i in range(len(content)):
        element = content[i]
        title = element.find('h1').get_text()
        raw_date = element.find('div', class_='eventdate').get_text('', strip=True)
        date = re.sub(r"\s+", " ", raw_date).replace("|", "").strip()
        description = element.find('div', class_='eventdate').find_next_sibling(string= True).strip()

        tmp = f'\nTitle: {title}\ndate: {date}\ndescription:{description}\n'

        if(curr_len > min_chunk_size):
            res+='jasujazmudzinski\n\nHere is a list of a few events in downtown Pittsburgh'
            curr_len=0
        res+=tmp
        curr_len += len(tmp.split(" "))
    res+='jasujazmudzinski\n'
    return res
        # print(element)

parse_dowtownpittsburghevents = False
if parse_dowtownpittsburghevents:
    with open(f"events_inputs/downtownpittsburgh_events_october.html", "r", encoding="utf-8") as f:
        response = f.read()
    soup = BeautifulSoup(response, 'html.parser')
    text_1=parse_downtownpittsburghevents_page(soup)

    with open(f"events_inputs/downtownpittsburgh_events_november.html", "r", encoding="utf-8") as f:
        response2 = f.read()
    soup2 = BeautifulSoup(response2, 'html.parser')
    text_2=parse_downtownpittsburghevents_page(soup2)

    with open(f"events_inputs/downtownpittsburgh_events_december.html", "r", encoding="utf-8") as f:
        response3 = f.read()
    soup3 = BeautifulSoup(response3, 'html.parser')
    text_3=parse_downtownpittsburghevents_page(soup3)

    with open("text_outputs/downtownpittsburgh_events.txt", "w", encoding="utf-8") as f:
        f.write(text_1)
        f.write(text_2)
        f.write(text_3)