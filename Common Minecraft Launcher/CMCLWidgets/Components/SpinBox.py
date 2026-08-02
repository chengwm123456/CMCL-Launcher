# -*- coding: utf-8 -*-
from typing import overload

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from ..Windows import RoundedMenu
from ..ThemeController import *

from .Widget import Widget


class SpinBox(QSpinBox, Widget):
    @overload
    def __init__(self, parent=None):
        ...
    
    def __init__(self, *__args):
        super().__init__(*__args)
    
    def paintEvent(self, a0):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing)
        
        rect = self.rect()
        baseOpacity = self.property("baseOpacity") or 0.85
        frameOpacity = self.property("frameOpacity") or 0.0
        
        # 柔和的阴影效果
        painter.save()
        shadowOpacity = baseOpacity * 0.5
        shadowColor = QColor(0, 0, 0, int(12 * shadowOpacity))
        painter.setOpacity(shadowOpacity)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(shadowColor)
        shadowRect = rect.adjusted(2, 2, -2, -2)
        painter.drawRoundedRect(shadowRect, 14, 14)
        painter.restore()
        
        # 绘制渐变背景
        painter.save()
        painter.setOpacity(baseOpacity)
        
        bgColor = getBackgroundColour(is_highlight=self.hasFocus() and self.isEnabled())
        bgGradient = QLinearGradient(QPointF(rect.topLeft()), QPointF(rect.bottomLeft()))
        bgColorLighter = QColor(
            min(255, bgColor.red() + 12),
            min(255, bgColor.green() + 12),
            min(255, bgColor.blue() + 12)
        )
        bgGradient.setColorAt(0.0, bgColorLighter)
        bgGradient.setColorAt(1.0, bgColor)
        
        painter.setPen(getBorderColour(is_highlight=self.hasFocus() and self.isEnabled()))
        painter.setBrush(bgGradient)
        painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 16, 16)
        painter.restore()
        
        # Hover/Focus 状态效果
        if frameOpacity > 0.1:
            painter.save()
            painter.setOpacity(frameOpacity)
            
            # 外发光环
            glowColor = getBorderColour(is_highlight=True)
            glowAlpha = int(80 * frameOpacity)
            glowPen = QPen(QColor(glowColor.red(), glowColor.green(), glowColor.blue(), glowAlpha), 1.5)
            painter.setPen(glowPen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(rect.adjusted(2, 2, -2, -2), 14, 14)
            
            # 内边框高亮
            highlightPen = QPen(getBorderColour(is_highlight=True), 1.0)
            painter.setPen(highlightPen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(rect.adjusted(2, 2, -2, -2), 14, 14)
            painter.restore()
            
            if self.buttonSymbols() != SpinBox.ButtonSymbols.NoButtons:
                painter.save()
                painter.setOpacity(self.property("frameOpacity"))
                match self.buttonSymbols():
                    case SpinBox.ButtonSymbols.PlusMinus:
                        pass
                    case SpinBox.ButtonSymbols.UpDownArrows:
                        pass
                painter.restore()
        
        self.setStyleSheet(
            f"color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {self.property('baseOpacity') + (self.property('frameOpacity') * (1.0 - self.property('baseOpacity')))}); background: transparent; selection-color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {self.property('baseOpacity') + (self.property('frameOpacity') * (1.0 - self.property('baseOpacity')))}); selection-background-color: rgb{getBorderColour(is_highlight=True, is_tuple=True)}; border: none; padding: 5px;")
    
    def contextMenuEvent(self, a0):
        def updateContextMenu(self):
            if self.lineEdit():
                menus = self.findChildren(QMenu)
                if menus:
                    menu = menus[-1]
                    menu.BORDER_RADIUS = RoundedMenu.BORDER_RADIUS
                    RoundedMenu.updateQSS(menu)
                    menu.popup(QCursor.pos())
        
        QTimer.singleShot(1, lambda: updateContextMenu(self))
        super().contextMenuEvent(a0)
