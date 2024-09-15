# -*- coding: utf-8 -*-
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from .CWMThemeControl import *
from .CWMToolTip import ToolTip


class ScrollBar(QScrollBar):
    def __init__(self, orientation, parent):
        super().__init__(orientation, parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.installEventFilter(ToolTip(self))
    
    def paintEvent(self, e):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self)
        painter.setOpacity(1.0 if self.underMouse() or self.hasFocus() else 0.6)
        if not self.isEnabled():
            painter.setOpacity(0.3)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getBorderColour())
        painter.setBrush(getBackgroundColour())
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)
        painter.setPen(getBorderColour(highlight=(self.underMouse() or self.hasFocus()) and self.isEnabled()))
        painter.setBrush(getBackgroundColour(
            highlight=self.isEnabled()))
        x = 0
        y = 0
        width = 0
        height = 0
        match self.orientation():
            case Qt.Orientation.Horizontal:
                x = max(min(self.width() - 100 - self.height(),
                            int((self.value() / (self.maximum() or 1)) * (
                                    self.width() - self.height() - max((self.width() - self.maximum()), 100)) + (
                                        self.height() * (1.0 - (self.value() / (self.maximum() or 1)))))),
                        self.height())
                y = 0
                width = min(max(100, self.width() - self.maximum()),
                            self.width() - x - self.height())
                height = self.height()
            case Qt.Orientation.Vertical:
                x = 0
                y = max(min(self.height() - 100 - self.width(),
                            int((self.value() / (self.maximum() or 1)) * (
                                    self.height() - self.width() - max((self.height() - self.maximum()), 100)) + (
                                        self.width() * (1.0 - (self.value() / (self.maximum() or 1)))))),
                        self.width())
                width = self.width()
                height = min(max(100, self.height() - self.maximum()),
                             self.height() - y - self.width())
            case _:
                pass
        painter.drawRoundedRect(QRect(x, y, width, height).adjusted(2, 2, -2, -2), 10, 10)
        match self.orientation():
            case Qt.Orientation.Horizontal:
                painter.save()
                p = QPen(getForegroundColour())
                p.setCapStyle(Qt.PenCapStyle.RoundCap)
                p.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
                painter.setPen(p)
                del p
                painter.setBrush(getForegroundColour())
                painter.translate(QPoint(0, 0))
                painter.drawPolygon(
                    [QPoint(3, self.height() // 2), QPoint(self.height() - 3, self.height() - 3),
                     QPoint(self.height() - 3, 3)])
                painter.translate(QPoint(self.width() - self.height(), 0))
                painter.drawPolygon(
                    [QPoint(self.height() - 3, self.height() // 2), QPoint(3, self.height() - 3),
                     QPoint(3, 3)])
                painter.restore()
            case Qt.Orientation.Vertical:
                painter.save()
                p = QPen(getForegroundColour())
                p.setCapStyle(Qt.PenCapStyle.RoundCap)
                p.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
                painter.setPen(p)
                del p
                painter.setBrush(getForegroundColour())
                painter.translate(QPoint(0, 0))
                painter.drawPolygon(
                    [QPoint(3, self.width()), QPoint(self.width() // 2, 3), QPoint(self.width() - 3, self.width())])
                painter.translate(QPoint(0, self.height() - self.width()))
                painter.drawPolygon(
                    [QPoint(3, 0), QPoint(self.width() // 2, self.width() - 3), QPoint(self.width() - 3, 0)])
                painter.restore()
            case _:
                pass


class ScrollArea(QScrollArea):
    def __init__(self, parent):
        super().__init__(parent)
        self.setHorizontalScrollBar(ScrollBar(Qt.Orientation.Horizontal, self))
        self.setVerticalScrollBar(ScrollBar(Qt.Orientation.Vertical, self))
