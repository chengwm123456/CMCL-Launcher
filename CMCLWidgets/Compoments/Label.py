# -*- coding: utf-8 -*-
from typing import overload

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from ..ThemeManager import *
from CMCLWidgets.Windows import RoundedMenu
from CMCLWidgets.ToolTip import ToolTip


class LabelBase(QLabel):
    @overload
    def __init__(self, parent=None):
        ...
    
    @overload
    def __init__(self, text="", parent=None):
        ...
    
    def __init__(self, *__args):
        super().__init__(*__args)
        self.installEventFilter(ToolTip(self))
        self.installEventFilter(self)
        self.setProperty("Opacity", 0.6)
        self.setStyleSheet(
            f"background: transparent; color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {self.property('Opacity')})")
    
    def paintEvent(self, a0):
        self.setStyleSheet(
            f"background: transparent; color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {self.property('Opacity')})")
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
    
    def eventFilter(self, a0, a1):
        if self != a0:
            return super().eventFilter(a0, a1)
        match a1.type():
            case QEvent.Type.MouseButtonPress:
                if self.isEnabled():
                    ani = QPropertyAnimation(self, b"Opacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("Opacity"))
                    ani.setEndValue(1.0)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.finished.connect(ani.deleteLater)
                    ani.start()
                else:
                    ani = QPropertyAnimation(self, b"Opacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("Opacity"))
                    ani.setEndValue(0.3)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.finished.connect(ani.deleteLater)
                    ani.start()
            case QEvent.Type.MouseMove:
                if self.isEnabled():
                    ani = QPropertyAnimation(self, b"Opacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("Opacity"))
                    ani.setEndValue(1.0)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.finished.connect(ani.deleteLater)
                    ani.start()
                else:
                    ani = QPropertyAnimation(self, b"Opacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("Opacity"))
                    ani.setEndValue(0.3)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.finished.connect(ani.deleteLater)
                    ani.start()
            case QEvent.Type.Enter:
                if self.isEnabled():
                    if not self.hasFocus():
                        ani = QPropertyAnimation(self, b"Opacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("Opacity"))
                        ani.setEndValue(1.0)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.finished.connect(ani.deleteLater)
                        ani.start()
                else:
                    ani = QPropertyAnimation(self, b"Opacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("Opacity"))
                    ani.setEndValue(0.3)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.finished.connect(ani.deleteLater)
                    ani.start()
            case QEvent.Type.FocusIn:
                if self.isEnabled():
                    if not self.underMouse():
                        ani = QPropertyAnimation(self, b"Opacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("Opacity"))
                        ani.setEndValue(1.0)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.finished.connect(ani.deleteLater)
                        ani.start()
                else:
                    ani = QPropertyAnimation(self, b"Opacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("Opacity"))
                    ani.setEndValue(0.3)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.finished.connect(ani.deleteLater)
                    ani.start()
            case QEvent.Type.Leave:
                if self.isEnabled():
                    if not self.hasFocus():
                        ani = QPropertyAnimation(self, b"Opacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("Opacity"))
                        ani.setEndValue(0.6)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.finished.connect(ani.deleteLater)
                        ani.start()
                else:
                    ani = QPropertyAnimation(self, b"Opacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("Opacity"))
                    ani.setEndValue(0.3)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.finished.connect(ani.deleteLater)
                    ani.start()
            case QEvent.Type.FocusOut:
                if self.isEnabled():
                    if not self.underMouse():
                        ani = QPropertyAnimation(self, b"Opacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("Opacity"))
                        ani.setEndValue(0.6)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.finished.connect(ani.deleteLater)
                        ani.start()
                else:
                    ani = QPropertyAnimation(self, b"Opacity", self)
                    ani.setDuration(500)
                    ani.setStartValue(self.property("Opacity"))
                    ani.setEndValue(0.3)
                    ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                    ani.finished.connect(ani.deleteLater)
                    ani.start()
            case QEvent.Type.EnabledChange:
                match self.isEnabled:
                    case True:
                        ani = QPropertyAnimation(self, b"Opacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(0.3)
                        ani.setEndValue(1.0 if (self.underMouse() or self.hasFocus()) and self.isEnabled() else 0.6)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.finished.connect(ani.deleteLater)
                        ani.start()
                    case False:
                        ani = QPropertyAnimation(self, b"Opacity", self)
                        ani.setDuration(500)
                        ani.setStartValue(self.property("Opacity"))
                        ani.setEndValue(0.3)
                        ani.setEasingCurve(QEasingCurve.Type.OutExpo)
                        ani.finished.connect(ani.deleteLater)
                        ani.start()
        return super().eventFilter(a0, a1)


class Label(LabelBase):
    pass


class StrongLabel(LabelBase):
    pass


class TitleLabel(LabelBase):
    pass
