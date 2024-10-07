# -*- coding: utf-8 -*-
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from .CWMThemeControl import *
from .CWMToolTip import ToolTip
from .CWMItemView import ItemDelegate
from .CWMScrollBar import ScrollBar


class HeaderView(QHeaderView):
    def __init__(self, orientation, parent):
        super().__init__(orientation, parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.installEventFilter(ToolTip(self))
        self.installEventFilter(self)
        self.setProperty("Opacity", 0.6)
        if orientation == Qt.Orientation.Vertical:
            self.setFixedWidth(int(self.fontMetrics().maxWidth() * 1.5))
        if orientation == Qt.Orientation.Horizontal:
            self.setFixedHeight(int(self.fontMetrics().height() * 2))
        self.setHorizontalScrollBar(ScrollBar(Qt.Orientation.Horizontal, self))
        self.setVerticalScrollBar(ScrollBar(Qt.Orientation.Vertical, self))
    
    def paintEvent(self, e):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self.viewport())
        painter.setOpacity(self.property("Opacity"))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getBorderColour(is_highlight=self.hasFocus() or self.underMouse()))
        painter.setBrush(getBackgroundColour(is_highlight=self.hasFocus()))
        rect = self.viewport().rect()
        rect.setWidth(rect.width() - rect.x() - 1)
        rect.setHeight(rect.height() - rect.y() - 1)
        rect.setX(1)
        rect.setY(1)
        painter.drawRoundedRect(rect, 10, 10)
        op = QStyleOptionHeader()
        op.initFrom(self)
        self.initStyleOption(op)
        op.palette.setColor(op.palette.ColorRole.Text, getForegroundColour())
        self.style().drawControl(QStyle.ControlElement.CE_Header, op, painter, self)
        self.setStyleSheet(
            f"color: rgba({str(getForegroundColour(is_tuple=True)).replace('(', '').replace(')', '')}, {str(painter.opacity())}); background: transparent; border: none;")
        super().paintEvent(e)
    
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


class TableView(QTableView):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.installEventFilter(ToolTip(self))
        self.installEventFilter(self)
        self.setProperty("Opacity", 0.6)
        self.setVerticalHeader(HeaderView(Qt.Orientation.Vertical, self))
        self.setHorizontalHeader(HeaderView(Qt.Orientation.Horizontal, self))
        self.setItemDelegate(ItemDelegate(self))
        self.setShowGrid(False)
        self.setHorizontalScrollBar(ScrollBar(Qt.Orientation.Horizontal, self))
        self.setVerticalScrollBar(ScrollBar(Qt.Orientation.Vertical, self))
    
    def paintEvent(self, e):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self.viewport())
        painter.setOpacity(self.property("Opacity"))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(
            getBorderColour(
                is_highlight=(self.viewport().underMouse() or self.viewport().hasFocus()) and self.isEnabled()))
        painter.setBrush(getBackgroundColour(
            is_highlight=self.viewport().hasFocus() and self.isEnabled()))
        rect = self.viewport().rect()
        rect.setWidth(rect.width() - rect.x() - 1)
        rect.setHeight(rect.height() - rect.y() - 1)
        rect.setX(1)
        rect.setY(1)
        painter.drawRoundedRect(rect, 10, 10)
        self.setShowGrid(False)
        op = QStyleOptionFrame()
        op.initFrom(self)
        self.initStyleOption(op)
        self.setStyleSheet(
            f"color: rgba({str(getForegroundColour(is_tuple=True)).replace('(', '').replace(')', '')}, {str(painter.opacity())}); background: transparent; border: none;")
        super().paintEvent(e)
    
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


class TableWidget(QTableWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.installEventFilter(ToolTip(self))
        self.installEventFilter(self)
        self.setProperty("Opacity", 0.6)
        self.setVerticalHeader(HeaderView(Qt.Orientation.Vertical, self))
        self.setHorizontalHeader(HeaderView(Qt.Orientation.Horizontal, self))
        self.setItemDelegate(ItemDelegate(self))
        self.setShowGrid(False)
        self.setHorizontalScrollBar(ScrollBar(Qt.Orientation.Horizontal, self))
        self.setVerticalScrollBar(ScrollBar(Qt.Orientation.Vertical, self))
    
    def paintEvent(self, e):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self.viewport())
        painter.setOpacity(self.property("Opacity"))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(
            getBorderColour(
                is_highlight=(self.viewport().underMouse() or self.viewport().hasFocus()) and self.isEnabled()))
        painter.setBrush(getBackgroundColour(
            is_highlight=self.viewport().hasFocus() and self.isEnabled()))
        rect = self.viewport().rect()
        rect.setWidth(rect.width() - rect.x() - 1)
        rect.setHeight(rect.height() - rect.y() - 1)
        rect.setX(1)
        rect.setY(1)
        painter.drawRoundedRect(rect, 10, 10)
        self.setShowGrid(False)
        op = QStyleOptionFrame()
        op.initFrom(self)
        self.initStyleOption(op)
        self.setStyleSheet(
            f"color: rgba({str(getForegroundColour(is_tuple=True)).replace('(', '').replace(')', '')}, {str(painter.opacity())}); background: transparent; border: none;")
        super().paintEvent(e)
    
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
