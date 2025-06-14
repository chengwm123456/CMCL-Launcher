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
        painter.setOpacity(self.property("widgetOpacity"))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        borderColour = getBorderColour()
        backgroundColour = getBackgroundColour()
        borderGradient = QLinearGradient(QPointF(0, 0), QPointF(0, self.height()))
        borderGradient.setColorAt(0.0, borderColour)
        borderGradient.setColorAt(1.0, Colour(*borderColour,
                                              int(255 * ((max(0.6, self.property("widgetOpacity")) - 0.6) * 10) / 4)))
        backgroundGradient = QRadialGradient(QPointF(self.rect().bottomRight()), min(self.width(), self.height()))
        backgroundGradient.setColorAt(0.0, backgroundColour)
        backgroundGradient.setColorAt(1.0, Colour(*backgroundColour, 190))
        painter.setPen(QPen(QBrush(borderGradient), 1))
        painter.setBrush(QBrush(backgroundGradient))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)
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
            painter.save()
            painter.translate(button.pos())
            rect = button.rect().adjusted(1, 1, -1, -1)
            borderColour = getBorderColour(
                is_highlight=(button.isDown() or button.isChecked()) or ((
                                                                                 button.isDown() or button.isChecked() or button.underMouse() or button.hasFocus()) and self.isEnabled()))
            backgroundColour = getBackgroundColour(is_highlight=(button.isDown() or button.isChecked()) or (
                    (button.isDown() or button.isChecked()) and button.isEnabled()))
            borderGradient = QLinearGradient(QPointF(rect.x(), rect.y()), QPointF(rect.x(), rect.y() + rect.height()))
            borderGradient.setColorAt(0.0, borderColour)
            borderGradient.setColorAt(1.0, Colour(*borderColour,
                                                  int(255 * ((max(0.6,
                                                                  self.property("widgetOpacity")) - 0.6) * 10) / 4)))
            backgroundGradient = QRadialGradient(QPointF(rect.bottomRight()), min(rect.width(), rect.height()))
            backgroundGradient.setColorAt(0.0, backgroundColour)
            backgroundGradient.setColorAt(1.0, Colour(*backgroundColour, 190))
            painter.setPen(QPen(QBrush(borderGradient), 1))
            painter.setBrush(QBrush(backgroundGradient))
            painter.drawRoundedRect(rect, 10, 10)
            painter.setPen(getForegroundColour())
            painter.setBrush(getForegroundColour())
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, button.text())
            painter.restore()
