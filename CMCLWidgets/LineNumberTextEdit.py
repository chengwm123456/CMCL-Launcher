# -*- coding: utf-8 -*-
from PyQt6.QtCore import *
from .Compoments.TextEdit import TextEdit
from .Compoments.Panel import Panel
from .ThemeController.ThemeControl import *


class LineNumberTextEdit(TextEdit):
    class LineNumberBar(Panel):
        def __init__(self, parent):
            super().__init__(parent)
            self.parent().cursorPositionChanged.connect(self.updateLineNumberBar)
            self.parent().textChanged.connect(self.updateLineNumberBar)
        
        def updateLineNumberBar(self):
            self.update()
            self.adjustSize()
        
        def adjustSize(self):
            super().adjustSize()
            count = self.parent().document().blockCount()
            width = max(
                (QFontMetrics(self.parent().font()).boundingRect(str(cnt)).width() for cnt in range(0, 10))) * len(
                str(count)) + 5
            self.setFixedWidth(width)
            self.parent().setViewportMargins(width, 0, 0, 0)
        
        def paintEvent(self, a0):
            super().paintEvent(a0)
            painter = QPainter(self)
            painter.setOpacity(self.property("widgetOpacity"))
            painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing)
            pp = QPainterPath()
            painter.setPen(getBorderColour())
            painter.setBrush(getBackgroundColour())
            pp.addRoundedRect(QRectF(self.rect()).adjusted(1.625, 1.625, -1.625, -1.625), 10, 10)
            painter.setClipPath(pp)
            painter.setPen(Qt.GlobalColor.black)
            painter.setBrush(Qt.GlobalColor.transparent)
            block = self.parent().document().firstBlock()
            
            current_block = self.parent().textCursor().block().blockNumber()
            while block.isValid():
                if block.blockNumber() == current_block:
                    painter.setPen(getBorderColour(is_highlight=True))
                else:
                    painter.setPen(getForegroundColour())
                painter.setFont(self.parent().font())
                painter.drawText(QRectF(0, block.layout().position().y() - self.parent().verticalScrollBar().value(),
                                        self.width() - 1.5, self.fontMetrics().height() + 1.5),
                                 Qt.AlignmentFlag.AlignRight,
                                 str(block.blockNumber() + 1))
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
