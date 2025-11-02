# -*- coding: utf-8 -*-
from typing import overload

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from ..Windows import RoundedMenu
from ..ThemeController import *
from .ScrollBar import ScrollBar

from .Widget import Widget


class TextEdit(QTextEdit, Widget):
    @overload
    def __init__(self, parent=None):
        ...
    
    @overload
    def __init__(self, text, parent=None):
        ...
    
    def __init__(self, *__args):
        super().__init__(*__args)
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
        painter.setPen(getBorderColour(is_highlight=self.hasFocus() and self.isEnabled()))
        painter.setBrush(getBackgroundColour(is_highlight=self.hasFocus() and self.isEnabled()))
        painter.drawRoundedRect(self.viewport().rect().adjusted(1, 1, -1, -1), 16, 16)
        painter.restore()
        
        if self.viewport().property("frameOpacity"):
            painter.save()
            painter.setOpacity(self.viewport().property("frameOpacity"))
            painter.setPen(getBorderColour(is_highlight=True))
            painter.setBrush(getBackgroundColour(is_highlight=self.hasFocus() and self.isEnabled()))
            painter.drawRoundedRect(
                self.viewport().rect().adjusted(
                    1 + self.viewport().property("frameRectAdjustment"),
                    1 + self.viewport().property("frameRectAdjustment"),
                    -(1 + self.viewport().property("frameRectAdjustment")),
                    -(1 + self.viewport().property("frameRectAdjustment"))
                ), 16, 16
            )
            painter.restore()
        
        self.setStyleSheet(
            f"color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {self.viewport().property('baseOpacity') + (self.viewport().property('frameOpacity') * (1.0 - self.viewport().property('baseOpacity')))}); background: transparent; selection-color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {self.viewport().property('baseOpacity') + (self.viewport().property('frameOpacity') * (1.0 - self.viewport().property('baseOpacity')))}); selection-background-color: rgb{getBorderColour(is_highlight=True, is_tuple=True)}; border: none; padding: 5px;")
        op = QStyleOptionFrame()
        op.initFrom(self)
        self.initStyleOption(op)
        super().paintEvent(e)
    
    def contextMenuEvent(self, e):
        super().contextMenuEvent(e)
        menus = self.findChildren(QMenu)
        if menus:
            menu = menus[-1]
            menu.BORDER_RADIUS = RoundedMenu.BORDER_RADIUS
            RoundedMenu.updateQSS(menu)
            menu.popup(QCursor.pos())


class PlainTextEdit(QPlainTextEdit, Widget):
    @overload
    def __init__(self, parent=None):
        ...
    
    @overload
    def __init__(self, text, parent=None):
        ...
    
    def __init__(self, *__args):
        super().__init__(*__args)
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
        painter.setPen(getBorderColour(is_highlight=self.hasFocus() and self.isEnabled()))
        painter.setBrush(getBackgroundColour(is_highlight=self.hasFocus() and self.isEnabled()))
        painter.drawRoundedRect(self.viewport().rect().adjusted(1, 1, -1, -1), 16, 16)
        painter.restore()
        
        if self.viewport().property("frameOpacity"):
            painter.save()
            painter.setOpacity(self.viewport().property("frameOpacity"))
            painter.setPen(getBorderColour(is_highlight=True))
            painter.setBrush(getBackgroundColour(is_highlight=self.hasFocus() and self.isEnabled()))
            painter.drawRoundedRect(
                self.viewport().rect().adjusted(
                    1 + self.viewport().property("frameRectAdjustment"),
                    1 + self.viewport().property("frameRectAdjustment"),
                    -(1 + self.viewport().property("frameRectAdjustment")),
                    -(1 + self.viewport().property("frameRectAdjustment"))
                ), 16, 16
            )
            painter.restore()
        
        self.setStyleSheet(
            f"color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {self.viewport().property('baseOpacity') + (self.viewport().property('frameOpacity') * (1.0 - self.viewport().property('baseOpacity')))}); background: transparent; selection-color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {self.viewport().property('baseOpacity') + (self.viewport().property('frameOpacity') * (1.0 - self.viewport().property('baseOpacity')))}); selection-background-color: rgb{getBorderColour(is_highlight=True, is_tuple=True)}; border: none; padding: 5px;")
        op = QStyleOptionFrame()
        op.initFrom(self)
        self.initStyleOption(op)
        super().paintEvent(e)
    
    def contextMenuEvent(self, e):
        super().contextMenuEvent(e)
        menus = self.findChildren(QMenu)
        if menus:
            menu = menus[-1]
            menu.BORDER_RADIUS = RoundedMenu.BORDER_RADIUS
            RoundedMenu.updateQSS(menu)
            menu.popup(QCursor.pos())
