# -*- coding: utf-8 -*-
from typing import overload

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from ..ThemeController import *
from .ScrollBar import ScrollBar
from ..Windows import RoundedMenu

from .Widget import Widget


class ItemDelegateLineEdit(QLineEdit, Widget):
    def setClearButtonEnabled(self, enable):
        super().setClearButtonEnabled(enable)
        if self.findChild(QToolButton):
            old_button = self.findChild(QToolButton)
            new_button = CloseButton(old_button.parent())
            new_button.setFixedSize(old_button.size())
            new_button.move(old_button.x(), old_button.y())
            new_button.setEnabled(bool(self.text()))
            new_button.setProperty("baseOpacity", 0.3 if not self.text() else 0.6)
            new_button.clicked.connect(old_button.clicked.emit)
            old_button.setVisible(False)
        else:
            self.findChild(CloseButton).destroy()
    
    def paintEvent(self, a0):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.save()
        painter.setOpacity(self.property("baseOpacity"))
        painter.setPen(getBorderColour(is_highlight=self.hasFocus() and self.isEnabled()))
        painter.setBrush(getBackgroundColour(is_highlight=self.hasFocus() and self.isEnabled()))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 16, 16)
        painter.restore()
        
        if self.property("frameOpacity"):
            painter.save()
            painter.setOpacity(self.property("frameOpacity"))
            painter.setPen(getBorderColour(is_highlight=True))
            painter.setBrush(getBackgroundColour(is_highlight=self.hasFocus() and self.isEnabled()))
            painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 16, 16)
            painter.restore()
        
        self.setStyleSheet(
            f"color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {self.property('baseOpacity') + (self.property('frameOpacity') * (1.0 - self.property('baseOpacity')))}); background: transparent; selection-color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {self.property('baseOpacity') + (self.property('frameOpacity') * (1.0 - self.property('baseOpacity')))}); selection-background-color: rgb{getBorderColour(is_highlight=True, is_tuple=True)}; border: none; padding: 5px;")
        super().paintEvent(a0)
    
    def contextMenuEvent(self, e):
        super().contextMenuEvent(e)
        menus = self.findChildren(QMenu)
        if menus:
            menu = menus[-1]
            menu.BORDER_RADIUS = RoundedMenu.BORDER_RADIUS
            RoundedMenu.updateQSS(menu)
            menu.popup(QCursor.pos())


class ItemDelegate(QItemDelegate):
    def paint(self, painter, option, index):
        option.rect.setX(option.rect.x() + 10)
        option.rect.setWidth(option.rect.width() - 5)
        super().paint(painter, option, index)
    
    def createEditor(self, parent, option, index):
        editor = ItemDelegateLineEdit(parent)
        return editor


class ItemView(QAbstractItemView, Widget):
    @overload
    def __init__(self, parent=None):
        ...
    
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setItemDelegate(ItemDelegate(self))
        self.setHorizontalScrollBar(ScrollBar(Qt.Orientation.Horizontal, self))
        self.setVerticalScrollBar(ScrollBar(Qt.Orientation.Vertical, self))
    
    def paintEvent(self, e):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.save()
        painter.setOpacity(self.property("baseOpacity"))
        painter.setPen(getBorderColour())
        painter.setBrush(getBackgroundColour())
        painter.drawRoundedRect(self.viewport().rect().adjusted(1, 1, -1, -1), 16, 16)
        painter.restore()
        
        if self.property("frameOpacity"):
            painter.save()
            painter.setOpacity(self.property("frameOpacity"))
            painter.setPen(getBorderColour())
            painter.setBrush(getBackgroundColour())
            painter.drawRoundedRect(self.viewport().rect().adjusted(1, 1, -1, -1), 16, 16)
            painter.restore()
        op = QStyleOptionFrame()
        op.initFrom(self)
        self.initStyleOption(op)
        self.setStyleSheet(
            f"color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {self.viewport().property('baseOpacity') + (self.viewport().property('frameOpacity') * (1.0 - self.viewport().property('baseOpacity')))}); background: transparent; border: none;")
        super().paintEvent(e)
