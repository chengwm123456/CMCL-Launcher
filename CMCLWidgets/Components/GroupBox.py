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
        self.setStyleSheet("padding: 15px 0px 5px 0px;")
        self.setStyle(QStyleFactory.create("windows11"))
    
    def paintEvent(self, a0):
        self.setStyleSheet("padding: 15px 0px 5px 0px;")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self)
        painter.setOpacity(self.property("widgetOpacity"))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        borderColour = getBorderColour()
        backgroundColour = getBackgroundColour()
        painter.save()
        painter.setOpacity((((max(painter.opacity(), 0.6) - 0.6) * 10) / 4))
        borderGradient = QLinearGradient(QPointF(0, 0), QPointF(0, self.height()))
        borderGradient.setColorAt(0.0, Colour(*getBorderColour(), 64))
        borderGradient.setColorAt(1.0, borderColour)
        painter.setPen(QPen(QBrush(borderGradient), 1))
        painter.setBrush(Qt.GlobalColor.transparent)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 12, 12)
        painter.restore()
        painter.save()
        painter.setOpacity(self.property("widgetOpacity"))
        borderGradient = QLinearGradient(QPointF(3, 3), QPointF(3, self.height() - 3))
        borderGradient.setColorAt(0.0, borderColour)
        borderGradient.setColorAt(1.0, Colour(*getBorderColour(), 64))
        backgroundGradient = QLinearGradient(QPointF(3, 3), QPointF(self.width() - 3, 3))
        backgroundGradient.setColorAt(0.0, backgroundColour)
        backgroundGradient.setColorAt(0.5, Colour(*backgroundColour, 230))
        backgroundGradient.setColorAt(1.0, backgroundColour)
        painter.setPen(QPen(QBrush(borderGradient), 1))
        painter.setBrush(QBrush(backgroundGradient))
        painter.drawRoundedRect(self.rect().adjusted(3, 3, -3, -3), 10, 10)
        painter.restore()
        op = QStyleOptionGroupBox()
        op.initFrom(self)
        self.initStyleOption(op)
        op.rect = op.rect.adjusted(4, 4, -4, -4)
        if self.title() or self.isCheckable():
            height = self.style().subControlRect(QStyle.ComplexControl.CC_GroupBox, op,
                                                 QStyle.SubControl.SC_GroupBoxLabel).height() - 2
            painter.save()
            painter.setPen(getBorderColour())
            painter.drawLine(QLine(QPoint(5, height), QPoint(self.width() - 5, height)))
            painter.restore()
        if self.title():
            painter.save()
            painter.setPen(getForegroundColour())
            painter.setBrush(Qt.GlobalColor.transparent)
            painter.drawText(
                self.style().subControlRect(QStyle.ComplexControl.CC_GroupBox, op,
                                            QStyle.SubControl.SC_GroupBoxLabel).adjusted(0, 0, 0, -5),
                Qt.AlignmentFlag.AlignCenter, self.title())
            painter.restore()
        if self.isCheckable():
            rect = self.style().subControlRect(QStyle.ComplexControl.CC_GroupBox, op,
                                               QStyle.SubControl.SC_GroupBoxCheckBox).adjusted(
                -2, -2, 2, 2).adjusted(
                0, -2, 0, -2)
            borderColour = getBorderColour(
                is_highlight=(self.isChecked()) or
                             ((self.isChecked() or self.underMouse() or self.hasFocus()) and
                              self.isEnabled())
            )
            backgroundColour = getBackgroundColour(
                is_highlight=(self.isChecked()) or (
                        (self.isChecked()) and self.isEnabled())
            )
            painter.save()
            painter.setOpacity((((max(painter.opacity(), 0.6) - 0.6) * 10) / 4))
            borderGradient = QLinearGradient(QPointF(rect.x(), rect.y()), QPointF(rect.x(), rect.y() + rect.height()))
            borderGradient.setColorAt(0.0, Colour(*getBorderColour(), 64))
            borderGradient.setColorAt(1.0, borderColour)
            painter.setPen(QPen(QBrush(borderGradient), 1))
            painter.setBrush(Qt.GlobalColor.transparent)
            painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 12, 12)
            painter.restore()
            painter.save()
            painter.setOpacity(self.property("widgetOpacity"))
            borderGradient = QLinearGradient(QPointF(rect.x() + 3, rect.y() + 3),
                                             QPointF(rect.x() + 3, rect.height() - 3 + rect.y()))
            borderGradient.setColorAt(0.0, borderColour)
            borderGradient.setColorAt(1.0, Colour(*getBorderColour(), 64))
            backgroundGradient = QLinearGradient(QPointF(rect.x() + 3, rect.y() + 3),
                                                 QPointF(self.width() - 3, 3 + rect.y()))
            backgroundGradient.setColorAt(0.0, backgroundColour)
            backgroundGradient.setColorAt(0.5, Colour(*backgroundColour, 230))
            backgroundGradient.setColorAt(1.0, backgroundColour)
            painter.setPen(QPen(QBrush(borderGradient), 1))
            painter.setBrush(QBrush(backgroundGradient))
            painter.drawRoundedRect(rect.adjusted(3, 3, -3, -3), 10, 10)
            painter.restore()
            painter.save()
            painter.setPen(getForegroundColour())
            painter.setBrush(Qt.GlobalColor.transparent)
            rect = self.style().subControlRect(QStyle.ComplexControl.CC_GroupBox, op,
                                               QStyle.SubControl.SC_GroupBoxCheckBox).adjusted(
                1, 1, -1, -1).adjusted(
                0, -2, 0, -2)
            if self.isChecked():
                painter.drawLines([QLine(
                    QPoint(4 + rect.x(), rect.y() + 8),
                    QPoint(rect.width() // 2 + rect.x(), rect.y() + 10)),
                    QLine(
                        QPoint(rect.width() // 2 + rect.x(), rect.y() + 10),
                        QPoint(9 + rect.x(), rect.y() + 4))])
            painter.restore()
