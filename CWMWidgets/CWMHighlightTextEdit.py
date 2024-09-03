# -*- coding: utf-8 -*-
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from .CWMTextEdit import TextEdit


class HighlightTextEdit(TextEdit):
    class Highlighter(QSyntaxHighlighter):
        highlight_styles = {
        }
        
        def __init__(self, document):
            super().__init__(document)
            
            self.rules = []
        
        def highlightBlock(self, text):
            rules_compiled = [(QRegularExpression(pat, QRegularExpression.PatternOption.DontCaptureOption), index, fmt)
                              for
                              pat, index, fmt in self.rules]
            for expression, nth, fmt in rules_compiled:
                matchIterator = expression.globalMatch(text)
                while matchIterator.hasNext():
                    one_match = matchIterator.next()
                    self.setFormat(one_match.capturedStart(), one_match.capturedLength(), fmt)
    
    Default_Highlighter = Highlighter
    
    def __init__(self, *args):
        super(HighlightTextEdit, self).__init__(*args)
        self.__highlighter = self.Default_Highlighter(self.document())
        if not isinstance(self.__highlighter, self.Highlighter):
            raise TypeError("`Highlighter` must be an instance of HighlightTextEdit.Highlighter")
