# -*- coding: utf-8 -*-
from .ThemeControlClasses import *


def setTheme(theme):
    globals()["currentTheme"] = theme


def getTheme():
    return globals().get("currentTheme", Theme.Light)


def setThemeColour(colour_role, is_primary, is_highlight, theme, colour):
    role_colours = globals()["currentThemeColours"].get(colour_role, {})
    role_colours.get(is_highlight, {})[theme] = Colour(*colour)
    globals()["currentThemeColours"][colour_role] = role_colours


def getThemeColour(colour_role, is_primary, is_highlight, theme):
    return Colour(*(globals().get("currentThemeColours", {}).get(colour_role, {}).get(is_highlight, {}).get(theme,
                                                                                                            Colour(0, 0,
                                                                                                                   0))))


def initThemeColours():
    themeColours = ThemeColours()
    foreHighlighs = HighlightsDict()
    foreNohColours = LightDarkDict()
    foreNohColours[Theme.Light] = Colour(0, 0, 0)
    foreNohColours[Theme.Dark] = Colour(255, 255, 255)
    foreHighlighs[False] = foreNohColours
    forehColours = LightDarkDict()
    forehColours[Theme.Light] = Colour(0, 0, 0)
    forehColours[Theme.Dark] = Colour(255, 255, 255)
    foreHighlighs[True] = forehColours
    themeColours[ColourRole.Foreground] = foreHighlighs
    backHighlights = HighlightsDict()
    backNohColours = LightDarkDict()
    backNohColours[Theme.Light] = Colour(253, 253, 253)
    backNohColours[Theme.Dark] = Colour(67, 67, 67)
    backHighlights[False] = backNohColours
    backhColours = LightDarkDict()
    backhColours[Theme.Light] = Colour(176, 224, 250)
    backhColours[Theme.Dark] = Colour(142, 197, 252)
    backHighlights[True] = backhColours
    themeColours[ColourRole.Background] = backHighlights
    borderHighlights = HighlightsDict()
    borderNohColours = LightDarkDict()
    borderNohColours[Theme.Light] = Colour(215, 237, 255)
    borderNohColours[Theme.Dark] = Colour(134, 143, 165)
    borderHighlights[False] = borderNohColours
    borderhColours = LightDarkDict()
    borderhColours[Theme.Light] = Colour(135, 206, 255)
    borderhColours[Theme.Dark] = Colour(79, 172, 255)
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
