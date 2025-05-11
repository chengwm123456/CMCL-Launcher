# -*- coding: utf-8 -*-
from ctypes import *
from ctypes.wintypes import *

import win32api
import win32con
import win32gui
import win32print
from win32comext.shell import shellcon

from PyQt6.QtGui import QGuiApplication
from PyQt6.QtCore import *


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
