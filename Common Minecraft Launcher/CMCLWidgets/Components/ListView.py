# -*- coding: utf-8 -*-
from typing import overload

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from ..ThemeController import *
from .ItemView import ItemDelegate
from .ScrollBar import ScrollBar

from .Widget import Widget


class ListView(QListView, Widget):
    @overload
    def __init__(self, parent=None):
        ...
    
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setItemDelegate(ItemDelegate(self))
        self.setHorizontalScrollBar(ScrollBar(Qt.Orientation.Horizontal, self))
        self.setVerticalScrollBar(ScrollBar(Qt.Orientation.Vertical, self))
        
        self.removeEventFilter(self)
        self.viewport().installEventFilter(self)
    
    def paintEvent(self, e):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.save()
        painter.setOpacity(self.viewport().property("baseOpacity"))
        painter.setPen(getBorderColour())
        painter.setBrush(getBackgroundColour())
        painter.drawRoundedRect(self.viewport().rect().adjusted(1, 1, -1, -1), 16, 16)
        painter.restore()
        
        if self.viewport().property("frameOpacity"):
            painter.save()
            painter.setOpacity(self.viewport().property("frameOpacity"))
            painter.setPen(getBorderColour())
            painter.setBrush(getBackgroundColour())
            painter.drawRoundedRect(
                self.viewport().rect().adjusted(
                    1 + self.viewport().property("frameRectAdjustment"),
                    1 + self.viewport().property("frameRectAdjustment"),
                    -(1 + self.viewport().property("frameRectAdjustment")),
                    -(1 + self.viewport().property("frameRectAdjustment"))
                ), 16, 16
            )
            painter.restore()
        
        op = QStyleOptionFrame()
        op.initFrom(self)
        self.initStyleOption(op)
        self.setStyleSheet(
            f"color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {self.property('baseOpacity') + (self.property('frameOpacity') * (1.0 - self.property('baseOpacity')))}); background: transparent; border: none;")
        super().paintEvent(e)


class ListWidget(QListWidget, Widget):
    @overload
    def __init__(self, parent=None):
        ...
    
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setItemDelegate(ItemDelegate(self))
        self.setHorizontalScrollBar(ScrollBar(Qt.Orientation.Horizontal, self))
        self.setVerticalScrollBar(ScrollBar(Qt.Orientation.Vertical, self))
        
        self.removeEventFilter(self)
        self.viewport().installEventFilter(self)
    
    def paintEvent(self, e):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.save()
        painter.setOpacity(self.viewport().property("baseOpacity"))
        painter.setPen(getBorderColour())
        painter.setBrush(getBackgroundColour())
        painter.drawRoundedRect(self.viewport().rect().adjusted(1, 1, -1, -1), 16, 16)
        painter.restore()
        
        if self.viewport().property("frameOpacity"):
            painter.save()
            painter.setOpacity(self.viewport().property("frameOpacity"))
            painter.setPen(getBorderColour())
            painter.setBrush(getBackgroundColour())
            painter.drawRoundedRect(
                self.viewport().rect().adjusted(
                    1 + self.viewport().property("frameRectAdjustment"),
                    1 + self.viewport().property("frameRectAdjustment"),
                    -(1 + self.viewport().property("frameRectAdjustment")),
                    -(1 + self.viewport().property("frameRectAdjustment"))
                ), 16, 16
            )
            painter.restore()
        
        op = QStyleOptionFrame()
        op.initFrom(self)
        self.initStyleOption(op)
        self.setStyleSheet(
            f"color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {self.property('baseOpacity') + (self.property('frameOpacity') * (1.0 - self.property('baseOpacity')))}); background: transparent; border: none;")
        super().paintEvent(e)
