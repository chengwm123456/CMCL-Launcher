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
        self.setStyleSheet("padding: 3px; border: none; background: transparent;")
    
    def paintEvent(self, a0):
        self.setStyleSheet("padding: 3px; border: none; background: transparent;")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.save()
        painter.setOpacity(self.property("baseOpacity"))
        painter.setPen(getBorderColour())
        painter.setBrush(getBackgroundColour())
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 16, 16)
        painter.restore()
        
        if self.property("frameOpacity"):
            painter.save()
            painter.setOpacity(self.property("frameOpacity"))
            painter.setPen(getBorderColour())
            painter.setBrush(getBackgroundColour())
            painter.drawRoundedRect(
                self.rect().adjusted(
                    1 + self.property("frameRectAdjustment"),
                    1 + self.property("frameRectAdjustment"),
                    -(1 + self.property("frameRectAdjustment")),
                    -(1 + self.property("frameRectAdjustment"))
                ), 16, 16
            )
            painter.restore()
