# -*- coding: utf-8 -*-
from ctypes import *
from ctypes.wintypes import *


class PWINDOWPOS(Structure):
    _fields_ = [
        ('hWnd', HWND),
        ('hwndInsertAfter', HWND),
        ('x', c_int),
        ('y', c_int),
        ('cx', c_int),
        ('cy', c_int),
        ('flags', UINT)
    ]


class NCCALCSIZE_PARAMS(Structure):
    _fields_ = [
        ('rgrc', RECT * 3),
        ('lppos', POINTER(PWINDOWPOS))
    ]
