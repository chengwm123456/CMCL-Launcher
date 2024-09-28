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
        self.__win32gui = None
        self.__objc = None
        self.__cocoa = None
        self.__nsWindow = None
        match platform.system().lower():
            case "windows":
                self.__win32gui = __import__("win32gui")
            case "darwin":
                self.__objc = __import__("objc")
                self.__cocoa = __import__("Cocoa")
                self.__nsWindow = self.__objc.objc_object(c_void_p=self.winId().__int__()).view()
        self.setProperty("resizeEnabled", True)
        self.setProperty("maximizeEnabled", True)
        self.setProperty("minimizeEnabled", True)
        self.setProperty("systemTitleBarButtonVisible", True)
        self.__updateFrameless()
    
    def __updateFrameless(self):
        match platform.system().lower():
            case "windows":
                self.__updateWindowFrameless()
            case "darwin":
                self.__updateNSWindowFrameless()
            case "linux":
                self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowMinMaxButtonsHint)
        self.__updateShadow()
        self.windowHandle().screenChanged.connect(self.__onScreenChanged)
    
    def __updateShadow(self):
        match platform.system().lower():
            case "windows":
                pass
            case "darwin":
                self.__nsWindow.setHasShadow_(True)
            case "linux":
                pass
    
    def __updateWindowFrameless(self):
        if platform.system().lower() == "windows":
            self.__win32gui.SetWindowLong(
                int(self.winId()),
                -16,
                self.__win32gui.GetWindowLong(int(self.winId()), -16)
                | 0x00010000
                | 0x00020000
                | 0x00C00000
                | 0x00080000
                | 0x00040000
            )
            if not self.property("maximizeEnabled"):
                self.__win32gui.SetWindowLong(
                    int(self.winId()),
                    -16,
                    self.__win32gui.GetWindowLong(int(self.winId()), -16) & ~0x00010000
                )
            if not self.property("minimizeEnabled"):
                self.__win32gui.SetWindowLong(
                    int(self.winId()),
                    -16,
                    self.__win32gui.GetWindowLong(int(self.winId()), -16) & ~0x00020000
                )
    
    def __updateNSWindowFrameless(self):
        if platform.system().lower() == "darwin":
            self.__nsWindow.setStyleMask_(
                self.__nsWindow.styleMask() | self.__cocoa.NSFullSizeContentViewWindowMask
            )
            self.__nsWindow.setTitleBarAppearsTransparent_(True)
            
            self.__nsWindow.setMovableByWindowBackground_(False)
            self.__nsWindow.setMovable_(False)
            
            self.__nsWindow.setTitleVisibility(self.__cocoa.NSWindowTitleHidden)
            self.__updateNSWindowTitleBar()
    
    def __updateNSWindowTitleBar(self):
        if platform.system().lower() == "darwin":
            self.__nsWindow.setShowsToolbarButton_(self.systemTitleBarButtonVisible())
            
            self.__nsWindow.standardWindowButton_(self.__cocoa.NSWindowCloseButton).setHidden_(
                not self.systemTitleBarButtonVisible())
            self.__nsWindow.standardWindowButton_(self.__cocoa.NSWindowZoomButton).setHidden_(
                not self.systemTitleBarButtonVisible())
            self.__nsWindow.standardWindowButton_(self.__cocoa.NSWindowMiniaturizeButton).setHidden_(
                not self.systemTitleBarButtonVisible())
            self.__updateNSWindowTitleBarRect()
    
    def __updateNSWindowTitleBarRect(self):
        if platform.system().lower() == "darwin":
            if self.systemTitleBarButtonVisible():
                left_button = self.__nsWindow.standardWindowButton_(self.__cocoa.NSWindowCloseButton)
                middle_button = self.__nsWindow.standardWindowButton_(self.__cocoa.NSWindowMiniaturizeButton)
                right_button = self.__nsWindow.standardWindowButton_(self.__cocoa.NSWindowZoomButton)
                
                title_bar = right_button.superview()
                title_bar_height = title_bar.frame().size.height
                
                spacing = middle_button.frame().origin.x - left_button.frame().origin.x
                width = middle_button.frame().size.width
                height = middle_button.frame().size.height
                
                centre = QRectF(0, 0, 75, title_bar_height).center()
                centre.setY(title_bar_height - centre.y())
                
                centre_origin = self.__cocoa.NSPoint(centre.x() - width // 2, centre.y() - height // 2)
                left_origin = self.__cocoa.NSPoint(centre_origin.x - spacing, centre_origin.y)
                right_origin = self.__cocoa.NSPoint(centre_origin.x + spacing, centre_origin.y)
                
                middle_button.setFrameOrigin_(centre_origin)
                left_button.setFrameOrigin_(left_origin)
                right_button.setFrameOrigin_(right_origin)
    
    def __onScreenChanged(self):
        match platform.system().lower():
            case "windows":
                self.__win32gui.SetWindowPos(int(self.windowHandle().winId()), None, 0, 0, 0, 0,
                                             win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_FRAMECHANGED)
            case "darwin":
                pass
            case "linux":
                pass
    
    def paintEvent(self, a0):
        self.__updateNSWindowFrameless()
        super().paintEvent(a0)
        self.__updateNSWindowFrameless()
    
    def resizeEvent(self, a0):
        self.__updateNSWindowTitleBarRect()
        super().resizeEvent(a0)
        self.__updateNSWindowTitleBarRect()
    
    def changeEvent(self, a0):
        if platform.system().lower() == "darwin":
            match a0.type():
                case QEvent.Type.WindowStateChange:
                    self.__updateNSWindowFrameless()
                    
                    QTimer.singleShot(1, self.__updateNSWindowTitleBarRect)
                case QEvent.Type.Resize:
                    self.__updateNSWindowTitleBarRect()
    
    def nativeEvent(self, eventType, message):
        msg = MSG.from_address(message.__int__())
        if not msg.hWnd:
            return False, 0
        
        match msg.message:
            case 134:
                return True, self.__win32gui.DefWindowProc(msg.hWnd, msg.message, msg.wParam, -1)
            case win32con.WM_PAINT:
                self.repaint()
            case 132:
                if self.property("resizeEnabled"):
                    pos = QCursor.pos() - self.pos()
                    w, h = self.width(), self.height()
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
                return True, 0 if not msg.wParam else 768
        return False, 0
    
    def resizeEnabled(self):
        return self.property("resizeEnabled")
    
    def setResizeEnabled(self, value):
        if value in [True, False, 1, 0]:
            self.setProperty("resizeEnabled", bool(value))
        else:
            raise TypeError(f"'{type(value)}' object cannot be interpreted as a bool.")
        self.__updateFrameless()
    
    def maximizeEnabled(self):
        return self.property("maximizeEnabled")
    
    def setMaximizeEnabled(self, value):
        if value in [True, False, 1, 0]:
            self.setProperty("maximizeEnabled", bool(value))
        else:
            raise TypeError(f"'{type(value)}' object cannot be interpreted as a bool.")
        self.__updateFrameless()
    
    def minimizeEnabled(self):
        return self.property("minimizeEnabled")
    
    def setMinimizeEnabled(self, value):
        if value in [True, False, 1, 0]:
            self.setProperty("minimizeEnabled", bool(value))
        else:
            raise TypeError(f"'{type(value)}' object cannot be interpreted as a bool.")
        self.__updateFrameless()
    
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
        self.__updateFrameless()
    
    def childEvent(self, *args):
        super().childEvent(*args)
        self.__updateFrameless()


class FramelessMainWindow(QMainWindow, FramelessWindow):
    pass
