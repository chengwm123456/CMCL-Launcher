# -*- coding: utf-8 -*-
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from ..ThemeController import *
from .ItemView import ItemDelegate
from .ScrollBar import ScrollBar

from .Widget import Widget


class HeaderView(QHeaderView, Widget):
    def __init__(self, orientation, parent):
        super().__init__(orientation, parent)
        rect = self.fontMetrics().boundingRect(str(self.count()))
        match self.orientation():
            case Qt.Orientation.Horizontal:
                self.setFixedHeight(rect.height() + 10)
        self.setHorizontalScrollBar(ScrollBar(Qt.Orientation.Horizontal, self))
        self.setVerticalScrollBar(ScrollBar(Qt.Orientation.Vertical, self))
    
    def paintEvent(self, e):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        rect = self.fontMetrics().boundingRect(str(self.count()))
        match self.orientation():
            case Qt.Orientation.Horizontal:
                self.setFixedHeight(rect.height() + 10)
        painter = QPainter(self.viewport())
        painter.setOpacity(self.property("widgetOpacity"))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getBorderColour())
        painter.setBrush(getBackgroundColour())
        rect = self.viewport().rect()
        rect.setWidth(rect.width() - rect.x() - 1)
        rect.setHeight(rect.height() - rect.y() - 1)
        rect.setX(1)
        rect.setY(1)
        painter.drawRoundedRect(rect, 10, 10)
        # self.setStyleSheet(
        #     f"color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {str(painter.opacity())}); background: transparent; border: none;")
        # super().paintEvent(e)
        # return
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
            size = self.style().sizeFromContents(QStyle.ContentsType.CT_HeaderSection, op, self.size(), self)
            x = y = width = height = 0
            match self.orientation():
                case Qt.Orientation.Horizontal:
                    x = self.parent().columnViewportPosition(section)
                    height = self.height()
                    width = self.parent().columnWidth(section)
                case Qt.Orientation.Vertical:
                    y = self.parent().rowViewportPosition(section)
                    width = self.width()
                    height = self.parent().rowHeight(section)
            op.rect = QRect(x + 1, y + 1, width, height)
            
            op.palette.setColor(op.palette.ColorRole.Text, getForegroundColour())
            painter.save()
            painter.setPen(getForegroundColour())
            painter.drawText(op.rect, op.textAlignment, op.text)
            painter.restore()


class TableView(QTableView, Widget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setVerticalHeader(HeaderView(Qt.Orientation.Vertical, self))
        self.setHorizontalHeader(HeaderView(Qt.Orientation.Horizontal, self))
        self.setItemDelegate(ItemDelegate(self))
        self.setShowGrid(False)
        self.setHorizontalScrollBar(ScrollBar(Qt.Orientation.Horizontal, self))
        self.setVerticalScrollBar(ScrollBar(Qt.Orientation.Vertical, self))
    
    def paintEvent(self, e):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self.viewport())
        painter.setOpacity(self.property("widgetOpacity"))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getBorderColour())
        painter.setBrush(getBackgroundColour())
        rect = self.viewport().rect()
        rect.setWidth(rect.width() - rect.x() - 1)
        rect.setHeight(rect.height() - rect.y() - 1)
        rect.setX(1)
        rect.setY(1)
        painter.drawRoundedRect(rect, 10, 10)
        self.setShowGrid(False)
        op = QStyleOptionFrame()
        op.initFrom(self)
        self.initStyleOption(op)
        self.setStyleSheet(
            f"color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {str(painter.opacity())}); background: transparent; border: none;")
        super().paintEvent(e)


class TableWidget(QTableWidget, Widget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setVerticalHeader(HeaderView(Qt.Orientation.Vertical, self))
        self.setHorizontalHeader(HeaderView(Qt.Orientation.Horizontal, self))
        self.setItemDelegate(ItemDelegate(self))
        self.setShowGrid(False)
        self.setHorizontalScrollBar(ScrollBar(Qt.Orientation.Horizontal, self))
        self.setVerticalScrollBar(ScrollBar(Qt.Orientation.Vertical, self))
    
    def paintEvent(self, e):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self.viewport())
        painter.setOpacity(self.property("widgetOpacity"))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getBorderColour())
        painter.setBrush(getBackgroundColour())
        rect = self.viewport().rect()
        rect.setWidth(rect.width() - rect.x() - 1)
        rect.setHeight(rect.height() - rect.y() - 1)
        rect.setX(1)
        rect.setY(1)
        painter.drawRoundedRect(rect, 10, 10)
        self.setShowGrid(False)
        op = QStyleOptionFrame()
        op.initFrom(self)
        self.initStyleOption(op)
        self.setStyleSheet(
            f"color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {str(painter.opacity())}); background: transparent; border: none;")
        super().paintEvent(e)
