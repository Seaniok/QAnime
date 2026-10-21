# This Python file uses the following encoding: utf-8
import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QMenu, QMenuBar, QPushButton, QLineEdit, QListWidget, QListWidgetItem
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from PySide6.QtHelp import QHelpSearchQueryWidget
import resources_rc
import anime_scrape


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUI()
        self.setupLayout()
    
    def setupUI(self):
        self.resize(1280, 720)
        self.setWindowTitle("QAnime")
        self.window_icon = QIcon(":/killua.jpg")
        self.setWindowIcon(self.window_icon)
    
    def setupLayout(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        
        self.layout = QVBoxLayout(self.central_widget)
        self.label = QLabel("Welcome to QAnime")
        self.layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet(
            "font-size: 20px"
        )
        
        self.search_button = QLineEdit(self, placeholderText="Search")
        self.layout.addWidget(self.search_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.search_button.returnPressed.connect(self.show_anime)
        
        self.anime_list = QListWidget()
        self.layout.addWidget(self.anime_list, alignment=Qt.AlignmentFlag.AlignVertical_Mask)
        self.anime_list.setStyleSheet(
            "font-size: 15px;"
        )
        
        self.episodes_list = QListWidget()
        self.layout.addWidget(self.episodes_list)
        self.anime_list.itemClicked.connect(self.on_anime_clicked)
    
    def show_anime(self):
        self.anime_list.clear()
        self.results = anime_scrape.hianime_search(self.search_button.text())
        
        for i in self.results:
            self.anime_list.addItem(i["title"])
            
    def on_anime_clicked(self, item):
        row = self.anime_list.row(item)
        anime_id = self.results[row]["id"]
        episodes = anime_scrape.hianime_episodes(anime_id)
        
        self.episodes_list.clear()
        for episode in episodes:
            ep_text = f"{episode["number"]}. {episode["title"]}"
            self.episodes_list.addItem(ep_text)
        
        
        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
