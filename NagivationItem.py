# -*- coding: utf-8 -*-
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from .ThemeController.ThemeControl import *
from .Components.Button import ToolButton


class NavigationItem(ToolButton):
    def __init__(self, parent, icon_path, text_data):
        super().__init__(parent)
        self.setContentsMargins(10, 10, 10, 10)
        self.setFixedSize(42, 42)
        self.setIconSize(QSize(32, 32))
        self.setIcon(QIcon(icon_path))
        self.setText(text_data)
        self.setCheckable(True)
        self.setAutoExclusive(True)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
    
    def setText(self, text):
        super().setText(text)
        super().setToolTip(text)
    
    def setToolTip(self, text):
        super().setToolTip(text)
        super().setText(text)
