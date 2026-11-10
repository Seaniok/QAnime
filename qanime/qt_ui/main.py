import sys
import subprocess
from pathlib import Path
from urllib.parse import urlparse

from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QLabel, QPushButton,
    QStackedWidget, QGraphicsOpacityEffect,
)

from qanime import anime_scrape
from qanime.qt_ui.workers import run_async
from qanime.qt_ui.landing import LandingPage

THUMB = QSize(140, 200)


def _placeholder() -> QPixmap:
    pm = QPixmap(THUMB)
    pm.fill(QColor("#1a1b1d"))
    return pm


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QAnime")
        self.resize(1100, 720)
        self.results = []
        self.episodes = []
        self.poster_cache = {}
        self._jobs = []  # keep worker references alive

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.landing = LandingPage()
        self.landing.searchRequested.connect(self.do_search)
        self.stack.addWidget(self.landing)

        # Page 1: results grid
        results_page = QWidget(objectName="root")
        outer = QVBoxLayout(results_page)
        outer.setContentsMargins(16, 16, 16, 8)
        outer.setSpacing(12)
        self.stack.addWidget(results_page)

        back_home = QPushButton("Back", objectName="backBtn")
        back_home.setCursor(Qt.CursorShape.PointingHandCursor)
        back_home.clicked.connect(lambda: self._goto(0))
        hdr = QHBoxLayout()
        hdr.addWidget(back_home)
        hdr.addStretch(1)
        outer.addLayout(hdr)

        self.anime_list = QListWidget()
        self.anime_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.anime_list.setIconSize(THUMB)
        self.anime_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.anime_list.setMovement(QListWidget.Movement.Static)
        self.anime_list.setWordWrap(True)
        self.anime_list.setGridSize(QSize(THUMB.width() + 24, THUMB.height() + 56))
        self.anime_list.itemClicked.connect(self.load_episodes)
        outer.addWidget(self.anime_list, 1)

        # Page 2: anime details + episodes
        detail_page = QWidget(objectName="root")
        rl = QVBoxLayout(detail_page)
        rl.setContentsMargins(16, 16, 16, 8)
        rl.setSpacing(12)
        self.stack.addWidget(detail_page)

        back_results = QPushButton("Back to results", objectName="backBtn")
        back_results.setCursor(Qt.CursorShape.PointingHandCursor)
        back_results.clicked.connect(lambda: self._goto(1))
        hdr2 = QHBoxLayout()
        hdr2.addWidget(back_results)
        hdr2.addStretch(1)
        rl.addLayout(hdr2)

        top = QHBoxLayout()
        self.poster = QLabel(objectName="poster")
        self.poster.setFixedSize(THUMB)
        self.poster.setScaledContents(True)
        top.addWidget(self.poster, 0, Qt.AlignmentFlag.AlignTop)
        info = QVBoxLayout()
        self.title_lbl = QLabel("", objectName="heading")
        self.title_lbl.setWordWrap(True)
        self.meta_lbl = QLabel("", objectName="meta")
        self.meta_lbl.setWordWrap(True)
        self.meta_lbl.setAlignment(Qt.AlignmentFlag.AlignTop)
        info.addWidget(self.title_lbl)
        info.addWidget(self.meta_lbl, 1)
        top.addLayout(info, 1)
        rl.addLayout(top)

        self.episode_list = QListWidget()
        self.episode_list.itemDoubleClicked.connect(self.play)
        rl.addWidget(self.episode_list, 1)
        self.play_btn = QPushButton("Play episode")
        self.play_btn.clicked.connect(self.play_selected)
        rl.addWidget(self.play_btn)

        self.statusBar().showMessage("Ready")

    # --- helpers ---
    def _run(self, fn, *args, on_done, busy=None):
        if busy:
            self.statusBar().showMessage(busy)
        job = run_async(fn, *args, on_done=on_done, on_error=self._error)
        self._jobs.append(job)
        job.signals.finished.connect(lambda *_: self._jobs.remove(job) if job in self._jobs else None)
        job.signals.error.connect(lambda *_: self._jobs.remove(job) if job in self._jobs else None)

    # --- search ---
    def do_search(self, query):
        query = query.strip()
        if not query:
            return
        self.landing.set_busy(True)
        self._run(anime_scrape.hianime_search, query,
                  on_done=self._search_done, busy=f"Searching “{query}”…")

    def _goto(self, index):
        if self.stack.currentIndex() == index:
            return
        eff = QGraphicsOpacityEffect(self.stack)
        self.stack.setGraphicsEffect(eff)
        out = QPropertyAnimation(eff, b"opacity", self)
        out.setDuration(180)
        out.setStartValue(1.0)
        out.setEndValue(0.0)
        inn = QPropertyAnimation(eff, b"opacity", self)
        inn.setDuration(320)
        inn.setStartValue(0.0)
        inn.setEndValue(1.0)
        inn.setEasingCurve(QEasingCurve.Type.OutCubic)

        def swap():
            self.stack.setCurrentIndex(index)
            inn.start()

        out.finished.connect(swap)
        inn.finished.connect(lambda: self.stack.setGraphicsEffect(None))
        self._fade = (out, inn)
        out.start()

    def _search_done(self, results):
        self.landing.set_busy(False)
        self.results = results
        self.anime_list.clear()
        self.episode_list.clear()
        if results:
            self._goto(1)
        for a in results:
            item = QListWidgetItem(QIcon(_placeholder()), a["title"])
            item.setSizeHint(self.anime_list.gridSize())
            item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
            item.setToolTip(a["title"])
            self.anime_list.addItem(item)
            url = a.get("poster")
            if url:
                self._load_poster(url, lambda pm, it=item: it.setIcon(QIcon(pm)))
        self.statusBar().showMessage(
            f"{len(results)} result(s)" if results else "No results", 5000)

    def _load_poster(self, url, apply):
        if url in self.poster_cache:
            apply(self.poster_cache[url])
            return

        def done(data):
            pm = QPixmap()
            if pm.loadFromData(data):
                self.poster_cache[url] = pm
                apply(pm)

        job = run_async(anime_scrape.hianime_poster, url, on_done=done)
        self._jobs.append(job)
        job.signals.finished.connect(lambda *_: self._jobs.remove(job) if job in self._jobs else None)

    # --- episodes ---
    def load_episodes(self, item):
        a = self.results[self.anime_list.row(item)]
        self.title_lbl.setText(a["title"])
        self.meta_lbl.setText(a.get("description", ""))
        self.poster.clear()
        if a.get("poster"):
            self._load_poster(a["poster"], self.poster.setPixmap)
        self.episode_list.clear()
        self._goto(2)
        self._run(anime_scrape.hianime_episodes, a["id"],
                  on_done=self._episodes_done, busy="Loading episodes…")

    def _episodes_done(self, episodes):
        self.episodes = episodes
        self.episode_list.clear()
        for ep in episodes:
            self.episode_list.addItem(f"{ep['number']}   {ep['title']}")
        self.statusBar().showMessage(f"{len(episodes)} episode(s)", 5000)

    # --- playback ---
    def play_selected(self):
        item = self.episode_list.currentItem()
        if item:
            self.play(item)
        else:
            self.statusBar().showMessage("Select an episode first", 4000)

    def play(self, item):
        ep = self.episodes[self.episode_list.row(item)]
        self.play_btn.setEnabled(False)
        self._run(self._resolve, ep["id"], on_done=self._play_ready,
                  busy=f"Resolving stream for episode {ep['number']}…")

    @staticmethod
    def _resolve(ep_id):
        info = anime_scrape.hianime_download_m3u8(ep_id, "sub")
        if not info.get("embed_url"):
            return None, "No stream found"
        info = anime_scrape.extract_video_data(info)
        if not info.get("m3u8_url"):
            return None, "No m3u8 link"
        return info, None

    def _play_ready(self, result):
        self.play_btn.setEnabled(True)
        info, err = result
        if err:
            self.statusBar().showMessage(err, 5000)
            return
        p = urlparse(info["embed_url"])
        try:
            subprocess.Popen([
                "mpv",
                f"--http-header-fields=Referer: {p.scheme}://{p.netloc}/",
                info["m3u8_url"],
            ])
            self.statusBar().showMessage("Playing in mpv", 5000)
        except FileNotFoundError:
            self.statusBar().showMessage("mpv not found on PATH", 8000)

    def _error(self, msg):
        self.statusBar().showMessage(f"Error: {msg}", 8000)
        self.landing.set_busy(False)
        self.play_btn.setEnabled(True)


def main():
    app = QApplication(sys.argv)
    qss = Path(__file__).with_name("style.qss")
    if qss.exists():
        app.setStyleSheet(qss.read_text(encoding="utf-8"))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
