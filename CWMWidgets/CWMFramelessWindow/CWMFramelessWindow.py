# -*- coding: utf-8 -*-
import platform

import win32con
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from qframelesswindow.utils.win32_utils import Taskbar

from .CWMFrameStructures import *
from .CWMFrameFunctions import *


class FramelessWindow(QWidget):
    def __init__(self, *__args):
        super().__init__(*__args)
        self.__ctypes = None
        self.__win32con = None
        self.__win32gui = None
        self.__objc = None
        self.__cocoa = None
        self.__nsWindow = None
        match platform.system().lower():
            case "windows":
                ctypes = __import__("ctypes")
                wintypes = __import__("ctypes.wintypes", fromlist=("ctypes",))
                
                class PWINDOWPOS(ctypes.Structure):
                    _fields_ = [
                        ('hWnd', wintypes.HWND),
                        ('hwndInsertAfter', wintypes.HWND),
                        ('x', ctypes.c_int),
                        ('y', ctypes.c_int),
                        ('cx', ctypes.c_int),
                        ('cy', ctypes.c_int),
                        ('flags', wintypes.UINT)
                    ]
                
                class NCCALCSIZE_PARAMS(ctypes.Structure):
                    _fields_ = [
                        ('rgrc', wintypes.RECT * 3),
                        ('lppos', ctypes.POINTER(PWINDOWPOS))
                    ]
                
                self.__ctypes = __import__("ctypes")
                self.__ctypes.PWINDOWPOS = PWINDOWPOS
                self.__ctypes.NCCLACSIZE_PARAMS = NCCALCSIZE_PARAMS
                self.__win32con = __import__("win32con")
                self.__win32con.CS_DROPSHADOW = 0x00020000
                self.__win32gui = __import__("win32gui")
            case "darwin":
                self.__objc = __import__("objc")
                self.__cocoa = __import__("Cocoa")
                self.__nsWindow = self.__objc.objc_object(c_void_p=self.winId().__int__()).window()
        self.setProperty("resizeEnabled", True)
        self.setProperty("maximizeEnabled", True)
        self.setProperty("minimizeEnabled", True)
        self.setProperty("systemTitleBarButtonVisible", True)
        self.__updateFrameless()
    
    def __updateFrameless(self):
        # TODO: test the compatibility on other platform
        # TODO: done the code of Linux.
        # TODO: check the spelling of MacOS
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
                user32 = WinDLL("user32")
                user32.SetClassLongPtrW(int(self.winId()), win32con.GCL_STYLE,
                                        user32.GetClassLongPtrW(int(self.winId()),
                                                                win32con.GCL_STYLE) | 0x00020000)
            case "darwin":
                self.__nsWindow.setHasShadow_(True)
            case "linux":
                pass
    
    def __updateWindowFrameless(self):
        if platform.system().lower() == "windows":
            self.__win32gui.SetWindowLong(
                int(self.winId()),
                self.__win32con.GWL_STYLE,
                self.__win32gui.GetWindowLong(int(self.winId()), self.__win32con.GWL_STYLE)
                | self.__win32con.WS_MINIMIZEBOX
                | self.__win32con.WS_MAXIMIZEBOX
                | self.__win32con.CS_DBLCLKS
                | self.__win32con.WS_CAPTION
                | self.__win32con.WS_THICKFRAME
            )
            if not self.property("maximizeEnabled"):
                self.__win32gui.SetWindowLong(
                    int(self.winId()),
                    self.__win32con.GWL_STYLE,
                    self.__win32gui.GetWindowLong(int(self.winId()),
                                                  self.__win32con.GWL_STYLE) & ~self.__win32con.WS_MINIMIZEBOX
                )
            if not self.property("minimizeEnabled"):
                self.__win32gui.SetWindowLong(
                    int(self.winId()),
                    self.__win32con.GWL_STYLE,
                    self.__win32gui.GetWindowLong(int(self.winId()), -16) & ~self.__win32con.WS_MAXIMIZEBOX
                )
    
    def __updateNSWindowFrameless(self):
        if platform.system().lower() == "darwin":
            self.__nsWindow.setStyleMask_(
                self.__nsWindow.styleMask() | self.__cocoa.NSFullSizeContentViewWindowMask
            )
            self.__nsWindow.setTitlebarAppearsTransparent_(True)
            
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
                close_button = self.__nsWindow.standardWindowButton_(self.__cocoa.NSWindowCloseButton)
                miniaturise_button = self.__nsWindow.standardWindowButton_(self.__cocoa.NSWindowMiniaturizeButton)
                zoom_button = self.__nsWindow.standardWindowButton_(self.__cocoa.NSWindowZoomButton)
                
                titlebar = zoom_button.superview()
                titlebar_height = titlebar.frame().size.height
                
                titlebar_spacing = miniaturise_button.frame().origin.x - close_button.frame().origin.x
                miniaturise_button_width = miniaturise_button.frame().size.width
                miniaturise_button_height = miniaturise_button.frame().size.height
                
                titlebar_centre = QRectF(0, 0, 75, titlebar_height).center()
                titlebar_centre.setY(titlebar_height - titlebar_centre.y())
                
                miniaturise_button_origin = self.__cocoa.NSPoint(titlebar_centre.x() - miniaturise_button_width // 2,
                                                                 titlebar_centre.y() - miniaturise_button_height // 2)
                close_button_origin = self.__cocoa.NSPoint(miniaturise_button_origin.x - titlebar_spacing,
                                                           miniaturise_button_origin.y)
                zoom_button_origin = self.__cocoa.NSPoint(miniaturise_button_origin.x + titlebar_spacing,
                                                          miniaturise_button_origin.y)
                
                miniaturise_button.setFrameOrigin_(miniaturise_button_origin)
                close_button.setFrameOrigin_(close_button_origin)
                zoom_button.setFrameOrigin_(zoom_button_origin)
    
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
        match eventType:
            case "windows_generic_MSG":
                msg = MSG.from_address(message.__int__())
                if not msg.hWnd:
                    return False, 0
                
                match msg.message:
                    case self.__win32con.WM_NCACTIVATE:
                        return True, self.__win32gui.DefWindowProc(msg.hWnd, msg.message, msg.wParam, -1)
                    case 132:
                        if self.property("resizeEnabled"):
                            pos = QCursor.pos() - QPoint(self.geometry().x(), self.geometry().y())
                            w, h = self.frameGeometry().width(), self.frameGeometry().height()
                            xw = getResizeBorderThickness(int(self.winId()), False)
                            yw = getResizeBorderThickness(int(self.winId()), True)
                            lx = pos.x() < xw
                            rx = pos.x() > w - xw
                            ty = pos.y() < yw
                            by = pos.y() > h - yw
                            if lx and ty:
                                return True, win32con.HTTOPLEFT
                            elif rx and by:
                                return True, win32con.HTBOTTOMRIGHT
                            elif rx and ty:
                                return True, win32con.HTTOPRIGHT
                            elif lx and by:
                                return True, win32con.HTBOTTOMLEFT
                            elif ty:
                                return True, win32con.HTTOP
                            elif by:
                                return True, win32con.HTBOTTOM
                            elif lx:
                                return True, win32con.HTLEFT
                            elif rx:
                                return True, win32con.HTRIGHT
                    case self.__win32con.WM_NCCALCSIZE:
                        if msg.wParam:
                            rect = self.__ctypes.cast(msg.lParam,
                                                      self.__ctypes.POINTER(
                                                          self.__ctypes.NCCLACSIZE_PARAMS)).contents.rgrc[
                                0]
                        else:
                            rect = self.__ctypes.cast(msg.lParam, self.__ctypes.POINTER(self.__ctypes.RECT)).contents
                        
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
                        if bool(msg.wParam):
                            self.update()
                        return True, 0 if not bool(msg.wParam) else win32con.WVR_VREDRAW
                result = super().nativeEvent(eventType, message)
                return result[0], result[1] or 0
        return super().nativeEvent(eventType, message)
    
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
