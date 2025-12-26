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
        if "windows11" in QStyleFactory.keys():
            self.setStyle(QStyleFactory.create("windows11"))
        else:
            self.setStyle(QStyleFactory.create("Windows"))
        if self.title() or self.isCheckable():
            self.setStyleSheet("GroupBox { padding: 21px 5px 5px 5px; }")
        else:
            self.setStyleSheet("GroupBox { padding: 5px 5px 5px 5px; }")
    
    def paintEvent(self, a0):
        if self.title() or self.isCheckable():
            self.setStyleSheet("GroupBox { padding: 21px 5px 5px 5px; }")
        else:
            self.setStyleSheet("GroupBox { padding: 5px 5px 5px 5px; }")
        
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.save()
        painter.setOpacity(self.property("baseOpacity"))
        painter.setPen(getBorderColour())
        painter.setBrush(getBackgroundColour())
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 16, 16)
        painter.restore()
        
        if self.property("frameOpacity"):
            painter.save()
            painter.setOpacity(self.property("frameOpacity"))
            painter.setPen(getBorderColour())
            painter.setBrush(getBackgroundColour())
            painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 16, 16)
            painter.restore()
        
        op = QStyleOptionGroupBox()
        op.initFrom(self)
        self.initStyleOption(op)
        if self.title() or self.isCheckable():
            rect = self.style().subControlRect(QStyle.ComplexControl.CC_GroupBox, op,
                                               QStyle.SubControl.SC_GroupBoxLabel).united(
                self.style().subControlRect(QStyle.ComplexControl.CC_GroupBox, op,
                                            QStyle.SubControl.SC_GroupBoxCheckBox))
            painter.save()
            painter.setOpacity(self.property("baseOpacity"))
            painter.setPen(getBorderColour())
            painter.drawLine(QLine(QPoint(2, max(rect.height(), 16)), QPoint(self.width() - 2, max(rect.height(), 16))))
            painter.restore()
            
            if self.property("frameOpacity"):
                rect = self.style().subControlRect(QStyle.ComplexControl.CC_GroupBox, op,
                                                   QStyle.SubControl.SC_GroupBoxLabel).united(
                    self.style().subControlRect(QStyle.ComplexControl.CC_GroupBox, op,
                                                QStyle.SubControl.SC_GroupBoxCheckBox))
                painter.save()
                painter.setOpacity(self.property("frameOpacity"))
                painter.setPen(getBorderColour())
                painter.drawLine(
                    QLine(QPoint(2, max(rect.height(), 16)), QPoint(self.width() - 2, max(rect.height(), 16))))
                painter.restore()
        if self.title():
            painter.save()
            painter.setOpacity(
                self.property("baseOpacity") + (self.property("frameOpacity") * (1.0 - self.property("baseOpacity"))))
            painter.setPen(getForegroundColour())
            painter.setBrush(Qt.GlobalColor.transparent)
            painter.drawText(
                self.style().subControlRect(QStyle.ComplexControl.CC_GroupBox, op, QStyle.SubControl.SC_GroupBoxLabel),
                Qt.AlignmentFlag.AlignCenter, self.title())
            painter.restore()
        if self.isCheckable():
            rect = self.style().subControlRect(QStyle.ComplexControl.CC_GroupBox, op,
                                               QStyle.SubControl.SC_GroupBoxCheckBox).adjusted(1, 1, -1, -1)
            rect.adjust(2, 0, 2, 0)
            
            painter.save()
            painter.setOpacity(self.property("baseOpacity"))
            painter.setPen(getBorderColour(
                is_highlight=self.isChecked() or (self.isChecked() and self.isEnabled())
            ))
            painter.setBrush(getBackgroundColour(
                is_highlight=self.isChecked() or (self.isChecked() and self.isEnabled())
            ))
            painter.drawRoundedRect(rect, 16, 16)
            painter.restore()
            if self.property("frameOpacity"):
                painter.save()
                painter.setOpacity(self.property("frameOpacity"))
                painter.setPen(getBorderColour(is_highlight=True))
                painter.setBrush(getBackgroundColour(
                    is_highlight=self.isChecked() or (self.isChecked() and self.isEnabled())
                ))
                painter.drawRoundedRect(rect, 16, 16)
                painter.restore()
            
            painter.save()
            painter.setPen(getForegroundColour())
            painter.setBrush(Qt.GlobalColor.transparent)
            if self.isChecked():
                painter.setOpacity(
                    self.property("baseOpacity") + (
                            self.property("frameOpacity") * (1.0 - self.property("baseOpacity"))))
                painter.drawLines([
                    QLine(QPoint(4 + rect.x(), rect.y() + 8), QPoint(rect.width() // 2 + rect.x(), rect.y() + 10)),
                    QLine(QPoint(rect.width() // 2 + rect.x(), rect.y() + 10), QPoint(9 + rect.x(), rect.y() + 4))
                ])
            painter.restore()
