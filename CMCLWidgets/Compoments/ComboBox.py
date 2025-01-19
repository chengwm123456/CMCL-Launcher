# -*- coding: utf-8 -*-
from typing import overload

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from ..ThemeController import *
from .ToolTip import ToolTip
from CMCLWidgets.Windows import RoundedMenu
from .ListView import ListWidget


class ComboBox(QComboBox):
    @overload
    def __init__(self, parent=None):
        ...

    def __init__(self, *__args):
        super().__init__(*__args)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        if self.lineEdit():
            self.lineEdit().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            self.lineEdit().setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
            self.lineEdit().installEventFilter(ToolTip(self))
            self.lineEdit().setStyleSheet(
                f"color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {str(0.6)}); background: transparent; border: none;")
            self.lineEdit().setFont(self.font())
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.installEventFilter(ToolTip(self))
        self.installEventFilter(self)
        self.setProperty("widgetOpacity", 0.6)
        self.setView(ListWidget(self))
        self.setModel(self.view().model())
        self.view().setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.view().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def paintEvent(self, e):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        if self.lineEdit():
            self.lineEdit().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            self.lineEdit().setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
            self.lineEdit().setStyleSheet(
                f"color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {str(self.property('widgetOpacity') or 1.0)}); background: transparent; border: none;")
            self.lineEdit().setFont(self.font())
        painter = QPainter(self)
        painter.setOpacity(self.property("widgetOpacity"))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getBorderColour(is_highlight=(self.hasFocus() or self.underMouse()) and self.isEnabled()))
        painter.setBrush(getBackgroundColour(is_highlight=self.hasFocus() and self.isEnabled()))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)
        painter.save()
        painter.setPen(QPen(getBorderColour(
            is_highlight=self.isEnabled()) if (
                                                      self.hasFocus() or self.underMouse() or self.view().isVisible()) and self.isEnabled() else getForegroundColour(),
                            1.0,
                            Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(getBorderColour(
            is_highlight=self.isEnabled()) if self.view().isVisible() and self.isEnabled() else getForegroundColour())
        painter.translate((self.width() - 8) - 3, self.height() / 2 - 4)
        painter.drawPolygon([QPoint(0, 0), QPoint(4, 8), QPoint(8, 0)])
        painter.restore()
        op = QStyleOptionComboBox()
        op.initFrom(self)
        self.initStyleOption(op)
        op.palette.setColor(op.palette.ColorRole.Text, getForegroundColour())
        self.style().drawControl(QStyle.ControlElement.CE_ComboBoxLabel, op, painter, self)
        self.view().setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.view().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.view().update()

    def contextMenuEvent(self, e):
        if self.lineEdit() and self.isEditable():
            default = self.lineEdit().createStandardContextMenu()
            menu = RoundedMenu(self)
            for i in default.actions():
                menu.addAction(i)
            menu.exec(self.mapToGlobal(e.pos()))

    def hasFocus(self):
        return super().hasFocus() or self.view().hasFocus()

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
