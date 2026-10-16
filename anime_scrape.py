import requests
import config as c
import json
from bs4 import BeautifulSoup

def hianime_request():
    headers = {f"User-Agent": c.AGENT}
    
    try:
        r = requests.get(c.BASE_API, headers=headers)
        http_code = r.status_code
    except requests.exceptions.ConnectTimeout:
        print(f"Connection Error or Connection Timeout")
        
def hianime_search(anime: str):
    search_page = c.SEARCH_API % anime
    headers = {f"User-Agent": c.AGENT}
    anime_list = []
    
    try:
        count = 0
        r = requests.get(search_page, headers=headers)
        content = BeautifulSoup(r.text, "html.parser")
        for anime_item in content.find_all("h3", class_="film-name"):
            count += 1
            if count == 10:
                break
            anime_title = anime_item.find("a")["title"]
            anime_link = anime_item.find("a")["href"]
            anime_list.append({
                "title": anime_title,
                "link": anime_link,
            })
        
    except requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError:
        print("Connection Error or Connection Timeout")
    
    return anime_list


    
        