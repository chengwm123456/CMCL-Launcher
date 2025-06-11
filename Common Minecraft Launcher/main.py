# -*- coding: utf-8 -*-
"""
"Common Minecraft Launcher" started time: 1693310591 (folder created time)
|-time.struct_time(tm_year=2023, tm_mon=8, tm_mday=29, tm_hour=20, tm_min=3, tm_sec=11, tm_wday=1, tm_yday=241, tm_isdst=0)
|-2023/08/29 20:03:11, 周二（Tuesday, Tues.）, 八月二十九日, 时区: 中国标准时间(UTC+8), 一年的第241天
main.py started time: 1693310592 (main.py created time)
|-time.struct_time(tm_year=2023, tm_mon=8, tm_mday=29, tm_hour=20, tm_min=3, tm_sec=12, tm_wday=1, tm_yday=241, tm_isdst=0)
|-2023/08/29 20:03:12, 周二（Tuesday, Tues.）, 八月二十九日, 时区: 中国标准时间(UTC+8), 一年的第241天
"""
import shlex
import json
import subprocess
import random
import sqlite3
import base64
import datetime
import platform
import sys
import traceback
import re
import locale
import webbrowser as webb
from pathlib import Path
from io import StringIO
from uuid import UUID
import logging
import time
import tempfile
import os

from CMCLWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView

from CMCLCore.Launch import LaunchMinecraft
from CMCLCore.Login import MicrosoftPlayerLogin
from CMCLCore.Player import create_online_player, create_offline_player, MicrosoftPlayer, LittleSkinPlayer
from CMCLCore.GetVersion import GetVersionByScanDirectory, GetVersionByMojangApi
from CMCLCore.DownloadVersion import DownloadMinecraft
from CMCLCore.GetOperationSystem import GetOperationSystemName

import requests

from CMCLModding.GetMods import GetMods, ListModVersions, GetOneMod
from CMCLModding.DownloadMods import DownloadMod
from CMCLModding.GetFabric import GetFabricLoaderVersions, GetFabricApiVersions

from CMCLSaveEditing.LevelDat import LoadData
import nbtlib

import resources

try:
    from dateutil import tz
except ImportError:
    import pytz as tz

DEBUG = "--debug" in sys.argv

output = StringIO()

if DEBUG:
    sys.stdout = sys.stderr = output
    
    formatter = logging.Formatter("[%(asctime)s][%(levelname)s]:%(message)s")
    formatter.datefmt = "%Y/%m/%d  %H:%M:%S %p"
    streamHandler = logging.StreamHandler(output)
    streamHandler.setFormatter(formatter)
    logging.root.addHandler(streamHandler)

lock = QMutex()


def log(type, context, msg):
    lock.lock()
    print(time.strftime(f"[%Y/%m/%d  %H:%M:%S %p]"), end="")
    match type:
        case QtMsgType.QtDebugMsg:
            print("[DEBUG]:", end="")
        case QtMsgType.QtInfoMsg:
            print("[INFO]:", end="")
        case QtMsgType.QtWarningMsg:
            print("[WARNING]:", end="")
        case QtMsgType.QtCriticalMsg:
            print("[CRITICAL]:", end="")
        case QtMsgType.QtFatalMsg:
            print("[FATAL]:", end="")
        case QtMsgType.QtSystemMsg:
            print("[SYSTEM]:", end="")
    print(msg)
    print(f"Context: {context.file}:{context.line}")
    lock.unlock()


qInstallMessageHandler(log)

CMCL_version = ("AlphaDev-25002", "Alpha Development-25002")
minecraft_path = Path(".")
current_language = locale._getdefaultlocale()[0].lower().replace("_", "-")

theme_colour_defines = {
    "PresetBlue": {
        Theme.Light: {
            ColourRole.Background: {
                False: (253, 253, 253),
                True: (176, 224, 250)
            },
            ColourRole.Border: {
                False: (215, 220, 229),
                True: (135, 206, 250)
            }
        },
        Theme.Dark: {
            ColourRole.Background: {
                False: (67, 67, 67),
                True: (142, 197, 252),
            },
            ColourRole.Border: {
                False: (134, 143, 150),
                True: (79, 172, 254)
            },
        }
    },
    "PresetPink": {
        Theme.Light: {
            ColourRole.Background: {
                False: (253, 253, 253),
                True: (250, 109, 194)
            },
            ColourRole.Border: {
                False: (215, 220, 229),
                True: (250, 137, 207)
            }
        },
        Theme.Dark: {
            ColourRole.Background: {
                False: (67, 67, 67),
                True: (252, 142, 173),
            },
            ColourRole.Border: {
                False: (134, 143, 150),
                True: (252, 79, 135)
            }
        }
    },
    "PresetRed": {
        Theme.Light: {
            ColourRole.Background: {
                False: (253, 253, 253),
                True: (250, 176, 176)
            },
            ColourRole.Border: {
                False: (215, 220, 229),
                True: (250, 135, 135)
            }
        },
        Theme.Dark: {
            ColourRole.Background: {
                False: (67, 67, 67),
                True: (252, 142, 142),
            },
            ColourRole.Border: {
                False: (134, 143, 150),
                True: (254, 79, 79)
            }
        }
    }
}
languages_map = {
    "zh-cn": "简体中文（中国大陆）",
    "zh-hk": "繁體中文（中國香港特別行政區/中國澳門特別行政區）",
    "zh-tw": "繁體中文（中國台灣）",
    "lzh": "文言（華夏）",
    "en-us": "English (United States)",
    "en-gb": "English (United Kingdom)",
}

window_class = MainWindow

lightGradients = [QGradient.Preset.PerfectWhite, QGradient.Preset.FreshOasis, QGradient.Preset.LandingAircraft,
                  QGradient.Preset.DeepBlue]
darkGradients = [QGradient.Preset.PerfectBlue, QGradient.Preset.PlumPlate, QGradient.Preset.NightSky]
backgroundGradient = random.choice(lightGradients), random.choice(darkGradients)


class AcrylicBackground(QWidget):
    def __init__(self, parent, tintColour, luminosityColour=QColor(255, 255, 255, 0), blurRadius=10, noiseOpacity=0.03):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.tintColour = tintColour
        self.luminosityColour = luminosityColour
        self.blurRadius = blurRadius
        self.noiseOpacity = noiseOpacity
        self.img = QPixmap()
    
    def setTintColour(self, colour):
        self.tintColour = colour
    
    def setLuminosityColour(self, colour):
        self.luminosityColour = colour
    
    def grabBehind(self):
        image = self.window().grab(QRect(self.mapTo(self.window(), QPoint(0, 0)),
                                         self.mapTo(self.window(), QPoint(self.width(), self.height()))))
        self.img = image
    
    def paintEvent(self, a0):
        brush = self.__createTexture()
        scene = QGraphicsScene()
        item = QGraphicsPixmapItem()
        item.setPixmap(self.img)
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(self.blurRadius)
        item.setGraphicsEffect(blur)
        scene.addItem(item)
        img = QPixmap(self.size())
        img.fill(Qt.GlobalColor.transparent)
        ptr = QPainter(img)
        scene.render(ptr, QRectF(img.rect()), QRectF(img.rect()))
        ptr.end()
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), img.scaled(self.size()))
        painter.fillRect(self.rect(), brush)
    
    def __createTexture(self):
        acrylicTexture = QImage(64, 64, QImage.Format.Format_ARGB32_Premultiplied)
        luminosityColour = QColor.fromRgb(self.luminosityColour.rgb())
        luminosityColour.setAlpha(10)
        acrylicTexture.fill(luminosityColour)
        painter = QPainter(acrylicTexture)
        tintColour = QColor.fromRgb(self.tintColour.rgb())
        tintColour.setAlpha(150)
        painter.fillRect(acrylicTexture.rect(), tintColour)
        painter.setOpacity(self.noiseOpacity)
        painter.drawImage(acrylicTexture.rect(), QImage(":/acrylic_noise.png"))
        painter.end()
        
        brush = QBrush(acrylicTexture)
        return brush


class AnimatedStackedWidget(QStackedWidget):
    def setCurrentWidget(self, w):
        if 1 in settings["Settings"]["LauncherSettings"]["Customise"]["Animations"]["EnabledItems"]:
            class OpacityAnimation(QVariantAnimation):
                def __init__(self, parent=None):
                    super().__init__(parent)
                    self.valueChanged.connect(self.__updateOpacity)
                
                def __updateOpacity(self, value):
                    op = QGraphicsOpacityEffect(self.parent())
                    op.setOpacity(self.currentValue() / 100)
                    if self.currentValue() == self.endValue():
                        self.parent().setGraphicsEffect(None)
                        return
                    self.parent().setGraphicsEffect(op)
            
            lastWidget = self.currentWidget()
            if lastWidget == w:
                return
            self.setProperty("currentIndex", self.indexOf(w))
            lastWidget.show()
            w.stackUnder(lastWidget)
            ani1 = QPropertyAnimation(lastWidget, b"pos", parent=lastWidget)
            ani1.setDuration(500)
            ani1.setStartValue(
                QPointF(lastWidget.x(), float(lastWidget.y())))
            ani1.setEndValue(
                QPointF(lastWidget.x(), float(lastWidget.y()) + 100))
            ani1.setEasingCurve(QEasingCurve.Type.OutQuad)
            ani1.start()
            ani11 = OpacityAnimation(lastWidget)
            ani11.setStartValue(100)
            ani11.setEndValue(0)
            ani11.setDuration(500)
            ani11.setEasingCurve(QEasingCurve.Type.OutQuad)
            ani11.finished.connect(lastWidget.hide)
            ani11.start()
            currentWidget = w
            ani2 = QPropertyAnimation(currentWidget, b"pos", parent=currentWidget)
            ani2.setDuration(500)
            ani2.setStartValue(
                QPointF(currentWidget.x(), float(currentWidget.y()) + 100))
            ani2.setEndValue(QPointF(currentWidget.x(), float(currentWidget.y())))
            ani2.setEasingCurve(QEasingCurve.Type.OutQuad)
            ani2.start()
            ani22 = OpacityAnimation(currentWidget)
            ani22.setStartValue(0)
            ani22.setEndValue(100)
            ani22.setDuration(500)
            ani22.setEasingCurve(QEasingCurve.Type.OutQuad)
            ani22.start()
            currentWidget.raise_()
            t = QTimer(self)
            t.setInterval(1)
            t.timeout.connect(lambda: self.update())
            t.start()
            QTimer.singleShot(500, lambda: t.stop())
            QTimer.singleShot(499, lambda: super(AnimatedStackedWidget, self).setCurrentWidget(w))
        else:
            super().setCurrentWidget(w)


class ContentPanel(AnimatedStackedWidget, Panel):
    pass


class LoadingAnimation(QFrame):
    class HideAnimation(QThread):
        def run(self):
            import time
            time.sleep(1)
            self.parent().hide()
    
    class TransparencyAnimation(QVariantAnimation):
        def __init__(self, parent=None, variant="in"):
            super().__init__(parent)
            self.setStartValue(0)
            self.setEndValue(255)
            self.setDirection(
                QAbstractAnimation.Direction.Forward if variant == "in" else QAbstractAnimation.Direction.Backward)
            self.setDuration(1000)
            self.setEasingCurve(QEasingCurve.Type.OutQuad)
            self.valueChanged.connect(self.update_opacity)
        
        def update_opacity(self, value):
            colour = value
            self.parent().setStyleSheet(
                f"background: rgba({str(getBackgroundColour(is_tuple=True)).strip('()')}, {colour / 255})")
    
    class SizingAnimation(QVariantAnimation):
        def __init__(self, parent=None, variant="in"):
            super().__init__(parent)
            size = parent.size()
            self.setStartValue(QSize(0, 0))
            self.setEndValue(size)
            self.setDirection(
                QAbstractAnimation.Direction.Forward if variant == "in" else QAbstractAnimation.Direction.Backward)
            self.setDuration(1000)
            self.setEasingCurve(QEasingCurve.Type.OutBack)
            self.valueChanged.connect(self.update_size)
        
        def update_size(self, value):
            self.parent().setFixedSize(value)
    
    class CentreAnimation(QWidget):
        def __init__(self, parent):
            super().__init__(parent)
            self.setProperty("animationValue", 0)
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.timeout)
            
            self.error = False
        
        def timeout(self):
            self.setProperty("animationValue", (self.property("animationValue") or 0) + 0.1)
        
        def paintEvent(self, a0):
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            gradient = QConicalGradient(QRectF(self.rect()).center(), self.property("animationValue") % 360)
            gradient.setColorAt(0.0, self.beRed(getBorderColour(is_highlight=True), 75 if self.error else 0))
            gradient.setColorAt(
                1.0,
                self.beRed(
                    getBackgroundColour(is_highlight=True),
                    75 if self.error else 0
                )
            )
            painter.setPen(Qt.GlobalColor.transparent)
            painter.setBrush(QBrush(gradient))
            painter.drawEllipse(self.rect())
        
        def beRed(self, colour, value=25):
            r, g, b = Colour(colour)
            r += value
            g -= value
            b -= value
            return Colour(r, g, b)
        
        def setError(self, isError=True):
            self.error = isError
            if isError:
                self.timer.stop()
            else:
                self.timer.start()
        
        def showEvent(self, a0):
            super().showEvent(a0)
            self.setProperty("animationValue", 0)
            self.timer.start(1)
            self.error = False
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.__centreAnimation = self.CentreAnimation(self)
        self.__centreAnimation.setFixedSize(96, 96)
        self.__centreAnimation.setStyleSheet("background: transparent;")
        dsg = QGraphicsDropShadowEffect(self.__centreAnimation)
        dsg.setBlurRadius(30)
        dsg.setOffset(0, 4)
        dsg.setColor(QColor(0, 0, 0, 200))
        self.__centreAnimation.setGraphicsEffect(dsg)
        self.__statusLabel = Label(self)
        self.__statusLabel.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.__reloadButton = PushButton(self)
        self.__reloadButton.setText("重新加载")
        self.__loadingTimer = QTimer(self)
        self.__loadingTimer.timeout.connect(self.__updateText)
        self.destroyed.connect(lambda: self.__loadingTimer.stop())
        self.__counter = 0
        self.hide()
    
    def __del__(self):
        try:
            self.__loadingTimer.stop()
        except RuntimeError:
            pass
    
    def event(self, e):
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setGeometry(self.parent().rect())
        try:
            self.__centreAnimation.setGeometry(QRect(int(self.width() / 2 - (self.__centreAnimation.width() / 2)),
                                                     int(self.height() / 2 - (self.__centreAnimation.height() / 2)),
                                                     self.__centreAnimation.width(),
                                                     self.__centreAnimation.height()))
        except AttributeError:
            pass
        try:
            self.__statusLabel.adjustSize()
            self.__statusLabel.setGeometry(QRect(int(self.width() / 2 - (self.__statusLabel.width() / 2)),
                                                 int(self.height() / 2 - (self.__statusLabel.height() / 2)) + 96 + 30,
                                                 self.__statusLabel.width(),
                                                 self.__statusLabel.height()))
        except AttributeError:
            pass
        try:
            self.__reloadButton.adjustSize()
            self.__reloadButton.setGeometry(
                QRect(self.__statusLabel.x() + self.__statusLabel.width() + 2, self.__statusLabel.y(),
                      self.__reloadButton.width(), self.__reloadButton.height()))
        except AttributeError:
            pass
        self.raise_()
        return super().event(e)
    
    def paintEvent(self, a0):
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        if not self.__centreAnimation.error:
            self.setStyleSheet(
                f"background: rgb({str(getBackgroundColour(is_tuple=True)).replace('(', '').replace(')', '')});")
        else:
            self.setStyleSheet(f"background: rgb({'255, 200, 200' if getTheme() == Theme.Light else '100, 50, 50'});")
        return super().paintEvent(a0)
    
    def __updateText(self):
        self.__counter += 1
        self.__statusLabel.setText(self.tr("LoadingAnimation.statusLabel.Text") + "." * (self.__counter % 4))
    
    def start(self, ani=True):
        self.__centreAnimation.setFixedSize(96, 96)
        self.__centreAnimation.setError(False)
        self.__statusLabel.setText(self.tr("LoadingAnimation.statusLabel.Text"))
        self.__reloadButton.hide()
        self.__reloadButton.setDown(False)
        if ani:
            self.setStyleSheet("background: transparent")
            self.TransparencyAnimation(self, "in").start()
            self.SizingAnimation(self.__centreAnimation, "in").start()
        else:
            self.setStyleSheet(
                f"background: rgb({str(getBackgroundColour(is_tuple=True)).replace('(', '').replace(')', '')});")
        self.__counter = 0
        self.__loadingTimer.start(1000)
        self.show()
    
    def finish(self, ani=True, failed=False):
        try:
            self.__loadingTimer.moveToThread(self.thread())
            self.__loadingTimer.stop()
            if not failed:
                if ani:
                    self.TransparencyAnimation(self, "out").start()
                    self.SizingAnimation(self.__centreAnimation, "out").start()
                    hideani = self.HideAnimation(self)
                    self.destroyed.connect(hideani.terminate)
                    hideani.start()
                else:
                    self.hide()
                self.__statusLabel.setText(self.tr("LoadingAnimation.statusLabel.SuccessText"))
            else:
                self.setStyleSheet(
                    f"background: rgb({'255, 200, 200' if getTheme() == Theme.Light else '100, 50, 50'});")
                self.__statusLabel.setText(self.tr("LoadingAnimation.statusLabel.FailedText"))
                self.__reloadButton.show()
                self.__centreAnimation.setError()
        except RuntimeError:
            pass
    
    def addReloadFunction(self, function):
        self.__reloadButton.pressed.connect(function)
    
    def setReloadText(self, text):
        self.__reloadButton.setText(text)
    
    def hideEvent(self, *args, **kwargs):
        try:
            self.__loadingTimer.stop()
            self.destroy()
        except RuntimeError:
            pass


class LoginDialogue(MaskedDialogue):
    class LoginThread(QThread):
        loginFinished = pyqtSignal()
        
        def __init__(self, token, parent=None):
            super().__init__(parent)
            self.token = token
        
        def run(self):
            try:
                datas = login_user(bytes(self.token, encoding="utf-8"))
                if datas is not None:
                    update_user(datas)
            except:
                traceback.print_exc()
            self.loginFinished.emit()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: white")
        self.setWindowTitle(self.tr("LoginDialogue.Title"))
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(11, 43, 11, 11)
        self.content = Label(self)
        self.content.setText(self.tr("LoginDialogue.content.Text"))
        self.content.setWordWrap(True)
        self.content.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.TextSelectableByKeyboard)
        self.verticalLayout.addWidget(self.content)
        self.horizontalLayout = QHBoxLayout(self)
        self.lineEdit = LineEdit(self)
        self.lineEdit.setInputMask("X.XXXX_XXX.X.X.XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX;X")
        self.horizontalLayout.addWidget(self.lineEdit)
        self.toolButton = ToolButton(self)
        self.toolButton.setText(self.tr("LoginDialogue.toolButton.Text"))
        self.toolButton.pressed.connect(self.process_login)
        self.horizontalLayout.addWidget(self.toolButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.pushButton = PushButton(self)
        self.pushButton.setText(self.tr("LoginDialogue.pushButton.Text"))
        self.pushButton.pressed.connect(lambda: webb.open(
            "https://login.live.com/oauth20_authorize.srf?client_id=00000000402b5328&response_type=code&scope=service%3A%3Auser.auth.xboxlive.com%3A%3AMBI_SSL&redirect_uri=https%3A%2F%2Flogin.live.com%2Foauth20_desktop.srf"))
        self.verticalLayout.addWidget(self.pushButton)
        self.trybtn = PushButton(self)
        self.trybtn.setText(self.tr("LoginDialogue.trybtn.Text"))
        self.trybtn.pressed.connect(self.open_new_login)
        self.verticalLayout.addWidget(self.trybtn)
        spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(spacer)
        self.resize(100, 300)
        self.setLayout(self.verticalLayout)
        webb.open(
            "https://login.live.com/oauth20_authorize.srf?client_id=00000000402b5328&response_type=code&scope=service%3A%3Auser.auth.xboxlive.com%3A%3AMBI_SSL&redirect_uri=https%3A%2F%2Flogin.live.com%2Foauth20_desktop.srf")
    
    def process_login(self):
        token = self.lineEdit.text()
        token = token.split(".")[-1]
        print(token)
        thread = self.LoginThread(token)
        thread.start()
        self.hide()
    
    def open_new_login(self):
        self.hide()
        w = LoginWindow(frame)
        w.exec()
    
    def paintEvent(self, a0, **kwargs):
        background = QPixmap(self.size())
        p = QPainter(background)
        x = 0 if self.isMaximized() else -self.geometry().x()
        y = 0 if self.isMaximized() else -self.geometry().y()
        p.fillRect(
            QRect(x, y, QGuiApplication.primaryScreen().geometry().width(),
                  QGuiApplication.primaryScreen().geometry().height()),
            QGradient(QGradient.Preset.FreshOasis if getTheme() == Theme.Light else QGradient.Preset.NightSky))
        p.end()
        scene = QGraphicsScene()
        item = QGraphicsPixmapItem()
        item.setPixmap(background)
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(settings["Settings"]["LauncherSettings"]["Customise"]["BackgroundBlur"])
        item.setGraphicsEffect(blur)
        scene.addItem(item)
        img = QPixmap(background.size())
        img.fill(Qt.GlobalColor.transparent)
        ptr = QPainter(img)
        scene.render(ptr, QRectF(img.rect()), QRectF(img.rect()))
        ptr.end()
        painter = QPainter(self)
        rect = QRect(-20, -20, self.width() + 40, self.height() + 40)
        painter.drawPixmap(rect, img)


class LoginWindow(MaskedDialogue):
    class LoginThread(QThread):
        loginFinished = pyqtSignal()
        
        def __init__(self, token, parent=None):
            super().__init__(parent)
            self.token = token
        
        def run(self):
            try:
                datas = login_user(bytes(self.token, encoding="utf-8"))
                update_user(datas)
            except:
                traceback.print_exc()
            self.loginFinished.emit()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("LoginWindow.Title"))
        self.resize(800, 600)
        self.view = QWebEngineView(self)
        self.view.show()
        self.view.load(QUrl(
            "https://login.live.com/oauth20_authorize.srf?client_id=00000000402b5328&response_type=code&scope=service%3A%3Auser.auth.xboxlive.com%3A%3AMBI_SSL&redirect_uri=https%3A%2F%2Flogin.live.com%2Foauth20_desktop.srf"))
        self.view.urlChanged.connect(self.assert_url)
        self.view.loadStarted.connect(self.loadStarted)
        self.view.loadFinished.connect(self.loadFinished)
        self.view.page().profile().setHttpAcceptLanguage(current_language)
        self.progress = LoadingAnimation(self)
        self.progress.hide()
        self.isFirstShow = False
        self.titleBar.raise_()
        self.update()
        self.setResizeEnabled(True)
    
    def assert_url(self):
        if re.match(r"https://login\.live\.com/oauth20_desktop\.srf\?error=.+&error_description=.+&lc=.+",
                    self.view.url().toString()):
            self.hide()
        result = re.match(r"https://login\.live\.com/oauth20_desktop\.srf\?code=.+&lc=.+", self.view.url().toString())
        if result:
            pos = re.search(r"code=.+&", self.view.url().toString())
            if pos:
                code = pos.string
                token = code.split("=")[1]
                token = token.split(".")[-1].split("&")[0]
                thread = self.LoginThread(token)
                thread.start()
                self.hide()
    
    def loadStarted(self):
        self.progress.start(ani=self.isFirstShow)
        self.isFirstShow = True
    
    def loadFinished(self):
        self.progress.finish()
    
    def resizeEvent(self, a0, **kwargs):
        super().resizeEvent(a0)
        if hasattr(self, "view"):
            self.view.setGeometry(self.rect())
    
    def showEvent(self, a0):
        super().showEvent(a0)
        self.isFirstShow = False
    
    def paintEvent(self, a0, **kwargs):
        background = QPixmap(self.size())
        p = QPainter(background)
        x = 0 if self.isMaximized() else -self.geometry().x()
        y = 0 if self.isMaximized() else -self.geometry().y()
        p.fillRect(
            QRect(x, y, QGuiApplication.primaryScreen().geometry().width(),
                  QGuiApplication.primaryScreen().geometry().height()),
            QGradient(QGradient.Preset.FreshOasis if getTheme() == Theme.Light else QGradient.Preset.NightSky))
        p.end()
        scene = QGraphicsScene()
        item = QGraphicsPixmapItem()
        item.setPixmap(background)
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(settings["Settings"]["LauncherSettings"]["Customise"]["BackgroundBlur"])
        item.setGraphicsEffect(blur)
        scene.addItem(item)
        img = QPixmap(background.size())
        img.fill(Qt.GlobalColor.transparent)
        ptr = QPainter(img)
        scene.render(ptr, QRectF(img.rect()), QRectF(img.rect()))
        ptr.end()
        painter = QPainter(self)
        rect = QRect(-20, -20, self.width() + 40, self.height() + 40)
        painter.drawPixmap(rect, img)


