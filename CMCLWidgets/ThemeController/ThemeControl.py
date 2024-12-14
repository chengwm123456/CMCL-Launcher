# -*- coding: utf-8 -*-
from .ThemeControlClasses import *


def setTheme(theme):
    globals()["currentTheme"] = theme


def getTheme():
    return globals().get("currentTheme", Theme.Light)


def setThemeColour(colour_role, is_primary, is_highlight, theme, colour):
    role_colours = globals()["currentThemeColours"].get(colour_role, {})
    role_colours.get(is_highlight, {})[theme] = colour
    globals()["currentThemeColours"][colour_role] = role_colours


def getThemeColour(colour_role, is_primary, is_highlight, theme):
    return globals().get("currentThemeColours", {}).get(colour_role, {}).get(is_highlight, {}).get(theme, (0, 0, 0))


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
    themeColours[ColourRole.Foreground] = foreHighlighs
    backHighlights = HighlightsDict()
    backNohColours = LightDarkDict()
    backNohColours[Theme.Light] = (253, 253, 253)
    backNohColours[Theme.Dark] = (67, 67, 67)
    backHighlights[False] = backNohColours
    backhColours = LightDarkDict()
    backhColours[Theme.Light] = (176, 224, 250)
    backhColours[Theme.Dark] = (142, 197, 252)
    backHighlights[True] = backhColours
    themeColours[ColourRole.Background] = backHighlights
    borderHighlights = HighlightsDict()
    borderNohColours = LightDarkDict()
    borderNohColours[Theme.Light] = (215, 220, 229)
    borderNohColours[Theme.Dark] = (134, 143, 150)
    borderHighlights[False] = borderNohColours
    borderhColours = LightDarkDict()
    borderhColours[Theme.Light] = (135, 206, 250)
    borderhColours[Theme.Dark] = (79, 172, 254)
    borderHighlights[True] = borderhColours
    themeColours[ColourRole.Border] = borderHighlights
    globals()["currentThemeColours"] = themeColours


setTheme(Theme.Light)
initThemeColours()


def getBorderColour(is_primary=False, is_highlight=False, is_tuple=False):
    border_colour = getThemeColour(
        colour_role=ColourRole.Border,
        is_primary=is_primary,
        is_highlight=is_highlight,
        theme=getTheme()
    )
    if is_tuple:
        return border_colour
    else:
        return Colour(*border_colour)


def getBackgroundColour(is_primary=False, is_highlight=False, is_tuple=False):
    background_colour = getThemeColour(
        colour_role=ColourRole.Background,
        is_primary=is_primary,
        is_highlight=is_highlight,
        theme=getTheme()
    )
    if is_tuple:
        return background_colour
    else:
        return Colour(*background_colour)


def getForegroundColour(is_primary=False, is_tuple=False):
    colour = getThemeColour(colour_role=ColourRole.Foreground, is_primary=is_primary, is_highlight=is_primary,
                            theme=getTheme())
    if is_tuple:
        return colour
    else:
        return QColor(*colour)
