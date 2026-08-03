# -*- coding: utf-8 -*-
from typing import overload

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from ..ThemeController import *
from .ToolTip import ToolTip

from .Widget import Widget


class ToolBox(QToolBox, Widget):
    @overload
    def __init__(self, parent=None):
        ...
    
    def __init__(self, *__args):
        super().__init__(*__args)
    
    def paintEvent(self, a0):
        self.setStyleSheet("padding: 3px;")
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
        
        for button in (button for button in self.children() if isinstance(button, QAbstractButton)):
            button.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            button.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
            opacity = QGraphicsOpacityEffect(button)
            opacity.setOpacity(0.0)
            if button.graphicsEffect():
                button.graphicsEffect().deleteLater()
            button.setGraphicsEffect(opacity)
            if not hasattr(button, "newTip"):
                newTip = ToolTip(self)
                button.newTip = newTip
                button.installEventFilter(newTip)
            if not hasattr(button, "evf"):
                button.evf = self
                button.installEventFilter(button.evf)
            
            isHighlight = (button.isDown() or button.isChecked() or button.underMouse() or button.hasFocus())
            
            painter.save()
            painter.translate(button.pos())
            btnRect = button.rect().adjusted(1, 1, -1, -1)
            btnBaseOpacity = button.property("baseOpacity") or 1
            
            btnBgColor = getBackgroundColour(is_highlight=isHighlight and button.isEnabled())
            btnGradient = QLinearGradient(QPointF(btnRect.topLeft()), QPointF(btnRect.bottomLeft()))
            btnBgColorLighter = QColor(
                min(255, btnBgColor.red() + 10),
                min(255, btnBgColor.green() + 10),
                min(255, btnBgColor.blue() + 10)
            )
            btnGradient.setColorAt(0.0, btnBgColorLighter)
            btnGradient.setColorAt(1.0, btnBgColor)
            
            painter.setOpacity(btnBaseOpacity)
            painter.setPen(getBorderColour(is_highlight=isHighlight and button.isEnabled()))
            painter.setBrush(btnGradient)
            painter.drawRoundedRect(btnRect, 16, 16)
            
            if button.property("frameOpacity"):
                btnFrameOpacity = button.property("frameOpacity")
                painter.setOpacity(btnFrameOpacity)
                
                glowColor = getBorderColour(is_highlight=True)
                glowAlpha = int(60 * btnFrameOpacity)
                glowPen = QPen(QColor(glowColor.red(), glowColor.green(), glowColor.blue(), glowAlpha), 1.5)
                painter.setPen(glowPen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRoundedRect(btnRect.adjusted(1, 1, -1, -1), 15, 15)
                
                highlightPen = QPen(getBorderColour(is_highlight=True), 1.0)
                painter.setPen(highlightPen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRoundedRect(btnRect.adjusted(1, 1, -1, -1), 15, 15)
            
            painter.restore()
