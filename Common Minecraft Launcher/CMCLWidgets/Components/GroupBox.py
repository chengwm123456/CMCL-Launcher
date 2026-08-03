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
            self.setContentsMargins(5, 21, 5, 5)
        else:
            self.setContentsMargins(5, 5, 5, 5)
        self.updateGeometry()
    
    def setTitle(self, title):
        super().setTitle(title)
        if self.title() or self.isCheckable():
            self.setContentsMargins(5, 21, 5, 5)
        else:
            self.setContentsMargins(5, 5, 5, 5)
        self.updateGeometry()
    
    def setCheckable(self, checkable):
        super().setCheckable(checkable)
        if self.title() or self.isCheckable():
            self.setContentsMargins(5, 21, 5, 5)
        else:
            self.setContentsMargins(5, 5, 5, 5)
        self.updateGeometry()
    
    def paintEvent(self, a0):
        if self.title() or self.isCheckable():
            self.setContentsMargins(5, 21, 5, 5)
        else:
            self.setContentsMargins(5, 5, 5, 5)
        
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing)
        
        rect = self.rect()
        baseOpacity = self.property("baseOpacity") or 0.85
        frameOpacity = self.property("frameOpacity") or 0.0
        
        painter.save()
        painter.setOpacity(baseOpacity * 0.7)
        
        shadowColor1 = QColor(0, 0, 0, int(12 * baseOpacity))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(shadowColor1)
        shadowRect1 = rect.adjusted(6, 6, -6, -6)
        painter.drawRoundedRect(shadowRect1, 18, 18)
        
        shadowColor2 = QColor(0, 0, 0, int(8 * baseOpacity))
        painter.setBrush(shadowColor2)
        shadowRect2 = rect.adjusted(4, 4, -4, -4)
        painter.drawRoundedRect(shadowRect2, 16, 16)
        
        shadowColor3 = QColor(0, 0, 0, int(5 * baseOpacity))
        painter.setBrush(shadowColor3)
        shadowRect3 = rect.adjusted(2, 2, -2, -2)
        painter.drawRoundedRect(shadowRect3, 14, 14)
        painter.restore()
        
        painter.save()
        painter.setOpacity(baseOpacity)
        
        bgGradient = QLinearGradient(QPointF(rect.topLeft()), QPointF(rect.bottomRight()))
        bgColor = getBackgroundColour()
        
        bgColorLight = QColor(
            min(255, bgColor.red() + 20),
            min(255, bgColor.green() + 20),
            min(255, bgColor.blue() + 20)
        )
        bgColorMid = QColor(
            min(255, bgColor.red() + 10),
            min(255, bgColor.green() + 10),
            min(255, bgColor.blue() + 10)
        )
        
        bgGradient.setColorAt(0.0, bgColorLight)
        bgGradient.setColorAt(0.3, bgColorMid)
        bgGradient.setColorAt(0.7, bgColorMid)
        bgGradient.setColorAt(1.0, bgColor)
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(bgGradient)
        painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 16, 16)
        painter.restore()
        
        painter.save()
        painter.setOpacity(baseOpacity * 0.9)
        
        borderGradient = QLinearGradient(QPointF(rect.topLeft()), QPointF(rect.bottomLeft()))
        borderColor = getBorderColour()
        borderColorDarker = QColor(
            max(0, borderColor.red() - 20),
            max(0, borderColor.green() - 20),
            max(0, borderColor.blue() - 20)
        )
        
        borderGradient.setColorAt(0.0, borderColorDarker)
        borderGradient.setColorAt(0.5, borderColor)
        borderGradient.setColorAt(1.0, borderColor)
        
        penBorder = QPen(borderGradient, 1.0)
        painter.setPen(penBorder)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 16, 16)
        painter.restore()
        
        op = QStyleOptionGroupBox()
        op.initFrom(self)
        self.initStyleOption(op)
        if self.title() or self.isCheckable():
            groupRect = self.style().subControlRect(QStyle.ComplexControl.CC_GroupBox, op,
                                               QStyle.SubControl.SC_GroupBoxLabel).united(
                self.style().subControlRect(QStyle.ComplexControl.CC_GroupBox, op,
                                            QStyle.SubControl.SC_GroupBoxCheckBox))
            painter.save()
            painter.setOpacity(self.property("baseOpacity") + (self.property("frameOpacity") * (1.0 - self.property("baseOpacity"))))
            painter.setPen(getBorderColour())
            painter.drawLine(QLine(QPoint(2, max(groupRect.height(), 16)), QPoint(self.width() - 2, max(groupRect.height(), 16))))
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
            checkBoxRect = self.style().subControlRect(QStyle.ComplexControl.CC_GroupBox, op,
                                               QStyle.SubControl.SC_GroupBoxCheckBox).adjusted(1, 1, -1, -1)
            checkBoxRect.adjust(2, 0, 2, 0)
            
            painter.save()
            painter.setOpacity(baseOpacity * 0.3)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(0, 0, 0, int(10 * baseOpacity)))
            shadowRect = checkBoxRect.adjusted(2, 2, -2, -2)
            painter.drawRoundedRect(shadowRect, 16, 16)
            painter.restore()
            
            painter.save()
            painter.setOpacity(baseOpacity)
            painter.setPen(getBorderColour(
                is_highlight=self.isChecked() or (self.isChecked() and self.isEnabled())
            ))
            
            bgColor = getBackgroundColour(
                is_highlight=self.isChecked() or (self.isChecked() and self.isEnabled())
            )
            bgGradient = QLinearGradient(QPointF(checkBoxRect.topLeft()), QPointF(checkBoxRect.bottomLeft()))
            bgColorLighter = QColor(
                min(255, bgColor.red() + 8),
                min(255, bgColor.green() + 8),
                min(255, bgColor.blue() + 8)
            )
            bgGradient.setColorAt(0.0, bgColorLighter)
            bgGradient.setColorAt(1.0, bgColor)
            painter.setBrush(bgGradient)
            painter.drawRoundedRect(checkBoxRect, 16, 16)
            painter.restore()
            
            if frameOpacity > 0.1:
                painter.save()
                painter.setOpacity(frameOpacity)
                painter.setPen(getBorderColour(is_highlight=True))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRoundedRect(checkBoxRect, 16, 16)
                painter.restore()
            
            painter.save()
            painter.setPen(getForegroundColour())
            painter.setBrush(Qt.GlobalColor.transparent)
            if self.isChecked():
                painter.setOpacity(
                    self.property("baseOpacity") + (
                            self.property("frameOpacity") * (1.0 - self.property("baseOpacity"))))
                painter.drawLines([
                    QLineF(QPointF(checkBoxRect.x() + (checkBoxRect.width() / 3), checkBoxRect.y() + (checkBoxRect.height() * 2 / 3)),
                           QPointF(checkBoxRect.width() / 2 + checkBoxRect.x(), checkBoxRect.y() + (checkBoxRect.height() * 5 / 6))),
                    QLineF(QPointF(checkBoxRect.width() / 2 + checkBoxRect.x(), checkBoxRect.y() + (checkBoxRect.height() * 5 / 6)),
                           QPointF(checkBoxRect.x() + (checkBoxRect.width() * 2 / 3) + 1, checkBoxRect.y() + (checkBoxRect.height() / 4) + 2))
                ])
            painter.restore()
