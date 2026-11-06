import requests
import config as c
import json
from bs4 import BeautifulSoup
import base64
import re
from urllib.parse import urlparse
from itertools import cycle

def hianime_request():
    headers = {"User-Agent": c.AGENT}
    
    try:
        requests.get(c.BASE_API, headers=headers, timeout=10)
    except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError):
        print("Connection Error or Connection Timeout")
        
""" Searches the query nad gives a list of different anime series"""
def hianime_search(anime: str):
    search_page = c.SEARCH_API % anime
    headers = {"User-Agent": c.AGENT}
    anime_list = []
    
    try:
        count = 0
        r = requests.get(search_page, headers=headers, timeout=10)
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
        r = requests.get(episodes_page, headers=headers, timeout=10)
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

"""Get specific episode server info with decoded data-hash"""
def hianime_download_m3u8(episode_id: int, desired_type: str):
    servers_page = c.SERVERS_API % episode_id
    headers = {"User-Agent": c.AGENT}
    server_info = {}
    
    try:
        r = requests.get(servers_page, headers=headers, timeout=10)
        data = r.json()
        html_content = data.get("html", "")
        content = BeautifulSoup(html_content, "html.parser")
        for server in content.find_all(class_="server-item"):
            server_type = server.get("data-type") # sub or dub
            
            if server.get("data-server-name") == "ZokoAnime" and server_type == desired_type:
                server_name = server.get("data-server-name")
                raw_hash = server.get("data-hash")

                decoded_hash = base64.b64decode(raw_hash).decode("utf-8")
            
                server_info = {
                    "type": server_type,
                    "name": server_name,
                    "embed_url": decoded_hash
                }
            break
        
    except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError):
        print("Ups !")
    
    return server_info

"""Decode XOR and get the decrypted json"""
def deobfuscate_blob(encrypted_blob: str) -> dict:
    decoded_bytes = base64.b64decode(encrypted_blob)
    
    key = b"otaku-embed-v1"
    
    decrypted_bytes = bytearray()
    for byte, key_byte in zip(decoded_bytes, cycle(key)):
        decrypted_bytes.append(byte ^ key_byte)
    
    decrypted_text = decrypted_bytes.decode('utf-8')
    
    return json.loads(decrypted_text)

"""Returns all the links / video data / subs links etc."""
def extract_video_data(server_info: dict):
    embed_url = server_info.get("embed_url")
    parsed_url = urlparse(embed_url)
    referer = f"{parsed_url.scheme}://{parsed_url.netloc}/"
    headers = {
        "User-Agent": c.AGENT,
        "Referer": referer
    }
    
    try:
        response = requests.get(embed_url, headers=headers, timeout=10)
        html_text = response.text
    except requests.exceptions.RequestException :
        print("Ups !")
        return server_info
    
    blob_match = re.search(r'window\.__P="([^"]+)"', html_text)
    if not blob_match:
        print("Nie znaleziono window.__P na stronie")
        return server_info
    
    encrypted_blob = blob_match.group(1)
    
    try:
        decrypted_json = deobfuscate_blob(encrypted_blob)
        server_info["m3u8_url"] = decrypted_json.get("src")
    except Exception as e:
        print(f"Błąd podczas dekodowania bloba: {e}")
        
    return server_info

        
    
    
    

    
    


    
        