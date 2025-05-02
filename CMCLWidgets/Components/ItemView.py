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
        painter.save()
        painter.setOpacity(self.parent().property("widgetOpacity") or 1.0)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)
        borderColour = getBorderColour(
            is_highlight=((option.rect.contains(QCursor.pos() - (
                self.parent().viewport().mapToGlobal(QPoint(0, 0))
                if hasattr(self.parent(), "viewport")
                else self.parent().mapToGlobal(QPoint(0, 0))
            ))) and self.parent().underMouse()) and self.parent().isEnabled()
        )
        backgroundColour = getBackgroundColour()
        borderGradient = QRadialGradient(
            QPointF(
                self.parent().viewport().mapFromGlobal(QCursor.pos())
                if hasattr(self.parent(), "viewport")
                else self.parent().mapFromGlobal(QCursor.pos())
            ),
            max(option.rect.width(), option.rect.height())
        )
        borderGradient.setColorAt(0.0, borderColour)
        borderGradient.setColorAt(1.0, Colour(*borderColour, 32))
        painter.setPen(QPen(QBrush(borderGradient), 1))
        backgroundGradient = QLinearGradient(QPointF(0, option.rect.y()),
                                             QPointF(0, option.rect.y() + option.rect.height()))
        backgroundGradient.setColorAt(0.0, backgroundColour)
        backgroundGradient.setColorAt(1.0, Colour(*backgroundColour, 210))
        painter.setBrush(QBrush(backgroundGradient))
        painter.drawRoundedRect(option.rect.adjusted(1, 1, -1, -1), 10, 10)
        painter.restore()
    
    def drawFocus(self, painter, option, rect):
        pass
    
    def drawBackground(self, painter, option, rect):
        pass
    
    def drawDisplay(self, painter, option, rect, text):
        painter.save()
        painter.setOpacity(self.parent().property("widgetOpacity") or 1.0)
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
        painter.setOpacity(self.property("widgetOpacity"))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.viewport().rect()
        rect.setWidth(rect.width() - rect.x() - 1)
        rect.setHeight(rect.height() - rect.y() - 1)
        rect.setX(1)
        rect.setY(1)
        borderColour = getBorderColour()
        backgroundColour = getBackgroundColour()
        borderGradient = QRadialGradient(QPointF(self.mapFromGlobal(QCursor.pos())),
                                         max(rect.width(), rect.height()))
        borderGradient.setColorAt(0.0, borderColour)
        borderGradient.setColorAt(1.0, Colour(*borderColour, 32))
        painter.setPen(QPen(QBrush(borderGradient), 1))
        backgroundGradient = QLinearGradient(QPointF(0, 0), QPointF(0, rect.height()))
        backgroundGradient.setColorAt(0.0, backgroundColour)
        backgroundGradient.setColorAt(1.0, Colour(*backgroundColour, 210))
        painter.setBrush(QBrush(backgroundGradient))
        painter.drawRoundedRect(rect, 10, 10)
        op = QStyleOptionFrame()
        op.initFrom(self)
        self.initStyleOption(op)
        self.setStyleSheet(
            f"color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {str(painter.opacity())}); background: transparent; border: none;")
        super().paintEvent(e)