class SaveEditingWindow(RoundedDialogue):
    def __init__(self, parent=None, savename="", savedir=None):
        super().__init__(parent)
        if not savedir:
            savedir = minecraft_path / "saves"
        self.savedir = savedir / savename
        self.leveldata = LoadData(self.savedir / "level.dat")
        
        self.resize(800, 600)
        
        self.toolBox = ToolBox(self)
        self.basicDataPage = QFrame(self.toolBox)
        self.verticalLayout = QVBoxLayout(self.basicDataPage)
        self.panel = Panel(self.basicDataPage)
        self.verticalLayout_2 = QVBoxLayout(self.panel)
        self.label = Label(self.panel)
        self.label.setWordWrap(True)
        self.verticalLayout_2.addWidget(self.label)
        self.verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.verticalLayout_2.addItem(self.verticalSpacer)
        self.verticalLayout.addWidget(self.panel)
        self.toolBox.addItem(self.basicDataPage, self.tr("SaveEditingWindow.Page1.Title"))  # 基础数据
        app.registerRetranslateFunction(self.retranslateUI)
        self.retranslateUI()
    
    def retranslateUI(self):
        print(self.leveldata)
        value_localisations = {
            "difficulty": {
                nbtlib.Byte(0): self.tr("SaveEditingWindow.ValueLocalisations.Difficulty.0"),  # 和平
                nbtlib.Byte(1): self.tr("SaveEditingWindow.ValueLocalisations.Difficulty.1"),  # 简单
                nbtlib.Byte(2): self.tr("SaveEditingWindow.ValueLocalisations.Difficulty.2"),  # 普通
                nbtlib.Byte(3): self.tr("SaveEditingWindow.ValueLocalisations.Difficulty.3")  # 困难
            },
            "gamemode": {
                nbtlib.Int(0): self.tr("SaveEditingWindow.ValueLocalisations.Gamemode.0"),  # 生存
                nbtlib.Int(1): self.tr("SaveEditingWindow.ValueLocalisations.Gamemode.1"),  # 创造
                nbtlib.Int(2): self.tr("SaveEditingWindow.ValueLocalisations.Gamemode.2"),  # 冒险
                nbtlib.Int(3): self.tr("SaveEditingWindow.ValueLocalisations.Gamemode.3"),  # 旁观
                "hardcore": self.tr("SaveEditingWindow.ValueLocalisations.Gamemode.4")  # 极限
            }
        }
        self.label.setText(self.tr("SaveEditingWindow.Infomation.Text").format(
            self.leveldata['LevelName'],
            value_localisations['difficulty'][
                self.leveldata['Difficulty']] if not
            self.leveldata['hardcore'] else
            value_localisations['gamemode'][
                'hardcore'],
            time.strftime(settings["Settings"]["LauncherSettings"]["Customise"]["DateTimeFormat"],
                          time.localtime(
                              self.leveldata[
                                  'LastPlayed'] / 1000)),
            value_localisations['gamemode'][
                self.leveldata['Player'][
                    'playerGameType']],
            self.leveldata['Player']['Health'] / 1,
            self.leveldata['Player']['Health'] / 2,
            self.leveldata['Player'][
                'foodLevel'] / 1, list(
                map(lambda x: x / 1, self.leveldata['Player']['Pos']))))
        self.toolBox.setItemText(self.toolBox.indexOf(self.basicDataPage), "基础数据")
    
    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        if hasattr(self, "toolBox"):
            self.toolBox.setGeometry(5, 35, self.width() - 10, self.height() - 40)
    
    def paintEvent(self, a0, **kwargs):
        background = QPixmap(self.size())
        p = QPainter(background)
        x = 0 if self.isMaximized() else -self.geometry().x()
        y = 0 if self.isMaximized() else -self.geometry().y()
        p.fillRect(
            QRect(x, y, QGuiApplication.primaryScreen().geometry().width(),
                  QGuiApplication.primaryScreen().geometry().height()),
            QGradient(QGradient.Preset.FreshOasis if getTheme() == Theme.Light else QGradient.Preset.NightSky))
        p.end()
        scene = QGraphicsScene()
        item = QGraphicsPixmapItem()
        item.setPixmap(background)
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(settings["Settings"]["LauncherSettings"]["Customise"]["BackgroundBlur"])
        item.setGraphicsEffect(blur)
        scene.addItem(item)
        img = QPixmap(background.size())
        img.fill(Qt.GlobalColor.transparent)
        ptr = QPainter(img)
        scene.render(ptr, QRectF(img.rect()), QRectF(img.rect()))
        ptr.end()
        painter = QPainter(self)
        rect = QRect(-20, -20, self.width() + 40, self.height() + 40)
        painter.drawPixmap(rect, img)


# class MultiPageBase(QFrame):
#     def __init__(self, parent):
#         super().__init__(parent)
#         self.verticalLayout = QVBoxLayout(self)
#         self.verticalLayout.setObjectName(u"verticalLayout")
#         self.navigationFrame = Panel(self)
#         self.navigationFrameScrollAreaLayout = QVBoxLayout(self.navigationFrame)
#         self.navigationFrameScrollAreaLayout.setContentsMargins(0, 0, 0, 0)
#         self.navigationFrameScrollArea = ScrollArea(self.navigationFrame)
#         self.navigationFrameScrollAreaLayout.addWidget(self.navigationFrameScrollArea)
#         self.navigationFrameScrollArea.setFixedHeight(self.navigationFrame.height() + 10)
#         self.navigationFrameScrollAreaWidgetContent = QWidget()
#         self.horizontalLayout = QHBoxLayout(self.navigationFrameScrollAreaWidgetContent)
#         self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
#         self.pages = {}
#
#         self.pushButton = PushButton(self.navigationFrameScrollAreaWidgetContent)
#         self.pushButton.setObjectName(u"pushButton")
#         self.pushButton.setCheckable(True)
#         self.pushButton.setChecked(True)
#         self.pushButton.setAutoExclusive(True)
#         self.pushButton.pressed.connect(lambda: self.update_page(self.pushButton))
#
#         self.horizontalLayout.addWidget(self.pushButton)
#
#         self.pushButton_2 = PushButton(self.navigationFrameScrollAreaWidgetContent)
#         self.pushButton_2.setObjectName(u"pushButton_2")
#         self.pushButton_2.setCheckable(True)
#         self.pushButton_2.setAutoExclusive(True)
#         self.pushButton_2.pressed.connect(lambda: self.update_page(self.pushButton_2))
#
#         self.horizontalLayout.addWidget(self.pushButton_2)
#
#         self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
#
#         self.horizontalLayout.addItem(self.horizontalSpacer)
#
#         self.navigationFrameScrollArea.setWidget(self.navigationFrameScrollAreaWidgetContent)
#         self.navigationFrameScrollArea.setWidgetResizable(True)
#
#         self.verticalLayout.addWidget(self.navigationFrame)
#
#         self.stackedWidget = AnimatedStackedWidget(self)
#         self.stackedWidget.setObjectName(u"stackedWidget")
#         self.page = QWidget()
#         self.page.setObjectName(u"page")
#         self.stackedWidget.addWidget(self.page)
#         self.pages[self.pushButton] = self.page
#         self.page_2 = QWidget()
#         self.page_2.setObjectName(u"page_2")
#         self.stackedWidget.addWidget(self.page_2)
#         self.pages[self.pushButton_2] = self.page_2
#
#         self.verticalLayout.addWidget(self.stackedWidget, 1)
#
#         app.registerRetranslateFunction(self.retranslateUi)
#         self.retranslateUi()
#         #
#         # QMetaObject.connectSlotsByName(Form)
#
#     # setupUi
#
#     def retranslateUi(self):
#         self.pushButton.setText("Page1")
#         self.pushButton_2.setText("Page2")
#     # retranslateUi
#
#     def update_page(self, btn):
#         self.stackedWidget.setCurrentWidget(self.pages[btn])


