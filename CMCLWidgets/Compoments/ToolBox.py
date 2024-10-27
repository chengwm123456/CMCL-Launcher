# -*- coding: utf-8 -*-
from typing import overload

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from ..ThemeManager import *
from CMCLWidgets.ToolTip import ToolTip


class ToolBox(QToolBox):
    @overload
    def __init__(self, parent=None):
        ...
    
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.installEventFilter(ToolTip(self))
        self.installEventFilter(self)
        self.setProperty("Opacity", 0.6)
    
    def paintEvent(self, a0):
        self.setStyleSheet("padding: 3px;")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self)
        painter.setOpacity(self.property("Opacity"))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getBorderColour())
        painter.setBrush(getBackgroundColour())
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)
        for i in self.children():
            if isinstance(i, QAbstractButton):
                i.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
                i.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
                opacity = QGraphicsOpacityEffect(i)
                opacity.setOpacity(0.0)
                i.setGraphicsEffect(opacity)
                painter.save()
                painter.setPen(getBorderColour(
                    is_highlight=(i.isDown() or i.isChecked()) or ((
                                                                           i.isDown() or i.isChecked() or i.underMouse() or i.hasFocus()) and self.isEnabled())))
                painter.setBrush(getBackgroundColour(is_highlight=(i.isDown() or i.isChecked()) or (
                        (i.isDown() or i.isChecked()) and i.isEnabled())))
                painter.drawRoundedRect(i.geometry().adjusted(1, 1, -1, -1), 10, 10)
                painter.setPen(getForegroundColour())
                painter.setBrush(getForegroundColour())
                painter.drawText(i.geometry().adjusted(1, 1, -1, -1), Qt.AlignmentFlag.AlignCenter, i.text())
                painter.restore()
    
    def eventFilter(self, a0, a1):
        if self != a0:
            return super().eventFilter(a0, a1)
        match a1.type():
            case QEvent.Type.MouseButtonPress:
                if self.isEnabled():
                    ani = QPropertyAnimation(self, b"Opacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("Opacity"))
                    ani.setEndValue(1.0)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.finished.connect(ani.deleteLater)
                    ani.start()
                else:
                    ani = QPropertyAnimation(self, b"Opacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("Opacity"))
                    ani.setEndValue(0.3)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.finished.connect(ani.deleteLater)
                    ani.start()
            case QEvent.Type.MouseMove:
                if self.isEnabled():
                    ani = QPropertyAnimation(self, b"Opacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("Opacity"))
                    ani.setEndValue(1.0)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.finished.connect(ani.deleteLater)
                    ani.start()
                else:
                    ani = QPropertyAnimation(self, b"Opacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("Opacity"))
                    ani.setEndValue(0.3)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.finished.connect(ani.deleteLater)
                    ani.start()
            case QEvent.Type.Enter:
                if self.isEnabled():
                    if not self.hasFocus():
                        ani = QPropertyAnimation(self, b"Opacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("Opacity"))
                        ani.setEndValue(1.0)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.finished.connect(ani.deleteLater)
                        ani.start()
                else:
                    ani = QPropertyAnimation(self, b"Opacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("Opacity"))
                    ani.setEndValue(0.3)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.finished.connect(ani.deleteLater)
                    ani.start()
            case QEvent.Type.FocusIn:
                if self.isEnabled():
                    if not self.underMouse():
                        ani = QPropertyAnimation(self, b"Opacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("Opacity"))
                        ani.setEndValue(1.0)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.finished.connect(ani.deleteLater)
                        ani.start()
                else:
                    ani = QPropertyAnimation(self, b"Opacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("Opacity"))
                    ani.setEndValue(0.3)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.finished.connect(ani.deleteLater)
                    ani.start()
            case QEvent.Type.Leave:
                if self.isEnabled():
                    if not self.hasFocus():
                        ani = QPropertyAnimation(self, b"Opacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("Opacity"))
                        ani.setEndValue(0.6)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.finished.connect(ani.deleteLater)
                        ani.start()
                else:
                    ani = QPropertyAnimation(self, b"Opacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("Opacity"))
                    ani.setEndValue(0.3)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.finished.connect(ani.deleteLater)
                    ani.start()
            case QEvent.Type.FocusOut:
                if self.isEnabled():
                    if not self.underMouse():
                        ani = QPropertyAnimation(self, b"Opacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("Opacity"))
                        ani.setEndValue(0.6)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.finished.connect(ani.deleteLater)
                        ani.start()
                else:
                    ani = QPropertyAnimation(self, b"Opacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("Opacity"))
                    ani.setEndValue(0.3)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.finished.connect(ani.deleteLater)
                    ani.start()
            case QEvent.Type.EnabledChange:
                match self.isEnabled:
                    case True:
                        ani = QPropertyAnimation(self, b"Opacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(0.3)
                        ani.setEndValue(1.0 if (self.underMouse() or self.hasFocus()) and self.isEnabled() else 0.6)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.finished.connect(ani.deleteLater)
                        ani.start()
                    case False:
                        ani = QPropertyAnimation(self, b"Opacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("Opacity"))
                        ani.setEndValue(0.3)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.finished.connect(ani.deleteLater)
                        ani.start()
        return super().eventFilter(a0, a1)
