# -*- coding: utf-8 -*-
import platform
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *
from qframelesswindow import TitleBar
from CMCLWidgets.ThemeController.ThemeControl import *
from .FramelessWindow import *

if platform.system().lower() == "windows":
    from ctypes import WinDLL, pointer, windll
    from ctypes.wintypes import RECT
    import win32con


class Window(FramelessWindow):
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


class MainWindow(FramelessMainWindow):
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


class RoundedWindow(MainWindow):
    BORDER_RADIUS = 10
    
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
                
                user32 = WinDLL("user32")
                user32.SetClassLongPtrW(int(self.winId()), win32con.GCL_STYLE,
                                        user32.GetClassLongPtrW(int(self.winId()),
                                                                win32con.GCL_STYLE) | 0x00020000)
            case "Darwin":
                pass
            case "Linux":
                pass
        # self.update()
    
    def event(self, a0, **kwargs):
        self.__updateWindowRegion()
        return super().event(a0)


class RoundedDialogue(QDialog, Window):
    BORDER_RADIUS = 10
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleBar.maxBtn.hide()
        self.titleBar.maxBtn.deleteLater()
        self.titleBar.minBtn.hide()
        self.titleBar.minBtn.deleteLater()
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowType.WindowMaximizeButtonHint)
        self.setResizeEnabled(False)
    
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
                
                user32 = WinDLL("user32")
                user32.SetClassLongPtrW(int(self.winId()), win32con.GCL_STYLE,
                                        user32.GetClassLongPtrW(int(self.winId()),
                                                                win32con.GCL_STYLE) | 0x00020000)
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
        self.__updateQSS()
    
    def __updateQSS(self):
        self.setStyleSheet(f"""RoundedMenu{{
            background: {"dark" if getTheme() == Theme.Dark else "white"};
        }}
        RoundedMenu::item{{
            background: rgba({str(getBackgroundColour(is_tuple=True)).replace('(', '').replace(')', '')}, 0.6);
            color: rgba({str(getForegroundColour(is_tuple=True)).replace('(', '').replace(')', '')}, 0.6);
            border-radius: 10px;
            border: 1px solid rgba({str(getBorderColour(is_tuple=True)).replace('(', '').replace(')', '')}, 0.6);
            padding: 4px 2px;
            margin: 3px;
            height: 30px;
        }}
        RoundedMenu::item:selected{{
            background: rgb({str(getBackgroundColour(is_tuple=True)).replace('(', '').replace(')', '')});
        }}
        RoundedMenu::item:selected, RoundedMenu::item:pressed{{
            border: 1px solid rgb({str(getBorderColour(is_highlight=True, is_tuple=True)).replace('(', '').replace(')', '')});
            color: rgb({str(getForegroundColour(is_tuple=True)).replace('(', '').replace(')', '')});
        }}
        RoundedMenu::item:pressed{{
            background: rgb({str(getBackgroundColour(is_highlight=True, is_tuple=True)).replace('(', '').replace(')', '')});
        }}
        """)
    
    def showEvent(self, a0):
        self.__updateRegion()
        super().showEvent(a0)
        self.__updateRegion()
        # Temp
        self.__updateQSS()
        # End:Temp
    
    def __updateRegion(self):
        match platform.system().lower():
            case "windows":
                WinDLL("user32").SetProcessDPIAware()
                dpiScaleRate = WinDLL("user32").GetDpiForWindow(int(self.winId())) / 96.0
                WinDLL("user32").SetWindowRgn(int(self.winId()),
                                              WinDLL("gdi32").CreateRoundRectRgn(0, 0, int(self.width() * dpiScaleRate),
                                                                                 int(self.height() * dpiScaleRate),
                                                                                 int(self.BORDER_RADIUS * dpiScaleRate),
                                                                                 int(self.BORDER_RADIUS * dpiScaleRate)),
                                              False)
                
                user32 = WinDLL("user32")
                user32.SetClassLongPtrW(int(self.winId()), win32con.GCL_STYLE,
                                        user32.GetClassLongPtrW(int(self.winId()),
                                                                win32con.GCL_STYLE) | 0x00020000)
            case "darwin":
                pass
            case "linux":
                pass
