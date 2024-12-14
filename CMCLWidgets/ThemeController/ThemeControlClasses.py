# -*- coding: utf-8 -*-
from PyQt6.QtGui import *
from enum import Enum


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


class Colour(QColor):
    pass
