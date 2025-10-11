# -*- coding: utf-8 -*-
from enum import Enum

from PyQt6.QtCore import QObject, QPropertyAnimation, QParallelAnimationGroup, QEasingCurve
from PyQt6.QtGui import *


class Colour(QColor):
    def __bool__(self) -> bool:
        return self.isValid()
    
    def __str__(self) -> str:
        return str(tuple(self.__iter__()))
    
    def __repr__(self) -> repr:
        return repr(self.__str__())
    
    def __iter__(self):
        for item in self.red(), self.green(), self.blue():
            yield item
        if self.alpha() < 255:
            yield self.alpha()
    
    def __getitem__(self, item):
        if isinstance(item, int) and item >= 4:
            raise IndexError("Colour index our of range")
        getFunc = lambda v: None
        match item:
            case "red" | 0:
                getFunc = self.red
            case "green" | 1:
                getFunc = self.green
            case "blue" | 2:
                getFunc = self.blue
            case "alpha" | 3:
                getFunc = self.alpha
        return getFunc()
    
    def __setitem__(self, key, value):
        if isinstance(key, int) and key >= 4:
            raise IndexError("Colour index our of range")
        setFunc = lambda v: None
        match key:
            case "red" | 0:
                setFunc = self.setRed
            case "green" | 1:
                setFunc = self.setGreen
            case "blue" | 2:
                setFunc = self.setBlue
            case "alpha" | 3:
                setFunc = self.setAlpha
        setFunc(max(value, 0))


class Theme(Enum):
    Light = "Light"
    Dark = "Dark"


class ColourRole(Enum):
    Foreground = "Foreground"
    Background = "Background"
    Border = "Border"


class ColourManager(QObject):
    def __init__(self):
        super().__init__()
        self.__animationGroup = None
        for primary in [True, False]:
            for role in [ColourRole.Background, ColourRole.Border, ColourRole.Foreground]:
                for theme in [Theme.Light, Theme.Dark]:
                    for highlight in [True, False]:
                        self.setProperty(f"{role.value}_{theme.value}_{highlight}_{primary}", QColor(0, 0, 0))
        
        for primary in [True, False]:
            for role in [ColourRole.Background, ColourRole.Border, ColourRole.Foreground]:
                for highlight in [True, False]:
                    self.setProperty(f"{role.value}_{highlight}_{primary}", QColor(0, 0, 0))
    
    def setColour(self, role, is_highlight, is_primary, theme, colour, ani=False, curTheme=Theme.Light):
        colour = Colour(colour)
        self.setProperty(f"{role.value}_{theme.value}_{is_highlight}_{is_primary}", QColor(colour))
        if theme != curTheme:
            return
        if ani:
            colourAnimation = QPropertyAnimation(self, f"{role.value}_{is_highlight}_{is_primary}".encode(), self)
            colourAnimation.setStartValue(QColor(self.property(f"{role.value}_{is_highlight}_{is_primary}")))
            colourAnimation.setEndValue(
                QColor(self.property(f"{role.value}_{curTheme.value}_{is_highlight}_{is_primary}")))
            colourAnimation.setDuration(500)
            colourAnimation.setEasingCurve(QEasingCurve.Type.OutQuint)
            colourAnimation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        else:
            self.setProperty(f"{role.value}_{is_highlight}_{is_primary}",
                             QColor(self.property(f"{role.value}_{curTheme.value}_{is_highlight}_{is_primary}")))
    
    def colour(self, role, is_highlight, is_primary, theme=None):
        if theme:
            return Colour(self.property(f"{role.value}_{theme.value}_{is_highlight}_{is_primary}"))
        return Colour(self.property(f"{role.value}_{is_highlight}_{is_primary}"))
    
    def toggleTheme(self, theme, ani=False):
        for primary in [True, False]:
            for role in [ColourRole.Background, ColourRole.Border, ColourRole.Foreground]:
                for highlight in [True, False]:
                    if ani:
                        colourAnimation = QPropertyAnimation(self, f"{role.value}_{highlight}_{primary}".encode(), self)
                        colourAnimation.setStartValue(QColor(self.property(f"{role.value}_{highlight}_{primary}")))
                        colourAnimation.setEndValue(
                            QColor(self.property(f"{role.value}_{theme.value}_{highlight}_{primary}")))
                        colourAnimation.setDuration(500)
                        colourAnimation.setEasingCurve(QEasingCurve.Type.OutQuint)
                        colourAnimation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                    else:
                        self.setProperty(f"{role.value}_{highlight}_{primary}",
                                         self.property(f"{role.value}_{theme.value}_{highlight}_{primary}"))
