# -*- coding: utf-8 -*-
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from .CWMTextEdit import TextEdit
from .CWMThemeControl import *


class LineNumberTextEdit(TextEdit):
    class LineNumberBar(QWidget):
        def __init__(self, parent):
            super().__init__(parent)
            self.__codeEditor = parent
            self.__codeEditor.cursorPositionChanged.connect(self.updateLineNumberBar)
            self.__codeEditor.textChanged.connect(self.updateLineNumberBar)
        
        def updateLineNumberBar(self):
            self.update()
            self.adjustSize()
        
        def adjustSize(self):
            super().adjustSize()
            count = self.__codeEditor.document().blockCount()
            width = self.fontMetrics().boundingRect(str(count)).width() + 5
            self.setFixedWidth(width)
            self.__codeEditor.setViewportMargins(width, 0, 0, 0)
        
        def paintEvent(self, event):
            self.setFont(self.__codeEditor.font())
            painter = QPainter(self)
            painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing)
            pp = QPainterPath()
            painter.setPen(getBorderColour())
            painter.setBrush(getBackgroundColour())
            painter.drawRoundedRect(self.rect(), 10, 10)
            pp.addRoundedRect(QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5), 10, 10)
            painter.setClipPath(pp)
            painter.setPen(Qt.GlobalColor.black)
            painter.setBrush(Qt.GlobalColor.transparent)
            block = self.__codeEditor.document().firstBlock()
            font_height = self.fontMetrics().height()
            
            y = self.y() + (
                    (self.fontMetrics().height() / 4) - self.y() - self.__codeEditor.verticalScrollBar().value())
            current_block = self.__codeEditor.textCursor().block().blockNumber()
            while block.isValid():
                if block.blockNumber() == current_block:
                    painter.setPen(getBorderColour(highlight=True))
                else:
                    painter.setPen(getForegroundColour())
                painter.setFont(self.font())
                painter.drawText(QRectF(0, y, self.width(), font_height), Qt.AlignmentFlag.AlignRight,
                                 str(block.blockNumber() + 1))
                y += block.layout().boundingRect().height()
                block = block.next()
    
    def __init__(self, *args):
        super().__init__(*args)
        self.__lineNumberBar = self.LineNumberBar(self)
        self.__lineNumberBar.updateLineNumberBar()
        self.setViewportMargins(self.__lineNumberBar.width(), 0, 0, 0)
    
    def event(self, e):
        try:
            self.__lineNumberBar.updateLineNumberBar()
            self.setViewportMargins(self.__lineNumberBar.width(), 0, 0, 0)
            self.__lineNumberBar.setGeometry(0,
                                             self.viewport().y(),
                                             self.__lineNumberBar.width(),
                                             self.viewport().height())
        except AttributeError:
            pass
        return super().event(e)
