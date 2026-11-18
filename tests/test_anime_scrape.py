import requests
from qanime import anime_scrape

class FakeResponse:
    """Udaje obiekt odpowiedzi z requests."""
    def __init__(self, data):
        self.data = data

    def json(self):
        return self.data

HIANIME_EPISODES_HTML = """
<a title="To You Two Thousand Years Later"
   class="ssl-item ep-item"
   data-number="1"
   data-id="4402"
   href="https://hianime.fm/watch/attack-on-titan-240?ep=4402">
    <div class="ssli-order">1</div>
    <div class="ssli-detail">
        <div class="ep-name dynamic-name"
             data-jname="Ni Sen-Nen-Go no Kimi e"
             title="To You Two Thousand Years Later">
            To You Two Thousand Years Later
        </div>
    </div>
    <div class="ssli-btn">
        <div class="btn btn-circle"><i class="fas fa-play"></i></div>
    </div>
    <div class="clearfix"></div>
</a>
"""

HIANIME_DOWNLOAD_M3U8_HTML = """
<div class="server-item" data-type="sub" data-server-name="ZokoAnime"
     data-hash="aHR0cHM6Ly96b2tvYW5pbWUudmlkZW8vc3RyZWFtL21hbC8xNjQ5OC8xL3N1Yg=="></div>
<div class="server-item" data-type="sub" data-server-name="HD-1"
     data-hash="aHR0cHM6Ly9tZWdhcGxheS5idXp6L3N0cmVhbS9zLTIvMzMwMy9zdWI/cz10Y2Ru"></div>
"""

def test_hianime_episodes(monkeypatch):
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: FakeResponse({"html": HIANIME_EPISODES_HTML}))
    result = anime_scrape.hianime_episodes(240)
    assert result == [
        {"id": "4402", "number": "1", "title": "To You Two Thousand Years Later"}
    ]

def test_hianime_download_m3u8(monkeypatch):
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: FakeResponse({"html": HIANIME_DOWNLOAD_M3U8_HTML}))
    result = anime_scrape.hianime_download_m3u8(4402, "sub")
    assert result == {
        "type": "sub", "name": "ZokoAnime", "embed_url": "https://zokoanime.video/stream/mal/16498/1/sub"
    }
