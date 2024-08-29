# -*- coding: utf-8 -*-
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from .CWMThemeControl import *
from .CWMToolTip import ToolTip
from .CWMWindows import RoundedMenu


class ComboBox(QComboBox):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.installEventFilter(ToolTip(self))
    
    def paintEvent(self, e):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self)
        painter.setOpacity(1.0 if self.underMouse() or self.hasFocus() else 0.6)
        if not self.isEnabled():
            painter.setOpacity(0.3)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getBorderColour(highlight=(self.hasFocus() or self.underMouse())))
        painter.setBrush(getBackgroundColour(highlight=self.hasFocus()))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)
        painter.save()
        p = QPen(getBorderColour(
            highlight=self.isEnabled()) if self.hasFocus() or self.underMouse() else getForegroundColour())
        p.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(p)
        del p
        painter.setBrush(getForegroundColour())
        painter.translate((self.width() - 8) - 3, self.height() / 2 - 4)
        painter.drawPolygon([QPoint(0, 0), QPoint(4, 8), QPoint(8, 0)])
        painter.restore()
        op = QStyleOptionComboBox()
        op.initFrom(self)
        self.initStyleOption(op)
        op.palette.setColor(self.foregroundRole(), getForegroundColour())
        op.palette.setColor(self.backgroundRole(), Qt.GlobalColor.transparent)
        self.setStyleSheet("color: black")
        self.style().drawControl(QStyle.ControlElement.CE_ComboBoxLabel, op, painter, self)
    
    def contextMenuEvent(self, e):
        menu = RoundedMenu(self)
        if self.isEditable() and not self.lineEdit().isReadOnly():
            undo = QAction()
            undo.setText("Undo")
            undo.setEnabled(self.lineEdit().isUndoAvailable())
            undo.triggered.connect(self.lineEdit().undo)
            undo.setShortcut("Ctrl+Z")
            menu.addAction(undo)
            redo = QAction()
            redo.setText("Redo")
            redo.setEnabled(self.lineEdit().isRedoAvailable())
            redo.triggered.connect(self.lineEdit().redo)
            redo.setShortcut("Ctrl+Y")
            menu.addAction(redo)
            menu.addSeparator()
            cut = QAction()
            cut.setText("Cut")
            cut.triggered.connect(self.lineEdit().cut)
            cut.setShortcut("Ctrl+X")
            menu.addAction(cut)
        copy = QAction()
        copy.setText("Copy")
        copy.triggered.connect(self.lineEdit().copy)
        copy.setShortcut("Ctrl+C")
        menu.addAction(copy)
        if self.isEditable() and not self.lineEdit().isReadOnly():
            paste = QAction()
            paste.setText("Paste")
            paste.triggered.connect(self.lineEdit().paste)
            paste.setShortcut("Ctrl+V")
            menu.addAction(paste)
            delete = QAction()
            delete.setText("Delete")
            delete.triggered.connect(
                lambda: self.lineEdit().setText(
                    self.lineEdit().text()[:self.lineEdit().cursorPosition() - 1] + self.lineEdit().text()[
                                                                                    self.lineEdit().cursorPosition():]))
            menu.addAction(delete)
        menu.addSeparator()
        select_all = QAction()
        select_all.setText("Select All")
        select_all.triggered.connect(self.lineEdit().selectAll)
        select_all.setShortcut("Ctrl+A")
        menu.addAction(select_all)
        menu.exec(self.mapToGlobal(e.pos()))
