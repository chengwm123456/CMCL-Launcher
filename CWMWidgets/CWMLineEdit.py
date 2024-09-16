# -*- coding: utf-8 -*-
from typing import overload

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from .CWMToolTip import ToolTip
from .CWMWindows import RoundedMenu
from .CWMThemeControl import *


class LineEdit(QLineEdit):
    @overload
    def __init__(self, parent=None):
        ...
    
    @overload
    def __init__(self, contents, parent=None):
        ...
    
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.installEventFilter(ToolTip(self))
    
    def paintEvent(self, a0):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self)
        painter.setOpacity(1.0 if self.hasFocus() or self.underMouse() else 0.6)
        if not self.isEnabled():
            painter.setOpacity(0.3)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getBorderColour(highlight=self.hasFocus() or self.underMouse()))
        painter.setBrush(getBackgroundColour(highlight=self.hasFocus()))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)
        self.setStyleSheet(
            f"color: rgba({str(getForegroundColour(tuple=True)).replace('(', '').replace(')', '')}, {str(painter.opacity())}); background: transparent; border: none; padding: 5px;")
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
