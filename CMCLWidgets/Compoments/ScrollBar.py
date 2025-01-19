# -*- coding: utf-8 -*-
from typing import overload

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from ..ThemeController import *
from .ToolTip import ToolTip
from ..Windows import RoundedMenu


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
        self.setProperty("widgetOpacity", 0.6)
        self.sliderPressed.connect(lambda: self.setSliderDown(True))
        self.sliderReleased.connect(lambda: self.setSliderDown(False))

    def mousePressEvent(self, a0):
        self.setSliderDown(True)
        super().mousePressEvent(a0)

    def mouseReleaseEvent(self, a0):
        self.setSliderDown(False)
        super().mouseReleaseEvent(a0)

    def paintEvent(self, e):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self)
        painter.setOpacity(self.property("widgetOpacity"))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        op = QStyleOptionSlider()
        op.initFrom(self)
        self.initStyleOption(op)
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
        painter.restore()
        painter.save()
        painter.setPen(
            QPen(
                getBorderColour(is_highlight=True) \
                    if ((self.underMouse() or self.hasFocus()) or self.isSliderDown()) and self.isEnabled() \
                    else getForegroundColour(),
                1.0,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin
            )
        )
        painter.setBrush(
            getBorderColour(is_highlight=True) \
                if (self.isSliderDown() or self.hasFocus()) and self.isEnabled() \
                else getForegroundColour()
        )
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
            case Qt.Orientation.Vertical:
                painter.translate(QPoint(0, 0))
                painter.drawPolygon(
                    [QPoint(3, self.width() - 3), QPoint(self.width() // 2, 3),
                     QPoint(self.width() - 3, self.width() - 3)])
                painter.translate(QPoint(0, self.height() - self.width()))
                painter.drawPolygon(
                    [QPoint(3, 3), QPoint(self.width() // 2, self.width() - 3), QPoint(self.width() - 3, 3)])
        painter.restore()
        painter.save()
        painter.setPen(getBorderColour(is_highlight=self.isEnabled()))
        painter.setBrush(getBackgroundColour(is_highlight=self.isEnabled()))
        painter.drawRoundedRect(self.style().subControlRect(QStyle.ComplexControl.CC_ScrollBar, op,
                                                            QStyle.SubControl.SC_ScrollBarSlider).adjusted(2, 2, -2,
                                                                                                           -2), 10, 10)
        painter.restore()

    def contextMenuEvent(self, a0):
        menu = RoundedMenu(self)
        menu.addAction("Scroll Here",
                       lambda: self.setValue(
                           int(self.style().sliderValueFromPosition(
                               self.minimum(),
                               self.maximum(),
                               QCursor.pos().x() - self.mapToGlobal(QPoint(0,
                                                                           0)).x() if self.orientation() == Qt.Orientation.Horizontal else QCursor.pos().y() - self.mapToGlobal(
                                   QPoint(0, 0)).y(),
                               self.width() if self.orientation() == Qt.Orientation.Horizontal else self.height(),
                           ))))
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


class ScrollArea(QScrollArea):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.installEventFilter(ToolTip(self))
        self.setHorizontalScrollBar(ScrollBar(Qt.Orientation.Horizontal, self))
        self.setVerticalScrollBar(ScrollBar(Qt.Orientation.Vertical, self))
