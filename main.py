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
from dateutil import tz
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
import gettext

from CMCLWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from CMCLWidgets.Windows import *
from qframelesswindow import StandardTitleBar

from CMCLCore.Launch import LaunchMinecraft
from CMCLCore.Login import MicrosoftPlayerLogin
from CMCLCore.Player import create_online_player, create_offline_player, MicrosoftPlayer, LittleSkinPlayer
from CMCLCore.GetVersion import GetVersionByScanDirectory, GetVersionByMojangApi
from CMCLCore.DownloadVersion import DownloadMinecraft
from CMCLCore.GetOperationSystem import GetOperationSystemName

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

CMCL_version = ("Alpha-24001", "Alpha-24001")
minecraft_path = Path(r"D:\Program Files\minecraft")
language = "zh-cn"


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
        self.__svgWidget.load("CMCL_loading.svg")
        self.__svgWidget.setFixedSize(96, 96)
        self.__svgWidget.setStyleSheet("background: transparent;")
        dsg = QGraphicsDropShadowEffect(self.__svgWidget)
        dsg.setBlurRadius(30)
        dsg.setOffset(0, 4)
        dsg.setColor(QColor(0, 0, 0, 100))
        self.__svgWidget.setGraphicsEffect(dsg)
        self.__failedSvg = QSvgWidget(self.__svgWidget)
        self.__failedSvg.load("CMCL_loading_failed.svg")
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
        self.__svgWidget.load("CMCL_loading.svg")
        self.__failedSvg.load("CMCL_loading_failed.svg")
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
        except RuntimeError:
            pass
        if not failed:
            if ani:
                self.TransparencyAnimation(self, "out").start()
                self.HideAnimation(self).start()
            else:
                self.hide()
            self.__statusLabel.setText(self.tr("LoadingAnimation.statusLabel.SuccessText"))
            self.__failedSvg.hide()
        else:
            self.setStyleSheet(f"background: rgb({'255, 200, 200' if getTheme() == Theme.Light else '100, 50, 50'});")
            self.__statusLabel.setText(self.tr("LoadingAnimation.statusLabel.FailedText"))
            self.__failedSvg.show()
    
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
        spacer2 = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.horizontalLayout.addItem(spacer2)
        self.retranslateUI()
        self.bottomPanelIsShow = True
    
    def retranslateUI(self):
        self.launch_btn.setText(self.tr("MainPage.launch_btn.Text"))
        self.select_version_btn.setText(self.version or self.tr("MainPage.select_version_btn.DefaultText"))
        self.change_dir_btn.setText(self.tr("MainPage.change_dir_btn.Text"))
    
    def select_version(self, version):
        self.version = version
        self.select_version_btn.setText(self.version or self.tr("MainPage.select_version_btn.DefaultText"))
    
    def launch(self):
        result = LaunchMinecraft(minecraft_path, self.version,
                                 None if settings["Settings"]["JavaSettings"]["Java"]["Path"]["is_auto"] else
                                 settings["Settings"]["JavaSettings"]["Java"]["Path"]["value"],
                                 settings["Settings"]["JavaSettings"]["Java"]["LaunchMode"],
                                 CMCL_version[0], "CMCL", None, None, None,
                                 settings["Settings"]["GameSettings"]["ExtraGameCommand"], None, None,
                                 player)
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
        self.select_version_btn.setMenu(menu)
    
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
                self.pushButton.setText(self.version or u"22.33")
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
            self.verticalLayout.setObjectName(u"verticalLayout")
            self.lineEdit = LineEdit(self)
            self.lineEdit.setObjectName(u"lineEdit")
            self.lineEdit.setClearButtonEnabled(True)
            self.lineEdit.textChanged.connect(self.searchVersion)
            
            self.verticalLayout.addWidget(self.lineEdit)
            
            self.tableView = TableView(self)
            self.tableView.setObjectName(u"tableView")
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
                            version_type = "正式版"
                        case "snapshot":
                            version_type = "快照版"
                        case "old_beta":
                            version_type = "远古 beta"
                        case "old_alpha":
                            version_type = "远古 alpha"
                        case _:
                            version_type = version_type_real
                    unformatted_release_time = i["releaseTime"]
                    release_datetime = datetime.datetime.strptime(unformatted_release_time,
                                                                  "%Y-%m-%dT%H:%M:%S+00:00")
                    localised_release_datetime = release_datetime.replace(tzinfo=datetime.UTC).astimezone(tz.tzlocal())
                    release_time = localised_release_datetime.strftime("%Y-%m-%d %H:%M:%S")
                    if release_datetime.month == 4 and release_datetime.day == 1:
                        version_type = "愚人节版本"
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
                            version_type = "正式版"
                        case "snapshot":
                            version_type = "快照版"
                        case "old_beta":
                            version_type = "远古 beta"
                        case "old_alpha":
                            version_type = "远古 alpha"
                        case _:
                            version_type = version_type
                    release_datetime = value["ReleaseDatetime"]
                    if release_datetime.month == 4 and release_datetime.day == 1:
                        version_type = "愚人节版本"
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
                            version_type = "正式版"
                            latest_release = True
                        case "snapshot":
                            if latest_snapshot:
                                continue
                            version_type = "快照版"
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
                                    version_type = "正式版"
                                case "snapshot":
                                    version_type = "快照版"
                                case "old_beta":
                                    version_type = "远古 beta"
                                case "old_alpha":
                                    version_type = "远古 alpha"
                                case _:
                                    version_type = version_type
                            release_datetime = value["ReleaseDatetime"]
                            if release_datetime.month == 4 and release_datetime.day == 1:
                                version_type = "愚人节版本"
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
        
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        self.horizontalLayout.addItem(self.horizontalSpacer)
        
        self.verticalLayout.addWidget(self.frame)
        
        self.stackedWidget = QStackedWidget(self)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.addWidget(self.page)
        self.stackedWidget.setCurrentIndex(0)
        
        self.verticalLayout.addWidget(self.stackedWidget)
        
        self.retranslateUi()
        #
        # QMetaObject.connectSlotsByName(Form)
    
    # setupUi
    
    def retranslateUi(self):
        self.pushButton.setText(self.tr("DownloadPage.pushButton.text"))
        # self.pushButton_2.setText("")
    
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
            font = QFont("Consolas")
            font.setPointSize(13)
            self.comboBox.setFont(font)
            self.horizontalLayout_3.addWidget(self.comboBox, 1)
            
            self.pushButton_2 = TogglePushButton(self.widget_2)
            self.pushButton_2.setObjectName(u"pushButton_2")
            self.pushButton_2.setChecked(settings["Settings"]["JavaSettings"]["Java"]["Path"]["is_auto"])
            if not self.pushButton_2.isChecked():
                self.comboBox.setEnabled(True)
                self.searchJava()
            else:
                self.comboBox.clear()
                self.comboBox.setCurrentText(self.tr("SettingsPage.JavaSettings.comboBox.Text"))
                self.comboBox.setEnabled(False)
            self.pushButton_2.toggled.connect(self.updateJavaPathIsAuto)
            
            self.horizontalLayout_3.addWidget(self.pushButton_2)
            
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
                self.searchJava()
            else:
                self.comboBox.clear()
                self.comboBox.setCurrentText(self.tr("SettingsPage.JavaSettings.comboBox.Text"))
                self.comboBox.setEnabled(False)
            self.retranslateUi()
        
        def updateJavaSelectPaths(self, data):
            self.comboBox.clear()
            for i in data:
                self.comboBox.addItem(i)
        
        def searchJava(self):
            thread = self.SearchVersionThread(self)
            thread.versionHasGot.connect(self.updateJavaSelectPaths)
            thread.start()
        
        def updateJVMArgIsOverride(self):
            global settings
            settings["Settings"]["JavaSettings"]["JVM"]["Arg"]["is_override"] = self.pushButton.isChecked()
            self.retranslateUi()
        
        def updateJavaLaunchMode(self):
            if self.radioButton.isChecked():
                settings["Settings"]["JavaSettings"]["Java"]["LaunchMode"] = "client"
            if self.radioButton_2.isChecked():
                settings["Settings"]["JavaSettings"]["Java"]["LaunchMode"] = "server"
    
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
        
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        self.horizontalLayout.addItem(self.horizontalSpacer)
        
        self.verticalLayout.addWidget(self.frame)
        
        self.stackedWidget = QStackedWidget(self)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.addWidget(self.page)
        self.stackedWidget.addWidget(self.page_2)
        
        self.verticalLayout.addWidget(self.stackedWidget)
        
        self.retranslateUi()
        #
        # QMetaObject.connectSlotsByName(Form)
    
    # setupUi
    
    def retranslateUi(self):
        self.pushButton.setText(self.tr("SettingsPage.pushButton.Text"))
        self.pushButton_2.setText(self.tr("SettingsPage.pushButton_2.Text"))
    
    # retranslateUi
    
    def update_page(self, btn):
        self.stackedWidget.setCurrentWidget(self.pages[btn])


