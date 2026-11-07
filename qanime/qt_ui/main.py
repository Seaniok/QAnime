import sys
import subprocess
from urllib.parse import urlparse

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLineEdit, QListWidget, QLabel,
)

from qanime import anime_scrape


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QAnime")
        self.resize(1000, 700)
        self.results = []
        self.episodes = []

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.search = QLineEdit(placeholderText="Search anime and press Enter")
        self.search.returnPressed.connect(self.do_search)
        layout.addWidget(self.search)

        layout.addWidget(QLabel("Anime"))
        self.anime_list = QListWidget()
        self.anime_list.itemClicked.connect(self.load_episodes)
        layout.addWidget(self.anime_list)

        layout.addWidget(QLabel("Episodes (double-click to play)"))
        self.episode_list = QListWidget()
        self.episode_list.itemDoubleClicked.connect(self.play)
        layout.addWidget(self.episode_list)

    def do_search(self):
        self.results = anime_scrape.hianime_search(self.search.text())
        self.anime_list.clear()
        self.episode_list.clear()
        for a in self.results:
            self.anime_list.addItem(a["title"])

    def load_episodes(self, item):
        anime_id = self.results[self.anime_list.row(item)]["id"]
        self.episodes = anime_scrape.hianime_episodes(anime_id)
        self.episode_list.clear()
        for ep in self.episodes:
            self.episode_list.addItem(f"{ep['number']}. {ep['title']}")

    def play(self, item):
        ep = self.episodes[self.episode_list.row(item)]
        info = anime_scrape.hianime_download_m3u8(ep["id"], "sub")
        if not info.get("embed_url"):
            self.statusBar().showMessage("No stream found", 5000)
            return
        info = anime_scrape.extract_video_data(info)
        url = info.get("m3u8_url")
        if not url:
            self.statusBar().showMessage("No m3u8 link", 5000)
            return
        p = urlparse(info["embed_url"])
        subprocess.Popen([
            "mpv",
            f"--http-header-fields=Referer: {p.scheme}://{p.netloc}/",
            url,
        ])


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())