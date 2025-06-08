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
    
    def paintEvent(self, e):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self.viewport())
        painter.setOpacity(self.property("widgetOpacity"))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.viewport().rect().adjusted(1, 1, -1, -1)
        borderColour = getBorderColour(is_highlight=(self.hasFocus() or self.underMouse()) and self.isEnabled())
        backgroundColour = getBackgroundColour(is_highlight=self.hasFocus() and self.isEnabled())
        borderGradient = QRadialGradient(QPointF(self.mapFromGlobal(QCursor.pos())),
                                         max(rect.width(), rect.height()))
        borderGradient.setColorAt(0.0, borderColour)
        borderGradient.setColorAt(1.0, Colour(
            *borderColour,
            (255 if self.hasFocus() and self.isEnabled() else 32)
        ))
        painter.setPen(QPen(QBrush(borderGradient), 1.0))
        backgroundGradient = QLinearGradient(QPointF(0, 0), QPointF(0, rect.height()))
        backgroundGradient.setColorAt(0.0, backgroundColour)
        backgroundGradient.setColorAt(1.0, Colour(*backgroundColour, 210))
        painter.setBrush(QBrush(backgroundGradient))
        painter.drawRoundedRect(rect, 10, 10)
        self.setStyleSheet(
            f"color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {str(painter.opacity())}); background: transparent; border: none; padding: 5px;")
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
    
    def paintEvent(self, e):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self.viewport())
        painter.setOpacity(self.property("widgetOpacity"))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.viewport().rect().adjusted(1, 1, -1, -1)
        borderColour = getBorderColour(is_highlight=(self.hasFocus() or self.underMouse()) and self.isEnabled())
        backgroundColour = getBackgroundColour(is_highlight=self.hasFocus() and self.isEnabled())
        borderGradient = QRadialGradient(QPointF(self.mapFromGlobal(QCursor.pos())),
                                         max(rect.width(), rect.height()))
        borderGradient.setColorAt(0.0, borderColour)
        borderGradient.setColorAt(1.0, Colour(
            *borderColour,
            (255 if self.hasFocus() and self.isEnabled() else 32)
        ))
        painter.setPen(QPen(QBrush(borderGradient), 1.0))
        backgroundGradient = QLinearGradient(QPointF(0, 0), QPointF(0, rect.height()))
        backgroundGradient.setColorAt(0.0, backgroundColour)
        backgroundGradient.setColorAt(1.0, Colour(*backgroundColour, 210))
        painter.setBrush(QBrush(backgroundGradient))
        painter.drawRoundedRect(rect, 10, 10)
        self.setStyleSheet(
            f"color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {str(painter.opacity())}); background: transparent; border: none; padding: 5px;")
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
