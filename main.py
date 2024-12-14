# -*- coding: utf-8 -*-
"""
project start time:1693310592
|-time.struct_time(tm_year=2023, tm_mon=8, tm_mday=29, tm_hour=20, tm_min=3, tm_sec=12, tm_wday=1, tm_yday=241, tm_isdst=0)
|-2023/08/29 20:03:12, Tuesday, August, Zone:中国标准时间(UTC+8), 一年的第241天
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
import ctypes
import webbrowser as webb
from pathlib import Path
from io import StringIO
from uuid import UUID
import logging
import time
import tempfile

try:
    from dateutil import tz
except ImportError:
    import pytz as tz

from CMCLWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from qframelesswindow import StandardTitleBar

from CMCLCore.Launch import LaunchMinecraft
from CMCLCore.Login import MicrosoftPlayerLogin
from CMCLCore.Player import create_online_player, create_offline_player, MicrosoftPlayer, LittleSkinPlayer
from CMCLCore.GetVersion import GetVersionByScanDirectory, GetVersionByMojangApi
from CMCLCore.DownloadVersion import DownloadMinecraft
from CMCLCore.GetOperationSystem import GetOperationSystemName

import requests

from CMCLModding.GetMods import GetModsOnModrinth

import resources

DEBUG = True

output = StringIO()

if DEBUG:
    sys.stdout = sys.stderr = output
    
    formatter = logging.Formatter("[%(asctime)s][%(levelname)s]:%(message)s")
    formatter.datefmt = "%Y/%m/%d][%H:%M:%S %p"
    streamHandler = logging.StreamHandler(output)
    streamHandler.setFormatter(formatter)
    logging.root.addHandler(streamHandler)
    
    lock = QMutex()
    
    
    def log(type, context, msg):
        lock.lock()
        print(time.strftime(f"[%Y/%m/%d][%H:%M:%S %p]"), end="")
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
        lock.unlock()
    
    
    qInstallMessageHandler(log)

CMCL_version = ("AlphaDev-24002", "Alpha Development-24002")
minecraft_path = Path(r"D:\Program Files\minecraft")
language = "zh-cn"

theme_colour_defines = {
    "CMCL_Blue": {
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
    "CMCL_Pink": {
        Theme.Light: {
            ColourRole.Background: {
                False: (253, 253, 253),
                True: (250, 176, 250)
            },
            ColourRole.Border: {
                False: (215, 220, 229),
                True: (250, 135, 250)
            }
        },
        Theme.Dark: {
            ColourRole.Background: {
                False: (67, 67, 67),
                True: (252, 142, 252),
            },
            ColourRole.Border: {
                False: (134, 143, 150),
                True: (252, 79, 252)
            }
        }
    },
    "CMCL_Red": {
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

window_class = MainWindow


class AcrylicBackground(QWidget):
    def __init__(self, parent, tintColour, luminosityColour, blurRadius, noiseOpacity):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.tintColour = tintColour
        self.luminosityColour = luminosityColour
        self.blurRadius = blurRadius
        self.noiseOpacity = noiseOpacity
        self.img = QPixmap()
    
    def paintEvent(self, a0):
        brush = self.createTexture()
        scene = QGraphicsScene()
        item = QGraphicsPixmapItem()
        item.setPixmap(self.img)
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(30)
        item.setGraphicsEffect(blur)
        scene.addItem(item)
        img = QPixmap(self.img.size())
        img.fill(Qt.GlobalColor.transparent)
        ptr = QPainter(img)
        scene.render(ptr, QRectF(img.rect()), QRectF(img.rect()))
        ptr.end()
        painter = QPainter(self)
        painter.drawImage(img)
        painter.fillRect(img.rect(), brush)
    
    def createTexture(self):
        acrylicTexture = QImage(64, 64, QImage.Format.Format_ARGB32_Premultiplied)
        acrylicTexture.fill(self.luminosityColour)
        painter = QPainter(acrylicTexture)
        painter.setOpacity(1.0)
        painter.fillRect(acrylicTexture.rect(), self.tintColour)
        painter.setOpacity(self.noiseOpacity)
        painter.drawImage(acrylicTexture.rect(), QImage("acrylic_noise.png"))
        
        brush = QBrush(acrylicTexture)
        return brush


class ContentPanel(QStackedWidget, Panel):
    def event(self, a0):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        for i in self.children():
            if hasattr(i, "setGeometry"):
                i.setGeometry(self.rect().adjusted(5, 5, -5, -5))
            if hasattr(i, "setAttribute"):
                i.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        return super().event(a0)


class LoadingAnimation(QFrame):
    class HideAnimation(QThread):
        def run(self):
            import time
            time.sleep(1)
            self.parent().hide()
    
    class TransparencyAnimation(QVariantAnimation):
        def __init__(self, parent=None, variant="in"):
            super().__init__(parent)
            self.setStartValue(0 if variant == "in" else 255)
            self.setEndValue(255 if variant == "in" else 0)
            self.setDuration(1000)
            self.valueChanged.connect(self.update_opacity)
        
        def update_opacity(self, value):
            colour = value
            self.parent().setStyleSheet(
                f"background: rgba({str(getBackgroundColour(is_tuple=True)).strip('()')}, {colour / 255})")
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setStyleSheet("background: rgb(249, 249, 249);")
        self.__svgWidget = QSvgWidget(self)
        self.__svgWidget.load(":/CMCL_loading.svg")
        self.__svgWidget.setFixedSize(96, 96)
        self.__svgWidget.setStyleSheet("background: transparent;")
        dsg = QGraphicsDropShadowEffect(self.__svgWidget)
        dsg.setBlurRadius(30)
        dsg.setOffset(0, 4)
        dsg.setColor(QColor(0, 0, 0, 100))
        self.__svgWidget.setGraphicsEffect(dsg)
        self.__failedSvg = QSvgWidget(self.__svgWidget)
        self.__failedSvg.load(":/CMCL_loading_failed.svg")
        self.__failedSvg.setFixedSize(96, 96)
        self.__failedSvg.setStyleSheet("background: transparent;")
        self.__failedSvg.hide()
        self.__statusLabel = Label(self)
        self.__statusLabel.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.__loadingTimer = QTimer(self)
        self.__loadingTimer.timeout.connect(self.__updateText)
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
            self.__svgWidget.setGeometry(QRect(int(self.width() / 2 - (self.__svgWidget.width() / 2)),
                                               int(self.height() / 2 - (self.__svgWidget.height() / 2)),
                                               self.__svgWidget.width(),
                                               self.__svgWidget.height()))
            self.__failedSvg.setGeometry(self.__svgWidget.rect())
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
        self.raise_()
        return super().event(e)
    
    def paintEvent(self, a0):
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        if not self.__failedSvg.isVisible():
            self.setStyleSheet(
                f"background: rgb({str(getBackgroundColour(is_tuple=True)).replace('(', '').replace(')', '')});")
        else:
            self.setStyleSheet(f"background: rgb({'255, 200, 200' if getTheme() == Theme.Light else '100, 50, 50'});")
        return super().paintEvent(a0)
    
    def __updateText(self):
        self.__counter += 1
        self.__statusLabel.setText(self.tr("LoadingAnimation.statusLabel.Text") + "." * (self.__counter % 4))
    
    def start(self, ani=True):
        self.setStyleSheet(
            f"background: rgb({str(getBackgroundColour(is_tuple=True)).replace('(', '').replace(')', '')});")
        self.__statusLabel.setText(self.tr("LoadingAnimation.statusLabel.Text"))
        self.__svgWidget.load(":/CMCL_loading.svg")
        self.__failedSvg.load(":/CMCL_loading_failed.svg")
        self.__failedSvg.hide()
        if ani:
            self.setStyleSheet("background: transparent")
            self.TransparencyAnimation(self, "in").start()
        self.__counter = 0
        self.__loadingTimer.start(1000)
        self.show()
    
    def finish(self, ani=True, failed=False):
        try:
            self.__loadingTimer.stop()
            if not failed:
                if ani:
                    self.TransparencyAnimation(self, "out").start()
                    self.HideAnimation(self).start()
                else:
                    self.hide()
                self.__statusLabel.setText(self.tr("LoadingAnimation.statusLabel.SuccessText"))
                self.__failedSvg.hide()
            else:
                self.setStyleSheet(
                    f"background: rgb({'255, 200, 200' if getTheme() == Theme.Light else '100, 50, 50'});")
                self.__statusLabel.setText(self.tr("LoadingAnimation.statusLabel.FailedText"))
                self.__failedSvg.show()
        except RuntimeError:
            pass
    
    def hideEvent(self, *args, **kwargs):
        try:
            self.__loadingTimer.stop()
            self.deleteLater()
        except RuntimeError:
            pass
    
    def destroy(self, *args, **kwargs):
        try:
            self.__loadingTimer.stop()
        except RuntimeError:
            pass
        super().destroy(*args, **kwargs)


class LoginDialogue(RoundedDialogue):
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
        w = LoginWindow()
        w.exec()
    
    def paintEvent(self, a0, **kwargs):
        painter = QPainter(self)
        painter.fillRect(
            QRect(-self.geometry().x(), -self.geometry().y(), QGuiApplication.primaryScreen().geometry().width(),
                  QGuiApplication.primaryScreen().geometry().height()),
            QGradient(QGradient.Preset.DeepBlue if getTheme() == Theme.Light else QGradient.Preset.PerfectBlue))


class LoginWindow(RoundedDialogue):
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
    
    class QWebEngineView(QWebEngineView):
        def contextMenuEvent(self, a0):
            menu = RoundedMenu(self)
            reload = QAction(menu)
            reload.setText(self.tr("LoginWindow.WebEngineView.Reload.Text"))
            reload.triggered.connect(self.reload)
            menu.addAction(reload)
            menu.popup(self.mapToGlobal(a0.pos()))
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("LoginWindow.Title"))
        self.resize(800, 600)
        self.view = self.QWebEngineView(self)
        self.view.show()
        self.view.load(QUrl(
            "https://login.live.com/oauth20_authorize.srf?client_id=00000000402b5328&response_type=code&scope=service%3A%3Auser.auth.xboxlive.com%3A%3AMBI_SSL&redirect_uri=https%3A%2F%2Flogin.live.com%2Foauth20_desktop.srf"))
        self.view.urlChanged.connect(self.assert_url)
        self.view.loadStarted.connect(self.loadStarted)
        self.view.loadFinished.connect(self.loadFinished)
        self.view.page().profile().setHttpAcceptLanguage(language)
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
        self.view.setGeometry(self.rect())
    
    def showEvent(self, a0):
        super().showEvent(a0)
        self.isFirstShow = False
    
    def paintEvent(self, a0, **kwargs):
        painter = QPainter(self)
        painter.fillRect(
            QRect(-self.geometry().x(), -self.geometry().y(), QGuiApplication.primaryScreen().geometry().width(),
                  QGuiApplication.primaryScreen().geometry().height()),
            QGradient(QGradient.Preset.DeepBlue if getTheme() == Theme.Light else QGradient.Preset.PerfectBlue))


# class MultiPageBase(QFrame):
#     def __init__(self, parent):
#         super().__init__(parent)
#         self.verticalLayout = QVBoxLayout(self)
#         self.verticalLayout.setObjectName(u"verticalLayout")
#         self.frame = Panel(self)
#         self.horizontalLayout = QHBoxLayout(self.frame)
#         self.horizontalLayout.setObjectName(u"horizontalLayout")
#         self.pages = {}
#
#         self.pushButton = PushButton(self.frame)
#         self.pushButton.setObjectName(u"pushButton")
#         self.pushButton.setCheckable(True)
#         self.pushButton.setChecked(True)
#         self.pushButton.setAutoExclusive(True)
#         self.pushButton.pressed.connect(lambda: self.update_page(self.pushButton))
#
#         self.horizontalLayout.addWidget(self.pushButton)
#
#         self.pushButton_2 = PushButton(self.frame)
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
#         self.verticalLayout.addWidget(self.frame)
#
#         self.stackedWidget = QStackedWidget(self)
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
#         self.verticalLayout.addWidget(self.stackedWidget)
#
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
    class VersionSettingsPage(QFrame):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.verticalLayout = QVBoxLayout(self)
            
            self.listWidget = ListWidget(self)
            
            for version in GetVersionByScanDirectory(minecraft_path):
                self.listWidget.addItem(version)
            
            self.verticalLayout.addWidget(self.listWidget)
    
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
                CMCL_version[0], "CMCL", None, None, None,
                settings["Settings"]["GameSettings"]["ExtraGameCommand"], None, None,
                self.player
            )
            self.launched.emit(result)
    
    def __init__(self, parent):
        super().__init__(parent)
        self.version = None
        
        self.verticalLayout = QVBoxLayout(self)
        self.scrollArea = ScrollArea(self)
        self.verticalLayout.addWidget(self.scrollArea)
        self.scrollAreaContentWidget = QWidget()
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaContentWidget)
        # testtextof2233(self.scrollAreaContentWidget, self.verticalLayout_2, self)
        # print(self.verticalLayout_2.addWidget(self.label2))
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
        self.launch_btn.pressed.connect(self.launch)
        self.horizontalLayout.addWidget(self.launch_btn)
        self.select_version_btn = ToolButton(self.bottomPanel)
        self.select_version_btn.setPopupMode(ToolButton.ToolButtonPopupMode.InstantPopup)
        self.update_menu()
        self.horizontalLayout.addWidget(self.select_version_btn)
        self.change_dir_btn = PushButton(self.bottomPanel)
        self.change_dir_btn.pressed.connect(self.setMinecraftDir)
        self.horizontalLayout.addWidget(self.change_dir_btn)
        self.settings_btn = PushButton(self.bottomPanel)
        self.settings_btn.pressed.connect(self.show_version_settings_page)
        self.horizontalLayout.addWidget(self.settings_btn)
        spacer2 = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.horizontalLayout.addItem(spacer2)
        self.retranslateUI()
        self.bottomPanelIsShow = True
        self.versionSettings = None
    
    def retranslateUI(self):
        self.launch_btn.setText(self.tr("MainPage.launch_btn.Text"))
        self.select_version_btn.setText(self.version or self.tr("MainPage.select_version_btn.DefaultText"))
        self.change_dir_btn.setText(self.tr("MainPage.change_dir_btn.Text"))
        self.settings_btn.setText("版本设置")  # self.tr("MainPage.settings_btn.Text")
    
    def select_version(self, version):
        self.version = version
        self.select_version_btn.setText(self.version or self.tr("MainPage.select_version_btn.DefaultText"))
    
    def launch(self):
        if self.version:
            self.launch_btn.setEnabled(False)
            launch_thread = self.LaunchThread(minecraft_path, self.version, player, self)
            launch_thread.launched.connect(lambda x: (self.launch_btn.setEnabled(True), self.launched(x)))
            launch_thread.start()
    
    def launched(self, result):
        print(result)
        if result[0] == "Successfully":
            tip = PopupTip(frame)
            label = Label(tip)
            label.setText(self.tr("MainPage.VersionLaunchedTip.Label.Text"))
            label.adjustSize()
            tip.setCentralWidget(label)
            tip.setGeometry(QRect(0, 0, 300, 64))
            tip.tip(PopupTip.PopupPosition.RIGHT, 3000)
            print(tip.geometry())
    
    def setMinecraftDir(self):
        global minecraft_path
        path = QFileDialog(self).getExistingDirectory(self, self.tr("MainPage.SelectDir.Title"), str(minecraft_path))
        if path:
            minecraft_path = Path(path)
            self.update_menu()
    
    def update_menu(self):
        menu = RoundedMenu()
        versions = GetVersionByScanDirectory(minecraft_path=minecraft_path)
        if isinstance(versions, list) and len(versions) >= 1:
            for version in versions:
                action = QAction(menu)
                action.setText(version)
                action.triggered.connect(lambda _, v=version: self.select_version(v))
                menu.addAction(action)
            self.select_version(versions[0])
        else:
            menu.addAction(self.tr("MainPage.NoVersionYet.Text"))
        self.select_version_btn.setMenu(menu)
    
    def show_version_settings_page(self):
        self.versionSettings = self.VersionSettingsPage(self)
    
    def resizeEvent(self, *args, **kwargs):
        super().resizeEvent(*args, **kwargs)
        self.bottomPanel.setGeometry(
            QRect(5, (self.height() - 80 if self.bottomPanelIsShow else self.height() + 62), self.width() - 10, 62))
        if self.bottomPanelIsShow:
            if self.verticalLayout_2.indexOf(self.bottom_space) == -1:
                self.verticalLayout_2.addItem(self.bottom_space)
        else:
            if self.verticalLayout_2.indexOf(self.bottom_space) != -1:
                self.verticalLayout_2.removeItem(self.bottom_space)
        if self.versionSettings:
            self.versionSettings.resize(self.width(), self.height())
            self.versionSettings.raise_()


class DownloadPage(QFrame):
    class DownloadVanilla(QFrame):
        class DownloadOptions(QFrame):
            frameClosed = pyqtSignal()
            
            class DownloadVersionThread(QThread):
                def __init__(self, parent, version=None, path="."):
                    super().__init__(parent)
                    self.__version = version
                    self.__path = Path(path)
                
                def run(self):
                    if self.__version:
                        DownloadMinecraft(self.__path, self.__version)
            
            def __init__(self, parent, version=None):
                super().__init__(parent)
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
                
                self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.pushButton)
                
                self.verticalLayout_3.addLayout(self.formLayout)
                
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
                painter = QPainter(self)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                painter.setBrush(getBackgroundColour())
                painter.drawRect(self.rect())
        
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
                [self.tr("DownloadPage.DownloadVanilla.tableView.horizontalHeaderLabels.1"),
                 self.tr("DownloadPage.DownloadVanilla.tableView.horizontalHeaderLabels.2"),
                 self.tr("DownloadPage.DownloadVanilla.tableView.horizontalHeaderLabels.3")])
            self.tableView.setModel(self.versionModel)
            self.versions = {}
            sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.tableView.sizePolicy().hasHeightForWidth())
            self.tableView.setSizePolicy(sizePolicy)
            
            self.verticalLayout.addWidget(self.tableView)
            
            self.frame = Panel(self)
            self.frame.setObjectName(u"frame")
            sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
            sizePolicy1.setHorizontalStretch(0)
            sizePolicy1.setVerticalStretch(0)
            sizePolicy1.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
            self.frame.setSizePolicy(sizePolicy1)
            self.horizontalLayout = QHBoxLayout(self.frame)
            self.horizontalLayout.setObjectName(u"horizontalLayout")
            self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
            self.formLayout = QFormLayout()
            self.formLayout.setObjectName(u"formLayout")
            self.label = Label(self.frame)
            self.label.setObjectName(u"label")
            
            self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)
            
            self.comboBox = ComboBox(self.frame)
            self.comboBox.setObjectName(u"comboBox")
            self.comboBox.addItem(self.tr("DownloadPage.DownloadVanilla.ComboBox.Item1.Text"))
            # self.comboBox.setEditable(True)
            
            self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.comboBox)
            
            self.horizontalLayout.addLayout(self.formLayout)
            
            self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
            
            self.horizontalLayout.addItem(self.horizontalSpacer)
            
            self.verticalLayout.addWidget(self.frame)
            
            self.retranslateUi()
            
            self.loadingAnimation = None
            self.getVersionThread = None
            self.downloadOptions = None
            
            # QMetaObject.connectSlotsByName(self)
            # setupUi
        
        def retranslateUi(self):
            self.lineEdit.setPlaceholderText(self.tr("DownloadPage.DownloadVanilla.lineEdit.PlaceholderText"))
            self.lineEdit.setToolTip(self.tr("DownloadPage.DownloadVanilla.lineEdit.ToolTip"))
            self.label.setText(self.tr("DownloadPage.DownloadVanilla.label.Text"))
            self.versionModel.setHorizontalHeaderLabels(
                [self.tr("DownloadPage.DownloadVanilla.tableView.horizontalHeaderLabels.1"),
                 self.tr("DownloadPage.DownloadVanilla.tableView.horizontalHeaderLabels.2"),
                 self.tr("DownloadPage.DownloadVanilla.tableView.horizontalHeaderLabels.3")])
        
        # retranslateUi
        
        def event(self, e):
            if hasattr(self, "downloadOptions") and self.downloadOptions:
                self.downloadOptions.setGeometry(self.rect())
                self.downloadOptions.raise_()
            return super().event(e)
        
        def showEvent(self, *args, **kwargs):
            super().showEvent(*args, **kwargs)
            if self.versions:
                pass
            else:
                self.getVersionThread = self.GetVersionThread(self)
                self.getVersionThread.gotVersion.connect(self.displayVersion)
                self.getVersionThread.start()
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
                    release_time = localised_release_datetime.strftime("%Y-%m-%d %H:%M:%S")
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
                    [self.tr("DownloadPage.DownloadVanilla.tableView.horizontalHeaderLabels.1"),
                     self.tr("DownloadPage.DownloadVanilla.tableView.horizontalHeaderLabels.2"),
                     self.tr("DownloadPage.DownloadVanilla.tableView.horizontalHeaderLabels.3")])
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
                    release_time = localised_release_datetime.strftime("%Y-%m-%d %H:%M:%S")
                    for e2, i2 in enumerate([version, version_type, release_time]):
                        self.versionModel.setItem(i, e2, QStandardItem(i2))
                    i += 1
                elif version_d == "latest" and (not latest_release or not latest_snapshot):
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
                            continue
                    release_datetime = value["ReleaseDatetime"]
                    localised_release_datetime = release_datetime.replace(tzinfo=datetime.UTC).astimezone(tz.tzlocal())
                    release_time = localised_release_datetime.strftime("%Y-%m-%d %H:%M:%S")
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
                            release_time = localised_release_datetime.strftime("%Y-%m-%d %H:%M:%S")
                            for e2, i2 in enumerate([version, version_type, release_time]):
                                self.versionModel.setItem(i, e2, QStandardItem(i2))
                            i += 1
                    except re.error:
                        pass
            self.versionModel.setHorizontalHeaderLabels(
                [self.tr("DownloadPage.DownloadVanilla.tableView.horizontalHeaderLabels.1"),
                 self.tr("DownloadPage.DownloadVanilla.tableView.horizontalHeaderLabels.2"),
                 self.tr("DownloadPage.DownloadVanilla.tableView.horizontalHeaderLabels.3")])
            self.tableView.setModel(self.versionModel)
            self.tableView.setSelectionMode(QTableView.SelectionMode.SingleSelection)
            self.tableView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            self.tableView.horizontalHeader().setVisible(True)
            self.tableView.verticalHeader().setVisible(False)
        
        def downloadOptionsOpen(self, value):
            data = self.tableView.model().item(value.row(), 0).text()
            print(data)
            self.downloadOptions = self.DownloadOptions(self, data)
            self.downloadOptions.frameClosed.connect(self.downloadOptionsClose)
            self.downloadOptions.show()
        
        def downloadOptionsClose(self):
            self.downloadOptions = None
    
    class DownloadMods(QFrame):
        class ModInfoPage(QFrame):
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
            
            def __init__(self, parent=None, mod_name=None, mod_icon=None, mod_description=None,
                         mod_supported_version=None):
                super().__init__(parent)
                self.mod_name = mod_name
                self.mod_icon = mod_icon
                self.mod_description = mod_description
                self.mod_supported_version = mod_supported_version
                
                self.icon_temp = None
                thread = self.GetIconThread(self, self.mod_icon)
                thread.requested.connect(self.updateIcon)
                thread.start()
                
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
                
                self.modInfo = QFrame(self.toolBox)
                
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
                
                self.verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
                
                self.verticalLayout_2.addItem(self.verticalSpacer)
                
                self.toolBox.addItem(self.modInfo, self.tr("DownloadPage.DownloadMods.ModInfoPage.Page1.Title"))
                
                self.verticalLayout.addWidget(self.toolBox)
                
                self.retranslateUI()
            
            def retranslateUI(self):
                self.modName.setText(self.mod_name)
                self.modDescription.setText(self.mod_description)
                self.toolBox.setItemText(self.toolBox.indexOf(self.modInfo),
                                         self.tr("DownloadPage.DownloadMods.ModInfoPage.Page1.Title"))
            
            def updateIcon(self, icon):
                try:
                    self.icon_temp = tempfile.NamedTemporaryFile(mode="wb+", suffix=".png")
                    self.icon_temp.write(requests.get(self.mod_icon).content)
                    self.icon_temp.flush()
                    self.icon_temp.seek(0)
                except:
                    self.icon_temp = None
                self.modIcon.setIcon(QIcon(self.icon_temp.name) if self.icon_temp else QIcon())
            
            def paintEvent(self, a0):
                painter = QPainter(self)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                painter.setBrush(getBackgroundColour())
                painter.drawRect(self.rect())
            
            def closeEvent(self, *args, **kwargs):
                super().closeEvent(*args, **kwargs)
                self.icon_temp.close()
        
        class GetModThread(QThread):
            gotMod = pyqtSignal(dict)
            
            def __init__(self, parent=None, page=1, page_items=10):
                super().__init__(parent)
                self.page = page
                self.page_items = page_items
            
            def run(self):
                try:
                    response = GetModsOnModrinth(limit=self.page_items, offset=(self.page - 1) * self.page_items)
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
            self.contentTabel.pressed.connect(self.modInfoPageOpen)
            self.model = QStandardItemModel()
            self.model.setHorizontalHeaderLabels(
                [self.tr("DownloadPage.DownloadMods.contentTabel.horizontalHeaderLabels.1"),
                 self.tr("DownloadPage.DownloadMods.contentTabel.horizontalHeaderLabels.2"),
                 self.tr("DownloadPage.DownloadMods.contentTabel.horizontalHeaderLabels.3"),
                 self.tr("DownloadPage.DownloadMods.contentTabel.horizontalHeaderLabels.4")])
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
            
            self.retranslateUI()
            
            self.mods = {}
            self.loadingAnimation = None
            self.getModThread = None
            self.modInfoPage = None
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
                 self.tr("DownloadPage.DownloadMods.contentTabel.horizontalHeaderLabels.3"),
                 self.tr("DownloadPage.DownloadMods.contentTabel.horizontalHeaderLabels.4")])
        
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
                self.modInfoPage.setGeometry(self.rect())
                self.modInfoPage.raise_()
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
                    self.model.setItem(e, 2, QStandardItem(hit["date_modified"]))
                    self.model.setItem(e, 3, QStandardItem("modrinth"))
                self.model.setHorizontalHeaderLabels(
                    [self.tr("DownloadPage.DownloadMods.contentTabel.horizontalHeaderLabels.1"),
                     self.tr("DownloadPage.DownloadMods.contentTabel.horizontalHeaderLabels.2"),
                     self.tr("DownloadPage.DownloadMods.contentTabel.horizontalHeaderLabels.3"),
                     self.tr("DownloadPage.DownloadMods.contentTabel.horizontalHeaderLabels.4")])
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
                            if re.match(value_query, hit["title"]):
                                self.model.setItem(cnt, 0, QStandardItem(hit["title"]))
                                self.model.setItem(cnt, 1, QStandardItem(hit["author"]))
                                self.model.setItem(cnt, 2, QStandardItem(hit["date_modified"]))
                                self.model.setItem(cnt, 3, QStandardItem("modrinth"))
                                cnt += 1
                else:
                    self.displayMods(None, self.currentPage)
            except re.error:
                pass
            self.model.setHorizontalHeaderLabels(
                [self.tr("DownloadPage.DownloadMods.contentTabel.horizontalHeaderLabels.1"),
                 self.tr("DownloadPage.DownloadMods.contentTabel.horizontalHeaderLabels.2"),
                 self.tr("DownloadPage.DownloadMods.contentTabel.horizontalHeaderLabels.3"),
                 self.tr("DownloadPage.DownloadMods.contentTabel.horizontalHeaderLabels.4")])
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
                self.modInfoPage = self.ModInfoPage(self, data, hit_data["icon_url"], hit_data["description"],
                                                    hit_data["versions"])
                self.modInfoPage.closePage.connect(self.modInfoPageClose)
                self.modInfoPage.show()
        
        def modInfoPageClose(self):
            self.modInfoPage = None
    
    def __init__(self, parent):
        super().__init__(parent)
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame = Panel(self)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.pages = {}
        
        self.page = self.DownloadVanilla()
        self.page.setObjectName(u"page")
        self.pushButton = PushButton(self.frame)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setCheckable(True)
        self.pushButton.setChecked(True)
        self.pushButton.setAutoExclusive(True)
        self.pushButton.pressed.connect(lambda: self.update_page(self.pushButton))
        
        self.horizontalLayout.addWidget(self.pushButton)
        self.pages[self.pushButton] = self.page
        
        self.page_2 = self.DownloadMods()
        self.page_2.setObjectName(u"page_2")
        self.pushButton_2 = PushButton(self.frame)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setCheckable(True)
        self.pushButton_2.setAutoExclusive(True)
        self.pushButton_2.pressed.connect(lambda: self.update_page(self.pushButton_2))
        
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.pages[self.pushButton_2] = self.page_2
        
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        self.horizontalLayout.addItem(self.horizontalSpacer)
        
        self.verticalLayout.addWidget(self.frame)
        
        self.stackedWidget = QStackedWidget(self)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.addWidget(self.page)
        self.stackedWidget.addWidget(self.page_2)
        self.stackedWidget.setCurrentIndex(0)
        
        self.verticalLayout.addWidget(self.stackedWidget)
        
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
            self.lineEdit.textChanged.connect(self.updatePresentsState)
            self.lineEdit.setClearButtonEnabled(True)
            
            self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lineEdit)
            
            self.verticalLayout.addLayout(self.formLayout)
            
            self.groupBox = GroupBox(self)
            self.groupBox.setObjectName(u"groupBox")
            # self.groupBox.setCheckable(True)
            self.gridLayout = QGridLayout(self.groupBox)
            self.gridLayout.setObjectName(u"gridLayout")
            self.checkBox = CheckBox(self.groupBox)
            self.checkBox.setObjectName(u"checkBox")
            self.checkBox.toggled.connect(lambda state=False: self.presentChecked(state, "-demo"))
            
            # self.checkBox.setFixedHeight(10)
            # self.checkBox.setFixedHeight(100)
            # self.checkBox.setTristate(True)
            
            self.gridLayout.addWidget(self.checkBox, 0, 0, 1, 1)
            
            self.checkBox_2 = CheckBox(self.groupBox)
            self.checkBox_2.setObjectName(u"checkBox_2")
            self.checkBox_2.toggled.connect(lambda state=False: self.presentChecked(state, "-fullscreen"))
            
            self.gridLayout.addWidget(self.checkBox_2, 1, 0, 1, 1)
            
            self.verticalLayout.addWidget(self.groupBox)
            
            self.verticalSpacer = QSpacerItem(20, 360, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
            
            self.verticalLayout.addItem(self.verticalSpacer)
            
            self.retranslateUi()
            #
            # QMetaObject.connectSlotsByName(Form)
        
        # setupUi
        
        def retranslateUi(self):
            self.label.setText(self.tr("SettingsPage.GameSettings.label.Text"))
            self.groupBox.setTitle(self.tr("SettingsPage.GameSettings.gropuBox.Title"))
            self.checkBox.setText(self.tr("SettingsPage.GameSettings.checkBox.Text"))
            self.checkBox_2.setText(self.tr("SettingsPage.GameSettings.checkBox_2.Text"))
        
        # retranslateUi
        
        def presentChecked(self, state, command):
            text = self.lineEdit.text()
            splited_command = shlex.split(text)
            if state:
                if command not in splited_command:
                    splited_command.append(command)
            else:
                if command in splited_command:
                    splited_command.remove(command)
            command = shlex.join(splited_command)
            self.lineEdit.setText(command)
        
        def updatePresentsState(self):
            text = self.lineEdit.text()
            splited_command = shlex.split(text)
            self.checkBox.setChecked("-demo" in splited_command)
            self.checkBox_2.setChecked("-fullscreen" in splited_command)
    
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
            
            self.horizontalLayout.addWidget(self.radioButton)
            
            self.radioButton_2 = RadioButton(self.groupBox)
            self.radioButton_2.setObjectName(u"radioButton_2")
            self.radioButton_2.setChecked(settings["Settings"]["JavaSettings"]["Java"]["LaunchMode"] == "server")
            
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
            font = QFont("Consolas")
            font.setPointSize(13)
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
            self.lineEdit.setFont(font)
            
            self.horizontalLayout_2.addWidget(self.lineEdit)
            
            self.pushButton = TogglePushButton(self.widget)
            self.pushButton.setObjectName(u"pushButton")
            self.pushButton.setChecked(settings["Settings"]["JavaSettings"]["JVM"]["Arg"]["is_override"])
            self.pushButton.toggled.connect(self.updateJVMArgIsOverride)
            
            self.horizontalLayout_2.addWidget(self.pushButton)
            
            self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.widget)
            
            self.verticalLayout.addLayout(self.formLayout)
            
            self.verticalSpacer = QSpacerItem(20, 163, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
            
            self.verticalLayout.addItem(self.verticalSpacer)
            
            self.retranslateUi()
            #
            # QMetaObject.connectSlotsByName(self)
        
        # setupUi
        
        def retranslateUi(self):
            self.groupBox.setTitle(self.tr("SettingsPage.JavaSettings.groupBox.Text"))
            self.radioButton.setText(self.tr("SettingsPage.JavaSettings.radioButton.Text"))
            self.radioButton_2.setText(self.tr("SettingsPage.JavaSettings.radioButton_2.Text"))
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
            print(self.comboBox.currentText())
            if self.comboBox.currentText() not in data and self.comboBox.currentText():
                data = [self.comboBox.currentText()] + data
            self.comboBox.clear()
            for i in data:
                self.comboBox.addItem(i)
        
        def updateJavaPath(self, path):
            print(path)
            if not settings["Settings"]["JavaSettings"]["Java"]["Path"]["is_auto"]:
                settings["Settings"]["JavaSettings"]["Java"]["Path"]["value"] = path
            else:
                settings["Settings"]["JavaSettings"]["Java"]["Path"]["value"] = None
        
        def searchJava(self):
            thread = self.SearchVersionThread(self)
            thread.versionHasGot.connect(self.updateJavaSelectPaths)
            thread.start()
        
        def applyJavaByUser(self):
            java = QFileDialog.getOpenFileName(self, self.tr("SettingsPage.JavaSettings.applyJavaDialogue.Title"),
                                               str(Path(".").absolute()), "java.exe")
            java_path = Path(java[0])
            self.comboBox.addItem(str(java_path))
        
        def updateJVMArgIsOverride(self):
            global settings
            settings["Settings"]["JavaSettings"]["JVM"]["Arg"]["is_override"] = self.pushButton.isChecked()
            self.retranslateUi()
        
        def updateJavaLaunchMode(self):
            if self.radioButton.isChecked():
                settings["Settings"]["JavaSettings"]["Java"]["LaunchMode"] = "client"
            if self.radioButton_2.isChecked():
                settings["Settings"]["JavaSettings"]["Java"]["LaunchMode"] = "server"
    
    class CustomiseSettings(QFrame):
        def __init__(self, parent):
            super().__init__(parent)
            self.verticalLayout = QVBoxLayout(self)
            
            self.groupBox = GroupBox(self)
            self.verticalLayout.addWidget(self.groupBox)
            
            self.girdLayout = QGridLayout(self.groupBox)
            
            self.group1_radioButton = RadioButton(self.groupBox)
            self.group1_radioButton.setChecked(
                settings["Settings"]["LauncherSettings"]["Customise"]["CurrentThemePresent"] == "CMCL_Blue")
            self.group1_radioButton.toggled.connect(lambda state: self.setThemePresent(state, "CMCL_Blue"))
            
            self.girdLayout.addWidget(self.group1_radioButton, 0, 0)
            
            self.group1_radioButton_2 = RadioButton(self.groupBox)
            self.group1_radioButton_2.setChecked(
                settings["Settings"]["LauncherSettings"]["Customise"]["CurrentThemePresent"] == "CMCL_Pink")
            self.group1_radioButton_2.toggled.connect(lambda state: self.setThemePresent(state, "CMCL_Pink"))
            
            self.girdLayout.addWidget(self.group1_radioButton_2, 0, 1)
            
            self.group1_radioButton_3 = RadioButton(self.groupBox)
            self.group1_radioButton.setChecked(
                settings["Settings"]["LauncherSettings"]["Customise"]["CurrentThemePresent"] == "CMCL_Red")
            self.group1_radioButton_3.toggled.connect(lambda state: self.setThemePresent(state, "CMCL_Red"))
            
            self.girdLayout.addWidget(self.group1_radioButton_3, 1, 0)
            
            self.groupBox_2 = GroupBox(self)
            self.verticalLayout.addWidget(self.groupBox_2)
            
            self.verticalLayout_2 = QVBoxLayout(self.groupBox_2)
            
            self.tipLabel = Label(self.groupBox_2)
            self.verticalLayout_2.addWidget(self.tipLabel)
            
            self.girdLayout_2 = QGridLayout()
            self.verticalLayout_2.addLayout(self.girdLayout_2)
            
            self.group2_radioButton = RadioButton(self.groupBox_2)
            self.group2_radioButton.setChecked(True)
            self.girdLayout_2.addWidget(self.group2_radioButton, 0, 0)
            
            self.verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
            self.verticalLayout.addItem(self.verticalSpacer)
            
            self.retranslateUI()
        
        def retranslateUI(self):
            self.groupBox.setTitle(self.tr("SettingsPage.CustomiseSettings.groupBox.Title"))
            self.group1_radioButton.setText("CMCL蓝")
            self.group1_radioButton_2.setText("CMCL粉")
            self.group1_radioButton_3.setText("CMCL红")
            self.groupBox_2.setTitle(self.tr("SettingsPage.CustomiseSettings.groupBox_2.Title"))
            self.tipLabel.setText(
                "该部分的设置要重启启动器才能生效。")  # self.tr("SettingsPage.CustomiseSettings.tipLabel.Text")
            self.group2_radioButton.setText("原生窗口")
        
        @staticmethod
        def setThemePresent(state, value):
            if not state:
                return
            settings["Settings"]["LauncherSettings"]["Customise"]["CurrentThemePresent"] = value
            if value in theme_colour_defines:
                define = theme_colour_defines[value]
                for theme in define:
                    for role in define[theme]:
                        for highlight in define[theme][role]:
                            setThemeColour(role, False, highlight, theme,
                                           theme_colour_defines[value][theme][role][highlight])
    
    def __init__(self, parent):
        super().__init__(parent)
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame = Panel(self)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.pages = {}
        
        self.page = self.GameSettings(self)
        self.pushButton = PushButton(self.frame)
        self.pushButton.setCheckable(True)
        self.pushButton.setChecked(True)
        self.pushButton.setAutoExclusive(True)
        self.pushButton.pressed.connect(lambda: self.update_page(self.pushButton))
        
        self.horizontalLayout.addWidget(self.pushButton)
        self.pages[self.pushButton] = self.page
        
        self.page_2 = self.JavaSettings(self)
        self.pushButton_2 = PushButton(self.frame)
        self.pushButton_2.setCheckable(True)
        self.pushButton_2.setAutoExclusive(True)
        self.pushButton_2.pressed.connect(lambda: self.update_page(self.pushButton_2))
        
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.pages[self.pushButton_2] = self.page_2
        
        self.page_3 = self.CustomiseSettings(self)
        self.pushButton_3 = PushButton(self.frame)
        self.pushButton_3.setCheckable(True)
        self.pushButton_3.setAutoExclusive(True)
        self.pushButton_3.pressed.connect(lambda: self.update_page(self.pushButton_3))
        
        self.horizontalLayout.addWidget(self.pushButton_3)
        self.pages[self.pushButton_3] = self.page_3
        
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        self.horizontalLayout.addItem(self.horizontalSpacer)
        
        self.verticalLayout.addWidget(self.frame)
        
        self.stackedWidget = QStackedWidget(self)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.addWidget(self.page)
        self.stackedWidget.addWidget(self.page_2)
        self.stackedWidget.addWidget(self.page_3)
        
        self.verticalLayout.addWidget(self.stackedWidget)
        
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
        self.avatar1.setIcon(QIcon(":/chengwm_headimage.png"))
        
        self.horizontalLayout.addWidget(self.avatar1)
        
        self.label1 = Label(self.panel1)
        self.label1.setText("chengwm\nCommon Minecraft Launcher 的作者。")
        
        self.horizontalLayout.addWidget(self.label1, 1)
        
        self.verticalLayout_2.addWidget(self.panel1)
        
        self.panel2 = Panel(self.page1)
        self.horizontalLayout_2 = QHBoxLayout(self.panel2)
        
        self.avatar2 = ToolButton(self.panel2)
        self.avatar2.setFixedSize(QSize(42, 42))
        self.avatar2.setIconSize(QSize(32, 32))
        self.avatar2.setIcon(QIcon())
        
        self.horizontalLayout_2.addWidget(self.avatar2)
        
        self.label2 = Label(self.panel2)
        self.label2.setText("Minecraft_稻田\nCommon Minecraft Launcher 的策划。")
        
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
        self.cmcl_icon.setIcon(QIcon(":/CMCL_icon.svg"))
        
        self.horizontalLayout_3.addWidget(self.cmcl_icon)
        
        self.cmcl_info = Label(self.panel_cmcl)
        self.cmcl_info.setText(self.tr("AboutPage.Page2.CMCL_info").format(CMCL_version[0], CMCL_version[1], language))
        
        self.horizontalLayout_3.addWidget(self.cmcl_info, 1)
        
        self.verticalLayout_3.addWidget(self.panel_cmcl)
        
        self.verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.verticalLayout_3.addItem(self.verticalSpacer)
        
        self.toolBox.addItem(self.page2, self.tr("AboutPage.Page2.Title"))
        
        self.verticalLayout.addWidget(self.toolBox)
        
        # Special Thanks:
        # 中文 Minecraft Wiki -> 提供教程。
        # 龙腾猫跃 -> PCL2启动器的作者
        # zhiyiYo
        self.retranslateUI()
    
    def retranslateUI(self):
        pass


class OfflinePlayerCreationDialogue(RoundedDialogue):
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
        self.horizontalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.OKButton = PushButton(self.bottomPanel)
        self.horizontalLayout.addWidget(self.OKButton)
        self.OKButton.pressed.connect(self.setPlayer)
        self.verticalLayout.addWidget(self.bottomPanel)
        self.retranslateUI()
    
    def retranslateUI(self):
        self.label.setText(self.tr("OfflinePlayerCreationDialogue.label.Text"))
        self.CancelButton.setText(self.tr("OfflinePlayerCreationDialogue.CancelButton.Text"))
        self.OKButton.setText(self.tr("OfflinePlayerCreationDialogue.OKButton.Text"))
    
    def setPlayer(self):
        global player
        player = create_offline_player(self.playernameLineEdit.text(), player.player_hasMC)
        frame.UserPage.user_datas[frame.UserPage.current_user] = player
        self.close()


class UserPage(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.user_datas = []
        self.current_user = 0
        
        # DEBUG: ON#
        # self.user_datas.append(create_online_player("2233", "68559", "TheFengHaoDouLuoOfBiZhan", True))
        # self.user_datas.append(create_online_player("22和33", "68559", "TheSameAsAbove", True))
        # self.user_datas.append(player)
        # self.user_datas.append(create_online_player("chengwm_CMCL", "100000000", "NoAccessToken", False))
        # self.current_user = 2
        # DEBUG: END#
        
        self.user_datas.append(player)
        
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
                self.tr("UserPage.UserDataFormat.Text").format(left_user.player_name, left_user.player_accountType[1],
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
                self.tr("UserPage.UserDataFormat.Text").format(current_user.player_name,
                                                               current_user.player_accountType[1],
                                                               current_user.player_hasMC))
        else:
            self.UserIcon.setText(self.tr("UserPage.UserIconNoUser.Text"))
        self.UserIcon.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.UserIcon.pressed.connect(self.startLogin)
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
                self.tr("UserPage.UserDataFormat.Text").format(right_user.player_name, right_user.player_accountType[1],
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
            self.userModel.setItem(e, 0, QStandardItem(i.player_name))
            self.userModel.setItem(e, 1, QStandardItem(i.player_accountType[1]))
        
        self.retranslateUI()
        
        def tempfun(self):
            if len(self.user_datas) > 0:
                current_user = self.user_datas[self.current_user]
                self.UserIcon.setText(
                    self.tr("UserPage.UserDataFormat.Text").format(current_user.player_name,
                                                                   current_user.player_accountType[1],
                                                                   current_user.player_hasMC))
            else:
                self.UserIcon.setText(self.tr("UserPage.UserIconNoUser.Text"))
            self.userModel.clear()
            self.userModel.setHorizontalHeaderLabels([self.tr("UserPage.userTable.horizontalHeaderLabels.1"),
                                                      self.tr("UserPage.userTable.horizontalHeaderLabels.2")])
            for e, i in enumerate(self.user_datas):
                self.userModel.setItem(e, 0, QStandardItem(i.player_name))
                self.userModel.setItem(e, 1, QStandardItem(i.player_accountType[1]))
        
        timer = QTimer(self)
        timer.setInterval(100)
        timer.timeout.connect(lambda: tempfun(self))
        timer.start()
    
    def retranslateUI(self):
        if len(self.user_datas) > 1 and self.current_user >= 1:
            left_user = self.user_datas[min(max(self.current_user - 1, 0), len(self.user_datas) - 1)]
            self.leftUserIcon.setToolTip(
                self.tr("UserPage.UserDataFormat.Text").format(left_user.player_name, left_user.player_accountType[1],
                                                               left_user.player_hasMC))
        else:
            self.leftUserIcon.setToolTip("")
        if len(self.user_datas) > 0:
            current_user = self.user_datas[self.current_user]
            self.UserIcon.setText(
                self.tr("UserPage.UserDataFormat.Text").format(current_user.player_name,
                                                               current_user.player_accountType[1],
                                                               current_user.player_hasMC))
        else:
            self.UserIcon.setText(self.tr("UserPage.UserIconNoUser.Text"))
        if len(self.user_datas) > 1 and self.current_user < len(self.user_datas) - 1:
            right_user = self.user_datas[min(max(self.current_user + 1, 0), len(self.user_datas) - 1)]
            self.rightUserIcon.setToolTip(
                self.tr("UserPage.UserDataFormat.Text").format(right_user.player_name, right_user.player_accountType[1],
                                                               right_user.player_hasMC))
        else:
            self.rightUserIcon.setToolTip("")
        self.addUserBtn.setText(self.tr("UserPage.addUserBtn.Text"))
        self.createAddUserBtnActions()
        self.userModel.clear()
        self.userModel.setHorizontalHeaderLabels([self.tr("UserPage.userTable.horizontalHeaderLabels.1"),
                                                  self.tr("UserPage.userTable.horizontalHeaderLabels.2")])
        for e, i in enumerate(self.user_datas):
            self.userModel.setItem(e, 0, QStandardItem(i.player_name))
            self.userModel.setItem(e, 1, QStandardItem(i.player_accountType[1]))
    
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
        self.current_user = id
        self.current_user = max(0, min(len(self.user_datas) - 1, self.current_user))
        self.retranslateUI()
    
    @staticmethod
    def startLogin():
        dialogue = LoginDialogue()
        dialogue.exec()
    
    @staticmethod
    def startCreateOfflinePlayer():
        dialogue = OfflinePlayerCreationDialogue()
        dialogue.exec()


class MainWindow(window_class):
    def __init__(self):
        super().__init__()
        self.resize(800, 600)
        self.setWindowIcon(QIcon(":/CMCL_icon.svg"))
        title = "Common Minecraft Launcher"
        if random.randint(1, 100) == random.randint(1, 100):
            title = "Chengwm's Minecraft Launcher"
        if random.randint(1, 100000) == random.randint(1, 100000):
            title = title.replace("Minecraft", "Minceraft")
        self.setWindowTitle(title)
        # self.setWindowOpacity(0.9)
        self.titleBar.hide()
        self.titleBar = StandardTitleBar(self)
        self.titleBar.show()
        self.titleBar.raise_()
        self.titleBar.iconLabel.setPixmap(self.windowIcon().pixmap(20, 20))
        self.titleBar.titleLabel.setText(self.windowTitle())
        self.titleBar.titleLabel.setStyleSheet(
            "background: transparent; padding: 0 4px; font: 13px 'Segoe UI'; color: black")
        self.setStyleSheet("background: transparent")
        self.centralwidget = QWidget(self)
        self.horizontalLayout = QVBoxLayout(self.centralwidget)
        self.horizontalLayout.setContentsMargins(5, 37, 5, 5)
        self.horizontalLayout.setSpacing(10)
        self.topWidget = NavigationPanel(self.centralwidget)
        self.topWidget.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.HomePage = MainPage(self)
        self.topWidget.addItem(self.HomePage, ":/Home.svg", self.tr("MainWindow.HomePage.Text"))
        # self.tr("MainWindow.VersionSettingsPage.Text") = "版本设置"
        self.DownloadPage = DownloadPage(self)
        self.topWidget.addItem(self.DownloadPage, ":/Download.svg", self.tr("MainWindow.DownloadPage.Text"))
        self.SettingsPage = SettingsPage(self)
        self.topWidget.addItem(self.SettingsPage, ":/Settings.svg", self.tr("MainWindow.SettingsPage.Text"))
        self.AboutPage = AboutPage(self)
        self.topWidget.addItem(self.AboutPage, ":/About.svg", self.tr("MainWindow.AboutPage.Text"))
        self.UserPage = UserPage(self)
        self.topWidget.addItem(self.UserPage, ":/user_icon-black.svg", self.tr("MainWindow.UserPage.Text"),
                               pos=NavigationPanel.NavigationItemPosition.Right)
        self.topWidget.addButton("", "", selectable=False, pressed=self.toggle_theme,
                                 pos=NavigationPanel.NavigationItemPosition.Right)
        self.horizontalLayout.addWidget(self.topWidget)
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
    
    def showCentre(self):
        geometry = QGuiApplication.primaryScreen().geometry()
        point = QPoint(geometry.width() // 2 - self.width() // 2, geometry.height() // 2 - self.height() // 2)
        self.move(point)
        self.showNormal()
    
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
    
    def updateIcon(self):
        if self.topWidget.button("5"):
            self.topWidget.button("5").setIcon(
                QIcon(f":/user_icon-{'black' if getTheme() == Theme.Light else 'white'}.svg"))
        if self.topWidget.button("6"):
            self.topWidget.button("6").setIcon(QIcon(f":/{'light' if getTheme() == Theme.Light else 'dark'}.svg"))
            self.topWidget.button("6").setText(
                self.tr("MainPage.ToggleTheme.Light.Text") if getTheme() == Theme.Light else self.tr(
                    "MainPage.ToggleTheme.Dark.Text"))
    
    def paintEvent(self, a0, **kwargs):
        painter = QPainter(self)
        painter.fillRect(
            QRect(-self.geometry().x(), -self.geometry().y(), QGuiApplication.primaryScreen().geometry().width(),
                  QGuiApplication.primaryScreen().geometry().height()),
            QGradient(QGradient.Preset.DeepBlue if getTheme() == Theme.Light else QGradient.Preset.PerfectBlue))
    
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
            
            def __import__(name, *args, **kwargs):
                raise RuntimeError("cannot use function `__import__` for safety")
            
            def exec(*args, **kwargs):
                raise RuntimeError("cannot use function `exec` for safety")
            
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
                "__import__": __import__,
                "exec": exec,
                "input": input,
                "sys": sys,
                "player": player,
                "frame": frame
            }
            for i in extra_globals.items():
                self.globals[i[0]] = i[1]
            self.locals = {
                "__import__": __import__,
                "exec": exec,
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
        self.setWindowIcon(QIcon(":/CMCL_icon.svg"))
        self.setWindowTitle(self.tr("LoggingWindow.Title"))
        self.titleBar.hide()
        self.titleBar = StandardTitleBar(self)
        self.titleBar.show()
        self.titleBar.raise_()
        self.titleBar.iconLabel.setPixmap(self.windowIcon().pixmap(20, 20))
        self.titleBar.iconLabel.setStyleSheet("background: transparent;")
        self.titleBar.titleLabel.setText(self.windowTitle())
        self.titleBar.titleLabel.setStyleSheet(
            "background: transparent; padding: 0 4px; font: 13px 'Segoe UI'; color: black")
        self.setStyleSheet("background: white;")
        self.toolPanel = Panel(self)
        self.horizontalLayout = QHBoxLayout(self.toolPanel)
        self.stopOutputBtn = PushButton(self.toolPanel)
        self.stopOutputBtn.setText("")
        self.stopOutputBtn.pressed.connect(self.toggleOutput)
        self.horizontalLayout.addWidget(self.stopOutputBtn)
        spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.horizontalLayout.addItem(spacer)
        self.loggingtext = self.LoggingText(self)
        self.loggingtext.setReadOnly(True)
        # self.loggingtext.setLineWrapMode(self.LoggingText.LineWrapMode.NoWrap)
        font = QFont("Consolas")
        font.setPointSize(13)
        self.loggingtext.setFont(font)
        self.bftext = output.getvalue()
        self.loggingtext.setText(output.getvalue())
        timer = QTimer(self)
        timer.timeout.connect(self.updateText)
        timer.start(100)
        self.inputtext = LineEdit(self)
        self.inputtext.returnPressed.connect(self.process_command)
        self.inputtext.setFont(font)
        self.inputtext.setToolTip(
            "输入代码以运行。\n内置的变量：\n  'frame'：启动器主窗口\n  'player'：当前玩家\n  '[一些奇奇怪怪的函数]'：没啥用")
        self.canOutput = True
        self.retranslateUI()
        import nothingtoseeheremovealong, hashlib
        self.cmd = self.Executer(
            {"frame": frame, "player": player,
             hashlib.md5(b"1").hexdigest(): (lambda: nothingtoseeheremovealong.testtextof2233()),
             hashlib.md5(b"2").hexdigest(): (lambda: nothingtoseeheremovealong.let2233banyou1()),
             hashlib.md5(b"3").hexdigest(): (lambda: nothingtoseeheremovealong.let2233banyou2())})
        self.history_command = []
        self.current_history = 0
    
    def retranslateUI(self):
        self.stopOutputBtn.setText(self.tr("LoggingWindow.stopOutputBtn.StopOut.Text") if self.canOutput else self.tr(
            "LoggingWindow.stopOutputBtn.StartOut.Text"))
    
    def updateText(self):
        if self.bftext != output.getvalue():
            Path("latest.log").write_text(output.getvalue(), encoding="utf-8")
        if self.canOutput:
            if self.bftext != output.getvalue() or self.loggingtext.toPlainText() != output.getvalue():
                self.loggingtext.setText("")
                self.loggingtext.textCursor().insertText(output.getvalue())
                self.loggingtext.ensureCursorVisible()
                self.bftext = output.getvalue()
    
    def toggleOutput(self):
        self.canOutput = not self.canOutput
        self.stopOutputBtn.setText(self.tr("LoggingWindow.stopOutputBtn.StopOut.Text") if self.canOutput else self.tr(
            "LoggingWindow.stopOutputBtn.StartOut.Text"))
    
    def process_command(self):
        if self.inputtext.text():
            self.history_command.append(self.inputtext.text())
            self.cmd.process_command(self.inputtext.text())
            self.inputtext.clear()
            self.current_history = 0
    
    def closeEvent(self, a0):
        super().closeEvent(a0)
        for i in QGuiApplication.allWindows():
            i.close()
    
    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        self.toolPanel.setGeometry(QRect(5, 32, self.width() - 10, 55))
        self.loggingtext.setGeometry(self.rect().adjusted(0, 92, 0, -37))
        self.inputtext.setGeometry(5, self.height() - 32 - 5,
                                   self.width() - 10,
                                   32)
    
    def keyPressEvent(self, a0):
        super().keyPressEvent(a0)
        if a0.key() == 16777235:
            if self.history_command and self.current_history < len(self.history_command):
                self.current_history += 1
                self.inputtext.setText(self.history_command[int(f"-{self.current_history}")])
        if a0.key() == 16777237:
            if self.history_command and self.current_history > 1:
                self.current_history -= 1
                self.inputtext.setText(self.history_command[int(f"-{self.current_history}")])
    
    def paintEvent(self, a0, **kwargs):
        painter = QPainter(self)
        painter.fillRect(
            QRect(-self.geometry().x(), -self.geometry().y(), QGuiApplication.primaryScreen().geometry().width(),
                  QGuiApplication.primaryScreen().geometry().height()),
            QGradient(QGradient.Preset.DeepBlue if getTheme() == Theme.Light else QGradient.Preset.PerfectBlue))


# class MidAutumnMsgDialogue(RoundedDialogue):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.verticalLayout = QVBoxLayout(self)
#         self.verticalLayout.setContentsMargins(11, 32, 11, 11)
#         self.scrollArea = ScrollArea(self)
#         self.verticalLayout.addWidget(self.scrollArea)
#         self.scrollAreaContentWidget = QWidget()
#         self.scrollArea.setStyleSheet("background: transparent;")
#         self.verticalLayout_2 = QVBoxLayout(self.scrollAreaContentWidget)
#         tip = Tip(self, False)
#         self.tlabel = Label(tip)
#         self.tlabel.setText(
#             "<a href=\"https://www.bilibili.com/v/topic/detail/?topic_id=1227830&topic_name=%E4%B8%AD%E7%A7%8B%E6%BC%AB%E6%B8%B8%E5%A4%9C&spm_id_from=333.1369.opus.module_topic.click\">#中秋漫游夜#</a>")
#         tip.setCentralWidget(self.tlabel)
#         self.verticalLayout_2.addWidget(tip)
#         self.label = Label(self.scrollAreaContentWidget)
#         self.label.setText(f"""<!DOCTYPE html>
#                         <html>
#                             <head/>
#                             <body>
#                                 <p>
#                                     <hr/>
#                                     <del style="text-decoration: line-through;">是的，我又来了</del><br/>
#                                     <h2>开头</h2>
#                                     ---------<br/>
#                                     大家都知道最近要过什么节日吧。<br/>
#                                     要过中秋了，我绝对不能缺席。<br/>
#                                     前几天，我去看22和33她们，发现她们新发了一个动态，<br/>
#                                     在这：<a href="https://www.bilibili.com/opus/977006529028816946?spm_id_from=333.999.0.0">https://www.bilibili.com/opus/977006529028816946?spm_id_from=333.999.0.0</a>。<br/>
#                                     然后呢？<small style="font-size: xx-small">（又来）</small>
#                                     <h2>内容</h2>
#                                     ---------<br/>
#                                     先感谢22和33送上的中秋节祝福。<br/>
#                                     然后......<br/>
#                                     等一下，22，你说什么？<br/>
#                                     你说今年有中秋晚会看？？？<br/>
#                                     (内容见这里：<a href="https://www.bilibili.com/blackboard/zhongqiu2024.html">https://www.bilibili.com/blackboard/zhongqiu2024.html</a>)<br/>
#                                     那么......<br/>
#                                     16日晚上19:30锁定哔哩哔哩<a href="https://search.bilibili.com/all?keyword=%E8%8A%B1%E5%A5%BD%E6%9C%88%E5%9C%86%E4%BC%9A">#花好月圆会#</a>，2233陪你过。<br/>
#                                     不过......<br/>
#                                     有什么问题？？？<br/>
#                                     我会不会....一不小心....就要......<br/>
#                                     我懂你接下来要说的话，<br/>
#                                     那么记得19:30过来！<br/>
#                                 </p>
#                             </body>
#                         </html>""")
#         self.label.setWordWrap(True)
#         self.verticalLayout_2.addWidget(self.label)
#         self.scrollArea.setWidget(self.scrollAreaContentWidget)
#         self.scrollArea.setWidgetResizable(True)
#         timer = QTimer(self)
#         timer.timeout.connect(self.__a)
#         timer.start(1)
#         self.__o = False
#
#     def __a(self):
#         self.tlabel.setText(
#             f"<a href=\"https://www.bilibili.com/v/topic/detail/?topic_id=1227830&topic_name=%E4%B8%AD%E7%A7%8B%E6%BC%AB%E6%B8%B8%E5%A4%9C&spm_id_from=333.1369.opus.module_topic.click\">#中秋漫游夜#</a><br/>{(time.strftime('距离《花好月圆会·2024Bilibili中秋漫游会》开播还有%H时%M分%S秒', time.gmtime(time.mktime((2024, 9, 16, 19, 30, 0, 0, 0, 0)) - time.time()))) if time.mktime((2024, 9, 16, 19, 30, 0, 0, 0, 0)) - time.time() > 0 else '《花好月圆会·2024Bilibili中秋漫游会》已开播。'}")
#
#     def resizeEvent(self, a0, **kwargs):
#         super().resizeEvent(a0)
#         self.scrollArea.setGeometry(0, 32, self.width(), self.height() - 32)
#
#     def paintEvent(self, a0, **kwargs):
#         painter = QPainter(self)
#         painter.fillRect(
#             QRect(-self.geometry().x(), -self.geometry().y(), QGuiApplication.primaryScreen().geometry().width(),
#                   QGuiApplication.primaryScreen().geometry().height()),
#             QGradient(QGradient.Preset.DeepBlue if getTheme() == Theme.Light else QGradient.Preset.PerfectBlue))


