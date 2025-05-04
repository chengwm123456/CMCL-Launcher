# -*- coding: utf-8 -*-
import ctypes
import platform

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from ctypes import *

if platform.system().lower() == "windows":
    from ctypes.wintypes import *
    
    import win32api
    import win32con
    import win32gui
    import win32print
    from win32comext.shell import shellcon
    
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
    
    
    def isGreaterEqualVersion(version):
        return QOperatingSystemVersion.current() >= version
    
    
    class TaskBar:
        class TaskBarPosition:
            LEFT = 0
            TOP = 1
            RIGHT = 2
            BOTTOM = 3
            NOPOSITION = 4
        
        AUTO_HIDE_THICKNESS = 2
        
        class APPBARDATA(Structure):
            _fields_ = [
                ('cbSize', DWORD),
                ('hWnd', HWND),
                ('uCallbackMessage', UINT),
                ('uEdge', UINT),
                ('rc', RECT),
                ('lParam', LPARAM)
            ]
        
        @classmethod
        def isAutoHide(cls):
            appbarData = cls.APPBARDATA(sizeof(cls.APPBARDATA), 0, 0, 0, RECT(0, 0, 0, 0), 0)
            taskbarState = windll.shell32.SHAppBarMessage(shellcon.ABM_GETSTATE, byref(appbarData))
            return taskbarState == shellcon.ABS_AUTOHIDE
        
        @classmethod
        def getPosition(cls, hwnd):
            if isGreaterEqualVersion(QOperatingSystemVersion.Windows8_1):
                monitorInfo = getMonitorInfo(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
                if not monitorInfo:
                    return cls.TaskBarPosition.NOPOSITION
                monitor = RECT(*monitorInfo["Monitor"])
                appbarData = cls.APPBARDATA(sizeof(cls.APPBARDATA), 0, 0, 0, monitor, 0)
                for pos in [cls.TaskBarPosition.LEFT, cls.TaskBarPosition.TOP, cls.TaskBarPosition.RIGHT,
                            cls.TaskBarPosition.BOTTOM]:
                    appbarData.uEdge = pos
                    if windll.shell32.SHAppBarMessage(11, byref(appbarData)):
                        return pos
                
                return cls.TaskBarPosition.NOPOSITION
            
            appbarData = cls.APPBARDATA(sizeof(cls.APPBARDATA), win32gui.FindWindow("Shell_TrayWnd", None), 0, 0,
                                        RECT(0, 0, 0, 0), 0)
            if appbarData.hWnd:
                windowMonitor = win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
                if not windowMonitor:
                    return cls.TaskBarPosition.NOPOSITION
                taskbarMonitor = win32api.MonitorFromWindow(appbarData.hWnd, win32con.MONITOR_DEFAULTTOPRIMARY)
                if not taskbarMonitor:
                    return cls.TaskBarPosition.NOPOSITION
                if taskbarMonitor == windowMonitor:
                    windll.shell32.SHAppBarMessage(shellcon.ABM_GETTASKBARPOS, byref(appbarData))
                    return appbarData.uEdge
            return cls.TaskBarPosition.NOPOSITION


class FramelessWindow(QWidget):
    def __init__(self, *__args):
        super(FramelessWindow, self).__init__(*__args)
        self.__platform = __import__("platform")
        self.__ctypes = None
        self.__wintypes = None
        self.__win32con = None
        self.__win32gui = None
        self.__dwmapi = None
        self.__objc = None
        self.__cocoa = None
        self.__nsWindow = None
        self.__windowSystem = None
        self.__xcffib = None
        self.__xproto = None
        self.__pywayland = None
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
                os = __import__("os")
                self.__windowSystem = os.getenv("XDG_SESSION_TYPE").lower()
                match self.__windowSystem:
                    case "x11":
                        self.__xcffib = __import__("xcffib")
                        self.__xproto = __import__("xcffib.xproto", fromlist=("xcffib",))
                    case "wayland":
                        self.__pywayland = __import__("pywayland")
        self.setProperty("resizeEnabled", True)
        self.setProperty("systemTitleBarButtonVisible", True)
        self.__updateWindowFrameless()
    
    def __updateWindowFrameless(self):
        match self.__platform.system().lower():
            case "windows":
                self.__updateWin32Frameless()
                self.windowHandle().screenChanged.connect(self.__onScreenChanged)
            case "darwin":
                self.__updateNSWindowFrameless()
            case "linux":
                if self.__windowSystem == "x11":
                    self.__updateX11WindowFrameless()
                if self.__windowSystem == "wayland":
                    self.__updateWaylandWindowFrameless()
        self.__updateShadow()
        self.update()
        self.updateGeometry()
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
    
    def __updateWin32Frameless(self):
        if self.__platform.system().lower() == "windows":
            super(FramelessWindow, self).setWindowFlag(Qt.WindowType.FramelessWindowHint, False)
            super(FramelessWindow, self).setWindowFlags(self.windowFlags() & ~Qt.WindowType.FramelessWindowHint)
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
    
    def __updateX11WindowFrameless(self):
        if self.__platform.system().lower() == "linux":
            if self.__windowSystem == "x11":
                super(FramelessWindow, self).setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
                connection = self.__xcffib.connect()
                connection.core.ChangeWindowAttributes(int(self.winId()), self.__xproto.CW.OverrideRedirect, [0])
                connection.flush()
    
    def __updateWaylandWindowFrameless(self):
        if self.__platform.system().lower() == "linux":
            if self.__windowSystem == "wayland":
                super(FramelessWindow, self).setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
                # self.__pywayland.lib.wl_shell_surface.set_toplevel(self.__pywayland.wl_compositor)
    
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
        self.updateGeometry()
        if e.type() == 129:
            if not self.property("resizeEnabled"):
                self.setCursor(Qt.CursorShape.ArrowCursor)
                return super(FramelessWindow, self).event(e)
            if self.isMaximized():
                self.setCursor(Qt.CursorShape.ArrowCursor)
                return super(FramelessWindow, self).event(e)
            pos = QCursor.pos() - self.mapToGlobal(QPoint(0, 0))
            verBorder = max(self.frameGeometry().x() - self.geometry().x(),
                            self.frameGeometry().y() - self.geometry().y())
            horBorder = max(self.frameGeometry().x() - self.geometry().x(),
                            self.frameGeometry().y() - self.geometry().y())
            if 0 <= pos.x() <= verBorder:
                if 0 <= pos.y() <= horBorder:
                    self.setCursor(Qt.CursorShape.SizeFDiagCursor)
                elif self.height() - horBorder <= pos.y() <= self.height():
                    self.setCursor(Qt.CursorShape.SizeBDiagCursor)
                else:
                    self.setCursor(Qt.CursorShape.SizeHorCursor)
            elif self.width() - verBorder <= pos.x() <= self.width():
                if 0 <= pos.y() <= horBorder:
                    self.setCursor(Qt.CursorShape.SizeBDiagCursor)
                elif self.height() - horBorder <= pos.y() <= self.height():
                    self.setCursor(Qt.CursorShape.SizeFDiagCursor)
                else:
                    self.setCursor(Qt.CursorShape.SizeHorCursor)
            elif 0 <= pos.y() <= horBorder or self.height() - horBorder <= pos.y() <= self.height():
                self.setCursor(Qt.CursorShape.SizeVerCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
        if e.type() == QEvent.Type.MouseButtonPress:
            if not self.property("resizeEnabled"):
                return super(FramelessWindow, self).event(e)
            if self.isMaximized():
                return super(FramelessWindow, self).event(e)
            if e.button() == Qt.MouseButton.LeftButton:
                pos = QCursor.pos() - self.mapToGlobal(QPoint(0, 0))
                verBorder = max(self.frameGeometry().x() - self.geometry().x(),
                                self.frameGeometry().y() - self.geometry().y())
                horBorder = max(self.frameGeometry().x() - self.geometry().x(),
                                self.frameGeometry().y() - self.geometry().y())
                if 0 <= pos.x() <= verBorder:
                    if 0 <= pos.y() <= horBorder:
                        self.windowHandle().startSystemResize(Qt.Edge.LeftEdge | Qt.Edge.TopEdge)
                    elif self.height() - horBorder <= pos.y() <= self.height():
                        self.windowHandle().startSystemResize(Qt.Edge.LeftEdge | Qt.Edge.BottomEdge)
                    else:
                        self.windowHandle().startSystemResize(Qt.Edge.LeftEdge)
                elif self.width() - verBorder <= pos.x() <= self.width():
                    if 0 <= pos.y() <= horBorder:
                        self.windowHandle().startSystemResize(Qt.Edge.RightEdge | Qt.Edge.TopEdge)
                    elif self.height() - horBorder <= pos.y() <= self.height():
                        self.windowHandle().startSystemResize(Qt.Edge.RightEdge | Qt.Edge.BottomEdge)
                    else:
                        self.windowHandle().startSystemResize(Qt.Edge.RightEdge)
                elif 0 <= pos.y() <= horBorder:
                    self.windowHandle().startSystemResize(Qt.Edge.TopEdge)
                elif self.height() - horBorder <= pos.y() <= self.height():
                    self.windowHandle().startSystemResize(Qt.Edge.BottomEdge)
        return super(FramelessWindow, self).event(e)
    
    def paintEvent(self, a0):
        self.__updateNSWindowFrameless()
        self.update()
        self.updateGeometry()
        super(FramelessWindow, self).paintEvent(a0)
        self.update()
        self.updateGeometry()
        self.__updateNSWindowFrameless()
    
    def resizeEvent(self, a0):
        self.__updateNSWindowTitleBarRect()
        self.update()
        super(FramelessWindow, self).resizeEvent(a0)
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
                winMsg = self.__wintypes.MSG.from_address(message.__int__())
                if not winMsg.hWnd:
                    return False, 0
                
                match winMsg.message:
                    case self.__win32con.WM_NCACTIVATE:
                        return True, self.__win32gui.DefWindowProc(winMsg.hWnd, winMsg.message, winMsg.wParam, -1)
                    case self.__win32con.WM_NCCALCSIZE:
                        match bool(winMsg.wParam):
                            case True:
                                rect = self.__ctypes.cast(
                                    winMsg.lParam,
                                    self.__ctypes.POINTER(self.__wintypes.NCCLACSIZE_PARAMS)
                                ).contents.rgrc[0]
                            case False | _:
                                rect = self.__ctypes.cast(
                                    winMsg.lParam,
                                    self.__wintypes.LPRECT
                                ).contents
                        
                        if isMaximized(winMsg.hWnd) and not isFullScreen(winMsg.hWnd):
                            bx = getSystemMetrics(int(winMsg.hWnd), win32con.SM_CYSIZEFRAME, True) + getSystemMetrics(
                                int(winMsg.hWnd), 92,
                                True)
                            by = getSystemMetrics(int(winMsg.hWnd), win32con.SM_CXSIZEFRAME, False) + getSystemMetrics(
                                int(winMsg.hWnd), 92,
                                False)
                            rect.top += by
                            rect.bottom -= by
                            rect.left += bx
                            rect.right -= bx
                        
                        if (isMaximized(winMsg.hWnd) or isFullScreen(winMsg.hWnd)) and TaskBar.isAutoHide():
                            position = TaskBar.getPosition(winMsg.hWnd)
                            if position == TaskBar.TaskBarPosition.TOP:
                                rect.top += TaskBar.AUTO_HIDE_THICKNESS
                            elif position == TaskBar.TaskBarPosition.BOTTOM:
                                rect.bottom -= TaskBar.AUTO_HIDE_THICKNESS
                            elif position == TaskBar.TaskBarPosition.LEFT:
                                rect.left += TaskBar.AUTO_HIDE_THICKNESS
                            elif position == TaskBar.TaskBarPosition.RIGHT:
                                rect.right -= TaskBar.AUTO_HIDE_THICKNESS
                        
                        if bool(winMsg.wParam):
                            self.update()
                        return True, 0 if not bool(winMsg.wParam) else self.__win32con.WVR_VREDRAW
                result = super(FramelessWindow, self).nativeEvent(eventType, message)
                return result[0], result[1] or 0
            case b"xcb_generic_event_t", "linux":
                return False, 0
        return super(FramelessWindow, self).nativeEvent(eventType, message)
    
    def setWindowFlag(self, flag, on=True):
        super(FramelessWindow, self).setWindowFlag(flag, on)
        self.__updateWindowFrameless()
    
    def setWindowFlags(self, flags):
        super(FramelessWindow, self).setWindowFlags(flags)
        self.__updateWindowFrameless()
    
    def resizeEnabled(self):
        return self.property("resizeEnabled")
    
    def setResizeEnabled(self, value):
        if value in [True, False, 1, 0]:
            self.setProperty("resizeEnabled", bool(value))
        else:
            raise TypeError(f"'{type(value)}' object cannot be interpreted as a bool.")
        self.__updateWindowFrameless()
    
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
        self.__updateWindowFrameless()


class FramelessMainWindow(QMainWindow, FramelessWindow):
    pass
