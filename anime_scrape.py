import requests
import config as c

def hianime_request():
    headers = {f"User-Agent": c.AGENT}
    
    try:
        r = requests.get(c.BASE_API, headers=headers)
        http_code = r.status_code
    except requests.exceptions.ConnectTimeout:
        print(f"Connection Error or Connection Timeout")
    
        