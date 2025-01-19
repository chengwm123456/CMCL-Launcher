# -*- coding: utf-8 -*-
from typing import overload

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from ..ThemeController import *
from .ToolTip import ToolTip
from .ScrollBar import ScrollBar


class ItemDelegate(QItemDelegate):
    def paint(self, painter, option, index):
        option.rect.setX(option.rect.x() + 10)
        option.rect.setWidth(option.rect.width() - 5)
        super().paint(painter, option, index)
        # self.drawDecoration(painter, option, option.rect, QPixmap())
        # self.drawDisplay(painter, option, option.rect, index.data())

    def drawDecoration(self, painter, option, rect, pixmap):
        painter.save()
        painter.setOpacity(self.parent().property("widgetOpacity") or 1.0)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)
        painter.setPen(
            getBorderColour(is_highlight=((option.rect.contains(QCursor.pos() - (
                self.parent().viewport().mapToGlobal(QPoint(0, 0)) if hasattr(self.parent(),
                                                                              "viewport") else self.parent().mapToGlobal(
                    QPoint(0, 0))))) and self.parent().underMouse()) and self.parent().isEnabled()))
        painter.setBrush(getBackgroundColour())
        painter.drawRoundedRect(option.rect.adjusted(1, 1, -1, -1), 10, 10)
        painter.restore()

    def drawFocus(self, painter, option, rect):
        pass

    def drawBackground(self, painter, option, rect):
        pass

    def drawDisplay(self, painter, option, rect, text):
        painter.save()
        painter.setOpacity(self.parent().property("widgetOpacity") or 1.0)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)
        painter.setPen(getForegroundColour())
        painter.drawText(option.rect.adjusted(1, 1, -1, -1), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                         text)
        painter.restore()


class ItemView(QAbstractItemView):
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
