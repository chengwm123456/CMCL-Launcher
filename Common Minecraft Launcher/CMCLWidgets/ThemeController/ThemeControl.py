# -*- coding: utf-8 -*-
from .ThemeControlClasses import *


def getTheme():
    return globals()["currentThemeColourManager"].currentTheme


def setTheme(theme, animation=False):
    globals()["currentThemeColourManager"].currentTheme = theme
    globals()["currentThemeColourManager"].toggleTheme(theme, animation)


def getThemeColour(colour_role, is_highlight, is_primary, theme=None):
    return globals()["currentThemeColourManager"].getColour(colour_role, is_highlight, is_primary, theme)


def setThemeColour(colour_role, is_highlight, is_primary, theme, colour, animation=False):
    globals()["currentThemeColourManager"].setColour(colour_role, is_highlight, is_primary, theme, colour, animation)


def initThemeColours():
    colourManager = ColourManager()
    
    # Foreground Colors - Fluent Design 风格
    colourManager.setColour(ColourRole.Foreground, False, False, Theme.Light, Colour(24, 24, 24))
    colourManager.setColour(ColourRole.Foreground, False, False, Theme.Dark, Colour(243, 243, 243))
    colourManager.setColour(ColourRole.Foreground, True, False, Theme.Light, Colour(24, 24, 24))
    colourManager.setColour(ColourRole.Foreground, True, False, Theme.Dark, Colour(243, 243, 243))
    colourManager.setColour(ColourRole.Foreground, False, True, Theme.Light, Colour(24, 24, 24))
    colourManager.setColour(ColourRole.Foreground, False, True, Theme.Dark, Colour(243, 243, 243))
    colourManager.setColour(ColourRole.Foreground, True, True, Theme.Light, Colour(24, 24, 24))
    colourManager.setColour(ColourRole.Foreground, True, True, Theme.Dark, Colour(243, 243, 243))
    
    # Background Colors - Fluent Design 风格（更柔和的灰度）
    colourManager.setColour(ColourRole.Background, False, False, Theme.Light, Colour(249, 249, 250))
    colourManager.setColour(ColourRole.Background, False, False, Theme.Dark, Colour(39, 39, 42))
    colourManager.setColour(ColourRole.Background, True, False, Theme.Light, Colour(184, 225, 255))
    colourManager.setColour(ColourRole.Background, True, False, Theme.Dark, Colour(72, 130, 235))
    colourManager.setColour(ColourRole.Border, False, False, Theme.Light, Colour(218, 218, 219))
    colourManager.setColour(ColourRole.Border, False, False, Theme.Dark, Colour(68, 68, 70))
    colourManager.setColour(ColourRole.Border, True, False, Theme.Light, Colour(140, 200, 255))
    colourManager.setColour(ColourRole.Border, True, False, Theme.Dark, Colour(100, 165, 255))
    
    # Primary Colors - 保持主题色不变
    colourManager.setColour(ColourRole.Background, False, True, Theme.Light, Colour(200, 230, 255))
    colourManager.setColour(ColourRole.Background, False, True, Theme.Dark, Colour(65, 115, 210))
    colourManager.setColour(ColourRole.Background, True, True, Theme.Light, Colour(215, 240, 255))
    colourManager.setColour(ColourRole.Background, True, True, Theme.Dark, Colour(80, 140, 245))
    colourManager.setColour(ColourRole.Border, False, True, Theme.Light, Colour(155, 205, 255))
    colourManager.setColour(ColourRole.Border, False, True, Theme.Dark, Colour(110, 170, 255))
    colourManager.setColour(ColourRole.Border, True, True, Theme.Light, Colour(175, 220, 255))
    colourManager.setColour(ColourRole.Border, True, True, Theme.Dark, Colour(125, 185, 255))
    
    globals()["currentThemeColourManager"] = colourManager


initThemeColours()


def getBorderColour(is_primary=False, is_highlight=False, is_tuple=False):
    border_colour = getThemeColour(
        colour_role=ColourRole.Border,
        is_primary=is_primary,
        is_highlight=is_highlight
    )
    if is_tuple:
        return tuple(border_colour)
    else:
        return border_colour


def getBackgroundColour(is_primary=False, is_highlight=False, is_tuple=False):
    background_colour = getThemeColour(
        colour_role=ColourRole.Background,
        is_primary=is_primary,
        is_highlight=is_highlight
    )
    if is_tuple:
        return tuple(background_colour)
    else:
        return background_colour


def getForegroundColour(is_primary=False, is_tuple=False):
    colour = getThemeColour(colour_role=ColourRole.Foreground, is_primary=is_primary, is_highlight=False)
    if is_tuple:
        return tuple(colour)
    else:
        return colour
