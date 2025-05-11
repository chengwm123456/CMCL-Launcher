# -*- coding: utf-8 -*-
from typing import overload

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from ..ThemeController import *

from .Widget import Widget


class Panel(QFrame, Widget):
    @overload
    def __init__(self, parent=None):
        ...
    
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setStyleSheet("padding: 3px; border: none;")
    
    def paintEvent(self, a0):
        self.setStyleSheet("padding: 3px; border: none;")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self)
        painter.setOpacity(self.property("widgetOpacity"))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        borderColour = getBorderColour()
        backgroundColour = getBackgroundColour()
        painter.save()
        painter.setOpacity((((max(painter.opacity(), 0.6) - 0.6) * 10) / 4))
        borderGradient = QLinearGradient(QPointF(0, 0), QPointF(0, self.height()))
        borderGradient.setColorAt(0.0, Colour(*getBorderColour(), 64))
        borderGradient.setColorAt(1.0, borderColour)
        painter.setPen(QPen(QBrush(borderGradient), 1))
        painter.setBrush(Qt.GlobalColor.transparent)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 12, 12)
        painter.restore()
        painter.save()
        painter.setOpacity(self.property("widgetOpacity"))
        borderGradient = QLinearGradient(QPointF(3, 3), QPointF(3, self.height() - 3))
        borderGradient.setColorAt(0.0, borderColour)
        borderGradient.setColorAt(1.0, Colour(*getBorderColour(), 64))
        backgroundGradient = QLinearGradient(QPointF(3, 3), QPointF(self.width() - 3, 3))
        backgroundGradient.setColorAt(0.0, backgroundColour)
        backgroundGradient.setColorAt(0.5, Colour(*backgroundColour, 230))
        backgroundGradient.setColorAt(1.0, backgroundColour)
        painter.setPen(QPen(QBrush(borderGradient), 1))
        painter.setBrush(QBrush(backgroundGradient))
        painter.drawRoundedRect(self.rect().adjusted(3, 3, -3, -3), 10, 10)
        painter.restore()
