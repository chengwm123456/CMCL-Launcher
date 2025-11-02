# -*- coding: utf-8 -*-
from .ThemeControlClasses import *


def getTheme():
    return globals()["currentThemeColourManager"].currentTheme


def setTheme(theme, animation=False):
    globals()["currentThemeColourManager"].currentTheme = theme
    globals()["currentThemeColourManager"].toggleTheme(theme, animation)


def getThemeColour(colour_role, is_highlight, is_primary, theme=None):
    if theme == getTheme():
        theme = None
    return globals()["currentThemeColourManager"].getColour(colour_role, is_highlight, is_primary, theme)


def setThemeColour(colour_role, is_highlight, is_primary, theme, colour, animation=False):
    globals()["currentThemeColourManager"].setColour(colour_role, is_highlight, is_primary, theme, colour, animation)


def initThemeColours():
    colourManager = ColourManager()
    colourManager.setColour(ColourRole.Foreground, False, False, Theme.Light, Colour(0, 0, 0))
    colourManager.setColour(ColourRole.Foreground, False, False, Theme.Dark, Colour(255, 255, 255))
    colourManager.setColour(ColourRole.Foreground, True, False, Theme.Light, Colour(0, 0, 0))
    colourManager.setColour(ColourRole.Foreground, True, False, Theme.Dark, Colour(255, 255, 255))
    colourManager.setColour(ColourRole.Foreground, False, True, Theme.Light, Colour(0, 0, 0))
    colourManager.setColour(ColourRole.Foreground, False, True, Theme.Dark, Colour(255, 255, 255))
    colourManager.setColour(ColourRole.Foreground, True, True, Theme.Light, Colour(0, 0, 0))
    colourManager.setColour(ColourRole.Foreground, True, True, Theme.Dark, Colour(255, 255, 255))
    colourManager.setColour(ColourRole.Background, False, False, Theme.Light, Colour(253, 253, 253))
    colourManager.setColour(ColourRole.Background, False, False, Theme.Dark, Colour(67, 67, 67))
    colourManager.setColour(ColourRole.Background, True, False, Theme.Light, Colour(163, 213, 255))
    colourManager.setColour(ColourRole.Background, True, False, Theme.Dark, Colour(80, 146, 255))
    colourManager.setColour(ColourRole.Border, False, False, Theme.Light, Colour(215, 237, 255))
    colourManager.setColour(ColourRole.Border, False, False, Theme.Dark, Colour(93, 103, 114))
    colourManager.setColour(ColourRole.Border, True, False, Theme.Light, Colour(135, 206, 255))
    colourManager.setColour(ColourRole.Border, True, False, Theme.Dark, Colour(93, 167, 255))
    colourManager.setColour(ColourRole.Background, False, True, Theme.Light, Colour(181, 213, 255))
    colourManager.setColour(ColourRole.Background, False, True, Theme.Dark, Colour(76, 126, 219))
    colourManager.setColour(ColourRole.Background, True, True, Theme.Light, Colour(193, 224, 255))
    colourManager.setColour(ColourRole.Background, True, True, Theme.Dark, Colour(84, 146, 255))
    colourManager.setColour(ColourRole.Border, False, True, Theme.Light, Colour(131, 182, 255))
    colourManager.setColour(ColourRole.Border, False, True, Theme.Dark, Colour(105, 157, 235))
    colourManager.setColour(ColourRole.Border, True, True, Theme.Light, Colour(153, 203, 255))
    colourManager.setColour(ColourRole.Border, True, True, Theme.Dark, Colour(103, 163, 255))
    globals()["currentThemeColourManager"] = colourManager


initThemeColours()


def getBorderColour(is_primary=False, is_highlight=False, is_tuple=False):
    border_colour = getThemeColour(
        colour_role=ColourRole.Border,
        is_primary=is_primary,
        is_highlight=is_highlight,
        theme=getTheme()
    )
    if is_tuple:
        return tuple(border_colour)
    else:
        return border_colour


def getBackgroundColour(is_primary=False, is_highlight=False, is_tuple=False):
    background_colour = getThemeColour(
        colour_role=ColourRole.Background,
        is_primary=is_primary,
        is_highlight=is_highlight,
        theme=getTheme()
    )
    if is_tuple:
        return tuple(background_colour)
    else:
        return background_colour


def getForegroundColour(is_primary=False, is_tuple=False):
    colour = getThemeColour(colour_role=ColourRole.Foreground, is_primary=is_primary, is_highlight=False,
                            theme=getTheme())
    if is_tuple:
        return tuple(colour)
    else:
        return colour
