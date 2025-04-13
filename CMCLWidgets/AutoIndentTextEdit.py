# -*- coding: utf-8 -*-
from .Compoments.TextEdit import TextEdit
import re


class AutoIndentTextEdit(TextEdit):
    Indent_Pattern = r""
    Indent_Length = 1
    
    def __init__(self, *args):
        super().__init__(*args)
        self.__indent = 1
        self.__indenting = False
    
    def keyPressEvent(self, e):
        super().keyPressEvent(e)
        if not self.Indent_Pattern:
            return
        cursor = self.textCursor()
        if cursor.atBlockStart() and not cursor.atStart() and e.key() == 16777220:
            previous_block_text = cursor.block().previous().text()
            if previous_block_text.startswith(" "):
                self.__indenting = True
                result = re.match(self.Indent_Pattern.strip(r"\b"),
                                  previous_block_text.lstrip(), re.UNICODE)
                if result:
                    self.__indent = ((len(previous_block_text) - len(
                        previous_block_text.lstrip())) // self.Indent_Length) + 1
                else:
                    self.__indent = ((len(previous_block_text) - len(
                        previous_block_text.lstrip())) // self.Indent_Length)
            else:
                if re.match(self.Indent_Pattern.strip(r"\b"), previous_block_text,
                            re.UNICODE):
                    self.__indent = 1
                    self.__indenting = True
                else:
                    self.__indent = 1
                    result = re.match(self.Indent_Pattern.strip(r"\b"),
                                      previous_block_text.lstrip(), re.UNICODE)
                    if result:
                        self.__indent = ((len(previous_block_text) - len(
                            previous_block_text.lstrip())) // self.Indent_Length) + 1
                        self.__indenting = True
                    else:
                        self.__indent = 0
                        self.__indenting = False
            if self.__indenting:
                cursor.insertText((" " * self.Indent_Length) * self.__indent)
        self.setTabStopDistance(self.Indent_Length * 8.75)
