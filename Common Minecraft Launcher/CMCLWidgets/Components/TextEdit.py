# -*- coding: utf-8 -*-
from typing import overload

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from ..Windows import RoundedMenu
from ..ThemeController import *
from .ScrollBar import ScrollBar

from .Widget import Widget


class TextEdit(QTextEdit, Widget):
    @overload
    def __init__(self, parent=None):
        ...
    
    @overload
    def __init__(self, text, parent=None):
        ...
    
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setHorizontalScrollBar(ScrollBar(Qt.Orientation.Horizontal, self))
        self.setVerticalScrollBar(ScrollBar(Qt.Orientation.Vertical, self))
        
        self.removeEventFilter(self)
        self.viewport().installEventFilter(self)
        
        self.setProperty("cursorOpacity", 0.0)
        self.setProperty("cursorPos", QPoint(0, 0))
        
        self.cursorPositionChanged.connect(self.__cursorPosChanged)
    
    def paintEvent(self, e):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self.viewport())
        painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing)
        
        painter.save()
        painter.setOpacity(self.viewport().property("baseOpacity"))
        painter.setPen(getBorderColour(is_highlight=self.hasFocus() and self.isEnabled()))
        painter.setBrush(getBackgroundColour(is_highlight=self.hasFocus() and self.isEnabled()))
        painter.drawRoundedRect(self.viewport().rect().adjusted(1, 1, -1, -1), 16, 16)
        painter.restore()
        
        if self.viewport().property("frameOpacity"):
            painter.save()
            painter.setOpacity(self.viewport().property("frameOpacity"))
            painter.setPen(getBorderColour(is_highlight=True))
            painter.setBrush(getBackgroundColour(is_highlight=self.hasFocus() and self.isEnabled()))
            painter.drawRoundedRect(self.viewport().rect().adjusted(1, 1, -1, -1), 16, 16)
            painter.restore()
        
        painter.save()
        painter.setOpacity(self.viewport().property("baseOpacity") + (
                self.viewport().property("frameOpacity") * (1.0 - self.viewport().property("baseOpacity"))))
        painter.translate(-self.horizontalScrollBar().value(), -self.verticalScrollBar().value())
        pp = QPainterPath()
        rect = QRectF(self.horizontalScrollBar().value(), self.verticalScrollBar().value(),
                      self.viewport().width(), self.viewport().height())
        pp.addRoundedRect(rect.adjusted(1.625, 1.625, -1.625, -1.625), 16, 16)
        painter.setClipPath(pp)
        context = self.document().documentLayout().PaintContext()
        context.palette = self.palette()
        context.palette.setColor(QPalette.ColorRole.Text, getForegroundColour())
        selection = self.document().documentLayout().Selection()
        selection.cursor = self.textCursor()
        charFormat = QTextCharFormat()
        charFormat.setBackground(getBorderColour(is_highlight=self.hasFocus() and self.isEnabled()))
        selection.format = charFormat
        context.selections = [selection]
        self.document().documentLayout().draw(painter, context)
        if not self.toPlainText() and self.placeholderText():
            placeholderDocument = QTextDocument()
            placeholderDocument.setDefaultStyleSheet(f"body {{ color: rgb{getForegroundColour(is_tuple=True)}; }}")
            placeholderDocument.setTextWidth(self.document().textWidth())
            placeholderDocument.setDocumentMargin(self.document().documentMargin())
            placeholderDocument.setDefaultFont(self.document().defaultFont())
            placeholderDocument.setLayoutEnabled(self.document().isLayoutEnabled())
            placeholderDocument.setPlainText(self.placeholderText())
            placeholderDocument.setHtml(placeholderDocument.toHtml())
            painter.save()
            painter.setOpacity(painter.opacity() * 0.45)
            placeholderDocument.drawContents(painter)
            painter.restore()
        painter.restore()
        
        painter.save()
        pp = QPainterPath()
        rect = QRectF(0, 0, self.viewport().width(), self.viewport().height())
        pp.addRoundedRect(rect.adjusted(1.625, 1.625, -1.625, -1.625), 16, 16)
        painter.setClipPath(pp)
        if self.property("cursorOpacity"):
            painter.setOpacity(self.property("cursorOpacity") * self.viewport().property("frameOpacity"))
            painter.setPen(getForegroundColour())
            painter.setBrush(getForegroundColour())
            painter.translate(-self.horizontalScrollBar().value(), -self.verticalScrollBar().value())
            rect = QRect(self.property("cursorPos"), self.cursorRect().size())
            painter.drawRoundedRect(rect, 1, 1)
        painter.restore()
    
    def contextMenuEvent(self, e):
        super().contextMenuEvent(e)
        menus = self.findChildren(QMenu)
        if menus:
            menu = menus[0]
            menu.BORDER_RADIUS = RoundedMenu.BORDER_RADIUS
            RoundedMenu.updateQSS(menu)
            menu.popup(QCursor.pos())
    
    def focusInEvent(self, a0):
        super().focusInEvent(a0)
        
        if not self.isEnabled() or self.isReadOnly():
            return
        
        def func(ani):
            if self.hasFocus() and self.isEnabled():
                ani.setDuration(QApplication.instance().cursorFlashTime())
                ani.start()
        
        ani = QPropertyAnimation(self, b"cursorOpacity", self)
        ani.setStartValue(0.0)
        ani.setKeyValueAt(0.5, 1.0)
        ani.setEndValue(0.0)
        ani.setDuration(QApplication.instance().cursorFlashTime())
        ani.finished.connect(lambda: func(ani))
        ani.start()
    
    def focusOutEvent(self, a0):
        super().focusOutEvent(a0)
        ani = QPropertyAnimation(self, b"cursorOpacity", self)
        ani.setStartValue(self.property("cursorOpacity"))
        ani.setEndValue(0.0)
        ani.setDuration(1000)
        ani.start()
    
    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        pos = self.cursorRect().topLeft() - QPoint(-self.horizontalScrollBar().value(),
                                                   -self.verticalScrollBar().value())
        self.setProperty("cursorPos", pos)
    
    def __cursorPosChanged(self):
        pos = self.cursorRect().topLeft() - QPoint(-self.horizontalScrollBar().value(),
                                                   -self.verticalScrollBar().value())
        ani = QPropertyAnimation(self, b"cursorPos", self)
        ani.setStartValue(self.property("cursorPos"))
        ani.setEndValue(pos)
        ani.setDuration(250)
        ani.setEasingCurve(QEasingCurve.Type.OutQuint)
        ani.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        if self.isEnabled and not self.isReadOnly():
            ani.valueChanged.connect(lambda: self.setProperty("cursorOpacity", 1.0))


