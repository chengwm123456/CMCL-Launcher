# -*- coding: utf-8 -*-
from typing import overload

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from .CWMThemeControl import *
from .CWMWindows import RoundedMenu
from .CWMToolTip import ToolTip


class LabelBase(QLabel):
    @overload
    def __init__(self, parent=None):
        ...
    
    @overload
    def __init__(self, text="", parent=None):
        ...
    
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setStyleSheet(
            f"background: transparent; color: rgba({str(getForegroundColour(tuple=True)).replace('(', '').replace(')', '')}, {1.0 if self.underMouse() else 0.6 if self.isEnabled() else 0.3})")
        self.installEventFilter(ToolTip(self))
    
    def paintEvent(self, a0):
        self.setStyleSheet(
            f"background: transparent; color: rgba({str(getForegroundColour(tuple=True)).replace('(', '').replace(')', '')}, {1.0 if self.underMouse() else 0.6 if self.isEnabled() else 0.3})")
        super().paintEvent(a0)
    
    def contextMenuEvent(self, e):
        if self.textInteractionFlags():
            menu = RoundedMenu(self)
            if self.textInteractionFlags() & Qt.TextInteractionFlag.TextEditable:
                undo = QAction()
                undo.setText("Undo")
                # undo.setEnabled(self.isUndoRedoEnabled())
                # undo.triggered.connect(self.undo)
                undo.setShortcut("Ctrl+Z")
                menu.addAction(undo)
                redo = QAction()
                redo.setText("Redo")
                # redo.setEnabled(self.isUndoRedoEnabled())
                # redo.triggered.connect(self.redo)
                redo.setShortcut("Ctrl+Y")
                menu.addAction(redo)
                menu.addSeparator()
                cut = QAction()
                cut.setText("Cut")
                # cut.triggered.connect(self.cut)
                cut.setShortcut("Ctrl+X")
                menu.addAction(cut)
            copy = QAction()
            copy.setText("Copy")
            # copy.triggered.connect(self.copy)
            # QApplication.clipboard().setText(self.selectedText())
            copy.setShortcut("Ctrl+C")
            menu.addAction(copy)
            if self.textInteractionFlags() & Qt.TextInteractionFlag.TextEditable:
                paste = QAction()
                paste.setText("Paste")
                # paste.triggered.connect(self.paste)
                paste.setShortcut("Ctrl+V")
                menu.addAction(paste)
                delete = QAction()
                delete.setText("Delete")
                # delete.triggered.connect(self.textCursor().deleteChar)
                menu.addAction(delete)
            menu.addSeparator()
            select_all = QAction()
            select_all.setText("Select All")
            # select_all.triggered.connect(self.selectAll)
            select_all.setShortcut("Ctrl+A")
            menu.addAction(select_all)
            menu.exec(self.mapToGlobal(e.pos()))


class Label(LabelBase):
    pass


class StrongLabel(LabelBase):
    pass


class TitleLabel(LabelBase):
    pass
