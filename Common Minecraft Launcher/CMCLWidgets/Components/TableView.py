# -*- coding: utf-8 -*-
from typing import overload

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from ..ThemeController import *
from .ItemView import ItemDelegate
from .ScrollBar import ScrollBar

from .Widget import Widget


class HeaderView(QHeaderView, Widget):
    def __init__(self, orientation, parent):
        super().__init__(orientation, parent)
        match self.orientation():
            case Qt.Orientation.Horizontal:
                self.adjustSize()
                self.setFixedHeight(self.height())
        self.setHorizontalScrollBar(ScrollBar(Qt.Orientation.Horizontal, self))
        self.setVerticalScrollBar(ScrollBar(Qt.Orientation.Vertical, self))
        
        self.removeEventFilter(self)
        self.viewport().installEventFilter(self)
    
    def paintEvent(self, e):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        match self.orientation():
            case Qt.Orientation.Horizontal:
                self.adjustSize()
                self.setFixedHeight(self.height())
        
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.save()
        painter.setOpacity(self.viewport().property("baseOpacity"))
        painter.setPen(getBorderColour())
        painter.setBrush(getBackgroundColour())
        painter.drawRoundedRect(self.viewport().rect().adjusted(1, 1, -1, -1), 16, 16)
        painter.restore()
        
        if self.viewport().property("frameOpacity"):
            painter.save()
            painter.setOpacity(self.viewport().property("frameOpacity"))
            painter.setPen(getBorderColour())
            painter.setBrush(getBackgroundColour())
            painter.drawRoundedRect(self.viewport().rect().adjusted(1, 1, -1, -1), 16, 16)
            painter.restore()
        
        pp = QPainterPath()
        pp.addRoundedRect(self.viewport().rect().toRectF().adjusted(1.625, 1.625, -1.625, -1.625), 16, 16)
        painter.setClipPath(pp)
        for section in range(self.count()):
            op = QStyleOptionHeader()
            op.initFrom(self)
            self.initStyleOption(op)
            op.section = section + 1
            op.text = str(self.model().headerData(section, self.orientation()))
            op.textAlignment = self.defaultAlignment()
            op.orientation = self.orientation()
            op.sortIndicatorOrder = self.sortIndicatorOrder()
            if self.count() > 1:
                op.position = QStyleOptionHeader.SectionPosition.Middle
                if section == 0:
                    op.position = QStyleOptionHeader.SectionPosition.Beginning
                if section == self.count() - 1:
                    op.position = QStyleOptionHeader.SectionPosition.End
            else:
                op.position = QStyleOptionHeader.SectionPosition.OnlyOneSection
            x = y = width = height = 0
            match self.orientation():
                case Qt.Orientation.Horizontal:
                    x = self.parent().columnViewportPosition(section)
                    width = self.parent().columnWidth(section)
                    y += 2
                    height = self.height()
                    op.textAlignment = op.textAlignment | Qt.AlignmentFlag.AlignCenter
                case Qt.Orientation.Vertical:
                    y = self.parent().rowViewportPosition(section)
                    height = self.parent().rowHeight(section)
                    x -= 3
                    width = self.width()
                    op.textAlignment = op.textAlignment | Qt.AlignmentFlag.AlignCenter
            op.rect = QRect(x, y, width, height).adjusted(1, 1, -1, -1)
            
            painter.save()
            painter.setOpacity(self.viewport().property("baseOpacity") + (
                    self.viewport().property("frameOpacity") * (1.0 - self.viewport().property("baseOpacity"))))
            painter.setPen(getForegroundColour())
            painter.drawText(op.rect, Qt.AlignmentFlag.AlignHCenter, op.text)
            painter.restore()


class TableView(QTableView, Widget):
    @overload
    def __init__(self, parent=None):
        ...
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setVerticalHeader(HeaderView(Qt.Orientation.Vertical, self))
        self.setHorizontalHeader(HeaderView(Qt.Orientation.Horizontal, self))
        self.setItemDelegate(ItemDelegate(self))
        self.setShowGrid(False)
        self.setHorizontalScrollBar(ScrollBar(Qt.Orientation.Horizontal, self))
        self.setVerticalScrollBar(ScrollBar(Qt.Orientation.Vertical, self))
        
        self.removeEventFilter(self)
        self.viewport().installEventFilter(self)
    
    def paintEvent(self, e):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.save()
        painter.setOpacity(self.viewport().property("baseOpacity"))
        painter.setPen(getBorderColour())
        painter.setBrush(getBackgroundColour())
        painter.drawRoundedRect(self.viewport().rect().adjusted(1, 1, -1, -1), 16, 16)
        painter.restore()
        
        if self.viewport().property("frameOpacity"):
            painter.save()
            painter.setOpacity(self.viewport().property("frameOpacity"))
            painter.setPen(getBorderColour())
            painter.setBrush(getBackgroundColour())
            painter.drawRoundedRect(self.viewport().rect().adjusted(1, 1, -1, -1), 16, 16)
            painter.restore()
        
        self.setShowGrid(False)
        op = QStyleOptionFrame()
        op.initFrom(self)
        self.initStyleOption(op)
        self.setStyleSheet(
            f"color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {self.viewport().property('baseOpacity') + (self.viewport().property('frameOpacity') * (1.0 - self.viewport().property('baseOpacity')))}); background: transparent; border: none;")
        super().paintEvent(e)


class TableWidget(QTableWidget, Widget):
    @overload
    def __init__(self, parent=None):
        ...
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setVerticalHeader(HeaderView(Qt.Orientation.Vertical, self))
        self.setHorizontalHeader(HeaderView(Qt.Orientation.Horizontal, self))
        self.setItemDelegate(ItemDelegate(self))
        self.setShowGrid(False)
        self.setHorizontalScrollBar(ScrollBar(Qt.Orientation.Horizontal, self))
        self.setVerticalScrollBar(ScrollBar(Qt.Orientation.Vertical, self))
        
        self.removeEventFilter(self)
        self.viewport().installEventFilter(self)
    
    def paintEvent(self, e):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.save()
        painter.setOpacity(self.viewport().property("baseOpacity"))
        painter.setPen(getBorderColour())
        painter.setBrush(getBackgroundColour())
        painter.drawRoundedRect(self.viewport().rect().adjusted(1, 1, -1, -1), 16, 16)
        painter.restore()
        
        if self.viewport().property("frameOpacity"):
            painter.save()
            painter.setOpacity(self.viewport().property("frameOpacity"))
            painter.setPen(getBorderColour())
            painter.setBrush(getBackgroundColour())
            painter.drawRoundedRect(self.viewport().rect().adjusted(1, 1, -1, -1), 16, 16)
            painter.restore()
        
        self.setShowGrid(False)
        op = QStyleOptionFrame()
        op.initFrom(self)
        self.initStyleOption(op)
        self.setStyleSheet(
            f"color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {self.viewport().property('baseOpacity') + (self.viewport().property('frameOpacity') * (1.0 - self.viewport().property('baseOpacity')))}); background: transparent; border: none;")
        super().paintEvent(e)