class MainPage(QFrame):
    class VersionSettingsPage(AcrylicBackground):
        frameClosed = pyqtSignal()
        
        class VersionDetailsPage(QFrame):
            def __init__(self, parent=None, version=None):
                super().__init__(parent)
                self.version = version
                
                self.verticalLayout = QVBoxLayout(self)
                
                self.toolBox = ToolBox(self)
                self.verticalLayout.addWidget(self.toolBox)
                
                self.versionDetails = QFrame(self.toolBox)
                
                self.verticalLayout_2 = QVBoxLayout(self.versionDetails)
                
                self.versionPanel = Panel(self.versionDetails)
                
                self.horizontalLayout_3 = QHBoxLayout(self.versionPanel)
                
                self.versionNameLabel = Label(self.versionPanel)
                self.horizontalLayout_3.addWidget(self.versionNameLabel, 1)
                
                self.toolButton = ToolButton(self.versionDetails)
                self.toolButton.setPopupMode(ToolButton.ToolButtonPopupMode.InstantPopup)
                self.horizontalLayout_3.addWidget(self.toolButton)
                
                self.verticalLayout_2.addWidget(self.versionPanel)
                
                self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
                
                self.verticalLayout_2.addItem(self.verticalSpacer)
                
                self.toolBox.addItem(self.versionDetails,
                                     self.tr("MainPage.VersionSettingsPage.VersionDetailsPage.Page1.Title"))
                
                self.versionSaves = QFrame(self.toolBox)
                self.verticalLayout_3 = QVBoxLayout(self.versionSaves)
                
                self.listView = ListView(self.versionSaves)
                self.listView.setEditTriggers(ListView.EditTrigger.NoEditTriggers)
                self.listView.pressed.connect(self.startEditSave)
                self.savesModel = QStandardItemModel()
                self.listView.setModel(self.savesModel)
                
                self.verticalLayout_3.addWidget(self.listView)
                
                self.listSaves()
                
                self.toolBox.addItem(self.versionSaves,
                                     self.tr("MainPage.VersionSettingsPage.VersionDetailsPage.Page2.Title"))
                
                app.registerRetranslateFunction(self.retranslateUI)
                self.retranslateUI()
            
            def retranslateUI(self):
                self.versionNameLabel.setText(
                    self.tr("MainPage.VersionSettingsPage.VersionDetailsPage.versionNameLabel.Text").format(
                        self.version))
                self.toolButton.setText(
                    self.tr("MainPage.VersionSettingsPage.VersionDetailsPage.toolButton.Text"))
                self.toolBox.setItemText(self.toolBox.indexOf(self.versionDetails),
                                         self.tr("MainPage.VersionSettingsPage.VersionDetailsPage.Page1.Title"))
                self.toolBox.setItemText(self.toolBox.indexOf(self.versionSaves),
                                         self.tr("MainPage.VersionSettingsPage.VersionDetailsPage.Page2.Title"))
                self.generateMenu()
            
            def generateMenu(self):
                menu = RoundedMenu(self.toolButton)
                action1 = QAction(menu)
                action1.setText(
                    self.tr("MainPage.VersionSettingsPage.VersionDetailsPage.toolButton.Item1.Text"))
                action1.triggered.connect(self.openVersionFolder)
                menu.addAction(action1)
                action2 = QAction(menu)
                action2.setText(
                    self.tr("MainPage.VersionSettingsPage.VersionDetailsPage.toolButton.Item2.Text"))
                action2.triggered.connect(self.openVersionSettingsFile)
                menu.addAction(action2)
                menu.addSeparator()
                action3 = QAction(menu)
                action3.setText(
                    self.tr("MainPage.VersionSettingsPage.VersionDetailsPage.toolButton.Item3.Text"))
                action3.triggered.connect(self.generateLaunchScript)
                menu.addAction(action3)
                self.toolButton.setMenu(menu)
            
            def openVersionFolder(self):
                if self.version:
                    if platform.system().lower() == "windows":
                        os.startfile(minecraft_path / "versions" / self.version)
                    elif platform.system().lower() == "linux":
                        os.system(f"xdg-open \"{str((minecraft_path / 'versions' / self.version).absolute())}\"")
            
            def openVersionSettingsFile(self):
                if self.version:
                    if platform.system().lower() == "windows":
                        os.startfile(minecraft_path / "options.txt")
                    elif platform.system().lower() == "linux":
                        os.system(f"xdg-open \"{str((minecraft_path / 'options.txt').absolute())}\"")
            
            def generateLaunchScript(self):
                if self.version:
                    # I've written the function for generating command.
                    pass
            
            def listSaves(self):
                self.savesModel.clear()
                for idx, dire in enumerate(os.listdir(minecraft_path / "saves")):
                    self.savesModel.setItem(idx, QStandardItem(dire))
                self.listView.setModel(self.savesModel)
            
            def startEditSave(self, index):
                saveName = self.savesModel.itemData(index)[0]
                saveEditWindow = SaveEditingWindow(frame, saveName, minecraft_path / "saves")
                saveEditWindow.show()
            
            def paintEvent(self, a0):
                painter = QPainter(self)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                colour = getBackgroundColour()
                colour.setAlpha(128)
                painter.setBrush(colour)
                painter.drawRect(self.rect())
        
        def __init__(self, parent=None):
            super().__init__(parent, getBackgroundColour(), QColor(0, 0, 255, 200), 10)
            self.verticalLayout = QVBoxLayout(self)
            
            self.topPanel = Panel(self)
            self.horizontalLayout = QHBoxLayout(self.topPanel)
            
            self.closeButton = CloseButton(self.topPanel)
            self.closeButton.pressed.connect(self.closeFrame)
            self.horizontalLayout.addWidget(self.closeButton)
            
            self.horizontalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
            self.horizontalLayout.addItem(self.horizontalSpacer)
            
            self.verticalLayout.addWidget(self.topPanel)
            
            self.listWidget = ListWidget(self)
            
            versions = GetVersionByScanDirectory(minecraft_path)
            if versions:
                for version in versions:
                    self.listWidget.addItem(version)
            
            self.listWidget.itemDoubleClicked.connect(self.startSettings)
            
            self.verticalLayout.addWidget(self.listWidget)
            
            self.versionDetailsPage = None
        
        def paintEvent(self, a0):
            self.setTintColour(getBackgroundColour())
            super().paintEvent(a0)
        
        def event(self, a0):
            if hasattr(self, "versionDetailsPage") and self.versionDetailsPage:
                self.versionDetailsPage.setGeometry(self.listWidget.geometry())
                self.versionDetailsPage.raise_()
            return super().event(a0)
        
        def closeFrame(self):
            if not self.versionDetailsPage:
                self.close()
                self.frameClosed.emit()
            else:
                self.versionDetailsPage.close()
                self.versionDetailsPage = None
        
        def startSettings(self, item):
            self.versionDetailsPage = self.VersionDetailsPage(self, item.text())
            self.versionDetailsPage.show()
    
    class LaunchThread(QThread):
        launched = pyqtSignal(tuple)
        
        def __init__(self, minecraft_path, version, player, parent=None):
            super().__init__(parent)
            self.minecraft_path = minecraft_path
            self.version = version
            self.player = player
        
        def run(self):
            result = LaunchMinecraft(
                self.minecraft_path,
                self.version,
                None if settings["Settings"]["JavaSettings"]["Java"]["Path"]["is_auto"] else
                settings["Settings"]["JavaSettings"]["Java"]["Path"]["value"],
                settings["Settings"]["JavaSettings"]["Java"]["LaunchMode"],
                CMCL_version[0], "CMCL", None, None, settings["Settings"]["JavaSettings"]["JVM"]["Arg"]["value"],
                settings["Settings"]["JavaSettings"]["JVM"]["Arg"]["is_override"],
                settings["Settings"]["GameSettings"]["ExtraGameCommand"], None, None,
                self.player
            )
            self.launched.emit(result)
    
    def __init__(self, parent):
        super().__init__(parent)
        self.version = None
        self.games = []
        
        self.verticalLayout = QVBoxLayout(self)
        self.scrollArea = ScrollArea(self)
        self.verticalLayout.addWidget(self.scrollArea)
        self.scrollAreaContentWidget = QWidget()
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaContentWidget)
        self.bottom_space = QSpacerItem(0, 80, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.verticalLayout_2.addItem(self.bottom_space)
        self.scrollArea.setWidget(self.scrollAreaContentWidget)
        self.scrollAreaContentWidget.adjustSize()
        self.scrollArea.setWidgetResizable(True)
        self.bottomPanel = Panel(self)
        self.bottomPanel.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.horizontalLayout = QHBoxLayout(self.bottomPanel)
        self.horizontalLayout.setContentsMargins(1, 1, 1, 1)
        self.spacerItem = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.horizontalLayout.addItem(self.spacerItem)
        self.launch_btn = PushButton(self.bottomPanel)
        self.launch_btn.pressed.connect(self.b4launch)
        self.horizontalLayout.addWidget(self.launch_btn)
        self.select_version_btn = ToolButton(self.bottomPanel)
        self.select_version_btn.setPopupMode(ToolButton.ToolButtonPopupMode.InstantPopup)
        self.update_menu()
        self.horizontalLayout.addWidget(self.select_version_btn)
        self.update_version_lst_btn = ToolButton(self.bottomPanel)
        self.update_version_lst_btn.pressed.connect(self.update_menu)
        self.horizontalLayout.addWidget(self.update_version_lst_btn)
        self.change_dir_btn = PushButton(self.bottomPanel)
        self.change_dir_btn.pressed.connect(self.setMinecraftDir)
        self.horizontalLayout.addWidget(self.change_dir_btn)
        self.settings_btn = PushButton(self.bottomPanel)
        self.settings_btn.pressed.connect(self.show_version_settings_page)
        self.horizontalLayout.addWidget(self.settings_btn)
        spacer2 = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.horizontalLayout.addItem(spacer2)
        self.stop_all_games_btn = ToolButton(self)
        self.stop_all_games_btn.setFixedSize(QSize(64, 64))
        self.stop_all_games_btn.setIconSize(QSize(54, 54))
        self.stop_all_games_btn.pressed.connect(self.stop_all_games)
        timer = QTimer(self)
        timer.timeout.connect(self.update_icon)
        timer.start(100)
        self.retranslateUI()
        app.registerRetranslateFunction(self.retranslateUI)
        self.bottomPanelIsShow = True
        self.versionSettings = None
        self.versionSettingsY = None
    
    def retranslateUI(self):
        self.launch_btn.setText(self.tr("MainPage.launch_btn.Text"))
        self.select_version_btn.setText(self.version or self.tr("MainPage.select_version_btn.DefaultText"))
        self.change_dir_btn.setText(self.tr("MainPage.change_dir_btn.Text"))
        self.settings_btn.setText(self.tr("MainPage.settings_btn.Text"))
        self.stop_all_games_btn.setToolTip(self.tr("MainPage.stop_all_games_btn.ToolTip"))
        self.update_version_lst_btn.setToolTip(self.tr("MainPage.update_version_lst_btn.ToolTip"))  # 重新加载版本列表
        self.change_dir_btn.setToolTip(
            self.tr("MainPage.change_dir_btn.ToolTip").format(str(minecraft_path.absolute())))
    
    def select_version(self, version):
        self.version = version
        self.select_version_btn.setText(self.version or self.tr("MainPage.select_version_btn.DefaultText"))
    
    def b4launch(self):
        if not player:
            UserPage.startLogin()
            if not player:
                return
        self.launch()
    
    def launch(self):
        if self.version:
            self.launch_btn.setEnabled(False)
            try:
                launch_thread = self.LaunchThread(minecraft_path, self.version, player, self)
                launch_thread.launched.connect(lambda x: self.launched(x))
                launch_thread.start()
            finally:
                self.launch_btn.setEnabled(True)
    
    def launched(self, result):
        print(result)
        if result[0] == "Successfully":
            self.games.append(result[1])
            tip = PopupTip(frame)
            label = Label(tip)
            label.setText(self.tr("MainPage.VersionLaunchedTip.Label.Text"))
            label.adjustSize()
            tip.setCentralWidget(label)
            tip.setGeometry(QRect(0, 0, 300, 64))
            tip.tip(PopupTip.PopupPosition.RIGHT, 3000)
            
            # loggingwindow = GameLoggingWindow(None, result[1])
            # loggingwindow.show()
        else:
            tip = PopupTip(frame)
            label = Label(tip)
            label.setText(self.tr("MainPage.VersionLaunchFailedTip.Label.Text").format(result[1]))
            label.adjustSize()
            tip.setCentralWidget(label)
            tip.setGeometry(QRect(0, 0, 300, 64))
            tip.tip(PopupTip.PopupPosition.RIGHT, 3000)
    
    def setMinecraftDir(self):
        global minecraft_path
        self.change_dir_btn.setDown(False)
        path = QFileDialog(self).getExistingDirectory(self, self.tr("MainPage.SelectDir.Title"), str(minecraft_path))
        if path:
            minecraft_path = Path(path)
            settings["Settings"]["LauncherSettings"]["CurrentMinecraftDirectory"] = str(Path(path).absolute())
            self.update_menu()
            self.change_dir_btn.setToolTip(
                self.tr("MainPage.change_dir_btn.ToolTip").format(str(minecraft_path.absolute())))
    
    def update_menu(self):
        menu = QMenu()
        menu.showEvent = lambda a0: menu.setStyleSheet("QMenu{ border: none; background: transparent; }")
        menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        listWidget = ListWidget(menu)
        maximumWidth = listWidget.width()
        
        versions = GetVersionByScanDirectory(minecraft_path=minecraft_path)
        if isinstance(versions, list) and len(versions) >= 1:
            for version in versions:
                action = QListWidgetItem(listWidget)
                action.setText(version)
                listWidget.addItem(action)
                maximumWidth = max(maximumWidth, listWidget.fontMetrics().boundingRect(version).width())
            listWidget.itemClicked.connect(lambda version: self.select_version(version.text()))
            self.select_version(versions[0])
        else:
            listWidget.addItem(self.tr("MainPage.NoVersionYet.Text"))
        menu.resizeEvent = lambda e: listWidget.setGeometry(menu.rect())
        menu.addAction("")
        listWidget.adjustSize()
        listWidget.setFixedWidth(maximumWidth + listWidget.verticalScrollBar().width())
        menu.setFixedHeight(app.primaryScreen().geometry().height())
        menu.setFixedSize(listWidget.size())
        self.select_version_btn.setMenu(menu)
    
    def show_version_settings_page(self):
        self.versionSettingsY = self.height()
        self.versionSettings = self.VersionSettingsPage(self)
        self.versionSettings.frameClosed.connect(self.hide_version_settings_page)
        rect = self.rect().adjusted(1, 1, -1, -1)
        self.versionSettings.setGeometry(rect)
        self.versionSettings.grabBehind()
        rect.moveTo(0, self.versionSettingsY)
        self.versionSettings.setGeometry(rect)
        self.versionSettings.show()
    
    def hide_version_settings_page(self):
        self.versionSettings = None
        self.versionSettingsY = None
    
    def stop_all_games(self):
        for popen in self.games:
            popen.kill()
        self.games.clear()
    
    def update_icon(self):
        self.stop_all_games_btn.setIcon(QIcon(f":/StopGame-{'black' if getTheme() == Theme.Light else 'white'}.svg"))
        self.update_version_lst_btn.setIcon(
            QIcon(f":/ReloadVersions-{'black' if getTheme() == Theme.Light else 'white'}.svg"))
    
    def resizeEvent(self, *args, **kwargs):
        super().resizeEvent(*args, **kwargs)
        try:
            self.bottomPanel.setGeometry(
                QRect(5, (self.height() - 80 if self.bottomPanelIsShow else self.height() + 62), self.width() - 10, 62))
            if self.bottomPanelIsShow:
                if self.verticalLayout_2.indexOf(self.bottom_space) == -1:
                    self.verticalLayout_2.addItem(self.bottom_space)
            else:
                if self.verticalLayout_2.indexOf(self.bottom_space) != -1:
                    self.verticalLayout_2.removeItem(self.bottom_space)
            self.stop_all_games_btn.setGeometry(
                QRect(self.width() - self.stop_all_games_btn.width() - 10,
                      self.height() - self.stop_all_games_btn.height() - 100,
                      self.stop_all_games_btn.width(), self.stop_all_games_btn.height()))
        except AttributeError:
            pass
    
    def event(self, a0):
        if hasattr(self, "versionSettings") and self.versionSettings:
            rect = self.rect().adjusted(1, 1, -1, -1)
            rect.moveTo(0, self.versionSettingsY)
            self.versionSettings.setGeometry(rect)
            self.versionSettings.raise_()
        if hasattr(self, "versionSettingsY") and self.versionSettingsY:
            if self.versionSettingsY > 0:
                self.versionSettingsY -= self.versionSettingsY // 16 + 1
            else:
                self.versionSettingsY = 0
        return super().event(a0)


class DownloadPage(QFrame):
    class DownloadVanilla(QFrame):
        class DownloadOptions(AcrylicBackground):
            frameClosed = pyqtSignal()
            
            class DownloadVersionThread(QThread):
                def __init__(self, parent, version=None, path="."):
                    super().__init__(parent)
                    self.__version = version
                    self.__path = Path(path)
                
                def run(self):
                    if self.__version:
                        DownloadMinecraft(self.__path, self.__version)
            
            class LoaderDialogue(MaskedDialogue):
                def __init__(self, parent):
                    super().__init__(parent)
                    self.verticalLayout = QVBoxLayout(self)
                    self.verticalLayout.setContentsMargins(5, 35, 5, 5)
                    self.groupBox = GroupBox(self)
                    self.groupBox.setTitle("Forge")
                    self.groupBox.setCheckable(True)
                    self.groupBox.setChecked(False)
                    self.groupBox.clicked.connect(lambda: self.updateGroupBoxState(1))
                    self.verticalLayout.addWidget(self.groupBox)
                    self.groupBox_2 = GroupBox(self)
                    self.groupBox_2.setTitle("Fabric & Fabric API")
                    self.groupBox_2.setCheckable(True)
                    self.groupBox_2.setChecked(False)
                    self.groupBox_2.clicked.connect(lambda: self.updateGroupBoxState(2))
                    self.verticalLayout.addWidget(self.groupBox_2)
                    
                    self.horizontalLayout_2 = QHBoxLayout(self.groupBox_2)
                    self.groupBox_4 = GroupBox(self.groupBox_2)
                    self.groupBox_4.setTitle("Fabric")
                    self.horizontalLayout_2.addWidget(self.groupBox_4)
                    self.groupBox_5 = GroupBox(self.groupBox_2)
                    self.groupBox_5.setTitle("Fabric API")
                    self.horizontalLayout_2.addWidget(self.groupBox_5)
                    
                    self.groupBox_3 = GroupBox(self)
                    self.groupBox_3.setTitle("Quilt")
                    self.groupBox_3.setCheckable(True)
                    self.groupBox_3.setChecked(False)
                    self.groupBox_3.clicked.connect(lambda: self.updateGroupBoxState(3))
                    self.verticalLayout.addWidget(self.groupBox_3)
                
                def updateGroupBoxState(self, which=1):
                    if which == 1 and self.groupBox.isChecked():
                        self.groupBox_2.setChecked(False)
                        self.groupBox_3.setChecked(False)
                    elif which == 2:
                        self.groupBox.setChecked(False)
                        self.groupBox_3.setChecked(False)
                    elif which == 3:
                        self.groupBox.setChecked(False)
                        self.groupBox_2.setChecked(False)
            
            def __init__(self, parent, version=None):
                super().__init__(parent, getBackgroundColour(), QColor(0, 0, 255, 200), 10)
                self.version = version
                
                self.verticalLayout = QVBoxLayout(self)
                
                self.topPanel = Panel(self)
                self.verticalLayout.addWidget(self.topPanel)
                
                self.horizontalLayout = QVBoxLayout(self.topPanel)
                
                self.closeButton = CloseButton(self.topPanel)
                self.closeButton.pressed.connect(self.closeFrame)
                self.closeButton.pressed.connect(self.frameClosed.emit)
                self.horizontalLayout.addWidget(self.closeButton)
                
                self.horizontalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                self.horizontalLayout.addItem(self.horizontalSpacer)
                
                self.toolBox = ToolBox(self)
                self.toolBox.setObjectName(u"toolBox")
                self.page = QWidget()
                self.page.setObjectName(u"page")
                self.page.setGeometry(QRect(0, 0, 623, 338))
                self.verticalLayout_3 = QVBoxLayout(self.page)
                self.verticalLayout_3.setObjectName(u"verticalLayout_3")
                self.formLayout = QFormLayout()
                self.formLayout.setObjectName(u"formLayout")
                self.lLabel = Label(self.page)
                self.lLabel.setObjectName(u"lLabel")
                
                self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lLabel)
                
                self.pushButton = PushButton(self.page)
                self.pushButton.setObjectName(u"pushButton")
                self.pushButton.pressed.connect(self.closeButton.pressed.emit)
                self.pushButton.setToolTip("单击重新选择版本")
                
                self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.pushButton)
                
                self.verticalLayout_3.addLayout(self.formLayout)
                
                self.formLayout_2 = QFormLayout()
                self.formLayout_2.setObjectName(u"formLayout_2")
                self.lLabel_2 = Label(self.page)
                self.lLabel_2.setObjectName(u"lLabel_2")
                self.lLabel_2.setText("模组加载器：")
                
                self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lLabel_2)
                
                self.pushButton_2 = PushButton(self.page)
                self.pushButton_2.setObjectName(u"pushButton_2")
                self.pushButton_2.setText("Forge: ---; NeoForge: ---; Fabric: ---; Fabric API: ---; Quilt: ---")
                self.pushButton_2.pressed.connect(self.selectLoader)
                
                self.formLayout_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.pushButton_2)
                
                self.verticalLayout_3.addLayout(self.formLayout_2)
                
                self.verticalSpacer_2 = QSpacerItem(20, 286, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
                
                self.verticalLayout_3.addItem(self.verticalSpacer_2)
                
                self.toolBox.addItem(self.page,
                                     self.tr("DownloadPage.DownloadVanilla.DownloadOptions.ToolBox.Page1.Title"))
                self.page_2 = QWidget()
                self.page_2.setObjectName(u"page_2")
                self.verticalLayout_4 = QVBoxLayout(self.page_2)
                self.verticalLayout_4.setObjectName(u"verticalLayout_2")
                self.formLayout_2 = QFormLayout()
                self.formLayout_2.setObjectName(u"formLayout_2")
                self.label_2 = Label(self.page_2)
                self.label_2.setObjectName(u"label_2")
                
                self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_2)
                
                self.lineEdit_2 = LineEdit(self.page_2)
                self.lineEdit_2.setObjectName(u"lineEdit_2")
                
                self.formLayout_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lineEdit_2)
                
                self.verticalLayout_4.addLayout(self.formLayout_2)
                
                self.verticalSpacer = QSpacerItem(20, 290, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
                
                self.verticalLayout_4.addItem(self.verticalSpacer)
                
                self.toolBox.addItem(self.page_2,
                                     self.tr("DownloadPage.DownloadVanilla.DownloadOptions.ToolBox.Page2.Title"))
                
                self.verticalLayout.addWidget(self.toolBox)
                
                self.startDownloadButton = PushButton(self)
                self.startDownloadButton.pressed.connect(self.startDownload)
                self.verticalLayout.addWidget(self.startDownloadButton)
                
                self.page_3 = QWidget()
                self.verticalLayout_5 = QVBoxLayout(self.page_3)
                
                self.groupBox = GroupBox(self.page_3)
                self.groupBox.setTitle("元素周期表（指优化模组）下载")
                self.groupBox.setCheckable(True)
                self.groupBox.setChecked(False)
                self.groupBox.toggled.connect(lambda: self.groupBoxStateSet(self.groupBox.isChecked()))
                self.verticalLayout_5.addWidget(self.groupBox)
                
                self.verticalLayout_6 = QVBoxLayout(self.groupBox)
                
                self.groupBoxDescription = Label(self.groupBox)
                self.groupBoxDescription.setText(
                    "由于原版那*一样的优化，我们的游戏会非常卡。\n因此，就出现了一堆优化模组，起了元素周期表（初三必背）中的元素名。\n此处可以选择想下载哪些优化模组（前提是你装了模组加载器）：")
                self.verticalLayout_6.addWidget(self.groupBoxDescription)
                
                self.girdLayout = QGridLayout()
                self.verticalLayout_6.addLayout(self.girdLayout)
                
                self.girdLayout_sodiumButton = CheckBox(self.groupBox)
                self.girdLayout_sodiumButton.setText("Sodium")
                self.girdLayout.addWidget(self.girdLayout_sodiumButton, 0, 0)
                
                self.girdLayout_lithiumButton = CheckBox(self.groupBox)
                self.girdLayout_lithiumButton.setText("Lithium")
                self.girdLayout.addWidget(self.girdLayout_lithiumButton, 0, 1)
                
                self.verticalSpacer_3 = QSpacerItem(0, 0, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
                self.verticalLayout_5.addItem(self.verticalSpacer_3)
                
                self.page_3_container = ScrollArea()
                self.page_3_container.setWidget(self.page_3)
                self.page_3_container.setWidgetResizable(True)
                
                self.toolBox.addItem(self.page_3_container, "其它选项")
                
                app.registerRetranslateFunction(self.retranslateUI)
                self.retranslateUI()
                
                self.toolBox.setCurrentIndex(0)
                
                QMetaObject.connectSlotsByName(self)
            
            def retranslateUI(self):
                self.lLabel.setText(self.tr("DownloadPage.DownloadVanilla.DownloadOptions.lLabel.Text"))
                self.pushButton.setText(self.version or u"RubyDung")
                self.toolBox.setItemText(self.toolBox.indexOf(self.page),
                                         self.tr("DownloadPage.DownloadVanilla.DownloadOptions.ToolBox.Page1.Title"))
                self.label_2.setText(self.tr("DownloadPage.DownloadVanilla.DownloadOptions.label_2.Text"))
                self.lineEdit_2.setText(str(minecraft_path))
                self.lineEdit_2.setPlaceholderText(str(minecraft_path))
                self.toolBox.setItemText(self.toolBox.indexOf(self.page_2),
                                         self.tr("DownloadPage.DownloadVanilla.DownloadOptions.ToolBox.Page2.Title"))
                self.startDownloadButton.setText(
                    self.tr("DownloadPage.DownloadVanilla.DownloadOptions.startDownloadButton.Text"))
            
            # retranslateUi
            
            def startDownload(self):
                download_thread = self.DownloadVersionThread(None, self.version, self.lineEdit_2.text())
                download_thread.start()
                self.closeButton.pressed.emit()
            
            def closeFrame(self):
                self.hide()
                self.deleteLater()
                del self
            
            def paintEvent(self, a0):
                self.setTintColour(getBackgroundColour())
                super().paintEvent(a0)
            
            def selectLoader(self):
                self.pushButton_2.setDown(False)
                dialogue = self.LoaderDialogue(frame)
                dialogue.exec()
            
            def updateLoaderText(self):
                pass
            
            def groupBoxStateSet(self, state=False):
                for cb in (self.girdLayout_sodiumButton, self.girdLayout_lithiumButton):
                    cb.setChecked(state)
        
        class GetVersionThread(QThread):
            gotVersion = pyqtSignal(dict)
            
            def run(self):
                try:
                    response = GetVersionByMojangApi(returns="RETURN_JSON")
                    if response:
                        self.gotVersion.emit({"status": "successfully", "result": response})
                    else:
                        self.gotVersion.emit({"status": "failed", "result": None})
                except:
                    self.gotVersion.emit({"status": "failed", "result": None})
        
        def __init__(self, parent=None):
            super().__init__(parent)
            self.verticalLayout = QVBoxLayout(self)
            
            self.lineEdit = LineEdit(self)
            self.lineEdit.setClearButtonEnabled(True)
            self.lineEdit.textChanged.connect(self.searchVersion)
            
            self.verticalLayout.addWidget(self.lineEdit)
            
            self.tableView = TableView(self)
            self.tableView.setSelectionMode(QTableView.SelectionMode.SingleSelection)
            self.tableView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            self.tableView.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.tableView.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
            self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.tableView.horizontalHeader().setVisible(True)
            self.tableView.verticalHeader().setVisible(False)
            self.tableView.clicked.connect(self.downloadOptionsOpen)
            self.versionModel = QStandardItemModel(self.tableView)
            self.versionModel.setHorizontalHeaderLabels(
                [
                    self.tr("DownloadPage.DownloadVanilla.tableView.horizontalHeaderLabels.1"),
                    self.tr("DownloadPage.DownloadVanilla.tableView.horizontalHeaderLabels.2"),
                    self.tr("DownloadPage.DownloadVanilla.tableView.horizontalHeaderLabels.3")
                ]
            )
            self.tableView.setModel(self.versionModel)
            self.versions = {}
            sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.tableView.sizePolicy().hasHeightForWidth())
            self.tableView.setSizePolicy(sizePolicy)
            
            self.verticalLayout.addWidget(self.tableView)
            
            self.bottomFrame = Panel(self)
            sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
            sizePolicy1.setHorizontalStretch(0)
            sizePolicy1.setVerticalStretch(0)
            sizePolicy1.setHeightForWidth(self.bottomFrame.sizePolicy().hasHeightForWidth())
            self.bottomFrame.setSizePolicy(sizePolicy1)
            self.horizontalLayout = QHBoxLayout(self.bottomFrame)
            self.horizontalLayout.setObjectName(u"horizontalLayout")
            self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
            self.formLayout = QFormLayout()
            self.formLayout.setObjectName(u"formLayout")
            self.label = Label(self.bottomFrame)
            self.label.setObjectName(u"label")
            
            self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)
            
            self.comboBox = ComboBox(self.bottomFrame)
            self.comboBox.setObjectName(u"comboBox")
            self.comboBox.addItem(self.tr("DownloadPage.DownloadVanilla.ComboBox.Item1.Text"))
            # self.comboBox.setEditable(True)
            
            self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.comboBox)
            
            self.horizontalLayout.addLayout(self.formLayout)
            
            self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
            
            self.horizontalLayout.addItem(self.horizontalSpacer)
            
            self.verticalLayout.addWidget(self.bottomFrame)
            
            app.registerRetranslateFunction(self.retranslateUi)
            self.retranslateUi()
            
            self.loadingAnimation = None
            self.getVersionThread = None
            self.downloadOptions = None
            self.downloadOptionsY = None
            
            # QMetaObject.connectSlotsByName(self)
            # setupUi
        
        def retranslateUi(self):
            self.lineEdit.setPlaceholderText(self.tr("DownloadPage.DownloadVanilla.lineEdit.PlaceholderText"))
            self.lineEdit.setToolTip(self.tr("DownloadPage.DownloadVanilla.lineEdit.ToolTip"))
            self.label.setText(self.tr("DownloadPage.DownloadVanilla.label.Text"))
            self.versionModel.setHorizontalHeaderLabels(
                [
                    self.tr("DownloadPage.DownloadVanilla.tableView.horizontalHeaderLabels.1"),
                    self.tr("DownloadPage.DownloadVanilla.tableView.horizontalHeaderLabels.2"),
                    self.tr("DownloadPage.DownloadVanilla.tableView.horizontalHeaderLabels.3")
                ]
            )
            self.comboBox.clear()
            self.comboBox.addItem(self.tr("DownloadPage.DownloadVanilla.ComboBox.Item1.Text"))
        
        # retranslateUi
        
        def event(self, e):
            if hasattr(self, "downloadOptions") and self.downloadOptions:
                rect = self.rect().adjusted(1, 1, -1, -1)
                rect.moveTo(0, self.downloadOptionsY)
                self.downloadOptions.setGeometry(rect)
                self.downloadOptions.raise_()
            if hasattr(self, "downloadOptionsY") and self.downloadOptionsY:
                if self.downloadOptionsY > 0:
                    self.downloadOptionsY -= self.downloadOptionsY // 16 + 1
                else:
                    self.downloadOptionsY = 0
            return super().event(e)
        
        def showEvent(self, *args, **kwargs):
            super().showEvent(*args, **kwargs)
            if self.getVersionThread or self.versions:
                pass
            else:
                self.getVersionThread = self.GetVersionThread(self)
                self.getVersionThread.gotVersion.connect(self.displayVersion)
                self.getVersionThread.start()
                self.loadingAnimation = LoadingAnimation(self)
                self.loadingAnimation.setReloadText("重新加载")
                self.loadingAnimation.addReloadFunction(self.reloadFunction)
                self.startAnimation(False)
        
        def hideEvent(self, a0):
            super().hideEvent(a0)
            if self.getVersionThread:
                self.getVersionThread.terminate()
            self.getVersionThread = None
            self.finishAnimation(False)
        
        def startAnimation(self, ani=True):
            if not self.loadingAnimation:
                self.loadingAnimation = LoadingAnimation(self)
            self.loadingAnimation.start(ani)
        
        def finishAnimation(self, ani=True, stat=True):
            if not self.loadingAnimation:
                return
            self.loadingAnimation.finish(ani, not stat)
        
        def reloadFunction(self):
            self.getVersionThread = self.GetVersionThread(self)
            self.getVersionThread.gotVersion.connect(self.displayVersion)
            self.getVersionThread.start()
            self.startAnimation(False)
        
        def displayVersion(self, data):
            if data["status"] == "successfully":
                data = data["result"]
                self.finishAnimation()
                completer_l = []
                for e, i in enumerate(data["versions"]):
                    version = i["id"]
                    version_type_real = i["type"]
                    match version_type_real:
                        case "release":
                            version_type = self.tr("DownloadPage.DownloadVanilla.VersionType.Release")
                        case "snapshot":
                            version_type = self.tr("DownloadPage.DownloadVanilla.VersionType.Snapshot")
                        case "old_beta":
                            version_type = self.tr("DownloadPage.DownloadVanilla.VersionType.OldBeta")
                        case "old_alpha":
                            version_type = self.tr("DownloadPage.DownloadVanilla.VersionType.OldAlpha")
                        case _:
                            version_type = version_type_real
                    unformatted_release_time = i["releaseTime"]
                    release_datetime = datetime.datetime.strptime(unformatted_release_time,
                                                                  "%Y-%m-%dT%H:%M:%S+00:00")
                    localised_release_datetime = release_datetime.replace(tzinfo=datetime.UTC).astimezone(tz.tzlocal())
                    release_time = localised_release_datetime.strftime(
                        settings["Settings"]["LauncherSettings"]["Customise"]["DateTimeFormat"])
                    if release_datetime.month == 4 and release_datetime.day == 1:
                        version_type = self.tr("DownloadPage.DownloadVanilla.VersionType.AprilFool")
                        version_type_real = "april_fool"
                    for e2, i2 in enumerate([version, version_type, release_time]):
                        self.versionModel.setItem(e, e2, QStandardItem(i2))
                    self.versions[version] = {"VersionId": version, "VersionType": version_type_real,
                                              "ReleaseTime": release_time, "ReleaseDatetime": release_datetime}
                    completer_l.append(version)
                self.lineEdit.setCompleter(QCompleter(completer_l, self.lineEdit))
                self.versionModel.setHorizontalHeaderLabels(
                    [
                        self.tr("DownloadPage.DownloadVanilla.tableView.horizontalHeaderLabels.1"),
                        self.tr("DownloadPage.DownloadVanilla.tableView.horizontalHeaderLabels.2"),
                        self.tr("DownloadPage.DownloadVanilla.tableView.horizontalHeaderLabels.3")
                    ]
                )
                self.tableView.setModel(self.versionModel)
                self.tableView.setSelectionMode(QTableView.SelectionMode.SingleSelection)
                self.tableView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
                self.tableView.horizontalHeader().setVisible(True)
                self.tableView.verticalHeader().setVisible(False)
            else:
                self.finishAnimation(stat=False)
        
        def searchVersion(self, value):
            version_d = value
            self.versionModel.clear()
            self.versionModel.setHorizontalHeaderLabels(
                [self.tr("DownloadPage.DownloadVanilla.tableView.horizontalHeaderLabels.1"),
                 self.tr("DownloadPage.DownloadVanilla.tableView.horizontalHeaderLabels.2"),
                 self.tr("DownloadPage.DownloadVanilla.tableView.horizontalHeaderLabels.3")])
            i = 0
            latest_release = False
            latest_snapshot = False
            for key, value in self.versions.items():
                if version_d == "":
                    version = value["VersionId"]
                    version_type = value["VersionType"]
                    match version_type:
                        case "release":
                            version_type = self.tr("DownloadPage.DownloadVanilla.VersionType.Release")
                        case "snapshot":
                            version_type = self.tr("DownloadPage.DownloadVanilla.VersionType.Snapshot")
                        case "old_beta":
                            version_type = self.tr("DownloadPage.DownloadVanilla.VersionType.OldBeta")
                        case "old_alpha":
                            version_type = self.tr("DownloadPage.DownloadVanilla.VersionType.OldAlpha")
                        case _:
                            version_type = version_type
                    release_datetime = value["ReleaseDatetime"]
                    if release_datetime.month == 4 and release_datetime.day == 1:
                        version_type = self.tr("DownloadPage.DownloadVanilla.VersionType.AprilFool")
                    localised_release_datetime = release_datetime.replace(tzinfo=datetime.UTC).astimezone(tz.tzlocal())
                    release_time = localised_release_datetime.strftime(
                        settings["Settings"]["LauncherSettings"]["Customise"]["DateTimeFormat"])
                    for e2, i2 in enumerate([version, version_type, release_time]):
                        self.versionModel.setItem(i, e2, QStandardItem(i2))
                    i += 1
                elif version_d.lower() in ["latest", "latest_version", "latest-version"] and (
                        not latest_release or not latest_snapshot):
                    version = value["VersionId"]
                    version_type = value["VersionType"]
                    match version_type:
                        case "release":
                            if latest_release:
                                continue
                            version_type = self.tr("DownloadPage.DownloadVanilla.VersionType.Release")
                            latest_release = True
                        case "snapshot":
                            if latest_snapshot:
                                continue
                            version_type = self.tr("DownloadPage.DownloadVanilla.VersionType.Snapshot")
                            latest_snapshot = True
                        case _:
                            if latest_release and latest_snapshot:
                                break
                            continue
                    release_datetime = value["ReleaseDatetime"]
                    localised_release_datetime = release_datetime.replace(tzinfo=datetime.UTC).astimezone(tz.tzlocal())
                    release_time = localised_release_datetime.strftime(
                        settings["Settings"]["LauncherSettings"]["Customise"]["DateTimeFormat"])
                    for e2, i2 in enumerate([version, version_type, release_time]):
                        self.versionModel.setItem(i, e2, QStandardItem(i2))
                    i += 1
                else:
                    try:
                        if re.match(version_d, key, re.UNICODE) or re.match(version_d, value["VersionType"],
                                                                            re.UNICODE) or re.match(version_d, value[
                            "ReleaseTime"], re.UNICODE):
                            version = value["VersionId"]
                            version_type = value["VersionType"]
                            match version_type:
                                case "release":
                                    version_type = self.tr("DownloadPage.DownloadVanilla.VersionType.Release")
                                case "snapshot":
                                    version_type = self.tr("DownloadPage.DownloadVanilla.VersionType.Snapshot")
                                case "old_beta":
                                    version_type = self.tr("DownloadPage.DownloadVanilla.VersionType.OldBeta")
                                case "old_alpha":
                                    version_type = self.tr("DownloadPage.DownloadVanilla.VersionType.OldAlpha")
                                case _:
                                    version_type = version_type
                            release_datetime = value["ReleaseDatetime"]
                            if release_datetime.month == 4 and release_datetime.day == 1:
                                version_type = self.tr("DownloadPage.DownloadVanilla.VersionType.AprilFool")
                            localised_release_datetime = release_datetime.replace(tzinfo=datetime.UTC).astimezone(
                                tz.tzlocal())
                            release_time = localised_release_datetime.strftime(
                                settings["Settings"]["LauncherSettings"]["Customise"]["DateTimeFormat"])
                            for e2, i2 in enumerate([version, version_type, release_time]):
                                self.versionModel.setItem(i, e2, QStandardItem(i2))
                            i += 1
                    except re.error:
                        pass
            self.versionModel.setHorizontalHeaderLabels(
                [
                    self.tr("DownloadPage.DownloadVanilla.tableView.horizontalHeaderLabels.1"),
                    self.tr("DownloadPage.DownloadVanilla.tableView.horizontalHeaderLabels.2"),
                    self.tr("DownloadPage.DownloadVanilla.tableView.horizontalHeaderLabels.3")
                ]
            )
            self.tableView.setModel(self.versionModel)
            self.tableView.setSelectionMode(QTableView.SelectionMode.SingleSelection)
            self.tableView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            self.tableView.horizontalHeader().setVisible(True)
            self.tableView.verticalHeader().setVisible(False)
        
        def downloadOptionsOpen(self, value):
            data = self.tableView.model().item(value.row(), 0).text()
            self.downloadOptionsY = self.height()
            self.downloadOptions = self.DownloadOptions(self, data)
            self.downloadOptions.frameClosed.connect(self.downloadOptionsClose)
            rect = self.rect().adjusted(1, 1, -1, -1)
            self.downloadOptions.setGeometry(rect)
            self.downloadOptions.grabBehind()
            rect.moveTo(0, self.downloadOptionsY)
            self.downloadOptions.setGeometry(rect)
            self.downloadOptions.show()
        
        def downloadOptionsClose(self):
            self.downloadOptions = None
            self.downloadOptionsY = None
    
    class DownloadMods(QFrame):
        class ModInfoPage(AcrylicBackground):
            class GetVersionsThread(QThread):
                requested = pyqtSignal(list)
                
                def __init__(self, parent=None, mod_name=None):
                    super().__init__(parent)
                    self.mod_name = mod_name
                
                def run(self):
                    try:
                        content = ListModVersions(self.mod_name)
                        self.requested.emit(content)
                    except:
                        self.requested.emit([])
            
            class DownloadThread(QThread):
                def __init__(self, parent=None, mod_name=None, mod_version=None, target_path=None):
                    super().__init__(parent)
                    self.mod_name = mod_name
                    self.mod_version = mod_version
                    self.target_path = target_path
                
                def run(self):
                    if self.mod_name and self.mod_version and self.target_path:
                        print("started")
                        DownloadMod(self.mod_name, self.mod_version, self.target_path)
            
            class GetIconThread(QThread):
                requested = pyqtSignal(bytes)
                
                def __init__(self, parent=None, icon_url=None):
                    super().__init__(parent)
                    self.icon_url = icon_url
                
                def run(self):
                    try:
                        content = requests.get(self.icon_url).content
                        self.requested.emit(content)
                    except:
                        self.requested.emit(b"")
            
            closePage = pyqtSignal()
            
            def __init__(self, parent=None, mod_name=None, mod_slug=None):
                super().__init__(parent, getBackgroundColour(), QColor(0, 0, 255, 200), 10)
                self.mod_name = mod_name
                self.mod_info_json = GetOneMod(mod_slug)
                self.mod_icon = self.mod_info_json["icon_url"]
                self.mod_description = self.mod_info_json["description"]
                self.mod_body = self.mod_info_json["body"]
                
                self.icon_temp = None
                thread = self.GetIconThread(self, self.mod_icon)
                thread.requested.connect(self.updateIcon)
                thread.start()
                
                self.mod_versions = []
                thread_2 = self.GetVersionsThread(self, self.mod_name)
                thread_2.requested.connect(self.updateVersions)
                thread_2.start()
                
                self.verticalLayout = QVBoxLayout(self)
                
                self.topPanel = Panel(self)
                
                self.horizontalLayout = QHBoxLayout(self.topPanel)
                
                self.closeButton = CloseButton(self.topPanel)
                self.closeButton.pressed.connect(self.close)
                self.closeButton.pressed.connect(self.closePage.emit)
                self.horizontalLayout.addWidget(self.closeButton)
                
                self.horizontalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                self.horizontalLayout.addItem(self.horizontalSpacer)
                
                self.verticalLayout.addWidget(self.topPanel)
                
                self.toolBox = ToolBox(self)
                
                self.modInfo = QFrame()
                
                self.verticalLayout_2 = QVBoxLayout(self.modInfo)
                
                self.modInfoCard = Panel(self.modInfo)
                
                self.horizontalLayout_2 = QHBoxLayout(self.modInfoCard)
                
                self.modIcon = ToolButton(self.modInfoCard)
                self.modIcon.setFixedSize(QSize(74, 74))
                self.modIcon.setIconSize(QSize(64, 64))
                
                self.horizontalLayout_2.addWidget(self.modIcon)
                
                self.verticalLayout_3 = QVBoxLayout(self.modInfoCard)
                
                self.modName = Label(self.modInfoCard)
                self.verticalLayout_3.addWidget(self.modName)
                
                self.modDescription = Label(self.modInfoCard)
                self.modDescription.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
                self.modDescription.setWordWrap(True)
                self.verticalLayout_3.addWidget(self.modDescription, 1)
                
                self.horizontalLayout_2.addLayout(self.verticalLayout_3)
                
                self.verticalLayout_2.addWidget(self.modInfoCard)
                
                self.modBody = TextEdit(self.modInfo)
                self.modBody.setReadOnly(True)
                self.modBody.setMarkdown(self.mod_body)
                self.verticalLayout_2.addWidget(self.modBody, 1)
                
                self.modInfoContainer = ScrollArea(self.toolBox)
                self.modInfoContainer.setWidget(self.modInfo)
                self.modInfoContainer.setWidgetResizable(True)
                
                self.toolBox.addItem(self.modInfoContainer,
                                     self.tr("DownloadPage.DownloadMods.ModInfoPage.Page1.Title"))
                
                self.modVersions = QFrame(self.toolBox)
                
                self.verticalLayout_4 = QVBoxLayout(self.modVersions)
                
                self.listWidget = ListWidget(self.modVersions)
                self.listWidget.doubleClicked.connect(self.startDownloadMod)
                self.verticalLayout_4.addWidget(self.listWidget)
                
                self.toolBox.addItem(self.modVersions, self.tr("DownloadPage.DownloadMods.ModInfoPage.Page2.Title"))
                
                self.verticalLayout.addWidget(self.toolBox)
                
                app.registerRetranslateFunction(self.retranslateUI)
                self.retranslateUI()
            
            def retranslateUI(self):
                self.modName.setText(self.mod_name)
                self.modDescription.setText(self.mod_description)
                self.toolBox.setItemText(self.toolBox.indexOf(self.modInfo),
                                         self.tr("DownloadPage.DownloadMods.ModInfoPage.Page1.Title"))
                self.toolBox.setItemText(self.toolBox.indexOf(self.modVersions),
                                         self.tr("DownloadPage.DownloadMods.ModInfoPage.Page2.Title"))
            
            def updateIcon(self, icon):
                try:
                    with tempfile.NamedTemporaryFile(mode="wb+", suffix=".png", delete=False) as self.icon_temp:
                        self.icon_temp.write(requests.get(self.mod_icon).content)
                        self.icon_temp.flush()
                except:
                    self.icon_temp = None
                self.modIcon.setIcon(QIcon(self.icon_temp.name) if self.icon_temp else QIcon())
            
            def updateVersions(self, versions):
                self.listWidget.clear()
                self.mod_versions = versions
                for version in versions:
                    self.listWidget.addItem(f"{version['name']}")
            
            def startDownloadMod(self, version):
                download_path = QFileDialog.getExistingDirectory(self, self.tr(
                    "DownloadPage.DownloadMods.ModInfoPage.Page2.DownloadPath"), str(Path(".").absolute()))
                if download_path:
                    version_text = self.listWidget.model().itemData(version)[0]
                    thread = self.DownloadThread(self, self.mod_name, version_text, download_path)
                    thread.start()
            
            def paintEvent(self, a0):
                self.setTintColour(getBackgroundColour())
                super().paintEvent(a0)
            
            def closeEvent(self, *args, **kwargs):
                super().closeEvent(*args, **kwargs)
                if self.icon_temp:
                    Path(self.icon_temp.name).unlink(missing_ok=True)
        
        class GetModThread(QThread):
            gotMod = pyqtSignal(dict)
            
            def __init__(self, parent=None, page=1, page_items=10):
                super().__init__(parent)
                self.page = page
                self.page_items = page_items
            
            def run(self):
                try:
                    response = GetMods(limit=self.page_items, offset=(self.page - 1) * self.page_items)
                    if response:
                        self.gotMod.emit({"status": "successfully", "result": response})
                    else:
                        self.gotMod.emit({"status": "failed", "result": None})
                except:
                    self.gotMod.emit({"status": "failed", "result": None})
        
        def __init__(self, parent=None):
            super().__init__(parent)
            self.verticalLayout = QVBoxLayout(self)
            
            self.filterPanel = GroupBox(self)
            self.horizontalLayout = QHBoxLayout(self.filterPanel)
            
            self.searchLineEdit = LineEdit(self.filterPanel)
            self.searchLineEdit.setClearButtonEnabled(True)
            self.searchLineEdit.textEdited.connect(self.searchMods)
            self.horizontalLayout.addWidget(self.searchLineEdit)
            
            self.verticalLayout.addWidget(self.filterPanel)
            
            self.contentTabel = TableView(self)
            self.verticalLayout.addWidget(self.contentTabel)
            self.contentTabel.verticalHeader().setVisible(False)
            self.contentTabel.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.contentTabel.setEditTriggers(TableView.EditTrigger.NoEditTriggers)
            self.contentTabel.pressed.connect(self.modInfoPageOpen)
            self.model = QStandardItemModel()
            self.model.setHorizontalHeaderLabels(
                [self.tr("DownloadPage.DownloadMods.contentTabel.horizontalHeaderLabels.1"),
                 self.tr("DownloadPage.DownloadMods.contentTabel.horizontalHeaderLabels.2"),
                 self.tr("DownloadPage.DownloadMods.contentTabel.horizontalHeaderLabels.3")])
            self.contentTabel.setModel(self.model)
            
            self.paginator = Panel(self)
            self.horizontalLayout_2 = QHBoxLayout(self.paginator)
            
            self.previousButton = PushButton(self.paginator)
            self.previousButton.pressed.connect(self.previousPage)
            self.horizontalLayout_2.addWidget(self.previousButton)
            
            self.currentPageLabel = Label(self.paginator)
            self.currentPageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.horizontalLayout_2.addWidget(self.currentPageLabel)
            
            self.nextButton = PushButton(self.paginator)
            self.nextButton.pressed.connect(self.nextPage)
            self.horizontalLayout_2.addWidget(self.nextButton)
            
            self.verticalLayout.addWidget(self.paginator)
            
            app.registerRetranslateFunction(self.retranslateUI)
            self.retranslateUI()
            
            self.mods = {}
            self.loadingAnimation = None
            self.getModThread = None
            self.modInfoPage = None
            self.modInfoPageY = None
            self.currentPage = 1
        
        def retranslateUI(self):
            self.filterPanel.setTitle(self.tr("DownloadPage.DownloadMods.filterPanel.Title"))
            self.searchLineEdit.setPlaceholderText(self.tr("DownloadPage.DownloadMods.searchLineEdit.PlaceholderText"))
            # self.searchLineEdit.setToolTip("")
            self.previousButton.setText(self.tr("DownloadPage.DownloadMods.previousButton.Text"))
            self.nextButton.setText(self.tr("DownloadPage.DownloadMods.nextButton.Text"))
            self.model.setHorizontalHeaderLabels(
                [self.tr("DownloadPage.DownloadMods.contentTabel.horizontalHeaderLabels.1"),
                 self.tr("DownloadPage.DownloadMods.contentTabel.horizontalHeaderLabels.2"),
                 self.tr("DownloadPage.DownloadMods.contentTabel.horizontalHeaderLabels.3")])
        
        def previousPage(self):
            self.currentPage -= 1
            self.currentPage = max(self.currentPage, 1)
            self.updatePage()
            self.loadPage()
        
        def nextPage(self):
            self.currentPage += 1
            self.updatePage()
            self.loadPage()
        
        def updatePage(self):
            self.currentPageLabel.setText(str(self.currentPage))
            if self.currentPage <= 1:
                self.previousButton.setEnabled(False)
            else:
                self.previousButton.setEnabled(True)
            if self.searchLineEdit.text():
                self.nextButton.setEnabled(False)
            else:
                self.nextButton.setEnabled(True)
        
        def loadPage(self):
            if self.currentPage in self.mods:
                self.displayMods(None, self.currentPage)
            else:
                self.getModThread = self.GetModThread(self, page=self.currentPage)
                self.getModThread.gotMod.connect(lambda data: self.displayMods(data, self.currentPage))
                self.getModThread.start()
                self.loadingAnimation = LoadingAnimation(self)
                self.startAnimation(True)
        
        def event(self, e):
            if hasattr(self, "modInfoPage") and self.modInfoPage:
                rect = self.rect().adjusted(1, 1, -1, -1)
                rect.moveTo(0, self.modInfoPageY)
                self.modInfoPage.setGeometry(rect)
                self.modInfoPage.raise_()
            if hasattr(self, "modInfoPageY") and self.modInfoPageY:
                if self.modInfoPageY > 0:
                    self.modInfoPageY -= self.modInfoPageY // 16 + 1
                else:
                    self.modInfoPageY = 0
            return super().event(e)
        
        def showEvent(self, a0):
            super().showEvent(a0)
            if self.mods:
                pass
            else:
                self.getModThread = self.GetModThread(self)
                self.getModThread.gotMod.connect(self.displayMods)
                self.getModThread.start()
                self.loadingAnimation = LoadingAnimation(self)
                self.startAnimation(False)
        
        def hideEvent(self, a0):
            super().hideEvent(a0)
            self.finishAnimation(False)
        
        def startAnimation(self, ani=True):
            if not self.loadingAnimation:
                self.loadingAnimation = LoadingAnimation(self)
            self.loadingAnimation.start(ani)
        
        def finishAnimation(self, ani=True, stat=True):
            if not self.loadingAnimation:
                return
            self.loadingAnimation.finish(ani, not stat)
        
        def displayMods(self, data, page=1):
            if not data or data["status"] == "successfully":
                if data:
                    dat = data["result"]
                    self.mods[page] = dat
                    self.finishAnimation(True, True)
                elif page in self.mods:
                    dat = self.mods[page]
                else:
                    self.finishAnimation(True, False)
                    return
                self.model.clear()
                for e, hit in enumerate(dat["hits"]):
                    self.model.setItem(e, 0, QStandardItem(hit["title"]))
                    self.model.setItem(e, 1, QStandardItem(hit["author"]))
                    self.model.setItem(e, 2, QStandardItem(
                        time.strftime(
                            settings["Settings"]["LauncherSettings"]["Customise"]["DateTimeFormat"],
                            time.strptime(
                                hit["date_modified"].split(".")[0],
                                "%Y-%m-%dT%H:%M:%S"
                            )
                        )
                    ))
                self.model.setHorizontalHeaderLabels(
                    [self.tr("DownloadPage.DownloadMods.contentTabel.horizontalHeaderLabels.1"),
                     self.tr("DownloadPage.DownloadMods.contentTabel.horizontalHeaderLabels.2"),
                     self.tr("DownloadPage.DownloadMods.contentTabel.horizontalHeaderLabels.3")])
                self.contentTabel.setModel(self.model)
                self.updatePage()
            else:
                if self.mods:
                    self.previousPage()
                    self.finishAnimation(True, True)
                else:
                    self.finishAnimation(True, False)
        
        def searchMods(self, value):
            value_query = value
            self.model.clear()
            self.currentPage = 1
            self.updatePage()
            try:
                if value_query:
                    cnt = 0
                    for dat in list(self.mods.values()):
                        for hit in dat["hits"]:
                            if re.match(value_query.lower(), hit["title"].lower()):
                                self.model.setItem(cnt, 0, QStandardItem(hit["title"]))
                                self.model.setItem(cnt, 1, QStandardItem(hit["author"]))
                                self.model.setItem(cnt, 2, QStandardItem(
                                    time.strftime(
                                        settings["Settings"]["LauncherSettings"]["Customise"]["DateTimeFormat"],
                                        time.strptime(
                                            hit["date_modified"].split(".")[0],
                                            "%Y-%m-%dT%H:%M:%S"
                                        )
                                    )
                                ))
                                cnt += 1
                else:
                    self.displayMods(None, self.currentPage)
            except re.error:
                pass
            self.model.setHorizontalHeaderLabels(
                [self.tr("DownloadPage.DownloadMods.contentTabel.horizontalHeaderLabels.1"),
                 self.tr("DownloadPage.DownloadMods.contentTabel.horizontalHeaderLabels.2"),
                 self.tr("DownloadPage.DownloadMods.contentTabel.horizontalHeaderLabels.3")])
            self.contentTabel.setModel(self.model)
        
        def modInfoPageOpen(self, value):
            data = self.contentTabel.model().item(value.row(), 0).text()
            print(data)
            hit_data = None
            for page in self.mods.values():
                for hit in page["hits"]:
                    if hit["title"] == data:
                        hit_data = hit
            if hit_data:
                self.modInfoPageY = self.height()
                self.modInfoPage = self.ModInfoPage(self, data, hit_data["slug"])
                self.modInfoPage.closePage.connect(self.modInfoPageClose)
                rect = self.rect().adjusted(1, 1, -1, -1)
                self.modInfoPage.setGeometry(rect)
                self.modInfoPage.grabBehind()
                rect.moveTo(0, self.modInfoPageY)
                self.modInfoPage.setGeometry(rect)
                self.modInfoPage.show()
        
        def modInfoPageClose(self):
            self.modInfoPage = None
            self.modInfoPageY = None
    
    def __init__(self, parent):
        super().__init__(parent)
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.navigationFrame = Panel(self)
        self.navigationFrameScrollAreaLayout = QVBoxLayout(self.navigationFrame)
        self.navigationFrameScrollAreaLayout.setContentsMargins(0, 0, 0, 0)
        self.navigationFrameScrollArea = ScrollArea(self.navigationFrame)
        self.navigationFrameScrollArea.setFixedHeight(self.navigationFrame.height() + 10)
        self.navigationFrameScrollAreaLayout.addWidget(self.navigationFrameScrollArea)
        self.navigationFrameScrollAreaWidgetContent = QWidget()
        self.horizontalLayout = QHBoxLayout(self.navigationFrameScrollAreaWidgetContent)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.pages = {}
        
        self.page = self.DownloadVanilla()
        self.page.setObjectName(u"page")
        self.pushButton = PushButton(self.navigationFrameScrollAreaWidgetContent)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setCheckable(True)
        self.pushButton.setChecked(True)
        self.pushButton.setAutoExclusive(True)
        self.pushButton.pressed.connect(lambda: self.update_page(self.pushButton))
        
        self.horizontalLayout.addWidget(self.pushButton)
        self.pages[self.pushButton] = self.page
        
        self.page_2 = self.DownloadMods()
        self.page_2.setObjectName(u"page_2")
        self.pushButton_2 = PushButton(self.navigationFrameScrollAreaWidgetContent)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setCheckable(True)
        self.pushButton_2.setAutoExclusive(True)
        self.pushButton_2.pressed.connect(lambda: self.update_page(self.pushButton_2))
        
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.pages[self.pushButton_2] = self.page_2
        
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        self.horizontalLayout.addItem(self.horizontalSpacer)
        
        self.navigationFrameScrollArea.setWidget(self.navigationFrameScrollAreaWidgetContent)
        self.navigationFrameScrollArea.setWidgetResizable(True)
        
        self.verticalLayout.addWidget(self.navigationFrame)
        
        self.stackedWidget = AnimatedStackedWidget(self)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.addWidget(self.page)
        self.stackedWidget.addWidget(self.page_2)
        self.stackedWidget.setCurrentIndex(0)
        
        self.verticalLayout.addWidget(self.stackedWidget, 1)
        
        app.registerRetranslateFunction(self.retranslateUi)
        self.retranslateUi()
        #
        # QMetaObject.connectSlotsByName(Form)
    
    # setupUi
    
    def retranslateUi(self):
        self.pushButton.setText(self.tr("DownloadPage.pushButton.Text"))
        self.pushButton_2.setText(self.tr("DownloadPage.pushButton_2.Text"))
    
    # retranslateUi
    
    def update_page(self, btn):
        self.stackedWidget.setCurrentWidget(self.pages[btn])


