# -*- coding: utf-8 -*-
from typing import overload

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from ..ThemeController import *
from .ToolTip import ToolTip

from .Widget import Widget


class GroupBox(QGroupBox, Widget):
    @overload
    def __init__(self, parent=None):
        ...
    
    @overload
    def __init__(self, title, parent=None):
        ...
    
    def __init__(self, *__args):
        super().__init__(*__args)
    
    def paintEvent(self, a0):
        self.setStyleSheet("padding: 10px 0px 5px 0px;")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self)
        painter.setOpacity(self.property("widgetOpacity"))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getBorderColour())
        painter.setBrush(getBackgroundColour())
        y = self.fontMetrics().boundingRect(QRect(8, 0, self.width() - 20, self.height()), self.alignment(),
                                            self.title()).height() + 1 if self.title() else 0
        rect = self.rect().adjusted(1, 1, -1, -1)
        rect = QRect(rect.x(), rect.y() + (y // 2 if self.title() else 0), rect.width(),
                     rect.height() - (y // 2 if self.title() else 0))
        painter.drawRoundedRect(rect, 10, 10)
        op = QStyleOptionGroupBox()
        op.initFrom(self)
        self.initStyleOption(op)
        if self.title() or self.isCheckable():
            painter.drawRoundedRect(
                self.style().subControlRect(QStyle.ComplexControl.CC_GroupBox, op,
                                            QStyle.SubControl.SC_GroupBoxLabel).united(
                    self.style().subControlRect(QStyle.ComplexControl.CC_GroupBox, op,
                                                QStyle.SubControl.SC_GroupBoxCheckBox)).adjusted(1, 1, -1, -1),
                10, 10)
        if self.title():
            painter.save()
            painter.setPen(getForegroundColour())
            painter.setBrush(Qt.GlobalColor.transparent)
            painter.drawText(
                self.style().subControlRect(QStyle.ComplexControl.CC_GroupBox, op, QStyle.SubControl.SC_GroupBoxLabel),
                Qt.AlignmentFlag.AlignCenter, self.title())
            painter.restore()
        if self.isCheckable():
            painter.setPen(getBorderColour(
                is_highlight=self.isChecked() or (
                        (self.isChecked() or self.underMouse() or self.hasFocus()) and self.isEnabled())))
            painter.setBrush(getBackgroundColour(is_highlight=(self.isChecked()) or (
                    self.isChecked() and self.isEnabled())))
            rect = self.style().subControlRect(QStyle.ComplexControl.CC_GroupBox, op,
                                               QStyle.SubControl.SC_GroupBoxCheckBox).adjusted(1, 1, -1, -1)
            painter.drawRoundedRect(rect, 10, 10)
            painter.save()
            painter.setPen(getForegroundColour())
            painter.setBrush(Qt.GlobalColor.transparent)
            if self.isChecked():
                painter.drawLines([QLine(
                    QPoint(4 + rect.x(), rect.y() + 8),
                    QPoint(rect.width() // 2 + rect.x(), rect.y() + 10)),
                    QLine(
                        QPoint(rect.width() // 2 + rect.x(), rect.y() + 10),
                        QPoint(9 + rect.x(), rect.y() + 4))])
            painter.restore()