class PlainTextEdit(QPlainTextEdit, Widget):
    @overload
    def __init__(self, parent=None):
        ...
    
    @overload
    def __init__(self, text, parent=None):
        ...
    
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setHorizontalScrollBar(ScrollBar(Qt.Orientation.Horizontal, self))
        self.setVerticalScrollBar(ScrollBar(Qt.Orientation.Vertical, self))
        
        self.removeEventFilter(self)
        self.viewport().installEventFilter(self)
        
        self.setProperty("cursorOpacity", 0.0)
        self.setProperty("cursorPos", QPoint(0, 0))
        
        self.cursorPositionChanged.connect(self.__cursorPosChanged)
    
    def paintEvent(self, e):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self.viewport())
        painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing)
        
        painter.save()
        painter.setOpacity(self.viewport().property("baseOpacity"))
        painter.setPen(getBorderColour(is_highlight=self.hasFocus() and self.isEnabled()))
        painter.setBrush(getBackgroundColour(is_highlight=self.hasFocus() and self.isEnabled()))
        painter.drawRoundedRect(self.viewport().rect().adjusted(1, 1, -1, -1), 16, 16)
        painter.restore()
        
        if self.viewport().property("frameOpacity"):
            painter.save()
            painter.setOpacity(self.viewport().property("frameOpacity"))
            painter.setPen(getBorderColour(is_highlight=True))
            painter.setBrush(getBackgroundColour(is_highlight=self.hasFocus() and self.isEnabled()))
            painter.drawRoundedRect(self.viewport().rect().adjusted(1, 1, -1, -1), 16, 16)
            painter.restore()
        
        painter.save()
        painter.setOpacity(self.viewport().property("baseOpacity") + (
                self.viewport().property("frameOpacity") * (1.0 - self.viewport().property("baseOpacity"))))
        painter.translate(-self.horizontalScrollBar().value(), -self.verticalScrollBar().value())
        pp = QPainterPath()
        rect = QRectF(self.horizontalScrollBar().value(), self.verticalScrollBar().value(),
                      self.viewport().width(), self.viewport().height())
        pp.addRoundedRect(rect.adjusted(1.625, 1.625, -1.625, -1.625), 16, 16)
        painter.setClipPath(pp)
        context = self.document().documentLayout().PaintContext()
        context.palette = self.palette()
        context.palette.setColor(QPalette.ColorRole.Text, getForegroundColour())
        selection = self.document().documentLayout().Selection()
        selection.cursor = self.textCursor()
        charFormat = QTextCharFormat()
        charFormat.setBackground(getBorderColour(is_highlight=self.hasFocus() and self.isEnabled()))
        selection.format = charFormat
        context.selections = [selection]
        self.document().documentLayout().draw(painter, context)
        if not self.toPlainText() and self.placeholderText():
            placeholderDocument = QTextDocument()
            placeholderDocument.setDefaultStyleSheet(f"body {{ color: rgb{getForegroundColour(is_tuple=True)}; }}")
            placeholderDocument.setTextWidth(self.document().textWidth())
            placeholderDocument.setDocumentMargin(self.document().documentMargin())
            placeholderDocument.setDefaultFont(self.document().defaultFont())
            placeholderDocument.setLayoutEnabled(self.document().isLayoutEnabled())
            placeholderDocument.setPlainText(self.placeholderText())
            placeholderDocument.setHtml(placeholderDocument.toHtml())
            painter.save()
            painter.setOpacity(painter.opacity() * 0.45)
            placeholderDocument.drawContents(painter)
            painter.restore()
        painter.restore()
        
        painter.save()
        pp = QPainterPath()
        rect = QRectF(0, 0, self.viewport().width(), self.viewport().height())
        pp.addRoundedRect(rect.adjusted(1.625, 1.625, -1.625, -1.625), 16, 16)
        painter.setClipPath(pp)
        if self.property("cursorOpacity"):
            painter.setOpacity(self.property("cursorOpacity") * self.viewport().property("frameOpacity"))
            painter.setPen(getForegroundColour())
            painter.setBrush(getForegroundColour())
            painter.translate(-self.horizontalScrollBar().value(), -self.verticalScrollBar().value())
            rect = QRect(self.property("cursorPos"), self.cursorRect().size())
            painter.drawRoundedRect(rect, 1, 1)
        painter.restore()
    
    def contextMenuEvent(self, e):
        super().contextMenuEvent(e)
        menus = self.findChildren(QMenu)
        if menus:
            menu = menus[0]
            menu.BORDER_RADIUS = RoundedMenu.BORDER_RADIUS
            RoundedMenu.updateQSS(menu)
            menu.popup(QCursor.pos())
    
    def focusInEvent(self, a0):
        super().focusInEvent(a0)
        
        if not self.isEnabled() or self.isReadOnly():
            return
        
        def func(ani):
            if self.hasFocus() and self.isEnabled():
                ani.setDuration(QApplication.instance().cursorFlashTime())
                ani.start()
        
        ani = QPropertyAnimation(self, b"cursorOpacity", self)
        ani.setStartValue(0.0)
        ani.setKeyValueAt(0.5, 1.0)
        ani.setEndValue(0.0)
        ani.setDuration(QApplication.instance().cursorFlashTime())
        ani.finished.connect(lambda: func(ani))
        ani.start()
    
    def focusOutEvent(self, a0):
        super().focusOutEvent(a0)
        ani = QPropertyAnimation(self, b"cursorOpacity", self)
        ani.setStartValue(self.property("cursorOpacity"))
        ani.setEndValue(0.0)
        ani.setDuration(1000)
        ani.start()
    
    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        pos = self.cursorRect().topLeft() - QPoint(-self.horizontalScrollBar().value(),
                                                   -self.verticalScrollBar().value())
        self.setProperty("cursorPos", pos)
    
    def __cursorPosChanged(self):
        pos = self.cursorRect().topLeft() - QPoint(-self.horizontalScrollBar().value(),
                                                   -self.verticalScrollBar().value())
        ani = QPropertyAnimation(self, b"cursorPos", self)
        ani.setStartValue(self.property("cursorPos"))
        ani.setEndValue(pos)
        ani.setDuration(250)
        ani.setEasingCurve(QEasingCurve.Type.OutQuint)
        ani.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        if self.isEnabled and not self.isReadOnly():
            ani.valueChanged.connect(lambda: self.setProperty("cursorOpacity", 1.0))
