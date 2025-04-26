# -*- coding: utf-8 -*-
from typing import overload

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from ..ThemeController import *
from .ToolTip import ToolTip
from CMCLWidgets.Windows import RoundedMenu
from .ListView import ListView

from .Widget import Widget


class ComboBox(QComboBox, Widget):
    @overload
    def __init__(self, parent=None):
        ...
    
    def __init__(self, *__args):
        super().__init__(*__args)
        if self.lineEdit():
            self.lineEdit().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            self.lineEdit().setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
            self.lineEdit().installEventFilter(ToolTip(self))
            self.lineEdit().setStyleSheet(
                f"color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {str(0.6)}); background: transparent; border: none; padding: 5px;")
            self.lineEdit().setFont(self.font())
        self.setStyle(QStyleFactory.create("Windows"))
        listView = ListView(self)
        self.setView(listView)
        self.view().parent().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.view().parent().setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint |
            Qt.WindowType.Popup
        )
        self.view().parent().update()
    
    def showPopup(self):
        self.view().parent().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.view().parent().setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint |
            Qt.WindowType.Popup
        )
        self.view().parent().update()
        super().showPopup()
        self.view().parent().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.view().parent().setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint |
            Qt.WindowType.Popup
        )
        self.view().parent().update()
    
    def paintEvent(self, e):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        if self.lineEdit():
            self.lineEdit().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            self.lineEdit().setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
            self.lineEdit().setStyleSheet(
                f"color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {str(self.property('widgetOpacity') or 1.0)}); background: transparent; border: none; padding: 5px;")
            self.lineEdit().setFont(self.font())
            self.lineEdit().setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            self.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        else:
            self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        painter = QPainter(self)
        painter.setOpacity(self.property("widgetOpacity"))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getBorderColour(is_highlight=(self.hasFocus() or self.underMouse()) and self.isEnabled()))
        painter.setBrush(getBackgroundColour(is_highlight=self.hasFocus() and self.isEnabled()))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)
        painter.save()
        painter.setPen(QPen(getBorderColour(
            is_highlight=self.isEnabled()) if (
                                                      self.hasFocus() or self.underMouse() or self.view().isVisible()) and self.isEnabled() else getForegroundColour(),
                            1.0,
                            Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(getBorderColour(
            is_highlight=self.isEnabled()) if self.view().isVisible() and self.isEnabled() else getForegroundColour())
        painter.translate((self.width() - 8) - 3, self.height() / 2 - 4)
        painter.drawPolygon([QPoint(0, 0), QPoint(4, 8), QPoint(8, 0)])
        painter.restore()
        op = QStyleOptionComboBox()
        op.initFrom(self)
        self.initStyleOption(op)
        op.palette.setColor(op.palette.ColorRole.Text, getForegroundColour())
        self.style().drawControl(QStyle.ControlElement.CE_ComboBoxLabel, op, painter, self)
        self.setStyleSheet("padding: 5px;")
    
    def contextMenuEvent(self, e):
        if self.lineEdit() and self.isEditable():
            default = self.lineEdit().createStandardContextMenu()
            menu = RoundedMenu(self)
            for i in default.actions():
                menu.addAction(i)
            menu.exec(self.mapToGlobal(e.pos()))
    
    def hasFocus(self):
        return super().hasFocus() or self.view().hasFocus()
