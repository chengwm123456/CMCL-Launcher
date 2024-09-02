# -*- coding: utf-8 -*-
from .CWMToolTip import ToolTip
from .CWMWindows import RoundedMenu
from .CWMThemeControl import *


class LineEdit(QLineEdit):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.installEventFilter(ToolTip(self))
        self.installEventFilter(self)
    
    def paintEvent(self, a0):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self)
        painter.setOpacity(1.0 if self.hasFocus() or self.underMouse() else 0.6)
        if not self.isEnabled():
            painter.setOpacity(0.3)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getBorderColour(highlight=self.hasFocus() or self.underMouse()))
        painter.setBrush(getBackgroundColour(highlight=self.hasFocus()))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)
        self.setStyleSheet(
            f"color: rgba({str(getForegroundColour(tuple=True)).replace('(', '').replace(')', '')}, {str(painter.opacity())}); background: transparent; border: none; padding: 5px;")
        op = QStyleOptionFrame()
        op.initFrom(self)
        self.initStyleOption(op)
        super().paintEvent(a0)
    
    def contextMenuEvent(self, e):
        default = self.createStandardContextMenu()
        menu = RoundedMenu(self)
        for i in default.actions():
            menu.addAction(i)
        menu.exec(self.mapToGlobal(e.pos()))
    
    def eventFilter(self, a0, a1):
        if a1.type() != QEvent.Type.KeyPress:
            return super().eventFilter(a0, a1)
        
        if self.completer():
            for i in self.children():
                if isinstance(i, RoundedMenu):
                    i.deleteLater()
            if self.hasFocus():
                menu = RoundedMenu(self)
                menu.popup(self.mapToGlobal(QPoint(self.cursorRect().x(), self.height())))
                self.setFocus()
                return self.completer().eventFilter(a0, a1)
        return super().eventFilter(a0, a1)
