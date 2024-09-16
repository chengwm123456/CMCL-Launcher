# -*- coding: utf-8 -*-
import platform

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from qframelesswindow.utils.win32_utils import Taskbar

from .CWMFrameStructures import *
from .CWMFrameFunctions import *


class FramelessWindow(QWidget):
    BORDER_WIDTH = 5
    
    def __init__(self, *__args):
        super().__init__(*__args)
        self.__gdi32 = None
        self.__user32 = None
        self.__objc = None
        self.__cocoa = None
        self.__nsWindow = None
        match platform.system().lower():
            case "windows":
                self.__gdi32 = WinDLL("gdi32")
                self.__user32 = WinDLL("user32")
            case "darwin":
                self.__objc = __import__("objc")
                self.__cocoa = __import__("Cocoa")
                self.__nsWindow = self.__objc.objc_object(c_void_p=self.winId().__int__()).view()
        self.setProperty("resizeEnabled", True)
        self.setProperty("maximizeEnabled", True)
        self.setProperty("minimizeEnabled", True)
        self.setProperty("systemTitleBarButtonVisible", True)
        # self.w = WindowEffect(self)
        self.__updateWindowFrameless()
    
    def __updateWindowFrameless(self):
        try:
            match platform.system().lower():
                case "windows":
                    self.__user32.SetWindowLongPtrW(
                        int(self.winId()),
                        -16,
                        self.__user32.GetWindowLongPtrW(int(self.winId()), -16)
                        | 0x00010000
                        | 0x00020000
                        | 0x00C00000
                        | 0x00080000
                        | 0x00040000
                    )
                    if not self.property("maximizeEnabled"):
                        self.__user32.SetWindowLongPtrW(
                            int(self.winId()),
                            -16,
                            self.__user32.GetWindowLongPtrW(int(self.winId()), -16) & ~0x00010000
                        )
                    if not self.property("minimizeEnabled"):
                        self.__user32.SetWindowLongPtrW(
                            int(self.winId()),
                            -16,
                            self.__user32.GetWindowLongPtrW(int(self.winId()), -16) & ~0x00020000
                        )
                case "darwin":
                    self.__updateNSWindow()
                case "linux":
                    pass
            self.__updateWindowShadow()
            self.windowHandle().screenChanged.connect(self.__onScreenChanged)
        finally:
            self.update()
    
    def __updateWindowShadow(self):
        try:
            match platform.system().lower():
                case "windows":
                    pass
                case "darwin":
                    self.__nsWindow.setHasShadow_(True)
                case "linux":
                    pass
        finally:
            self.update()
    
    def __updateNSWindow(self):
        try:
            if platform.system().lower() == "darwin":
                self.__nsWindow.setStyleMask_(
                    self.__nsWindow.styleMask() | self.__cocoa.NSFullSizeContentViewWindowMask
                )
                self.__nsWindow.setTitleBarAppearsTransparent_(True)
                
                self.__nsWindow.setMovableByWindowBackground_(False)
                self.__nsWindow.setMovable_(False)
                
                self.__nsWindow.setTitleVisibility(self.__cocoa.NSWindowTitleHidden)
                self.__updateSystemTitleBarButton()
        finally:
            self.update()
    
    def __updateSystemTitleBarButton(self):
        try:
            if platform.system().lower() == "darwin":
                self.__nsWindow.setShowsToolbarButton_(self.systemTitleBarButtonVisible())
                
                self.__nsWindow.standardWindowButton_(self.__cocoa.NSWindowCloseButton).setHidden_(
                    not self.systemTitleBarButtonVisible())
                self.__nsWindow.standardWindowButton_(self.__cocoa.NSWindowZoomButton).setHidden_(
                    not self.systemTitleBarButtonVisible())
                self.__nsWindow.standardWindowButton_(self.__cocoa.NSWindowMiniaturizeButton).setHidden_(
                    not self.systemTitleBarButtonVisible())
                self.__updateSystemTitleBarButtonRect()
        finally:
            self.update()
    
    def __updateSystemTitleBarButtonRect(self):
        try:
            if platform.system().lower() == "darwin":
                if self.systemTitleBarButtonVisible():
                    leftButton = self.__nsWindow.standardWindowButton_(self.__cocoa.NSWindowCloseButton)
                    middleButton = self.__nsWindow.standardWindowButton_(self.__cocoa.NSWindowMiniaturizeButton)
                    rightButton = self.__nsWindow.standardWindowButton_(self.__cocoa.NSWindowZoomButton)
                    
                    titleBar = rightButton.superview()
                    titleBarHeight = titleBar.frame().size.height
                    
                    spacing = middleButton.frame().origin.x - leftButton.frame().origin.x
                    width = middleButton.frame().size.width
                    height = middleButton.frame().size.height
                    
                    centre = QRectF(0, 0, 75, titleBarHeight).center()
                    centre.setY(titleBarHeight - centre.y())
                    
                    centreOrigin = self.__cocoa.NSPoint(centre.x() - width // 2, centre.y() - height // 2)
                    leftOrigin = self.__cocoa.NSPoint(centreOrigin.x - spacing, centreOrigin.y)
                    rightOrigin = self.__cocoa.NSPoint(centreOrigin.x + spacing, centreOrigin.y)
                    
                    middleButton.setFrameOrigin_(centreOrigin)
                    leftButton.setFrameOrigin_(leftOrigin)
                    rightButton.setFrameOrigin_(rightOrigin)
        finally:
            self.update()
    
    def __onScreenChanged(self):
        try:
            match platform.system().lower():
                case "windows":
                    self.__user32.SetWindowPos(int(self.windowHandle().winId()), None, 0, 0, 0, 0,
                                               win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_FRAMECHANGED)
                case "darwin":
                    pass
                case "linux":
                    pass
        finally:
            self.update()
    
    def paintEvent(self, a0):
        self.__updateNSWindow()
        self.update()
    
    def resizeEvent(self, *args):
        self.__updateSystemTitleBarButtonRect()
        self.update()
        super().resizeEvent(*args)
        self.__updateSystemTitleBarButtonRect()
        self.update()
    
    def changeEvent(self, a0):
        if platform.system().lower() == "darwin":
            match a0.type():
                case QEvent.Type.WindowStateChange:
                    self.__updateNSWindow()
                    
                    QTimer.singleShot(1, self.__updateSystemTitleBarButtonRect)
                case QEvent.Type.Resize:
                    self.__updateSystemTitleBarButtonRect()
        self.update()
    
    def event(self, a0):
        self.update()
        return super().event(a0)
    
    def nativeEvent(self, eventType, message):
        msg = MSG.from_address(message.__int__())
        if not msg.hWnd:
            return super().nativeEvent(eventType, message)
        
        match msg.message:
            case 134:
                result = win32gui.DefWindowProc(msg.hWnd, msg.message, msg.wParam, -1)
                self.update()
                return bool(msg.wParam), result
            case 129:
                result = win32gui.DefWindowProc(msg.hWnd, msg.message, msg.wParam, -1)
                self.update()
                return bool(msg.wParam), result
            case 8:
                result = win32gui.DefWindowProc(msg.hWnd, msg.message, msg.wParam, -1)
                self.update()
                return bool(msg.wParam), result
            case 15:
                self.update()
            case 133:
                self.update()
            case 132:
                if self.property("resizeEnabled"):
                    pos = QCursor.pos() - self.pos()
                    w, h = self.frameGeometry().width(), self.frameGeometry().height()
                    bw = 0 if isMaximized(msg.hWnd) or isFullScreen(msg.hWnd) else self.BORDER_WIDTH
                    lx = pos.x() < bw
                    rx = pos.x() > w - bw
                    ty = pos.y() < bw
                    by = pos.y() > h - bw
                    if lx and ty:
                        return True, 13
                    elif rx and by:
                        return True, 17
                    elif rx and ty:
                        return True, 14
                    elif lx and by:
                        return True, 16
                    elif ty:
                        return True, 12
                    elif by:
                        return True, 15
                    elif lx:
                        return True, 10
                    elif rx:
                        return True, 11
            case 131:
                if msg.wParam:
                    rect = cast(msg.lParam, POINTER(NCCALCSIZE_PARAMS)).contents.rgrc[0]
                else:
                    rect = cast(msg.lParam, LPRECT).contents
                
                if isMaximized(msg.hWnd) and not isFullScreen(msg.hWnd):
                    bx = getResizeBorderThickness(msg.hWnd, True)
                    by = getResizeBorderThickness(msg.hWnd, False)
                    rect.top += by
                    rect.bottom -= by
                    rect.left += bx
                    rect.right -= bx
                
                if (isMaximized(msg.hWnd) or isFullScreen(msg.hWnd)) and Taskbar.isAutoHide():
                    position = Taskbar.getPosition(msg.hWnd)
                    if position == Taskbar.TOP:
                        rect.top += Taskbar.AUTO_HIDE_THICKNESS
                    elif position == Taskbar.BOTTOM:
                        rect.bottom -= Taskbar.AUTO_HIDE_THICKNESS
                    elif position == Taskbar.LEFT:
                        rect.left += Taskbar.AUTO_HIDE_THICKNESS
                    elif position == Taskbar.RIGHT:
                        rect.right -= Taskbar.AUTO_HIDE_THICKNESS
                return True, 0 if not msg.wParam else 256 | 512
        return False, 0
    
    def resizeEnabled(self):
        return self.property("resizeEnabled")
    
    def setResizeEnabled(self, value):
        if value in [True, False, 1, 0]:
            self.setProperty("resizeEnabled", bool(value))
        else:
            raise TypeError(f"'{type(value)}' object cannot be interpreted as a bool.")
        self.__updateWindowFrameless()
    
    def maximizeEnabled(self):
        return self.property("maximizeEnabled")
    
    def setMaximizeEnabled(self, value):
        if value in [True, False, 1, 0]:
            self.setProperty("maximizeEnabled", bool(value))
        else:
            raise TypeError(f"'{type(value)}' object cannot be interpreted as a bool.")
        self.__updateWindowFrameless()
    
    def minimizeEnabled(self):
        return self.property("minimizeEnabled")
    
    def setMinimizeEnabled(self, value):
        if value in [True, False, 1, 0]:
            self.setProperty("minimizeEnabled", bool(value))
        else:
            raise TypeError(f"'{type(value)}' object cannot be interpreted as a bool.")
        self.__updateWindowFrameless()
    
    def systemTitleBarButtonVisible(self):
        if platform.system() == "Darwin":
            return self.property("systemTitleBarButtonVisible")
        return False
    
    def setSystemTitleBarButtonVisible(self, value):
        if platform.system().lower() == "darwin":
            if value in [True, False, 1, 0]:
                self.setProperty("systemTitleBarButtonVisible", bool(value))
            else:
                raise TypeError(f"'{type(value)}' object cannot be interpreted as a bool.")
        self.__updateWindowFrameless()
    
    def childEvent(self, *args):
        super().childEvent(*args)
        self.__updateWindowFrameless()


class FramelessMainWindow(QMainWindow, FramelessWindow):
    pass
