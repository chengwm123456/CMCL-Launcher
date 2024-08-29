# -*- coding: utf-8 -*-
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from .CWMThemeControl import *
from .CWMToolTip import ToolTip
from .CWMWindows import RoundedMenu


class ComboBox(QComboBox):
    def __init__(self, parent):
        super().__init__(parent)
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
        painter.setPen(getBorderColour(highlight=(self.hasFocus() or self.underMouse())))
        painter.setBrush(getBackgroundColour(highlight=self.hasFocus()))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)
        painter.save()
        p = QPen(getBorderColour(
            highlight=self.isEnabled()) if self.hasFocus() or self.underMouse() else getForegroundColour())
        p.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(p)
        del p
        painter.setBrush(getForegroundColour())
        painter.translate((self.width() - 8) - 3, self.height() / 2 - 4)
        painter.drawPolygon([QPoint(0, 0), QPoint(4, 8), QPoint(8, 0)])
        painter.restore()
        op = QStyleOptionComboBox()
        op.initFrom(self)
        self.initStyleOption(op)
        op.palette.setColor(self.foregroundRole(), getForegroundColour())
        op.palette.setColor(self.backgroundRole(), Qt.GlobalColor.transparent)
        self.setStyleSheet("color: black")
        self.style().drawControl(QStyle.ControlElement.CE_ComboBoxLabel, op, painter, self)
    
    def contextMenuEvent(self, e):
        if self.lineEdit() and self.isEditable():
            default = self.lineEdit().createStandardContextMenu()
            menu = RoundedMenu(self)
            for i in default.actions():
                menu.addAction(i)
            menu.exec(self.mapToGlobal(e.pos()))
