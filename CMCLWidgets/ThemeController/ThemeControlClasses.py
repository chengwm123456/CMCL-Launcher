# -*- coding: utf-8 -*-
from enum import Enum

from PyQt6.QtGui import *


class Colour(QColor):
    def __bool__(self):
        return self.isValid()
    
    def __str__(self):
        return f"({self.red()}, {self.green()}, {self.blue()})"
    
    def __repr__(self):
        return repr(self.__str__())
    
    def __iter__(self):
        yield self.red()
        yield self.green()
        yield self.blue()
        if self.alpha() != 255:
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
        setFunc(value)


class Theme(Enum):
    Light = "Light"
    Dark = "Dark"


class ColourRole(Enum):
    Foreground = "Foreground"
    Background = "Background"
    Border = "Border"


class LightDarkDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __getitem__(self, item):
        if item not in [Theme.Dark, Theme.Light]:
            raise KeyError(item)
        return super().__getitem__(item)
    
    def __setitem__(self, key, value):
        if key not in [Theme.Dark, Theme.Light]:
            raise KeyError(key)
        super().__setitem__(key, value)


class HighlightsDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __getitem__(self, item):
        if item not in [True, False]:
            raise KeyError(item)
        return LightDarkDict(super().__getitem__(item))
    
    def __setitem__(self, key, value):
        if key not in [True, False]:
            raise KeyError(key)
        super().__setitem__(key, LightDarkDict(value))


class ThemeColours(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __getitem__(self, item):
        if item not in [ColourRole.Foreground, ColourRole.Background, ColourRole.Border]:
            raise KeyError(item)
        return HighlightsDict(super().__getitem__(item))
    
    def __setitem__(self, key, value):
        if key not in [ColourRole.Foreground, ColourRole.Background, ColourRole.Border]:
            raise KeyError(key)
        super().__setitem__(key, HighlightsDict(value))
