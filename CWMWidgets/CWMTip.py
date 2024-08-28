# -*- coding: utf-8 -*-
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from .CWMThemeControl import *


class TipBase(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(QSize(256, 64))
    
    def paintEvent(self, a0):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.adjustSize()
        self.setStyleSheet(
            f"background: transparent; color: rgb({str(getForegroundColour(tuple=True)).replace('(', '').replace(')', '')});")
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getBorderColour())
        painter.setBrush(getBackgroundColour())
        painter.drawRoundedRect(self.rect(), 10, 10)
        super().paintEvent(a0)
    
    def setEnabled(self, a0):
        super().setEnabled(a0)
        if a0:
            self.setGraphicsEffect(None)
        else:
            og = QGraphicsOpacityEffect()
            og.setOpacity(0.3)
            self.setGraphicsEffect(og)


class Tip(TipBase):
    pass


class PopoutTip(TipBase):
    def tip(self):
        self.show()
        animation = QPropertyAnimation(self, b"geometry", parent=self.parent())
        animation.setDuration(1000)
        animation.setStartValue(QRect(self.parent().width() - self.width(), 0, self.width(), self.height()))
        animation.setEndValue(QRect(0, 0, self.width(), self.height()))
        animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        animation.start()