class SettingsPage(QFrame):
    class GameSettings(QFrame):
        def __init__(self, parent):
            super().__init__(parent)
            self.verticalLayout = QVBoxLayout(self)
            self.verticalLayout.setObjectName(u"verticalLayout")
            self.formLayout = QFormLayout()
            self.formLayout.setObjectName(u"formLayout")
            self.label = Label(self)
            self.label.setObjectName(u"label")
            
            self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)
            
            self.lineEdit = LineEdit(self)
            self.lineEdit.setObjectName(u"lineEdit")
            self.lineEdit.setText(settings["Settings"]["GameSettings"]["ExtraGameCommand"])
            self.lineEdit.textChanged.connect(self.updatePresetsState)
            self.lineEdit.textChanged.connect(self.updateSettings)
            self.lineEdit.setClearButtonEnabled(True)
            font = fixedFont
            self.lineEdit.setFont(font)
            
            self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lineEdit)
            
            self.verticalLayout.addLayout(self.formLayout)
            
            self.groupBox = GroupBox(self)
            self.groupBox.setObjectName(u"groupBox")
            # self.groupBox.setCheckable(True)
            self.gridLayout = QGridLayout(self.groupBox)
            self.gridLayout.setObjectName(u"gridLayout")
            self.checkBox = CheckBox(self.groupBox)
            self.checkBox.setObjectName(u"checkBox")
            self.checkBox.toggled.connect(lambda state=False: self.presetChecked(state, "-demo"))
            
            # self.checkBox.setFixedHeight(10)
            # self.checkBox.setFixedHeight(100)
            # self.checkBox.setTristate(True)
            
            self.gridLayout.addWidget(self.checkBox, 0, 0, 1, 1)
            
            self.checkBox_2 = CheckBox(self.groupBox)
            self.checkBox_2.setObjectName(u"checkBox_2")
            self.checkBox_2.toggled.connect(lambda state=False: self.presetChecked(state, "-fullscreen"))
            
            self.gridLayout.addWidget(self.checkBox_2, 1, 0, 1, 1)
            
            self.verticalLayout.addWidget(self.groupBox)
            
            self.verticalSpacer = QSpacerItem(20, 360, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
            
            self.verticalLayout.addItem(self.verticalSpacer)
            
            app.registerRetranslateFunction(self.retranslateUi)
            self.retranslateUi()
            
            self.updatePresetsState()
            #
            # QMetaObject.connectSlotsByName(Form)
        
        # setupUi
        
        def retranslateUi(self):
            self.label.setText(self.tr("SettingsPage.GameSettings.label.Text"))
            self.groupBox.setTitle(self.tr("SettingsPage.GameSettings.groupBox.Title"))
            self.checkBox.setText(self.tr("SettingsPage.GameSettings.checkBox.Text"))
            self.checkBox_2.setText(self.tr("SettingsPage.GameSettings.checkBox_2.Text"))
        
        # retranslateUi
        
        def presetChecked(self, state, command):
            text = self.lineEdit.text()
            try:
                splited_command = shlex.split(text)
            except ValueError:
                return
            else:
                if state:
                    if command not in splited_command:
                        splited_command.append(command)
                else:
                    if command in splited_command:
                        splited_command.remove(command)
                command = shlex.join(splited_command)
            self.lineEdit.setText(command)
        
        def updatePresetsState(self):
            text = self.lineEdit.text()
            try:
                splited_command = shlex.split(text)
            except ValueError:
                return
            else:
                self.checkBox.setChecked("-demo" in splited_command)
                self.checkBox_2.setChecked("-fullscreen" in splited_command)
        
        def updateSettings(self, value):
            settings["Settings"]["GameSettings"]["ExtraGameCommand"] = value
    
    class JavaSettings(QFrame):
        class SearchVersionThread(QThread):
            versionHasGot = pyqtSignal(list)
            
            def run(self):
                where_out = subprocess.run(
                    ["which" if GetOperationSystemName()[0].lower() != "windows" else "where",
                     "java"],
                    capture_output=True,
                    check=False).stdout
                result = []
                for i in where_out.decode(errors="ignore").splitlines():
                    result.append(i)
                self.versionHasGot.emit(result)
        
        def __init__(self, parent):
            super().__init__(parent)
            self.verticalLayout = QVBoxLayout(self)
            self.verticalLayout.setObjectName(u"verticalLayout")
            self.groupBox = GroupBox(self)
            self.groupBox.setObjectName(u"groupBox")
            self.horizontalLayout = QHBoxLayout(self.groupBox)
            self.horizontalLayout.setObjectName(u"horizontalLayout")
            self.radioButton = RadioButton(self.groupBox)
            self.radioButton.setObjectName(u"radioButton")
            self.radioButton.setChecked(settings["Settings"]["JavaSettings"]["Java"]["LaunchMode"] == "client")
            self.radioButton.toggled.connect(self.updateJavaLaunchMode)
            
            self.horizontalLayout.addWidget(self.radioButton)
            
            self.radioButton_2 = RadioButton(self.groupBox)
            self.radioButton_2.setObjectName(u"radioButton_2")
            self.radioButton_2.setChecked(settings["Settings"]["JavaSettings"]["Java"]["LaunchMode"] == "server")
            self.radioButton_2.toggled.connect(self.updateJavaLaunchMode)
            
            self.horizontalLayout.addWidget(self.radioButton_2)
            
            self.verticalLayout.addWidget(self.groupBox)
            
            self.formLayout_2 = QFormLayout()
            self.formLayout_2.setObjectName(u"formLayout_2")
            self.label_2 = Label(self)
            self.label_2.setObjectName(u"label_2")
            
            self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_2)
            
            self.widget_2 = QWidget(self)
            self.widget_2.setObjectName(u"widget_2")
            self.horizontalLayout_3 = QHBoxLayout(self.widget_2)
            self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
            self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
            self.comboBox = ComboBox(self.widget_2)
            self.comboBox.setObjectName(u"lineEdit_2")
            self.comboBox.setEditable(True)
            self.comboBox.currentTextChanged.connect(self.updateJavaPath)
            self.comboBox.setSizeAdjustPolicy(ComboBox.SizeAdjustPolicy.AdjustToContentsOnFirstShow)
            font = fixedFont
            self.comboBox.setFont(font)
            self.horizontalLayout_3.addWidget(self.comboBox, 1)
            
            self.pushButton_2 = TogglePushButton(self.widget_2)
            self.pushButton_2.setObjectName(u"pushButton_2")
            self.pushButton_2.setChecked(settings["Settings"]["JavaSettings"]["Java"]["Path"]["is_auto"])
            if not self.pushButton_2.isChecked():
                self.comboBox.setEnabled(True)
                self.comboBox.setCurrentText(settings["Settings"]["JavaSettings"]["Java"]["Path"]["value"])
                self.searchJava()
            else:
                self.comboBox.clear()
                self.comboBox.setCurrentText(self.tr("SettingsPage.JavaSettings.comboBox.Text"))
                self.comboBox.setEnabled(False)
            self.pushButton_2.toggled.connect(self.updateJavaPathIsAuto)
            
            self.horizontalLayout_3.addWidget(self.pushButton_2)
            
            self.pushButton_3 = PushButton(self.widget_2)
            self.pushButton_3.pressed.connect(self.applyJavaByUser)
            self.pushButton_3.setEnabled(self.comboBox.isEnabled())
            
            self.horizontalLayout_3.addWidget(self.pushButton_3)
            
            self.formLayout_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.widget_2)
            
            self.verticalLayout.addLayout(self.formLayout_2)
            
            self.formLayout = QFormLayout()
            self.formLayout.setObjectName(u"formLayout")
            self.label = Label(self)
            self.label.setObjectName(u"label")
            
            self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)
            
            self.widget = QWidget(self)
            self.widget.setObjectName(u"widget")
            self.horizontalLayout_2 = QHBoxLayout(self.widget)
            self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
            self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
            self.lineEdit = LineEdit(self.widget)
            self.lineEdit.setObjectName(u"lineEdit")
            self.lineEdit.setText(settings["Settings"]["JavaSettings"]["JVM"]["Arg"]["value"])
            self.lineEdit.setFont(font)
            self.lineEdit.editingFinished.connect(self.editingFinished)
            
            self.horizontalLayout_2.addWidget(self.lineEdit)
            
            self.pushButton = TogglePushButton(self.widget)
            self.pushButton.setObjectName(u"pushButton")
            self.pushButton.setChecked(settings["Settings"]["JavaSettings"]["JVM"]["Arg"]["is_override"])
            self.groupBox.setEnabled(not self.pushButton.isChecked())
            self.pushButton.toggled.connect(self.updateJVMArgIsOverride)
            
            self.horizontalLayout_2.addWidget(self.pushButton)
            
            self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.widget)
            
            self.verticalLayout.addLayout(self.formLayout)
            
            self.verticalSpacer = QSpacerItem(20, 163, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
            
            self.verticalLayout.addItem(self.verticalSpacer)
            
            app.registerRetranslateFunction(self.retranslateUi)
            self.retranslateUi()
            #
            # QMetaObject.connectSlotsByName(self)
        
        # setupUi
        
        def retranslateUi(self):
            self.groupBox.setTitle(self.tr("SettingsPage.JavaSettings.groupBox.Text"))
            self.radioButton.setText(self.tr("SettingsPage.JavaSettings.radioButton.Text"))
            self.radioButton.setToolTip(self.tr("SettingsPage.JavaSettings.radioButton.ToolTip"))
            self.radioButton_2.setText(self.tr("SettingsPage.JavaSettings.radioButton_2.Text"))
            self.radioButton_2.setToolTip(
                self.tr("SettingsPage.JavaSettings.radioButton_2.ToolTip"))
            self.label_2.setText(self.tr("SettingsPage.JavaSettings.label_2.Text"))
            self.pushButton_2.setText(self.tr("SettingsPage.JavaSettings.pushButton_2.Text"))
            self.pushButton_3.setText(self.tr("SettingsPage.JavaSettings.pushButton_3.Text"))
            self.label.setText(
                self.tr("SettingsPage.JavaSettings.label.Text.1") if not self.pushButton.isChecked() else self.tr(
                    "SettingsPage.JavaSettings.label.Text.2"))
            self.pushButton.setText(self.tr("SettingsPage.JavaSettings.pushButton.Text"))
        
        # retranslateUi
        
        def updateJavaPathIsAuto(self):
            global settings
            settings["Settings"]["JavaSettings"]["Java"]["Path"]["is_auto"] = self.pushButton_2.isChecked()
            if not self.pushButton_2.isChecked():
                self.comboBox.setEnabled(True)
                self.comboBox.setCurrentText(settings["Settings"]["JavaSettings"]["Java"]["Path"]["value"])
                self.searchJava()
            else:
                self.comboBox.clear()
                self.comboBox.setCurrentText(self.tr("SettingsPage.JavaSettings.comboBox.Text"))
                self.comboBox.setEnabled(False)
            self.pushButton_3.setEnabled(self.comboBox.isEnabled())
            self.retranslateUi()
        
        def updateJavaSelectPaths(self, data):
            if self.comboBox.currentText() not in data and self.comboBox.currentText() and Path(
                    self.comboBox.currentText()).exists():
                data = [self.comboBox.currentText()] + data
            self.comboBox.clear()
            for i in data:
                self.comboBox.addItem(i)
        
        def updateJavaPath(self, path):
            if not settings["Settings"]["JavaSettings"]["Java"]["Path"]["is_auto"]:
                settings["Settings"]["JavaSettings"]["Java"]["Path"]["value"] = path
            else:
                settings["Settings"]["JavaSettings"]["Java"]["Path"]["value"] = None
        
        def searchJava(self):
            thread = self.SearchVersionThread(self)
            thread.versionHasGot.connect(self.updateJavaSelectPaths)
            thread.start()
        
        def applyJavaByUser(self):
            file_filter = ""
            match platform.system().lower():
                case "windows":
                    file_filter = "java.exe"
                case "linux":
                    file_filter = "java"
            java = QFileDialog.getOpenFileName(self, self.tr("SettingsPage.JavaSettings.applyJavaDialogue.Title"),
                                               str(Path(".").absolute()), file_filter)
            java_path = Path(java[0])
            self.comboBox.addItem(str(java_path))
            self.comboBox.setCurrentText(str(java_path))
        
        def updateJVMArgIsOverride(self):
            global settings
            settings["Settings"]["JavaSettings"]["JVM"]["Arg"]["is_override"] = self.pushButton.isChecked()
            self.groupBox.setEnabled(not self.pushButton.isChecked())
            self.retranslateUi()
        
        def updateJavaLaunchMode(self):
            if self.radioButton.isChecked():
                settings["Settings"]["JavaSettings"]["Java"]["LaunchMode"] = "client"
            if self.radioButton_2.isChecked():
                settings["Settings"]["JavaSettings"]["Java"]["LaunchMode"] = "server"
        
        def editingFinished(self):
            if not self.lineEdit.text():
                self.setJVMArgs(None)
                return
            dialogue = MaskedDialogue(frame)
            label = Label(dialogue)
            label.setText(self.tr("SettingsPage.JavaSettings.JVMEditConfirmation.Text"))
            label.adjustSize()
            bottomPanel = Panel(dialogue)
            horizontalLayout = QHBoxLayout(bottomPanel)
            yesButton = PushButton(dialogue)
            yesButton.setText(self.tr("SettingsPage.JavaSettings.JVMEditConfirmation.OK"))  # 确定
            yesButton.pressed.connect(lambda: (dialogue.close(), self.setJVMArgs(self.lineEdit.text())))
            horizontalLayout.addWidget(yesButton)
            cancelButton = PushButton(dialogue)
            cancelButton.setText(self.tr("SettingsPage.JavaSettings.JVMEditConfirmation.Cancel"))  # 取消
            cancelButton.pressed.connect(lambda: (
                dialogue.close(), self.lineEdit.setText(settings["Settings"]["JavaSettings"]["JVM"]["Arg"]["value"])))
            dialogue.closeEvent = lambda e: self.lineEdit.setText(
                settings["Settings"]["JavaSettings"]["JVM"]["Arg"]["value"])
            horizontalLayout.addWidget(cancelButton)
            bottomPanel.adjustSize()
            bottomPanel.setGeometry(QRect(10, label.y() + label.height() + 30, label.width(), bottomPanel.height()))
            dialogue.setGeometry(
                QRect(dialogue.x(), dialogue.y(), 20 + label.width(), 20 + label.height() + 10 + bottomPanel.height()))
            label.move(10, 30)
            dialogue.exec()
        
        def setJVMArgs(self, args):
            global settings
            settings["Settings"]["JavaSettings"]["JVM"]["Arg"]["value"] = args
    
    class JavaSettingsContainer(ScrollArea):
        def __init__(self, parent, javasettings):
            super().__init__(parent)
            self.javaSettings = javasettings(self)
            self.setWidget(self.javaSettings)
            self.setWidgetResizable(True)
    
    class CustomiseSettings(QFrame):
        def __init__(self, parent):
            super().__init__(parent)
            self.setThemePreset(True, settings["Settings"]["LauncherSettings"]["Customise"]["CurrentThemePreset"])
            
            self.verticalLayout = QVBoxLayout(self)
            
            self.groupBox = GroupBox(self)
            self.verticalLayout.addWidget(self.groupBox)
            
            self.girdLayout = QGridLayout(self.groupBox)
            
            self.group1_radioButton = RadioButton(self.groupBox)
            self.group1_radioButton.setChecked(
                settings["Settings"]["LauncherSettings"]["Customise"]["CurrentThemePreset"] == "PresetBlue")
            self.group1_radioButton.toggled.connect(lambda state: self.setThemePreset(state, "PresetBlue"))
            
            self.girdLayout.addWidget(self.group1_radioButton, 0, 0)
            
            self.group1_radioButton_2 = RadioButton(self.groupBox)
            self.group1_radioButton_2.setChecked(
                settings["Settings"]["LauncherSettings"]["Customise"]["CurrentThemePreset"] == "PresetPink")
            self.group1_radioButton_2.toggled.connect(lambda state: self.setThemePreset(state, "PresetPink"))
            
            self.girdLayout.addWidget(self.group1_radioButton_2, 0, 1)
            
            self.group1_radioButton_3 = RadioButton(self.groupBox)
            self.group1_radioButton_3.setChecked(
                settings["Settings"]["LauncherSettings"]["Customise"]["CurrentThemePreset"] == "PresetRed")
            self.group1_radioButton_3.toggled.connect(lambda state: self.setThemePreset(state, "PresetRed"))
            
            self.girdLayout.addWidget(self.group1_radioButton_3, 1, 0)
            
            self.groupBox_2 = GroupBox(self)
            self.verticalLayout.addWidget(self.groupBox_2)
            
            self.verticalLayout_2 = QVBoxLayout(self.groupBox_2)
            
            self.girdLayout_2 = QGridLayout()
            self.verticalLayout_2.addLayout(self.girdLayout_2)
            
            self.group2_radioButton = RadioButton(self.groupBox_2)
            self.girdLayout_2.addWidget(self.group2_radioButton, 0, 0)
            
            self.group2_radioButton_2 = RadioButton(self.groupBox_2)
            self.group2_radioButton_2.setChecked(True)
            self.girdLayout_2.addWidget(self.group2_radioButton_2, 0, 1)
            
            self.tipLabel = Label(self.groupBox_2)
            self.verticalLayout_2.addWidget(self.tipLabel)
            
            self.formLayout = QFormLayout()
            
            self.label1 = Label(self.groupBox_2)
            
            self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label1)
            
            self.blurSlider = Slider(self.groupBox_2)
            self.blurSlider.setOrientation(Qt.Orientation.Horizontal)
            self.blurSlider.setMinimum(0)
            self.blurSlider.setMaximum(100)
            self.blurSlider.setValue(settings["Settings"]["LauncherSettings"]["Customise"]["BackgroundBlur"])
            self.blurSlider.valueChanged.connect(self.updateBackgroundBlur)
            self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.blurSlider)
            
            self.verticalLayout_2.addLayout(self.formLayout)
            
            self.groupBox_3 = GroupBox(self)
            self.groupBox_3.setCheckable(True)
            self.verticalLayout.addWidget(self.groupBox_3)
            
            self.verticalLayout_3 = QVBoxLayout(self.groupBox_3)
            
            self.group3_checkBox = SwitchButton(self.groupBox_3)
            self.group3_checkBox.setSwitchState(
                1 in settings["Settings"]["LauncherSettings"]["Customise"]["Animations"]["EnabledItems"])
            self.group3_checkBox.toggled.connect(lambda: self.updateAnimation(1))
            self.verticalLayout_3.addWidget(self.group3_checkBox)
            
            self.groupBox_4 = GroupBox(self)
            self.verticalLayout.addWidget(self.groupBox_4)
            
            self.verticalLayout_4 = QVBoxLayout(self.groupBox_4)
            
            self.formLayout_2 = QFormLayout()
            
            self.label2 = Label(self.groupBox_4)
            self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label2)
            
            self.comboBox = ComboBox(self.groupBox_4)
            self.comboBox.wheelEvent = lambda e: None
            self.updateComboBoxLanguageList()
            self.comboBox.currentIndexChanged.connect(self.comboBoxLanguageChanged)
            self.formLayout_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.comboBox)
            
            self.verticalLayout_4.addLayout(self.formLayout_2)
            
            self.translationMayNotBeCorrectLabel = Label(self.groupBox_4)
            self.verticalLayout_4.addWidget(self.translationMayNotBeCorrectLabel)
            
            self.verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
            self.verticalLayout.addItem(self.verticalSpacer)
            
            app.registerRetranslateFunction(self.retranslateUI)
            self.retranslateUI()
        
        def retranslateUI(self):
            self.groupBox.setTitle(self.tr("SettingsPage.CustomiseSettings.groupBox.Title"))
            self.group1_radioButton.setText(self.tr("SettingsPage.CustomiseSettings.group1_radioButton.Text"))
            self.group1_radioButton_2.setText(
                self.tr("SettingsPage.CustomiseSettings.group1_radioButton_2.Text"))
            self.group1_radioButton_3.setText(
                self.tr("SettingsPage.CustomiseSettings.group1_radioButton_3.Text"))
            self.groupBox_2.setTitle(self.tr("SettingsPage.CustomiseSettings.groupBox_2.Title"))
            self.group2_radioButton.setText(self.tr("SettingsPage.CustomiseSettings.group2_radioButton.Text"))
            self.group2_radioButton_2.setText(
                self.tr("SettingsPage.CustomiseSettings.group2_radioButton_2.Text"))
            self.tipLabel.setText(self.tr("SettingsPage.CustomiseSettings.tipLabel.Text"))
            self.label1.setText(self.tr("SettingsPage.CustomiseSettings.label1.Text"))
            self.groupBox_3.setTitle(self.tr("SettingsPage.CustomiseSettings.groupBox_3.Title"))
            self.group3_checkBox.setTextPrefix(self.tr("SettingsPage.CustomiseSettings.group3_checkBox.Text"))
            # self.group3_checkBox.setTextPrefix(self.tr("SettingsPage.CustomiseSettings.group3_checkBox.Text"))
            self.group3_checkBox.setSwitchOnText("开")
            self.group3_checkBox.setSwitchOffText("关")
            self.groupBox_4.setTitle(self.tr("SettingsPage.CustomiseSettings.groupBox_4.Title"))
            self.label2.setText(self.tr("SettingsPage.CustomiseSettings.label2.Text"))
            self.translationMayNotBeCorrectLabel.setText(
                self.tr("SettingsPage.CustomiseSettings.translationMayNotBeCorrectLabel.Text"))
        
        @staticmethod
        def setThemePreset(state, value):
            if not state:
                return
            settings["Settings"]["LauncherSettings"]["Customise"]["CurrentThemePreset"] = value
            if value in theme_colour_defines:
                define = theme_colour_defines[value]
                for theme in define:
                    for role in define[theme]:
                        for highlight in define[theme][role]:
                            setThemeColour(role, False, highlight, theme,
                                           theme_colour_defines[value][theme][role][highlight])
        
        def updateBackgroundBlur(self, value):
            settings["Settings"]["LauncherSettings"]["Customise"]["BackgroundBlur"] = value
        
        def updateAnimation(self, value):
            items = settings["Settings"]["LauncherSettings"]["Customise"]["Animations"]["EnabledItems"]
            if value == 1:
                print(self.group3_checkBox.isChecked())
                if value:
                    items.append(1)
                else:
                    items.remove(1)
            settings["Settings"]["LauncherSettings"]["Customise"]["Animations"]["EnabledItems"] = items
        
        def updateComboBoxLanguageList(self):
            self.comboBox.clear()
            sorted_languages_map = sorted(languages_map)
            for language in sorted_languages_map:
                self.comboBox.addItem(f"{languages_map[language]} ({language})")
            self.comboBox.setCurrentIndex(sorted(sorted_languages_map).index(current_language))
        
        def comboBoxLanguageChanged(self):
            global current_language
            settings["Settings"]["LauncherSettings"]["CurrentLanguage"] = self.comboBox.currentText().split(
                " ")[-1].strip("()")
            current_language = settings["Settings"]["LauncherSettings"]["CurrentLanguage"]
            app.removeTranslator(app.translator)
            app.removeTranslator(app.qt_translator)
            app.translator = QTranslator()
            app.translator.load(f":/CMCL_{current_language}.qm")
            app.installTranslator(app.translator)
            app.qt_translator = QTranslator()
            app.qt_translator.load(QLocale(locale.normalize(current_language.replace("-", "_")).split(".")[0]),
                                   "qtbase", "_",
                                   QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath))
            app.installTranslator(app.qt_translator)
            app.retranslate()
            saveSettings()
    
    class CustomiseSettingsContainer(ScrollArea):
        def __init__(self, parent, customisesettings):
            super().__init__(parent)
            self.customiseSettings = customisesettings(self)
            self.setWidget(self.customiseSettings)
            self.setWidgetResizable(True)
    
    def __init__(self, parent):
        super().__init__(parent)
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.navigationFrame = Panel(self)
        self.navigationFrameScrollAreaLayout = QVBoxLayout(self.navigationFrame)
        self.navigationFrameScrollAreaLayout.setContentsMargins(0, 0, 0, 0)
        self.navigationFrameScrollArea = ScrollArea(self.navigationFrame)
        self.navigationFrameScrollAreaLayout.addWidget(self.navigationFrameScrollArea)
        self.navigationFrameScrollArea.setFixedHeight(self.navigationFrame.height() + 10)
        self.navigationFrameScrollAreaWidgetContent = QWidget()
        self.horizontalLayout = QHBoxLayout(self.navigationFrameScrollAreaWidgetContent)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.pages = {}
        
        self.page = self.GameSettings(self)
        self.pushButton = PushButton(self.navigationFrameScrollAreaWidgetContent)
        self.pushButton.setCheckable(True)
        self.pushButton.setChecked(True)
        self.pushButton.setAutoExclusive(True)
        self.pushButton.pressed.connect(lambda: self.update_page(self.pushButton))
        
        self.horizontalLayout.addWidget(self.pushButton)
        self.pages[self.pushButton] = self.page
        
        self.page_2 = self.JavaSettingsContainer(self, self.JavaSettings)
        self.pushButton_2 = PushButton(self.navigationFrameScrollAreaWidgetContent)
        self.pushButton_2.setCheckable(True)
        self.pushButton_2.setAutoExclusive(True)
        self.pushButton_2.pressed.connect(lambda: self.update_page(self.pushButton_2))
        
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.pages[self.pushButton_2] = self.page_2
        
        self.page_3 = self.CustomiseSettingsContainer(self, self.CustomiseSettings)
        self.pushButton_3 = PushButton(self.navigationFrameScrollAreaWidgetContent)
        self.pushButton_3.setCheckable(True)
        self.pushButton_3.setAutoExclusive(True)
        self.pushButton_3.pressed.connect(lambda: self.update_page(self.pushButton_3))
        
        self.horizontalLayout.addWidget(self.pushButton_3)
        self.pages[self.pushButton_3] = self.page_3
        
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        self.horizontalLayout.addItem(self.horizontalSpacer)
        
        self.navigationFrameScrollArea.setWidget(self.navigationFrameScrollAreaWidgetContent)
        self.navigationFrameScrollArea.setWidgetResizable(True)
        
        self.verticalLayout.addWidget(self.navigationFrame)
        
        self.stackedWidget = AnimatedStackedWidget(self)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.addWidget(self.page)
        self.stackedWidget.addWidget(self.page_2)
        self.stackedWidget.addWidget(self.page_3)
        
        self.verticalLayout.addWidget(self.stackedWidget, 1)
        
        app.registerRetranslateFunction(self.retranslateUi)
        self.retranslateUi()
        #
        # QMetaObject.connectSlotsByName(Form)
    
    # setupUi
    
    def retranslateUi(self):
        self.pushButton.setText(self.tr("SettingsPage.pushButton.Text"))
        self.pushButton_2.setText(self.tr("SettingsPage.pushButton_2.Text"))
        self.pushButton_3.setText(self.tr("SettingsPage.pushButton_3.Text"))
    
    # retranslateUi
    
    def update_page(self, btn):
        self.stackedWidget.setCurrentWidget(self.pages[btn])