class AboutPage(QFrame):
    def __init__(self, parent):
        super().__init__(parent)


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
        self.bottomPanel = Panel(self)
        self.horizontalLayout = QHBoxLayout(self.bottomPanel)
        self.CancelButton = PushButton(self.bottomPanel)
        self.horizontalLayout.addWidget(self.CancelButton)
        self.horizontalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.OKButton = PushButton(self.bottomPanel)
        self.horizontalLayout.addWidget(self.OKButton)
        self.verticalLayout.addWidget(self.bottomPanel)
        self.retranslateUI()
    
    def retranslateUI(self):
        self.label.setText(self.tr("OfflinePlayerCreationDialogue.label.Text"))
        self.CancelButton.setText(self.tr("OfflinePlayerCreationDialogue.CancelButton.Text"))
        self.OKButton.setText(self.tr("OfflinePlayerCreationDialogue.OKButton.Text"))
    
    def setPlayer(self):
        global player
        player = create_offline_user(self.playernameLineEdit.text(), player.player_hasMC)


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
        self.leftUserIcon.setIcon(QIcon("user_icon-black.svg"))
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
        self.UserIcon.setIcon(QIcon("user_icon-black.svg"))
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
        self.rightUserIcon.setIcon(QIcon("user_icon-black.svg"))
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
        
        def tempfun(elf):
            if len(self.user_datas) > 0:
                current_user = self.user_datas[self.current_user]
                self.UserIcon.setText(
                    self.tr("UserPage.UserDataFormat.Text").format(current_user.player_name,
                                                                   current_user.player_accountType[1],
                                                                   current_user.player_hasMC))
            else:
                self.UserIcon.setText(self.tr("UserPage.UserIconNoUser.Text"))
        
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
        self.leftUserIcon.setIcon(QIcon(f"user_icon-{'black' if getTheme() == Theme.Light else 'white'}.svg"))
        self.UserIcon.setIcon(QIcon(f"user_icon-{'black' if getTheme() == Theme.Light else 'white'}.svg"))
        self.rightUserIcon.setIcon(QIcon(f"user_icon-{'black' if getTheme() == Theme.Light else 'white'}.svg"))
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