def login_user(name_or_token=b"", is_refresh_login=False):
    try:
        conn = sqlite3.connect("user_data.DAT")
        cursor = conn.cursor()
        try:
            cursor.execute("create table users (refresh_token TEXT, player_name TEXT)")
        except sqlite3.OperationalError:
            pass
        if is_refresh_login:
            cursor.execute(
                f'select refresh_token from users where player_name = "{name_or_token.decode()}"')
            token = base64.b64decode(cursor.fetchone()[0])
        else:
            token = name_or_token
        token = token.decode()
        status, player, refresh_token = MicrosoftPlayerLogin(token, is_refresh_login)
        if not is_refresh_login:
            byte_name = b"".join(
                [str(player.player_name[i] if i < len(player.player_name) else random.randrange(0, 10)).encode("utf-8")
                 for
                 i in range(16)])
            key = str(UUID(bytes=byte_name))
        else:
            byte_name = b"1234567890123456"
            key = name_or_token.decode()
        if refresh_token:
            if not is_refresh_login:
                cursor.execute(
                    f'insert into users (refresh_token, player_name) values ("{base64.b64encode(bytes(refresh_token, encoding="utf-8")).decode()}", "{key}")')
            else:
                cursor.execute(
                    f'update users set refresh_token = "{base64.b64encode(bytes(refresh_token, encoding="utf-8")).decode()}" where player_name = "{key}"')
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


