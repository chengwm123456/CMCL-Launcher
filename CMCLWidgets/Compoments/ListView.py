# -*- coding: utf-8 -*-
from typing import overload

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from ..ThemeController import *
from .ToolTip import ToolTip
from .ItemView import ItemDelegate
from .ScrollBar import ScrollBar


class ListView(QListView):
    @overload
    def __init__(self, parent=None):
        ...

    def __init__(self, *__args):
        super().__init__(*__args)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.installEventFilter(ToolTip(self))
        self.installEventFilter(self)
        self.setProperty("widgetOpacity", 0.6)
        self.setItemDelegate(ItemDelegate(self))
        self.setHorizontalScrollBar(ScrollBar(Qt.Orientation.Horizontal, self))
        self.setVerticalScrollBar(ScrollBar(Qt.Orientation.Vertical, self))

    def paintEvent(self, e):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self.viewport())
        painter.setOpacity(self.property("widgetOpacity"))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getBorderColour())
        painter.setBrush(getBackgroundColour())
        rect = self.viewport().rect()
        rect.setWidth(rect.width() - rect.x() - 1)
        rect.setHeight(rect.height() - rect.y() - 1)
        rect.setX(1)
        rect.setY(1)
        painter.drawRoundedRect(rect, 10, 10)
        op = QStyleOptionFrame()
        op.initFrom(self)
        self.initStyleOption(op)
        self.setStyleSheet(
            f"color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {str(painter.opacity())}); background: transparent; border: none;")
        super().paintEvent(e)

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
                    anit.singleShot(ani.duration(), ani.deleteLater)
            case QEvent.Type.Leave:
                if self.isEnabled():
                    if not self.hasFocus():
                        ani = QPropertyAnimation(self, b"widgetOpacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("widgetOpacity"))
                        ani.setEndValue(0.6)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.start()
                        anit = QTimer(self)
                        self.destroyed.connect(anit.stop)
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
                    anit.singleShot(ani.duration(), ani.deleteLater)
            case QEvent.Type.FocusOut:
                if self.isEnabled():
                    if not self.underMouse():
                        ani = QPropertyAnimation(self, b"widgetOpacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("widgetOpacity"))
                        ani.setEndValue(0.6)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.start()
                        anit = QTimer(self)
                        self.destroyed.connect(anit.stop)
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
                        anit.singleShot(ani.duration(), ani.deleteLater)
            case QEvent.Type.Paint | QEvent.Type.UpdateRequest:
                if self.isEnabled():
                    if self.underMouse() or self.hasFocus():
                        if self.property("widgetOpacity") != 1.0 and not bool(self.findChild(QPropertyAnimation)):
                            ani = QPropertyAnimation(self, b"widgetOpacity", self)
                            ani.setDuration(500)
                            ani.setStartValue(self.property("widgetOpacity"))
                            ani.setEndValue(1.0)
                            ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                            ani.start()
                            anit = QTimer(self)
                            self.destroyed.connect(anit.stop)
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
                        anit.singleShot(ani.duration(), ani.deleteLater)
        return super().eventFilter(a0, a1)


class ListWidget(QListWidget):
    @overload
    def __init__(self, parent=None):
        ...

    def __init__(self, *__args):
        super().__init__(*__args)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.installEventFilter(ToolTip(self))
        self.installEventFilter(self)
        self.setProperty("widgetOpacity", 0.6)
        self.setItemDelegate(ItemDelegate(self))
        self.setHorizontalScrollBar(ScrollBar(Qt.Orientation.Horizontal, self))
        self.setVerticalScrollBar(ScrollBar(Qt.Orientation.Vertical, self))

    def paintEvent(self, e):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self.viewport())
        painter.setOpacity(self.property("widgetOpacity"))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getBorderColour())
        painter.setBrush(getBackgroundColour())
        rect = self.viewport().rect()
        rect.setWidth(rect.width() - rect.x() - 1)
        rect.setHeight(rect.height() - rect.y() - 1)
        rect.setX(1)
        rect.setY(1)
        painter.drawRoundedRect(rect, 10, 10)
        op = QStyleOptionFrame()
        op.initFrom(self)
        self.initStyleOption(op)
        self.setStyleSheet(
            f"color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {str(painter.opacity())}); background: transparent; border: none;")
        super().paintEvent(e)

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
                    anit.singleShot(ani.duration(), ani.deleteLater)
            case QEvent.Type.Leave:
                if self.isEnabled():
                    if not self.hasFocus():
                        ani = QPropertyAnimation(self, b"widgetOpacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("widgetOpacity"))
                        ani.setEndValue(0.6)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.start()
                        anit = QTimer(self)
                        self.destroyed.connect(anit.stop)
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
                    anit.singleShot(ani.duration(), ani.deleteLater)
            case QEvent.Type.FocusOut:
                if self.isEnabled():
                    if not self.underMouse():
                        ani = QPropertyAnimation(self, b"widgetOpacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("widgetOpacity"))
                        ani.setEndValue(0.6)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.start()
                        anit = QTimer(self)
                        self.destroyed.connect(anit.stop)
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
                        anit.singleShot(ani.duration(), ani.deleteLater)
            case QEvent.Type.Paint | QEvent.Type.UpdateRequest:
                if self.isEnabled():
                    if self.underMouse() or self.hasFocus():
                        if self.property("widgetOpacity") != 1.0 and not bool(self.findChild(QPropertyAnimation)):
                            ani = QPropertyAnimation(self, b"widgetOpacity", self)
                            ani.setDuration(500)
                            ani.setStartValue(self.property("widgetOpacity"))
                            ani.setEndValue(1.0)
                            ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                            ani.start()
                            anit = QTimer(self)
                            self.destroyed.connect(anit.stop)
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
                        anit.singleShot(ani.duration(), ani.deleteLater)
        return super().eventFilter(a0, a1)
