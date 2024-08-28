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
        match platform.system():
            case "Windows":
                self.__gdi32 = WinDLL("gdi32")
                self.__user32 = WinDLL("user32")
        self.__resizeEnabled = True
        self.__maximizeEnabled = True
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
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowMinMaxButtonsHint)
        match platform.system():
            case "Windows":
                self.__user32.SetWindowLongPtrW(
                    int(self.winId()),
                    -16,
                    ((0x00010000 | 0x00020000) if self.__maximizeEnabled else 0x00000000)
                    | 0x00C00000
                    | 0x00080000
                    | (0x00040000 if self.__resizeEnabled else 0x00000000),
                )
            case "Darwin":
                pass
            case "Linux":
                pass
        self.__updateWindowRegion()
        self.windowHandle().screenChanged.connect(self.__onScreenChanged)
    
    def __updateWindowRegion(self):
        match platform.system():
            case "Windows":
                rect = win32gui.GetWindowRect(int(self.winId()))
                dpiScaleRate = self.__getCurrentDpiScaleRate()
                self.__user32.SetWindowRgn(int(self.winId()),
                                           self.__gdi32.CreateRoundRectRgn(0,
                                                                           0,
                                                                           (rect[2] - rect[0]),
                                                                           (rect[3] - rect[1]),
                                                                           0 if isFullScreen(
                                                                               self.winId()) or isMaximized(
                                                                               self.winId()) else int(
                                                                               self.BORDER_RADIUS * dpiScaleRate),
                                                                           0 if isFullScreen(
                                                                               self.winId()) or isMaximized(
                                                                               self.winId()) else int(
                                                                               self.BORDER_RADIUS * dpiScaleRate)),
                                           False)
                self.update()
            case "Darwin":
                pass
            case "Linux":
                pass
    
    def __onScreenChanged(self):
        self.__user32.SetWindowPos(int(self.windowHandle().winId()), None, 0, 0, 0, 0,
                                   win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_FRAMECHANGED)
    
    def paintEvent(self, a0):
        self.__updateWindowRegion()
    
    def resizeEvent(self, *args, **kwargs):
        self.__updateWindowRegion()
        super().resizeEvent(*args, **kwargs)
        self.__updateWindowRegion()
    
    def event(self, a0):
        try:
            self.__updateWindowRegion()
        finally:
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
    
    def childEvent(self, *args, **kwargs):
        super().childEvent(*args, **kwargs)
        self.__updateWindowFrameless()


class RoundedFramelessMainWindow(QMainWindow, RoundedFramelessWindow):
    pass

