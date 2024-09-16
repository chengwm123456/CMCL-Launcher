# -*- coding: utf-8 -*-
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from .CWMThemeControl import *


class ToolTipBase(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.setStyleSheet(
            f"background: transparent; color: {str(getForegroundColour(tuple=True)).replace('(', '').replace(')', '')}")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        dsg = QGraphicsDropShadowEffect(self)
        dsg.setBlurRadius(32)
        dsg.setColor(QColor(0, 0, 0, 60))
        dsg.setOffset(QPointF(0, 5))
        self.setGraphicsEffect(dsg)
        self.setContentsMargins(5, 5, 5, 5)
        self.hide()
    
    def paintEvent(self, a0):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.adjustSize()
        self.raise_()
        painter = QPainter(self)
        painter.setOpacity(1.0)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getBorderColour())
        painter.setBrush(getBackgroundColour())
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)
        self.setStyleSheet(
            f"background: transparent; color: rgba({str(getForegroundColour(tuple=True)).replace('(', '').replace(')', '')}, {painter.opacity()});")
        super().paintEvent(a0)


class ToolTip(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.__tooltip = ToolTipBase(self.parent().parent())
        self.__tooltip.setText(parent.toolTip())
        self.__tooltip.adjustSize()
        pos = parent.mapTo(parent.parent(), QPoint(0, 0))
        x = (
                pos.x() + parent.width()) if pos.x() + parent.width() + self.__tooltip.width() <= parent.parent().width() else (
                pos.x() - self.__tooltip.width())
        y = pos.y() - 5 - self.__tooltip.height()
        x = min(max(5, x), parent.parent().width() - self.__tooltip.width() - 5)
        y = min(max(5, y), parent.parent().height() - self.__tooltip.height() - 5)
        self.__tooltip.move(x, y)
    
    def eventFilter(self, a0, a1):
        if a0.toolTip():
            match a1.type():
                case QEvent.Type.ToolTip:
                    self.__tooltip.setText(a0.toolTip())
                    self.__tooltip.adjustSize()
                    pos = a0.mapTo(a0.parent(), QPoint(0, 0))
                    x = (
                            pos.x() + a0.width()) if pos.x() + a0.width() + self.__tooltip.width() <= a0.parent().width() else (
                            pos.x() - self.__tooltip.width())
                    y = pos.y() - 5 - self.__tooltip.height()
                    x = min(max(5, x), a0.parent().width() - self.__tooltip.width() - 5)
                    y = min(max(5, y), a0.parent().height() - self.__tooltip.height() - 5)
                    self.__tooltip.move(x, y)
                    self.__tooltip.show()
                    if a0.toolTipDuration() > 0:
                        QTimer.singleShot(a0.toolTipDuration(), self.__tooltip.hide)
                    return True
                case QEvent.Type.ToolTipChange:
                    self.__tooltip.setText(a0.toolTip())
                case QEvent.Type.Leave:
                    if not self.__tooltip.underMouse():
                        self.__tooltip.hide()
        return super().eventFilter(a0, a1)
