# -*- coding: utf-8 -*-
from typing import overload

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from .CWMThemeControl import *
from .CWMToolTip import ToolTip
from .CWMScrollBar import ScrollBar


class ItemDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        option.rect.setX(option.rect.x() + 5)
        option.rect.setWidth(option.rect.width() - 5)
        super().paint(painter, option, index)
        
        painter.save()
        painter.setClipRegion(
            QRegion(self.parent().rect().adjusted(2, 2, -2, -40),
                    QRegion.RegionType.Rectangle))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getBorderColour())
        painter.drawRoundedRect(option.rect.adjusted(1, 1, -1, -1), 10, 10)
        painter.restore()


class ItemView(QAbstractItemView):
    @overload
    def __init__(self, parent=None):
        ...
    
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.installEventFilter(ToolTip(self))
        self.setItemDelegate(ItemDelegate(self))
        self.setHorizontalScrollBar(ScrollBar(Qt.Orientation.Horizontal, self))
        self.setVerticalScrollBar(ScrollBar(Qt.Orientation.Vertical, self))
    
    def paintEvent(self, e):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self.viewport())
        painter.setOpacity(1.0 if self.viewport().underMouse() or self.viewport().hasFocus() else 0.6)
        if not self.isEnabled():
            painter.setOpacity(0.3)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(
            getBorderColour(
                highlight=(self.viewport().underMouse() or self.viewport().hasFocus()) and self.isEnabled()))
        painter.setBrush(getBackgroundColour(
            highlight=self.viewport().hasFocus() and self.isEnabled()))
        rect = self.viewport().rect()
        rect.setWidth(rect.width() - rect.x() - 1)
        rect.setHeight(rect.height() - rect.y() - 1)
        rect.setX(1)
        rect.setY(1)
        painter.drawRoundedRect(rect, 10, 10)
        op = QStyleOptionFrame()
        op.initFrom(self)
        self.initStyleOption(op)
        self.setStyleSheet(
            f"color: rgba({str(getForegroundColour(tuple=True)).replace('(', '').replace(')', '')}, {str(painter.opacity())}); background: transparent; border: none;")
        super().paintEvent(e)
