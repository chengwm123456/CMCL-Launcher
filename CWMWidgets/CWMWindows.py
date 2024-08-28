# -*- coding: utf-8 -*-
from qframelesswindow import TitleBar
from .CWMThemeControl import *
from .CWMFramelessWindow import *
from ctypes import WinDLL


class RoundedWindow(RoundedFramelessMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleBar = TitleBar(self)
    
    def resizeEvent(self, a0):
        self.titleBar.resize(self.width(), self.titleBar.height())
        super().resizeEvent(a0)
        self.titleBar.resize(self.width(), self.titleBar.height())
        self.titleBar.raise_()


class RoundedDialogue(QDialog, RoundedFramelessWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleBar = TitleBar(self)
        self.titleBar.maxBtn.hide()
        self.titleBar.maxBtn.deleteLater()
        self.titleBar.minBtn.hide()
        self.titleBar.minBtn.deleteLater()
        self.setMaximizeEnabled(False)
        self.setResizeEnabled(False)
    
    def resizeEvent(self, a0):
        self.titleBar.resize(self.width(), self.titleBar.height())
        super().resizeEvent(a0)
        self.titleBar.resize(self.width(), self.titleBar.height())
        self.titleBar.raise_()


class RoundedMenu(QMenu):
    BORDER_RADIUS = 10
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""RoundedMenu{{
    background: white;
}}
RoundedMenu::item{{
    background: rgba({str(getBackgroundColour(tuple=True)).replace('(', '').replace(')', '')}, 0.6);
    color: rgba({str(getForegroundColour(tuple=True)).replace('(', '').replace(')', '')}, 0.6);
    border-radius: 6px;
    border: 1px solid rgba({str(getBorderColour(tuple=True)).replace('(', '').replace(')', '')}, 0.6);
    padding: 4px, 2px;
    margin: 3px;
    height: 30px;
}}
RoundedMenu::item:selected{{
    background: rgb({str(getBackgroundColour(tuple=True)).replace('(', '').replace(')', '')});
}}
RoundedMenu::item:selected, RoundedMenu::item:pressed{{
    border: 1px solid rgb({str(getBorderColour(highlight=True, tuple=True)).replace('(', '').replace(')', '')});
    color: rgb(0, 0, 0);
}}
RoundedMenu::item:pressed{{
    background: rgb({str(getBackgroundColour(highlight=True, tuple=True)).replace('(', '').replace(')', '')});
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
