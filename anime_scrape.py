import requests
import config as c
import json
from bs4 import BeautifulSoup
import base64

def hianime_request():
    headers = {"User-Agent": c.AGENT}
    
    try:
        r = requests.get(c.BASE_API, headers=headers)
        http_code = r.status_code
    except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError):
        print(f"Connection Error or Connection Timeout")
        
""" Searches the query nad gives a list of different anime series"""
def hianime_search(anime: str):
    search_page = c.SEARCH_API % anime
    headers = {"User-Agent": c.AGENT}
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
            anime_id = anime_link.split("-")[-1]
            anime_list.append({
                "title": anime_title,
                "link": anime_link,
                "id": anime_id,
            })
        
    except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError):
        print("Connection Error or Connection Timeout")
    
    return anime_list

"""Get the episodes list of the selected anime"""
def hianime_episodes(anime_id: int):
    episodes_page = c.EPISODES_API % anime_id
    headers = {"User-Agent": c.AGENT}
    episode_info = []
    
    try:
        r = requests.get(episodes_page, headers=headers)
        data = r.json()
        html_content = data.get("html", "")
        content = BeautifulSoup(html_content, "html.parser")
        for episode in content.find_all("a", class_="ep-item"):
            ep_id = episode.get("data-id")
            ep_number = episode.get("data-number")
            ep_title = episode.get("title")
            
            episode_info.append({
                "id": ep_id,
                "number": ep_number,
                "title": ep_title
            })
            
    except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError):
        print("Ups !")
        
    return episode_info

def hianime_download_m3u8(episode_id: int):
    servers_page = c.SERVERS_API % episode_id
    headers = {"User-Agent": c.AGENT}
    server_info = []
    
    try:
        r = requests.get(servers_page, headers=headers)
        data = r.json()
        html_content = data.get("html", "")
        content = BeautifulSoup(html_content, "html.parser")
        for server in content.find_all(class_="server-item"):
            server_type = server.get("data-type") # sub or dub
            server_name = server.get("data-server-name") # for example ZokoAnime
            server_hash = server.get("data-hash")

            server_info.append({
                "type": server_type,
                "name": server_name,
                "hash": server_hash
            })
    except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError):
        print("Ups !")
    
    return server_info

def decode_server_hash(server_hashes: list):
    decoded_hash_list = []
    for hash in server_hashes:
        decoded_hash = base64.b64decode(hash["hash"]) 
        decoded_hash_list.append(decoded_hash)
    
    return decoded_hash_list

print(decode_server_hash(hianime_download_m3u8(4402)))
        
    
    
    

    
    


    
        