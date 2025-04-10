# -*- coding: utf-8 -*-
from enum import IntEnum

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from .NagivationItem import NavigationItem
from .Compoments.Panel import Panel


class NavigationPanel(Panel):
    class NavigationItemPosition(IntEnum):
        Left = 0
        Centre = 1
        Right = 2
    
    def __init__(self, parent, content_widget=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setContentsMargins(5, 5, 5, 5)
        self.items = {}
        self.roles = {}
        self.__verticalLayout = QHBoxLayout(self)
        self.__leftLayout = QHBoxLayout()
        self.__verticalLayout.addLayout(self.__leftLayout)
        spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.__verticalLayout.addItem(spacer)
        self.__centreLayout = QHBoxLayout()
        self.__verticalLayout.addLayout(self.__centreLayout)
        spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.__verticalLayout.addItem(spacer)
        self.__rightLayout = QHBoxLayout()
        self.__verticalLayout.addLayout(self.__rightLayout)
        self.__content_widget = content_widget
    
    def addItem(self, page, icon=None, text="", role=None, pos=NavigationItemPosition.Left):
        page.setParent(self.__content_widget)
        page.hide()
        btnrole = self.addButton(icon, text, role, pos, page=page, selectable=True)
        self.items[self.roles[btnrole]] = page
    
    def removeItem(self, data):
        if isinstance(data, int):
            if data < len(self.items):
                if self.items[list(self.items.keys())[data]] in self.__leftLayout.children():
                    self.__leftLayout.removeWidget(self.items[list(self.items.keys())[data]])
                if self.items[list(self.items.keys())[data]] in self.__centreLayout.children():
                    self.__centreLayout.removeWidget(self.items[list(self.items.keys())[data]])
                if self.items[list(self.items.keys())[data]] in self.__rightLayout.children():
                    self.__rightLayout.removeWidget(self.items[list(self.items.keys())[data]])
        elif isinstance(data, str):
            if data in self.roles.keys():
                print(self.roles[data])
                if self.roles[data] in self.__leftLayout.children():
                    self.__leftLayout.removeWidget(self.roles[data])
                if self.roles[data] in self.__centreLayout.children():
                    self.__centreLayout.removeWidget(self.roles[data])
                if self.roles[data] in self.__rightLayout.children():
                    self.__rightLayout.removeWidget(self.roles[data])
        else:
            if data in self.__leftLayout.children() + self.__centreLayout.children() + self.__rightLayout.children():
                if data in self.__leftLayout.children():
                    self.__leftLayout.removeWidget(data)
                if data in self.__centreLayout.children():
                    self.__centreLayout.removeWidget(data)
                if data in self.__rightLayout.children():
                    self.__rightLayout.removeWidget(data)
            if data in self.items.keys():
                self.__verticalLayout.removeWidget(data)
            if data in self.items.values():
                widgets = {j: i for i, j in self.items.items()}
                if widgets[data] in self.__leftLayout.children():
                    self.__leftLayout.removeWidget(widgets[data])
                if widgets[data] in self.__centreLayout.children():
                    self.__centreLayout.removeWidget(widgets[data])
                if widgets[data] in self.__rightLayout.children():
                    self.__rightLayout.removeWidget(widgets[data])
    
    def addButton(self, icon=None, text="", role=None, pos=NavigationItemPosition.Left, **kwargs):
        btn = NavigationItem(self, icon, text)
        btn.setCheckable(kwargs.get("selectable", False))
        if kwargs.get("page"):
            self.items[btn] = kwargs.get("page")
            btn.pressed.connect(lambda: self.selectAt(kwargs.get("page")))
        if kwargs.get("pressed"):
            btn.pressed.connect(kwargs.get("pressed"))
        layout = self.__leftLayout
        match pos:
            case self.NavigationItemPosition.Left:
                layout = self.__leftLayout
            case self.NavigationItemPosition.Right:
                layout = self.__rightLayout
            case self.NavigationItemPosition.Centre:
                layout = self.__centreLayout
        layout.addWidget(btn)
        role = role or str(self.__leftLayout.count() + self.__centreLayout.count() + self.__rightLayout.count())
        self.roles[role] = btn
        return role
    
    def button(self, data):
        if isinstance(data, int):
            if data < len(self.items):
                return self.items[list(self.items.keys())[data]]
        elif isinstance(data, str):
            if data in self.roles.keys():
                return self.roles[data]
        else:
            if data in self.__leftLayout.children() + self.__centreLayout.children() + self.__rightLayout.children():
                return data
            if data in self.items.keys():
                return data
            if data in self.items.values():
                widgets = {j: i for i, j in self.items.items()}
                return widgets[data]
    
    def removeButton(self, data):
        self.removeItem(data)
    
    def selectAt(self, page):
        if not self.__content_widget:
            return
        for i in self.items.values():
            i.setParent(self.__content_widget)
            i.hide()
        page.setParent(self.__content_widget)
        page.show()
        if isinstance(self.__content_widget, QStackedWidget):
            self.__content_widget.setCurrentWidget(page)
    
    def setContentWidget(self, widget):
        b4_widget = self.__content_widget
        self.__content_widget = widget
        show = False
        for i in self.items.values():
            if isinstance(b4_widget, QStackedWidget):
                b4_widget.removeWidget(i)
            i.setParent(self.__content_widget)
            if isinstance(self.__content_widget, QStackedWidget):
                self.__content_widget.addWidget(i)
            if i.isVisible():
                show = True
        if not show and len(self.items):
            list(self.items.keys())[0].setChecked(True)
            self.selectAt(self.items[list(self.items.keys())[0]])
