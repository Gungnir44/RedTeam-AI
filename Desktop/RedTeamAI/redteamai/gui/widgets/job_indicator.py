"""Animated spinner / job indicator widget."""
from __future__ import annotations
import math
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen


class SpinnerWidget(QWidget):
    """Lightweight CSS-free spinner using QPainter."""

    def __init__(self, size: int = 20, color: str = "#1f6feb", parent=None):
        super().__init__(parent)
        self._size = size
        self._color = QColor(color)
        self._angle = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self.setFixedSize(size, size)
        self.hide()

    def _tick(self) -> None:
        self._angle = (self._angle + 15) % 360
        self.update()

    def start(self) -> None:
        self.show()
        self._timer.start(50)

    def stop(self) -> None:
        self._timer.stop()
        self.hide()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.translate(self._size / 2, self._size / 2)
        painter.rotate(self._angle)

        pen = QPen(self._color, 2.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        r = self._size / 2 - 3
        rect = QRectF(-r, -r, r * 2, r * 2)
        # Draw arc (270 degrees = 3/4 circle)
        painter.drawArc(rect, 0, 270 * 16)
