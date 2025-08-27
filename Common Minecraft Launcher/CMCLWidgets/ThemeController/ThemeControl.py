# -*- coding: utf-8 -*-
from .ThemeControlClasses import *


def setTheme(theme, animation=False):
    globals()["currentTheme"] = theme
    globals()["currentThemeColourManager"].toggleTheme(theme, animation)


def getTheme():
    return globals().get("currentTheme", Theme.Light)


def setThemeColour(colour_role, is_primary, is_highlight, theme, colour, animation=False):
    globals()["currentThemeColourManager"].setColour(colour_role, is_highlight, theme, colour, animation, getTheme())


def getThemeColour(colour_role, is_primary, is_highlight, theme=None):
    if theme == getTheme():
        theme = None
    return globals()["currentThemeColourManager"].colour(colour_role, is_highlight, theme)


def initThemeColours():
    colourManager = ColourManager()
    colourManager.setColour(ColourRole.Foreground, False, Theme.Light, Colour(0, 0, 0))
    colourManager.setColour(ColourRole.Foreground, False, Theme.Dark, Colour(255, 255, 255))
    colourManager.setColour(ColourRole.Foreground, True, Theme.Light, Colour(0, 0, 0))
    colourManager.setColour(ColourRole.Foreground, True, Theme.Dark, Colour(255, 255, 255))
    colourManager.setColour(ColourRole.Background, False, Theme.Light, Colour(253, 253, 253))
    colourManager.setColour(ColourRole.Background, False, Theme.Dark, Colour(67, 67, 67))
    colourManager.setColour(ColourRole.Background, True, Theme.Light, Colour(176, 224, 250))
    colourManager.setColour(ColourRole.Background, True, Theme.Dark, Colour(142, 197, 252))
    colourManager.setColour(ColourRole.Border, False, Theme.Light, Colour(215, 237, 255))
    colourManager.setColour(ColourRole.Border, False, Theme.Dark, Colour(134, 143, 165))
    colourManager.setColour(ColourRole.Border, True, Theme.Light, Colour(135, 206, 255))
    colourManager.setColour(ColourRole.Border, True, Theme.Dark, Colour(79, 172, 255))
    globals()["currentThemeColourManager"] = colourManager


initThemeColours()
setTheme(Theme.Light)


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
    colour = getThemeColour(colour_role=ColourRole.Foreground, is_primary=is_primary, is_highlight=is_primary,
                            theme=getTheme())
    if is_tuple:
        return tuple(colour)
    else:
        return colour
