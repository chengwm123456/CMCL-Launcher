# -*- coding: utf-8 -*-
from enum import IntEnum

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from .CWMNagivationItem import NavigationItem


class NavigationPanel(QWidget):
    class NavigationItemPosition(IntEnum):
        Left = 0
        Centre = 1
        Right = 2
    
    def __init__(self, parent, content_widget=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setContentsMargins(5, 5, 5, 5)
        self.items = {}
        self.__verticalLayout = QHBoxLayout(self)
        spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.__verticalLayout.addItem(spacer)
        self.__content_widget = content_widget
    
    def addItem(self, page, icon="", pos=NavigationItemPosition.Left):
        item = NavigationItem(self, icon)
        if not bool(len(self.items)):
            item.setChecked(True)
            self.selectAt(page)
        page.setParent(self.__content_widget)
        item.pressed.connect(lambda: self.selectAt(page))
        self.items[item] = page
        page.hide()
        match pos:
            case self.NavigationItemPosition.Left:
                pos = len(self.items) - 1
            case self.NavigationItemPosition.Right:
                pos = -1
            case _:
                pos = len(self.items) - 1
        self.__verticalLayout.insertWidget(pos, item)
    
    def removeItem(self, data):
        if isinstance(data, int):
            if data < len(self.items):
                self.__verticalLayout.removeWidget(self.items[list(self.items.keys())[data]])
        else:
            if data in self.__verticalLayout.children():
                self.__verticalLayout.removeWidget(data)
            if data in self.items.keys():
                self.__verticalLayout.removeWidget(data)
            if data in self.items.values():
                widgets = {j: i for i, j in self.items.items()}
                self.__verticalLayout.removeWidget(widgets[data])
    
    def addButton(self, icon=None, **kwargs):
        btn = NavigationItem(self, icon)
        btn.setCheckable(kwargs.get("selectable"))
        if kwargs.get("page"):
            self.items[btn] = kwargs.get("page")
            btn.pressed.connect(lambda: self.selectAt(kwargs.get("page")))
        if kwargs.get("pressed"):
            btn.pressed.connect(kwargs.get("pressed"))
        self.__verticalLayout.addWidget(btn)
    
    def selectAt(self, page):
        if not self.__content_widget:
            return
        for i in self.items.values():
            i.setParent(self.__content_widget)
            i.hide()
        page.setParent(self.__content_widget)
        page.show()
    
    def setContentWidget(self, widget):
        self.__content_widget = widget
        show = False
        for i in self.items.values():
            i.setParent(self.__content_widget)
            if i.isVisible():
                show = True
        if not show and len(self.items):
            list(self.items.keys())[0].setChecked(True)
            self.selectAt(self.items[list(self.items.keys())[0]])
    
    def paintEvent(self, a0):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QColor(230, 230, 230))  # Light: 255, 255, 255, 18   Light: 0, 0, 0, 18
        painter.setBrush(QColor(249, 249, 249))  # Dark: 43, 43, 43   Light: 249, 249, 249
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)


class FoldableNavigationPanel(NavigationPanel):
    def __init__(self, parent, content_widget=None):
        super().__init__(parent, content_widget)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
    
    def showEvent(self, a0):
        super().showEvent(a0)
        self.fold()
    
    def fold(self):
        self.setContentsMargins(0, 0, 0, 0)
        for i in self.children():
            if hasattr(i, "hide"):
                i.hide()
    
    def expand(self):
        self.setContentsMargins(5, 5, 5, 5)
        for i in self.children():
            if hasattr(i, "show"):
                i.show()
    
    def focusInEvent(self, a0):
        self.expand()
    
    def focusOutEvent(self, a0):
        for i in self.children():
            if hasattr(i, "hasFocus"):
                if i.hasFocus():
                    return
        if self.underMouse():
            return
        self.fold()
    
    def enterEvent(self, event):
        self.expand()
    
    def leaveEvent(self, a0):
        if self.hasFocus():
            return
        for i in self.children():
            if hasattr(i, "hasFocus"):
                if i.hasFocus():
                    return
        self.fold()
