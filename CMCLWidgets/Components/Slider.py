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
        painter = QPainter(self)
        painter.setOpacity(self.property("widgetOpacity"))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        op = QStyleOptionSlider()
        op.initFrom(self)
        self.initStyleOption(op)
        painter.save()
        borderColour = getBorderColour()
        backgroundColour = getBackgroundColour()
        borderGradient = QRadialGradient(QPointF(self.mapFromGlobal(QCursor.pos())),
                                         max(self.width(), self.height()))
        borderGradient.setColorAt(0.0, borderColour)
        borderGradient.setColorAt(1.0, Colour(*borderColour, 32))
        painter.setPen(QPen(QBrush(borderGradient), 1))
        backgroundGradient = QLinearGradient(QPointF(0, 0), QPointF(0, self.height()))
        backgroundGradient.setColorAt(0.0, backgroundColour)
        backgroundGradient.setColorAt(1.0, Colour(*backgroundColour, 210))
        painter.setBrush(QBrush(backgroundGradient))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)
        borderColour = getBorderColour(is_highlight=self.isSliderDown())
        backgroundColour = getBackgroundColour(is_highlight=self.isSliderDown())
        borderGradient = QRadialGradient(QPointF(self.mapFromGlobal(QCursor.pos())),
                                         max(self.width(), self.height()))
        borderGradient.setColorAt(0.0, borderColour)
        borderGradient.setColorAt(1.0, Colour(*borderColour, 32))
        painter.setPen(QPen(QBrush(borderGradient), 1))
        backgroundGradient = QLinearGradient(QPointF(0, 0), QPointF(0, self.height()))
        backgroundGradient.setColorAt(0.0, backgroundColour)
        backgroundGradient.setColorAt(1.0, Colour(*backgroundColour, 210))
        painter.setBrush(QBrush(backgroundGradient))
        match self.orientation():
            case Qt.Orientation.Horizontal:
                painter.drawLine(QLine(QPoint(2, self.height() // 2), QPoint(self.width() - 2, self.height() // 2)))
            case Qt.Orientation.Vertical:
                painter.drawLine(QLine(QPoint(self.width() // 2, 2), QPoint(self.width() // 2, self.height() - 2)))
        painter.restore()
        painter.save()
        rect = self.style().subControlRect(QStyle.ComplexControl.CC_Slider, op, QStyle.SubControl.SC_SliderHandle,
                                           self).adjusted(3, 3, -3, -3)
        borderColour = getBorderColour(is_highlight=(self.underMouse() or self.hasFocus()) and self.isEnabled())
        backgroundColour = getBackgroundColour(is_highlight=(self.isSliderDown()) and self.isEnabled())
        borderGradient = QRadialGradient(QPointF(self.mapFromGlobal(QCursor.pos())),
                                         max(rect.width(), rect.height()))
        borderGradient.setColorAt(0.0, borderColour)
        borderGradient.setColorAt(1.0, Colour(*borderColour, 32))
        painter.setPen(QPen(QBrush(borderGradient), 1))
        backgroundGradient = QLinearGradient(QPointF(0, 0), QPointF(0, rect.height()))
        backgroundGradient.setColorAt(0.0, backgroundColour)
        backgroundGradient.setColorAt(1.0, Colour(*backgroundColour, 210))
        painter.setBrush(QBrush(backgroundGradient))
        painter.drawEllipse(rect)
        painter.restore()
