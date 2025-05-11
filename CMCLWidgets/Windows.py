# -*- coding: utf-8 -*-
import platform
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from CMCLWidgets.ThemeController.ThemeControl import *
from .FramelessWindow import *

if platform.system().lower() == "windows":
    from ctypes import WinDLL, pointer, windll
    from ctypes.wintypes import RECT
    import win32con


class TitleBarButton(QPushButton):
    def __init__(self, parent):
        super().__init__(parent)
        match platform.system().lower():
            case "windows":
                self.setFixedSize(46, 30)
            case "linux":
                self.setFixedSize(20, 20)
    
    def paintEvent(self, a0):
        pass


class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedHeight(30)
        self.minimiseButton = TitleBarButton(self)
        self.maximiseButton = TitleBarButton(self)
        self.closeButton = TitleBarButton(self)
        self.minimiseButton.pressed.connect(self.parent().showMinimized)
        self.maximiseButton.pressed.connect(
            lambda: self.parent().showNormal() if self.parent().isMaximized() else self.parent().showMaximized())
        self.closeButton.pressed.connect(self.parent().close)
    
    def showEvent(self, a0):
        self.setGeometry(QRect(0, 0, 0, 0))
        self.setGeometry(QRect(0, 0, self.parent().width(), self.height()))
        super().showEvent(a0)
    
    def mousePressEvent(self, a0):
        if a0.button() == Qt.MouseButton.LeftButton:
            self.parent().windowHandle().startSystemMove()
    
    def mouseMoveEvent(self, a0):
        if a0.button() == Qt.MouseButton.LeftButton:
            if self.parent().isMaximized():
                self.parent().showNormal()
    
    def mouseDoubleClickEvent(self, a0):
        if not self.parent().windowFlags() & Qt.WindowType.WindowMaximizeButtonHint:
            return
        match platform.system().lower():
            case "windows":
                if self.parent().isMaximized():
                    self.parent().showNormal()
                else:
                    self.parent().showMaximized()
    
    def resizeEvent(self, a0):
        match platform.system().lower():
            case "windows":
                self.closeButton.move(self.width() - self.closeButton.width(), 0)
                self.maximiseButton.move(self.closeButton.x() - self.maximiseButton.width(), 0)
                self.minimiseButton.move(self.maximiseButton.x() - self.minimiseButton.width(), 0)
                if not self.maximiseButton.isVisible():
                    self.minimiseButton.move(self.maximiseButton.x(), 0)
            case "linux":
                self.closeButton.move(self.width() - self.closeButton.width() - 10, 6)
                self.maximiseButton.move(self.closeButton.x() - self.maximiseButton.width() - 10, 6)
                self.minimiseButton.move(self.maximiseButton.x() - self.minimiseButton.width() - 10, 6)
                if not self.maximiseButton.isVisible():
                    self.minimiseButton.move(self.maximiseButton.x(), 6)
    
    def leaveEvent(self, a0):
        self.repaint()
        super().leaveEvent(a0)
    
    def paintEvent(self, a0):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if platform.system().lower() == "linux":
            if self.parent().isActiveWindow():
                painter.setOpacity(1.0)
            else:
                painter.setOpacity(0.6)
        if platform.system().lower() == "windows":
            painter.save()
            icon = self.parent().windowIcon()
            painter.drawPixmap(QRect(10, 5, 20, 20), icon.pixmap(20, 20))
            painter.restore()
        painter.save()
        painter.setPen(getForegroundColour())
        match platform.system().lower():
            case "windows":
                font = QFont("Segoe UI")
                font.setPointSize(10)
                painter.setFont(font)
                painter.drawText(QRect(40, 5, 200, 20), Qt.AlignmentFlag.AlignLeft, self.parent().windowTitle())
            case "linux":
                font = QFont("Ubuntu")
                font.setPointSize(10)
                font.setBold(True)
                painter.setFont(font)
                painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.parent().windowTitle())
        painter.restore()
        painter.setPen(QColor(0, 0, 0, 0))
        match platform.system().lower():
            case "windows":
                if self.closeButton.isVisible():
                    painter.save()
                    if self.closeButton.underMouse():
                        if self.closeButton.isDown():
                            painter.setBrush(QColor(241, 112, 122))
                        else:
                            painter.setBrush(QColor(232, 17, 35))
                    else:
                        painter.setBrush(QColor(0, 0, 0, 0))
                    painter.drawRect(self.closeButton.geometry())
                    
                    painter.setClipRect(self.closeButton.geometry())
                    painter.setPen(getForegroundColour())
                    close_icon_pp = QPainterPath()
                    close_icon_pp.moveTo(QPointF(0 + self.closeButton.x() + 18, 11))
                    close_icon_pp.lineTo(QPointF(9 + self.closeButton.x() + 18, 9 + 11))
                    close_icon_pp.moveTo(QPointF(9 + self.closeButton.x() + 18, 11))
                    close_icon_pp.lineTo(QPointF(0 + self.closeButton.x() + 18, 9 + 11))
                    painter.drawPath(close_icon_pp)
                    painter.restore()
                if self.maximiseButton.isVisible():
                    painter.save()
                    if self.maximiseButton.underMouse():
                        if self.maximiseButton.isDown():
                            painter.setBrush(QColor(0, 0, 0, 51))
                        else:
                            painter.setBrush(QColor(0, 0, 0, 26))
                    else:
                        painter.setBrush(QColor(0, 0, 0, 0))
                    painter.drawRect(self.maximiseButton.geometry())
                    
                    painter.setClipRect(self.maximiseButton.geometry())
                    painter.setPen(getForegroundColour())
                    maximise_icon_pp = QPainterPath()
                    if self.parent().isMaximized():
                        maximise_icon_pp.addRect(QRectF(0 + self.maximiseButton.x() + 18, 12, 7, 7))
                        maximise_icon_pp.moveTo(QPointF(0 + self.maximiseButton.x() + 20, 10))
                        maximise_icon_pp.lineTo(QPointF(0 + self.maximiseButton.x() + 27, 10))
                        maximise_icon_pp.lineTo(QPointF(0 + self.maximiseButton.x() + 27, 17))
                    else:
                        maximise_icon_pp.addRect(QRectF(0 + self.maximiseButton.x() + 18, 11, 9, 9))
                    painter.drawPath(maximise_icon_pp)
                    painter.restore()
                if self.minimiseButton.isVisible():
                    painter.save()
                    if self.minimiseButton.underMouse():
                        if self.minimiseButton.isDown():
                            painter.setBrush(QColor(0, 0, 0, 51))
                        else:
                            painter.setBrush(QColor(0, 0, 0, 26))
                    else:
                        painter.setBrush(QColor(0, 0, 0, 0))
                    painter.drawRect(self.minimiseButton.geometry())
                    
                    painter.setClipRect(self.minimiseButton.geometry())
                    painter.setPen(getForegroundColour())
                    minimise_icon_pp = QPainterPath()
                    minimise_icon_pp.moveTo(0 + self.minimiseButton.x() + 18, self.minimiseButton.height() // 2)
                    minimise_icon_pp.lineTo(0 + self.minimiseButton.x() + 27, self.minimiseButton.height() // 2)
                    painter.drawPath(minimise_icon_pp)
                    painter.restore()
            case "linux":
                if self.closeButton.isVisible():
                    painter.save()
                    if self.closeButton.underMouse():
                        if self.closeButton.isDown():
                            painter.setBrush(QColor(88, 88, 88))
                        else:
                            painter.setBrush(QColor(78, 78, 78))
                    else:
                        painter.setBrush(QColor(55, 55, 55))
                    painter.drawEllipse(self.closeButton.geometry())
                    
                    painter.setClipRect(self.closeButton.geometry())
                    painter.setPen(Qt.GlobalColor.white)
                    close_icon_pp = QPainterPath()
                    close_icon_pp.moveTo(QPointF(0 + self.closeButton.x() + 5.5, 11.5))
                    close_icon_pp.lineTo(QPointF(9 + self.closeButton.x() + 5.5, 9 + 11.5))
                    close_icon_pp.moveTo(QPointF(9 + self.closeButton.x() + 5.5, 11.5))
                    close_icon_pp.lineTo(QPointF(0 + self.closeButton.x() + 5.5, 9 + 11.5))
                    painter.drawPath(close_icon_pp)
                    
                    painter.restore()
                
                if self.maximiseButton.isVisible():
                    painter.save()
                    if self.maximiseButton.underMouse():
                        if self.maximiseButton.isDown():
                            painter.setBrush(QColor(88, 88, 88))
                        else:
                            painter.setBrush(QColor(78, 78, 78))
                    else:
                        painter.setBrush(QColor(55, 55, 55))
                    painter.drawEllipse(self.maximiseButton.geometry())
                    
                    painter.setClipRect(self.maximiseButton.geometry())
                    painter.setPen(Qt.GlobalColor.white)
                    maximise_icon_pp = QPainterPath()
                    if self.parent().isMaximized():
                        maximise_icon_pp.addRect(QRectF(0 + self.maximiseButton.x() + 5, 13, 7, 7))
                        maximise_icon_pp.moveTo(QPointF(0 + self.maximiseButton.x() + 7, 11))
                        maximise_icon_pp.lineTo(QPointF(0 + self.maximiseButton.x() + 14, 11))
                        maximise_icon_pp.lineTo(QPointF(0 + self.maximiseButton.x() + 14, 18))
                    else:
                        maximise_icon_pp.addRect(QRectF(0 + self.maximiseButton.x() + 6, 11, 9, 9))
                    painter.drawPath(maximise_icon_pp)
                    
                    painter.restore()
                
                if self.minimiseButton.isVisible():
                    painter.save()
                    if self.minimiseButton.underMouse():
                        if self.minimiseButton.isDown():
                            painter.setBrush(QColor(88, 88, 88))
                        else:
                            painter.setBrush(QColor(78, 78, 78))
                    else:
                        painter.setBrush(QColor(55, 55, 55))
                    painter.drawEllipse(self.minimiseButton.geometry())
                    
                    painter.setClipRect(self.minimiseButton.geometry())
                    painter.setPen(Qt.GlobalColor.white)
                    minimise_icon_pp = QPainterPath()
                    minimise_icon_pp.moveTo(0 + self.minimiseButton.x() + 6,
                                            self.minimiseButton.height() + self.minimiseButton.y() - 7)
                    minimise_icon_pp.lineTo(0 + self.minimiseButton.x() + 15,
                                            self.minimiseButton.height() + self.minimiseButton.y() - 7)
                    painter.drawPath(minimise_icon_pp)
                    
                    painter.restore()


class Window(FramelessWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleBar = TitleBar(self)
    
    def resizeEvent(self, a0):
        if hasattr(self, "titleBar"):
            self.titleBar.resize(self.width(), self.titleBar.height())
        super().resizeEvent(a0)
        if hasattr(self, "titleBar"):
            self.titleBar.resize(self.width(), self.titleBar.height())
            self.titleBar.raise_()


class MainWindow(FramelessMainWindow, Window):
    pass


class RoundedWindow(MainWindow):
    BORDER_RADIUS = 10
    
    def __getCurrentDpiScaleRate(self):
        match platform.system():
            case "Windows":
                windll.user32.SetProcessDPIAware()
                return windll.user32.GetDpiForWindow(int(self.winId())) / 96.0
            case "Darwin":
                return 1
            case "Linux":
                return 1
    
    def __updateWindowRegion(self):
        match platform.system():
            case "Windows":
                rect = RECT()
                windll.user32.GetWindowRect(int(self.winId()), pointer(rect))
                dpiScaleRate = self.__getCurrentDpiScaleRate()
                windll.user32.SetWindowRgn(int(self.winId()),
                                           windll.gdi32.CreateRoundRectRgn(
                                               0,
                                               0,
                                               (rect.right - rect.left),
                                               (rect.bottom - rect.top),
                                               int(self.BORDER_RADIUS * dpiScaleRate),
                                               int(self.BORDER_RADIUS * dpiScaleRate)
                                           ),
                                           False)
                
                user32 = WinDLL("user32")
                user32.SetClassLongPtrW(int(self.winId()), win32con.GCL_STYLE,
                                        user32.GetClassLongPtrW(int(self.winId()),
                                                                win32con.GCL_STYLE) | 0x00020000)
            case "Darwin":
                pass
            case "Linux":
                pass
        # self.update()
    
    def event(self, a0, **kwargs):
        self.__updateWindowRegion()
        return super().event(a0)


class DialogueMask(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    
    def paintEvent(self, a0):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 120))
    
    def event(self, a0):
        if self.parent():
            self.setGeometry(self.parent().rect())
        self.raise_()
        return super().event(a0)


class RoundedDialogue(QDialog, Window):
    BORDER_RADIUS = 10
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleBar.maximiseButton.hide()
        self.titleBar.minimiseButton.hide()
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowType.WindowMaximizeButtonHint)
        self.setResizeEnabled(False)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    
    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        Window.resizeEvent(self, a0)
    
    def paintEvent(self, *args, **kwargs):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getBorderColour())
        painter.setBrush(getBackgroundColour())
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), self.BORDER_RADIUS, self.BORDER_RADIUS)


