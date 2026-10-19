# This Python file uses the following encoding: utf-8
import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QMenu, QMenuBar, QPushButton, QLineEdit
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
        """self.search_button.setStyleSheet"""
        
        self.search_button.returnPressed.connect(self.show_anime)
        
        self.results_layout = QVBoxLayout()
        self.layout.addLayout(self.results_layout)
    
    def show_anime(self):
        result = anime_scrape.hianime_search(self.search_button.text())
        for i in result:
            anime_title = i["title"]
            title_boxes = QPushButton(anime_title)
            self.layout.addWidget(title_boxes)
        
        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
