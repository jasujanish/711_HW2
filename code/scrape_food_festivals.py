from bs4 import BeautifulSoup

def parse_visit_pittsburgh_food_festivals(soup):
    res = ""
    data = soup.find(class_="content--primary")
    if not data:
        return "EMPTY"

    curr_len = 0 
    min_chunk_size = 200

    all_elements = data.find_all()

    for element in all_elements:
        if element.name == 'h2':
            text = element.get_text(strip=True)
            curr_len+=len(text.split(" "))
            if(curr_len > min_chunk_size):
                res+='\njasujazmudzinski\n'
                curr_len=0
            res+=text
        elif element.name == 'p':
            text = element.get_text(" ", strip=True)
            curr_len+=len(text.split(" "))
            res+=text
            res+='\n'    
    res+='\njasujazmudzinski\n'
    return res

visit_p_food = False
if visit_p_food:
    with open("other_inputs/visit-pittsburgh-food-festivals.html", "r", encoding="utf-8") as f:
        response = f.read()
    soup = BeautifulSoup(response, 'html.parser')
    main_text = parse_visit_pittsburgh_food_festivals(soup)
    with open("text_outputs/visit_pittsburgh_food_festivals.txt", "w", encoding="utf-8") as f:
        f.write(main_text)


def parse_little_italy_schedule(soup):
    res = ""
    for element in soup.find_all():
        if element.name == 'h1' or element.name == 'p':
            res += element.get_text(" ", strip=True)    
            res += '\n'
    res+='\njasujazmudzinski\n'
    return res

little_italy_schedule = False
if little_italy_schedule:
    with open("other_inputs/little_italy_schedule.html", "r", encoding="utf-8") as f:
        response = f.read()
    soup = BeautifulSoup(response, 'html.parser')
    main_text = parse_little_italy_schedule(soup)
    with open("text_outputs/little_italy.txt", "a", encoding="utf-8") as f:
        f.write(main_text)



def parse_little_italy_FAQ(soup):
    res = ""
    for element in soup.find_all(class_="x-accordion-group"):
        res += element.get_text(" ", strip=True)    
        res += '\n'
    res+='\njasujazmudzinski\n'
    return res

little_italy_FAQ = False
if little_italy_FAQ:
    with open("other_inputs/little_italy_FAQ.html", "r", encoding="utf-8") as f:
        response = f.read()
    soup = BeautifulSoup(response, 'html.parser')
    main_text = parse_little_italy_FAQ(soup)
    print(main_text)
    with open("text_outputs/little_italy.txt", "a", encoding="utf-8") as f:
        f.write(main_text)


def parse_picklesburgh_vendors(soup):
    table = soup.find('table')
    
    vendors = "Here are the vendors at the 2025 Picklesberg Fest (The 10th Anniversary of Picklesberg)\n"

    rows = table.find('tbody').find_all('tr')

    for row in rows:
        cells = row.find_all('td')
        
        if len(cells) >= 3:
            vendor_name = cells[0].get_text(strip=True)
            
            location_cell = cells[1]
            location_link = location_cell.find('a')
            location = location_link.get_text(strip=True) if location_link else cells[1].get_text(strip=True)
            
            description = cells[2].get_text(strip=True)

            vendors+= f"Vendor: {vendor_name}\t Location:{location}\tDescription: {description}\n"
    vendors+='jasujazmudzinski\n'
    return vendors
picklesburgh_vendors = True
if picklesburgh_vendors:
    with open("other_inputs/picklesburgh_vendors.html", "r", encoding="utf-8") as f:
        response = f.read()
    soup = BeautifulSoup(response, 'html.parser')
    main_text = parse_picklesburgh_vendors(soup)
    print(main_text)
    with open("text_outputs/picklesburgh.txt", "a", encoding="utf-8") as f:
        f.write(main_text)
