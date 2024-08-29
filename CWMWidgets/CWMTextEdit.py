# -*- coding: utf-8 -*-
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from .CWMWindows import RoundedMenu
from .CWMThemeControl import *
from .CWMToolTip import ToolTip


class TextEdit(QTextEdit):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.installEventFilter(ToolTip(self))
    
    def paintEvent(self, e):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self.viewport())
        painter.setOpacity(1.0 if self.hasFocus() or self.underMouse() else 0.6)
        if not self.isEnabled():
            painter.setOpacity(0.3)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getBorderColour(highlight=self.hasFocus() or self.underMouse()))
        painter.setBrush(getBackgroundColour(highlight=self.hasFocus()))
        rect = self.contentsRect()
        rect.setWidth(rect.width() - rect.x() - 1)
        rect.setHeight(rect.height() - rect.y() - 1)
        rect.setX(1)
        rect.setY(1)
        painter.drawRoundedRect(rect, 10, 10)
        self.setStyleSheet(
            f"color: rgba({str(getForegroundColour(tuple=True)).replace('(', '').replace(')', '')}, {str(painter.opacity())}); background: transparent; border: none; padding: 5px;")
        op = QStyleOptionFrame()
        op.initFrom(self)
        self.initStyleOption(op)
        super().paintEvent(e)
    
    def contextMenuEvent(self, e):
        menu = RoundedMenu(self)
        if not self.isReadOnly():
            undo = QAction()
            undo.setText("Undo")
            undo.setEnabled(self.isUndoRedoEnabled())
            undo.triggered.connect(self.undo)
            undo.setShortcut("Ctrl+Z")
            menu.addAction(undo)
            redo = QAction()
            redo.setText("Redo")
            redo.setEnabled(self.isUndoRedoEnabled())
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
            delete.triggered.connect(self.textCursor().deleteChar)
            menu.addAction(delete)
        menu.addSeparator()
        select_all = QAction()
        select_all.setText("Select All")
        select_all.triggered.connect(self.selectAll)
        select_all.setShortcut("Ctrl+A")
        menu.addAction(select_all)
        menu.exec(self.mapToGlobal(e.pos()))


class PlainTextEdit(QPlainTextEdit):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
    
    def paintEvent(self, e):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self.viewport())
        painter.setOpacity(1.0 if self.hasFocus() or self.underMouse() else 0.6)
        if not self.isEnabled():
            painter.setOpacity(0.3)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getBorderColour(highlight=self.hasFocus() or self.underMouse()))
        painter.setBrush(getBackgroundColour(highlight=self.hasFocus()))
        rect = self.contentsRect()
        rect.setWidth(rect.width() - rect.x() - 1)
        rect.setHeight(rect.height() - rect.y() - 1)
        rect.setX(1)
        rect.setY(1)
        painter.drawRoundedRect(rect, 10, 10)
        self.setStyleSheet(
            f"color: rgba({str(getForegroundColour(tuple=True)).replace('(', '').replace(')', '')}, {str(painter.opacity())}); background: transparent; border: none; padding: 5px;")
        op = QStyleOptionFrame()
        op.initFrom(self)
        self.initStyleOption(op)
        super().paintEvent(e)
    
    def contextMenuEvent(self, e):
        menu = RoundedMenu(self)
        if not self.isReadOnly():
            undo = QAction()
            undo.setText("Undo")
            undo.setEnabled(self.isUndoRedoEnabled())
            undo.triggered.connect(self.undo)
            undo.setShortcut("Ctrl+Z")
            menu.addAction(undo)
            redo = QAction()
            redo.setText("Redo")
            redo.setEnabled(self.isUndoRedoEnabled())
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
            delete.triggered.connect(self.textCursor().deleteChar)
            menu.addAction(delete)
        menu.addSeparator()
        select_all = QAction()
        select_all.setText("Select All")
        select_all.triggered.connect(self.selectAll)
        select_all.setShortcut("Ctrl+A")
        menu.addAction(select_all)
        menu.exec(self.mapToGlobal(e.pos()))
