# -*- coding: utf-8 -*-
from PyQt6.QtCore import *
from .Compoments.TextEdit import TextEdit
from .Compoments.Panel import Panel
from .ThemeController.ThemeControl import *


class LineNumberTextEdit(TextEdit):
    class LineNumberBar(Panel):
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
        
        def paintEvent(self, a0):
            super().paintEvent(a0)
            self.setFont(self.__codeEditor.font())
            painter = QPainter(self)
            painter.setOpacity(self.property("Opacity"))
            painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing)
            pp = QPainterPath()
            painter.setPen(getBorderColour())
            painter.setBrush(getBackgroundColour())
            # painter.drawRoundedRect(self.rect(), 10, 10)
            pp.addRoundedRect(QRectF(self.rect()).adjusted(1.625, 1.625, -1.625, -1.625), 10, 10)
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
                    painter.setPen(getBorderColour(is_highlight=True))
                else:
                    painter.setPen(getForegroundColour())
                painter.setFont(self.font())
                painter.drawText(QRectF(0, y, self.width() - 1.5, font_height), Qt.AlignmentFlag.AlignRight,
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
            self.__lineNumberBar.setGeometry(3,
                                             self.viewport().y(),
                                             self.__lineNumberBar.width(),
                                             self.viewport().height())
        except AttributeError:
            pass
        return super().event(e)