class AboutPage(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.verticalLayout = QVBoxLayout(self)
        self.toolBox = ToolBox(self)
        
        self.page1 = QFrame(self.toolBox)
        self.verticalLayout_2 = QVBoxLayout(self.page1)
        
        self.panel1 = Panel(self.page1)
        self.horizontalLayout = QHBoxLayout(self.panel1)
        
        self.avatar1 = ToolButton(self.panel1)
        self.avatar1.setFixedSize(QSize(42, 42))
        self.avatar1.setIconSize(QSize(32, 32))
        self.avatar1.setIcon(QIcon(":/chengwm_avatar.png"))
        
        self.horizontalLayout.addWidget(self.avatar1)
        
        self.label1 = Label(self.panel1)
        self.label1.setText("chengwm\n" + self.tr('AboutPage.label1.Text'))
        
        self.horizontalLayout.addWidget(self.label1, 1)
        
        self.verticalLayout_2.addWidget(self.panel1)
        
        self.panel2 = Panel(self.page1)
        self.horizontalLayout_2 = QHBoxLayout(self.panel2)
        
        self.avatar2 = ToolButton(self.panel2)
        self.avatar2.setFixedSize(QSize(42, 42))
        self.avatar2.setIconSize(QSize(32, 32))
        self.avatar2.setIcon(QIcon(":/mcdaotian_avatar.png"))
        
        self.horizontalLayout_2.addWidget(self.avatar2)
        
        self.label2 = Label(self.panel2)
        self.label2.setText(
            self.tr('AboutPage.label2.Text.LocalisedName') + "\n" + self.tr(
                'AboutPage.label2.Text'))
        
        self.horizontalLayout_2.addWidget(self.label2, 1)
        
        self.verticalLayout_2.addWidget(self.panel2)
        
        self.verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.verticalLayout_2.addItem(self.verticalSpacer)
        
        self.toolBox.addItem(self.page1, self.tr("AboutPage.Page1.Title"))
        
        self.page2 = QFrame(self.toolBox)
        self.verticalLayout_3 = QVBoxLayout(self.page2)
        
        self.panel_cmcl = Panel(self.page2)
        self.horizontalLayout_3 = QHBoxLayout(self.panel_cmcl)
        
        self.cmcl_icon = ToolButton(self.panel_cmcl)
        self.cmcl_icon.setFixedSize(QSize(74, 74))
        self.cmcl_icon.setIconSize(QSize(64, 64))
        self.cmcl_icon.setIcon(QIcon(":/CommonMinecraftLauncherIcon.svg"))
        
        self.horizontalLayout_3.addWidget(self.cmcl_icon)
        
        self.cmcl_info = Label(self.panel_cmcl)
        self.cmcl_info.setText(
            self.tr("AboutPage.Page2.CMCL_info").format(CMCL_version[0], CMCL_version[1],
                                                        languages_map.get(current_language, current_language)))
        
        self.horizontalLayout_3.addWidget(self.cmcl_info, 1)
        
        self.verticalLayout_3.addWidget(self.panel_cmcl)
        
        self.verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.verticalLayout_3.addItem(self.verticalSpacer)
        
        self.toolBox.addItem(self.page2, self.tr("AboutPage.Page2.Title"))
        
        translationjson = QFile(":/aboutPageTranslations.json")
        translationjson.open(QIODevice.OpenModeFlag.ReadOnly)
        translationjson = json.loads(QTextStream(translationjson).readAll())
        
        def gettrans(numb, text):
            if numb:
                return translationjson[current_language][numb].get(text, translationjson["zh-cn"][numb][text])
            return translationjson[current_language].get(text, translationjson["zh-cn"][text])
        
        self.page3 = QFrame()
        self.verticalLayout_4 = QVBoxLayout(self.page3)
        
        self.noteTip = Tip(self.page3)
        
        self.label_3 = Label(self.noteTip)
        self.label_3.setText(gettrans(None, "announcement"))
        self.label_3.adjustSize()
        self.noteTip.setCloseEnabled(False)
        self.noteTip.setMinimumHeight(self.label_3.height() + 10)
        self.noteTip.setMinimumWidth(self.label_3.width() + 10)
        self.noteTip.setCentralWidget(self.label_3)
        
        self.verticalLayout_4.addWidget(self.noteTip)
        
        self.card1 = Panel(self.page3)
        self.horizontalLayout_4 = QHBoxLayout(self.card1)
        
        self.avatar3 = ToolButton(self.card1)
        self.avatar3.setFixedSize(QSize(42, 42))
        self.avatar3.setIconSize(QSize(32, 32))
        self.horizontalLayout_4.addWidget(self.avatar3)
        
        self.label3 = Label(self.card1)
        self.label3.setText(gettrans("1", "name") + "\n" + gettrans("1", "description"))
        self.horizontalLayout_4.addWidget(self.label3, 1)
        
        self.verticalLayout_4.addWidget(self.card1)
        
        self.card2 = Panel(self.page3)
        self.horizontalLayout_5 = QHBoxLayout(self.card2)
        
        self.avatar4 = ToolButton(self.card2)
        self.avatar4.setFixedSize(QSize(42, 42))
        self.avatar4.setIconSize(QSize(32, 32))
        self.horizontalLayout_5.addWidget(self.avatar4)
        
        self.label4 = Label(self.card2)
        self.label4.setText(gettrans("2", "name") + "\n" + gettrans("2", "description"))
        self.horizontalLayout_5.addWidget(self.label4, 1)
        
        self.verticalLayout_4.addWidget(self.card2)
        
        self.card3 = Panel(self.page3)
        self.horizontalLayout_6 = QHBoxLayout(self.card3)
        
        self.avatar5 = ToolButton(self.card3)
        self.avatar5.setFixedSize(QSize(42, 42))
        self.avatar5.setIconSize(QSize(32, 32))
        self.horizontalLayout_6.addWidget(self.avatar5)
        
        self.label5 = Label(self.card2)
        self.label5.setText(gettrans("3", "name") + "\n" + gettrans("3", "description"))
        self.horizontalLayout_6.addWidget(self.label5, 1)
        
        self.verticalLayout_4.addWidget(self.card3)
        
        self.verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.verticalLayout_4.addItem(self.verticalSpacer)
        
        self.page3container = ScrollArea(self.toolBox)
        self.page3container.setWidget(self.page3)
        self.page3container.setWidgetResizable(True)
        
        self.toolBox.addItem(self.page3container, gettrans(None, "title"))
        
        self.verticalLayout.addWidget(self.toolBox)
        
        app.registerRetranslateFunction(self.retranslateUI)
        self.retranslateUI()
    
    def retranslateUI(self):
        self.toolBox.setItemText(self.toolBox.indexOf(self.page1), self.tr("AboutPage.Page1.Title"))
        self.label1.setText("chengwm\n" + self.tr('AboutPage.label1.Text'))
        self.label2.setText(
            self.tr('AboutPage.label2.Text.LocalisedName') + "\n" + self.tr(
                'AboutPage.label2.Text'))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page2), self.tr("AboutPage.Page2.Title"))
        self.cmcl_info.setText(
            self.tr("AboutPage.Page2.CMCL_info").format(CMCL_version[0], CMCL_version[1],
                                                        languages_map.get(current_language, current_language)))
        
        translationjson = QFile(":/aboutPageTranslations.json")
        translationjson.open(QIODevice.OpenModeFlag.ReadOnly)
        translationjson = json.loads(QTextStream(translationjson).readAll())
        
        def gettrans(numb, text):
            if numb:
                return translationjson[current_language][numb].get(text, translationjson["zh-cn"][numb][text])
            return translationjson[current_language].get(text, translationjson["zh-cn"][text])
        
        self.toolBox.setItemText(self.toolBox.indexOf(self.page3container), gettrans(None, "title"))
        self.label_3.setText(gettrans(None, "announcement"))
        self.label3.setText(gettrans("1", "name") + "\n" + gettrans("1", "description"))
        self.label4.setText(gettrans("2", "name") + "\n" + gettrans("2", "description"))
        self.label5.setText(gettrans("3", "name") + "\n" + gettrans("3", "description"))


