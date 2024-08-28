# -*- coding: utf-8 -*-
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from enum import Enum


class Theme(Enum):
    Light = "Light"
    Dark = "Dark"


currentTheme = Theme.Light


def getBorderColour(primary=False, highlight=False, tuple=False):
    match currentTheme:
        case Theme.Light:
            if tuple:
                return (135, 206, 235) if highlight else (230, 230, 230)
            else:
                return QColor(135, 206, 235) if highlight else QColor(230, 230, 230)


def getBackgroundColour(primary=False, highlight=False, tuple=False):
    match currentTheme:
        case Theme.Light:
            if tuple:
                return (176, 224, 230) if highlight else (253, 253, 253)
            else:
                return QColor(176, 224, 230) if highlight else QColor(253, 253, 253)


def getForegroundColour(primary=True, tuple=False):
    match currentTheme:
        case Theme.Light:
            if tuple:
                return (0, 0, 0)
            else:
                return QColor(0, 0, 0)
        case Theme.Dark:
            if tuple:
                return (255, 255, 255)
            else:
                return QColor(0, 0, 0)
