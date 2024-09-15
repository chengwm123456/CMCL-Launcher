# -*- coding: utf-8 -*-
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from .CWMThemeControl import *


class NavigationItem(QToolButton):
    def __init__(self, parent, icon_path):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setContentsMargins(10, 10, 10, 10)
        self.setFixedSize(42, 42)
        self.setIcon(QIcon(icon_path))
        self.setCheckable(True)
        self.setAutoExclusive(True)
    
    def paintEvent(self, a0):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        painter = QPainter(self)
        painter.setOpacity(1.0 if self.underMouse() or self.hasFocus() else 0.6)
        if not self.isEnabled():
            painter.setOpacity(0.3)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(
            getBorderColour(highlight=self.isDown() or self.isChecked() or self.hasFocus() or self.underMouse()))
        painter.setBrush(getBackgroundColour(highlight=self.isDown() or self.isChecked()))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)
        self.icon().paint(painter, QRect(5, 5, 32, 32))
    
    def keyPressEvent(self, *args, **kwargs):
        super().keyPressEvent(*args, **kwargs)
        if args[0].key() == 16777220 and self.hasFocus():
            self.setChecked(True)
            self.setDown(True)
            self.repaint()
    
    def keyReleaseEvent(self, *args, **kwargs):
        super().keyReleaseEvent(*args, **kwargs)
        if args[0].key() == 16777220 and self.hasFocus():
            self.setDown(False)
            self.pressed.emit()
            self.repaint()
