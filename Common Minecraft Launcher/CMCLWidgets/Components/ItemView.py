# -*- coding: utf-8 -*-
from typing import overload

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from ..ThemeController import *
from .ScrollBar import ScrollBar

from .Widget import Widget


class ItemDelegate(QItemDelegate):
    def paint(self, painter, option, index):
        option.rect.setX(option.rect.x() + 10)
        option.rect.setWidth(option.rect.width() - 5)
        super().paint(painter, option, index)
        # self.drawDecoration(painter, option, option.rect, QPixmap())
        # self.drawDisplay(painter, option, option.rect, index.data())
    
    def drawDecoration(self, painter, option, rect, pixmap):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rectAdjustmentRatio = (min(option.rect.width() // 2, option.rect.height() // 2)
                               / min(32, min(self.parent().viewport().width() // 2,
                                             self.parent().viewport().height() // 2)))
        
        painter.save()
        painter.setOpacity(self.parent().viewport().property("baseOpacity"))
        painter.setPen(getBorderColour())
        painter.setBrush(getBackgroundColour())
        painter.drawRoundedRect(option.rect.adjusted(1, 1, -1, -1), 16, 16)
        painter.restore()
        
        if self.parent().viewport().property("frameOpacity") and \
                ((option.rect.contains(QCursor.pos() - (self.parent().viewport().mapToGlobal(
                    QPoint(0, 0))))) and self.parent().underMouse()) and self.parent().isEnabled():
            painter.save()
            painter.setOpacity(self.parent().viewport().property("frameOpacity"))
            painter.setPen(getBorderColour(
                is_highlight=((option.rect.contains(QCursor.pos() - (self.parent().viewport().mapToGlobal(
                    QPoint(0, 0))))) and self.parent().underMouse()) and self.parent().isEnabled()
            ))
            painter.setBrush(getBackgroundColour())
            painter.drawRoundedRect(option.rect.adjusted(1, 1, -1, -1), 16, 16)
            painter.restore()
    
    def drawFocus(self, painter, option, rect):
        pass
    
    def drawBackground(self, painter, option, rect):
        pass
    
    def drawDisplay(self, painter, option, rect, text):
        painter.save()
        if ((option.rect.contains(QCursor.pos() - (self.parent().viewport().mapToGlobal(
                QPoint(0, 0))))) and self.parent().underMouse()) and self.parent().isEnabled():
            painter.setOpacity(self.parent().viewport().property("baseOpacity")
                               + (self.parent().viewport().property("frameOpacity") * (
                    1.0 - self.parent().viewport().property("baseOpacity"))))
        else:
            painter.setOpacity(self.parent().viewport().property("baseOpacity"))
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)
        painter.setPen(getForegroundColour())
        painter.drawText(option.rect.adjusted(1, 1, -1, -1), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                         text)
        painter.restore()


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