def exception(*args, **kwargs):
    Path("settings.json").write_text(json.dumps(settings, indent=2))


def __excepthook__(*args, **kwargs):
    try:
        traceback.print_exception(*args, **kwargs)
        exception(*args, **kwargs)
    finally:
        Path("error.log").open("a", encoding="utf-8").write("".join(traceback.format_exception(*args, **kwargs)))


sys.excepthook = __excepthook__
if platform.system().lower() == "windows":
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv),
                                            str(Path(".").absolute()), 1)
        sys.exit(0)
logging.basicConfig(
    level=logging.NOTSET,
    format="[%(asctime)s][%(levelname)s]:%(message)s",
    datefmt="%Y/%m/%d][%H:%M:%S %p"
)
if Path("settings.json").exists():
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
                    "CurrentThemePresent": "CMCL_Blue",
                    "CurrentTheme": "Light"
                }
            }
        }
    }
app = QApplication(sys.argv)
app.setFont(QFont("Harmony OS Sans SC"))
font_id = QFontDatabase.addApplicationFont(":/Unifont 13.0.01.ttf")
if font_id != -1:
    font_families = QFontDatabase.applicationFontFamilies(font_id)
    if font_families:
        font = QFont(font_families[0])
        app.setFont(font)

app.setDesktopSettingsAware(False)
app.setEffectEnabled(Qt.UIEffect.UI_AnimateMenu)

