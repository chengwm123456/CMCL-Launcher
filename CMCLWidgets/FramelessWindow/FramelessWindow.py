# -*- coding: utf-8 -*-
import platform

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from qframelesswindow.utils.win32_utils import Taskbar

from ctypes import *

import win32api
import win32con
import win32gui
import win32print

from PyQt6.QtGui import QGuiApplication


def isMaximized(hwnd):
    if not hwnd:
        return False
    
    windowPlacement = win32gui.GetWindowPlacement(int(hwnd))
    
    if not windowPlacement:
        return False
    
    return windowPlacement[1] == win32con.SW_MAXIMIZE


def isFullScreen(hwnd):
    if not hwnd:
        return False
    
    windowRect = win32gui.GetWindowRect(int(hwnd))
    if not windowRect:
        return False
    
    monitorInfo = getMonitorInfo(int(hwnd), win32con.MONITOR_DEFAULTTOPRIMARY)
    if not monitorInfo:
        return False
    
    monitorRect = monitorInfo["Monitor"]
    return all(i == j for i, j in zip(windowRect, monitorRect))


def getMonitorInfo(hwnd, dwFlags):
    monitor = win32api.MonitorFromWindow(int(hwnd), dwFlags)
    if not monitor:
        return
    
    return win32api.GetMonitorInfo(monitor)


def getResizeBorderThickness(hwnd, horizontal=True):
    window = findWindow(int(hwnd))
    if not window:
        return 0
    
    frame = 33 if horizontal else 32
    thickness = getSystemMetrics(int(hwnd), frame, horizontal) + getSystemMetrics(int(hwnd), 92, horizontal)
    if thickness:
        return int(thickness)
    
    return round(8 * window.devicePixelRatio() if IsCompositionEnabled() else 4 * window.devicePixelRatio())


def getSystemMetrics(hwnd, index, horizontal=True):
    if not hasattr(windll.user32, "GetSystemMetricsForDpi"):
        return win32api.GetSystemMetrics(index)
    
    return windll.user32.GetSystemMetricsForDpi(index, int(getMetricsDpi(hwnd, horizontal)))


def getMetricsDpi(hwnd, horizontal=True):
    if hasattr(windll.user32, "GetDpiForWindow"):
        return windll.user32.GetDpiForWindow(int(hwnd))
    
    hdc = win32gui.GetDC(int(hwnd))
    if not hdc:
        return 96
    dpiX, dpiY = win32print.GetDeviceCaps(hdc, win32con.LOGPIXELSX), win32print.GetDeviceCaps(hdc,
                                                                                              win32con.LOGPIXELSY)
    win32gui.ReleaseDC(int(hwnd), hdc)
    if dpiX and not horizontal:
        return dpiX
    if dpiY and horizontal:
        return dpiY
    
    return 96


def getWindowDpi(hwnd):
    windll.user32.SetProcessDPIAware()
    return windll.user32.GetDpiForWindow(int(hwnd)) / 96.0


def getSystemDpi():
    windll.user32.SetProcessDPIAware()
    return windll.user32.GetDpiForSystem() / 96.0


def findWindow(hwnd):
    if not hwnd:
        return
    
    topWindows = QGuiApplication.topLevelWindows()
    if not topWindows:
        return
    
    for topWindow in topWindows:
        if topWindow and int(topWindow.winId()) == int(hwnd):
            return topWindow


def IsCompositionEnabled():
    bResult = c_int(0)
    windll.dwmapi.DwmIsCompositionEnabled(byref(bResult))
    return bool(bResult.value)


class FramelessWindow(QWidget):
    def __init__(self, *__args):
        super().__init__(*__args)
        self.__ctypes = None
        self.__wintypes = None
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
                self.__wintypes = __import__("ctypes.wintypes", fromlist=("ctypes",))
                self.__wintypes.PWINDOWPOS = PWINDOWPOS
                self.__wintypes.NCCLACSIZE_PARAMS = NCCALCSIZE_PARAMS
                self.__win32con = __import__("win32con")
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
                import ctypes
                class MARGINS(ctypes.Structure):
                    _fields_ = [
                        ("cxLeftWidth", ctypes.c_int),
                        ("cxRightWidth", ctypes.c_int),
                        ("cyTopHeight", ctypes.c_int),
                        ("cyBottomHeight", ctypes.c_int),
                    ]
                
                dwmapi = WinDLL("dwmapi")
                margins = MARGINS(1, 1, 1, 1)
                dwmapi.DwmExtendFrameIntoClientArea(int(self.winId()), ctypes.byref(margins))
            case "darwin":
                self.__nsWindow.setHasShadow_(True)
            case "linux":
                pass
    
    def __updateWindowFrameless(self):
        if platform.system().lower() == "windows":
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.FramelessWindowHint)
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
            case b"windows_generic_MSG":
                msg = self.__wintypes.MSG.from_address(message.__int__())
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
                            lx = pos.x() < xw // 2
                            rx = pos.x() > w + xw // 2
                            ty = pos.y() < yw
                            by = pos.y() > h
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
                        match bool(msg.wParam):
                            case True:
                                rect = self.__ctypes.cast(
                                    msg.lParam,
                                    self.__ctypes.POINTER(self.__wintypes.NCCLACSIZE_PARAMS)
                                ).contents.rgrc[0]
                            case False:
                                rect = self.__ctypes.cast(
                                    msg.lParam,
                                    self.__wintypes.LPRECT
                                ).contents
                            case _:
                                rect = self.__wintypes.RECT()
                        
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
                        return True, 0 if not bool(msg.wParam) else self.__win32con.WVR_VREDRAW
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
        if platform.system().lower() == "darwin":
            return self.property("systemTitleBarButtonVisible")
        return False
    
    def setSystemTitleBarButtonVisible(self, value):
        if platform.system().lower() == "darwin":
            if value in [True, False, 1, 0]:
                self.setProperty("systemTitleBarButtonVisible", bool(value))
            else:
                raise TypeError(f"'{type(value)}' object cannot be interpreted as a bool.")
        self.__updateFrameless()


class FramelessMainWindow(QMainWindow, FramelessWindow):
    pass
