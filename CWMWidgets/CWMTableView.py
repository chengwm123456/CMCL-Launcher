# -*- coding: utf-8 -*-
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from .CWMThemeControl import *
from .CWMToolTip import ToolTip


class HeaderView(QHeaderView):
    def __init__(self, orientation, parent):
        super().__init__(orientation, parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.installEventFilter(ToolTip(self))
        if orientation == Qt.Orientation.Vertical:
            self.setFixedWidth(int(self.fontMetrics().maxWidth() * 1.5))
        if orientation == Qt.Orientation.Horizontal:
            self.setFixedHeight(int(self.fontMetrics().height() * 2))
    
    def paintEvent(self, e):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self.viewport())
        painter.setOpacity(1.0 if self.underMouse() or self.hasFocus() else 0.6)
        if not self.isEnabled():
            painter.setOpacity(0.3)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getBorderColour(highlight=self.hasFocus() or self.underMouse()))
        painter.setBrush(getBackgroundColour(highlight=self.hasFocus()))
        rect = self.viewport().rect()
        rect.setWidth(rect.width() - rect.x() - 1)
        rect.setHeight(rect.height() - rect.y() - 1)
        rect.setX(1)
        rect.setY(1)
        painter.drawRoundedRect(rect, 10, 10)
        op = QStyleOptionHeader()
        op.initFrom(self)
        self.initStyleOption(op)
        op.palette.setColor(self.foregroundRole(), getForegroundColour())
        op.palette.setColor(self.backgroundRole(), Qt.GlobalColor.transparent)
        self.style().drawControl(QStyle.ControlElement.CE_Header, op, painter, self)
        self.setStyleSheet(
            f"color: rgba({str(getForegroundColour(tuple=True)).replace('(', '').replace(')', '')}, {str(painter.opacity())}); background: transparent; border: none;")
        super().paintEvent(e)


class TableView(QTableView):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.installEventFilter(ToolTip(self))
        self.setVerticalHeader(HeaderView(Qt.Orientation.Vertical, self))
        self.setHorizontalHeader(HeaderView(Qt.Orientation.Horizontal, self))
    
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


class TableWidget(QTableWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.installEventFilter(ToolTip(self))
        self.setVerticalHeader(HeaderView(Qt.Orientation.Vertical, self))
        self.setHorizontalHeader(HeaderView(Qt.Orientation.Horizontal, self))
    
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
