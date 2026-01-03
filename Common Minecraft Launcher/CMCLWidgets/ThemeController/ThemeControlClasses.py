# -*- coding: utf-8 -*-
from enum import Enum

from PyQt6.QtCore import QObject, QPropertyAnimation, QParallelAnimationGroup, QEasingCurve
from PyQt6.QtGui import *


class Colour(QColor):
    def mix(self, colour, percent=50):
        percent /= 100
        r, g, b, a = self.red(), self.green(), self.blue(), self.alpha()
        r2, g2, b2, a2 = colour.red(), colour.green(), colour.blue(), colour.alpha()
        return Colour(r2 * percent + r * (1 - percent), g2 * percent + g * (1 - percent),
                      b2 * percent + b * (1 - percent), a2 * percent + a * (1 - percent))
    
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
        return (self.red, self.green, self.blue, self.alpha)[item]()
    
    def __setitem__(self, key, value):
        (self.setRed, self.setGreen, self.setBlue, self.setAlpha)[key](max(value, 0))


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
        self.__currentTheme = Theme.Light
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
    
    def setColour(self, role, is_highlight, is_primary, theme, colour, animation=False):
        is_highlight = bool(is_highlight)
        is_primary = bool(is_primary)
        curTheme = self.currentTheme
        colour = Colour(colour)
        self.setProperty(f"{role.value}_{theme.value}_{is_highlight}_{is_primary}", QColor(colour))
        if theme != curTheme:
            return
        if animation:
            colourAnimation = QPropertyAnimation(self, f"{role.value}_{is_highlight}_{is_primary}".encode(), self)
            colourAnimation.setStartValue(QColor(self.property(f"{role.value}_{is_highlight}_{is_primary}")))
            colourAnimation.setEndValue(
                QColor(self.property(f"{role.value}_{curTheme.value}_{is_highlight}_{is_primary}")))
            colourAnimation.setDuration(500)
            colourAnimation.setEasingCurve(QEasingCurve.Type.OutExpo)
            colourAnimation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        else:
            self.setProperty(f"{role.value}_{is_highlight}_{is_primary}",
                             QColor(self.property(f"{role.value}_{curTheme.value}_{is_highlight}_{is_primary}")))
    
    def getColour(self, role, is_highlight, is_primary, theme=None):
        is_highlight = bool(is_highlight)
        is_primary = bool(is_primary)
        if theme:
            return Colour(self.property(f"{role.value}_{theme.value}_{is_highlight}_{is_primary}"))
        return Colour(self.property(f"{role.value}_{is_highlight}_{is_primary}"))
    
    def toggleTheme(self, theme, animation=False):
        if animation:
            self.__animationGroup = QParallelAnimationGroup(self)
        
        for primary in [True, False]:
            for role in [ColourRole.Background, ColourRole.Border, ColourRole.Foreground]:
                for highlight in [True, False]:
                    if animation:
                        colourAnimation = QPropertyAnimation(self, f"{role.value}_{highlight}_{primary}".encode(), self)
                        colourAnimation.setStartValue(QColor(self.property(f"{role.value}_{highlight}_{primary}")))
                        colourAnimation.setEndValue(
                            QColor(self.property(f"{role.value}_{theme.value}_{highlight}_{primary}")))
                        colourAnimation.setDuration(500)
                        colourAnimation.setEasingCurve(QEasingCurve.Type.OutExpo)
                        self.__animationGroup.addAnimation(colourAnimation)
                    else:
                        self.setProperty(f"{role.value}_{highlight}_{primary}",
                                         self.property(f"{role.value}_{theme.value}_{highlight}_{primary}"))
        
        if animation:
            self.__animationGroup.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
    
    @property
    def currentTheme(self):
        return self.__currentTheme
    
    @currentTheme.setter
    def currentTheme(self, value):
        self.__currentTheme = value