class OfflinePlayerCreationDialogue(MaskedDialogue):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {'white' if getTheme() == Theme.Light else 'black'}")
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(5, 37, 5, 5)
        self.formLayout = QFormLayout(self)
        self.label = Label(self)
        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)
        self.playernameLineEdit = LineEdit(self)
        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.playernameLineEdit)
        self.verticalLayout.addLayout(self.formLayout)
        self.bottomPanel = Panel(self)
        self.horizontalLayout = QHBoxLayout(self.bottomPanel)
        self.CancelButton = PushButton(self.bottomPanel)
        self.horizontalLayout.addWidget(self.CancelButton)
        self.CancelButton.pressed.connect(self.close)
        self.horizontalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.OKButton = PushButton(self.bottomPanel)
        self.horizontalLayout.addWidget(self.OKButton)
        self.OKButton.pressed.connect(self.setPlayer)
        self.verticalLayout.addWidget(self.bottomPanel)
        app.registerRetranslateFunction(self.retranslateUI)
        self.retranslateUI()
    
    def retranslateUI(self):
        self.label.setText(self.tr("OfflinePlayerCreationDialogue.label.Text"))
        self.CancelButton.setText(self.tr("OfflinePlayerCreationDialogue.CancelButton.Text"))
        self.OKButton.setText(self.tr("OfflinePlayerCreationDialogue.OKButton.Text"))
    
    def setPlayer(self):
        global player
        player = create_offline_player(self.playernameLineEdit.text(), player.player_hasMC)
        frame.UserPage.user_datas.append(player)
        frame.UserPage.select_new_user(frame.UserPage.current_user + 1)
        self.close()
    
    def paintEvent(self, a0, **kwargs):
        background = QPixmap(self.size())
        p = QPainter(background)
        x = 0 if self.isMaximized() else -self.geometry().x()
        y = 0 if self.isMaximized() else -self.geometry().y()
        p.fillRect(
            QRect(x, y, QGuiApplication.primaryScreen().geometry().width(),
                  QGuiApplication.primaryScreen().geometry().height()),
            QGradient(QGradient.Preset.FreshOasis if getTheme() == Theme.Light else QGradient.Preset.NightSky))
        p.end()
        scene = QGraphicsScene()
        item = QGraphicsPixmapItem()
        item.setPixmap(background)
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(settings["Settings"]["LauncherSettings"]["Customise"]["BackgroundBlur"])
        item.setGraphicsEffect(blur)
        scene.addItem(item)
        img = QPixmap(background.size())
        img.fill(Qt.GlobalColor.transparent)
        ptr = QPainter(img)
        scene.render(ptr, QRectF(img.rect()), QRectF(img.rect()))
        ptr.end()
        painter = QPainter(self)
        rect = QRect(-20, -20, self.width() + 40, self.height() + 40)
        painter.drawPixmap(rect, img)


