# -*- coding: utf-8 -*-
from PyQt6.QtGui import *
from enum import Enum


class Theme(Enum):
    Light = "Light"
    Dark = "Dark"


class ColourRoles(Enum):
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
        return super().__getitem__(LightDarkDict(item))
    
    def __setitem__(self, key, value):
        if key not in [True, False]:
            raise KeyError(key)
        super().__setitem__(key, LightDarkDict(value))


class ThemeColours(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __getitem__(self, item):
        if item not in [ColourRoles.Foreground, ColourRoles.Background, ColourRoles.Border]:
            raise KeyError(item)
        return HighlightsDict(super().__getitem__(item))
    
    def __setitem__(self, key, value):
        if key not in [ColourRoles.Foreground, ColourRoles.Background, ColourRoles.Border]:
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
    foreHighlighs = HighlightsDict()
    foreNohColours = LightDarkDict()
    foreNohColours[Theme.Light] = (0, 0, 0)
    foreNohColours[Theme.Dark] = (255, 255, 255)
    foreHighlighs[False] = foreNohColours
    forehColours = LightDarkDict()
    forehColours[Theme.Light] = (0, 0, 0)
    forehColours[Theme.Dark] = (255, 255, 255)
    foreHighlighs[True] = forehColours
    themeColours[ColourRoles.Foreground] = foreHighlighs
    backHighlights = HighlightsDict()
    backNohColours = LightDarkDict()
    backNohColours[Theme.Light] = (253, 253, 253)
    backNohColours[Theme.Dark] = (67, 67, 67)
    backHighlights[False] = backNohColours
    backhColours = LightDarkDict()
    backhColours[Theme.Light] = (176, 224, 250)
    backhColours[Theme.Dark] = (142, 197, 252)
    themeColours[ColourRoles.Background] = backHighlights
    borderHighlights = HighlightsDict()
    borderNohColours = LightDarkDict()
    borderNohColours[Theme.Light] = (230, 230, 230)
    borderNohColours[Theme.Dark] = (134, 143, 150)
    borderHighlights[False] = borderNohColours
    borderhColours = LightDarkDict()
    borderhColours[Theme.Light] = (135, 206, 250)
    borderhColours[Theme.Dark] = (79, 172, 254)
    borderHighlights[True] = borderhColours
    themeColours[ColourRoles.Border] = borderHighlights
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
