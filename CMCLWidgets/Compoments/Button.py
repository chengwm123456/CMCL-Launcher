# -*- coding: utf-8 -*-
from typing import overload

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from ..ThemeController import *
from .ToolTip import ToolTip


class PushButton(QPushButton):
    @overload
    def __init__(self, parent=None):
        ...

    @overload
    def __init__(self, text, parent=None):
        ...

    @overload
    def __init__(self, icon, text, parent=None):
        ...

    def __init__(self, *__args):
        super().__init__(*__args)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.installEventFilter(ToolTip(self))
        self.installEventFilter(self)
        self.setProperty("widgetOpacity", 0.6)

    def paintEvent(self, a0):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self)
        painter.setOpacity(self.property("widgetOpacity"))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getBorderColour(
            is_highlight=(self.isDown() or self.isChecked()) or ((
                                                                         self.isDown() or self.isChecked() or self.underMouse() or self.hasFocus()) and self.isEnabled())))
        painter.setBrush(getBackgroundColour(is_highlight=(self.isDown() or self.isChecked()) or (
                (self.isDown() or self.isChecked()) and self.isEnabled())))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)
        if self.menu():
            painter.save()
            painter.setPen(QPen(getBorderColour(
                is_highlight=self.isEnabled()) if self.isDown() or self.isChecked() or self.hasFocus() or self.underMouse() else getForegroundColour(),
                                1.0,
                                Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            painter.setBrush(
                getBorderColour(
                    is_highlight=self.isEnabled()) if self.isDown() or self.isChecked() else getForegroundColour())
            painter.translate((self.width() - 8) - 3, self.height() / 2 - 4)
            painter.drawPolygon([QPoint(0, 0), QPoint(4, 8), QPoint(8, 0)])
            painter.restore()
        op = QStyleOptionButton()
        op.initFrom(self)
        self.initStyleOption(op)
        op.palette.setColor(self.foregroundRole(), getForegroundColour())
        self.style().drawControl(QStyle.ControlElement.CE_PushButtonLabel, op, painter, self)
        self.setStyleSheet("padding: 5px;")

    def keyPressEvent(self, *__args):
        super().keyPressEvent(*__args)
        if __args[0].key() == 16777220 and self.hasFocus() and self.isVisible():
            self.setDown(True)
            self.repaint()

    def keyReleaseEvent(self, *__args):
        super().keyReleaseEvent(*__args)
        if __args[0].key() == 16777220 and self.hasFocus() and self.isVisible():
            self.setDown(False)
            self.pressed.emit()
            self.repaint()

    def eventFilter(self, a0, a1):
        if self != a0:
            return super().eventFilter(a0, a1)
        match a1.type():
            case QEvent.Type.MouseButtonPress | QEvent.Type.MouseButtonRelease:
                if self.isEnabled():
                    ani = QPropertyAnimation(self, b"widgetOpacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("widgetOpacity"))
                    ani.setEndValue(1.0)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.start()
                    anit = QTimer(self)
                    self.destroyed.connect(anit.stop)
                    ani.destroyed.connect(anit.deleteLater)
                    anit.singleShot(ani.duration(), ani.deleteLater)
                else:
                    ani = QPropertyAnimation(self, b"widgetOpacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("widgetOpacity"))
                    ani.setEndValue(0.3)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.start()
                    anit = QTimer(self)
                    self.destroyed.connect(anit.stop)
                    ani.destroyed.connect(anit.deleteLater)
                    anit.singleShot(ani.duration(), ani.deleteLater)
            case QEvent.Type.Enter:
                if self.isEnabled():
                    if not self.hasFocus():
                        ani = QPropertyAnimation(self, b"widgetOpacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("widgetOpacity"))
                        ani.setEndValue(1.0)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.start()
                        anit = QTimer(self)
                        self.destroyed.connect(anit.stop)
                        ani.destroyed.connect(anit.deleteLater)
                        anit.singleShot(ani.duration(), ani.deleteLater)
                else:
                    ani = QPropertyAnimation(self, b"widgetOpacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("widgetOpacity"))
                    ani.setEndValue(0.3)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.start()
                    anit = QTimer(self)
                    self.destroyed.connect(anit.stop)
                    ani.destroyed.connect(anit.deleteLater)
                    anit.singleShot(ani.duration(), ani.deleteLater)
            case QEvent.Type.FocusIn:
                if self.isEnabled():
                    if not self.underMouse():
                        ani = QPropertyAnimation(self, b"widgetOpacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("widgetOpacity"))
                        ani.setEndValue(1.0)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.start()
                        anit = QTimer(self)
                        self.destroyed.connect(anit.stop)
                        ani.destroyed.connect(anit.deleteLater)
                        anit.singleShot(ani.duration(), ani.deleteLater)
                else:
                    ani = QPropertyAnimation(self, b"widgetOpacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("widgetOpacity"))
                    ani.setEndValue(0.3)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.start()
                    anit = QTimer(self)
                    self.destroyed.connect(anit.stop)
                    ani.destroyed.connect(anit.deleteLater)
                    anit.singleShot(ani.duration(), ani.deleteLater)
            case QEvent.Type.Leave:
                if self.isEnabled():
                    if not self.hasFocus() and \
                            not (True in (child.hasFocus() and child.isVisible() and child.isEnabled() and \
                                          child.focusPolicy() == Qt.FocusPolicy.TabFocus
                                          for child in self.findChildren(QWidget)) and self.isActiveWindow()):
                        ani = QPropertyAnimation(self, b"widgetOpacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("widgetOpacity"))
                        ani.setEndValue(0.6)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.start()
                        anit = QTimer(self)
                        self.destroyed.connect(anit.stop)
                        ani.destroyed.connect(anit.deleteLater)
                        anit.singleShot(ani.duration(), ani.deleteLater)
                else:
                    ani = QPropertyAnimation(self, b"widgetOpacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("widgetOpacity"))
                    ani.setEndValue(0.3)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.start()
                    anit = QTimer(self)
                    self.destroyed.connect(anit.stop)
                    ani.destroyed.connect(anit.deleteLater)
                    anit.singleShot(ani.duration(), ani.deleteLater)
            case QEvent.Type.FocusOut:
                if self.isEnabled():
                    if not self.underMouse() and \
                            not (True in (child.hasFocus() and child.isVisible() and child.isEnabled() and \
                                          child.focusPolicy() == Qt.FocusPolicy.TabFocus
                                          for child in self.findChildren(QWidget)) and self.isActiveWindow()):
                        ani = QPropertyAnimation(self, b"widgetOpacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("widgetOpacity"))
                        ani.setEndValue(0.6)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.start()
                        anit = QTimer(self)
                        self.destroyed.connect(anit.stop)
                        ani.destroyed.connect(anit.deleteLater)
                        anit.singleShot(ani.duration(), ani.deleteLater)
                else:
                    ani = QPropertyAnimation(self, b"widgetOpacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("widgetOpacity"))
                    ani.setEndValue(0.3)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.start()
                    anit = QTimer(self)
                    self.destroyed.connect(anit.stop)
                    ani.destroyed.connect(anit.deleteLater)
                    anit.singleShot(ani.duration(), ani.deleteLater)
            case QEvent.Type.EnabledChange:
                match self.isEnabled():
                    case True:
                        ani = QPropertyAnimation(self, b"widgetOpacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(0.3)
                        ani.setEndValue(1.0 if (self.underMouse() or self.hasFocus()) and self.isEnabled() else 0.6)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.start()
                        anit = QTimer(self)
                        self.destroyed.connect(anit.stop)
                        ani.destroyed.connect(anit.deleteLater)
                        anit.singleShot(ani.duration(), ani.deleteLater)
                    case False:
                        ani = QPropertyAnimation(self, b"widgetOpacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("widgetOpacity"))
                        ani.setEndValue(0.3)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.start()
                        anit = QTimer(self)
                        self.destroyed.connect(anit.stop)
                        ani.destroyed.connect(anit.deleteLater)
                        anit.singleShot(ani.duration(), ani.deleteLater)
            case QEvent.Type.Paint | QEvent.Type.UpdateRequest | QEvent.Type.UpdateLater | QEvent.Type.KeyPress | QEvent.Type.KeyRelease | QEvent.Type.MouseButtonPress | QEvent.Type.MouseButtonRelease:
                if self.isEnabled():
                    if self.underMouse() or self.hasFocus() or \
                            (True in (child.hasFocus() and child.isVisible() and child.isEnabled() and \
                                      child.focusPolicy() == Qt.FocusPolicy.TabFocus
                                      for child in self.findChildren(QWidget)) and self.isActiveWindow()):
                        if self.property("widgetOpacity") != 1.0 and not bool(self.findChild(QPropertyAnimation)):
                            ani = QPropertyAnimation(self, b"widgetOpacity", self)
                            ani.setDuration(500)
                            ani.setStartValue(self.property("widgetOpacity"))
                            ani.setEndValue(1.0)
                            ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                            ani.start()
                            anit = QTimer(self)
                            self.destroyed.connect(anit.stop)
                            ani.destroyed.connect(anit.deleteLater)
                            anit.singleShot(ani.duration(), ani.deleteLater)
                    else:
                        if self.property("widgetOpacity") != 0.6 and not bool(self.findChild(QPropertyAnimation)):
                            ani = QPropertyAnimation(self, b"widgetOpacity", self)
                            ani.setDuration(500)
                            ani.setStartValue(self.property("widgetOpacity"))
                            ani.setEndValue(0.6)
                            ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                            ani.start()
                            anit = QTimer(self)
                            self.destroyed.connect(anit.stop)
                            ani.destroyed.connect(anit.deleteLater)
                            anit.singleShot(ani.duration(), ani.deleteLater)
                else:
                    if self.property("widgetOpacity") != 0.3 and not bool(self.findChild(QPropertyAnimation)):
                        ani = QPropertyAnimation(self, b"widgetOpacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("widgetOpacity"))
                        ani.setEndValue(0.3)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.start()
                        anit = QTimer(self)
                        self.destroyed.connect(anit.stop)
                        ani.destroyed.connect(anit.deleteLater)
                        anit.singleShot(ani.duration(), ani.deleteLater)
        return super().eventFilter(a0, a1)


class ToolButton(QToolButton):
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.installEventFilter(ToolTip(self))
        self.installEventFilter(self)
        self.setProperty("widgetOpacity", 0.6)

    def paintEvent(self, a0):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self)
        painter.setOpacity(self.property("widgetOpacity"))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getBorderColour(
            is_highlight=(self.isDown() or self.isChecked()) or ((
                                                                         self.isDown() or self.isChecked() or self.underMouse() or self.hasFocus()) and self.isEnabled())))
        painter.setBrush(getBackgroundColour(is_highlight=(self.isDown() or self.isChecked()) or (
                (self.isDown() or self.isChecked()) and self.isEnabled())))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)
        if self.menu():
            painter.save()
            painter.setPen(QPen(getBorderColour(
                is_highlight=self.isEnabled()) if self.isDown() or self.isChecked() or self.hasFocus() or self.underMouse() else getForegroundColour(),
                                1.0,
                                Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            painter.setBrush(
                getBorderColour(
                    is_highlight=self.isEnabled()) if self.isDown() or self.isChecked() else getForegroundColour())
            painter.translate((self.width() - 8) - 3, self.height() / 2 - 4)
            painter.drawPolygon([QPoint(0, 0), QPoint(4, 8), QPoint(8, 0)])
            painter.restore()
        op = QStyleOptionToolButton()
        op.initFrom(self)
        self.initStyleOption(op)
        op.palette.setColor(self.foregroundRole(), getForegroundColour())
        self.style().drawControl(QStyle.ControlElement.CE_ToolButtonLabel, op, painter, self)
        self.setStyleSheet("padding: 5px;")

    def keyPressEvent(self, *__args):
        super().keyPressEvent(*__args)
        if __args[0].key() == 16777220 and self.hasFocus() and self.isVisible():
            self.setDown(True)
            self.repaint()

    def keyReleaseEvent(self, *__args):
        super().keyReleaseEvent(*__args)
        if __args[0].key() == 16777220 and self.hasFocus() and self.isVisible():
            self.setDown(False)
            self.pressed.emit()
            self.repaint()

    def eventFilter(self, a0, a1):
        if self != a0:
            return super().eventFilter(a0, a1)
        match a1.type():
            case QEvent.Type.MouseButtonPress | QEvent.Type.MouseButtonRelease:
                if self.isEnabled():
                    ani = QPropertyAnimation(self, b"widgetOpacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("widgetOpacity"))
                    ani.setEndValue(1.0)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.start()
                    anit = QTimer(self)
                    self.destroyed.connect(anit.stop)
                    ani.destroyed.connect(anit.deleteLater)
                    anit.singleShot(ani.duration(), ani.deleteLater)
                else:
                    ani = QPropertyAnimation(self, b"widgetOpacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("widgetOpacity"))
                    ani.setEndValue(0.3)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.start()
                    anit = QTimer(self)
                    self.destroyed.connect(anit.stop)
                    ani.destroyed.connect(anit.deleteLater)
                    anit.singleShot(ani.duration(), ani.deleteLater)
            case QEvent.Type.Enter:
                if self.isEnabled():
                    if not self.hasFocus():
                        ani = QPropertyAnimation(self, b"widgetOpacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("widgetOpacity"))
                        ani.setEndValue(1.0)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.start()
                        anit = QTimer(self)
                        self.destroyed.connect(anit.stop)
                        ani.destroyed.connect(anit.deleteLater)
                        anit.singleShot(ani.duration(), ani.deleteLater)
                else:
                    ani = QPropertyAnimation(self, b"widgetOpacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("widgetOpacity"))
                    ani.setEndValue(0.3)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.start()
                    anit = QTimer(self)
                    self.destroyed.connect(anit.stop)
                    ani.destroyed.connect(anit.deleteLater)
                    anit.singleShot(ani.duration(), ani.deleteLater)
            case QEvent.Type.FocusIn:
                if self.isEnabled():
                    if not self.underMouse():
                        ani = QPropertyAnimation(self, b"widgetOpacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("widgetOpacity"))
                        ani.setEndValue(1.0)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.start()
                        anit = QTimer(self)
                        self.destroyed.connect(anit.stop)
                        ani.destroyed.connect(anit.deleteLater)
                        anit.singleShot(ani.duration(), ani.deleteLater)
                else:
                    ani = QPropertyAnimation(self, b"widgetOpacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("widgetOpacity"))
                    ani.setEndValue(0.3)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.start()
                    anit = QTimer(self)
                    self.destroyed.connect(anit.stop)
                    ani.destroyed.connect(anit.deleteLater)
                    anit.singleShot(ani.duration(), ani.deleteLater)
            case QEvent.Type.Leave:
                if self.isEnabled():
                    if not self.hasFocus() and \
                            not (True in (child.hasFocus() and child.isVisible() and child.isEnabled() and \
                                          child.focusPolicy() == Qt.FocusPolicy.TabFocus
                                          for child in self.findChildren(QWidget)) and self.isActiveWindow()):
                        ani = QPropertyAnimation(self, b"widgetOpacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("widgetOpacity"))
                        ani.setEndValue(0.6)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.start()
                        anit = QTimer(self)
                        self.destroyed.connect(anit.stop)
                        ani.destroyed.connect(anit.deleteLater)
                        anit.singleShot(ani.duration(), ani.deleteLater)
                else:
                    ani = QPropertyAnimation(self, b"widgetOpacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("widgetOpacity"))
                    ani.setEndValue(0.3)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.start()
                    anit = QTimer(self)
                    self.destroyed.connect(anit.stop)
                    ani.destroyed.connect(anit.deleteLater)
                    anit.singleShot(ani.duration(), ani.deleteLater)
            case QEvent.Type.FocusOut:
                if self.isEnabled():
                    if not self.underMouse() and \
                            not (True in (child.hasFocus() and child.isVisible() and child.isEnabled() and \
                                          child.focusPolicy() == Qt.FocusPolicy.TabFocus
                                          for child in self.findChildren(QWidget)) and self.isActiveWindow()):
                        ani = QPropertyAnimation(self, b"widgetOpacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("widgetOpacity"))
                        ani.setEndValue(0.6)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.start()
                        anit = QTimer(self)
                        self.destroyed.connect(anit.stop)
                        ani.destroyed.connect(anit.deleteLater)
                        anit.singleShot(ani.duration(), ani.deleteLater)
                else:
                    ani = QPropertyAnimation(self, b"widgetOpacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("widgetOpacity"))
                    ani.setEndValue(0.3)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.start()
                    anit = QTimer(self)
                    self.destroyed.connect(anit.stop)
                    ani.destroyed.connect(anit.deleteLater)
                    anit.singleShot(ani.duration(), ani.deleteLater)
            case QEvent.Type.EnabledChange:
                match self.isEnabled():
                    case True:
                        ani = QPropertyAnimation(self, b"widgetOpacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(0.3)
                        ani.setEndValue(1.0 if (self.underMouse() or self.hasFocus()) and self.isEnabled() else 0.6)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.start()
                        anit = QTimer(self)
                        self.destroyed.connect(anit.stop)
                        ani.destroyed.connect(anit.deleteLater)
                        anit.singleShot(ani.duration(), ani.deleteLater)
                    case False:
                        ani = QPropertyAnimation(self, b"widgetOpacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("widgetOpacity"))
                        ani.setEndValue(0.3)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.start()
                        anit = QTimer(self)
                        self.destroyed.connect(anit.stop)
                        ani.destroyed.connect(anit.deleteLater)
                        anit.singleShot(ani.duration(), ani.deleteLater)
            case QEvent.Type.Paint | QEvent.Type.UpdateRequest | QEvent.Type.UpdateLater | QEvent.Type.KeyPress | QEvent.Type.KeyRelease | QEvent.Type.MouseButtonPress | QEvent.Type.MouseButtonRelease:
                if self.isEnabled():
                    if self.underMouse() or self.hasFocus() or \
                            (True in (child.hasFocus() and child.isVisible() and child.isEnabled() and \
                                      child.focusPolicy() == Qt.FocusPolicy.TabFocus
                                      for child in self.findChildren(QWidget)) and self.isActiveWindow()):
                        if self.property("widgetOpacity") != 1.0 and not bool(self.findChild(QPropertyAnimation)):
                            ani = QPropertyAnimation(self, b"widgetOpacity", self)
                            ani.setDuration(500)
                            ani.setStartValue(self.property("widgetOpacity"))
                            ani.setEndValue(1.0)
                            ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                            ani.start()
                            anit = QTimer(self)
                            self.destroyed.connect(anit.stop)
                            ani.destroyed.connect(anit.deleteLater)
                            anit.singleShot(ani.duration(), ani.deleteLater)
                    else:
                        if self.property("widgetOpacity") != 0.6 and not bool(self.findChild(QPropertyAnimation)):
                            ani = QPropertyAnimation(self, b"widgetOpacity", self)
                            ani.setDuration(500)
                            ani.setStartValue(self.property("widgetOpacity"))
                            ani.setEndValue(0.6)
                            ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                            ani.start()
                            anit = QTimer(self)
                            self.destroyed.connect(anit.stop)
                            ani.destroyed.connect(anit.deleteLater)
                            anit.singleShot(ani.duration(), ani.deleteLater)
                else:
                    if self.property("widgetOpacity") != 0.3 and not bool(self.findChild(QPropertyAnimation)):
                        ani = QPropertyAnimation(self, b"widgetOpacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("widgetOpacity"))
                        ani.setEndValue(0.3)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.start()
                        anit = QTimer(self)
                        self.destroyed.connect(anit.stop)
                        ani.destroyed.connect(anit.deleteLater)
                        anit.singleShot(ani.duration(), ani.deleteLater)
        return super().eventFilter(a0, a1)


class TogglePushButton(PushButton):
    @overload
    def __init__(self, parent=None):
        ...

    @overload
    def __init__(self, text, parent=None):
        ...

    @overload
    def __init__(self, icon, text, parent=None):
        ...

    def __init__(self, *__args):
        super().__init__(*__args)
        self.setCheckable(True)

    def toggleState(self):
        return self.isChecked()

    def setToggleState(self, value):
        self.setChecked(value)

    def keyPressEvent(self, *__args):
        super().keyPressEvent(*__args)
        if __args[0].key() == 16777220 and self.hasFocus() and self.isVisible():
            self.repaint()

    def keyReleaseEvent(self, *__args):
        super().keyReleaseEvent(*__args)
        if __args[0].key() == 16777220 and self.hasFocus() and self.isVisible():
            self.setChecked(not self.isChecked())
            self.pressed.emit()
            self.repaint()


class ToggleToolButton(ToolButton):
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setCheckable(True)

    def toggleState(self):
        return self.isChecked()

    def setToggleState(self, value):
        self.setChecked(value)

    def keyPressEvent(self, *__args):
        super().keyPressEvent(*__args)
        if __args[0].key() == 16777220 and self.hasFocus() and self.isVisible():
            self.repaint()

    def keyReleaseEvent(self, *__args):
        super().keyReleaseEvent(*__args)
        if __args[0].key() == 16777220 and self.hasFocus() and self.isVisible():
            self.setChecked(not self.isChecked())
            self.pressed.emit()
            self.repaint()


class CloseButton(ToolButton):
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setFixedSize(QSize(32, 32))

    def paintEvent(self, a0):
        super().paintEvent(a0)
        painter = QPainter(self)
        painter.setOpacity(self.property("widgetOpacity"))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getForegroundColour())
        painter.translate(QPointF(self.width() / 4, self.width() / 4))
        painter.drawLines([QLineF(QPointF(0, 0), QPointF(self.width() / 2, self.height() / 2)),
                           QLineF(QPointF(self.width() / 2, 0), QPointF(0, self.height() / 2))])


class CheckBox(QCheckBox):
    @overload
    def __init__(self, parent=None):
        ...

    @overload
    def __init__(self, text, parent=None):
        ...

    def __init__(self, *__args):
        super().__init__(*__args)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.installEventFilter(ToolTip(self))
        self.installEventFilter(self)
        self.setProperty("widgetOpacity", 0.6)

    def paintEvent(self, a0):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        op = QStyleOptionButton()
        op.initFrom(self)
        self.initStyleOption(op)
        op.rect.adjust(min(5, self.width()), min(5, self.height()), -min(5, self.width()), -min(5, self.height()))
        painter = QPainter(self)
        painter.setOpacity(self.property("widgetOpacity"))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getBorderColour())
        painter.setBrush(getBackgroundColour())
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)
        painter.setPen(getBorderColour(
            is_highlight=(self.isDown() or self.isChecked()) or ((
                                                                         self.isDown() or self.isChecked() or self.underMouse() or self.hasFocus()) and self.isEnabled())))
        painter.setBrush(getBackgroundColour(is_highlight=(self.isDown() or self.isChecked()) or (
                (self.isDown() or self.isChecked()) and self.isEnabled())))
        rect = self.style().subElementRect(QStyle.SubElement.SE_CheckBoxIndicator, op).adjusted(1, 1, -1, -1)
        painter.drawRoundedRect(rect, 10, 10)
        painter.save()
        painter.setPen(getForegroundColour())
        painter.setBrush(Qt.GlobalColor.transparent)
        match self.checkState():
            case Qt.CheckState.Checked:
                painter.drawLines([QLine(
                    QPoint(4 + rect.x(), rect.y() + 8),
                    QPoint(rect.width() // 2 + rect.x(), rect.y() + 10)),
                    QLine(
                        QPoint(rect.width() // 2 + rect.x(), rect.y() + 10),
                        QPoint(9 + rect.x(), rect.y() + 4))])
            case Qt.CheckState.PartiallyChecked:
                painter.drawLine(QLine(
                    QPoint(4 + rect.x(), rect.y() + rect.height() // 2),
                    QPoint(rect.x() + rect.width() - 4, rect.y() + rect.height() // 2)
                ))
        painter.restore()
        op.palette.setColor(self.foregroundRole(), getForegroundColour())
        op.rect = self.style().subElementRect(QStyle.SubElement.SE_CheckBoxContents, op)
        self.style().drawControl(QStyle.ControlElement.CE_CheckBoxLabel, op, painter, self)
        self.setStyleSheet("padding: 5px;")

    def keyPressEvent(self, *__args):
        super().keyPressEvent(*__args)
        if __args[0].key() == 16777220 and self.hasFocus() and self.isVisible():
            self.repaint()

    def keyReleaseEvent(self, *__args):
        super().keyReleaseEvent(*__args)
        if __args[0].key() == 16777220 and self.hasFocus() and self.isVisible():
            self.nextCheckState()
            self.pressed.emit()
            self.repaint()

    def eventFilter(self, a0, a1):
        if self != a0:
            return super().eventFilter(a0, a1)
        match a1.type():
            case QEvent.Type.MouseButtonPress | QEvent.Type.MouseButtonRelease:
                if self.isEnabled():
                    ani = QPropertyAnimation(self, b"widgetOpacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("widgetOpacity"))
                    ani.setEndValue(1.0)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.start()
                    anit = QTimer(self)
                    self.destroyed.connect(anit.stop)
                    ani.destroyed.connect(anit.deleteLater)
                    anit.singleShot(ani.duration(), ani.deleteLater)
                else:
                    ani = QPropertyAnimation(self, b"widgetOpacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("widgetOpacity"))
                    ani.setEndValue(0.3)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.start()
                    anit = QTimer(self)
                    self.destroyed.connect(anit.stop)
                    ani.destroyed.connect(anit.deleteLater)
                    anit.singleShot(ani.duration(), ani.deleteLater)
            case QEvent.Type.Enter:
                if self.isEnabled():
                    if not self.hasFocus():
                        ani = QPropertyAnimation(self, b"widgetOpacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("widgetOpacity"))
                        ani.setEndValue(1.0)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.start()
                        anit = QTimer(self)
                        self.destroyed.connect(anit.stop)
                        ani.destroyed.connect(anit.deleteLater)
                        anit.singleShot(ani.duration(), ani.deleteLater)
                else:
                    ani = QPropertyAnimation(self, b"widgetOpacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("widgetOpacity"))
                    ani.setEndValue(0.3)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.start()
                    anit = QTimer(self)
                    self.destroyed.connect(anit.stop)
                    ani.destroyed.connect(anit.deleteLater)
                    anit.singleShot(ani.duration(), ani.deleteLater)
            case QEvent.Type.FocusIn:
                if self.isEnabled():
                    if not self.underMouse():
                        ani = QPropertyAnimation(self, b"widgetOpacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("widgetOpacity"))
                        ani.setEndValue(1.0)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.start()
                        anit = QTimer(self)
                        self.destroyed.connect(anit.stop)
                        ani.destroyed.connect(anit.deleteLater)
                        anit.singleShot(ani.duration(), ani.deleteLater)
                else:
                    ani = QPropertyAnimation(self, b"widgetOpacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("widgetOpacity"))
                    ani.setEndValue(0.3)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.start()
                    anit = QTimer(self)
                    self.destroyed.connect(anit.stop)
                    ani.destroyed.connect(anit.deleteLater)
                    anit.singleShot(ani.duration(), ani.deleteLater)
            case QEvent.Type.Leave:
                if self.isEnabled():
                    if not self.hasFocus() and \
                            not (True in (child.hasFocus() and child.isVisible() and child.isEnabled() and \
                                          child.focusPolicy() == Qt.FocusPolicy.TabFocus
                                          for child in self.findChildren(QWidget)) and self.isActiveWindow()):
                        ani = QPropertyAnimation(self, b"widgetOpacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("widgetOpacity"))
                        ani.setEndValue(0.6)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.start()
                        anit = QTimer(self)
                        self.destroyed.connect(anit.stop)
                        ani.destroyed.connect(anit.deleteLater)
                        anit.singleShot(ani.duration(), ani.deleteLater)
                else:
                    ani = QPropertyAnimation(self, b"widgetOpacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("widgetOpacity"))
                    ani.setEndValue(0.3)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.start()
                    anit = QTimer(self)
                    self.destroyed.connect(anit.stop)
                    ani.destroyed.connect(anit.deleteLater)
                    anit.singleShot(ani.duration(), ani.deleteLater)
            case QEvent.Type.FocusOut:
                if self.isEnabled():
                    if not self.underMouse() and \
                            not (True in (child.hasFocus() and child.isVisible() and child.isEnabled() and \
                                          child.focusPolicy() == Qt.FocusPolicy.TabFocus
                                          for child in self.findChildren(QWidget)) and self.isActiveWindow()):
                        ani = QPropertyAnimation(self, b"widgetOpacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("widgetOpacity"))
                        ani.setEndValue(0.6)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.start()
                        anit = QTimer(self)
                        self.destroyed.connect(anit.stop)
                        ani.destroyed.connect(anit.deleteLater)
                        anit.singleShot(ani.duration(), ani.deleteLater)
                else:
                    ani = QPropertyAnimation(self, b"widgetOpacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("widgetOpacity"))
                    ani.setEndValue(0.3)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.start()
                    anit = QTimer(self)
                    self.destroyed.connect(anit.stop)
                    ani.destroyed.connect(anit.deleteLater)
                    anit.singleShot(ani.duration(), ani.deleteLater)
            case QEvent.Type.EnabledChange:
                match self.isEnabled():
                    case True:
                        ani = QPropertyAnimation(self, b"widgetOpacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(0.3)
                        ani.setEndValue(1.0 if (self.underMouse() or self.hasFocus()) and self.isEnabled() else 0.6)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.start()
                        anit = QTimer(self)
                        self.destroyed.connect(anit.stop)
                        ani.destroyed.connect(anit.deleteLater)
                        anit.singleShot(ani.duration(), ani.deleteLater)
                    case False:
                        ani = QPropertyAnimation(self, b"widgetOpacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("widgetOpacity"))
                        ani.setEndValue(0.3)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.start()
                        anit = QTimer(self)
                        self.destroyed.connect(anit.stop)
                        ani.destroyed.connect(anit.deleteLater)
                        anit.singleShot(ani.duration(), ani.deleteLater)
            case QEvent.Type.Paint | QEvent.Type.UpdateRequest | QEvent.Type.UpdateLater | QEvent.Type.KeyPress | QEvent.Type.KeyRelease | QEvent.Type.MouseButtonPress | QEvent.Type.MouseButtonRelease:
                if self.isEnabled():
                    if self.underMouse() or self.hasFocus() or \
                            (True in (child.hasFocus() and child.isVisible() and child.isEnabled() and \
                                      child.focusPolicy() == Qt.FocusPolicy.TabFocus
                                      for child in self.findChildren(QWidget)) and self.isActiveWindow()):
                        if self.property("widgetOpacity") != 1.0 and not bool(self.findChild(QPropertyAnimation)):
                            ani = QPropertyAnimation(self, b"widgetOpacity", self)
                            ani.setDuration(500)
                            ani.setStartValue(self.property("widgetOpacity"))
                            ani.setEndValue(1.0)
                            ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                            ani.start()
                            anit = QTimer(self)
                            self.destroyed.connect(anit.stop)
                            ani.destroyed.connect(anit.deleteLater)
                            anit.singleShot(ani.duration(), ani.deleteLater)
                    else:
                        if self.property("widgetOpacity") != 0.6 and not bool(self.findChild(QPropertyAnimation)):
                            ani = QPropertyAnimation(self, b"widgetOpacity", self)
                            ani.setDuration(500)
                            ani.setStartValue(self.property("widgetOpacity"))
                            ani.setEndValue(0.6)
                            ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                            ani.start()
                            anit = QTimer(self)
                            self.destroyed.connect(anit.stop)
                            ani.destroyed.connect(anit.deleteLater)
                            anit.singleShot(ani.duration(), ani.deleteLater)
                else:
                    if self.property("widgetOpacity") != 0.3 and not bool(self.findChild(QPropertyAnimation)):
                        ani = QPropertyAnimation(self, b"widgetOpacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("widgetOpacity"))
                        ani.setEndValue(0.3)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.start()
                        anit = QTimer(self)
                        self.destroyed.connect(anit.stop)
                        ani.destroyed.connect(anit.deleteLater)
                        anit.singleShot(ani.duration(), ani.deleteLater)
        return super().eventFilter(a0, a1)


class RadioButton(QRadioButton):
    @overload
    def __init__(self, parent=None):
        ...

    @overload
    def __init__(self, text, parent=None):
        ...

    def __init__(self, *__args):
        super().__init__(*__args)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.installEventFilter(ToolTip(self))
        self.installEventFilter(self)
        self.setProperty("widgetOpacity", 0.6)

    def paintEvent(self, a0):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        op = QStyleOptionButton()
        op.initFrom(self)
        self.initStyleOption(op)
        op.rect.adjust(min(5, self.width()), min(5, self.height()), -min(5, self.width()), -min(5, self.height()))
        painter = QPainter(self)
        painter.setOpacity(self.property("widgetOpacity"))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getBorderColour())
        painter.setBrush(getBackgroundColour())
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)
        painter.setPen(getBorderColour(
            is_highlight=(self.isDown() or self.isChecked()) or ((
                                                                         self.isDown() or self.isChecked() or self.underMouse() or self.hasFocus()) and self.isEnabled())))
        painter.setBrush(getBackgroundColour(is_highlight=(self.isDown() or self.isChecked()) or (
                (self.isDown() or self.isChecked()) and self.isEnabled())))
        rect = self.style().subElementRect(QStyle.SubElement.SE_CheckBoxIndicator, op).adjusted(1, 1, -1, -1)
        painter.drawRoundedRect(rect, 10, 10)
        op.palette.setColor(self.foregroundRole(), getForegroundColour())
        op.rect = self.style().subElementRect(QStyle.SubElement.SE_RadioButtonContents, op)
        self.style().drawControl(QStyle.ControlElement.CE_RadioButtonLabel, op, painter, self)
        self.setStyleSheet("padding: 5px;")

    def keyPressEvent(self, *__args):
        super().keyPressEvent(*__args)
        if __args[0].key() == 16777220 and self.hasFocus() and self.isVisible():
            self.repaint()

    def keyReleaseEvent(self, *__args):
        super().keyReleaseEvent(*__args)
        if __args[0].key() == 16777220 and self.hasFocus() and self.isVisible():
            self.setChecked(not self.isChecked())
            self.pressed.emit()
            self.repaint()

    def eventFilter(self, a0, a1):
        if self != a0:
            return super().eventFilter(a0, a1)
        match a1.type():
            case QEvent.Type.MouseButtonPress | QEvent.Type.MouseButtonRelease:
                if self.isEnabled():
                    ani = QPropertyAnimation(self, b"widgetOpacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("widgetOpacity"))
                    ani.setEndValue(1.0)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.start()
                    anit = QTimer(self)
                    self.destroyed.connect(anit.stop)
                    ani.destroyed.connect(anit.deleteLater)
                    anit.singleShot(ani.duration(), ani.deleteLater)
                else:
                    ani = QPropertyAnimation(self, b"widgetOpacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("widgetOpacity"))
                    ani.setEndValue(0.3)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.start()
                    anit = QTimer(self)
                    self.destroyed.connect(anit.stop)
                    ani.destroyed.connect(anit.deleteLater)
                    anit.singleShot(ani.duration(), ani.deleteLater)
            case QEvent.Type.Enter:
                if self.isEnabled():
                    if not self.hasFocus():
                        ani = QPropertyAnimation(self, b"widgetOpacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("widgetOpacity"))
                        ani.setEndValue(1.0)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.start()
                        anit = QTimer(self)
                        self.destroyed.connect(anit.stop)
                        ani.destroyed.connect(anit.deleteLater)
                        anit.singleShot(ani.duration(), ani.deleteLater)
                else:
                    ani = QPropertyAnimation(self, b"widgetOpacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("widgetOpacity"))
                    ani.setEndValue(0.3)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.start()
                    anit = QTimer(self)
                    self.destroyed.connect(anit.stop)
                    ani.destroyed.connect(anit.deleteLater)
                    anit.singleShot(ani.duration(), ani.deleteLater)
            case QEvent.Type.FocusIn:
                if self.isEnabled():
                    if not self.underMouse():
                        ani = QPropertyAnimation(self, b"widgetOpacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("widgetOpacity"))
                        ani.setEndValue(1.0)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.start()
                        anit = QTimer(self)
                        self.destroyed.connect(anit.stop)
                        ani.destroyed.connect(anit.deleteLater)
                        anit.singleShot(ani.duration(), ani.deleteLater)
                else:
                    ani = QPropertyAnimation(self, b"widgetOpacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("widgetOpacity"))
                    ani.setEndValue(0.3)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.start()
                    anit = QTimer(self)
                    self.destroyed.connect(anit.stop)
                    ani.destroyed.connect(anit.deleteLater)
                    anit.singleShot(ani.duration(), ani.deleteLater)
            case QEvent.Type.Leave:
                if self.isEnabled():
                    if not self.hasFocus() and \
                            not (True in (child.hasFocus() and child.isVisible() and child.isEnabled() and \
                                          child.focusPolicy() == Qt.FocusPolicy.TabFocus
                                          for child in self.findChildren(QWidget)) and self.isActiveWindow()):
                        ani = QPropertyAnimation(self, b"widgetOpacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("widgetOpacity"))
                        ani.setEndValue(0.6)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.start()
                        anit = QTimer(self)
                        self.destroyed.connect(anit.stop)
                        ani.destroyed.connect(anit.deleteLater)
                        anit.singleShot(ani.duration(), ani.deleteLater)
                else:
                    ani = QPropertyAnimation(self, b"widgetOpacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("widgetOpacity"))
                    ani.setEndValue(0.3)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.start()
                    anit = QTimer(self)
                    self.destroyed.connect(anit.stop)
                    ani.destroyed.connect(anit.deleteLater)
                    anit.singleShot(ani.duration(), ani.deleteLater)
            case QEvent.Type.FocusOut:
                if self.isEnabled():
                    if not self.underMouse() and \
                            not (True in (child.hasFocus() and child.isVisible() and child.isEnabled() and \
                                          child.focusPolicy() == Qt.FocusPolicy.TabFocus
                                          for child in self.findChildren(QWidget)) and self.isActiveWindow()):
                        ani = QPropertyAnimation(self, b"widgetOpacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("widgetOpacity"))
                        ani.setEndValue(0.6)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.start()
                        anit = QTimer(self)
                        self.destroyed.connect(anit.stop)
                        ani.destroyed.connect(anit.deleteLater)
                        anit.singleShot(ani.duration(), ani.deleteLater)
                else:
                    ani = QPropertyAnimation(self, b"widgetOpacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("widgetOpacity"))
                    ani.setEndValue(0.3)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.start()
                    anit = QTimer(self)
                    self.destroyed.connect(anit.stop)
                    ani.destroyed.connect(anit.deleteLater)
                    anit.singleShot(ani.duration(), ani.deleteLater)
            case QEvent.Type.EnabledChange:
                match self.isEnabled():
                    case True:
                        ani = QPropertyAnimation(self, b"widgetOpacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(0.3)
                        ani.setEndValue(1.0 if (self.underMouse() or self.hasFocus()) and self.isEnabled() else 0.6)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.start()
                        anit = QTimer(self)
                        self.destroyed.connect(anit.stop)
                        ani.destroyed.connect(anit.deleteLater)
                        anit.singleShot(ani.duration(), ani.deleteLater)
                    case False:
                        ani = QPropertyAnimation(self, b"widgetOpacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("widgetOpacity"))
                        ani.setEndValue(0.3)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.start()
                        anit = QTimer(self)
                        self.destroyed.connect(anit.stop)
                        ani.destroyed.connect(anit.deleteLater)
                        anit.singleShot(ani.duration(), ani.deleteLater)
            case QEvent.Type.Paint | QEvent.Type.UpdateRequest | QEvent.Type.UpdateLater | QEvent.Type.KeyPress | QEvent.Type.KeyRelease | QEvent.Type.MouseButtonPress | QEvent.Type.MouseButtonRelease:
                if self.isEnabled():
                    if self.underMouse() or self.hasFocus() or \
                            (True in (child.hasFocus() and child.isVisible() and child.isEnabled() and \
                                      child.focusPolicy() == Qt.FocusPolicy.TabFocus
                                      for child in self.findChildren(QWidget)) and self.isActiveWindow()):
                        if self.property("widgetOpacity") != 1.0 and not bool(self.findChild(QPropertyAnimation)):
                            ani = QPropertyAnimation(self, b"widgetOpacity", self)
                            ani.setDuration(500)
                            ani.setStartValue(self.property("widgetOpacity"))
                            ani.setEndValue(1.0)
                            ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                            ani.start()
                            anit = QTimer(self)
                            self.destroyed.connect(anit.stop)
                            ani.destroyed.connect(anit.deleteLater)
                            anit.singleShot(ani.duration(), ani.deleteLater)
                    else:
                        if self.property("widgetOpacity") != 0.6 and not bool(self.findChild(QPropertyAnimation)):
                            ani = QPropertyAnimation(self, b"widgetOpacity", self)
                            ani.setDuration(500)
                            ani.setStartValue(self.property("widgetOpacity"))
                            ani.setEndValue(0.6)
                            ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                            ani.start()
                            anit = QTimer(self)
                            self.destroyed.connect(anit.stop)
                            ani.destroyed.connect(anit.deleteLater)
                            anit.singleShot(ani.duration(), ani.deleteLater)
                else:
                    if self.property("widgetOpacity") != 0.3 and not bool(self.findChild(QPropertyAnimation)):
                        ani = QPropertyAnimation(self, b"widgetOpacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("widgetOpacity"))
                        ani.setEndValue(0.3)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.start()
                        anit = QTimer(self)
                        self.destroyed.connect(anit.stop)
                        ani.destroyed.connect(anit.deleteLater)
                        anit.singleShot(ani.duration(), ani.deleteLater)
        return super().eventFilter(a0, a1)


class SwitchButton(QAbstractButton):
    switched = pyqtSignal(bool)

    @overload
    def __init__(self, parent=None):
        ...

    @overload
    def __init__(self, on, parent=None):
        ...

    @overload
    def __init__(self, on, off, parent=None):
        ...

    def __init__(self, *__args):
        super().__init__(__args[-1])
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.installEventFilter(ToolTip(self))
        self.installEventFilter(self)
        self.setProperty("widgetOpacity", 0.6)
        self.setCheckable(True)
        self.setProperty("switchOnText", __args[0] if len(__args) > 2 else "On")
        self.setProperty("switchOffText", __args[1] if len(__args) > 2 else "Off")
        self.setMinimumSize(52, 24)

    def switchOnText(self):
        return self.property("switchOnText")

    def setSwitchOnText(self, text):
        self.setProperty("switchOnText", text)

    def switchOffText(self):
        return self.property("switchOffText")

    def setSwitchOffText(self, text):
        self.setProperty("switchOffText", text)

    def setText(self, text):
        if self.isChecked():
            self.setSwitchOnText(text)
        else:
            self.setSwitchOffText(text)

    def switchState(self):
        return self.isChecked()

    def setSwitchState(self, state):
        self.setChecked(state)

    def paintEvent(self, a0):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setMinimumSize(52 + 2 + max(self.fontMetrics().boundingRect(
            self.switchOnText()).width(), self.fontMetrics().boundingRect(
            self.switchOffText()).width()), 24)
        painter = QPainter(self)
        painter.setOpacity(self.property("widgetOpacity"))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getBorderColour())
        painter.setBrush(getBackgroundColour())
        painter.drawRoundedRect(QRect(1, (self.height() - 22) // 2, 50, 21),
                                self.height() // 2 - 1, self.height() // 2 - 1)
        painter.setPen(getBorderColour(
            is_highlight=(self.isDown() or self.isChecked()) or ((
                                                                         self.isDown() or self.isChecked() or self.underMouse() or self.hasFocus()) and self.isEnabled())))
        painter.setBrush(getBackgroundColour(is_highlight=(self.isDown() or self.isChecked()) or (
                (self.isDown() or self.isChecked()) and self.isEnabled())))
        painter.drawEllipse(QRect(3 if not self.isChecked() else 49 - 17, (self.height() - 22) // 2 + 2, 17, 17))
        painter.setPen(getForegroundColour())
        painter.setBrush(Qt.GlobalColor.transparent)
        painter.drawText(QRect(54, 0, self.width() - 52, self.height()), Qt.AlignmentFlag.AlignCenter,
                         self.switchOnText() if self.isChecked() else self.switchOffText())
        self.setStyleSheet("padding: 5px;")

    def keyPressEvent(self, *__args):
        super().keyPressEvent(*__args)
        if __args[0].key() == 16777220 and self.hasFocus() and self.isVisible():
            self.repaint()

    def keyReleaseEvent(self, *__args):
        super().keyReleaseEvent(*__args)
        if __args[0].key() == 16777220 and self.hasFocus() and self.isVisible():
            self.setChecked(not self.isChecked())
            self.pressed.emit()
            self.switched.emit(self.isChecked())
            self.repaint()

    def eventFilter(self, a0, a1):
        if self != a0:
            return super().eventFilter(a0, a1)
        match a1.type():
            case QEvent.Type.MouseButtonPress | QEvent.Type.MouseButtonRelease:
                if self.isEnabled():
                    ani = QPropertyAnimation(self, b"widgetOpacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("widgetOpacity"))
                    ani.setEndValue(1.0)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.start()
                    anit = QTimer(self)
                    self.destroyed.connect(anit.stop)
                    ani.destroyed.connect(anit.deleteLater)
                    anit.singleShot(ani.duration(), ani.deleteLater)
                else:
                    ani = QPropertyAnimation(self, b"widgetOpacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("widgetOpacity"))
                    ani.setEndValue(0.3)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.start()
                    anit = QTimer(self)
                    self.destroyed.connect(anit.stop)
                    ani.destroyed.connect(anit.deleteLater)
                    anit.singleShot(ani.duration(), ani.deleteLater)
            case QEvent.Type.Enter:
                if self.isEnabled():
                    if not self.hasFocus():
                        ani = QPropertyAnimation(self, b"widgetOpacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("widgetOpacity"))
                        ani.setEndValue(1.0)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.start()
                        anit = QTimer(self)
                        self.destroyed.connect(anit.stop)
                        ani.destroyed.connect(anit.deleteLater)
                        anit.singleShot(ani.duration(), ani.deleteLater)
                else:
                    ani = QPropertyAnimation(self, b"widgetOpacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("widgetOpacity"))
                    ani.setEndValue(0.3)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.start()
                    anit = QTimer(self)
                    self.destroyed.connect(anit.stop)
                    ani.destroyed.connect(anit.deleteLater)
                    anit.singleShot(ani.duration(), ani.deleteLater)
            case QEvent.Type.FocusIn:
                if self.isEnabled():
                    if not self.underMouse():
                        ani = QPropertyAnimation(self, b"widgetOpacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("widgetOpacity"))
                        ani.setEndValue(1.0)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.start()
                        anit = QTimer(self)
                        self.destroyed.connect(anit.stop)
                        ani.destroyed.connect(anit.deleteLater)
                        anit.singleShot(ani.duration(), ani.deleteLater)
                else:
                    ani = QPropertyAnimation(self, b"widgetOpacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("widgetOpacity"))
                    ani.setEndValue(0.3)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.start()
                    anit = QTimer(self)
                    self.destroyed.connect(anit.stop)
                    ani.destroyed.connect(anit.deleteLater)
                    anit.singleShot(ani.duration(), ani.deleteLater)
            case QEvent.Type.Leave:
                if self.isEnabled():
                    if not self.hasFocus() and \
                            not (True in (child.hasFocus() and child.isVisible() and child.isEnabled() and \
                                          child.focusPolicy() == Qt.FocusPolicy.TabFocus
                                          for child in self.findChildren(QWidget)) and self.isActiveWindow()):
                        ani = QPropertyAnimation(self, b"widgetOpacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("widgetOpacity"))
                        ani.setEndValue(0.6)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.start()
                        anit = QTimer(self)
                        self.destroyed.connect(anit.stop)
                        ani.destroyed.connect(anit.deleteLater)
                        anit.singleShot(ani.duration(), ani.deleteLater)
                else:
                    ani = QPropertyAnimation(self, b"widgetOpacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("widgetOpacity"))
                    ani.setEndValue(0.3)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.start()
                    anit = QTimer(self)
                    self.destroyed.connect(anit.stop)
                    ani.destroyed.connect(anit.deleteLater)
                    anit.singleShot(ani.duration(), ani.deleteLater)
            case QEvent.Type.FocusOut:
                if self.isEnabled():
                    if not self.underMouse() and \
                            not (True in (child.hasFocus() and child.isVisible() and child.isEnabled() and \
                                          child.focusPolicy() == Qt.FocusPolicy.TabFocus
                                          for child in self.findChildren(QWidget)) and self.isActiveWindow()):
                        ani = QPropertyAnimation(self, b"widgetOpacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("widgetOpacity"))
                        ani.setEndValue(0.6)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.start()
                        anit = QTimer(self)
                        self.destroyed.connect(anit.stop)
                        ani.destroyed.connect(anit.deleteLater)
                        anit.singleShot(ani.duration(), ani.deleteLater)
                else:
                    ani = QPropertyAnimation(self, b"widgetOpacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("widgetOpacity"))
                    ani.setEndValue(0.3)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.start()
                    anit = QTimer(self)
                    self.destroyed.connect(anit.stop)
                    ani.destroyed.connect(anit.deleteLater)
                    anit.singleShot(ani.duration(), ani.deleteLater)
            case QEvent.Type.EnabledChange:
                match self.isEnabled():
                    case True:
                        ani = QPropertyAnimation(self, b"widgetOpacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(0.3)
                        ani.setEndValue(1.0 if (self.underMouse() or self.hasFocus()) and self.isEnabled() else 0.6)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.start()
                        anit = QTimer(self)
                        self.destroyed.connect(anit.stop)
                        ani.destroyed.connect(anit.deleteLater)
                        anit.singleShot(ani.duration(), ani.deleteLater)
                    case False:
                        ani = QPropertyAnimation(self, b"widgetOpacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("widgetOpacity"))
                        ani.setEndValue(0.3)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.start()
                        anit = QTimer(self)
                        self.destroyed.connect(anit.stop)
                        ani.destroyed.connect(anit.deleteLater)
                        anit.singleShot(ani.duration(), ani.deleteLater)
            case QEvent.Type.Paint | QEvent.Type.UpdateRequest | QEvent.Type.UpdateLater | QEvent.Type.KeyPress | QEvent.Type.KeyRelease | QEvent.Type.MouseButtonPress | QEvent.Type.MouseButtonRelease:
                if self.isEnabled():
                    if self.underMouse() or self.hasFocus() or \
                            (True in (child.hasFocus() and child.isVisible() and child.isEnabled() and \
                                      child.focusPolicy() == Qt.FocusPolicy.TabFocus
                                      for child in self.findChildren(QWidget)) and self.isActiveWindow()):
                        if self.property("widgetOpacity") != 1.0 and not bool(self.findChild(QPropertyAnimation)):
                            ani = QPropertyAnimation(self, b"widgetOpacity", self)
                            ani.setDuration(500)
                            ani.setStartValue(self.property("widgetOpacity"))
                            ani.setEndValue(1.0)
                            ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                            ani.start()
                            anit = QTimer(self)
                            self.destroyed.connect(anit.stop)
                            ani.destroyed.connect(anit.deleteLater)
                            anit.singleShot(ani.duration(), ani.deleteLater)
                    else:
                        if self.property("widgetOpacity") != 0.6 and not bool(self.findChild(QPropertyAnimation)):
                            ani = QPropertyAnimation(self, b"widgetOpacity", self)
                            ani.setDuration(500)
                            ani.setStartValue(self.property("widgetOpacity"))
                            ani.setEndValue(0.6)
                            ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                            ani.start()
                            anit = QTimer(self)
                            self.destroyed.connect(anit.stop)
                            ani.destroyed.connect(anit.deleteLater)
                            anit.singleShot(ani.duration(), ani.deleteLater)
                else:
                    if self.property("widgetOpacity") != 0.3 and not bool(self.findChild(QPropertyAnimation)):
                        ani = QPropertyAnimation(self, b"widgetOpacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("widgetOpacity"))
                        ani.setEndValue(0.3)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.start()
                        anit = QTimer(self)
                        self.destroyed.connect(anit.stop)
                        ani.destroyed.connect(anit.deleteLater)
                        anit.singleShot(ani.duration(), ani.deleteLater)
        return super().eventFilter(a0, a1)
