# -*- coding: utf-8 -*-
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from ..ThemeController.ThemeControl import *


class ToolTipLabel(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.setStyleSheet(
            f"background: transparent; color: {str(getForegroundColour(is_tuple=True)).strip('()')}")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setContentsMargins(5, 5, 5, 5)
        self.show()

    def paintEvent(self, a0):
        self.setStyleSheet("padding: 3px;")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self)
        painter.setOpacity(1.0)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getBorderColour())
        painter.setBrush(getBackgroundColour())
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)
        self.setStyleSheet(
            f"background: transparent; color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {painter.opacity()});")
        super().paintEvent(a0)


class ToolTipWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setStyleSheet(f"background: transparent;")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setWindowFlag(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.label = ToolTipLabel(self)
        shadow = QGraphicsDropShadowEffect(self.label)
        shadow.setBlurRadius(32)
        shadow.setColor(QColor(0, 0, 0, 128))
        shadow.setOffset(QPointF(5, 5))
        self.label.setGraphicsEffect(shadow)
        self.hide()

    def paintEvent(self, a0):
        self.label.adjustSize()
        self.resize(self.label.graphicsEffect().boundingRect().size().toSize())

    def setText(self, text):
        self.label.setText(text)

    def setFont(self, a0):
        super().setFont(a0)
        self.label.setFont(a0)


class ToolTip(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.__tooltip = ToolTipWidget(self.parent().parent())
        self.__tooltip.setText(self.parent().toolTip())
        self.__tooltip.adjustSize()
        x = self.parent().mapToGlobal(QPoint(0, self.parent().height())).x()
        y = self.parent().mapToGlobal(QPoint(0, self.parent().height())).y()
        self.__tooltip.move(x, y)
        self.__tooltip.raise_()

    def event(self, a0):
        self.hide()
        return super().event(a0)

    def eventFilter(self, a0, a1):
        match a1.type():
            case QEvent.Type.ToolTip:
                if a0.toolTip():
                    if not self.__tooltip.isVisible():
                        self.__tooltip.setText(a0.toolTip())
                        self.__tooltip.adjustSize()
                        x = a0.mapToGlobal(QPoint(0, a0.height())).x()
                        y = a0.mapToGlobal(QPoint(0, a0.height())).y()
                        self.__tooltip.move(x, y)
                        self.__tooltip.raise_()
                        self.__tooltip.show()
                        if a0.toolTipDuration() > 0:
                            QTimer.singleShot(a0.toolTipDuration(), self.__tooltip.hide)
                return True
            case QEvent.Type.Leave:
                self.__tooltip.hide()
            case QEvent.Type.Hide:
                self.__tooltip.hide()
            case QEvent.Type.ToolTipChange:
                self.__tooltip.setText(a0.toolTip())
            case QEvent.Type.FontChange:
                self.__tooltip.setFont(a0.font())
            case QEvent.Type.ParentChange:
                self.__tooltip.setParent(a0.parent())
        return super().eventFilter(a0, a1)
