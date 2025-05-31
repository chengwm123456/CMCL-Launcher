# -*- coding: utf-8 -*-
from typing import overload

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from ..ThemeController import *
from CMCLWidgets.Windows import RoundedMenu

from .Widget import Widget


class LabelBase(QLabel, Widget):
    @overload
    def __init__(self, parent=None):
        ...
    
    @overload
    def __init__(self, text="", parent=None):
        ...
    
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setStyleSheet(
            f"background: transparent; color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {self.property('widgetOpacity')})")
    
    def paintEvent(self, a0):
        self.setStyleSheet(
            f"background: transparent; color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, {self.property('widgetOpacity')})")
        super().paintEvent(a0)
    
    def contextMenuEvent(self, e):
        super().contextMenuEvent(e)
        if isinstance(self.children()[-1], QMenu):
            menu = self.children()[-1]
            menu.BORDER_RADIUS = 10
            RoundedMenu.updateQSS(menu)


class Label(LabelBase):
    pass


class StrongLabel(LabelBase):
    pass


class TitleLabel(LabelBase):
    pass
