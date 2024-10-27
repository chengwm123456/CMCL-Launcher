# -*- coding: utf-8 -*-
from typing import overload

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from ..ThemeManager import *
from CMCLWidgets.ToolTip import ToolTip
from CMCLWidgets.Windows import RoundedMenu


class ScrollBar(QScrollBar):
    @overload
    def __init__(self, parent=None):
        ...
    
    @overload
    def __init__(self, orientation, parent=None):
        ...
    
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.installEventFilter(ToolTip(self))
        self.installEventFilter(self)
        self.setProperty("Opacity", 0.6)
    
    def paintEvent(self, e):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self)
        painter.setOpacity(self.property("Opacity"))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.save()
        painter.setPen(getBorderColour())
        painter.setBrush(getBackgroundColour())
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)
        match self.orientation():
            case Qt.Orientation.Horizontal:
                painter.drawLines([QLine(QPoint(self.height(), 2), QPoint(self.height(), self.height() - 2)),
                                   QLine(QPoint(self.width() - self.height(), 2),
                                         QPoint(self.width() - self.height(), self.height() - 2))])
            case Qt.Orientation.Vertical:
                painter.drawLines([QLine(QPoint(2, self.width()), QPoint(self.width() - 2, self.width())),
                                   QLine(QPoint(2, self.height() - self.width()),
                                         QPoint(self.width() - 2, self.height() - self.width()))])
        painter.setPen(
            QPen(
                getBorderColour(is_highlight=True) \
                    if (self.underMouse() or self.hasFocus()) and self.isEnabled() \
                    else getForegroundColour(),
                1.0,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin
            )
        )
        painter.setBrush(getForegroundColour())
        match self.orientation():
            case Qt.Orientation.Horizontal:
                painter.translate(QPoint(0, 0))
                painter.drawPolygon(
                    [QPoint(3, self.height() // 2), QPoint(self.height() - 3, self.height() - 3),
                     QPoint(self.height() - 3, 3)])
                painter.translate(QPoint(self.width() - self.height(), 0))
                painter.drawPolygon(
                    [QPoint(self.height() - 3, self.height() // 2), QPoint(3, self.height() - 3),
                     QPoint(3, 3)])
                painter.translate(QPoint(0, 0))
            case Qt.Orientation.Vertical:
                painter.translate(QPoint(0, 0))
                painter.drawPolygon(
                    [QPoint(3, self.width() - 3), QPoint(self.width() // 2, 3),
                     QPoint(self.width() - 3, self.width() - 3)])
                painter.translate(QPoint(0, self.height() - self.width()))
                painter.drawPolygon(
                    [QPoint(3, 3), QPoint(self.width() // 2, self.width() - 3), QPoint(self.width() - 3, 3)])
                painter.translate(QPoint(0, 0))
        painter.restore()
        painter.save()
        painter.setPen(getBorderColour(is_highlight=(self.underMouse() or self.hasFocus()) and self.isEnabled()))
        painter.setBrush(getBackgroundColour(is_highlight=self.isEnabled()))
        x = 0
        y = 0
        width = 0
        height = 0
        match self.orientation():
            case Qt.Orientation.Horizontal:
                x = max(min(self.width() - 50 - self.height(),
                            int((self.value() / (self.maximum() or 1)) * (
                                    self.width() - self.height() - max((self.width() - self.maximum()), 50)) + (
                                        self.height() * (1.0 - (self.value() / (self.maximum() or 1)))))),
                        self.height())
                y = 0
                width = min(max(50, self.width() - self.maximum()),
                            self.width() - x - self.height())
                height = self.height()
            case Qt.Orientation.Vertical:
                x = 0
                y = max(min(self.height() - 50 - self.width(),
                            int((self.value() / (self.maximum() or 1)) * (
                                    self.height() - self.width() - max((self.height() - self.maximum()), 50)) + (
                                        self.width() * (1.0 - (self.value() / (self.maximum() or 1)))))),
                        self.width())
                width = self.width()
                height = min(max(50, self.height() - self.maximum()),
                             self.height() - y - self.width())
        painter.drawRoundedRect(QRect(x, y, width, height).adjusted(2, 2, -2, -2), 10, 10)
        painter.restore()
    
    def contextMenuEvent(self, a0):
        menu = RoundedMenu(self)
        value = 0
        match self.orientation():
            case Qt.Orientation.Horizontal:
                value = QCursor.pos().x() - self.mapToGlobal(
                    QPoint(0, 0)).x()
            case Qt.Orientation.Vertical:
                value = QCursor.pos().y() - self.mapToGlobal(
                    QPoint(0, 0)).y() * self.height()
        if value >= self.maximum():
            value = self.maximum()
        if value <= 0:
            value = 0
        print(value, QCursor.pos().y() - self.mapToGlobal(QPoint(0, 0)).y(), self.height(), self.maximum(),
              self.height() / self.maximum(), value / (self.height() / self.maximum()))
        menu.addAction("Scroll Here", lambda: self.setValue(int(value)))
        menu.addSeparator()
        menu.addAction("Top", lambda: self.setValue(0))
        menu.addAction("Bottom", lambda: self.setValue(self.maximum()))
        menu.addSeparator()
        menu.addAction("Page up", lambda: self.setValue(max(0, self.value() - self.pageStep())))
        menu.addAction("Page down", lambda: self.setValue(min(self.maximum(), self.value() + self.pageStep())))
        menu.addSeparator()
        menu.addAction("Scroll up", lambda: self.setValue(max(0, self.value() - 20)))
        menu.addAction("Scroll down", lambda: self.setValue(min(self.maximum(), self.value() + 20)))
        menu.popup(QCursor.pos())
    
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


class ScrollArea(QScrollArea):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.installEventFilter(ToolTip(self))
        self.setHorizontalScrollBar(ScrollBar(Qt.Orientation.Horizontal, self))
        self.setVerticalScrollBar(ScrollBar(Qt.Orientation.Vertical, self))