# class AntialiasingRoundedFramelessWindow(QMainWindow):
#     BORDER_WIDTH = 5
#     BORDER_RADIUS = 10
#
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.__gdi32 = WinDLL("gdi32")
#         self.__user32 = WinDLL("user32")
#         self.__dwmapi = WinDLL("dwmapi")
#         self.__resizeEnabled = True
#         # self.w = WindowEffect(self)
#         self.__updateFrameless()
#         self.titleBar = TitleBar(self)
#
#     def __updateFrameless(self):
#         self.setWindowFlags(
#             Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowMinMaxButtonsHint)
#         self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
#         self.setStyleSheet(
#             f"AntialiasingRoundedFramelessWindow {{border: {self.BORDER_WIDTH / 5}px solid gray; border-radius: {self.BORDER_RADIUS}px; background: white}}")
#         match platform.system():
#             case "Windows":
#                 self.__user32.SetWindowLongPtrW(
#                     int(self.winId()),
#                     -16,
#                     self.__user32.GetWindowLongPtrW(int(self.winId()), -16)
#                     | 0x00010000
#                     | 0x00020000
#                     | 0x00C00000
#                     | 0x00080000
#                     | 0x00040000,
#                 )
#             case "Darwin":
#                 pass
#             case "Linux":
#                 pass
#         self.windowHandle().screenChanged.connect(self.__onScreenChanged)
#
#     def __onScreenChanged(self):
#         self.__user32.SetWindowPos(int(self.windowHandle().winId()), None, 0, 0, 0, 0,
#                                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_FRAMECHANGED)
#
#     def paintEvent(self, a0):
#         opt = QStyleOption()
#         opt.initFrom(self)
#         p = QPainter(self)
#         self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)
#         super().paintEvent(a0)
#
#     def resizeEvent(self, *args, **kwargs):
#         self.titleBar.resize(self.width(), self.titleBar.height())
#         super().resizeEvent(*args, **kwargs)
#         self.titleBar.resize(self.width(), self.titleBar.height())
#         self.titleBar.raise_()
#
#     def nativeEvent(self, eventType, message):
#         msg = MSG.from_address(message.__int__())
#         if not msg.hWnd:
#             return super().nativeEvent(eventType, message)
#
#         match msg.message:
#             case win32con.WM_SIZE:
#                 self.titleBar.resize(self.width(), self.titleBar.height())
#             case win32con.WM_SIZING:
#                 self.titleBar.resize(self.width(), self.titleBar.height())
#             case win32con.WM_NCHITTEST:
#                 if self.__resizeEnabled:
#                     pos = QCursor.pos() - self.pos()
#                     w, h = self.width(), self.height()
#                     lx = pos.x() < self.BORDER_WIDTH
#                     rx = pos.x() > w - self.BORDER_WIDTH
#                     ty = pos.y() < self.BORDER_WIDTH
#                     by = pos.y() > h - self.BORDER_WIDTH
#                     if lx and ty:
#                         return True, win32con.HTTOPLEFT
#                     elif rx and by:
#                         return True, win32con.HTBOTTOMRIGHT
#                     elif rx and ty:
#                         return True, win32con.HTTOPRIGHT
#                     elif lx and by:
#                         return True, win32con.HTBOTTOMLEFT
#                     elif ty:
#                         return True, win32con.HTTOP
#                     elif by:
#                         return True, win32con.HTBOTTOM
#                     elif lx:
#                         return True, win32con.HTLEFT
#                     elif rx:
#                         return True, win32con.HTRIGHT
#             case win32con.WM_NCCALCSIZE:
#                 if msg.wParam:
#                     rect = cast(msg.lParam, LPNCCALCSIZE_PARAMS).contents.rgrc[0]
#                 else:
#                     rect = cast(msg.lParam, LPRECT).contents
#
#                 isMax = isMaximized(msg.hWnd)
#                 isFull = isFullScreen(msg.hWnd)
#
#                 if isMax and not isFull:
#                     thickness = getResizeBorderThickness(msg.hWnd)
#                     rect.top += thickness
#                     rect.left += thickness
#                     rect.right -= thickness
#                     rect.bottom -= thickness
#
#                 if (isMax or isFull) and Taskbar.isAutoHide():
#                     position = Taskbar.getPosition(msg.hWnd)
#                     if position == Taskbar.TOP:
#                         rect.top += Taskbar.AUTO_HIDE_THICKNESS
#                     elif position == Taskbar.BOTTOM:
#                         rect.bottom -= Taskbar.AUTO_HIDE_THICKNESS
#                     elif position == Taskbar.LEFT:
#                         rect.left += Taskbar.AUTO_HIDE_THICKNESS
#                     elif position == Taskbar.RIGHT:
#                         rect.right -= Taskbar.AUTO_HIDE_THICKNESS
#
#                 result = 0 if not msg.wParam else win32con.WVR_REDRAW
#                 return True, result
#         return 0, 0
#
#     def resizeEnabled(self):
#         return self.__resizeEnabled
#
#     def setResizeEnabled(self, value):
#         if value in [True, False, 1, 0]:
#             self.__resizeEnabled = bool(value)
#         else:
#             raise TypeError(f"cannot set property \"resizeEnabled\" to type {type(value)}")
