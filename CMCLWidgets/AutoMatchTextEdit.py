# -*- coding: utf-8 -*-
from .Compoments.TextEdit import TextEdit


class AutoMatchTextEdit(TextEdit):
    need_match = {}
    
    def __init__(self, *args):
        super().__init__(*args)
        self.__yuechu = True
    
    def keyPressEvent(self, e):
        super().keyPressEvent(e)
        cursor = self.textCursor()
        try:
            if chr(e.key()) in self.need_match.keys():
                cursor.insertText(self.need_match[chr(e.key())])
                cursor.setPosition(cursor.position() - 1)
                self.setTextCursor(cursor)
                self.__yuechu = False
            elif chr(e.key()) in self.need_match.values():
                new_dict = {j: i for i, j in self.need_match.items()}
                try:
                    if new_dict[cursor.block().text()[cursor.positionInBlock()]] == cursor.block().text()[
                        cursor.positionInBlock() - 1]:
                        self.__yuechu = True
                    if not self.__yuechu:
                        self.__yuechu = True
                        cursor.deletePreviousChar()
                        cursor.setPosition(cursor.position() + 1)
                        self.setTextCursor(cursor)
                except (IndexError, KeyError):
                    pass
        except ValueError:
            if e.key() == 16777219:
                if not cursor.atBlockEnd():
                    if cursor.block().text()[cursor.positionInBlock() - 1] in self.need_match.keys():
                        if cursor.block().text()[cursor.positionInBlock()] == self.need_match[
                            cursor.block().text()[cursor.positionInBlock() - 1]]:
                            self.__yuechu = True
                            cursor.setPosition(cursor.position() + 1)
                            cursor.deletePreviousChar()
                            self.setTextCursor(cursor)
                    elif not self.__yuechu:
                        if cursor.block().text()[cursor.positionInBlock()] in self.need_match.values():
                            self.__yuechu = True
                            cursor.setPosition(cursor.position() + 1)
                            cursor.deletePreviousChar()
                            self.setTextCursor(cursor)
