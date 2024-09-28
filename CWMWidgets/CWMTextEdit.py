# -*- coding: utf-8 -*-
from typing import overload

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from .CWMWindows import RoundedMenu
from .CWMThemeControl import *
from .CWMToolTip import ToolTip
from .CWMScrollBar import ScrollBar


class TextEdit(QTextEdit):
    @overload
    def __init__(self, parent=None):
        ...
    
    @overload
    def __init__(self, text, parent=None):
        ...
    
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.installEventFilter(ToolTip(self))
        self.setHorizontalScrollBar(ScrollBar(Qt.Orientation.Horizontal, self))
        self.setVerticalScrollBar(ScrollBar(Qt.Orientation.Vertical, self))
    
    def paintEvent(self, e):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self.viewport())
        painter.setOpacity(1.0 if self.hasFocus() or self.underMouse() else 0.6)
        if not self.isEnabled():
            painter.setOpacity(0.3)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getBorderColour(highlight=(self.hasFocus() or self.underMouse()) and self.isEnabled()))
        painter.setBrush(getBackgroundColour(highlight=self.hasFocus() and self.isEnabled()))
        rect = self.contentsRect()
        rect.setWidth(rect.width() - rect.x() - 1)
        rect.setHeight(rect.height() - rect.y() - 1)
        rect.setX(1)
        rect.setY(1)
        painter.drawRoundedRect(rect, 10, 10)
        self.setStyleSheet(
            f"color: rgba({str(getForegroundColour(is_tuple=True)).replace('(', '').replace(')', '')}, {str(painter.opacity())}); background: transparent; border: none; padding: 5px;")
        op = QStyleOptionFrame()
        op.initFrom(self)
        self.initStyleOption(op)
        super().paintEvent(e)
    
    def contextMenuEvent(self, e):
        default = self.createStandardContextMenu()
        menu = RoundedMenu(self)
        for i in default.actions():
            menu.addAction(i)
        menu.exec(self.mapToGlobal(e.pos()))


class PlainTextEdit(QPlainTextEdit):
    @overload
    def __init__(self, parent=None):
        ...
    
    @overload
    def __init__(self, text, parent=None):
        ...
    
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.installEventFilter(ToolTip(self))
        self.setHorizontalScrollBar(ScrollBar(Qt.Orientation.Horizontal, self))
        self.setVerticalScrollBar(ScrollBar(Qt.Orientation.Vertical, self))
    
    def paintEvent(self, e):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self.viewport())
        painter.setOpacity(1.0 if self.hasFocus() or self.underMouse() else 0.6)
        if not self.isEnabled():
            painter.setOpacity(0.3)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getBorderColour(highlight=(self.hasFocus() or self.underMouse()) and self.isEnabled()))
        painter.setBrush(getBackgroundColour(highlight=self.hasFocus() and self.isEnabled()))
        rect = self.contentsRect()
        rect.setWidth(rect.width() - rect.x() - 1)
        rect.setHeight(rect.height() - rect.y() - 1)
        rect.setX(1)
        rect.setY(1)
        painter.drawRoundedRect(rect, 10, 10)
        self.setStyleSheet(
            f"color: rgba({str(getForegroundColour(is_tuple=True)).replace('(', '').replace(')', '')}, {str(painter.opacity())}); background: transparent; border: none; padding: 5px;")
        op = QStyleOptionFrame()
        op.initFrom(self)
        self.initStyleOption(op)
        super().paintEvent(e)
    
    def contextMenuEvent(self, e):
        default = self.createStandardContextMenu()
        menu = RoundedMenu(self)
        for i in default.actions():
            menu.addAction(i)
        menu.exec(self.mapToGlobal(e.pos()))