class MaskedDialogue(RoundedDialogue):
    def __init__(self, parent):
        super().__init__(parent)
        self.dialogueMask = DialogueMask(parent)
        
        pos = self.parent().mapToGlobal(QPoint(0, 0)) if self.parent() else QPoint(0, 0)
        x = pos.x()
        y = pos.y()
        geometry = self.dialogueMask.parent().rect() if self.parent() else QGuiApplication.primaryScreen().geometry()
        point = QPoint(geometry.width() // 2 - self.width() // 2 + x,
                       geometry.height() // 2 - self.height() // 2 + y)
        self.move(point)
    
    def paintEvent(self, *args, **kwargs):
        super().paintEvent(*args, **kwargs)
        self.updateMaskVisible()
    
    def showEvent(self, a0):
        super().showEvent(a0)
        self.updateMaskVisible()
    
    def hideEvent(self, *args, **kwargs):
        super().hideEvent(*args, **kwargs)
        self.updateMaskVisible()
    
    def moveEvent(self, *args, **kwargs):
        super().moveEvent(*args, **kwargs)
        self.updateDialoguePosition()
    
    def resizeEvent(self, *args, **kwargs):
        super().resizeEvent(*args, **kwargs)
        self.updateDialoguePosition()
    
    def updateMaskVisible(self):
        if hasattr(self, "dialogueMask"):
            self.dialogueMask.setVisible(self.isVisible())
    
    def updateDialoguePosition(self):
        if not hasattr(self, "dialogueMask"):
            return
        pos = self.parent().mapToGlobal(QPoint(0, 0)) if self.parent() else QPoint(0, 0)
        x = pos.x()
        y = pos.y()
        geometry = self.dialogueMask.parent().rect() if self.parent() else QGuiApplication.primaryScreen().geometry()
        point = QPoint(geometry.width() // 2 - self.width() // 2 + x,
                       geometry.height() // 2 - self.height() // 2 + y)
        self.move(point)


class RoundedMenu(QMenu):
    BORDER_RADIUS = 10
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.updateQSS()
    
    def updateQSS(self, name=None):
        if not name:
            name = self.__class__.__name__
        self.setStyleSheet(f"""{name}{{
            background: rgb({str(getBackgroundColour(is_tuple=True)).strip('()')});
            color: rgb({str(getForegroundColour(is_tuple=True)).strip('()')});
            border: 1px solid rgb({str(getBorderColour(is_tuple=True)).strip('()')});
            border-radius: {self.BORDER_RADIUS}px;
        }}
        {name}::item{{
            background: rgba({str(getBackgroundColour(is_tuple=True)).strip('()')}, 0.6);
            color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, 0.6);
            border-radius: 10px;
            border: 1px solid rgba({str(getBorderColour(is_tuple=True)).strip('()')}, 0.6);
            padding: 4px 2px;
            margin: 3px;
            height: 30px;
        }}
        {name}::item:selected{{
            background: rgb({str(getBackgroundColour(is_tuple=True)).strip('()')});
        }}
        {name}::item:selected, {name}::item:pressed{{
            border: 1px solid rgb({str(getBorderColour(is_highlight=True, is_tuple=True)).strip('()')});
            color: rgb({str(getForegroundColour(is_tuple=True)).strip('()')});
        }}
        {name}::item:pressed{{
            background: rgb({str(getBackgroundColour(is_highlight=True, is_tuple=True)).strip('()')});
        }}
        {name}::item:disabled{{
            background: rgba({str(getBackgroundColour(is_tuple=True)).strip('()')}, 0.3);
            color: rgba({str(getForegroundColour(is_tuple=True)).strip('()')}, 0.3);
            border: 1px solid rgba({str(getBorderColour(is_tuple=True)).strip('()')}, 0.3);
        }}
        """)
    
    def showEvent(self, a0):
        super().showEvent(a0)
        self.updateQSS()
