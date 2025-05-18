# -*- coding: utf-8 -*-
from typing import overload

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from .Button import CloseButton
from .ListView import ListView, ItemDelegate
from ..Windows import RoundedMenu
from ..ThemeController import *

from .Widget import Widget


class LineEdit(QLineEdit, Widget):
    @overload
    def __init__(self, parent=None):
        ...
    
    @overload
    def __init__(self, contents, parent=None):
        ...
    
    def __init__(self, *__args):
        super().__init__(*__args)
    
    def setClearButtonEnabled(self, enable):
        super().setClearButtonEnabled(enable)
        if self.findChild(QToolButton):
            old_button = self.findChild(QToolButton)
            new_button = CloseButton(old_button.parent())
            new_button.setFixedSize(old_button.size())
            new_button.move(old_button.x(), old_button.y())
            new_button.setEnabled(bool(self.text()))
            new_button.setProperty("widgetOpacity", 0.3 if not self.text() else 0.6)
            new_button.clicked.connect(old_button.clicked.emit)
            old_button.setVisible(False)
        else:
            self.findChild(CloseButton).destroy()
    
    def setCompleter(self, completer):
        super().setCompleter(completer)
        if completer:
            completer.setWidget(self)
            completerMenu = ListView(self)
            completerMenu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            completerMenu.setWindowFlags(
                Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint |
                Qt.WindowType.Popup | Qt.WindowType.Sheet
            )
            completer.setPopup(completerMenu)
            completer.popup().setItemDelegate(ItemDelegate(completerMenu))
    
    def paintEvent(self, a0):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        if self.findChild(CloseButton) and self.findChild(QToolButton):
            old_button = self.findChild(QToolButton)
            new_button = self.findChild(CloseButton)
            new_button.setFixedSize(QSize(old_button.height(), old_button.height()))
            new_button.move(old_button.x(), old_button.y())
            new_button.setEnabled(bool(self.text()))
            old_button.setVisible(False)
            
            if new_button.underMouse():
                self.setCursor(Qt.CursorShape.ArrowCursor)
            else:
                self.setCursor(Qt.CursorShape.IBeamCursor)
        painter = QPainter(self)
        painter.setOpacity(self.property("widgetOpacity"))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        borderColour = getBorderColour(is_highlight=(self.hasFocus() or self.underMouse()) and self.isEnabled())
        backgroundColour = getBackgroundColour(is_highlight=self.hasFocus() and self.isEnabled())
        borderGradient = QRadialGradient(QPointF(self.mapFromGlobal(QCursor.pos())),
                                         max(self.width(), self.height()))
        borderGradient.setColorAt(0.0, borderColour)
        borderGradient.setColorAt(1.0, Colour(
            *borderColour,
            (255 if self.hasFocus() and self.isEnabled() else 32)
        ))
        painter.setPen(QPen(QBrush(borderGradient), 1.0))
        backgroundGradient = QLinearGradient(QPointF(0, 0), QPointF(0, self.height()))
        backgroundGradient.setColorAt(0.0, backgroundColour)
        backgroundGradient.setColorAt(1.0, Colour(*backgroundColour, 210))
        painter.setBrush(QBrush(backgroundGradient))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)
        self.setStyleSheet(
            f"color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {str(painter.opacity())}); background: transparent; border: none; padding: 5px;")
        op = QStyleOptionFrame()
        op.initFrom(self)
        self.initStyleOption(op)
        super().paintEvent(a0)
    
    def contextMenuEvent(self, e):
        default = self.createStandardContextMenu()
        menu = RoundedMenu(self)
        for i in default.actions():
            menu.addAction(i)
        menu.exec(self.mapToGlobal(e.pos()))