player = create_online_player(None, None, None, False)

# player = LittleSkinPlayer("chengwm", "random", "random",
#                           "MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEArGcNOOFIqLJSqoE3u0hj\ntOEnOcET3wj9Drss1BE6sBqgPo0bMulOULhqjkc/uH/wyosYnzw3xaazJt87jTHh\nJ8BPMxCeQMoyEdRoS3Jnj1G0Kezj4A2b61PJJM1DpvDAcqQBYsrSdpBJ+52MjoGS\nvJoeQO5XUlJVQm21/HmJnqsPhzcA6HgY71RHYE5xnhpWJiPxLKUPtmt6CNYUQQoS\no2v36XWgMmLBZhAbNOPxYX+1ioxKamjhLO29UhwtgY9U6PWEO7/SBfXzyRPTzhPV\n2nHq7KJqd8IIrltslv6i/4FEM81ivS/mm+PN3hYlIYK6z6Ymii1nrQAplsJ67OGq\nYHtWKOvpfTzOollugsRihkAG4OB6hM0Pr45jjC3TIc7eO7kOgIcGUGUQGuuugDEz\nJ1N9FFWnN/H6P9ukFeg5SmGC5+wmUPZZCtNBLr8o8sI5H7QhK7NgwCaGFoYuiAGL\ngz3k/3YwJ40BbwQayQ2gIqenz+XOFIAlajv+/nyfcDvZH9vGNKP9lVcHXUT5YRnS\nZSHo5lwvVrYUrqEAbh/zDz8QMEyiujWvUkPhZs9fh6fimUGxtm8mFIPCtPJVXjeY\nwD3Lvt3aIB1JHdUTJR3eEc4eIaTKMwMPyJRzVn5zKsitaZz3nn/cOA/wZC9oqyEU\nmc9h6ZMRTRUEE4TtaJyg9lMCAwEAAQ==",
#                           "https://littleskin.cn/api/yggdrasil", True)

