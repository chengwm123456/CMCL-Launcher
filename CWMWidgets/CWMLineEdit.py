# -*- coding: utf-8 -*-
from typing import overload

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from .CWMToolTip import ToolTip
from .CWMWindows import RoundedMenu
from .CWMThemeControl import *


class LineEdit(QLineEdit):
    @overload
    def __init__(self, parent=None):
        ...
    
    @overload
    def __init__(self, contents, parent=None):
        ...
    
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.installEventFilter(ToolTip(self))
        self.installEventFilter(self)
        self.setProperty("Opacity", 0.6)
    
    def paintEvent(self, a0):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self)
        painter.setOpacity(self.property("Opacity"))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getBorderColour(is_highlight=self.hasFocus() or self.underMouse()))
        painter.setBrush(getBackgroundColour(is_highlight=self.hasFocus()))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)
        self.setStyleSheet(
            f"color: rgba({str(getForegroundColour(is_tuple=True)).replace('(', '').replace(')', '')}, {str(painter.opacity())}); background: transparent; border: none; padding: 5px;")
        op = QStyleOptionFrame()
        op.initFrom(self)
        self.initStyleOption(op)
        super().paintEvent(a0)
    
    def contextMenuEvent(self, e):
        default = self.createStandardContextMenu()
        menu = RoundedMenu(self)
        for i in default.actions():
            menu.addAction(i)
        menu.exec(self.mapToGlobal(e.pos()))
    
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
                if self.isEnabled():
                    ani = QPropertyAnimation(self, b"Opacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(0.3)
                    ani.setEndValue(1.0 if (self.underMouse() or self.hasFocus()) and self.isEnabled() else 0.6)
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
        return super().eventFilter(a0, a1)
