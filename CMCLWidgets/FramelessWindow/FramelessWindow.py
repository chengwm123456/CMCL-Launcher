# -*- coding: utf-8 -*-
import platform

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from ctypes import *

if platform.system().lower() == "windows":
    from qframelesswindow.utils.win32_utils import Taskbar
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
        self.__platform = __import__("platform")
        self.__ctypes = None
        self.__wintypes = None
        self.__win32con = None
        self.__win32gui = None
        self.__dwmapi = None
        self.__objc = None
        self.__cocoa = None
        self.__nsWindow = None
        self.__xcffib = None
        self.__xproto = None
        match self.__platform.system().lower():
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
                
                class MARGINS(ctypes.Structure):
                    _fields_ = [
                        ("cxLeftWidth", ctypes.c_int),
                        ("cxRightWidth", ctypes.c_int),
                        ("cyTopHeight", ctypes.c_int),
                        ("cyBottomHeight", ctypes.c_int),
                    ]
                
                self.__ctypes = __import__("ctypes")
                self.__wintypes = __import__("ctypes.wintypes", fromlist=("ctypes",))
                self.__wintypes.PWINDOWPOS = PWINDOWPOS
                self.__wintypes.NCCLACSIZE_PARAMS = NCCALCSIZE_PARAMS
                self.__wintypes.MARGINS = MARGINS
                self.__win32con = __import__("win32con")
                self.__win32gui = __import__("win32gui")
                self.__dwmapi = ctypes.WinDLL("dwmapi")
            case "darwin":
                self.__objc = __import__("objc")
                self.__cocoa = __import__("Cocoa")
                self.__nsWindow = self.__objc.objc_object(c_void_p=self.winId().__int__()).window()
            case "linux":
                self.__xcffib = __import__("xcffib")
                self.__xproto = __import__("xcffib.xproto", fromlist=("xcffib",))
        self.setProperty("resizeEnabled", True)
        self.setProperty("systemTitleBarButtonVisible", True)
        self.__updateFrameless()
    
    def __updateFrameless(self):
        match self.__platform.system().lower():
            case "windows":
                self.__updateWindowFrameless()
                self.windowHandle().screenChanged.connect(self.__onScreenChanged)
            case "darwin":
                self.__updateNSWindowFrameless()
            case "linux":
                self.__updateXWindowFrameless()
        self.__updateShadow()
        self.update()
        self.setUpdatesEnabled(True)
    
    def __updateShadow(self):
        match self.__platform.system().lower():
            case "windows":
                margins = self.__wintypes.MARGINS(1, 1, 1, 1)
                self.__dwmapi.DwmExtendFrameIntoClientArea(int(self.winId()), self.__ctypes.byref(margins))
            case "darwin":
                self.__nsWindow.setHasShadow_(True)
            case "linux":
                pass
    
    def __updateWindowFrameless(self):
        if self.__platform.system().lower() == "windows":
            super().setWindowFlag(Qt.WindowType.FramelessWindowHint, False)
            super().setWindowFlags(self.windowFlags() & ~Qt.WindowType.FramelessWindowHint)
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
            if self.windowFlags() & Qt.WindowType.WindowMinimizeButtonHint != 16384:
                self.__win32gui.SetWindowLong(
                    int(self.winId()),
                    self.__win32con.GWL_STYLE,
                    self.__win32gui.GetWindowLong(
                        int(self.winId()),
                        self.__win32con.GWL_STYLE
                    ) & ~self.__win32con.WS_MINIMIZEBOX
                )
            else:
                self.__win32gui.SetWindowLong(
                    int(self.winId()),
                    self.__win32con.GWL_STYLE,
                    self.__win32gui.GetWindowLong(
                        int(self.winId()),
                        self.__win32con.GWL_STYLE
                    ) | self.__win32con.WS_MINIMIZEBOX
                )
            if self.windowFlags() & Qt.WindowType.WindowMaximizeButtonHint != 32768:
                self.__win32gui.SetWindowLong(
                    int(self.winId()),
                    self.__win32con.GWL_STYLE,
                    self.__win32gui.GetWindowLong(
                        int(self.winId()),
                        self.__win32con.GWL_STYLE
                    ) & ~self.__win32con.WS_MAXIMIZEBOX
                )
            else:
                self.__win32gui.SetWindowLong(
                    int(self.winId()),
                    self.__win32con.GWL_STYLE,
                    self.__win32gui.GetWindowLong(
                        int(self.winId()),
                        self.__win32con.GWL_STYLE
                    ) | self.__win32con.WS_MAXIMIZEBOX
                )
    
    def __updateNSWindowFrameless(self):
        if self.__platform.system().lower() == "darwin":
            self.__nsWindow.setStyleMask_(
                self.__nsWindow.styleMask() | self.__cocoa.NSWindowStyleMaskFullSizeContentView
            )
            self.__nsWindow.setTitlebarAppearsTransparent_(True)
            
            self.__nsWindow.setMovableByWindowBackground_(False)
            self.__nsWindow.setMovable_(False)
            
            self.__nsWindow.setTitleVisibility(self.__cocoa.NSWindowTitleHidden)
            self.__updateNSWindowTitleBar()
    
    def __updateNSWindowTitleBar(self):
        if self.__platform.system().lower() == "darwin":
            self.__nsWindow.setShowsToolbarButton_(self.systemTitleBarButtonVisible())
            
            self.__nsWindow.standardWindowButton_(self.__cocoa.NSWindowCloseButton).setHidden_(
                not self.systemTitleBarButtonVisible())
            self.__nsWindow.standardWindowButton_(self.__cocoa.NSWindowZoomButton).setHidden_(
                not self.systemTitleBarButtonVisible())
            self.__nsWindow.standardWindowButton_(self.__cocoa.NSWindowMiniaturizeButton).setHidden_(
                not self.systemTitleBarButtonVisible())
            self.__updateNSWindowTitleBarRect()
    
    def __updateNSWindowTitleBarRect(self):
        if self.__platform.system().lower() == "darwin":
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
    
    def __updateXWindowFrameless(self):
        if self.__platform.system().lower() == "linux":
            connection = self.__xcffib.connect()
            
            connection.core.ChangeWindowAttributes(int(self.winId()), self.__xproto.CW.OverrideRedirect, [1])
            connection.core.MapWindow(int(self.winId()))
            
            connection.flush()
    
    def __onScreenChanged(self):
        match self.__platform.system().lower():
            case "windows":
                self.__win32gui.SetWindowPos(int(self.windowHandle().winId()), None, 0, 0, 0, 0,
                                             win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_FRAMECHANGED)
            case "darwin":
                pass
            case "linux":
                pass
    
    def event(self, e):
        self.update()
        return super().event(e)
    
    def paintEvent(self, a0):
        self.__updateNSWindowFrameless()
        self.update()
        super().paintEvent(a0)
        self.update()
        self.__updateNSWindowFrameless()
    
    def resizeEvent(self, a0):
        self.__updateNSWindowTitleBarRect()
        self.update()
        super().resizeEvent(a0)
        self.update()
        self.__updateNSWindowTitleBarRect()
    
    def changeEvent(self, a0):
        if self.__platform.system().lower() == "darwin":
            match a0.type():
                case QEvent.Type.WindowStateChange:
                    self.__updateNSWindowFrameless()
                    
                    QTimer.singleShot(1, self.__updateNSWindowTitleBarRect)
                case QEvent.Type.Resize:
                    self.__updateNSWindowTitleBarRect()
    
    def nativeEvent(self, eventType, message):
        match eventType, self.__platform.system().lower():
            case b"windows_generic_MSG", "windows":
                winmsg = self.__wintypes.MSG.from_address(message.__int__())
                if not winmsg.hWnd:
                    return False, 0
                
                match winmsg.message:
                    case self.__win32con.WM_NCACTIVATE:
                        return True, self.__win32gui.DefWindowProc(winmsg.hWnd, winmsg.message, winmsg.wParam, -1)
                    case self.__win32con.WM_NCHITTEST:
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
                                return True, self.__win32con.HTTOPLEFT
                            elif rx and by:
                                return True, self.__win32con.HTBOTTOMRIGHT
                            elif rx and ty:
                                return True, self.__win32con.HTTOPRIGHT
                            elif lx and by:
                                return True, self.__win32con.HTBOTTOMLEFT
                            elif ty:
                                return True, self.__win32con.HTTOP
                            elif by:
                                return True, self.__win32con.HTBOTTOM
                            elif lx:
                                return True, self.__win32con.HTLEFT
                            elif rx:
                                return True, self.__win32con.HTRIGHT
                    case self.__win32con.WM_NCCALCSIZE:
                        match bool(winmsg.wParam):
                            case True:
                                rect = self.__ctypes.cast(
                                    winmsg.lParam,
                                    self.__ctypes.POINTER(self.__wintypes.NCCLACSIZE_PARAMS)
                                ).contents.rgrc[0]
                            case False | _:
                                rect = self.__ctypes.cast(
                                    winmsg.lParam,
                                    self.__wintypes.LPRECT
                                ).contents
                        
                        if isMaximized(winmsg.hWnd) and not isFullScreen(winmsg.hWnd):
                            bx = getSystemMetrics(int(winmsg.hWnd), win32con.SM_CYSIZEFRAME, True) + getSystemMetrics(
                                int(winmsg.hWnd), 92,
                                True)
                            by = getSystemMetrics(int(winmsg.hWnd), win32con.SM_CXSIZEFRAME, False) + getSystemMetrics(
                                int(winmsg.hWnd), 92,
                                False)
                            rect.top += by
                            rect.bottom -= by
                            rect.left += bx
                            rect.right -= bx
                        
                        if (isMaximized(winmsg.hWnd) or isFullScreen(winmsg.hWnd)) and Taskbar.isAutoHide():
                            position = Taskbar.getPosition(winmsg.hWnd)
                            if position == Taskbar.TOP:
                                rect.top += Taskbar.AUTO_HIDE_THICKNESS
                            elif position == Taskbar.BOTTOM:
                                rect.bottom -= Taskbar.AUTO_HIDE_THICKNESS
                            elif position == Taskbar.LEFT:
                                rect.left += Taskbar.AUTO_HIDE_THICKNESS
                            elif position == Taskbar.RIGHT:
                                rect.right -= Taskbar.AUTO_HIDE_THICKNESS
                        
                        if bool(winmsg.wParam):
                            self.update()
                        return True, 0 if not bool(winmsg.wParam) else self.__win32con.WVR_VREDRAW
                result = super().nativeEvent(eventType, message)
                return result[0], result[1] or 0
        return super().nativeEvent(eventType, message)
    
    def setWindowFlag(self, flag, on=True):
        super().setWindowFlag(flag, on)
        self.__updateFrameless()
    
    def setWindowFlags(self, flags):
        super().setWindowFlags(flags)
        self.__updateFrameless()
    
    def resizeEnabled(self):
        return self.property("resizeEnabled")
    
    def setResizeEnabled(self, value):
        if value in [True, False, 1, 0]:
            self.setProperty("resizeEnabled", bool(value))
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
