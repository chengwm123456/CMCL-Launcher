# -*- coding: utf-8 -*-
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtSvg import QSvgRenderer
from .CWMThemeControl import *
from .CWMToolTip import ToolTip


class PushButton(QPushButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.installEventFilter(ToolTip(self))
    
    def paintEvent(self, a0):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self)
        painter.setOpacity(1.0 if self.isDown() or self.isChecked() or self.underMouse() or self.hasFocus() else 0.6)
        if not self.isEnabled():
            painter.setOpacity(0.3)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getBorderColour(
            highlight=(self.isDown() or self.isChecked() or self.underMouse() or self.hasFocus()) and self.isEnabled()))
        painter.setBrush(getBackgroundColour(highlight=(self.isDown() or self.isChecked()) and self.isEnabled()))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)
        if self.menu():
            painter.save()
            p = QPen(getBorderColour(
                highlight=self.isEnabled()) if self.isDown() or self.hasFocus() or self.underMouse() else getForegroundColour())
            p.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(p)
            del p
            painter.setBrush(
                getBorderColour(highlight=self.isEnabled()) if self.isDown() else getForegroundColour())
            painter.translate((self.width() - 8) - 3, self.height() / 2 - 4)
            painter.drawPolygon([QPoint(0, 0), QPoint(4, 8), QPoint(8, 0)])
            painter.restore()
        op = QStyleOptionButton()
        op.initFrom(self)
        op.icon = self.icon()
        op.text = self.text()
        op.iconSize = self.iconSize()
        op.palette.setColor(self.foregroundRole(), getForegroundColour())
        op.palette.setColor(self.backgroundRole(), Qt.GlobalColor.transparent)
        self.style().drawControl(QStyle.ControlElement.CE_PushButtonLabel, op, painter, self)
        self.setStyleSheet("padding: 5px;")
    
    def keyPressEvent(self, *args, **kwargs):
        super().keyPressEvent(*args, **kwargs)
        if args[0].key() == 16777220 and self.hasFocus() and self.isVisible():
            self.setDown(True)
            self.repaint()
    
    def keyReleaseEvent(self, *args, **kwargs):
        super().keyReleaseEvent(*args, **kwargs)
        if args[0].key() == 16777220 and self.hasFocus() and self.isVisible():
            self.setDown(False)
            self.pressed.emit()
            self.repaint()


class ToolButton(QToolButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.installEventFilter(ToolTip(self))
    
    def paintEvent(self, a0):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self)
        painter.setOpacity(1.0 if self.isDown() or self.isChecked() or self.underMouse() or self.hasFocus() else 0.6)
        if not self.isEnabled():
            painter.setOpacity(0.3)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getBorderColour(
            highlight=(self.isDown() or self.isChecked() or self.underMouse() or self.hasFocus()) and self.isEnabled()))
        painter.setBrush(getBackgroundColour(highlight=(self.isDown() or self.isChecked()) and self.isEnabled()))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)
        if self.menu():
            painter.save()
            p = QPen(getBorderColour(
                highlight=self.isEnabled()) if self.isDown() or self.hasFocus() or self.underMouse() else getForegroundColour())
            p.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(p)
            del p
            painter.setBrush(
                getBorderColour(highlight=self.isEnabled()) if self.isDown() else getForegroundColour())
            painter.translate((self.width() - 8) - 3, self.height() / 2 - 4)
            painter.drawPolygon([QPoint(0, 0), QPoint(4, 8), QPoint(8, 0)])
            painter.restore()
        op = QStyleOptionToolButton()
        op.initFrom(self)
        op.icon = self.icon()
        op.text = self.text()
        op.iconSize = self.iconSize()
        op.arrowType = self.arrowType()
        op.palette.setColor(self.foregroundRole(), getForegroundColour())
        op.palette.setColor(self.backgroundRole(), Qt.GlobalColor.transparent)
        self.style().drawControl(QStyle.ControlElement.CE_ToolButtonLabel, op, painter, self)
        self.setStyleSheet("padding: 5px;")
    
    def keyPressEvent(self, *args, **kwargs):
        super().keyPressEvent(*args, **kwargs)
        if args[0].key() == 16777220 and self.hasFocus() and self.isVisible():
            self.setDown(True)
            self.repaint()
    
    def keyReleaseEvent(self, *args, **kwargs):
        super().keyReleaseEvent(*args, **kwargs)
        if args[0].key() == 16777220 and self.hasFocus() and self.isVisible():
            self.setDown(False)
            self.pressed.emit()
            self.repaint()
