# -*- coding: utf-8 -*-
from typing import overload

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from ..ThemeController import *
from .ItemView import ItemDelegate
from .ScrollBar import ScrollBar

from .Widget import Widget


class ListView(QListView, Widget):
    @overload
    def __init__(self, parent=None):
        ...
    
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setItemDelegate(ItemDelegate(self))
        self.setHorizontalScrollBar(ScrollBar(Qt.Orientation.Horizontal, self))
        self.setVerticalScrollBar(ScrollBar(Qt.Orientation.Vertical, self))
        
        self.removeEventFilter(self)
        self.viewport().installEventFilter(self)
    
    def paintEvent(self, e):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self.viewport())
        painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing)
        
        rect = self.viewport().rect()
        baseOpacity = self.viewport().property("baseOpacity") or 0.85
        
        painter.save()
        painter.setOpacity(baseOpacity * 0.7)
        
        shadowColor1 = QColor(0, 0, 0, int(12 * baseOpacity))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(shadowColor1)
        shadowRect1 = rect.adjusted(6, 6, -6, -6)
        painter.drawRoundedRect(shadowRect1, 18, 18)
        
        shadowColor2 = QColor(0, 0, 0, int(8 * baseOpacity))
        painter.setBrush(shadowColor2)
        shadowRect2 = rect.adjusted(4, 4, -4, -4)
        painter.drawRoundedRect(shadowRect2, 16, 16)
        
        shadowColor3 = QColor(0, 0, 0, int(5 * baseOpacity))
        painter.setBrush(shadowColor3)
        shadowRect3 = rect.adjusted(2, 2, -2, -2)
        painter.drawRoundedRect(shadowRect3, 14, 14)
        painter.restore()
        
        painter.save()
        painter.setOpacity(baseOpacity)
        
        bgGradient = QLinearGradient(QPointF(rect.topLeft()), QPointF(rect.bottomRight()))
        bgColor = getBackgroundColour()
        
        bgColorLight = QColor(
            min(255, bgColor.red() + 20),
            min(255, bgColor.green() + 20),
            min(255, bgColor.blue() + 20)
        )
        bgColorMid = QColor(
            min(255, bgColor.red() + 10),
            min(255, bgColor.green() + 10),
            min(255, bgColor.blue() + 10)
        )
        
        bgGradient.setColorAt(0.0, bgColorLight)
        bgGradient.setColorAt(0.3, bgColorMid)
        bgGradient.setColorAt(0.7, bgColorMid)
        bgGradient.setColorAt(1.0, bgColor)
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(bgGradient)
        painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 16, 16)
        painter.restore()
        
        painter.save()
        painter.setOpacity(baseOpacity * 0.3)
        
        glowColor = QColor(255, 255, 255, int(180 * baseOpacity))
        painter.setPen(QPen(glowColor, 1.5))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect.adjusted(2, 2, -2, -2), 14, 14)
        painter.restore()
        
        painter.save()
        painter.setOpacity(baseOpacity * 0.9)
        
        borderGradient = QLinearGradient(QPointF(rect.topLeft()), QPointF(rect.bottomLeft()))
        borderColor = getBorderColour()
        borderColorDarker = QColor(
            max(0, borderColor.red() - 20),
            max(0, borderColor.green() - 20),
            max(0, borderColor.blue() - 20)
        )
        
        borderGradient.setColorAt(0.0, borderColorDarker)
        borderGradient.setColorAt(0.5, borderColor)
        borderGradient.setColorAt(1.0, borderColor)
        
        penBorder = QPen(borderGradient, 1.0)
        painter.setPen(penBorder)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 16, 16)
        painter.restore()
        
        op = QStyleOptionFrame()
        op.initFrom(self)
        self.initStyleOption(op)
        self.setStyleSheet(
            f"color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {self.property('baseOpacity') + (self.property('frameOpacity') * (1.0 - self.property('baseOpacity')))}); background: transparent; border: none;")
        super().paintEvent(e)