class UserPage(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.user_datas = [player]
        self.current_user = 0
        
        # DEBUG: ON#
        # self.user_datas.append(create_online_player("2233", "68559", "TheFengHaoDouLuoOfBiZhan", True))
        # self.user_datas.append(create_online_player("22和33", "68559", "TheSameAsAbove", True))
        # self.user_datas.append(player)
        # self.user_datas.append(create_online_player("chengwm_CMCL", "100000000", "NoAccessToken", False))
        # self.current_user = 2
        # DEBUG: END#
        
        self.user_type_localisations = {
            "msa": self.tr("UserPage.UserTypeLocalisations.msa"),
            "offline": self.tr("UserPage.UserTypeLocalisations.offline"),
            "authlib-injector": self.tr("UserPage.UserTypeLocalisations.authlib-injector"),
            "littleskin": self.tr("UserPage.UserTypeLocalisations.littleskin")
        }
        
        self.verticalLayout = QVBoxLayout(self)
        self.topPanel = Panel(self)
        self.horizontalLayout = QHBoxLayout(self.topPanel)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.leftUserIcon = ToolButton(self.topPanel)
        self.leftUserIcon.setIcon(QIcon(""))
        self.leftUserIcon.setIconSize(QSize(32, 32))
        self.leftUserIcon.setVisible(len(self.user_datas) > 1 and self.current_user >= 1)
        if len(self.user_datas) > 1 and self.current_user >= 1:
            left_user = self.user_datas[min(max(self.current_user - 1, 0), len(self.user_datas) - 1)]
            self.leftUserIcon.setToolTip(
                self.tr("UserPage.UserDataFormat.Text").format(left_user.player_playerName,
                                                               self.user_type_localisations[
                                                                   left_user.player_accountType[1]] if
                                                               left_user.player_accountType[0] != "offline" else
                                                               self.user_type_localisations["offline"],
                                                               left_user.player_hasMC))
        else:
            self.leftUserIcon.setToolTip("")
        self.leftUserIcon.pressed.connect(lambda: self.select_new_user(self.current_user - 1))
        self.horizontalLayout.addWidget(self.leftUserIcon)
        spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacer)
        self.UserIcon = ToolButton(self.topPanel)
        self.UserIcon.setIcon(QIcon(""))
        self.UserIcon.setIconSize(QSize(32, 32))
        if len(self.user_datas) > 0:
            current_user = self.user_datas[self.current_user]
            self.UserIcon.setText(
                self.tr("UserPage.UserDataFormat.Text").format(current_user.player_playerName,
                                                               self.user_type_localisations[
                                                                   current_user.player_accountType[1]] if
                                                               current_user.player_accountType[0] != "offline" else
                                                               self.user_type_localisations["offline"],
                                                               current_user.player_hasMC))
        else:
            self.UserIcon.setText(self.tr("UserPage.UserIconNoUser.Text"))
        self.UserIcon.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.UserIcon.pressed.connect(self.mainButtonPressed)
        self.horizontalLayout.addWidget(self.UserIcon)
        spacer2 = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacer2)
        self.rightUserIcon = ToolButton(self.topPanel)
        self.rightUserIcon.setIcon(QIcon(""))
        self.rightUserIcon.setIconSize(QSize(32, 32))
        self.rightUserIcon.setVisible(len(self.user_datas) > 1 and self.current_user < len(self.user_datas) - 1)
        if len(self.user_datas) > 1 and self.current_user < len(self.user_datas) - 1:
            right_user = self.user_datas[min(max(self.current_user + 1, 0), len(self.user_datas) - 1)]
            self.rightUserIcon.setToolTip(
                self.tr("UserPage.UserDataFormat.Text").format(right_user.player_playerName,
                                                               self.user_type_localisations[
                                                                   right_user.player_accountType[1]] if
                                                               right_user.player_accountType[0] != "offline" else
                                                               self.user_type_localisations["offline"],
                                                               right_user.player_hasMC))
        else:
            self.rightUserIcon.setToolTip("")
        self.rightUserIcon.pressed.connect(lambda: self.select_new_user(self.current_user + 1))
        self.horizontalLayout.addWidget(self.rightUserIcon)
        self.verticalLayout.addWidget(self.topPanel)
        
        self.centrePanel = Panel(self)
        self.horizontalLayout_2 = QHBoxLayout(self.centrePanel)
        self.addUserBtn = ToolButton(self.centrePanel)
        self.createAddUserBtnActions()
        self.horizontalLayout_2.addWidget(self.addUserBtn)
        self.horizontalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.horizontalLayout_2.addItem(self.horizontalSpacer)
        self.verticalLayout.addWidget(self.centrePanel)
        
        self.userTabel = TableView(self)
        self.verticalLayout.addWidget(self.userTabel)
        self.userTabel.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.userTabel.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.userTabel.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.userTabel.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.userTabel.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.userTabel.horizontalHeader().setVisible(True)
        self.userTabel.verticalHeader().setVisible(False)
        self.userModel = QStandardItemModel()
        self.userModel.setHorizontalHeaderLabels([self.tr("UserPage.userTable.horizontalHeaderLabels.1"),
                                                  self.tr("UserPage.userTable.horizontalHeaderLabels.2")])
        self.userTabel.setModel(self.userModel)
        self.userModel.clear()
        self.userModel.setHorizontalHeaderLabels([self.tr("UserPage.userTable.horizontalHeaderLabels.1"),
                                                  self.tr("UserPage.userTable.horizontalHeaderLabels.2")])
        for e, i in enumerate(self.user_datas):
            self.userModel.setItem(e, 0, QStandardItem(i.player_playerName))
            self.userModel.setItem(e, 1, QStandardItem(
                (self.user_type_localisations[i.player_accountType[1]]
                 if i.player_accountType[0] != "offline"
                 else self.user_type_localisations["offline"]) + self.tr("UserPage.UserTypeLocalisations.suffix")))
        
        app.registerRetranslateFunction(self.retranslateUI)
        self.retranslateUI()
        
        def tempfun(self):
            if len(self.user_datas) > 0:
                current_user = self.user_datas[self.current_user]
                self.UserIcon.setText(
                    self.tr("UserPage.UserDataFormat.Text").format(current_user.player_playerName,
                                                                   self.user_type_localisations[
                                                                       current_user.player_accountType[1]] if
                                                                   current_user.player_accountType[0] != "offline" else
                                                                   self.user_type_localisations["offline"],
                                                                   current_user.player_hasMC))
            else:
                self.UserIcon.setText(self.tr("UserPage.UserIconNoUser.Text"))
            self.userModel.clear()
            self.userModel.setHorizontalHeaderLabels([self.tr("UserPage.userTable.horizontalHeaderLabels.1"),
                                                      self.tr("UserPage.userTable.horizontalHeaderLabels.2")])
            for e, i in enumerate(self.user_datas):
                self.userModel.setItem(e, 0, QStandardItem(i.player_playerName))
                self.userModel.setItem(e, 1, QStandardItem(
                    (self.user_type_localisations[i.player_accountType[1]]
                     if i.player_accountType[0] != "offline"
                     else self.user_type_localisations["offline"]) + self.tr("UserPage.UserTypeLocalisations.suffix")))
        
        timer = QTimer(self)
        timer.setInterval(100)
        timer.timeout.connect(lambda: tempfun(self))
        timer.start()
    
    def retranslateUI(self):
        self.user_type_localisations = {
            "msa": self.tr("UserPage.UserTypeLocalisations.msa"),
            "offline": self.tr("UserPage.UserTypeLocalisations.offline"),
            "authlib-injector": self.tr("UserPage.UserTypeLocalisations.authlib-injector"),
            "littleskin": self.tr("UsetPage.UserTypeLocalisations.littleskin")
        }
        if len(self.user_datas) > 1 and self.current_user >= 1:
            left_user = self.user_datas[min(max(self.current_user - 1, 0), len(self.user_datas) - 1)]
            self.leftUserIcon.setToolTip(
                self.tr("UserPage.UserDataFormat.Text").format(left_user.player_playerName,
                                                               self.user_type_localisations[
                                                                   left_user.player_accountType[1]] if
                                                               left_user.player_accountType[0] != "offline" else
                                                               self.user_type_localisations["offline"],
                                                               left_user.player_hasMC))
        else:
            self.leftUserIcon.setToolTip("")
        if len(self.user_datas) > 0:
            current_user = self.user_datas[self.current_user]
            self.UserIcon.setText(
                self.tr("UserPage.UserDataFormat.Text").format(current_user.player_playerName,
                                                               self.user_type_localisations[
                                                                   current_user.player_accountType[1]] if
                                                               current_user.player_accountType[0] != "offline" else
                                                               self.user_type_localisations["offline"],
                                                               current_user.player_hasMC))
        else:
            self.UserIcon.setText(self.tr("UserPage.UserIconNoUser.Text"))
        if len(self.user_datas) > 1 and self.current_user < len(self.user_datas) - 1:
            right_user = self.user_datas[min(max(self.current_user + 1, 0), len(self.user_datas) - 1)]
            self.rightUserIcon.setToolTip(
                self.tr("UserPage.UserDataFormat.Text").format(right_user.player_playerName,
                                                               self.user_type_localisations[
                                                                   right_user.player_accountType[1]] if
                                                               right_user.player_accountType[0] != "offline" else
                                                               self.user_type_localisations["offline"],
                                                               right_user.player_hasMC))
        else:
            self.rightUserIcon.setToolTip("")
        self.addUserBtn.setText(self.tr("UserPage.addUserBtn.Text"))
        self.createAddUserBtnActions()
        self.userModel.clear()
        self.userModel.setHorizontalHeaderLabels([self.tr("UserPage.userTable.horizontalHeaderLabels.1"),
                                                  self.tr("UserPage.userTable.horizontalHeaderLabels.2")])
        for e, i in enumerate(self.user_datas):
            self.userModel.setItem(e, 0, QStandardItem(i.player_playerName))
            self.userModel.setItem(e, 1, QStandardItem(
                (self.user_type_localisations[i.player_accountType[1]]
                 if i.player_accountType[0] != "offline"
                 else self.user_type_localisations["offline"]) + self.tr("UserPage.UserTypeLocalisations.suffix")))
    
    def paintEvent(self, a0):
        self.leftUserIcon.setVisible(len(self.user_datas) > 1 and self.current_user >= 1)
        self.rightUserIcon.setVisible(len(self.user_datas) > 1 and self.current_user < len(self.user_datas) - 1)
        self.leftUserIcon.setIcon(QIcon(f":/user_icon-{'black' if getTheme() == Theme.Light else 'white'}.svg"))
        self.UserIcon.setIcon(QIcon(f":/user_icon-{'black' if getTheme() == Theme.Light else 'white'}.svg"))
        self.rightUserIcon.setIcon(QIcon(f":/user_icon-{'black' if getTheme() == Theme.Light else 'white'}.svg"))
        super().paintEvent(a0)
    
    def createAddUserBtnActions(self):
        menu = RoundedMenu(self.addUserBtn)
        action1 = QAction(menu)
        action1.setText(self.tr("UserPage.addUserBtn.Item1.Text"))
        action1.triggered.connect(self.startLogin)
        menu.addAction(action1)
        action2 = QAction(menu)
        action2.setText(self.tr("UserPage.addUserBtn.Item2.Text"))
        action2.triggered.connect(self.startCreateOfflinePlayer)
        menu.addAction(action2)
        self.addUserBtn.setMenu(menu)
        self.addUserBtn.setPopupMode(ToolButton.ToolButtonPopupMode.InstantPopup)
    
    def select_new_user(self, id):
        global player
        self.current_user = id
        self.keep_current_user_range()
        player = self.user_datas[self.current_user]
        self.leftUserIcon.setDown(False)
        self.rightUserIcon.setDown(False)
        app.registerRetranslateFunction(self.retranslateUI)
        self.retranslateUI()
    
    def keep_current_user_range(self):
        self.current_user = max(0, min(len(self.user_datas) - 1, self.current_user))
    
    def mainButtonPressed(self):
        if self.user_datas:
            return
        self.startLogin()
    
    @staticmethod
    def startLogin():
        dialogue = LoginDialogue(frame)
        dialogue.exec()
    
    @staticmethod
    def startCreateOfflinePlayer():
        dialogue = OfflinePlayerCreationDialogue(frame)
        dialogue.exec()


