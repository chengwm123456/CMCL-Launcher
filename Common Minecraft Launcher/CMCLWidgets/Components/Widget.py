# -*- coding: utf-8 -*-
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from .ToolTip import ToolTip


class Widget(QWidget):
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.installEventFilter(self)
        self.installEventFilter(ToolTip(self))
    
    def eventFilter(self, a0, a1):
        if self != a0:
            return super().eventFilter(a0, a1)
        if not isinstance(self.property("widgetOpacity"), (float, int)):
            self.setProperty("widgetOpacity", 0.6 if self.isEnabled() else 0.3)
        match a1.type():
            case QEvent.Type.MouseButtonPress | QEvent.Type.MouseButtonRelease:
                self.setAttribute(Qt.WidgetAttribute.WA_UnderMouse)
            case QEvent.Type.Enter:
                if self.isEnabled():
                    if not self.hasFocus():
                        opacityAnimation = QPropertyAnimation(self, b"widgetOpacity", self)
                        opacityAnimation.setDuration(500)
                        opacityAnimation.setStartValue(self.property("widgetOpacity"))
                        opacityAnimation.setEndValue(1.0)
                        opacityAnimation.setEasingCurve(QEasingCurve.Type.OutExpo)
                        opacityAnimation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                else:
                    opacityAnimation = QPropertyAnimation(self, b"widgetOpacity", self)
                    opacityAnimation.setDuration(500)
                    opacityAnimation.setStartValue(self.property("widgetOpacity"))
                    opacityAnimation.setEndValue(0.3)
                    opacityAnimation.setEasingCurve(QEasingCurve.Type.OutExpo)
                    opacityAnimation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
            case QEvent.Type.FocusIn:
                if self.isEnabled():
                    if not self.underMouse():
                        opacityAnimation = QPropertyAnimation(self, b"widgetOpacity", self)
                        opacityAnimation.setDuration(500)
                        opacityAnimation.setStartValue(self.property("widgetOpacity"))
                        opacityAnimation.setEndValue(1.0)
                        opacityAnimation.setEasingCurve(QEasingCurve.Type.OutExpo)
                        opacityAnimation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                else:
                    opacityAnimation = QPropertyAnimation(self, b"widgetOpacity", self)
                    opacityAnimation.setDuration(500)
                    opacityAnimation.setStartValue(self.property("widgetOpacity"))
                    opacityAnimation.setEndValue(0.3)
                    opacityAnimation.setEasingCurve(QEasingCurve.Type.OutExpo)
                    opacityAnimation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
            case QEvent.Type.Leave:
                if self.isEnabled():
                    if not self.hasFocus() and \
                            not (any(child.hasFocus() and child.isVisible() and child.isEnabled() and
                                     child.focusPolicy() == Qt.FocusPolicy.TabFocus
                                     for child in self.findChildren(QWidget)) and self.isActiveWindow()):
                        opacityAnimation = QPropertyAnimation(self, b"widgetOpacity", self)
                        opacityAnimation.setDuration(500)
                        opacityAnimation.setStartValue(self.property("widgetOpacity"))
                        opacityAnimation.setEndValue(0.6)
                        opacityAnimation.setEasingCurve(QEasingCurve.Type.OutExpo)
                        opacityAnimation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                else:
                    opacityAnimation = QPropertyAnimation(self, b"widgetOpacity", self)
                    opacityAnimation.setDuration(500)
                    opacityAnimation.setStartValue(self.property("widgetOpacity"))
                    opacityAnimation.setEndValue(0.3)
                    opacityAnimation.setEasingCurve(QEasingCurve.Type.OutExpo)
                    opacityAnimation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
            case QEvent.Type.FocusOut:
                if self.isEnabled():
                    if not self.underMouse() and \
                            not (any(child.hasFocus() and child.isVisible() and child.isEnabled() and
                                     child.focusPolicy() == Qt.FocusPolicy.TabFocus
                                     for child in self.findChildren(QWidget)) and self.isActiveWindow()):
                        opacityAnimation = QPropertyAnimation(self, b"widgetOpacity", self)
                        opacityAnimation.setDuration(500)
                        opacityAnimation.setStartValue(self.property("widgetOpacity"))
                        opacityAnimation.setEndValue(0.6)
                        opacityAnimation.setEasingCurve(QEasingCurve.Type.OutExpo)
                        opacityAnimation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                else:
                    opacityAnimation = QPropertyAnimation(self, b"widgetOpacity", self)
                    opacityAnimation.setDuration(500)
                    opacityAnimation.setStartValue(self.property("widgetOpacity"))
                    opacityAnimation.setEndValue(0.3)
                    opacityAnimation.setEasingCurve(QEasingCurve.Type.OutExpo)
                    opacityAnimation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
            case QEvent.Type.EnabledChange:
                match self.isEnabled():
                    case True:
                        opacityAnimation = QPropertyAnimation(self, b"widgetOpacity", self)
                        opacityAnimation.setDuration(500)
                        opacityAnimation.setStartValue(self.property("widgetOpacity"))
                        opacityAnimation.setEndValue(
                            1.0 if (self.underMouse() or self.hasFocus()) and self.isEnabled() else 0.6)
                        opacityAnimation.setEasingCurve(QEasingCurve.Type.OutExpo)
                        opacityAnimation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                    case False:
                        opacityAnimation = QPropertyAnimation(self, b"widgetOpacity", self)
                        opacityAnimation.setDuration(500)
                        opacityAnimation.setStartValue(self.property("widgetOpacity"))
                        opacityAnimation.setEndValue(0.3)
                        opacityAnimation.setEasingCurve(QEasingCurve.Type.OutExpo)
                        opacityAnimation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
            case QEvent.Type.Paint | QEvent.Type.UpdateRequest | QEvent.Type.UpdateLater | QEvent.Type.KeyPress | QEvent.Type.KeyRelease | QEvent.Type.MouseButtonPress | QEvent.Type.MouseButtonRelease:
                if self.isEnabled():
                    if self.underMouse() or self.hasFocus() or \
                            (any(child.hasFocus() and child.isVisible() and child.isEnabled() and
                                 child.focusPolicy() == Qt.FocusPolicy.TabFocus
                                 for child in self.findChildren(QWidget)) and self.isActiveWindow()):
                        if self.property("widgetOpacity") != 1.0 and not bool(self.findChild(QPropertyAnimation)):
                            opacityAnimation = QPropertyAnimation(self, b"widgetOpacity", self)
                            opacityAnimation.setDuration(500)
                            opacityAnimation.setStartValue(self.property("widgetOpacity"))
                            opacityAnimation.setEndValue(1.0)
                            opacityAnimation.setEasingCurve(QEasingCurve.Type.OutExpo)
                            opacityAnimation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                    else:
                        if self.property("widgetOpacity") != 0.6 and not bool(self.findChild(QPropertyAnimation)):
                            opacityAnimation = QPropertyAnimation(self, b"widgetOpacity", self)
                            opacityAnimation.setDuration(500)
                            opacityAnimation.setStartValue(self.property("widgetOpacity"))
                            opacityAnimation.setEndValue(0.6)
                            opacityAnimation.setEasingCurve(QEasingCurve.Type.OutExpo)
                            opacityAnimation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                else:
                    if self.property("widgetOpacity") != 0.3 and not bool(self.findChild(QPropertyAnimation)):
                        opacityAnimation = QPropertyAnimation(self, b"widgetOpacity", self)
                        opacityAnimation.setDuration(500)
                        opacityAnimation.setStartValue(self.property("widgetOpacity"))
                        opacityAnimation.setEndValue(0.3)
                        opacityAnimation.setEasingCurve(QEasingCurve.Type.OutExpo)
                        opacityAnimation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        return super().eventFilter(a0, a1)