class MainWindow(RoundedWindow):
    def __init__(self):
        super().__init__()
        self.resize(800, 600)
        self.setWindowIcon(QIcon("CMCL_icon.svg"))
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
        self.topWidget.addItem(self.HomePage, "Home.svg", self.tr("MainWindow.HomePage.Text"))
        self.DownloadPage = DownloadPage(self)
        self.topWidget.addItem(self.DownloadPage, "Download.svg", self.tr("MainWindow.DownloadPage.Text"))
        self.SettingsPage = SettingsPage(self)
        self.topWidget.addItem(self.SettingsPage, "Settings.svg", self.tr("MainWindow.SettingsPage.Text"))
        self.AboutPage = AboutPage(self)
        self.topWidget.addItem(self.AboutPage, "About.svg", self.tr("MainWindow.AboutPage.Text"))
        self.UserPage = UserPage(self)
        self.topWidget.addItem(self.UserPage, "user_icon-black.svg", self.tr("MainWindow.UserPage.Text"),
                               pos=NavigationPanel.NavigationItemPosition.Right)
        self.topWidget.addButton("auto_black.svg", "", selectable=False, pressed=self.toggle_theme,
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
        elif getTheme() == Theme.Dark:
            setTheme(Theme.Light)
        for i in QGuiApplication.allWindows():
            i.requestUpdate()
    
    def updateIcon(self):
        if self.topWidget.button("5"):
            self.topWidget.button("5").setIcon(
                QIcon(f"user_icon-{'black' if getTheme() == Theme.Light else 'white'}.svg"))
        if self.topWidget.button("6"):
            self.topWidget.button("6").setIcon(QIcon(f"auto_{'black' if getTheme() == Theme.Light else 'white'}.svg"))
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


class LoggingWindow(RoundedWindow):
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
                    (r"\[.+\]:", 0, "state"),
                    (string, 0, "string"),
                    # (r"([^.]-.+\s|[^.]--.+\s|[^.]\"-.+\"|[^.]\'--.+\')", 0, "command"),
                    (r"http[s]?://.+", 0, "url")
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
                "__builtins__": {i: eval(i) for i in dir(__builtins__) if i not in ["exec", "__import__"]},
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
                "__builtins__": {i: eval(i) for i in dir(__builtins__) if i not in ["exec", "__import__"]}
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
        self.setWindowIcon(QIcon("CMCL_icon.svg"))
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
        # self.inputtext.setToolTip("Enter command below and press 'Return' to execute command.")
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
    if data:
        player.player_name = data.player_name
        player.player_uuid = data.player_uuid
        player.player_accessToken = data.player_accessToken
        player.player_hasMC = data.player_hasMC


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
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
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
            }
        }
    }