class ErrorDialogue(MaskedDialogue):
    class ErrorText(HighlightTextEdit):
        class Highlighter(HighlightTextEdit.Highlighter):
            def __init__(self, document):
                super().__init__(document)
                
                string = QTextCharFormat()
                string.setForeground(QColor(0, 170, 9))
                
                url = QTextCharFormat()
                url.setForeground(QColor(100, 80, 255))
                url.setFontUnderline(True)
                
                self.highlight_styles["string"] = string
                self.highlight_styles["url"] = url
                
                stringprefix = r"(?i:r|u|f|fr|rf|b|br|rb)?"
                sqstring = stringprefix + r"'[^'\\\n]*(\\.[^'\\\n]*)*'?"
                dqstring = stringprefix + r'"[^"\\\n]*(\\.[^"\\\n]*)*"?'
                sq3string = stringprefix + r"'''[^'\\]*((\\.|'(?!''))[^'\\]*)*(''')?"
                dq3string = stringprefix + r'"""[^"\\]*((\\.|"(?!""))[^"\\]*)*(""")?'
                string = "|".join([sqstring, dqstring, sq3string, dq3string])
                
                self.rules.extend([
                    (string, 0, "string"),
                    (r"http[s]?://(.+|\[.+\])(:[0-9]+)?(/(.+|#))?", 0, "url")
                ])
        
        Default_Highlighter = Highlighter
    
    def __init__(self, parent, errorMessage):
        super().__init__(parent)
        self.message = errorMessage
        
        self.label = self.ErrorText(self)
        self.label.setFont(fixedFont)
        self.label.setText(self.message)
        self.label.setReadOnly(True)
        self.label.setLineWrapMode(self.ErrorText.LineWrapMode.NoWrap)
        
        rect = self.label.fontMetrics().boundingRect(self.label.rect(), self.label.alignment(),
                                                     self.label.toPlainText())
        rect.setSize(
            rect.size() + QSize(self.label.verticalScrollBar().width(), self.label.horizontalScrollBar().height()))
        rect.moveTo(self.pos())
        self.setGeometry(rect)
        
        geometry = self.parent().rect()
        size = QGuiApplication.primaryScreen().geometry().size()
        point = QPoint(min(max(geometry.width() // 2 - self.width() // 2, 0), size.width()),
                       min(max(0, geometry.height() // 2 - self.height() // 2), size.height()))
        self.move(point)
        
        self.setMaximumSize(QGuiApplication.primaryScreen().geometry().size())
    
    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        if hasattr(self, "label"):
            self.label.setGeometry(10, 40, self.width() - 20, self.height() - 50)


class MainWindow(window_class):
    def __init__(self):
        super().__init__()
        self.resize(800, 600)
        self.setWindowIcon(QIcon(":/CommonMinecraftLauncherIcon.svg"))
        title = "Common Minecraft Launcher"
        if random.randint(1, 100) == random.randint(1, 100):
            title = "Chengwm's Minecraft Launcher"
        if random.randint(1, 100000) == random.randint(1, 100000):
            title = title.replace("Minecraft", "Minceraft")
        self.setWindowTitle(title)
        # self.setWindowOpacity(0.9)
        self.setStyleSheet("background: transparent")
        self.centralwidget = QWidget(self)
        self.horizontalLayout = QVBoxLayout(self.centralwidget)
        self.horizontalLayout.setContentsMargins(5, 35, 5, 5)
        self.horizontalLayout.setSpacing(10)
        self.topWidget = NavigationPanel(self.centralwidget)
        self.topWidget.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.HomePage = MainPage(self)
        self.topWidget.addItem(self.HomePage, "", self.tr("MainWindow.HomePage.Text"))
        self.DownloadPage = DownloadPage(self)
        self.topWidget.addItem(self.DownloadPage, "", self.tr("MainWindow.DownloadPage.Text"))
        self.SettingsPage = SettingsPage(self)
        self.topWidget.addItem(self.SettingsPage, "", self.tr("MainWindow.SettingsPage.Text"))
        self.AboutPage = AboutPage(self)
        self.topWidget.addItem(self.AboutPage, "", self.tr("MainWindow.AboutPage.Text"))
        self.UserPage = UserPage(self)
        self.topWidget.addItem(self.UserPage, ":/user_icon-black.svg", self.tr("MainWindow.UserPage.Text"),
                               pos=NavigationPanel.NavigationItemPosition.Right)
        self.topWidget.addButton("", "", selectable=False, pressed=self.toggle_theme,
                                 pos=NavigationPanel.NavigationItemPosition.Right)
        self.horizontalLayout.addWidget(self.topWidget)
        # self.topWidget.removeButton(1)
        self.content = ContentPanel(self.centralwidget)
        self.horizontalLayout.addWidget(self.content, 1)
        self.topWidget.setContentWidget(self.content)
        timer = QTimer(self)
        timer.timeout.connect(self.updateIcon)
        timer.start(100)
        # tip = Tip(self)
        # self.horizontalLayout.addWidget(tip)
        # popoutTip = PopupTip(self)
        # popoutTip.tip()
        self.centralwidget.setLayout(self.horizontalLayout)
        self.setCentralWidget(self.centralwidget)
        
        app.registerRetranslateFunction(self.retranslateUI)
        self.retranslateUI()
        
        # April FOOL Code:
        if datetime.datetime.now().month == 4 and datetime.datetime.now().day == 1:
            self.dx = self.dy = 1
            t = QTimer(self)
            t.timeout.connect(self.SUPERFOOL)
            t.start(1)
        else:
            self.dx = self.dy = 0
    
    def SUPERFOOL(self):
        self.move(self.x() + self.dx, self.y() + self.dy)
        sg = QGuiApplication.primaryScreen().geometry()
        if self.x() <= 0 or self.x() + self.width() >= sg.width():
            self.dx = -self.dx
        if self.y() <= 0 or self.y() + self.height() >= sg.height():
            self.dy = -self.dy
    
    def mousePressEvent(self, a0):
        super().mousePressEvent(a0)
        if 0 <= a0.pos().x() - self.x() <= 100 and 0 <= a0.pos().y() - self.x() <= 100:
            self.dx = self.dy = 0
        else:
            if self.dx and self.dy:
                if self.dx > 0:
                    self.dx += 1
                else:
                    self.dx -= 1
                if self.dy > 0:
                    self.dy += 1
                else:
                    self.dy -= 1
    
    # End
    
    def setCentre(self):
        geometry = QGuiApplication.primaryScreen().geometry()
        point = QPoint(geometry.width() // 2 - self.width() // 2, geometry.height() // 2 - self.height() // 2)
        self.move(point)
    
    @staticmethod
    def toggle_theme():
        if getTheme() == Theme.Light:
            setTheme(Theme.Dark)
            settings["Settings"]["LauncherSettings"]["Customise"]["CurrentTheme"] = "Dark"
        elif getTheme() == Theme.Dark:
            setTheme(Theme.Light)
            settings["Settings"]["LauncherSettings"]["Customise"]["CurrentTheme"] = "Light"
        for window in QGuiApplication.allWindows():
            window.requestUpdate()
    
    def errorDialogue(self, message):
        dialogue = ErrorDialogue(self, message)
        dialogue.exec()
    
    def updateIcon(self):
        if self.topWidget.button("1"):
            self.topWidget.button("1").setIcon(QIcon(f":/Home-{'black' if getTheme() == Theme.Light else 'white'}.svg"))
        if self.topWidget.button("2"):
            self.topWidget.button("2").setIcon(
                QIcon(f":/Download-{'black' if getTheme() == Theme.Light else 'white'}.svg"))
        if self.topWidget.button("3"):
            self.topWidget.button("3").setIcon(
                QIcon(f":/Settings-{'black' if getTheme() == Theme.Light else 'white'}.svg"))
        if self.topWidget.button("4"):
            self.topWidget.button("4").setIcon(
                QIcon(f":/About-{'black' if getTheme() == Theme.Light else 'white'}.svg"))
        if self.topWidget.button("5"):
            self.topWidget.button("5").setIcon(
                QIcon(f":/user_icon-{'black' if getTheme() == Theme.Light else 'white'}.svg"))
        if self.topWidget.button("6"):
            self.topWidget.button("6").setIcon(QIcon(f":/{'light' if getTheme() == Theme.Light else 'dark'}.svg"))
            self.topWidget.button("6").setText(
                self.tr("MainPage.ToggleTheme.Light.Text") if getTheme() == Theme.Light else self.tr(
                    "MainPage.ToggleTheme.Dark.Text"))
    
    def retranslateUI(self):
        if self.topWidget.button("1"):
            self.topWidget.button("1").setText(self.tr("MainWindow.HomePage.Text"))
        if self.topWidget.button("2"):
            self.topWidget.button("2").setText(self.tr("MainWindow.DownloadPage.Text"))
        if self.topWidget.button("3"):
            self.topWidget.button("3").setText(self.tr("MainWindow.SettingsPage.Text"))
        if self.topWidget.button("4"):
            self.topWidget.button("4").setText(self.tr("MainWindow.AboutPage.Text"))
        if self.topWidget.button("5"):
            self.topWidget.button("5").setText(self.tr("MainWindow.UserPage.Text"))
    
    def paintEvent(self, a0, **kwargs):
        background = QPixmap(self.size())
        p = QPainter(background)
        x = 0 if self.isMaximized() else -self.geometry().x()
        y = 0 if self.isMaximized() else -self.geometry().y()
        p.fillRect(
            QRect(x, y, QGuiApplication.primaryScreen().geometry().width(),
                  QGuiApplication.primaryScreen().geometry().height()),
            QGradient(backgroundGradient[int(not getTheme() == Theme.Light)]))
        p.end()
        scene = QGraphicsScene()
        item = QGraphicsPixmapItem()
        item.setPixmap(background)
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(settings["Settings"]["LauncherSettings"]["Customise"]["BackgroundBlur"])
        item.setGraphicsEffect(blur)
        scene.addItem(item)
        img = QPixmap(background.size())
        img.fill(Qt.GlobalColor.transparent)
        ptr = QPainter(img)
        scene.render(ptr, QRectF(img.rect()), QRectF(img.rect()))
        ptr.end()
        painter = QPainter(self)
        rect = QRect(-20, -20, self.width() + 40, self.height() + 40)
        painter.drawPixmap(rect, img)
        # painter.setPen(Qt.PenStyle.NoPen)
        # painter.setBrush(QBrush(img))
        # painter.drawRoundedRect(self.rect(), 10, 10)
    
    def showEvent(self, a0):
        super().showEvent(a0)
        
        class OpacityAnimation(QVariantAnimation):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.valueChanged.connect(self.__updateOpacity)
            
            def __updateOpacity(self, value):
                op = QGraphicsOpacityEffect(self.parent())
                op.setOpacity(self.currentValue() / 100)
                if self.currentValue() == self.endValue():
                    self.parent().setGraphicsEffect(None)
                    return
                self.parent().setGraphicsEffect(op)
        
        ani = QPropertyAnimation(self.content, b"pos", parent=self)
        ani.setDuration(1000)
        ani.setStartValue(QPoint(self.content.x(), self.content.y() + 300))
        ani.setEndValue(QPoint(self.content.x(), self.content.y() + 5))
        ani.setEasingCurve(QEasingCurve.Type.OutQuad)
        ani.start()
        ani2 = OpacityAnimation(self.content)
        ani2.setDuration(1000)
        ani2.setStartValue(0)
        ani2.setEndValue(100)
        ani2.setEasingCurve(QEasingCurve.Type.OutQuad)
        ani2.start()
        self.update()


class LoggingWindow(window_class):
    class LoggingText(HighlightTextEdit):  # , LineNumberTextEdit):
        class Highlighter(HighlightTextEdit.Highlighter):
            def __init__(self, document):
                super().__init__(document)
                
                state = QTextCharFormat()
                state.setFontItalic(True)
                state.setForeground(QColor(144, 0, 144))
                
                string = QTextCharFormat()
                string.setForeground(QColor(0, 170, 9))
                
                command = QTextCharFormat()
                command.setForeground(QColor(144, 0, 200))
                
                url = QTextCharFormat()
                url.setForeground(QColor(100, 80, 255))
                url.setFontUnderline(True)
                
                self.highlight_styles["state"] = state
                self.highlight_styles["string"] = string
                self.highlight_styles["command"] = command
                self.highlight_styles["url"] = url
                
                stringprefix = r"(?i:r|u|f|fr|rf|b|br|rb)?"
                sqstring = stringprefix + r"'[^'\\\n]*(\\.[^'\\\n]*)*'?"
                dqstring = stringprefix + r'"[^"\\\n]*(\\.[^"\\\n]*)*"?'
                sq3string = stringprefix + r"'''[^'\\]*((\\.|'(?!''))[^'\\]*)*(''')?"
                dq3string = stringprefix + r'"""[^"\\]*((\\.|"(?!""))[^"\\]*)*(""")?'
                string = "|".join([sqstring, dqstring, sq3string, dq3string])
                
                self.rules.extend([
                    (r"^\[.+\]:", 0, "state"),
                    (string, 0, "string"),
                    # (r"([^.]-.+\s|[^.]--.+\s|[^.]\"-.+\"|[^.]\'--.+\')", 0, "command"),
                    (r"http[s]?://(.+|\[.+\])(:[0-9]+)?(/(.+|#))?", 0, "url")
                ])
        
        Default_Highlighter = Highlighter
    
    class Executer:
        def __init__(self, extra_globals=None):
            if not extra_globals:
                extra_globals = {}
            
            self.__th = None
            
            def input(prompt=""):
                class Th(QThread):
                    def __init__(self, prompt=""):
                        super().__init__()
                        self.prompt = prompt
                        self.__flag = False
                        self.__in = ""
                        self.__stdin = sys.stdin
                    
                    def finish(self, _in):
                        self.__flag = True
                        self.__in = _in
                    
                    def run(self):
                        sys.stdin = _in = StringIO()
                        while self.__flag:
                            self.usleep(1000)
                        _in.write(self.__in)
                        __builtins__.input(self.prompt)
                        sys.stdin = self.__stdin
                
                self.__th = Th(prompt)
                self.__th.start()
            
            self.globals = {
                "input": input,
                "sys": sys,
                "player": player,
                "frame": frame
            }
            for i in extra_globals.items():
                self.globals[i[0]] = i[1]
            self.locals = {
                "input": input,
                "sys": sys,
            }
        
        def process_command(self, command):
            try:
                if self.__th:
                    self.__th.finish(command)
                    self.__th = None
                else:
                    d = eval(command, self.globals, self.locals)
                    print(d, file=sys.stdout)
            except:
                sys.stderr.write(traceback.format_exc())
    
    def __init__(self):
        super().__init__()
        self.resize(800, 600)
        self.setWindowIcon(QIcon(":/CommonMinecraftLauncherIcon.svg"))
        self.setWindowTitle(self.tr("LoggingWindow.Title"))
        self.setStyleSheet("background: transparent;")
        self.toolPanel = Panel(self)
        self.horizontalLayout = QHBoxLayout(self.toolPanel)
        self.stopOutputBtn = PushButton(self.toolPanel)
        self.stopOutputBtn.setText("")
        self.stopOutputBtn.pressed.connect(self.toggleOutput)
        self.horizontalLayout.addWidget(self.stopOutputBtn)
        self.triggerExceptionBtn = PushButton(self.toolPanel)
        self.triggerExceptionBtn.setText("")
        self.triggerExceptionBtn.pressed.connect(self.triggerException)
        self.horizontalLayout.addWidget(self.triggerExceptionBtn)
        spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.horizontalLayout.addItem(spacer)
        self.loggingtext = self.LoggingText(self)
        self.loggingtext.setReadOnly(True)
        # self.loggingtext.setLineWrapMode(self.LoggingText.LineWrapMode.NoWrap)
        self.loggingtext.setFont(fixedFont)
        self.bftext = output.getvalue()
        self.loggingtext.setText(output.getvalue())
        timer = QTimer(self)
        timer.timeout.connect(self.updateText)
        timer.start(100)
        self.inputtext = LineEdit(self)
        self.inputtext.returnPressed.connect(self.process_command)
        self.inputtext.setFont(fixedFont)
        self.inputtext.setToolTip(self.tr("LoggingWindow.inputtext.ToolTip"))
        self.canOutput = True
        app.registerRetranslateFunction(self.retranslateUI)
        self.retranslateUI()
        import nothingtoseeheremovealong, hashlib
        self.cmd = self.Executer(
            {"frame": frame, "player": player,
             hashlib.md5("SummonACreeperToYouHouse".encode()).hexdigest(): nothingtoseeheremovealong.creeper})
        self.history_command = []
        self.current_history = 0
    
    def retranslateUI(self):
        self.stopOutputBtn.setText(self.tr("LoggingWindow.stopOutputBtn.StopOut.Text") if self.canOutput else self.tr(
            "LoggingWindow.stopOutputBtn.StartOut.Text"))
        self.triggerExceptionBtn.setText(self.tr("LoggingWindow.triggerExceptionBtn.Text"))
    
    def updateText(self):
        if self.bftext != output.getvalue():
            Path("latest.log").write_text(output.getvalue(), encoding="utf-8")
        if self.canOutput:
            if self.bftext != output.getvalue() or self.loggingtext.toPlainText() != output.getvalue():
                self.loggingtext.setText("")
                self.loggingtext.textCursor().insertText(output.getvalue().split("")[-1])
                self.loggingtext.ensureCursorVisible()
                self.bftext = output.getvalue()
    
    def toggleOutput(self):
        self.canOutput = not self.canOutput
        self.stopOutputBtn.setText(self.tr("LoggingWindow.stopOutputBtn.StopOut.Text") if self.canOutput else self.tr(
            "LoggingWindow.stopOutputBtn.StartOut.Text"))
    
    def triggerException(self):
        def trigger1():
            trigger2()
        
        def trigger2():
            trigger3()
        
        def trigger3():
            trigger4()
        
        def trigger4():
            trigger5()
        
        def trigger5():
            trigger6()
        
        def trigger6():
            error
        
        try:
            trigger1()
        except NameError as n:
            try:
                raise ZeroDivisionError() from n
            except ZeroDivisionError as z:
                try:
                    raise SyntaxError()
                except SyntaxError as s:
                    try:
                        raise ArithmeticError() from s
                    except ArithmeticError as a:
                        try:
                            raise MemoryError()
                        except MemoryError as m:
                            try:
                                raise SystemError() from m
                            except SystemError as s:
                                try:
                                    raise ArithmeticError() from s
                                except ArithmeticError as a:
                                    try:
                                        raise MemoryError()
                                    except MemoryError as m:
                                        try:
                                            raise SystemError() from m
                                        except SystemError as s:
                                            try:
                                                raise ArithmeticError() from s
                                            except ArithmeticError as a:
                                                raise MemoryError()
    
    def process_command(self):
        if self.inputtext.text():
            self.history_command.append(self.inputtext.text())
            self.cmd.process_command(self.inputtext.text())
            self.inputtext.clear()
            self.current_history = 0
    
    def closeEvent(self, a0):
        super().closeEvent(a0)
        QApplication.closeAllWindows()
    
    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        if hasattr(self, "titleBar"):
            self.titleBar.setGeometry(QRect(0, 0, self.width(), self.titleBar.height()))
        try:
            self.toolPanel.setGeometry(QRect(5, 32, self.width() - 10, 55))
            self.loggingtext.setGeometry(self.rect().adjusted(0, 92, 0, -37))
            self.inputtext.setGeometry(5, self.height() - 32 - 5,
                                       self.width() - 10,
                                       32)
        except AttributeError:
            pass
    
    def keyPressEvent(self, a0):
        super().keyPressEvent(a0)
        if not self.history_command:
            return
        if a0.key() == 16777235:
            if self.history_command and self.current_history < len(self.history_command):
                self.current_history += 1
                self.inputtext.setText(self.history_command[-self.current_history])
        if a0.key() == 16777237:
            if self.history_command and self.current_history > 1:
                self.current_history -= 1
                self.inputtext.setText(self.history_command[-self.current_history])
            if self.current_history == 1:
                self.current_history = 0
                self.inputtext.setText("")
    
    def paintEvent(self, a0, **kwargs):
        background = QPixmap(self.size())
        p = QPainter(background)
        x = 0 if self.isMaximized() else -self.geometry().x()
        y = 0 if self.isMaximized() else -self.geometry().y()
        p.fillRect(
            QRect(x, y, QGuiApplication.primaryScreen().geometry().width(),
                  QGuiApplication.primaryScreen().geometry().height()),
            QGradient(QGradient.Preset.FreshOasis if getTheme() == Theme.Light else QGradient.Preset.NightSky))
        p.end()
        scene = QGraphicsScene()
        item = QGraphicsPixmapItem()
        item.setPixmap(background)
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(settings["Settings"]["LauncherSettings"]["Customise"]["BackgroundBlur"])
        item.setGraphicsEffect(blur)
        scene.addItem(item)
        img = QPixmap(background.size())
        img.fill(Qt.GlobalColor.transparent)
        ptr = QPainter(img)
        scene.render(ptr, QRectF(img.rect()), QRectF(img.rect()))
        ptr.end()
        painter = QPainter(self)
        rect = QRect(-20, -20, self.width() + 40, self.height() + 40)
        painter.drawPixmap(rect, img)


class GameLoggingWindow(window_class):
    def __init__(self, parent=None, popen_obj=None):
        super().__init__(parent)
        self.popen_obj = popen_obj
        
        self.resize(800, 600)
        
        self.textEdit = TextEdit(self)
        
        if popen_obj.stdout:
            self.beforeText = popen_obj.stdout.read()
        else:
            self.beforeText = ""
        
        t = QTimer(self)
        t.timeout.connect(self.updateLogs)
        t.start(1000)
    
    def updateLogs(self):
        if self.popen_obj.stdout:
            if self.popen_obj.stdout.read() != self.beforeText:
                self.textEdit.clear()
                self.textEdit.append(self.popen_obj.stdout.read().decode("utf-8"))
                self.beforeText = self.popen_obj.stdout.read()
    
    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        if hasattr(self, "textEdit"):
            self.textEdit.setGeometry(QRect(5, 37, self.width() - 10, self.height() - 42))
    
    def paintEvent(self, a0, **kwargs):
        background = QPixmap(self.size())
        p = QPainter(background)
        x = 0 if self.isMaximized() else -self.geometry().x()
        y = 0 if self.isMaximized() else -self.geometry().y()
        p.fillRect(
            QRect(x, y, QGuiApplication.primaryScreen().geometry().width(),
                  QGuiApplication.primaryScreen().geometry().height()),
            QGradient(QGradient.Preset.FreshOasis if getTheme() == Theme.Light else QGradient.Preset.NightSky))
        p.end()
        scene = QGraphicsScene()
        item = QGraphicsPixmapItem()
        item.setPixmap(background)
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(settings["Settings"]["LauncherSettings"]["Customise"]["BackgroundBlur"])
        item.setGraphicsEffect(blur)
        scene.addItem(item)
        img = QPixmap(background.size())
        img.fill(Qt.GlobalColor.transparent)
        ptr = QPainter(img)
        scene.render(ptr, QRectF(img.rect()), QRectF(img.rect()))
        ptr.end()
        painter = QPainter(self)
        rect = QRect(-20, -20, self.width() + 40, self.height() + 40)
        painter.drawPixmap(rect, img)


class SplashScreen(QSplashScreen):
    def __init__(self):
        super().__init__()
        self.setFixedSize(
            QSize(
                max(
                    96,
                    QFontMetrics(app.font()).boundingRect(self.rect(), Qt.AlignmentFlag.AlignCenter,
                                                          self.tr("SplashScreen.LoadingText")).width()
                ),
                114)
        )
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        geometry = QGuiApplication.primaryScreen().geometry()
        point = QPoint(geometry.width() // 2 - self.width() // 2, geometry.height() // 2 - self.height() // 2)
        self.move(point)
        
        self.show()
        self.update()
    
    def paintEvent(self, a0, **kwargs):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        QSvgRenderer(":/CommonMinecraftLauncherIcon.svg").render(painter, QRectF(self.width() // 2 - 48, 0, 96, 96))
        painter.setPen(getForegroundColour())
        painter.setFont(app.font())
        painter.drawText(QRect(0, 96, self.width(), 18), Qt.AlignmentFlag.AlignCenter,
                         self.tr("SplashScreen.LoadingText"))
    
    def closeEvent(self, a0, **kwargs):
        super().closeEvent(a0)
        frame.show()


def login_user(name_or_token=b"", is_refresh_login=False):
    try:
        conn = sqlite3.connect("user_data.DAT")
        cursor = conn.cursor()
        try:
            cursor.execute("create table users (refresh_token TEXT, player_playerName TEXT)")
        except sqlite3.OperationalError:
            pass
        if is_refresh_login:
            cursor.execute(
                f'select refresh_token from users where player_playerName = "{name_or_token.decode()}"')
            token = base64.b64decode(cursor.fetchone()[0])
        else:
            token = name_or_token
        token = token.decode()
        status, player, refresh_token = MicrosoftPlayerLogin(token, is_refresh_login)
        if not is_refresh_login:
            byte_name = b"".join(
                [str(player.player_playerName[i] if i < len(player.player_playerName) else random.randrange(0,
                                                                                                            10)).encode(
                    "utf-8")
                    for
                    i in range(16)])
            key = str(UUID(bytes=byte_name))
        else:
            byte_name = b"1234567890123456"
            key = name_or_token.decode()
        if refresh_token:
            if not is_refresh_login:
                cursor.execute(
                    f'insert into users (refresh_token, player_playerName) values ("{base64.b64encode(bytes(refresh_token, encoding="utf-8")).decode()}", "{key}")')
            else:
                cursor.execute(
                    f'update users set refresh_token = "{base64.b64encode(bytes(refresh_token, encoding="utf-8")).decode()}" where player_playerName = "{key}"')
        cursor.close()
        conn.commit()
        conn.close()
        with open("current_user.DAT", "wb") as file:
            file.write(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" + r"\x0".join(
                [str(i) for i in list(key)]).encode() + b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
        return player
    except:
        traceback.print_exc()
        return MicrosoftPlayer(None, None, None, False)


class LoginThread(QThread):
    loginFinished = pyqtSignal(MicrosoftPlayer)
    
    def run(self):
        try:
            data = Path("current_user.DAT").read_bytes().replace(
                b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00", b"").replace(br"\x0", b"")
            data = login_user(data, True)
        except FileNotFoundError:
            Path("current_user.DAT").write_text("", encoding="utf-8")
        finally:
            try:
                self.loginFinished.emit(data)
            except NameError:
                self.loginFinished.emit(MicrosoftPlayer(None, None, None, False))


def update_user(data):
    global player
    player = data
    frame.UserPage.user_datas[frame.UserPage.current_user] = player


Path("error.log").write_text("", encoding="utf-8")
Path("latest.log").write_text("", encoding="utf-8")


class Application(QApplication):
    def __init__(self, *args):
        super().__init__(*args)
        self.setProperty("retranslateFunctions", [])
    
    def registerRetranslateFunction(self, function):
        retranslateFunctions = self.property("retranslateFunctions")
        if function not in retranslateFunctions:
            retranslateFunctions.append(function)
        self.setProperty("retranslateFunctions", retranslateFunctions)
    
    def removeRetranslateFunction(self, function):
        retranslateFunctions = self.property("retranslateFunctions")
        if function in retranslateFunctions:
            retranslateFunctions.remove(function)
        self.setProperty("retranslateFunctions", retranslateFunctions)
    
    def retranslate(self):
        for function in self.property("retranslateFunctions"):
            function()


def saveSettings():
    Path("settings.json").write_text(json.dumps(settings, indent=2))


def exception(*args, **kwargs):
    saveSettings()
    # emitter = ExceptionEmitter(lambda: frame.errorDialogue("".join(traceback.format_exception(*args, **kwargs))))
    frame.errorDialogue("".join(traceback.format_exception(*args, **kwargs)))


def __excepthook__(*args, **kwargs):
    Path("error.log").open("a", encoding="utf-8").write("".join(traceback.format_exception(*args, **kwargs)))
    traceback.print_exception(*args, **kwargs)
    exception(*args, **kwargs)


sys.excepthook = __excepthook__

logging.basicConfig(
    level=logging.NOTSET,
    format="[%(asctime)s][%(levelname)s]:%(message)s",
    datefmt="%Y/%m/%d  %H:%M:%S %p"
)
if Path("settings.json").exists() and Path("settings.json").read_text("utf-8"):
    settings = json.loads(Path("settings.json").read_text("utf-8"))
else:
    Path("settings.json").write_text("", encoding="utf-8")
    settings = {
        "Settings": {
            "JavaSettings": {
                "Java": {
                    "Path": {
                        "is_auto": True,
                        "value": None
                    },
                    "LaunchMode": "client"
                },
                "JVM": {
                    "Arg": {
                        "is_override": False,
                        "value": None
                    }
                }
            },
            "GameSettings": {
                "ExtraGameCommand": None,
            },
            "LauncherSettings": {
                "Customise": {
                    "CurrentThemePreset": "PresetBlue",
                    "CurrentTheme": "Light",
                    "BackgroundBlur": 0,
                    "Animations": {
                        "Enabled": True,
                        "EnabledItems": [
                            1
                        ]
                    },
                    "DateTimeFormat": "%Y-%m-%d %H:%M:%S"
                },
                "ModSearching": {
                    "OnePageModNum": 10
                },
                "CurrentLanguage": locale._getdefaultlocale()[0].lower().replace("_", "-"),
                "CurrentMinecraftDirectory": "."
            }
        }
    }
    saveSettings()
minecraft_path = Path(settings["Settings"]["LauncherSettings"]["CurrentMinecraftDirectory"]).absolute()
if not minecraft_path.exists():
    minecraft_path = Path(".").absolute()
    settings["Settings"]["LauncherSettings"]["CurrentMinecraftDirectory"] = str(minecraft_path)
# QApplication.setDesktopSettingsAware(False)
app = Application(sys.argv)
app.setApplicationName("Common Minecraft Launcher")
app.setApplicationVersion(CMCL_version[0])
app.setFont(QFont("HarmonyOS Sans SC"))
fixedFont = QFont(["Jetbrains Mono", "Consolas", "Ubuntu", "Monospace", "HarmonyOS Sans SC"], 13)
#                                  --- Monospace ---                      --- Chinese ---

# app.setEffectEnabled(Qt.UIEffect.UI_AnimateMenu)
# app.setEffectEnabled(Qt.UIEffect.UI_FadeMenu)

player = create_online_player(None, None, None, False)

# player = LittleSkinPlayer("chengwm", "random", "random",
#                           "MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEArGcNOOFIqLJSqoE3u0hj\ntOEnOcET3wj9Drss1BE6sBqgPo0bMulOULhqjkc/uH/wyosYnzw3xaazJt87jTHh\nJ8BPMxCeQMoyEdRoS3Jnj1G0Kezj4A2b61PJJM1DpvDAcqQBYsrSdpBJ+52MjoGS\nvJoeQO5XUlJVQm21/HmJnqsPhzcA6HgY71RHYE5xnhpWJiPxLKUPtmt6CNYUQQoS\no2v36XWgMmLBZhAbNOPxYX+1ioxKamjhLO29UhwtgY9U6PWEO7/SBfXzyRPTzhPV\n2nHq7KJqd8IIrltslv6i/4FEM81ivS/mm+PN3hYlIYK6z6Ymii1nrQAplsJ67OGq\nYHtWKOvpfTzOollugsRihkAG4OB6hM0Pr45jjC3TIc7eO7kOgIcGUGUQGuuugDEz\nJ1N9FFWnN/H6P9ukFeg5SmGC5+wmUPZZCtNBLr8o8sI5H7QhK7NgwCaGFoYuiAGL\ngz3k/3YwJ40BbwQayQ2gIqenz+XOFIAlajv+/nyfcDvZH9vGNKP9lVcHXUT5YRnS\nZSHo5lwvVrYUrqEAbh/zDz8QMEyiujWvUkPhZs9fh6fimUGxtm8mFIPCtPJVXjeY\nwD3Lvt3aIB1JHdUTJR3eEc4eIaTKMwMPyJRzVn5zKsitaZz3nn/cOA/wZC9oqyEU\nmc9h6ZMRTRUEE4TtaJyg9lMCAwEAAQ==",
#                           "https://littleskin.cn/api/yggdrasil", True)

# "%appdata%\Python\Python311\Scripts\pyside6-rcc.exe" resources.qrc -o resources.py

# "%appdata%\Python\Python311\Scripts\pyside6-lupdate.exe" main.py -ts CMCL_zh-cn.ts
# "%appdata%\Python\Python311\Scripts\pyside6-lupdate.exe" main.py -ts CMCL_zh-hk.ts
# "%appdata%\Python\Python311\Scripts\pyside6-lupdate.exe" main.py -ts CMCL_zh-tw.ts

fallback_translator = QTranslator()
fallback_translator.load(f":/CMCL_zh-cn.qm")
app.installTranslator(fallback_translator)
current_language = settings["Settings"]["LauncherSettings"]["CurrentLanguage"]
app.translator = QTranslator()
app.translator.load(f":/CMCL_{current_language}.qm")
app.installTranslator(app.translator)
app.qt_translator = QTranslator()
app.qt_translator.load(QLocale(locale.normalize(current_language.replace("-", "_")).split(".")[0]), "qtbase", "_",
                       QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath))
app.installTranslator(app.qt_translator)

match settings["Settings"]["LauncherSettings"]["Customise"]["CurrentTheme"]:
    case "Light":
        setTheme(Theme.Light)
    case "Dark":
        setTheme(Theme.Dark)

frame = MainWindow()
if DEBUG:
    debug = LoggingWindow()
    debug.show()
thread = LoginThread()
thread.loginFinished.connect(update_user)
thread.start()
splash = SplashScreen()
QTimer.singleShot(2999, lambda: (frame.show(), frame.resize(800, 600), frame.setCentre()))
QTimer.singleShot(3000, splash.close)
QTimer.singleShot(3001, frame.activateWindow)
# April FOOL Code
if datetime.datetime.now().month == 4 and datetime.datetime.now().day == 1:
    def sttttttttttttttttttttttttttttttop():
        if frame.dx and frame.dy and random.random():
            frame.dy = frame.dx = 0
            frame.setWindowTitle(":D" * 15)
        stopbutton.close()
    
    
    stopbutton = QPushButton("🏳️")
    stopbutton.setWindowFlags(Qt.WindowType.FramelessWindowHint)
    stopbutton.pressed.connect(sttttttttttttttttttttttttttttttop)
    stopbutton.show()
# End
app.exec()
saveSettings()
