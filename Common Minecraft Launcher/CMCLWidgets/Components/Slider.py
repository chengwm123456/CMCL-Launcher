# -*- coding: utf-8 -*-
from typing import overload

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from ..ThemeController import *

from .Widget import Widget


class Slider(QSlider, Widget):
    @overload
    def __init__(self, parent=None):
        ...
    
    @overload
    def __init__(self, orientation, parent=None):
        ...
    
    def __init__(self, *__args):
        super().__init__(*__args)
        self.sliderPressed.connect(lambda: self.setSliderDown(True))
        self.sliderReleased.connect(lambda: self.setSliderDown(False))
    
    def mousePressEvent(self, ev):
        super().mousePressEvent(ev)
        if ev.button() == Qt.MouseButton.LeftButton:
            self.setSliderDown(True)
    
    def mouseReleaseEvent(self, ev):
        super().mouseReleaseEvent(ev)
        self.setSliderDown(False)
    
    def keyPressEvent(self, ev):
        super().keyPressEvent(ev)
        if ev.key() in [16777234, 16777235, 16777236, 16777237]:
            self.setSliderDown(True)
    
    def keyReleaseEvent(self, ev):
        super().keyPressEvent(ev)
        self.setSliderDown(False)
    
    def paintEvent(self, a0):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        op = QStyleOptionSlider()
        op.initFrom(self)
        self.initStyleOption(op)
        
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
        painter.setPen(getBorderColour(is_highlight=self.isSliderDown()))
        frameRect = self.rect().adjusted(
            self.property("frameRectAdjustment"),
            self.property("frameRectAdjustment"),
            -self.property("frameRectAdjustment"),
            -self.property("frameRectAdjustment")
        )
        match self.orientation():
            case Qt.Orientation.Horizontal:
                painter.drawLine(QLine(QPoint(2, self.height() // 2), QPoint(self.width() - 2, self.height() // 2)))
                painter.drawLine(QLine(
                    QPoint(2 + frameRect.x(), frameRect.height() // 2 + frameRect.y()),
                    QPoint(frameRect.width() - 2 + frameRect.x(), frameRect.height() // 2 + frameRect.y())
                ))
            case Qt.Orientation.Vertical:
                painter.drawLine(QLine(QPoint(self.width() // 2, 2), QPoint(self.width() // 2, self.height() - 2)))
                painter.drawLine(QLine(
                    QPoint(frameRect.width() // 2 + frameRect.x(), 2 + frameRect.y()),
                    QPoint(frameRect.width() // 2 + frameRect.x(), frameRect.height() // 2 + frameRect.y())
                ))
        painter.restore()
        
        rect = self.style().subControlRect(QStyle.ComplexControl.CC_Slider, op, QStyle.SubControl.SC_SliderHandle,
                                           self).adjusted(3, 3, -3, -3)
        
        painter.save()
        painter.setOpacity(self.property("baseOpacity"))
        painter.setPen(getBorderColour(is_highlight=self.isSliderDown() and self.isEnabled()))
        painter.setBrush(getBackgroundColour(is_highlight=self.isSliderDown() and self.isEnabled()))
        painter.drawEllipse(rect)
        painter.restore()
        
        if self.property("frameOpacity"):
            painter.save()
            op2 = QStyleOptionSlider()
            op2.initFrom(self)
            self.initStyleOption(op)
            op2.rect = self.rect().adjusted(
                self.property("frameRectAdjustment"),
                self.property("frameRectAdjustment"),
                -self.property("frameRectAdjustment"),
                -self.property("frameRectAdjustment")
            )
            rect2 = self.style().subControlRect(QStyle.ComplexControl.CC_Slider, op2, QStyle.SubControl.SC_SliderHandle,
                                                self).adjusted(3, 3, -3, -3)
            painter.setOpacity(self.property("frameOpacity"))
            painter.setPen(getBorderColour(is_highlight=(self.underMouse() or self.hasFocus()) and self.isEnabled()))
            painter.setBrush(getBackgroundColour(is_highlight=self.isSliderDown() and self.isEnabled()))
            painter.drawEllipse(rect2)
            painter.restore()
