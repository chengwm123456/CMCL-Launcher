# -*- coding: utf-8 -*-
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from .CWMThemeControl import *
from .CWMButton import CloseButton
from .CWMPanel import Panel


class TipBase(Panel):
    windowClosed = pyqtSignal()
    
    def __init__(self, parent, close_enabled=True):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedHeight(64)
        self.closeEnabled = lambda: close_enabled
        self._closeButton = CloseButton(self)
        self._closeButton.setVisible(self.closeEnabled())
        self._closeButton.move(QPoint(self.width() - self._closeButton.width() - 16, 16))
        self._closeButton.pressed.connect(self.close)
    
    def setCloseEnabled(self, value):
        if value in [True, False, 1, 0]:
            self.closeEnabled = lambda: value
        else:
            raise TypeError(f"'{type(value)}' object cannot be interpreted as a bool.")
        self._closeButton.setVisible(self.closeEnabled())
    
    def paintEvent(self, a0):
        opacity = 1.0 if self.hasFocus() or self.underMouse() else 0.6
        if not self.isEnabled():
            opacity = 0.3
        self.setStyleSheet(
            f"background: transparent; color: rgba({str(getForegroundColour(tuple=True)).replace('(', '').replace(')', '')}, {opacity});")
        super().paintEvent(a0)
    
    def resizeEvent(self, a0):
        self._closeButton.move(QPoint(self.width() - self._closeButton.width() - 16, 16))
        super().resizeEvent(a0)
        self._closeButton.move(QPoint(self.width() - self._closeButton.width() - 16, 16))
    
    def closeEvent(self, a0):
        super().closeEvent(a0)
        self.windowClosed.emit()


class Tip(TipBase):
    def __init__(self, parent, close_enabled=True):
        super().__init__(parent, close_enabled)
        self.centralWidget = lambda: None
    
    def setCentralWidget(self, widget):
        if isinstance(widget, QWidget):
            self.centralWidget = lambda: widget
    
    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        if hasattr(self.centralWidget(), "setGeometry"):
            self.centralWidget().setGeometry(5, 5, self.width() - self._closeButton.width() - 32, self.height() - 10)


class PopupTip(Tip):
    class PopupPosition(Enum):
        LEFT = "left"
        RIGHT = "right"
    
    def tip(self, position=PopupPosition.RIGHT):
        self.show()
        point_size = QPoint(self.width(), self.height())
        pos = QPoint(self.parent().width(), 0)
        match position:
            case self.PopupPosition.LEFT:
                pos = QPoint(0, 0)
            case self.PopupPosition.RIGHT:
                pos = QPoint(self.parent().width(), 0)
        animation = QPropertyAnimation(self, b"geometry")
        animation.setDuration(1000)
        animation.setStartValue(
            QRect(QPoint(self.parent().width() - self.width(), 0), QPoint(self.width(), self.height())))
        animation.setEndValue(QRect(pos, point_size))
        animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        animation.start()
