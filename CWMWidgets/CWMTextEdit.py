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
        self.setStyleSheet(f"""TextEdit{{
    background: rgba({str(getBackgroundColour(tuple=True)).replace('(', '').replace(')', '')}, 0.6);
    color: rgba({str(getForegroundColour(tuple=True)).replace('(', '').replace(')', '')}, 0.6);
    border: 1px solid rgba({str(getBorderColour(tuple=True)).replace('(', '').replace(')', '')}, 0.6);
    padding: 5px;
    border-radius: 10px;
}}
TextEdit:focus, TextEdit:hover{{
    border: 1px solid rgb({str(getBorderColour(highlight=True, tuple=True)).replace('(', '').replace(')', '')});
    color: rgb({str(getForegroundColour(tuple=True)).replace('(', '').replace(')', '')});
}}
TextEdit:hover{{
    background: rgb({str(getBackgroundColour(tuple=True)).replace('(', '').replace(')', '')});
}}
TextEdit:focus{{
    background: rgb({str(getBackgroundColour(highlight=True, tuple=True)).replace('(', '').replace(')', '')});
}}
        """)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.installEventFilter(ToolTip(self))
    
    def paintEvent(self, e):
        self.setStyleSheet(f"""TextEdit{{
            background: rgba({str(getBackgroundColour(tuple=True)).replace('(', '').replace(')', '')}, 0.6);
            color: rgba({str(getForegroundColour(tuple=True)).replace('(', '').replace(')', '')}, 0.6);
            border: 1px solid rgba({str(getBorderColour(tuple=True)).replace('(', '').replace(')', '')}, 0.6);
            padding: 5px;
            border-radius: 10px;
        }}
        TextEdit:focus, TextEdit:hover{{
            border: 1px solid rgb({str(getBorderColour(highlight=True, tuple=True)).replace('(', '').replace(')', '')});
            color: rgb({str(getForegroundColour(tuple=True)).replace('(', '').replace(')', '')});
        }}
        TextEdit:hover{{
            background: rgb({str(getBackgroundColour(tuple=True)).replace('(', '').replace(')', '')});
        }}
        TextEdit:focus{{
            background: rgb({str(getBackgroundColour(highlight=True, tuple=True)).replace('(', '').replace(')', '')});
        }}
        """)
        palette = self.palette()
        colour = getForegroundColour()
        colour.setAlpha(128)
        palette.setColor(self.backgroundRole(), colour)
        self.setPalette(palette)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        super().paintEvent(e)
    
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
    
    # def paintEvent(self, a0):
    #     self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    #     self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
    #     self.setStyleSheet(
    #         f"background: transparent; color: rgba(0, 0, 0, {1.0 if self.underMouse() or self.hasFocus() else 0.5}); border: none; margin: 5px;")
    #     painter = QPainter(self)
    #     painter.setOpacity(1.0 if self.underMouse() or self.hasFocus() else 0.5)
    #     painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    #     painter.setPen(
    #         QColor(150, 150, 255) if self.hasFocus() else QColor(230, 230, 230))
    #     painter.setBrush(QColor(173, 173, 255) if self.hasFocus() else QColor(253, 253, 253))
    #     painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)
    #     super().paintEvent(a0)


class PlainTextEdit(QPlainTextEdit):
    def __init__(self, parent):
        super().__init__(parent)
        self.setStyleSheet(f"""PlainTextEdit{{
    background: rgba({str(getBackgroundColour(tuple=True)).replace('(', '').replace(')', '')}, 0.6);
    color: rgba({str(getForegroundColour(tuple=True)).replace('(', '').replace(')', '')}, 0.6);
    border: 1px solid rgba({str(getBorderColour(tuple=True)).replace('(', '').replace(')', '')}, 0.6);
    padding: 5px;
    border-radius: 10px;
}}
PlainTextEdit:focus, PlainTextEdit:hover{{
    border: 1px solid rgb({str(getBorderColour(highlight=True, tuple=True)).replace('(', '').replace(')', '')});
    color: rgb({str(getForegroundColour(tuple=True)).replace('(', '').replace(')', '')});
}}
PlainTextEdit:hover{{
    background: rgb({str(getBackgroundColour(tuple=True)).replace('(', '').replace(')', '')});
}}
PlainTextEdit:focus{{
    background: rgb({str(getBackgroundColour(highlight=True, tuple=True)).replace('(', '').replace(')', '')});
}}
        """)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
    
    def paintEvent(self, e):
        self.setStyleSheet(f"""PlainTextEdit{{
            background: rgba({str(getBackgroundColour(tuple=True)).replace('(', '').replace(')', '')}, 0.6);
            color: rgba({str(getForegroundColour(tuple=True)).replace('(', '').replace(')', '')}, 0.6);
            border: 1px solid rgba({str(getBorderColour(tuple=True)).replace('(', '').replace(')', '')}, 0.6);
            padding: 5px;
            border-radius: 10px;
        }}
        PlainTextEdit:focus, PlainTextEdit:hover{{
            border: 1px solid rgb({str(getBorderColour(highlight=True, tuple=True)).replace('(', '').replace(')', '')});
            color: rgb({str(getForegroundColour(tuple=True)).replace('(', '').replace(')', '')});
        }}
        PlainTextEdit:hover{{
            background: rgb({str(getBackgroundColour(tuple=True)).replace('(', '').replace(')', '')});
        }}
        PlainTextEdit:focus{{
            background: rgb({str(getBackgroundColour(highlight=True, tuple=True)).replace('(', '').replace(')', '')});
        }}
        """)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        super().paintEvent(e)
    
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
    
    # def paintEvent(self, a0):
    #     self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    #     self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
    #     self.setStyleSheet(
    #         f"background: transparent; color: rgba(0, 0, 0, {1.0 if self.underMouse() or self.hasFocus() else 0.5}); border: none; margin: 5px;")
    #     painter = QPainter(self)
    #     painter.setOpacity(1.0 if self.underMouse() or self.hasFocus() else 0.5)
    #     painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    #     painter.setPen(
    #         QColor(150, 150, 255) if self.hasFocus() else QColor(230, 230, 230))
    #     painter.setBrush(QColor(173, 173, 255) if self.hasFocus() else QColor(253, 253, 253))
    #     painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)
    #     super().paintEvent(a0)
