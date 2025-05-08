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
        borderColour = getBorderColour()
        backgroundColour = getBackgroundColour()
        borderGradient = QRadialGradient(QPointF(self.mapFromGlobal(QCursor.pos())),
                                         max(self.width(), self.height()))
        borderGradient.setColorAt(0.0, borderColour)
        borderGradient.setColorAt(1.0, Colour(*borderColour, 32))
        painter.setPen(QPen(QBrush(borderGradient), 1))
        backgroundGradient = QLinearGradient(QPointF(0, 0), QPointF(0, self.height()))
        backgroundGradient.setColorAt(0.0, backgroundColour)
        backgroundGradient.setColorAt(1.0, Colour(*backgroundColour, 210))
        painter.setBrush(QBrush(backgroundGradient))
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
    
    def hideEvent(self, a0):
        super().hideEvent(a0)
        self.deleteLater()


class ToolTip(QObject):
    def __init__(self, parent):
        super().__init__(parent)
        self.__tooltip = None
    
    def eventFilter(self, a0, a1):
        match a1.type():
            case QEvent.Type.ToolTip:
                if a0.toolTip():
                    if not self.__tooltip:
                        self.__tooltip = ToolTipWidget(self.parent().parent())
                        self.__tooltip.setText(a0.toolTip())
                        self.__tooltip.adjustSize()
                        self.__tooltip.raise_()
                        self.__tooltip.show()
                        if a0.toolTipDuration() > 0:
                            QTimer.singleShot(a0.toolTipDuration(), self.closeTooltip)
                        maxWidth, maxHeight = (QGuiApplication.primaryScreen().geometry().width(),
                                               QGuiApplication.primaryScreen().geometry().height())
                        self.__tooltip.move(QCursor.pos())
                        if self.__tooltip.y() + self.__tooltip.height() > maxHeight:
                            self.__tooltip.move(self.__tooltip.x(), self.__tooltip.y() - self.__tooltip.height())
                        if self.__tooltip.x() + self.__tooltip.width() > maxWidth:
                            self.__tooltip.move(self.__tooltip.x() - self.__tooltip.width(), self.__tooltip.y())
                return True
            case QEvent.Type.Leave:
                self.closeTooltip()
            case QEvent.Type.Hide:
                self.closeTooltip()
            case QEvent.Type.ToolTipChange:
                if self.__tooltip:
                    self.__tooltip.setText(a0.toolTip())
            case QEvent.Type.FontChange:
                if self.__tooltip:
                    self.__tooltip.setFont(a0.font())
            case QEvent.Type.ParentChange:
                if self.__tooltip:
                    self.__tooltip.setParent(a0.parent())
        return super().eventFilter(a0, a1)
    
    def closeTooltip(self):
        if self.__tooltip:
            self.__tooltip.hide()
        self.__tooltip = None
