from pathlib import Path

from PySide6.QtCore import Qt, QPoint, QTimer, Signal, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup
from PySide6.QtGui import QPainter, QPixmap, QLinearGradient, QColor, QIcon
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QGraphicsOpacityEffect,
)

BG = Path(__file__).resolve().parents[2] / "resources" / "killua.jpg"
ACCENT = QColor("#6c5ce7")


class LandingPage(QWidget):
    searchRequested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._bg = QPixmap(str(BG)) if BG.exists() else QPixmap()
        self._scaled = QPixmap()
        self._played = False

        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)
        outer.addStretch(5)

        self.content = QWidget(objectName="heroContent")
        self.content.setFixedWidth(520)
        self.content.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        col = QVBoxLayout(self.content)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(10)

        logo = QLabel("qanime", objectName="logo")

        self.search = QLineEdit(objectName="heroSearch",
                                placeholderText="Title to search for")
        self.search.setClearButtonEnabled(True)
        self.search.returnPressed.connect(self._submit)

        col.addWidget(logo)
        col.addSpacing(12)
        col.addWidget(self.search)

        outer.addWidget(self.content, 0, Qt.AlignmentFlag.AlignHCenter)
        outer.addStretch(6)

        self._opacity = QGraphicsOpacityEffect(self.content)
        self._opacity.setOpacity(0.0)
        self.content.setGraphicsEffect(self._opacity)

    # --- public ---
    def set_busy(self, busy: bool):
        self.search.setEnabled(not busy)
        self.search.setPlaceholderText("Searching…" if busy else "Title to search for")
        if not busy:
            self.search.setFocus()

    def focus_search(self):
        self.search.setFocus()

    # --- internals ---
    def _submit(self):
        q = self.search.text().strip()
        if q:
            self.searchRequested.emit(q)

    def showEvent(self, ev):
        super().showEvent(ev)
        if self._played:
            return
        self._played = True
        fade = QPropertyAnimation(self._opacity, b"opacity", self)
        fade.setDuration(250)
        fade.setStartValue(0.0)
        fade.setEndValue(1.0)
        fade.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._intro = QParallelAnimationGroup(self)
        self._intro.addAnimation(fade)
        # Position is only known after layout; start it next tick.
        def start():
            self._intro.start()
            self.search.setFocus()

        QTimer.singleShot(0, start)

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        if not self._bg.isNull():
            self._scaled = self._bg.scaled(
                self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation)

    def paintEvent(self, ev):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        p.fillRect(self.rect(), QColor("#131415"))
        if not self._scaled.isNull():
            x = (self.width() - self._scaled.width()) // 2
            y = (self.height() - self._scaled.height()) // 2
            p.drawPixmap(x, y, self._scaled)
        g = QLinearGradient(0, 0, 0, self.height())
        g.setColorAt(0.0, QColor(19, 20, 21, 238))
        g.setColorAt(0.5, QColor(19, 20, 21, 215))
        g.setColorAt(1.0, QColor(19, 20, 21, 252))
        p.fillRect(self.rect(), g)
