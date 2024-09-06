# -*- coding: utf-8 -*-
import platform

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from qframelesswindow.utils.win32_utils import Taskbar

from .CWMFrameStructures import *
from .CWMFrameFunctions import *


class RoundedFramelessWindow(QWidget):
    BORDER_WIDTH = 5
    BORDER_RADIUS = 10
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__gdi32 = None
        self.__user32 = None
        self.__nsWindow = None
        self.__objc = None
        self.__cocoa = None
        match platform.system():
            case "Windows":
                self.__gdi32 = WinDLL("gdi32")
                self.__user32 = WinDLL("user32")
            case "Darwin":
                self.__objc = __import__("objc")
                self.__cocoa = __import__("Cocoa")
                self.__nsWindow = self.__objc.objc_object(c_void_p=self.winId().__int__()).view()
        self.__resizeEnabled = True
        self.__maximizeEnabled = True
        self.__systemTitleBarButtonVisible = False
        # self.w = WindowEffect(self)
        self.__updateWindowFrameless()
    
    def __getCurrentDpiScaleRate(self):
        match platform.system():
            case "Windows":
                self.__user32.SetProcessDPIAware()
                return self.__user32.GetDpiForWindow(int(self.winId())) / 96.0
            case "Darwin":
                return 1
            case "Linux":
                return 1
    
    def __updateWindowFrameless(self):
        match platform.system():
            case "Windows":
                self.setWindowFlags(
                    self.windowFlags() | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowMinMaxButtonsHint)
                self.__user32.SetWindowLongPtrW(
                    int(self.winId()),
                    -16,
                    ((0x00010000 | 0x00020000) if self.__maximizeEnabled else 0x00000000)
                    | 0x00C00000
                    | 0x00080000
                    | (0x00040000 if self.__resizeEnabled else 0x00000000),
                )
            case "Darwin":
                self.__updateNSWindow()
            case "Linux":
                pass
        self.__updateWindowRegion()
        self.__updateWindowShadow()
        self.windowHandle().screenChanged.connect(self.__onScreenChanged)
    
    def __updateWindowRegion(self):
        try:
            match platform.system():
                case "Windows":
                    rect = RECT()
                    self.__user32.GetWindowRect(int(self.winId()), pointer(rect))
                    dpiScaleRate = self.__getCurrentDpiScaleRate()
                    self.__user32.SetWindowRgn(int(self.winId()),
                                               self.__gdi32.CreateRoundRectRgn(
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
        finally:
            super().setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
            super().setWindowFlag(Qt.WindowType.WindowMinMaxButtonsHint, True)
            self.update()
    
    def __updateWindowShadow(self):
        try:
            match platform.system():
                case "Windows":
                    pass
                case "Darwin":
                    self.__nsWindow.setHasShadow_(True)
                case "Linux":
                    pass
        finally:
            super().setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
            super().setWindowFlag(Qt.WindowType.WindowMinMaxButtonsHint, True)
            self.update()
    
    def __updateNSWindow(self):
        if platform.system() == "Darwin":
            self.__nsWindow.setStyleMask_(
                self.__nsWindow.styleMask() | self.__cocoa.NSFullSizeContentViewWindowMask
            )
            self.__nsWindow.setTitleBarAppearsTransparent_(True)
            
            self.__nsWindow.setMovableByWindowBackground_(False)
            self.__nsWindow.setMovable_(False)
            
            self.__nsWindow.setTitleVisibility(self.__cocoa.NSWindowTitleHidden)
            self.__updateSystemTitleBarButton()
        self.update()
    
    def __updateSystemTitleBarButton(self):
        if platform.system() == "Darwin":
            self.__nsWindow.setShowsToolbarButton_(self.__systemTitleBarButtonVisible)
            
            self.__nsWindow.standardWindowButton_(self.__cocoa.NSWindowCloseButton).setHidden_(
                not self.__systemTitleBarButtonVisible)
            self.__nsWindow.standardWindowButton_(self.__cocoa.NSWindowZoomButton).setHidden_(
                not self.__systemTitleBarButtonVisible)
            self.__nsWindow.standardWindowButton_(self.__cocoa.NSWindowMiniaturizeButton).setHidden_(
                not self.__systemTitleBarButtonVisible)
            self.__updateSystemTitleBarButtonRect()
        self.update()
    
    def __updateSystemTitleBarButtonRect(self):
        if platform.system() == "Darwin":
            if self.__systemTitleBarButtonVisible:
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
        self.update()
    
    def __onScreenChanged(self):
        match platform.system():
            case "Windows":
                self.__user32.SetWindowPos(int(self.windowHandle().winId()), None, 0, 0, 0, 0,
                                           win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_FRAMECHANGED)
            case "Darwin":
                pass
            case "Linux":
                pass
    
    def paintEvent(self, a0):
        self.__updateNSWindow()
        self.__updateWindowRegion()
    
    def resizeEvent(self, *args, **kwargs):
        self.__updateWindowRegion()
        self.__updateSystemTitleBarButtonRect()
        self.repaint()
        super().resizeEvent(*args, **kwargs)
        self.__updateWindowRegion()
        self.__updateSystemTitleBarButtonRect()
        self.repaint()
    
    def changeEvent(self, a0):
        if platform.system() == "Darwin":
            match a0.type():
                case QEvent.Type.WindowStateChange:
                    self.__updateNSWindow()
                    
                    QTimer.singleShot(1, self.__updateSystemTitleBarButtonRect)
                case QEvent.Type.Resize:
                    self.__updateSystemTitleBarButtonRect()
    
    def event(self, a0):
        self.__updateWindowRegion()
        return super().event(a0)
    
    def nativeEvent(self, eventType, message):
        msg = MSG.from_address(message.__int__())
        if not msg.hWnd:
            return super().nativeEvent(eventType, message)
        
        match msg.message:
            case 134:
                win32gui.DefWindowProc(msg.hWnd, msg.message, msg.wParam, -1)
                return bool(msg.wParam), 0
            case 133:
                self.__updateWindowRegion()
            case 532:
                self.__updateWindowRegion()
            case 132:
                if self.__resizeEnabled:
                    pos = QCursor.pos() - self.pos()
                    w, h = self.width(), self.height()
                    bw = 0 if isMaximized(msg.hWnd) or isFullScreen(msg.hWnd) else self.BORDER_WIDTH
                    lx = pos.x() < bw
                    rx = pos.x() > w - bw
                    ty = pos.y() < bw
                    by = pos.y() > h - bw
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
                return True, 0 if not msg.wParam else win32con.WVR_REDRAW
        return False, 0
    
    def resizeEnabled(self):
        return self.__resizeEnabled
    
    def setResizeEnabled(self, value):
        if value in [True, False, 1, 0]:
            self.__resizeEnabled = bool(value)
        else:
            raise TypeError(f"cannot set property \"resizeEnabled\" to type {type(value)}")
        self.__updateWindowFrameless()
    
    def maximizeEnabled(self):
        return self.__maximizeEnabled
    
    def setMaximizeEnabled(self, value):
        if value in [True, False, 1, 0]:
            self.__maximizeEnabled = bool(value)
        else:
            raise TypeError(f"cannot set property \"maximizeEnabled\" to type {type(value)}")
        self.__updateWindowFrameless()
    
    def systemTitleBarButtonVisible(self):
        if platform.system() == "Darwin":
            return self.__systemTitleBarButtonVisible
        return False
    
    def setSystemTitleBarButtonVisible(self, value):
        if platform.system() == "Darwin":
            if value in [True, False, 1, 0]:
                self.__systemTitleBarButtonVisible = bool(value)
            else:
                raise TypeError(f"cannot set property \"systemTitleBarButtonVisible\" to type {type(value)}")
        self.__updateWindowFrameless()
    
    def setWindowFlags(self, type):
        super().setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        super().setWindowFlag(Qt.WindowType.WindowMinMaxButtonsHint, True)
        super().setWindowFlags(type)
        super().setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        super().setWindowFlag(Qt.WindowType.WindowMinMaxButtonsHint, True)
    
    def setWindowFlag(self, a0, on=True):
        super().setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        super().setWindowFlag(Qt.WindowType.WindowMinMaxButtonsHint, True)
        super().setWindowFlag(a0, on)
        super().setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        super().setWindowFlag(Qt.WindowType.WindowMinMaxButtonsHint, True)
    
    def childEvent(self, *args, **kwargs):
        super().childEvent(*args, **kwargs)
        self.__updateWindowFrameless()


class RoundedFramelessMainWindow(QMainWindow, RoundedFramelessWindow):
    pass