# "%appdata%\Python\Python311\Scripts\pyside6-rcc.exe" resources.qrc -o resources.py
# "%appdata%\Python\Python311\Scripts\pyside6-lupdate.exe" main.py -ts CMCL_zh-cn.ts
translator = QTranslator()
translator.load(":/CMCL_zh-cn.qm")
app.installTranslator(translator)

match settings["Settings"]["LauncherSettings"]["Customise"]["CurrentTheme"]:
    case "Light":
        setTheme(Theme.Light)
    case "Dark":
        setTheme(Theme.Dark)

frame = MainWindow()
frame.showCentre()
if DEBUG:
    debug = LoggingWindow()
    debug.show()
# Log Redirect Text
# print("[2024/08/16][22:33:00 PM][INFO]:F22战斗姬！22是F！33也可以是F！\n"
#       "[2024/08/16][22:33:00 PM][INFO]:在刚毅云音乐上，22娘这个账号有九首歌，\n"
#       "[2024/08/16][22:33:00 PM][INFO]:33娘这个账号则有11首歌。\n"
#       "[2024/08/16][22:33:00 PM][INFO]:她们还有个叫 22和33 的账号。\n"
#       "[2024/08/16][22:33:00 PM][INFO]:让我们祝她们生日快乐！\n"
#       "[2023/08/29][20:03:12 PM][INFO]:启动器的第一个文件创建！\n"
#       "[2009/06/26][??:??:?? ??][INFO]:某个叫 Mikufans 的网站创建！（Mikufans 就是今天的 Bilibili！）\n"
#       "[2008/??/??][??:??:?? ??][INFO]:Minecraft 前身 RubyDung 被 Markus Persson 创建！\n"
#       "[2009/05/10][17:36:00 PM][INFO]:Minecraft 最早版本 rd-131655 的视频被上传！\n"
#       "[2011/11/17][22:00:00 PM][INFO]:Minecraft 1.0.0 发布！")
# END Text
thread = LoginThread()
thread.loginFinished.connect(update_user)
thread.start()
app.exec()
Path("settings.json").write_text(json.dumps(settings, indent=2))
