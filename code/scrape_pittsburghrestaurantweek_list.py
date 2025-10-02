from bs4 import BeautifulSoup

def parse_sections(soup):
    res = "Here is a list of restaurants at the summer 2025 pittsburgh restaurant week:\n"

    curr_len = 0 
    min_chunk_size = 200

    all_elements = soup.find_all()
    if not all_elements:
        return "EMPTY"

    for element in all_elements:
        if element.name == 'strong':
            text = element.get_text(" ", strip=True)
            res+=text
            res+='\n'
    res+='jasujazmudzinski\n'
    return res

with open("other_inputs/pittsburghrestaurantweek.html", "r", encoding="utf-8") as f:
    response = f.read()
soup = BeautifulSoup(response, 'html.parser')
main_text = parse_sections(soup)
with open("text_outputs/pittsburghrestaurantweek_list.txt", "w", encoding="utf-8") as f:
    f.write(main_text)