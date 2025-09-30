# -*- coding: utf-8 -*-
import platform

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

if platform.system().lower() == "windows":
    from .WindowsFunctions import *
    from .WindowsStructures import *


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
        self.setProperty("resizeEnabled", True)
        self.setProperty("systemTitleBarButtonVisible", True)
        self.setProperty("windowBorderAccentColour", QColor(0, 0, 0, 0))
        self.setProperty("borderAccentColourEnabled", False)
        match self.__platform.system().lower():
            case "windows":
                self.__ctypes = __import__("ctypes")
                self.__wintypes = __import__("ctypes.wintypes", fromlist=("ctypes",))
                self.__wintypes.WINDOWPOS = WINDOWPOS
                self.__wintypes.PWINDOWPOS = PWINDOWPOS
                self.__wintypes.NCCLACSIZE_PARAMS = NCCALCSIZE_PARAMS
                self.__wintypes.LPNCCLACSIZE_PARAMS = LPNCCALCSIZE_PARAMS
                self.__wintypes.MARGINS = MARGINS
                self.__win32con = __import__("win32con")
                self.__win32gui = __import__("win32gui")
                self.__dwmapi = ctypes.WinDLL("dwmapi")
                self.setProperty("windowBorderAccentColour", getSystemAccentColour())
            case "darwin":
                self.__objc = __import__("objc")
                self.__cocoa = __import__("Cocoa")
                self.__nsWindow = self.__objc.objc_object(c_void_p=self.winId().__int__()).window()
            case "linux":
                pass
        self.__updateWindowFrameless()
    
    def __updateWindowFrameless(self):
        match self.__platform.system().lower():
            case "windows":
                self.__updateWin32Frameless()
                self.windowHandle().screenChanged.connect(self.__onScreenChanged)
            case "darwin":
                self.__updateNSWindowFrameless()
            case "linux":
                self.__updateLinuxWindowFrameless()
        self.__updateShadow()
        self.update()
        self.updateGeometry()
        self.setUpdatesEnabled(True)
    
    def __updateShadow(self):
        match self.__platform.system().lower():
            case "windows":
                margins = self.__wintypes.MARGINS(-1, -1, -1, -1)
                self.__dwmapi.DwmExtendFrameIntoClientArea(int(self.winId()), self.__ctypes.byref(margins))
            case "darwin":
                self.__nsWindow.setHasShadow_(True)
            case "linux":
                pass
    
    def __updateWin32Frameless(self):
        if self.__platform.system().lower() == "windows":
            super(FramelessWindow, self).setWindowFlag(Qt.WindowType.FramelessWindowHint, False)
            self.__win32gui.SetWindowLong(
                int(self.winId()),
                self.__win32con.GWL_STYLE,
                self.__win32gui.GetWindowLong(int(self.winId()), self.__win32con.GWL_STYLE)
                | self.__win32con.CS_DBLCLKS
                | self.__win32con.WS_CAPTION
                | self.__win32con.WS_THICKFRAME
            )
            if self.windowFlags() & Qt.WindowType.WindowMinimizeButtonHint:
                self.__win32gui.SetWindowLong(
                    int(self.winId()),
                    self.__win32con.GWL_STYLE,
                    self.__win32gui.GetWindowLong(
                        int(self.winId()),
                        self.__win32con.GWL_STYLE
                    )
                ) | self.__win32con.WS_MINIMIZEBOX
            else:
                self.__win32gui.SetWindowLong(
                    int(self.winId()),
                    self.__win32con.GWL_STYLE,
                    self.__win32gui.GetWindowLong(
                        int(self.winId()),
                        self.__win32con.GWL_STYLE
                    ) & ~self.__win32con.WS_MINIMIZEBOX
                )
            if self.windowFlags() & Qt.WindowType.WindowMaximizeButtonHint:
                self.__win32gui.SetWindowLong(
                    int(self.winId()),
                    self.__win32con.GWL_STYLE,
                    self.__win32gui.GetWindowLong(
                        int(self.winId()),
                        self.__win32con.GWL_STYLE
                    ) | self.__win32con.WS_MAXIMIZEBOX
                )
            else:
                self.__win32gui.SetWindowLong(
                    int(self.winId()),
                    self.__win32con.GWL_STYLE,
                    self.__win32gui.GetWindowLong(
                        int(self.winId()),
                        self.__win32con.GWL_STYLE
                    ) & ~self.__win32con.WS_MAXIMIZEBOX
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
    
    def __updateLinuxWindowFrameless(self):
        super(FramelessWindow, self).setWindowFlag(Qt.WindowType.FramelessWindowHint)
        super(FramelessWindow, self).setWindowFlag(Qt.WindowType.WindowMinMaxButtonsHint)
    
    def __onScreenChanged(self):
        match self.__platform.system().lower():
            case "windows":
                self.__win32gui.SetWindowPos(int(self.windowHandle().winId()), None, 0, 0, 0, 0,
                                             win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_FRAMECHANGED)
            case "darwin":
                pass
            case "linux":
                pass
    
    def event(self, a0):
        self.update()
        self.updateGeometry()
        return super(FramelessWindow, self).event(a0)
    
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
        super().changeEvent(a0)
    
    def nativeEvent(self, eventType, message):
        match eventType:
            case b"windows_generic_MSG":
                winMsg = self.__wintypes.MSG.from_address(message.__int__())
                if not winMsg.hWnd:
                    return False, 0
                
                match winMsg.message:
                    case self.__win32con.WM_SETFOCUS:
                        if self.property("borderAccentColourEnabled"):
                            colour = self.windowBorderAccentColour()
                            colourref = DWORD(
                                colour.red() | (colour.green() << 8) | (colour.blue() << 16) | (colour.alpha() << 32))
                            self.__dwmapi.DwmSetWindowAttribute(
                                int(self.winId()),
                                DWMWINDOWATTRIBUTE.DWMWA_BORDER_COLOR.value,
                                byref(colourref),
                                4
                            )
                        else:
                            colourref = DWORD(0xFFFFFFFF)
                            self.__dwmapi.DwmSetWindowAttribute(
                                int(self.winId()),
                                DWMWINDOWATTRIBUTE.DWMWA_BORDER_COLOR.value,
                                byref(colourref),
                                4
                            )
                        return True, 0
                    case self.__win32con.WM_KILLFOCUS:
                        colourref = DWORD(0xFFFFFFFF)
                        self.__dwmapi.DwmSetWindowAttribute(
                            int(self.winId()),
                            DWMWINDOWATTRIBUTE.DWMWA_BORDER_COLOR.value,
                            byref(colourref),
                            4
                        )
                        return True, 0
                    case self.__win32con.WM_NCHITTEST:
                        if self.resizeEnabled():
                            xPos, yPos = self.__win32gui.ScreenToClient(winMsg.hWnd, self.__win32gui.GetCursorPos())
                            clientRect = self.__win32gui.GetClientRect(winMsg.hWnd)
                            
                            w = clientRect[2] - clientRect[0]
                            h = clientRect[3] - clientRect[1]
                            
                            verBorder = 5
                            horBorder = 5
                            
                            if isMaximised(winMsg.hWnd):
                                verBorder = horBorder = 0
                            
                            lx = xPos < horBorder
                            rx = xPos > w - horBorder
                            ty = yPos < verBorder
                            by = yPos > h - verBorder
                            
                            if lx and ty:
                                return True, self.__win32con.HTTOPLEFT
                            if lx and by:
                                return True, self.__win32con.HTBOTTOMRIGHT
                            if rx and ty:
                                return True, self.__win32con.HTTOPRIGHT
                            if rx and by:
                                return True, self.__win32con.HTBOTTOMRIGHT
                            if lx:
                                return True, self.__win32con.HTLEFT
                            if rx:
                                return True, self.__win32con.HTRIGHT
                            if ty:
                                return True, self.__win32con.HTTOP
                            if by:
                                return True, self.__win32con.HTBOTTOM
                        
                        return False, 0
                    case self.__win32con.WM_NCCALCSIZE:
                        if winMsg.wParam:
                            rect = self.__ctypes.cast(
                                winMsg.lParam,
                                self.__wintypes.LPNCCLACSIZE_PARAMS
                            ).contents.rgrc[0]
                        else:
                            rect = self.__ctypes.cast(
                                winMsg.lParam,
                                self.__wintypes.LPRECT
                            ).contents
                        
                        if isMaximised(winMsg.hWnd) and not isFullScreen(winMsg.hWnd):
                            bx = (getSystemMetrics(int(winMsg.hWnd), win32con.SM_CYSIZEFRAME, True)
                                  + getSystemMetrics(int(winMsg.hWnd), 92, True))
                            by = (getSystemMetrics(int(winMsg.hWnd), win32con.SM_CXSIZEFRAME, False)
                                  + getSystemMetrics(int(winMsg.hWnd), 92, False))
                            rect.top += by
                            rect.bottom -= by
                            rect.left += bx
                            rect.right -= bx
                        
                        if (isMaximised(winMsg.hWnd) or isFullScreen(winMsg.hWnd)) and TaskBar.isAutoHide():
                            position = TaskBar.getPosition(winMsg.hWnd)
                            if position == TaskBar.TaskBarPosition.TOP:
                                rect.top += TaskBar.AUTO_HIDE_THICKNESS
                            elif position == TaskBar.TaskBarPosition.BOTTOM:
                                rect.bottom -= TaskBar.AUTO_HIDE_THICKNESS
                            elif position == TaskBar.TaskBarPosition.LEFT:
                                rect.left += TaskBar.AUTO_HIDE_THICKNESS
                            elif position == TaskBar.TaskBarPosition.RIGHT:
                                rect.right -= TaskBar.AUTO_HIDE_THICKNESS
                        
                        if winMsg.wParam:
                            self.update()
                        return True, 0 if not winMsg.wParam else self.__win32con.WVR_VREDRAW
                
                result = super(FramelessWindow, self).nativeEvent(eventType, message)
                return result[0], result[1] or 0
            case b"xcb_generic_event_t":
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
    
    def setWindowStaysOnTop(self, on):
        if on:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & -Qt.WindowType.WindowStaysOnTopHint)
        
        self.__updateWindowFrameless()
    
    def windowBorderAccentColour(self):
        return self.property("windowBorderAccentColour")
    
    def setWindowBorderAccentColour(self, colour):
        self.setProperty("windowBorderAccentColour", colour)
    
    def borderAccentColourEnabled(self):
        return self.property("borderAccentColourEnabled")
    
    def setBorderAccentColourEnabled(self, enabled):
        self.setProperty("borderAccentColourEnabled", enabled)


class FramelessMainWindow(QMainWindow, FramelessWindow):
    pass
