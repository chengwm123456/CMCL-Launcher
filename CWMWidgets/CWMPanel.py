# -*- coding: utf-8 -*-
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


class Panel(QFrame):
    def paintEvent(self, a0):
        self.setStyleSheet("padding: 3px;")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QColor(230, 230, 230))  # Light: 255, 255, 255, 18   Light: 0, 0, 0, 18
        painter.setBrush(QColor(249, 249, 249))  # Dark: 43, 43, 43   Light: 249, 249, 249
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)
