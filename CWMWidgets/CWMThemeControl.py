# -*- coding: utf-8 -*-
from PyQt6.QtGui import *
from enum import Enum


class Theme(Enum):
    Light = "Light"
    Dark = "Dark"


class LightDarkDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __getitem__(self, item):
        if item not in ["Dark", "Light"]:
            raise KeyError(item)
        return super().__getitem__(item)
    
    def __setitem__(self, key, value):
        if key not in ["Dark", "Light"]:
            raise KeyError(key)
        super().__setitem__(key, value)


class HighlightsDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __getitem__(self, item):
        if item not in [True, False]:
            raise KeyError(item)
        return super().__getitem__(LightDarkDict(item))
    
    def __setitem__(self, key, value):
        if key not in [True, False]:
            raise KeyError(key)
        super().__setitem__(key, LightDarkDict(value))


class ThemeColours(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __getitem__(self, item):
        if item not in ["Foreground", "Background", "Border"]:
            raise KeyError(item)
        return HighlightsDict(super().__getitem__(item))
    
    def __setitem__(self, key, value):
        if key not in ["Foreground", "Background", "Border"]:
            raise KeyError(key)
        super().__setitem__(key, HighlightsDict(value))


def setTheme(theme):
    globals()["currentTheme"] = theme


def getTheme():
    return globals().get("currentTheme", Theme.Light)


def setThemeColour(role, is_primary, is_highlight, theme, colour):
    globals()["currentThemeColours"][role][is_highlight][theme] = colour


def getThemeColour(role, is_primary, is_highlight, theme):
    return globals().get("currentThemeColours", {role: {}}).get(role, {is_highlight: {}}).get(is_highlight, {}).get(
        theme)


def initThemeColours():
    themeColours = ThemeColours()
    foreColours = LightDarkDict()
    foreColours["Light"] = (0, 0, 0)
    foreColours["Dark"] = (255, 255, 255)
    themeColours["Foreground"] = foreColours
    backColours = LightDarkDict()
    backColours["Light"] = (253, 253, 253)
    backColours["Dark"] = (67, 67, 67)
    themeColours["Background"] = backColours
    borderColours = LightDarkDict()
    borderColours["Light"] = (230, 230, 230)
    borderColours["Dark"] = (134, 143, 150)
    themeColours["Border"] = borderColours
    globals()["currentThemeColours"] = themeColours


setTheme(Theme.Light)
initThemeColours()


def getBorderColour(is_primary=False, is_highlight=False, is_tuple=False):
    match getTheme():
        case Theme.Light:
            result = (135, 206, 250) if is_highlight else (230, 230, 230)
            if is_tuple:
                return result
            else:
                return QColor(*result)
        case Theme.Dark:
            result = (79, 172, 254) if is_highlight else (134, 143, 150)
            if is_tuple:
                return result
            else:
                return QColor(*result)


def getBackgroundColour(is_primary=False, is_highlight=False, is_tuple=False):
    match getTheme():
        case Theme.Light:
            result = (176, 224, 250) if is_highlight else (253, 253, 253)
            if is_tuple:
                return result
            else:
                return QColor(*result)
        case Theme.Dark:
            result = (142, 197, 252) if is_highlight else (67, 67, 67)
            if is_tuple:
                return result
            else:
                return QColor(*result)


def getForegroundColour(is_primary=False, is_tuple=False):
    match getTheme():
        case Theme.Light:
            result = (0, 0, 0)
            if is_tuple:
                return result
            else:
                return QColor(*result)
        case Theme.Dark:
            result = (255, 255, 255)
            if is_tuple:
                return result
            else:
                return QColor(*result)
