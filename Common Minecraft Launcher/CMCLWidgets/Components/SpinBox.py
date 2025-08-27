# -*- coding: utf-8 -*-
from typing import overload

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from ..Windows import RoundedMenu
from ..ThemeController import *

from .Widget import Widget


class SpinBox(QSpinBox, Widget):
    @overload
    def __init__(self, parent=None):
        ...
    
    def __init__(self, *__args):
        super().__init__(*__args)
    
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
            painter.drawRoundedRect(
                self.rect().adjusted(
                    1 + self.property("frameRectAdjustment"),
                    1 + self.property("frameRectAdjustment"),
                    -(1 + self.property("frameRectAdjustment")),
                    -(1 + self.property("frameRectAdjustment"))
                ), 16, 16
            )
            painter.restore()
            
            if self.buttonSymbols() != SpinBox.ButtonSymbols.NoButtons:
                painter.save()
                painter.setOpacity(self.property("frameOpacity"))
                match self.buttonSymbols():
                    case SpinBox.ButtonSymbols.PlusMinus:
                        pass
                    case SpinBox.ButtonSymbols.UpDownArrows:
                        pass
                painter.restore()
        
        self.setStyleSheet(
            f"color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {self.property('baseOpacity') + (self.property('frameOpacity') * (1.0 - self.property('baseOpacity')))}); background: transparent; border: none; padding: 5px;")
    
    def contextMenuEvent(self, a0):
        def updateContextMenu(self):
            if self.lineEdit():
                menus = self.findChildren(QMenu)
                if menus:
                    menu = menus[-1]
                    menu.BORDER_RADIUS = RoundedMenu.BORDER_RADIUS
                    RoundedMenu.updateQSS(menu)
                    menu.popup(QCursor.pos())
        
        QTimer.singleShot(1, lambda: updateContextMenu(self))
        super().contextMenuEvent(a0)
