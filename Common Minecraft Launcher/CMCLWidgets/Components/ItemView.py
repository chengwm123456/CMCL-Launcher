# -*- coding: utf-8 -*-
from typing import overload

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from ..ThemeController import *
from .ScrollBar import ScrollBar
from ..Windows import RoundedMenu

from .Widget import Widget


class ItemDelegateLineEdit(QLineEdit, Widget):
    def setClearButtonEnabled(self, enable):
        super().setClearButtonEnabled(enable)
        if self.findChild(QToolButton):
            old_button = self.findChild(QToolButton)
            new_button = CloseButton(old_button.parent())
            new_button.setFixedSize(old_button.size())
            new_button.move(old_button.x(), old_button.y())
            new_button.setEnabled(bool(self.text()))
            new_button.setProperty("baseOpacity", 0.3 if not self.text() else 0.6)
            new_button.clicked.connect(old_button.clicked.emit)
            old_button.setVisible(False)
        else:
            self.findChild(CloseButton).destroy()
    
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
        
        if frameOpacity > 0.1:
            painter.save()
            painter.setOpacity(frameOpacity)
            
            glowColor = getBorderColour(is_highlight=True)
            glowAlpha = int(80 * frameOpacity)
            glowPen = QPen(QColor(glowColor.red(), glowColor.green(), glowColor.blue(), glowAlpha), 1.5)
            painter.setPen(glowPen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(rect.adjusted(2, 2, -2, -2), 14, 14)
            
            highlightPen = QPen(getBorderColour(is_highlight=True), 1.0)
            painter.setPen(highlightPen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(rect.adjusted(2, 2, -2, -2), 14, 14)
            painter.restore()
        
        self.setStyleSheet(
            f"color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {self.property('baseOpacity') + (self.property('frameOpacity') * (1.0 - self.property('baseOpacity')))}); background: transparent; selection-color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {self.property('baseOpacity') + (self.property('frameOpacity') * (1.0 - self.property('baseOpacity')))}); selection-background-color: rgb{getBorderColour(is_highlight=True, is_tuple=True)}; border: none; padding: 5px;")
        super().paintEvent(a0)
    
    def contextMenuEvent(self, e):
        super().contextMenuEvent(e)
        menus = self.findChildren(QMenu)
        if menus:
            menu = menus[-1]
            menu.BORDER_RADIUS = RoundedMenu.BORDER_RADIUS
            RoundedMenu.updateQSS(menu)
            menu.popup(QCursor.pos())


class ItemDelegate(QItemDelegate):
    def paint(self, painter, option, index):
        if index.column() == 0:
            row = index.row()
            model = index.model()
            rowCount = model.rowCount()
            
            if row % 2 == 1:
                rowRect = QRect(option.rect)
                
                if isinstance(model, QAbstractListModel):
                    pass
                else:
                    for col in range(1, model.columnCount()):
                        colIndex = model.index(row, col)
                        colRect = self.parent().visualRect(colIndex)
                        if not colRect.isEmpty() and colRect.right() > rowRect.right():
                            rowRect.setWidth(colRect.right() - rowRect.left())
                    rowRect.setX(rowRect.x() + 5)
                    rowRect.setWidth(rowRect.width() + 5)
                
                painter.save()
                painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing)
                
                viewport = self.parent().viewport()
                painter.setOpacity(viewport.property("baseOpacity") if viewport else 1.0)
                painter.setPen(getBorderColour())
                
                bgColor = getBackgroundColour()
                bgGradient = QLinearGradient(QPointF(rowRect.topLeft()), QPointF(rowRect.bottomLeft()))
                bgColorLighter = QColor(
                    min(255, bgColor.red() + 8),
                    min(255, bgColor.green() + 8),
                    min(255, bgColor.blue() + 8)
                )
                bgGradient.setColorAt(0.0, bgColorLighter)
                bgGradient.setColorAt(1.0, bgColor)
                painter.setBrush(bgGradient)
                painter.drawRoundedRect(rowRect.adjusted(1, 0, -1, 0), 16, 16)
                
                painter.restore()
        
        if option.state & QStyle.StateFlag.State_Selected:
            painter.save()
            painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing)
            
            viewport = self.parent().viewport()
            painter.setOpacity(viewport.property("baseOpacity") if viewport else 1.0)
            
            painter.setPen(getBorderColour(is_highlight=True))
            
            bgColor = getBackgroundColour(is_highlight=True)
            bgGradient = QLinearGradient(QPointF(option.rect.topLeft()), QPointF(option.rect.bottomLeft()))
            bgColorLighter = QColor(
                min(255, bgColor.red() + 8),
                min(255, bgColor.green() + 8),
                min(255, bgColor.blue() + 8)
            )
            bgGradient.setColorAt(0.0, bgColorLighter)
            bgGradient.setColorAt(1.0, bgColor)
            painter.setBrush(bgGradient)
            
            rowRect = QRect(option.rect)
            rowRect.setX(rowRect.x() + 5)
            rowRect.setWidth(rowRect.width() + 5)
            painter.drawRoundedRect(rowRect.adjusted(1, 0, -1, 0), 16, 16)
            
            painter.restore()
        
        option.state &= ~QStyle.StateFlag.State_Selected
        option.state &= ~QStyle.StateFlag.State_HasFocus
        option.showDecorationSelected = False
        
        option.rect.setX(option.rect.x() + 10)
        option.rect.setWidth(option.rect.width() - 5)
        super().paint(painter, option, index)
    
    def createEditor(self, parent, option, index):
        editor = ItemDelegateLineEdit(parent)
        return editor


class ItemView(QAbstractItemView, Widget):
    @overload
    def __init__(self, parent=None):
        ...
    
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setItemDelegate(ItemDelegate(self))
        self.setHorizontalScrollBar(ScrollBar(Qt.Orientation.Horizontal, self))
        self.setVerticalScrollBar(ScrollBar(Qt.Orientation.Vertical, self))
    
    def paintEvent(self, e):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self.viewport())
        painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing)
        
        rect = self.viewport().rect()
        baseOpacity = self.property("baseOpacity") or 0.85
        
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
        painter.setOpacity(baseOpacity * 0.3)
        
        glowColor = QColor(255, 255, 255, int(180 * baseOpacity))
        painter.setPen(QPen(glowColor, 1.5))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect.adjusted(2, 2, -2, -2), 14, 14)
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
        
        op = QStyleOptionFrame()
        op.initFrom(self)
        self.initStyleOption(op)
        self.setStyleSheet(
            f"color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {self.viewport().property('baseOpacity') + (self.viewport().property('frameOpacity') * (1.0 - self.viewport().property('baseOpacity')))}); background: transparent; border: none;")
        super().paintEvent(e)