class ListWidget(QListWidget, Widget):
    @overload
    def __init__(self, parent=None):
        ...
    
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setItemDelegate(ItemDelegate(self))
        self.setHorizontalScrollBar(ScrollBar(Qt.Orientation.Horizontal, self))
        self.setVerticalScrollBar(ScrollBar(Qt.Orientation.Vertical, self))
        
        self.removeEventFilter(self)
        self.viewport().installEventFilter(self)
    
    def paintEvent(self, e):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self.viewport())
        painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing)
        
        rect = self.viewport().rect()
        baseOpacity = self.viewport().property("baseOpacity") or 0.85
        
        painter.save()
        painter.setOpacity(baseOpacity * 0.7)
        
        shadowColor1 = QColor(0, 0, 0, int(12 * baseOpacity))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(shadowColor1)
        shadowRect1 = rect.adjusted(6, 6, -6, -6)
        painter.drawRoundedRect(shadowRect1, 18, 18)
        
        shadowColor2 = QColor(0, 0, 0, int(8 * baseOpacity))
        painter.setBrush(shadowColor2)
        shadowRect2 = rect.adjusted(4, 4, -4, -4)
        painter.drawRoundedRect(shadowRect2, 16, 16)
        
        shadowColor3 = QColor(0, 0, 0, int(5 * baseOpacity))
        painter.setBrush(shadowColor3)
        shadowRect3 = rect.adjusted(2, 2, -2, -2)
        painter.drawRoundedRect(shadowRect3, 14, 14)
        painter.restore()
        
        painter.save()
        painter.setOpacity(baseOpacity)
        
        bgGradient = QLinearGradient(QPointF(rect.topLeft()), QPointF(rect.bottomRight()))
        bgColor = getBackgroundColour()
        
        bgColorLight = QColor(
            min(255, bgColor.red() + 20),
            min(255, bgColor.green() + 20),
            min(255, bgColor.blue() + 20)
        )
        bgColorMid = QColor(
            min(255, bgColor.red() + 10),
            min(255, bgColor.green() + 10),
            min(255, bgColor.blue() + 10)
        )
        
        bgGradient.setColorAt(0.0, bgColorLight)
        bgGradient.setColorAt(0.3, bgColorMid)
        bgGradient.setColorAt(0.7, bgColorMid)
        bgGradient.setColorAt(1.0, bgColor)
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(bgGradient)
        painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 16, 16)
        painter.restore()
        
        painter.save()
        painter.setOpacity(baseOpacity * 0.3)
        
        glowColor = QColor(255, 255, 255, int(180 * baseOpacity))
        painter.setPen(QPen(glowColor, 1.5))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect.adjusted(2, 2, -2, -2), 14, 14)
        painter.restore()
        
        painter.save()
        painter.setOpacity(baseOpacity * 0.9)
        
        borderGradient = QLinearGradient(QPointF(rect.topLeft()), QPointF(rect.bottomLeft()))
        borderColor = getBorderColour()
        borderColorDarker = QColor(
            max(0, borderColor.red() - 20),
            max(0, borderColor.green() - 20),
            max(0, borderColor.blue() - 20)
        )
        
        borderGradient.setColorAt(0.0, borderColorDarker)
        borderGradient.setColorAt(0.5, borderColor)
        borderGradient.setColorAt(1.0, borderColor)
        
        penBorder = QPen(borderGradient, 1.0)
        painter.setPen(penBorder)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 16, 16)
        painter.restore()
        
        op = QStyleOptionFrame()
        op.initFrom(self)
        self.initStyleOption(op)
        self.setStyleSheet(
            f"color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {self.property('baseOpacity') + (self.property('frameOpacity') * (1.0 - self.property('baseOpacity')))}); background: transparent; border: none;")
        super().paintEvent(e)
