# -*- coding: utf-8 -*-
from typing import overload

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from ..ThemeController import *
from .ToolTip import ToolTip
from ..Windows import RoundedMenu
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
                f"color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {0.6 if self.isEnabled() else 0.3}); background: transparent; border: none; padding: 5px;")
            self.lineEdit().setFont(self.font())
        self.setStyle(QStyleFactory.create("Windows"))
        self.setView(ListView(self))
        self.view().window().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.view().window().setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint |
            Qt.WindowType.Popup
        )
        self.view().window().update()
        
        self.setProperty("dropdownIndicatorRotation", 0.0)
    
    def showPopup(self):
        self.view().window().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.view().window().setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint |
            Qt.WindowType.Popup
        )
        self.view().window().update()
        super().showPopup()
        self.view().window().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.view().window().setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint |
            Qt.WindowType.Popup
        )
        self.view().window().update()
        
        if self.count():
            rotationAnimation = QPropertyAnimation(self, b"dropdownIndicatorRotation", self)
            rotationAnimation.setStartValue(self.property("dropdownIndicatorRotation"))
            rotationAnimation.setEndValue(180.0)
            rotationAnimation.setDuration(500)
            rotationAnimation.setEasingCurve(QEasingCurve.Type.OutExpo)
            rotationAnimation.start()
    
    def hidePopup(self):
        super().hidePopup()
        
        rotationAnimation = QPropertyAnimation(self, b"dropdownIndicatorRotation", self)
        rotationAnimation.setStartValue(self.property("dropdownIndicatorRotation"))
        rotationAnimation.setEndValue(0.0)
        rotationAnimation.setDuration(500)
        rotationAnimation.setEasingCurve(QEasingCurve.Type.OutExpo)
        rotationAnimation.start()
    
    def paintEvent(self, e):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        if self.lineEdit():
            self.lineEdit().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            self.lineEdit().setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
            self.lineEdit().setStyleSheet(
                f"color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {self.property('baseOpacity') + (self.property('frameOpacity') * (1.0 - self.property('baseOpacity')))}); background: transparent; selection-color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {self.property('baseOpacity') + (self.property('frameOpacity') * (1.0 - self.property('baseOpacity')))}); selection-background-color: rgb{getBorderColour(is_highlight=True, is_tuple=True)}; border: none; padding: 5px;")
            self.lineEdit().setFont(self.font())
            self.lineEdit().setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            self.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        else:
            self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
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
        
        painter.save()
        x = (self.width() - 8) - 3 + 4
        y = self.height() / 2 - 2 + 2
        painter.setOpacity(self.property("baseOpacity"))
        painter.setPen(getBorderColour(is_highlight=self.hasFocus() and self.isEnabled()))
        painter.translate(x, y)
        painter.rotate(self.property("dropdownIndicatorRotation"))
        painter.drawLines([QLineF(QPointF(-4, -2), QPointF(0, 2)), QLineF(QPointF(0, 2), QPointF(4, -2))])
        painter.restore()
        
        if self.property("frameOpacity"):
            painter.save()
            x = (self.width() - 8) - 3 + 4
            y = self.height() / 2 - 2 + 2
            painter.setOpacity(self.property("frameOpacity"))
            painter.setPen(getBorderColour(is_highlight=True))
            painter.translate(x, y)
            painter.rotate(self.property("dropdownIndicatorRotation"))
            painter.drawLines([QLineF(QPointF(-4, -2), QPointF(0, 2)), QLineF(QPointF(0, 2), QPointF(4, -2))])
            painter.restore()
        
        op = QStyleOptionComboBox()
        op.initFrom(self)
        self.initStyleOption(op)
        op.palette.setColor(op.palette.ColorRole.Text, getForegroundColour())
        painter.save()
        painter.setOpacity(
            self.property("baseOpacity") + (self.property("frameOpacity") * (1.0 - self.property("baseOpacity"))))
        self.style().drawControl(QStyle.ControlElement.CE_ComboBoxLabel, op, painter, self)
        painter.restore()
        self.setStyleSheet("padding: 5px;")
    
    def contextMenuEvent(self, e):
        super().contextMenuEvent(e)
        if self.lineEdit() and self.isEditable():
            menus = self.findChildren(QMenu)
            if menus:
                menu = menus[-1]
                menu.BORDER_RADIUS = RoundedMenu.BORDER_RADIUS
                RoundedMenu.updateQSS(menu)
                menu.popup(QCursor.pos())
    
    def hasFocus(self):
        return super().hasFocus() or self.view().hasFocus()
    
    def setFont(self, font):
        super().setFont(font)
        self.view().setFont(font)
        if self.isEditable():
            self.lineEdit().setFont(font)
