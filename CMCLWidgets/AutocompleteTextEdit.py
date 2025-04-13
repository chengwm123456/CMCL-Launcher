# -*- coding: utf-8 -*-
import re

from PyQt6.QtCore import *
from PyQt6.QtGui import *

from .Compoments.TextEdit import TextEdit
from .Windows import RoundedMenu


class AutocompleteTextEdit(TextEdit):
    Complete_List = []
    Default_Complete_Panel = RoundedMenu
    
    def __init__(self, *args):
        super().__init__(*args)
        self.__complete_panel = self.Default_Complete_Panel(self)
        self.__complete_panel.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.Sheet)
    
    def __complete(self, start, end, text):
        length = end - start
        cursor = self.textCursor()
        for i in range(length):
            cursor.deletePreviousChar()
        cursor.insertText(text)
    
    def keyPressEvent(self, e):
        super().keyPressEvent(e)
        cursor = self.textCursor()
        possibilities = []
        for i in self.Complete_List:
            pattern = fr"\b({'|'.join([i[:j] for j in range(1, len(i))])})\b"
            result = re.search(pattern, cursor.block().text()[:cursor.positionInBlock()])
            if result:
                possibilities.append((result, i))
        
        if possibilities:
            self.__complete_panel.clear()
            for i in possibilities:
                result = i[0]
                start, end = result.start(), result.end()
                action = QAction(i[1], self.__complete_panel)
                action.triggered.connect(
                    lambda _, s=start, e=end, text=i[1]: (self.__complete(s, e, text), self.__complete_panel.hide()))
                self.__complete_panel.addAction(action)
            fm = QFontMetrics(self.font())
            h = int(cursor.block().layout().position().y() + fm.height())
            w = fm.boundingRect(cursor.block().text()[:cursor.positionInBlock()]).width()
            self.__complete_panel.adjustSize()
            self.__complete_panel.move(self.mapToGlobal(QPoint(w, h)))
            self.__complete_panel.setVisible(True)
        else:
            self.__complete_panel.hide()
    
    def focusOutEvent(self, e):
        super().focusOutEvent(e)
        self.__complete_panel.hide()