app = QApplication(sys.argv)
app.setFont(QFont("Harmony OS Sans SC"))
font_id = QFontDatabase.addApplicationFont("Unifont 13.0.01.ttf")
if font_id != -1:
    font_families = QFontDatabase.applicationFontFamilies(font_id)
    if font_families:
        font = QFont(font_families[0])
        app.setFont(font)
player = create_online_player(None, None, None, False)

translator = QTranslator()
translator.load("CMCL_zh-cn.qm")
app.installTranslator(translator)
# player = LittleSkinPlayer("chengwm", "random", "random",
#                           "MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEArGcNOOFIqLJSqoE3u0hj\ntOEnOcET3wj9Drss1BE6sBqgPo0bMulOULhqjkc/uH/wyosYnzw3xaazJt87jTHh\nJ8BPMxCeQMoyEdRoS3Jnj1G0Kezj4A2b61PJJM1DpvDAcqQBYsrSdpBJ+52MjoGS\nvJoeQO5XUlJVQm21/HmJnqsPhzcA6HgY71RHYE5xnhpWJiPxLKUPtmt6CNYUQQoS\no2v36XWgMmLBZhAbNOPxYX+1ioxKamjhLO29UhwtgY9U6PWEO7/SBfXzyRPTzhPV\n2nHq7KJqd8IIrltslv6i/4FEM81ivS/mm+PN3hYlIYK6z6Ymii1nrQAplsJ67OGq\nYHtWKOvpfTzOollugsRihkAG4OB6hM0Pr45jjC3TIc7eO7kOgIcGUGUQGuuugDEz\nJ1N9FFWnN/H6P9ukFeg5SmGC5+wmUPZZCtNBLr8o8sI5H7QhK7NgwCaGFoYuiAGL\ngz3k/3YwJ40BbwQayQ2gIqenz+XOFIAlajv+/nyfcDvZH9vGNKP9lVcHXUT5YRnS\nZSHo5lwvVrYUrqEAbh/zDz8QMEyiujWvUkPhZs9fh6fimUGxtm8mFIPCtPJVXjeY\nwD3Lvt3aIB1JHdUTJR3eEc4eIaTKMwMPyJRzVn5zKsitaZz3nn/cOA/wZC9oqyEU\nmc9h6ZMRTRUEE4TtaJyg9lMCAwEAAQ==",
#                           "https://littleskin.cn/api/yggdrasil", True)
# setTheme(Theme.Dark)
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
