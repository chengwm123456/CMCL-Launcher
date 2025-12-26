# -*- coding: utf-8 -*-
from typing import overload

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from ..ThemeController import *
from .ToolTip import ToolTip

from .Widget import Widget


class ToolBox(QToolBox, Widget):
    @overload
    def __init__(self, parent=None):
        ...
    
    def __init__(self, *__args):
        super().__init__(*__args)
    
    def paintEvent(self, a0):
        self.setStyleSheet("padding: 3px;")
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
            painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 16, 16)
            painter.restore()
        
        for button in (button for button in self.children() if isinstance(button, QAbstractButton)):
            button.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            button.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
            opacity = QGraphicsOpacityEffect(button)
            opacity.setOpacity(0.0)
            if button.graphicsEffect():
                button.graphicsEffect().deleteLater()
            button.setGraphicsEffect(opacity)
            if not hasattr(button, "newTip"):
                newTip = ToolTip(self)
                button.newTip = newTip
                button.installEventFilter(newTip)
            if not hasattr(button, "evf"):
                button.evf = self
                button.installEventFilter(button.evf)
                print(button.evf)
            
            painter.save()
            painter.translate(button.pos())
            rect = button.rect().adjusted(1, 1, -1, -1)
            painter.setOpacity(button.property("baseOpacity") or 1)
            painter.setPen(getBorderColour(is_highlight=(button.isDown() or button.isChecked()) or (
                    (button.isDown() or button.isChecked()) and button.isEnabled())))
            painter.setBrush(getBackgroundColour(is_highlight=(button.isDown() or button.isChecked()) or (
                    (button.isDown() or button.isChecked()) and button.isEnabled())))
            painter.drawRoundedRect(rect, 16, 16)
            
            if button.property("frameOpacity"):
                painter.setOpacity(button.property("frameOpacity"))
                painter.setPen(getBorderColour(is_highlight=True))
                painter.setBrush(getBackgroundColour(is_highlight=(button.isDown() or button.isChecked()) or (
                        (button.isDown() or button.isChecked()) and button.isEnabled())))
                painter.drawRoundedRect(rect, 16, 16)
            
            painter.restore()
