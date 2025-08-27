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
                f"color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {self.property('baseOpacity') + (self.property('frameOpacity') * (1.0 - self.property('baseOpacity')))}); background: transparent; border: none; padding: 5px;")
            self.lineEdit().setFont(self.font())
            self.lineEdit().setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            self.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        else:
            self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.save()
        painter.setOpacity(self.property("baseOpacity"))
        painter.setPen(getBorderColour(is_highlight=self.hasFocus() and self.isEnabled()))
        painter.setBrush(getBackgroundColour(is_highlight=self.hasFocus() and self.isEnabled()))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 16, 16)
        painter.restore()
        
        if self.property("frameOpacity"):
            painter.save()
            painter.setOpacity(self.property("frameOpacity"))
            painter.setPen(getBorderColour(is_highlight=True))
            painter.setBrush(getBackgroundColour(is_highlight=self.hasFocus() and self.isEnabled()))
            painter.drawRoundedRect(
                self.rect().adjusted(
                    1 + self.property("frameRectAdjustment"),
                    1 + self.property("frameRectAdjustment"),
                    -(1 + self.property("frameRectAdjustment")),
                    -(1 + self.property("frameRectAdjustment"))
                ), 16, 16
            )
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
            rect2 = self.rect().adjusted(
                self.property("frameRectAdjustment"),
                self.property("frameRectAdjustment"),
                -self.property("frameRectAdjustment"),
                -self.property("frameRectAdjustment")
            )
            adjustmentScaleRatio = 1 - (self.property("frameRectAdjustment") / min(
                32, min(self.width() // 2, self.height() // 2)))
            x2 = (rect2.width() - 8) - 3 + 4 + rect2.x()
            y2 = rect2.height() / 2 - 2 + 2 + rect2.y()
            painter.setOpacity(self.property("frameOpacity"))
            painter.setPen(getBorderColour(is_highlight=True))
            painter.translate(x2, y2)
            painter.rotate(self.property("dropdownIndicatorRotation"))
            painter.drawLines(
                [
                    QLineF(QPointF(-4 * adjustmentScaleRatio, -2 * adjustmentScaleRatio),
                           QPointF(0, 2 * adjustmentScaleRatio)),
                    QLineF(QPointF(0, 2 * adjustmentScaleRatio),
                           QPointF(4 * adjustmentScaleRatio, -2 * adjustmentScaleRatio))
                ]
            )
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
