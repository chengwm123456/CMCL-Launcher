# -*- coding: utf-8 -*-
from typing import overload

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from ..ThemeController import *
from .Button import CloseButton
from .Panel import Panel


class TipBase(Panel):
    windowClosed = pyqtSignal()
    
    @overload
    def __init__(self, parent=None):
        ...
    
    @overload
    def __init__(self, parent=None, close_enabled=True):
        ...
    
    def __init__(self, *__args):
        super().__init__(__args[0])
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setProperty("closeEnabled", __args[1] if len(__args) > 1 else True)
        self._closeButton = CloseButton(self)
        self._closeButton.setVisible(self.closeEnabled())
        self._closeButton.move(QPoint(self.width() - self._closeButton.width() - 16, 16))
        if self.closeEnabled():
            self.setMinimumWidth(64)
            self.setFixedHeight(64)
        else:
            self.setMinimumWidth(0)
            self.setMinimumHeight(0)
        self._closeButton.pressed.connect(self.close)
    
    def closeEnabled(self):
        return self.property("closeEnabled")
    
    def setCloseEnabled(self, value):
        if value in [True, False, 1, 0]:
            self.setProperty("closeEnabled", value)
        else:
            raise TypeError(f"'{type(value)}' object cannot be interpreted as a bool.")
        self._closeButton.setVisible(self.closeEnabled())
    
    def resizeEvent(self, a0):
        self._closeButton.move(QPoint(self.width() - self._closeButton.width() - 16, 16))
        super().resizeEvent(a0)
        self._closeButton.move(QPoint(self.width() - self._closeButton.width() - 16, 16))
    
    def closeEvent(self, a0):
        super().closeEvent(a0)
        self.windowClosed.emit()


class Tip(TipBase):
    @overload
    def __init__(self, parent=None):
        ...
    
    @overload
    def __init__(self, parent=None, close_enabled=True):
        ...
    
    @overload
    def __init__(self, parent=None, close_enabled=True, central_widget=None):
        ...
    
    def __init__(self, *args):
        super().__init__(*args[:2])
        self.setProperty("centralWidget", args[3] if len(args) > 2 else None)
    
    def centralWidget(self):
        return self.property("centralWidget")
    
    def setCentralWidget(self, widget):
        if isinstance(widget, QWidget):
            self.setProperty("centralWidget", widget)
            self.resize(widget.width() + 10 + ((32 if self.closeEnabled() else 0) + 5),
                        widget.height() + 10)
    
    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        if hasattr(self.centralWidget(), "setGeometry"):
            self.centralWidget().setGeometry(5, 5, self.width() - (
                (self._closeButton.width() - 32) if self._closeButton.isVisible() else 0), self.height() - 10)


class PopupTip(Tip):
    class PopupPosition(Enum):
        LEFT = "left"
        RIGHT = "right"
    
    def tip(self, position=PopupPosition.RIGHT, duration=-1):
        if duration >= 0:
            QTimer.singleShot(duration + 1000, self.hide)
        self.show()
        pos = QPoint(self.parent().width(), 0)
        start_pos = QPoint(self.parent().width(), 0)
        match position:
            case self.PopupPosition.LEFT:
                pos = QPoint(0, 0)
                start_pos = QPoint(-self.width(), 0)
            case self.PopupPosition.RIGHT:
                pos = QPoint(self.parent().width() - self.width(), 0)
                start_pos = QPoint(self.parent().width() + self.width(), 0)
        
        animation = QPropertyAnimation(self, b"pos", self)
        animation.setDuration(1000)
        animation.setStartValue(start_pos)
        animation.setEndValue(pos)
        animation.setEasingCurve(QEasingCurve.Type.OutQuint)
        animation.start()
