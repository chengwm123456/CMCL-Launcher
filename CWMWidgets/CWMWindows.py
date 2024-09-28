# -*- coding: utf-8 -*-
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from qframelesswindow import TitleBar
from .CWMThemeControl import *
from .CWMFramelessWindow import *
from ctypes import WinDLL, pointer, windll
from ctypes.wintypes import RECT
import platform


class RoundedWindow(FramelessMainWindow):
    BORDER_RADIUS = 10
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleBar = TitleBar(self)
    
    def resizeEvent(self, a0):
        if hasattr(self, "titleBar"):
            self.titleBar.resize(self.width(), self.titleBar.height())
        super().resizeEvent(a0)
        if hasattr(self, "titleBar"):
            self.titleBar.resize(self.width(), self.titleBar.height())
            self.titleBar.raise_()
    
    def __getCurrentDpiScaleRate(self):
        match platform.system():
            case "Windows":
                windll.user32.SetProcessDPIAware()
                return windll.user32.GetDpiForWindow(int(self.winId())) / 96.0
            case "Darwin":
                return 1
            case "Linux":
                return 1
    
    def __updateWindowRegion(self):
        match platform.system():
            case "Windows":
                rect = RECT()
                windll.user32.GetWindowRect(int(self.winId()), pointer(rect))
                dpiScaleRate = self.__getCurrentDpiScaleRate()
                windll.user32.SetWindowRgn(int(self.winId()),
                                           windll.gdi32.CreateRoundRectRgn(
                                               0,
                                               0,
                                               (rect.right - rect.left),
                                               (rect.bottom - rect.top),
                                               int(self.BORDER_RADIUS * dpiScaleRate),
                                               int(self.BORDER_RADIUS * dpiScaleRate)
                                           ),
                                           False)
            case "Darwin":
                pass
            case "Linux":
                pass
        # self.update()
    
    def event(self, a0, **kwargs):
        self.__updateWindowRegion()
        return super().event(a0)


class RoundedDialogue(QDialog, FramelessWindow):
    BORDER_RADIUS = 10
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleBar = TitleBar(self)
        self.titleBar.maxBtn.hide()
        self.titleBar.maxBtn.deleteLater()
        self.titleBar.minBtn.hide()
        self.titleBar.minBtn.deleteLater()
        self.setMaximizeEnabled(False)
        self.setResizeEnabled(False)
    
    def resizeEvent(self, a0, **kwargs):
        if hasattr(self, "titleBar"):
            self.titleBar.resize(self.width(), self.titleBar.height())
        super().resizeEvent(a0)
        if hasattr(self, "titleBar"):
            self.titleBar.resize(self.width(), self.titleBar.height())
            self.titleBar.raise_()
    
    def __getCurrentDpiScaleRate(self):
        match platform.system():
            case "Windows":
                windll.user32.SetProcessDPIAware()
                return windll.user32.GetDpiForWindow(int(self.winId())) / 96.0
            case "Darwin":
                return 1
            case "Linux":
                return 1
    
    def __updateWindowRegion(self):
        match platform.system():
            case "Windows":
                rect = RECT()
                windll.user32.GetWindowRect(int(self.winId()), pointer(rect))
                dpiScaleRate = self.__getCurrentDpiScaleRate()
                windll.user32.SetWindowRgn(int(self.winId()),
                                           windll.gdi32.CreateRoundRectRgn(
                                               0,
                                               0,
                                               (rect.right - rect.left),
                                               (rect.bottom - rect.top),
                                               int(self.BORDER_RADIUS * dpiScaleRate),
                                               int(self.BORDER_RADIUS * dpiScaleRate)
                                           ),
                                           False)
            case "Darwin":
                pass
            case "Linux":
                pass
    
    def event(self, a0, **kwargs):
        self.__updateWindowRegion()
        return super().event(a0)


class RoundedMenu(QMenu):
    BORDER_RADIUS = 10
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""RoundedMenu{{
    background: {"dark" if getTheme() == Theme.Dark else "white"};
}}
RoundedMenu::item{{
    background: rgba({str(getBackgroundColour(is_tuple=True)).replace('(', '').replace(')', '')}, 0.6);
    color: rgba({str(getForegroundColour(is_tuple=True)).replace('(', '').replace(')', '')}, 0.6);
    border-radius: 6px;
    border: 1px solid rgba({str(getBorderColour(is_tuple=True)).replace('(', '').replace(')', '')}, 0.6);
    padding: 4px, 2px;
    margin: 3px;
    height: 30px;
}}
RoundedMenu::item:selected{{
    background: rgb({str(getBackgroundColour(is_tuple=True)).replace('(', '').replace(')', '')});
}}
RoundedMenu::item:selected, RoundedMenu::item:pressed{{
    border: 1px solid rgb({str(getBorderColour(highlight=True, is_tuple=True)).replace('(', '').replace(')', '')});
    color: rgb({str(getForegroundColour(is_tuple=True)).replace('(', '').replace(')', '')});
}}
RoundedMenu::item:pressed{{
    background: rgb({str(getBackgroundColour(highlight=True, is_tuple=True)).replace('(', '').replace(')', '')});
}}
""")
    
    def showEvent(self, a0):
        super().showEvent(a0)
        WinDLL("user32").SetProcessDPIAware()
        dpiScaleRate = WinDLL("user32").GetDpiForWindow(int(self.winId())) / 96.0
        WinDLL("user32").SetWindowRgn(int(self.winId()),
                                      WinDLL("gdi32").CreateRoundRectRgn(0, 0, int(self.width() * dpiScaleRate),
                                                                         int(self.height() * dpiScaleRate),
                                                                         int(self.BORDER_RADIUS * dpiScaleRate),
                                                                         int(self.BORDER_RADIUS * dpiScaleRate)),
                                      False)
