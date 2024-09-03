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
        self.setStyleSheet(
            f"background: transparent; color: rgb({str(getForegroundColour(tuple=True)).replace('(', '').replace(')', '')});")
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getBorderColour())
        painter.setBrush(getBackgroundColour())
        painter.drawRoundedRect(self.rect(), 10, 10)
        super().paintEvent(a0)


class ToolTip(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.__tooltip = ToolTipBase(self.parent().parent())
        self.__tooltip.hide()
    
    def eventFilter(self, a0, a1):
        if a0.toolTip():
            if a1.type() == QEvent.Type.Enter:
                self.__tooltip.setText(a0.toolTip())
                pos = a0.mapTo(a0.parent(), QPoint(0, 0))
                x = pos.x() + a0.parent().width() // 2 - self.__tooltip.width() // 2
                y = pos.y() - 5 - self.__tooltip.height()
                x = min(max(5, x), a0.parent().width() - self.__tooltip.width() - 5)
                y = min(max(5, y), a0.parent().height() - self.__tooltip.height() - 5)
                self.__tooltip.move(x, y)
                self.__tooltip.show()
                if a0.toolTipDuration() >= 0:
                    t = QTimer(self.__tooltip)
                    t.setInterval(a0.toolTipDuration())
                    t.setSingleShot(True)
                    t.timeout.connect(self.__tooltip.hide)
                    t.start()
            if a1.type() == QEvent.Type.Leave:
                if not self.__tooltip.underMouse():
                    self.__tooltip.hide()
            if a1.type() == QEvent.Type.ToolTip:
                return True
        return super().eventFilter(a0, a1)
