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
    
    def paintEvent(self, a0):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self)
        painter.setOpacity(1.0 if self.hasFocus() or self.underMouse() else 0.6)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getBorderColour(highlight=self.hasFocus() or self.underMouse()))
        painter.setBrush(getBackgroundColour(highlight=self.hasFocus()))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)
        self.setStyleSheet(
            f"color: rgba({str(getForegroundColour(tuple=True)).replace('(', '').replace(')', '')}, {str(painter.opacity())}); background: transparent; border: none; padding: 5px;")
        super().paintEvent(a0)
    
    def setEnabled(self, a0):
        super().setEnabled(a0)
        if a0:
            self.setGraphicsEffect(None)
        else:
            og = QGraphicsOpacityEffect()
            og.setOpacity(0.3)
            self.setGraphicsEffect(og)
    
    def contextMenuEvent(self, e):
        menu = RoundedMenu(self)
        if not self.isReadOnly():
            undo = QAction()
            undo.setText("Undo")
            undo.setEnabled(self.isUndoAvailable())
            undo.triggered.connect(self.undo)
            undo.setShortcut("Ctrl+Z")
            menu.addAction(undo)
            redo = QAction()
            redo.setText("Redo")
            redo.setEnabled(self.isRedoAvailable())
            redo.triggered.connect(self.redo)
            redo.setShortcut("Ctrl+Y")
            menu.addAction(redo)
            menu.addSeparator()
            cut = QAction()
            cut.setText("Cut")
            cut.triggered.connect(self.cut)
            cut.setShortcut("Ctrl+X")
            menu.addAction(cut)
        copy = QAction()
        copy.setText("Copy")
        copy.triggered.connect(self.copy)
        copy.setShortcut("Ctrl+C")
        menu.addAction(copy)
        if not self.isReadOnly():
            paste = QAction()
            paste.setText("Paste")
            paste.triggered.connect(self.paste)
            paste.setShortcut("Ctrl+V")
            menu.addAction(paste)
            delete = QAction()
            delete.setText("Delete")
            delete.triggered.connect(
                lambda: self.setText(self.text()[:self.cursorPosition() - 1] + self.text()[self.cursorPosition():]))
            menu.addAction(delete)
        menu.addSeparator()
        select_all = QAction()
        select_all.setText("Select All")
        select_all.triggered.connect(self.selectAll)
        select_all.setShortcut("Ctrl+A")
        menu.addAction(select_all)
        menu.exec(self.mapToGlobal(e.pos()))
