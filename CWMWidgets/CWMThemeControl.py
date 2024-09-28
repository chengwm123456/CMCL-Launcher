# -*- coding: utf-8 -*-
from PyQt6.QtGui import *
from enum import Enum


class Theme(Enum):
    Light = "Light"
    Dark = "Dark"


def setTheme(theme):
    globals()["currentTheme"] = theme


def getTheme():
    return globals().get("currentTheme", Theme.Light)


setTheme(Theme.Light)


def getBorderColour(primary=False, highlight=False, is_tuple=False):
    match getTheme():
        case Theme.Light:
            result = (135, 206, 250) if highlight else (230, 230, 230)
            if is_tuple:
                return result
            else:
                return QColor(*result)
        case Theme.Dark:
            result = (79, 172, 254) if highlight else (134, 143, 150)
            if is_tuple:
                return result
            else:
                return QColor(*result)


def getBackgroundColour(primary=False, highlight=False, is_tuple=False):
    match getTheme():
        case Theme.Light:
            result = (176, 224, 250) if highlight else (253, 253, 253)
            if is_tuple:
                return result
            else:
                return QColor(*result)
        case Theme.Dark:
            result = (142, 197, 252) if highlight else (67, 67, 67)
            if is_tuple:
                return result
            else:
                return QColor(*result)


def getForegroundColour(primary=False, is_tuple=False):
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
