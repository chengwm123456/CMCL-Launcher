# -*- coding: utf-8 -*-
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from ..ThemeController import getBackgroundColour, getBorderColour

from .ToolTip import ToolTip


class Widget(QWidget):
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setUpdatesEnabled(True)
        self.installEventFilter(self)
        self.installEventFilter(ToolTip(self))
        
        self.setStyleSheet("border: none; background: transparent; padding: 3px;")
    
    def isDisabled(self):
        return not self.isEnabled()
    
    def widgetAttribute(self, attr, default=None):
        return self.property(f"widgetAttributes.{attr}") or default
    
    def setWidgetAttribute(self, attr, val=True):
        self.setProperty(f"widgetAttributes.{attr}", val)
    
    def paintEvent(self, a0):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing)

        rect = self.rect()
        baseOpacity = self.property("baseOpacity") or 0.85
        frameOpacity = self.property("frameOpacity") or 0.0

        # 柔和的阴影效果
        if frameOpacity > 0.1 or baseOpacity > 0.5:
            painter.save()
            shadowOpacity = frameOpacity * 0.6 + baseOpacity * 0.2
            
            # 外层大阴影
            shadowColor1 = QColor(0, 0, 0, int(10 * shadowOpacity))
            painter.setOpacity(shadowOpacity * 0.8)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(shadowColor1)
            shadowRect1 = rect.adjusted(4, 4, -4, -4)
            painter.drawRoundedRect(shadowRect1, 10, 10)
            
            # 内层阴影
            shadowColor2 = QColor(0, 0, 0, int(6 * shadowOpacity))
            painter.setOpacity(shadowOpacity * 0.6)
            painter.setBrush(shadowColor2)
            shadowRect2 = rect.adjusted(2, 2, -2, -2)
            painter.drawRoundedRect(shadowRect2, 8, 8)
            painter.restore()

        # 微妙的背景层
        painter.save()
        painter.setOpacity(baseOpacity * 0.08)
        painter.setPen(Qt.PenStyle.NoPen)
        bgColor = getBackgroundColour()
        painter.setBrush(bgColor)
        painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 8, 8)
        painter.restore()

        # Hover/Focus 状态的增强效果
        if frameOpacity > 0.1:
            # 外发光环
            painter.save()
            painter.setOpacity(frameOpacity * 0.6)
            
            glowColor = getBorderColour(is_highlight=True)
            for i in range(2):
                glowAlpha = int((50 - i * 15) * frameOpacity)
                glowPen = QPen(QColor(glowColor.red(), glowColor.green(), glowColor.blue(), glowAlpha), 1.5 - i * 0.5)
                glowPen.setWidthF(1.5 - i * 0.5)
                painter.setPen(glowPen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                glowOffset = i + 1
                painter.drawRoundedRect(
                    rect.adjusted(-glowOffset, -glowOffset, glowOffset, glowOffset),
                    8 + glowOffset, 8 + glowOffset
                )
            painter.restore()
            
            # 高亮边框
            painter.save()
            painter.setOpacity(frameOpacity)
            
            borderGradient = QLinearGradient(QPointF(rect.topLeft()), QPointF(rect.bottomLeft()))
            highlightColor = getBorderColour(is_highlight=True)
            borderColorLighter = QColor(
                min(255, highlightColor.red() + 20),
                min(255, highlightColor.green() + 20),
                min(255, highlightColor.blue() + 20)
            )
            borderGradient.setColorAt(0.0, borderColorLighter)
            borderGradient.setColorAt(1.0, highlightColor)
            
            pen = QPen(borderGradient, 1.5)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 7, 7)
            painter.restore()

    def eventFilter(self, a0, a1):
        if not (a0.property("widgetOpacity") or a0.property("baseOpacity") or a0.property("frameOpacity")):
            a0.setProperty("widgetOpacity", 0.85 if a0.isEnabled() else 0.4)
            a0.setProperty("baseOpacity", 0.85 if a0.isEnabled() else 0.4)
            a0.setProperty("frameOpacity", 0.0)
        a0.setProperty("frameRectAdjustment", 0)
        match a1.type():
            case QEvent.Type.MouseButtonPress | QEvent.Type.MouseButtonRelease | QEvent.Type.MouseMove:
                a0.setAttribute(Qt.WidgetAttribute.WA_UnderMouse)
            case QEvent.Type.Enter:
                if a0.isEnabled():
                    fadeInAnimation = QPropertyAnimation(a0, b"frameOpacity", a0)
                    fadeInAnimation.setStartValue(a0.property("frameOpacity"))
                    fadeInAnimation.setEndValue(1.0)
                    fadeInAnimation.setDuration(350)
                    fadeInAnimation.setEasingCurve(QEasingCurve.Type.OutCubic)
                    fadeInAnimation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                else:
                    opacityAnimationBase = QPropertyAnimation(a0, b"baseOpacity", a0)
                    opacityAnimationBase.setStartValue(a0.property("baseOpacity"))
                    opacityAnimationBase.setEndValue(0.4)
                    opacityAnimationBase.setDuration(350)
                    opacityAnimationBase.setEasingCurve(QEasingCurve.Type.OutCubic)
                    opacityAnimationBase.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                    fadeOutAnimationFrame = QPropertyAnimation(a0, b"frameOpacity", a0)
                    fadeOutAnimationFrame.setStartValue(a0.property("frameOpacity"))
                    fadeOutAnimationFrame.setEndValue(0.0)
                    fadeOutAnimationFrame.setDuration(350)
                    fadeOutAnimationFrame.setEasingCurve(QEasingCurve.Type.OutCubic)
                    fadeOutAnimationFrame.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
            case QEvent.Type.Leave:
                if not a0.hasFocus():
                    fadeOutAnimation = QPropertyAnimation(a0, b"frameOpacity", a0)
                    fadeOutAnimation.setStartValue(a0.property("frameOpacity"))
                    fadeOutAnimation.setEndValue(0.0)
                    fadeOutAnimation.setDuration(350)
                    fadeOutAnimation.setEasingCurve(QEasingCurve.Type.OutCubic)
                    fadeOutAnimation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
            case QEvent.Type.FocusIn:
                if a0.isEnabled():
                    fadeInAnimation = QPropertyAnimation(a0, b"frameOpacity", a0)
                    fadeInAnimation.setStartValue(a0.property("frameOpacity"))
                    fadeInAnimation.setEndValue(1.0)
                    fadeInAnimation.setDuration(350)
                    fadeInAnimation.setEasingCurve(QEasingCurve.Type.OutCubic)
                    fadeInAnimation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                else:
                    opacityAnimationBase = QPropertyAnimation(a0, b"baseOpacity", a0)
                    opacityAnimationBase.setStartValue(a0.property("baseOpacity"))
                    opacityAnimationBase.setEndValue(0.4)
                    opacityAnimationBase.setDuration(350)
                    opacityAnimationBase.setEasingCurve(QEasingCurve.Type.OutCubic)
                    opacityAnimationBase.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                    fadeOutAnimationFrame = QPropertyAnimation(a0, b"frameOpacity", a0)
                    fadeOutAnimationFrame.setStartValue(a0.property("frameOpacity"))
                    fadeOutAnimationFrame.setEndValue(0.0)
                    fadeOutAnimationFrame.setDuration(350)
                    fadeOutAnimationFrame.setEasingCurve(QEasingCurve.Type.OutCubic)
                    fadeOutAnimationFrame.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
            case QEvent.Type.FocusOut:
                if not a0.underMouse():
                    fadeOutAnimation = QPropertyAnimation(a0, b"frameOpacity", a0)
                    fadeOutAnimation.setStartValue(a0.property("frameOpacity"))
                    fadeOutAnimation.setEndValue(0.0)
                    fadeOutAnimation.setDuration(350)
                    fadeOutAnimation.setEasingCurve(QEasingCurve.Type.OutCubic)
                    fadeOutAnimation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
            case QEvent.Type.EnabledChange:
                match a0.isEnabled():
                    case True:
                        opacityAnimationBase = QPropertyAnimation(a0, b"baseOpacity", a0)
                        opacityAnimationBase.setStartValue(a0.property("baseOpacity"))
                        opacityAnimationBase.setEndValue(0.85)
                        opacityAnimationBase.setDuration(350)
                        opacityAnimationBase.setEasingCurve(QEasingCurve.Type.OutCubic)
                        opacityAnimationBase.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                        if a0.underMouse() or a0.hasFocus():
                            fadeInAnimation = QPropertyAnimation(a0, b"frameOpacity", a0)
                            fadeInAnimation.setStartValue(a0.property("frameOpacity"))
                            fadeInAnimation.setEndValue(1.0)
                            fadeInAnimation.setDuration(350)
                            fadeInAnimation.setEasingCurve(QEasingCurve.Type.OutCubic)
                            fadeInAnimation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                    case False:
                        opacityAnimationBase = QPropertyAnimation(a0, b"baseOpacity", a0)
                        opacityAnimationBase.setStartValue(a0.property("baseOpacity"))
                        opacityAnimationBase.setEndValue(0.4)
                        opacityAnimationBase.setDuration(350)
                        opacityAnimationBase.setEasingCurve(QEasingCurve.Type.OutCubic)
                        opacityAnimationBase.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                        fadeOutAnimationFrame = QPropertyAnimation(a0, b"frameOpacity", a0)
                        fadeOutAnimationFrame.setStartValue(a0.property("frameOpacity"))
                        fadeOutAnimationFrame.setEndValue(0.0)
                        fadeOutAnimationFrame.setDuration(350)
                        fadeOutAnimationFrame.setEasingCurve(QEasingCurve.Type.OutCubic)
                        fadeOutAnimationFrame.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
            case QEvent.Type.Paint:
                if a0.isEnabled():
                    if a0.property("baseOpacity") != 0.85 and not bool(a0.findChildren(QPropertyAnimation)):
                        opacityAnimationBase = QPropertyAnimation(a0, b"baseOpacity", a0)
                        opacityAnimationBase.setStartValue(a0.property("baseOpacity"))
                        opacityAnimationBase.setEndValue(0.85)
                        opacityAnimationBase.setDuration(350)
                        opacityAnimationBase.setEasingCurve(QEasingCurve.Type.OutCubic)
                        opacityAnimationBase.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                    if a0.underMouse() or a0.hasFocus():
                        if a0.property("frameOpacity") != 1.0 and not bool(a0.findChildren(QPropertyAnimation)):
                            fadeInAnimation = QPropertyAnimation(a0, b"frameOpacity", a0)
                            fadeInAnimation.setStartValue(a0.property("frameOpacity"))
                            fadeInAnimation.setEndValue(1.0)
                            fadeInAnimation.setDuration(350)
                            fadeInAnimation.setEasingCurve(QEasingCurve.Type.OutCubic)
                            fadeInAnimation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                    else:
                        if a0.property("frameOpacity") != 0.0 and not bool(a0.findChildren(QPropertyAnimation)):
                            fadeOutAnimation = QPropertyAnimation(a0, b"frameOpacity", a0)
                            fadeOutAnimation.setStartValue(a0.property("frameOpacity"))
                            fadeOutAnimation.setEndValue(0.0)
                            fadeOutAnimation.setDuration(350)
                            fadeOutAnimation.setEasingCurve(QEasingCurve.Type.OutCubic)
                            fadeOutAnimation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                else:
                    if a0.property("baseOpacity") != 0.4 and not bool(a0.findChildren(QPropertyAnimation)):
                        opacityAnimationBase = QPropertyAnimation(a0, b"baseOpacity", a0)
                        opacityAnimationBase.setStartValue(a0.property("baseOpacity"))
                        opacityAnimationBase.setEndValue(0.4)
                        opacityAnimationBase.setDuration(350)
                        opacityAnimationBase.setEasingCurve(QEasingCurve.Type.OutCubic)
                        opacityAnimationBase.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                    
                    if a0.property("frameOpacity") != 0.0 and not bool(a0.findChildren(QPropertyAnimation)):
                        fadeOutAnimationFrame = QPropertyAnimation(a0, b"frameOpacity", a0)
                        fadeOutAnimationFrame.setStartValue(a0.property("frameOpacity"))
                        fadeOutAnimationFrame.setEndValue(0.0)
                        fadeOutAnimationFrame.setDuration(350)
                        fadeOutAnimationFrame.setEasingCurve(QEasingCurve.Type.OutCubic)
                        fadeOutAnimationFrame.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        return super().eventFilter(a0, a1)
