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
        match self.orientation():
            case Qt.Orientation.Horizontal:
                self.adjustSize()
                self.setFixedHeight(self.height())
        self.setHorizontalScrollBar(ScrollBar(Qt.Orientation.Horizontal, self))
        self.setVerticalScrollBar(ScrollBar(Qt.Orientation.Vertical, self))
    
    def paintEvent(self, e):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        match self.orientation():
            case Qt.Orientation.Horizontal:
                self.adjustSize()
                self.setFixedHeight(self.height())
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
        borderGradient.setColorAt(1.0, Colour(
            *borderColour,
            (255 if self.hasFocus() and self.isEnabled() else 32)
        ))
        painter.setPen(QPen(QBrush(borderGradient), 1.0))
        backgroundGradient = QLinearGradient(QPointF(0, 0), QPointF(0, rect.height()))
        backgroundGradient.setColorAt(0.0, backgroundColour)
        backgroundGradient.setColorAt(1.0, Colour(*backgroundColour, 210))
        painter.setBrush(QBrush(backgroundGradient))
        painter.drawRoundedRect(rect, 10, 10)
        pp = QPainterPath()
        pp.addRoundedRect(QRectF(rect).adjusted(.625, .625, -.625, -.625), 10, 10)
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
            
            op.palette.setColor(op.palette.ColorRole.Text, getForegroundColour())
            painter.save()
            painter.setPen(getForegroundColour())
            painter.drawText(op.rect, Qt.AlignmentFlag.AlignHCenter, op.text)
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
        borderGradient.setColorAt(1.0, Colour(
            *borderColour,
            (255 if self.hasFocus() and self.isEnabled() else 32)
        ))
        painter.setPen(QPen(QBrush(borderGradient), 1.0))
        backgroundGradient = QLinearGradient(QPointF(0, 0), QPointF(0, rect.height()))
        backgroundGradient.setColorAt(0.0, backgroundColour)
        backgroundGradient.setColorAt(1.0, Colour(*backgroundColour, 210))
        painter.setBrush(QBrush(backgroundGradient))
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
        borderGradient.setColorAt(1.0, Colour(
            *borderColour,
            (255 if self.hasFocus() and self.isEnabled() else 32)
        ))
        painter.setPen(QPen(QBrush(borderGradient), 1.0))
        backgroundGradient = QLinearGradient(QPointF(0, 0), QPointF(0, rect.height()))
        backgroundGradient.setColorAt(0.0, backgroundColour)
        backgroundGradient.setColorAt(1.0, Colour(*backgroundColour, 210))
        painter.setBrush(QBrush(backgroundGradient))
        painter.drawRoundedRect(rect, 10, 10)
        self.setShowGrid(False)
        op = QStyleOptionFrame()
        op.initFrom(self)
        self.initStyleOption(op)
        self.setStyleSheet(
            f"color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {str(painter.opacity())}); background: transparent; border: none;")
        super().paintEvent(e)
