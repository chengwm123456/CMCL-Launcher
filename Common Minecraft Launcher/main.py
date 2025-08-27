# -*- coding: utf-8 -*-
"""
"Common Minecraft Launcher" started time: 1693310591 (folder created time)
|-time.struct_time(tm_year=2023, tm_mon=8, tm_mday=29, tm_hour=20, tm_min=3, tm_sec=11, tm_wday=1, tm_yday=241, tm_isdst=0)
|-2023/08/29 20:03:11, 周二（Tuesday, Tues.）, 八月二十九日, 时区: 中国标准时间(UTC+8), 一年的第241天
main.py started time: 1693310592 (main.py created time)
|-time.struct_time(tm_year=2023, tm_mon=8, tm_mday=29, tm_hour=20, tm_min=3, tm_sec=12, tm_wday=1, tm_yday=241, tm_isdst=0)
|-2023/08/29 20:03:12, 周二（Tuesday, Tues.）, 八月二十九日, 时区: 中国标准时间(UTC+8), 一年的第241天
"""
import cProfile
from contextlib import redirect_stdout, redirect_stderr

import base64
import datetime
import sys
import traceback
import re
import os
import subprocess
import webbrowser

from CMCLWidgets import *
from PyQt6.QtWebEngineWidgets import QWebEngineView

from CMCLCore.Launch import LaunchMinecraft
from CMCLCore.Login import MicrosoftPlayerLogin
from CMCLCore.Player import create_online_player, create_offline_player, MicrosoftPlayer
from CMCLCore.GetVersion import (GetVersionsByIterDirectory, GetVersionsByMojangAPI,
                                 GetMinecraftClientDownloadUrl, GetMinecraftServerDownloadUrl)
from CMCLCore.CMCLGameDownloading import DownloadMinecraft
from CMCLCore.GetOperationSystem import GetOperationSystemName

import requests

from CMCLModding.GetMods import GetMods, ListModVersions, GetOneMod
from CMCLModding.DownloadMods import DownloadMod

from CMCLSaveEditing.LevelDat import LoadData
import nbtlib

import resources
from launcherConfig import *

CMCLVersion = ("AlphaDev-25002", "Alpha Development-25002")
minecraft_path = Path(".")

fixedFontList = ["Jetbrains Mono", "Consolas", "Ubuntu", "Monospace", "HarmonyOS Sans SC"]
fixedFont = QFont(fixedFontList)
fixedFont.setHintingPreference(QFont.HintingPreference.PreferFullHinting)

themeColourDefines = {
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
                True: (255, 150, 220)
            },
            ColourRole.Border: {
                False: (215, 220, 229),
                True: (255, 150, 209)
            }
        },
        Theme.Dark: {
            ColourRole.Background: {
                False: (67, 67, 67),
                True: (255, 142, 193),
            },
            ColourRole.Border: {
                False: (134, 143, 150),
                True: (255, 79, 200)
            }
        }
    },
    "PresetPurple": {
        Theme.Light: {
            ColourRole.Background: {
                False: (253, 253, 253),
                True: (190, 150, 255)
            },
            ColourRole.Border: {
                False: (215, 220, 229),
                True: (163, 143, 255)
            }
        },
        Theme.Dark: {
            ColourRole.Background: {
                False: (67, 67, 67),
                True: (151, 142, 208),
            },
            ColourRole.Border: {
                False: (134, 143, 150),
                True: (107, 79, 208)
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

languagesCodeMapping = {
    "zh-cn": "简体中文（中国大陆）",
    "zh-hk": "繁體中文（中國香港/中國澳門特別行政區）",
    "zh-tw": "繁體中文（中國台灣）",
    "lzh": "文言（華夏）",
    "en-us": "English (United States)",
    "en-gb": "English (United Kingdom)",
}


class AcrylicBackground(QWidget):
    def __init__(self, parent, tintColour, luminosityColour=QColor(255, 255, 255, 0), blurRadius=10, noiseOpacity=0.03):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.tintColour = tintColour
        self.luminosityColour = luminosityColour
        self.blurRadius = blurRadius
        self.noiseOpacity = noiseOpacity
        self.img = QPixmap()
        self.blurredImg = QPixmap()
    
    def setTintColour(self, colour):
        self.tintColour = colour
    
    def setLuminosityColour(self, colour):
        self.luminosityColour = colour
    
    def grabBehind(self):
        image = self.window().grab(QRect(self.mapTo(self.window(), QPoint(0, 0)),
                                         self.mapTo(self.window(), QPoint(self.width(), self.height()))))
        self.img = image
        scene = QGraphicsScene()
        item = QGraphicsPixmapItem()
        item.setPixmap(self.img)
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(self.blurRadius)
        item.setGraphicsEffect(blur)
        scene.addItem(item)
        self.blurredImg = QPixmap(self.size())
        self.blurredImg.fill(Qt.GlobalColor.transparent)
        ptr = QPainter(self.blurredImg)
        scene.render(ptr, QRectF(self.blurredImg.rect()), QRectF(self.blurredImg.rect()))
        ptr.end()
    
    def paintEvent(self, a0):
        brush = self.__createTexture()
        
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.blurredImg.scaled(self.size()))
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
        class OpacityAnimation(QVariantAnimation):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.valueChanged.connect(self.__updateOpacity)
            
            def __updateOpacity(self, value):
                op = QGraphicsOpacityEffect(self.parent())
                op.setOpacity(self.currentValue() / 100)
                if self.currentValue() == self.endValue() and self.currentValue():
                    self.parent().setGraphicsEffect(None)
                    return
                self.parent().setGraphicsEffect(op)
        
        lastWidget = self.currentWidget()
        if lastWidget == w:
            return
        self.setProperty("currentIndex", self.indexOf(w))
        lastWidget.show()
        w.stackUnder(lastWidget)
        w.raise_()
        ani11 = OpacityAnimation(lastWidget)
        ani11.setStartValue(100)
        ani11.setEndValue(0)
        ani11.setDuration(450)
        ani11.setEasingCurve(QEasingCurve.Type.OutQuad)
        ani11.finished.connect(lastWidget.hide)
        ani11.start()
        currentWidget = w
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
        QTimer.singleShot(500, lambda: super(AnimatedStackedWidget, self).setCurrentWidget(w))


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
            self.animation = None
            
            self.error = False
        
        def paintEvent(self, a0):
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            gradient = QConicalGradient(QRectF(self.rect()).center(), self.property("animationValue") % 360)
            gradient.setColorAt(
                0.0,
                self.adjustRed(
                    getBorderColour(is_highlight=True),
                    50 if self.error else 0
                )
            )
            gradient.setColorAt(
                1.0,
                self.adjustRed(
                    getBackgroundColour(is_highlight=True),
                    50 if self.error else 0
                )
            )
            painter.setPen(Qt.GlobalColor.transparent)
            painter.setBrush(QBrush(gradient))
            painter.drawEllipse(self.rect())
        
        @staticmethod
        def adjustRed(colour, percent=25):
            percent /= 100
            percent = max(0, min(percent, 1))
            r, g, b = Colour(colour)
            r = int((r * (1 - percent)) + (255 * percent))
            g = int(g * (1 - percent))
            b = int(b * (1 - percent))
            return Colour(r, g, b)
        
        def setError(self, isError=True):
            self.error = isError
            if isError:
                self.stop()
            else:
                self.start()
        
        def stop(self):
            if self.animation:
                self.animation.stop()
            
            if self.property("animationValue") % 360 != 0:
                animation = QPropertyAnimation(self, b"animationValue", self)
                animation.setStartValue(self.property("animationValue"))
                animation.setEndValue(self.animation.startValue() + 360)
                animation.setDuration(1000)
                animation.setEasingCurve(QEasingCurve.Type.OutQuad)
                animation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        
        def start(self):
            if self.error:
                return
            self.setProperty("animationValue", 0)
            if self.animation:
                self.animation.stop()
            
            self.animation = QPropertyAnimation(self, b"animationValue", self)
            self.animation.setStartValue(self.property("animationValue"))
            self.animation.setEndValue(self.animation.startValue() + 360)
            self.animation.setDuration(1000)
            self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
            self.animation.setLoopCount(-1)
            self.animation.start()
            self.error = False
        
        def showEvent(self, a0):
            super().showEvent(a0)
            self.start()
    
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
                QRect(self.__statusLabel.x() + self.__statusLabel.width() + 1,
                      int(self.height() / 2 - (self.__reloadButton.height() / 2)) + 96 + 30,
                      self.__reloadButton.width(), self.__reloadButton.height()))
        except AttributeError:
            pass
        self.raise_()
        return super().event(e)
    
    def paintEvent(self, a0):
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        if not self.__centreAnimation.error:
            self.setStyleSheet(
                f"background: rgb({str(getBackgroundColour(is_tuple=True)).strip('()')});")
        else:
            self.setStyleSheet(
                f"background: rgb({str(tuple(self.__centreAnimation.adjustRed(getBackgroundColour(), 50))).strip('()')});")
        return super().paintEvent(a0)
    
    def __updateText(self):
        self.__counter += 1
        self.__statusLabel.setText("加载中" + "." * (self.__counter % 7))
    
    def start(self, ani=True):
        self.__centreAnimation.setFixedSize(96, 96)
        self.__centreAnimation.setError(False)
        self.__statusLabel.setText("加载中")
        self.__reloadButton.hide()
        self.__reloadButton.setDown(False)
        if ani:
            self.setStyleSheet("background: transparent")
            self.TransparencyAnimation(self, "in").start()
            self.SizingAnimation(self.__centreAnimation, "in").start()
        else:
            self.setStyleSheet(
                f"background: rgb({str(getBackgroundColour(is_tuple=True)).strip('()')});")
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
                self.__statusLabel.setText("已加载完成")
            else:
                self.setStyleSheet(
                    f"background: rgb({str(tuple(self.__centreAnimation.adjustRed(getBackgroundColour(), 50))).strip('()')});")
                self.__statusLabel.setText("加载失败，请重试")
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
        except RuntimeError:
            pass


class LoginWindow(MaskedDialogue):
    class LoginThread(QThread):
        loginFinished = pyqtSignal()
        
        def __init__(self, token, parent=None):
            super().__init__(parent)
            self.token = token
        
        def run(self):
            try:
                datas = login_user(bytes(self.token, encoding="utf-8"))
                updatePlayer(datas)
            except:
                traceback.print_exc()
            self.loginFinished.emit()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("登录")
        self.resize(800, 600)
        self.view = QWebEngineView(self)
        self.view.show()
        self.view.load(QUrl(
            "https://login.live.com/oauth20_authorize.srf?client_id=00000000402b5328&response_type=code&scope=service%3A%3Auser.auth.xboxlive.com%3A%3AMBI_SSL&redirect_uri=https%3A%2F%2Flogin.live.com%2Foauth20_desktop.srf"))
        self.view.urlChanged.connect(self.assert_url)
        self.view.loadStarted.connect(self.loadStarted)
        self.view.loadFinished.connect(self.loadFinished)
        self.view.page().profile().setHttpAcceptLanguage(currentLanguage)
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


class HomePage(QFrame):
    class LaunchThread(QThread):
        launchFinished = pyqtSignal(tuple)
        
        def __init__(self, parent=None, version=None, jar_path=None):
            super().__init__(parent)
            self.version = version
            self.jar_path = jar_path
        
        def run(self):
            cfg = {}
            syncWithDefault = True
            if self.jar_path:
                version_path = Path(self.jar_path).parent
                cfg_path = Path(version_path / "version.cfg")
                if not cfg_path.exists():
                    createVersionConfigFile(cfg_path, self.version)
                cfg = json.loads(Path(cfg_path).read_text(encoding="utf-8"))
                syncWithDefault = cfg["LaunchConfig"]["SyncWithDefault"]
            
            if self.jar_path:
                curVerDir = self.jar_path.parent
            else:
                curVerDir = minecraft_path / "versions" / self.version
            
            jsonFile = json.loads(
                Path(curVerDir / f"{self.version}.json").read_text(encoding="utf-8"))
            
            seperationMode = settings["LaunchSettings"]["VersionSeperation"]
            match seperationMode:
                case 0:
                    seperationRequired = False
                case 1:
                    seperationRequired = True
                case 3:
                    versionType = jsonFile["type"]
                    if versionType == "release":
                        seperationRequired = False
                    else:
                        seperationRequired = True
                case _:
                    seperationRequired = False
            
            if seperationRequired:
                if seperationMode == 3:
                    saves = curVerDir / "saves"
                    saves_dest = minecraft_path / f".{jsonFile['type']}.saves"
                    
                    date = datetime.datetime.fromisoformat(jsonFile["releaseDate"])
                    if date.month == 4 and date.day == 1:
                        saves_dest = minecraft_path / f"{self.version}.saves"
                    
                    if saves.exists():
                        for save in saves.iterdir():
                            save.rename(saves_dest / save.name)
                        saves.rmdir()
                    
                    saves.symlink_to(saves_dest)
                else:
                    if os.path.islink((curVerDir / "saves").absolute()):
                        (curVerDir / "saves").rmdir()
                    if seperationMode == 1:
                        (curVerDir / "saves").mkdir(parent=True, exist_ok=True)
                        
                        if versionType == "release":
                            savesDir = (minecraft_path / f"saves")
                        else:
                            savesDir = (minecraft_path / f".{versionType}.saves")
                        for save in savesDir.iterdir():
                            version = str(nbtlib.load(save / "level.dat")["Data"].get("Version", {}).get("Name"))
                            versionName = jsonFile["id"]
                            if version == versionName:
                                save.rename(curVerDir / "saves" / save.name)
            
            if seperationRequired:
                if settings["LaunchSettings"]["VersionSeperationConfig"]["ShareVersionOptions"]:
                    if not os.path.islink((curVerDir / "options.txt").absolute()):
                        if not (minecraft_path / "options.txt").exists():
                            if (curVerDir / "options.txt").exists():
                                (curVerDir / "options.txt").rename(minecraft_path / "options.txt")
                            else:
                                (minecraft_path / "options.txt").touch(exist_ok=True)
                        (curVerDir / "options.txt").unlink(missing_ok=True)
                        (curVerDir / "options.txt").symlink_to(minecraft_path / "options.txt")
                else:
                    if os.path.islink((curVerDir / "options.txt").absolute()):
                        (curVerDir / "options.txt").unlink(missing_ok=True)
                        if (minecraft_path / "options.txt").exists():
                            (curVerDir / "options.txt").write_bytes((minecraft_path / "options.txt").read_bytes())
                
                if settings["LaunchSettings"]["VersionSeperationConfig"]["ShareVersionResourcePacks"]:
                    if not os.path.islink((curVerDir / "resourcepacks").absolute()):
                        if not (minecraft_path / "resourcepacks").exists():
                            (minecraft_path / "resourcepacks").mkdir(parents=True, exist_ok=True)
                        if (curVerDir / "resourcepacks").exists():
                            for resourcepack in (curVerDir / "resourcepacks").iterdir():
                                resourcepack.rename(minecraft_path / "resourcepacks" / resourcepack.name)
                        if (curVerDir / "resourcepacks").exists():
                            (curVerDir / "resourcepacks").rmdir()
                        (curVerDir / "resourcepacks").symlink_to(minecraft_path / "resourcepacks", True)
                else:
                    if os.path.islink((curVerDir / "resourcepacks").absolute()):
                        (curVerDir / "resourcepacks").rmdir()
            
            result = LaunchMinecraft(
                minecraft_path, self.version,
                settings["LaunchSettings"]["Java"]["JavaPath"],
                CMCLVersion[0], "CMCL",
                None, None,
                settings["LaunchSettings"]["Java"]["JVM"]["JVMArguments"]["Arguments"],
                settings["LaunchSettings"]["ExtraGameCommand"],
                currentPlayer,
                game_seperation=seperationRequired
            )
            self.launchFinished.emit(result)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.topPanel = Panel(self)
        self.horizontalLayout = QHBoxLayout(self.topPanel)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.horizontalLayout.addItem(self.horizontalSpacer)
        self.launchButton = PushButton(self.topPanel)
        self.launchButton.setMinimumWidth(60)
        self.launchButton.setMinimumHeight(32)
        self.launchButton.pressed.connect(self.launch)
        self.horizontalLayout.addWidget(self.launchButton)
        self.selectVersionButton = PushButton(self.topPanel)
        self.selectVersionButton.setMinimumWidth(60)
        self.selectVersionButton.setMinimumHeight(32)
        self.horizontalLayout.addWidget(self.selectVersionButton)
        self.reloadButton = ToolButton(self.topPanel)
        self.reloadButton.setFixedSize(QSize(32, 32))
        self.reloadButton.setIcon(QIcon(""))
        self.horizontalLayout.addWidget(self.reloadButton)
        self.selectNewMinecraftDirButton = PushButton(self.topPanel)
        self.selectNewMinecraftDirButton.setMinimumWidth(60)
        self.selectNewMinecraftDirButton.setMinimumHeight(32)
        self.selectNewMinecraftDirButton.pressed.connect(self.selectNewMinecraftDir)
        self.horizontalLayout.addWidget(self.selectNewMinecraftDirButton)
        self.horizontalSpacer_2 = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.horizontalLayout.addItem(self.horizontalSpacer_2)
        
        self.version = None
        self.versionAliasConv = {}
        self.displayVersion = None
        
        app.registerRetranslateFunction(self.retranslateUI)
        self.retranslateUI()
        self.updateVersionList()
        self.updateIcon()
    
    def retranslateUI(self):
        self.launchButton.setText("启动")
        self.launchButton.setToolTip(f"启动：{self.displayVersion}" if self.displayVersion else "暂未选择版本")
        self.selectVersionButton.setText(self.displayVersion if self.displayVersion else "选择版本")
        self.selectVersionButton.setToolTip(
            f"当前版本：{self.displayVersion}" if self.displayVersion else "暂未选择版本")
        self.reloadButton.setToolTip("重新加载版本列表")
        self.selectNewMinecraftDirButton.setText("选择文件夹")
        self.selectNewMinecraftDirButton.setToolTip(f"当前文件夹：{str(minecraft_path)}")
    
    def updateVersionList(self):
        menu = QMenu(self.selectVersionButton)
        menu.setStyleSheet("background: transparent;")
        listWidget = ListWidget(menu)
        listWidget.itemDoubleClicked.connect(lambda x: (self.selectVersion(x.text()), menu.close()))
        menu.addAction(QAction(""))
        
        self.versionAliasConv.clear()
        
        versionList = GetVersionsByIterDirectory(minecraft_path)
        if versionList:
            for version in versionList:
                versionConfig = Path(version[1] / "version.cfg")
                versionName = version[0]
                if versionConfig.exists():
                    cfg = json.loads(Path(versionConfig).read_text(encoding="utf-8"))
                    versionName = cfg["VersionAlias"]
                    self.versionAliasConv[versionName] = version[0]
                item = QListWidgetItem(versionName, listWidget)
                item.setSizeHint(QSize(0, 24))
                listWidget.addItem(item)
            if not self.version:
                self.version = self.versionAliasConv.get(versionList[0][0], versionList[0][0])
                self.displayVersion = versionList[0][0]
            else:
                if self.version not in map(lambda x: x[0], versionList):
                    self.version = self.versionAliasConv.get(versionList[0][0], versionList[0][0])
                    self.displayVersion = versionList[0][0]
        else:
            self.version = None
            self.displayVersion = None
            # menu.addAction("暂无版本")
        
        # openVersionFolder = QAction(menu)
        # openVersionFolder.setText("打开版本文件夹")
        # openVersionFolder.triggered.connect(lambda: None)
        # menu.addAction(openVersionFolder)
        
        listWidget.adjustSize()
        menu.setFixedSize(listWidget.size())
        
        self.selectVersionButton.setMenu(menu)
        
        self.retranslateUI()
    
    def selectVersion(self, version):
        self.version = self.versionAliasConv.get(version, version)
        self.displayVersion = version
        self.retranslateUI()
        self.updateVersionList()
    
    def launch(self):
        self.preLaunch()
        self.launchFunction()
    
    def preLaunch(self):
        self.launchButton.setEnabled(False)
    
    def launchFunction(self):
        if self.version:
            launchThread = self.LaunchThread(self, self.version)
            launchThread.start()
            launchThread.launchFinished.connect(self.postLaunch)
    
    def postLaunch(self, result):
        self.launchButton.setEnabled(True)
        print(result)
    
    def selectNewMinecraftDir(self):
        global minecraft_path
        self.selectNewMinecraftDirButton.setDown(False)
        dirDialogue = QFileDialog.getExistingDirectory(self, "选择游戏文件夹", str(minecraft_path))
        if dirDialogue:
            minecraft_path = Path(dirDialogue).absolute()
            settings["LauncherSettings"]["MinecraftPath"] = str(minecraft_path.absolute())
            self.updateVersionList()
    
    def postToggleTheme(self):
        self.updateIcon()
    
    def updateIcon(self):
        colour = "black" if getTheme() == Theme.Light else "white"
        self.reloadButton.setIcon(QIcon(f":/Reload-{colour}.svg"))
    
    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        
        self.topPanel.move(QPoint(15, 15))
        
        sizeAnimation = QPropertyAnimation(self.topPanel, b"size", self)
        sizeAnimation.setStartValue(self.topPanel.size())
        sizeAnimation.setEndValue(QSize(self.width() - 30, 54))
        sizeAnimation.setDuration(100)
        sizeAnimation.setEasingCurve(QEasingCurve.Type.OutQuad)
        sizeAnimation.start()


class DownloadPage(QFrame):
    class DownloadVanilla(QFrame):
        class GetVersionThread(QThread):
            gettingFinished = pyqtSignal(dict)
            
            def run(self):
                try:
                    response = GetVersionsByMojangAPI(returns="RETURN_JSON")
                    if response:
                        self.gettingFinished.emit({"status": 0, "result": response})
                    else:
                        self.gettingFinished.emit({"status": 1, "result": None})
                except:
                    self.gettingFinished.emit({"status": 1, "result": None})
        
        class DownloadOptions(AcrylicBackground):
            frameClosed = pyqtSignal()
            
            class DownloadVersionThread(QThread):
                def __init__(self, parent, minecraft_pth=minecraft_path, version=None):
                    super().__init__(parent)
                    self.minecraft_path = minecraft_pth
                    self.version = version
                
                def run(self):
                    DownloadMinecraft(self.minecraft_path, self.version, self.version)
                    createVersionConfigFile(self.minecraft_path / "versions" / self.version, self.version, self.version)
            
            class DownloadConfirmation(MaskedDialogue):
                def __init__(self, parent, version):
                    super().__init__(parent)
                    self.version = version
                    
                    self.mainLayout = QVBoxLayout(self)
                    
                    self.label = Label(self)
                    self.mainLayout.addWidget(self.label)
                
                def retranslateUI(self):
                    self.label.setText(
                        f"确定下载 {self.version} 吗？\n这会覆盖当前的下载，如果你不想覆盖当前的下载，可以改一下版本文件夹名")
            
            def __init__(self, parent, version=None):
                super().__init__(parent, getBackgroundColour(), QColor(0, 0, 255, 200), 10)
                self.version = version
                
                self.mainLayout = QVBoxLayout(self)
                
                self.topPanel = Panel(self)
                self.mainLayout.addWidget(self.topPanel)
                
                self.horizontalLayout = QHBoxLayout(self.topPanel)
                
                self.exitButton = CloseButton(self.topPanel)
                self.exitButton.setFixedSize(QSize(32, 32))
                self.exitButton.pressed.connect(self.closeFrame)
                self.horizontalLayout.addWidget(self.exitButton)
                
                self.groupBox1Btn = PushButton(self)
                self.groupBox1Btn.setCheckable(True)
                self.groupBox1Btn.setChecked(True)
                self.groupBox1Btn.setAutoExclusive(True)
                self.horizontalLayout.addWidget(self.groupBox1Btn)
                
                self.groupBox2Btn = PushButton(self)
                self.groupBox2Btn.setCheckable(True)
                self.groupBox2Btn.setAutoExclusive(True)
                self.horizontalLayout.addWidget(self.groupBox2Btn)
                
                self.groupBox3Btn = PushButton(self)
                self.groupBox3Btn.setCheckable(True)
                self.groupBox3Btn.setAutoExclusive(True)
                self.horizontalLayout.addWidget(self.groupBox3Btn)
                
                self.horizontalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                self.horizontalLayout.addItem(self.horizontalSpacer)
                
                self.scrollArea = ScrollArea(self)
                self.mainLayout.addWidget(self.scrollArea, 1)
                
                self.scrollAreaWidgetContents = QWidget()
                self.verticalLayout = QVBoxLayout(self.scrollAreaWidgetContents)
                
                self.groupBox = GroupBox(self)
                self.verticalLayout.addWidget(self.groupBox)
                
                self.form_1 = QFormLayout(self.groupBox)
                
                self.form_1_Label = Label(self.groupBox)
                self.form_1.setWidget(0, QFormLayout.ItemRole.LabelRole, self.form_1_Label)
                
                self.form_1_PushButton = PushButton(self.groupBox)
                self.form_1.setWidget(0, QFormLayout.ItemRole.FieldRole, self.form_1_PushButton)
                
                self.form_2_Label = Label(self.groupBox)
                self.form_1.setWidget(1, QFormLayout.ItemRole.LabelRole, self.form_2_Label)
                
                self.form_2_PushButton = PushButton(self.groupBox)
                self.form_1.setWidget(1, QFormLayout.ItemRole.FieldRole, self.form_2_PushButton)
                
                self.groupBox_2 = GroupBox(self.scrollAreaWidgetContents)
                self.verticalLayout.addWidget(self.groupBox_2)
                
                self.form_2 = QFormLayout(self.groupBox_2)
                
                self.form_3_Label = Label(self.groupBox_2)
                self.form_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.form_3_Label)
                
                self.form_3_LineEdit = LineEdit(self.groupBox_2)
                self.form_3_LineEdit.setPlaceholderText(str(minecraft_path.absolute()))
                self.form_3_LineEdit.setText(str(minecraft_path.absolute()))
                self.form_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.form_3_LineEdit)
                
                self.form_4_Label = Label(self.groupBox_2)
                self.form_2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.form_4_Label)
                
                self.form_4_LineEdit = LineEdit(self.groupBox_2)
                self.form_4_LineEdit.setPlaceholderText(str(self.version))
                self.form_4_LineEdit.setText(str(self.version))
                self.form_2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.form_4_LineEdit)
                
                self.groupBox_3 = GroupBox(self)
                self.verticalLayout.addWidget(self.groupBox_3)
                
                self.gridLayout = QGridLayout(self.groupBox_3)
                
                self.wikiVersionPage = CommandLinkButton(self.groupBox_3)
                self.wikiVersionPage.pressed.connect(self.openWiki)
                self.gridLayout.addWidget(self.wikiVersionPage, 0, 0)
                
                self.clientJarURL = CommandLinkButton(self.groupBox_3)
                self.clientJarURL.pressed.connect(self.openClientURL)
                self.gridLayout.addWidget(self.clientJarURL, 1, 0)
                
                self.serverJarURL = CommandLinkButton(self.groupBox_3)
                self.serverJarURL.pressed.connect(self.openServerURL)
                self.gridLayout.addWidget(self.serverJarURL, 1, 1)
                
                self.verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
                self.verticalLayout.addItem(self.verticalSpacer)
                
                self.scrollArea.setWidget(self.scrollAreaWidgetContents)
                self.scrollArea.setWidgetResizable(True)
                
                self.scrollArea.verticalScrollBar().valueChanged.connect(self.updateTopSelections)
                
                self.startDownloadBtn = PushButton(self.scrollAreaWidgetContents)
                self.startDownloadBtn.pressed.connect(self.downloadVersion)
                self.startDownloadBtn.pressed.connect(self.closeFrame)
                self.mainLayout.addWidget(self.startDownloadBtn)
                
                app.registerRetranslateFunction(self.retranslateUI)
                self.retranslateUI()
            
            def retranslateUI(self):
                self.groupBox1Btn.setText("版本")
                self.groupBox2Btn.setText("下载设置")
                self.groupBox3Btn.setText("其他链接")
                self.groupBox.setTitle("版本")
                self.form_1_Label.setText("下载版本")
                self.form_1_PushButton.setText(f"{self.version}（单击重新选择版本）")
                self.form_2_Label.setText("模组加载器")
                self.form_2_PushButton.setText("点击选择模组加载器")
                self.groupBox_2.setTitle("下载设置")
                self.form_3_Label.setText("下载路径")
                self.form_3_LineEdit.setToolTip("""注意：这不是版本 jar 文件的下载路径。
比如说你填的是：
① G:\\.minecraft
② /home/mc/.minecraft
jar 下载位置在：
① G:\\.minecraft\\versions\\{当前版本}\\{当前版本}.jar
② /home/mc/.minecraft/versions/{当前版本}/{当前版本}.jar
若存在与下载版本同名的文件夹，启动器会在下载前询问是否继续下载。""")
                self.form_4_Label.setText("版本文件夹名")
                self.form_4_LineEdit.setToolTip("默认是当前下载的版本，如果遇到版本已存在可以尝试修改此项")
                self.groupBox_3.setTitle("其他链接")
                self.wikiVersionPage.setText(f"Minecraft Wiki 上的 {self.version}")
                self.clientJarURL.setText("Minecraft 客户端下载链接")
                self.serverJarURL.setText("Minecraft 服务端下载链接")
                self.startDownloadBtn.setText("下载")
            
            def updateTopSelections(self, value):
                if value >= self.groupBox_3.y():
                    self.groupBox3Btn.setChecked(True)
                elif value >= self.groupBox_2.y():
                    self.groupBox2Btn.setChecked(True)
                else:
                    self.groupBox1Btn.setChecked(True)
            
            def downloadVersion(self):
                thread = self.DownloadVersionThread(
                    self.window(),
                    Path(self.form_3_LineEdit.text() or minecraft_path),
                    self.version
                )
                thread.start()
            
            def openWiki(self):
                webbrowser.open(f"https://zh.minecraft.wiki/w/{self.version}")
            
            def openClientURL(self):
                webbrowser.open(GetMinecraftClientDownloadUrl(self.version))
            
            def openServerURL(self):
                webbrowser.open(GetMinecraftServerDownloadUrl(self.version))
            
            def closeFrame(self):
                self.frameClosed.emit()
            
            def paintEvent(self, a0):
                self.setTintColour(getBackgroundColour())
                super().paintEvent(a0)
        
        def __init__(self, parent):
            super().__init__(parent)
            self.verticalLayout = QVBoxLayout(self)
            
            self.topSearchPanel = GroupBox(self)
            # self.topSearchPanel.setCheckable(True)
            
            self.verticalLayout.addWidget(self.topSearchPanel)
            self.horizontalLayout = QHBoxLayout(self.topSearchPanel)
            
            self.searchInput = LineEdit(self.topSearchPanel)
            self.searchInput.setMinimumHeight(36)
            self.searchInput.textChanged.connect(self.searchVersions)
            self.searchInput.setClearButtonEnabled(True)
            self.horizontalLayout.addWidget(self.searchInput)
            
            self.versionDisplayTable = TableView(self)
            self.versionDisplayTable.setSelectionMode(QTableView.SelectionMode.SingleSelection)
            self.versionDisplayTable.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            self.versionDisplayTable.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            self.versionDisplayTable.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.versionDisplayTable.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
            self.versionDisplayTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.versionDisplayTable.horizontalHeader().setVisible(True)
            self.versionDisplayTable.verticalHeader().setVisible(False)
            self.versionDisplayTable.doubleClicked.connect(self.openDownloadOptions)
            self.versionData = {}
            self.versionModel = QStandardItemModel(self.versionDisplayTable)
            self.versionDisplayTable.setModel(self.versionModel)
            self.verticalLayout.addWidget(self.versionDisplayTable, 1)
            
            self.loader = LoadingAnimation(self)
            self.loader.addReloadFunction(self.startLoad)
            self.getThread = None
            
            self.downloadOptions = None
            
            app.registerRetranslateFunction(self.retranslateUI)
            self.retranslateUI()
        
        def retranslateUI(self):
            self.topSearchPanel.setTitle("搜索版本")
            self.searchInput.setPlaceholderText("输入版本、类型、日期")
            self.searchInput.setToolTip("""◉ 输入版本：查询版本；
◉ 输入类型：筛选版本类型；
  ◎ release：正式版（如 1.21.8）；
  ◎ snapshot：快照（如 25w21a）；
  ◎ old_beta：远古 Beta 版（如 b1.8.1）；
  ◎ old_alpha：远古 Alpha 版（如 a1.2.6）；
    ◎ classic：Classic 版（如 c0.30_01c）；
    ◎ pre_classic：pre-Classic 版（如 rd-161348）。
  ◎ april_fool：愚人节版本。
◉ 输入日期：查询在该日期发布的版本，格式：\"{}\"；
◉ *输入 latest：
  ◎ latest：最新正式版 + 快照；
  ◎ latest_release：最新正式版；
  ◎ latest_snapshot：最新快照。
注：以上方式均可使用正则表达式（带“*”的必须完整输入），
示例：
◉ \"1\\.14.+\"（版本号）；
◉ \"(old_alpha|old_beta|classic|pre_classic)\"（版本类型）；
◉ \"2024-05-28 .+\"（发布日期）等。
更多正则表达式语法请上网查询，这里不讲述太多。""".format("%Y-%m-%d %H:%M:%S"))
            self.versionModel.setHorizontalHeaderLabels(["版本", "类型", "发布日期"])
        
        def showEvent(self, a0):
            super().showEvent(a0)
            if not self.getThread and not self.versionData:
                self.startLoad()
        
        def startLoad(self, ani=False):
            self.getThread = self.GetVersionThread(self)
            self.getThread.gettingFinished.connect(self.displayVersions)
            self.getThread.start()
            self.loader.start(ani)
        
        def resizeEvent(self, a0):
            super().resizeEvent(a0)
            if self.downloadOptions:
                self.downloadOptions.resize(self.size())
        
        @staticmethod
        def normaliseVersionData(data):
            versions = data["versions"]
            for version in data["versions"]:
                version["releaseTime"] = datetime.datetime.fromisoformat(version["releaseTime"])
                
                versionId = version["id"]
                versionType = version["type"]
                releaseTime = version["releaseTime"]
                if releaseTime.month == 4 and releaseTime.day == 1:
                    versionType = "april_fool"
                if versionId.startswith("c"):
                    versionType = "classic"
                if versionId.startswith("rd-"):
                    versionType = "pre_classic"
                version["type"] = versionType
            data["versions"] = versions
            return data
        
        @staticmethod
        def localiseType(versionType):
            match versionType:
                case "release":
                    versionType = "正式版"
                case "snapshot":
                    versionType = "快照"
                case "old_beta":  # In Chinese, versions earier than 1.0.0 are called as "远古版"
                    versionType = "远古版"
                case "old_alpha":  # In case of requiring this.
                    versionType = "远古版"
                case "april_fool":
                    versionType = "愚人节版"
                case "classic":  # Same as above
                    versionType = "远古版"
                case "pre_classic":  # Same as above
                    versionType = "远古版"
            return versionType
        
        def displayVersions(self, data):
            self.versionModel.clear()
            self.getThread = None
            if not data["status"]:
                self.versionData = self.normaliseVersionData(data["result"])
                self.loader.finish(True, False)
                
                completer = QCompleter(self.searchInput)
                model = QStandardItemModel(completer)
                completer.setModel(model)
                self.searchInput.setCompleter(completer)
                
                self.versionModel.clear()
                row = 0
                for version in self.versionData["versions"]:
                    self.versionModel.setItem(row, 0, QStandardItem(version["id"]))
                    self.versionModel.setItem(row, 1, QStandardItem(self.localiseType(version["type"])))
                    self.versionModel.setItem(row, 2, QStandardItem(
                        version["releaseTime"].astimezone().strftime("%Y-%m-%d %H:%M:%S")
                    ))
                    model.setItem(row, 0, QStandardItem(version["id"]))
                    row += 1
                self.retranslateUI()
            else:
                self.loader.finish(False, True)
        
        def searchVersions(self, text):
            text = text.lower()
            
            latest_release = latest_snapshot = False
            if text.startswith("latest") and "_" in text:
                versionType = text.split("_")[1]
                if versionType:
                    if "release".startswith(versionType):
                        latest_snapshot = True
                    elif "snapshot".startswith(versionType):
                        latest_release = True
            
            try:
                self.versionModel.clear()
                row = 0
                for version in self.versionData["versions"]:
                    if text.startswith("latest"):
                        if latest_release and latest_snapshot:
                            break
                        if version["type"] == "snapshot" and not latest_snapshot:
                            latest_snapshot = True
                            self.versionModel.setItem(row, 0, QStandardItem(version["id"]))
                            self.versionModel.setItem(row, 1, QStandardItem(self.localiseType(version["type"])))
                            self.versionModel.setItem(row, 2, QStandardItem(
                                version["releaseTime"].astimezone().strftime("%Y-%m-%d %H:%M:%S")
                            ))
                            row += 1
                        if version["type"] == "release" and not latest_release:
                            latest_release = True
                            self.versionModel.setItem(row, 0, QStandardItem(version["id"]))
                            self.versionModel.setItem(row, 1, QStandardItem(self.localiseType(version["type"])))
                            self.versionModel.setItem(row, 2, QStandardItem(
                                version["releaseTime"].astimezone().strftime("%Y-%m-%d %H:%M:%S")
                            ))
                            row += 1
                    elif re.match(text, version["id"], re.UNICODE):
                        self.versionModel.setItem(row, 0, QStandardItem(version["id"]))
                        self.versionModel.setItem(row, 1, QStandardItem(self.localiseType(version["type"])))
                        self.versionModel.setItem(row, 2, QStandardItem(
                            version["releaseTime"].astimezone().strftime("%Y-%m-%d %H:%M:%S")
                        ))
                        row += 1
                    elif re.match(text, version["type"], re.UNICODE):
                        self.versionModel.setItem(row, 0, QStandardItem(version["id"]))
                        self.versionModel.setItem(row, 1, QStandardItem(self.localiseType(version["type"])))
                        self.versionModel.setItem(row, 2, QStandardItem(
                            version["releaseTime"].astimezone().strftime("%Y-%m-%d %H:%M:%S")
                        ))
                        row += 1
                    elif re.match(text, version["releaseTime"].astimezone().strftime("%Y-%m-%d %H:%M:%S"), re.UNICODE):
                        self.versionModel.setItem(row, 0, QStandardItem(version["id"]))
                        self.versionModel.setItem(row, 1, QStandardItem(self.localiseType(version["type"])))
                        self.versionModel.setItem(row, 2, QStandardItem(
                            version["releaseTime"].astimezone().strftime("%Y-%m-%d %H:%M:%S")
                        ))
                        row += 1
            except re.error:
                self.versionModel.clear()
                row = 0
            self.retranslateUI()
        
        def openDownloadOptions(self, item):
            match item.column():
                case 0:
                    self.downloadOptions = self.DownloadOptions(self, self.versionModel.item(item.row(), 0).text())
                    self.downloadOptions.frameClosed.connect(self.closeDownloadOptions)
                    rect = self.rect().adjusted(1, 1, -1, -1)
                    self.downloadOptions.setGeometry(rect)
                    self.downloadOptions.grabBehind()
                    self.downloadOptions.move(QPoint(0, self.height()))
                    ani = QPropertyAnimation(self.downloadOptions, b"pos", self)
                    ani.setStartValue(QPoint(0, self.height()))
                    ani.setEndValue(QPoint(0, 0))
                    ani.setKeyValueAt(0.8, QPoint(0, 50))
                    ani.setDuration(500)
                    ani.setEasingCurve(QEasingCurve.Type.OutQuad)
                    ani.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                    self.downloadOptions.show()
                case 1:
                    versionName = self.versionModel.item(item.row(), 0).text()
                    versionType = None
                    for version in self.versionData["versions"]:
                        if version["id"] == versionName:
                            versionType = version["type"]
                            break
                    
                    if versionType:
                        self.searchInput.setText(versionType)
                case 2:
                    releaseDate = self.versionModel.item(item.row(), 2).text()
                    self.searchInput.setText(releaseDate.split()[0])
        
        def closeDownloadOptions(self):
            ani = QPropertyAnimation(self.downloadOptions, b"pos", self)
            ani.setStartValue(QPoint(0, 0))
            ani.setEndValue(QPoint(0, self.height()))
            ani.setKeyValueAt(0.8, QPoint(0, self.height() - 50))
            ani.setDuration(500)
            ani.setEasingCurve(QEasingCurve.Type.OutQuad)
            ani.finished.connect(self.closingFinished)
            ani.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        
        def closingFinished(self):
            self.downloadOptions.close()
            self.downloadOptions.deleteLater()
            self.downloadOptions = None
        
        def reloadVersions(self):
            if self.downloadOptions:
                return
            self.retranslateUI()
            self.startLoad(self.loader and not self.loader.isVisible())
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.topNavigationPanel = Panel(self)
        self.horizontalLayout = QHBoxLayout(self.topNavigationPanel)
        self.page1 = PushButton(self.topNavigationPanel)
        self.page1.setMinimumHeight(32)
        self.page1.setCheckable(True)
        self.page1.setChecked(True)
        self.page1.setAutoExclusive(True)
        self.page1.released.connect(lambda: self.setCurrentPage(0))
        self.horizontalLayout.addWidget(self.page1)
        self.horizontalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.horizontalLayout.addItem(self.horizontalSpacer)
        
        self.stackedWidget = AnimatedStackedWidget(self)
        
        self.page1Frame = self.DownloadVanilla(self.stackedWidget)
        self.stackedWidget.addWidget(self.page1Frame)
        
        app.registerRetranslateFunction(self.retranslateUI)
        self.retranslateUI()
    
    def retranslateUI(self):
        self.page1.setText("原版游戏")
        menu = RoundedMenu(self.page1)
        action1 = QAction(menu)
        action1.setIcon(QIcon(f":/Reload-{'black' if getTheme() == Theme.Light else 'white'}.avg"))
        action1.setText("重新加载")
        action1.triggered.connect(self.page1Frame.reloadVersions)
        menu.addAction(action1)
        self.page1.setMenu(menu)
    
    def setCurrentPage(self, page_id=-1):
        page_seq = (self.page1,)
        page_frame_dict = {
            self.page1: self.page1Frame
        }
        if -1 < page_id < len(page_seq):
            page = page_seq[page_id]
            page_frame = page_frame_dict[page]
            page.setChecked(True)
            self.stackedWidget.setCurrentWidget(page_frame)
    
    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        
        self.topNavigationPanel.move(QPoint(15, 15))
        
        sizeAnimation = QPropertyAnimation(self.topNavigationPanel, b"size", self)
        sizeAnimation.setStartValue(self.topNavigationPanel.size())
        sizeAnimation.setEndValue(QSize(self.width() - 30, 54))
        sizeAnimation.setDuration(100)
        sizeAnimation.setEasingCurve(QEasingCurve.Type.OutQuad)
        sizeAnimation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        
        self.stackedWidget.move(QPoint(15, 79))
        
        sizeAnimation = QPropertyAnimation(self.stackedWidget, b"size", self)
        sizeAnimation.setStartValue(self.stackedWidget.size())
        sizeAnimation.setEndValue(QSize(self.width() - 30, self.height() - 15 - 79))
        sizeAnimation.setDuration(100)
        sizeAnimation.setEasingCurve(QEasingCurve.Type.OutQuad)
        sizeAnimation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)


class SettingsPage(QFrame):
    class LaunchSettings(QFrame):
        class GetJavaThread(QThread):
            gettingFinished = pyqtSignal(list)
            
            def run(self):
                java_list = []
                where_out = subprocess.run(
                    ["which" if GetOperationSystemName().lower() != "windows" else "where", "java"],
                    capture_output=True, check=False).stdout
                java_path = where_out.decode(errors="ignore").splitlines()
                if len(java_path) >= 2 and not java_path[-1]:
                    del java_path[-1]
                if not java_path:
                    self.gettingFinished.emit([])
                    return
                if Path(java_path[0]).exists():
                    for i in java_path:
                        if Path(i).is_file():
                            try:
                                version_data = \
                                    subprocess.check_output([i, "--version"], stderr=subprocess.STDOUT,
                                                            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(
                                                                subprocess,
                                                                "CREATE_NO_WINDOW") else 0).decode().splitlines()[
                                        0].split(" ")[1].strip('"')
                            except subprocess.CalledProcessError:
                                version_data = \
                                    subprocess.check_output([i, "-version"], stderr=subprocess.STDOUT,
                                                            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(
                                                                subprocess,
                                                                "CREATE_NO_WINDOW") else 0).decode().splitlines()[
                                        0].split(" ")[2].strip('"')
                            java_list.append((i, version_data))
                
                self.gettingFinished.emit(java_list)
        
        def __init__(self, parent):
            super().__init__(parent)
            self.mainLayout = QVBoxLayout(self)
            self.scrollArea = ScrollArea(self)
            self.mainLayout.addWidget(self.scrollArea)
            
            self.scrollAreaWidgetContents = QWidget()
            
            self.verticalLayout = QVBoxLayout(self.scrollAreaWidgetContents)
            
            self.groupBox_Java = GroupBox(self.scrollAreaWidgetContents)
            self.verticalLayout.addWidget(self.groupBox_Java)
            
            self.form_1 = QFormLayout(self.groupBox_Java)
            self.form_1.setContentsMargins(5, 5, 5, 5)
            self.form_1.setSpacing(5)
            
            self.form_4_Label = Label(self.groupBox_Java)
            self.form_1.setWidget(0, QFormLayout.ItemRole.LabelRole, self.form_4_Label)
            
            self.form_4_VerticalLayout = QVBoxLayout()
            self.form_4_VerticalLayout.setContentsMargins(0, 0, 0, 0)
            self.form_4_VerticalLayout.setSpacing(5)
            self.form_1.setLayout(0, QFormLayout.ItemRole.FieldRole, self.form_4_VerticalLayout)
            
            self.form_4_ComboBox = ComboBox(self.groupBox_Java)
            self.form_4_ComboBox.currentIndexChanged.connect(self.updateSeperationMode)
            self.form_4_VerticalLayout.addWidget(self.form_4_ComboBox)
            
            self.form_4_HorizontalLayout = QHBoxLayout()
            self.form_4_VerticalLayout.addLayout(self.form_4_HorizontalLayout)
            
            self.form_4_CheckBox = CheckBox(self.groupBox_Java)
            self.form_4_CheckBox.setChecked(
                settings["LaunchSettings"]["VersionSeperationConfig"]["ShareVersionOptions"])
            self.form_4_CheckBox.toggled.connect(self.updateSharingOptionsState)
            self.form_4_HorizontalLayout.addWidget(self.form_4_CheckBox)
            
            self.form_4_CheckBox_2 = CheckBox(self.groupBox_Java)
            self.form_4_CheckBox_2.setChecked(
                settings["LaunchSettings"]["VersionSeperationConfig"]["ShareVersionResourcePacks"])
            self.form_4_CheckBox_2.toggled.connect(self.updateSharingResourcePacksState)
            self.form_4_HorizontalLayout.addWidget(self.form_4_CheckBox_2)
            
            self.form_4_HorizontalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            self.form_4_HorizontalLayout.addItem(self.form_4_HorizontalSpacer)
            
            self.form_1_Label = Label(self.groupBox_Java)
            self.form_1.setWidget(1, QFormLayout.ItemRole.LabelRole, self.form_1_Label)
            
            self.form_1_VerticalLayout = QVBoxLayout()
            self.form_1_VerticalLayout.setContentsMargins(0, 0, 0, 0)
            self.form_1_VerticalLayout.setSpacing(5)
            self.form_1.setLayout(1, QFormLayout.ItemRole.FieldRole, self.form_1_VerticalLayout)
            
            self.form_1_ComboBox = ComboBox(self.groupBox_Java)
            self.form_1_ComboBox.setEditable(True)
            self.form_1_ComboBox.setFont(fixedFont)
            self.form_1_ComboBox.setCurrentText(settings["LaunchSettings"]["Java"]["JavaPath"])
            self.form_1_ComboBox.currentTextChanged.connect(self.updateJavaPath)
            self.form_1_ComboBox.lineEdit().editingFinished.connect(self.updateJavaPathCandidates)
            self.form_1_VerticalLayout.addWidget(self.form_1_ComboBox, 1)
            self.form_1_ComboBox.setMinimumHeight(self.form_1_ComboBox.fontMetrics().boundingRect("Jj").height() + 19)
            
            self.form_1_HorizontalLayout = QHBoxLayout()
            self.form_1_HorizontalLayout.setContentsMargins(0, 0, 0, 0)
            
            self.form_1_PushButton = TogglePushButton(self.groupBox_Java)
            self.form_1_PushButton.setChecked(settings["LaunchSettings"]["Java"]["AutoSelect"])
            self.form_1_PushButton.toggled.connect(self.updateJavaSelectState)
            self.form_1_HorizontalLayout.addWidget(self.form_1_PushButton)
            
            self.form_1_PushButton_2 = PushButton(self.groupBox_Java)
            self.form_1_PushButton_2.pressed.connect(self.selectJava)
            self.form_1_HorizontalLayout.addWidget(self.form_1_PushButton_2)
            
            self.form_1_HorizontalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            self.form_1_HorizontalLayout.addItem(self.form_1_HorizontalSpacer)
            
            self.form_1_VerticalLayout.addLayout(self.form_1_HorizontalLayout)
            
            self.groupBox_2 = GroupBox(self.scrollAreaWidgetContents)
            self.groupBox_2.setCheckable(True)
            self.groupBox_2.setChecked(False)
            self.verticalLayout.addWidget(self.groupBox_2)
            
            self.form_2 = QFormLayout(self.groupBox_2)
            
            self.form_2_Label = Label(self.groupBox_2)
            self.form_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.form_2_Label)
            
            self.form_2_TextEdit = TextEdit(self.groupBox_2)
            self.form_2_TextEdit.setFont(fixedFont)
            self.form_2_TextEdit.setText(
                "-XX:+UseG1GC -XX:+UseAdaptiveSizePolicy -XX:MaxInlineSize=420 -XX:+TieredCompilation -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=152 -XX:+UnlockExperimentalVMOptions -XX:+UnlockDiagnosticVMOptions -XX:+Inline -XX:+DisableExplicitGC -XX:+AlwaysPreTouch -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=8M -XX:G1ReservePercent=20 -XX:G1HeapWastePercent=5 -XX:G1MixedGCCountTarget=4 -XX:InitiatingHeapOccupancyPercent=15 -XX:G1MixedGCLiveThresholdPercent=90 -XX:G1RSetUpdatingPauseTimePercent=5 -XX:SurvivorRatio=31 -XX:+PerfDisableSharedMem -XX:ParallelGCThreads=20 -XX:ConcGCThreads=20 -XX:MaxTenuringThreshold=1 -Dfml.ignoreInvalidMinecraftCertificates=True -Dfml.ignorePatchDiscrepancies=True -Dlog4j2.formatMsgNoLookups=true -Dfile.encoding=UTF-8 -Dstdout.encoding=UTF-8 -Dstderr.encoding=UTF-8 -Dorg.lwjgl.util.DebugLoader=true -Dorg.lwjgl.util.Debug=true")
            self.form_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.form_2_TextEdit)
            
            self.form_3_Label = Label(self.groupBox_2)
            self.form_2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.form_3_Label)
            
            self.form_3_TextEdit = TextEdit(self.groupBox_2)
            self.form_2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.form_3_TextEdit)
            
            self.verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
            self.verticalLayout.addItem(self.verticalSpacer)
            
            self.scrollArea.setWidget(self.scrollAreaWidgetContents)
            self.scrollArea.setWidgetResizable(True)
            
            self.getJavaThread = None
            self.javaList = None
            self.updateJavaPathComboBox()
            
            app.registerRetranslateFunction(self.retranslateUI)
            self.retranslateUI()
        
        def retranslateUI(self):
            self.groupBox_Java.setTitle("启动设置")
            self.form_4_Label.setText("版本隔离")
            self.form_4_ComboBox.clear()
            self.form_4_ComboBox.addItem("不隔离")
            self.form_4_ComboBox.addItem("隔离所有版本")
            self.form_4_ComboBox.addItem("隔离模组加载器与其他版本")
            self.form_4_ComboBox.addItem("隔离正式版与测试版")
            self.form_4_ComboBox.setCurrentIndex(settings["LaunchSettings"]["VersionSeperation"])
            self.form_4_ComboBox.setToolTip("""通过修改游戏的运行路径，使游戏的运行路径各不相同，从而避免模组冲突。
◉ 不隔离：所有版本都在同一文件夹下；
◉ 隔离所有版本：所有版本的文件各不互通，这可能会导致你电脑的 Ctrl、C 和 V 键的使用次数增多（人话：复制很麻烦）；
◉ 隔离模组加载器与其他版本：（暂未支持）模组加载器（如 Forge、Fabric）互相隔离，其他版本（如原版）则不隔离；
◉ 隔离正式版和测试版：隔离正式版和测试版（快照及远古版）。
除了第一种，其他的均会在版本文件夹下创建内容。
启动器处理方式根据版本有区别，请以游戏具体文件夹为准。""")
            self.form_4_CheckBox.setText("共用设置文件")
            self.form_4_CheckBox.setToolTip(
                "所有版本使用同一个设置文件\n注意：这会覆盖当前版本设置，请先行将设置文件复制到根目录，或者删除根目录的设置文件！")
            self.form_4_CheckBox_2.setText("共用资源包")
            self.form_4_CheckBox_2.setToolTip(
                "所有版本使用同一个资源包文件夹\n注意：当前版本的资源包会被移动到全局资源包文件夹里。")
            self.form_1_Label.setText("Java 路径")
            if self.form_1_PushButton.isChecked():
                self.form_1_ComboBox.setCurrentText("自动选择")
            self.form_1_ComboBox.setToolTip("""手动输入 Java 路径，启动器会自行检测版本号。
如果输入了版本号，请在路径左右打上英文半角双引号（\"...\"），以方便启动器检测路径。
启动器会自动纠正版本号，不用担心。而且版本号是给你看的，不是给我看的，不要糊弄人！！！
同时，启动器会自动补全相对路径，以启动器当前所在文件夹补全。""")
            self.form_1_PushButton.setText("自动选择 Java")
            self.form_1_PushButton.setToolTip("""让启动器自动选择 Java。
因技术原因，有的 Java 检测不出来。
如果无法启动，请尝试取消该选项。
启动器暂时不会对没有 Java、Java 版本不兼容的情况作弹窗提示，请自行判断。""")
            self.form_1_PushButton_2.setText("添加 Java")
            self.groupBox_2.setTitle("高级启动设置")
            self.form_2_Label.setText("JVM 启动参数头")
            self.form_2_TextEdit.setToolTip("""这一段参数会加在 JVM 参数的最前面，自动去除前后空格。
比如说你设置的是：
“-Dchengwm.CMCL.abc=true”
无论前后有没有空格：
“              -Dchengwm.CMCL.abc=true                                  ”
JVM 参数就是：
“\"{Java 路径}\" -Dchengwm.CMCL.abc=true {Minecraft 启动的其他 JVM 参数} -cp {一堆 jar 文件} {游戏参数}”。
- 注明：实际除了设置的参数位置以外，后面的参数根据版本的不同有所差异。

**奉劝你去看一下 JVM 参数的相关文档，任何因为修改 JVM 参数引发的启动问题均不在启动器作者的受理范围内**
（前提是你拿其他启动器也搞不了，如果确实是本启动器的问题，请附上你的 JVM 参数，你的 Java 版本以及你的游戏版本）""")
            self.form_3_Label.setText("额外启动参数")
            self.form_3_TextEdit.setToolTip("""设置额外启动参数，加在游戏参数的末尾。
比如说，如果你想启动时全屏（不是最大化），你可以这样设置：
“-fullscreen”
自动去除前后空格，设置错误不影响启动（但是影响游玩）
同时，这是全局设置，请注意版本兼容性。""")
        
        def updateJavaPathComboBox(self, state=True):
            if self.form_1_PushButton.isChecked():
                self.form_1_ComboBox.setDisabled(True)
                self.form_1_ComboBox.clear()
                self.form_1_ComboBox.setCurrentText("自动选择")
                if self.getJavaThread:
                    self.getJavaThread.terminate()
                    self.getJavaThread = None
                if self.javaList:
                    self.javaList = None
            else:
                self.form_1_ComboBox.setEnabled(True)
                if not state:
                    self.form_1_ComboBox.setCurrentText("")
                if not self.getJavaThread:
                    self.getJavaThread = self.GetJavaThread(self)
                    self.getJavaThread.gettingFinished.connect(self.updateJavaPathSelections)
                    self.getJavaThread.start()
        
        def updateJavaPathSelections(self, java_list):
            path = self.form_1_ComboBox.currentText()
            if path and Path(path.strip('"')).exists() and path.strip('"') not in set(
                    self.javaList or map(lambda a: a[0], java_list)):
                path = path.strip('"')
                try:
                    version_data = \
                        subprocess.check_output([path, "--version"], stderr=subprocess.STDOUT,
                                                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(
                                                    subprocess,
                                                    "CREATE_NO_WINDOW") else 0).decode().splitlines()[
                            0].split(" ")[1].strip('"')
                except subprocess.CalledProcessError:
                    version_data = \
                        subprocess.check_output([path, "-version"], stderr=subprocess.STDOUT,
                                                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(
                                                    subprocess,
                                                    "CREATE_NO_WINDOW") else 0).decode().splitlines()[
                            0].split(" ")[2].strip('"')
                java_list.insert(0, (path, version_data))
            self.javaList = list(map(lambda a: str(Path(a[0]).absolute()), java_list))
            self.form_1_ComboBox.clear()
            for java in java_list:
                self.form_1_ComboBox.addItem(f'"{str(Path(java[0]).absolute())}" ({java[1]})')
        
        def updateJavaPath(self, text):
            if not self.form_1_PushButton.isChecked():
                settings["LaunchSettings"]["Java"]["AutoSelect"] = False
                settings["LaunchSettings"]["Java"]["JavaPath"] = (
                    text[:min(text.rindex('"') + 1, len(text) - 1)] if '"' in text else text).strip('"')
            else:
                settings["LaunchSettings"]["Java"]["AutoSelect"] = True
                settings["LaunchSettings"]["Java"]["JavaPath"] = None
        
        def updateJavaPathCandidates(self, raw_text=None):
            if not raw_text:
                raw_text = self.form_1_ComboBox.lineEdit().text()
            if not raw_text:
                return
            text = (raw_text[:min(raw_text.rindex('"') + 1, len(raw_text) - 1)] if '"' in raw_text else raw_text).strip(
                '"')
            if text and Path(text).exists() and text not in set(self.javaList or []):
                text = str(Path(text).absolute())
                self.javaList.append(text)
                try:
                    version_data = \
                        subprocess.check_output([text, "--version"], stderr=subprocess.STDOUT,
                                                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(
                                                    subprocess,
                                                    "CREATE_NO_WINDOW") else 0).decode().splitlines()[
                            0].split(" ")[1].strip('"')
                except subprocess.CalledProcessError:
                    version_data = \
                        subprocess.check_output([text, "-version"], stderr=subprocess.STDOUT,
                                                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(
                                                    subprocess,
                                                    "CREATE_NO_WINDOW") else 0).decode().splitlines()[
                            0].split(" ")[2].strip('"')
                self.form_1_ComboBox.addItem(f'"{text}" ({version_data})')
                self.form_1_ComboBox.setEditText(f'"{text}" ({version_data})')
        
        def updateJavaSelectState(self, state):
            self.updateJavaPathComboBox(state)
        
        def selectJava(self):
            self.form_1_PushButton_2.setDown(False)
            fileDialogue = QFileDialog.getOpenFileName(self, "选择 Java", str(Path(".").absolute()),
                                                       "java.exe javaw.exe")
            if fileDialogue:
                javaPath = str(Path(fileDialogue[0]).absolute())
                self.updateJavaPathCandidates(javaPath)
        
        def updateSeperationMode(self):
            if not self.form_4_ComboBox.count():
                return
            index = self.form_4_ComboBox.currentIndex()
            settings["LaunchSettings"]["VersionSeperation"] = index
            if index != 0:
                self.form_4_CheckBox.setEnabled(True)
                self.form_4_CheckBox_2.setEnabled(True)
            else:
                self.form_4_CheckBox.setDisabled(True)
                self.form_4_CheckBox_2.setDisabled(True)
                self.form_4_CheckBox.setChecked(False)
                self.form_4_CheckBox_2.setChecked(False)
        
        def updateSharingOptionsState(self, state):
            settings["LaunchSettings"]["VersionSeperationConfig"]["ShareVersionOptions"] = state
        
        def updateSharingResourcePacksState(self, state):
            settings["LaunchSettings"]["VersionSeperationConfig"]["ShareVersionResourcePacks"] = state
        
        def resizeEvent(self, a0):
            super().resizeEvent(a0)
            self.form_1_ComboBox.lineEdit().setMinimumHeight(
                self.form_1_ComboBox.height() - (self.form_1_ComboBox.lineEdit().y() * 2))
    
    class PersonalisationSettings(QFrame):
        def __init__(self, parent):
            super().__init__(parent)
            self.mainLayout = QVBoxLayout(self)
            self.scrollArea = ScrollArea(self)
            self.mainLayout.addWidget(self.scrollArea)
            
            self.scrollAreaWidgetContents = QWidget()
            
            self.verticalLayout = QVBoxLayout(self.scrollAreaWidgetContents)
            
            self.groupBox = GroupBox(self)
            self.verticalLayout.addWidget(self.groupBox)
            
            self.setThemePreset(True, settings["LauncherSettings"]["Personalisation"]["CurrentThemePreset"], False)
            
            self.gridLayout = QGridLayout(self.groupBox)
            
            self.groupBox_radioButton = RadioButton(self.groupBox)
            self.groupBox_radioButton.setChecked(
                settings["LauncherSettings"]["Personalisation"]["CurrentThemePreset"] == "PresetBlue")
            self.groupBox_radioButton.toggled.connect(
                lambda state: self.setThemePreset(self.groupBox_radioButton.isChecked(), "PresetBlue"))
            self.gridLayout.addWidget(self.groupBox_radioButton, 0, 0)
            
            self.groupBox_radioButton_2 = RadioButton(self.groupBox)
            self.groupBox_radioButton_2.setChecked(
                settings["LauncherSettings"]["Personalisation"]["CurrentThemePreset"] == "PresetPink")
            self.groupBox_radioButton_2.toggled.connect(
                lambda state: self.setThemePreset(self.groupBox_radioButton_2.isChecked(), "PresetPink"))
            self.gridLayout.addWidget(self.groupBox_radioButton_2, 0, 1)
            
            self.groupBox_radioButton_3 = RadioButton(self.groupBox)
            self.groupBox_radioButton_3.setChecked(
                settings["LauncherSettings"]["Personalisation"]["CurrentThemePreset"] == "PresetPurple")
            self.groupBox_radioButton_3.toggled.connect(
                lambda state: self.setThemePreset(self.groupBox_radioButton_3.isChecked(), "PresetPurple"))
            self.gridLayout.addWidget(self.groupBox_radioButton_3, 1, 0)
            
            self.groupBox_radioButton_4 = RadioButton(self.groupBox)
            self.groupBox_radioButton_4.setChecked(
                settings["LauncherSettings"]["Personalisation"]["CurrentThemePreset"] == "PresetRed")
            self.groupBox_radioButton_4.toggled.connect(
                lambda state: self.setThemePreset(self.groupBox_radioButton_4.isChecked(), "PresetRed"))
            self.gridLayout.addWidget(self.groupBox_radioButton_4, 1, 1)
            
            self.groupBox_2 = GroupBox(self.scrollAreaWidgetContents)
            self.verticalLayout.addWidget(self.groupBox_2)
            
            self.verticalLayout_2 = QVBoxLayout(self.groupBox_2)
            
            self.horizontalLayout = QHBoxLayout()
            self.verticalLayout_2.addLayout(self.horizontalLayout)
            
            self.groupBox_2_Label = Label()
            self.horizontalLayout.addWidget(self.groupBox_2_Label)
            
            colour = Colour(*settings["LauncherSettings"]["Personalisation"]["BackgroundColour"])
            
            self.groupBox_2_SpinBox = SpinBox()
            self.groupBox_2_SpinBox.setMaximum(255)
            self.groupBox_2_SpinBox.setValue(colour.red())
            self.groupBox_2_SpinBox.valueChanged.connect(
                lambda value: self.setBackgroundColour(True, False, False, value))
            self.horizontalLayout.addWidget(self.groupBox_2_SpinBox)
            
            self.groupBox_2_SpinBox_2 = SpinBox()
            self.groupBox_2_SpinBox_2.setMaximum(255)
            self.groupBox_2_SpinBox_2.setValue(colour.green())
            self.groupBox_2_SpinBox_2.valueChanged.connect(
                lambda value: self.setBackgroundColour(False, True, False, value))
            self.horizontalLayout.addWidget(self.groupBox_2_SpinBox_2)
            
            self.groupBox_2_SpinBox_3 = SpinBox()
            self.groupBox_2_SpinBox_3.setMaximum(255)
            self.groupBox_2_SpinBox_3.setValue(colour.blue())
            self.groupBox_2_SpinBox_3.valueChanged.connect(
                lambda value: self.setBackgroundColour(False, False, True, value))
            self.horizontalLayout.addWidget(self.groupBox_2_SpinBox_3)
            
            # self.horizontalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            # self.horizontalLayout.addItem(self.horizontalSpacer)
            
            self.groupBox_3 = GroupBox(self.scrollAreaWidgetContents)
            self.verticalLayout.addWidget(self.groupBox_3)
            
            self.groupBox_4 = GroupBox(self.scrollAreaWidgetContents)
            self.verticalLayout.addWidget(self.groupBox_4)
            
            self.form_1 = QFormLayout(self.groupBox_4)
            
            self.form_1_Label = Label(self.groupBox_4)
            self.form_1.setWidget(0, QFormLayout.ItemRole.LabelRole, self.form_1_Label)
            
            self.form_1_ComboBox = ComboBox(self.groupBox_4)
            self.form_1_ComboBox.wheelEvent = lambda: None
            self.form_1.setWidget(0, QFormLayout.ItemRole.FieldRole, self.form_1_ComboBox)
            
            self.updateLanguagesList()
            
            self.groupBox_4_Tip = Label(self.groupBox_4)
            self.form_1.setWidget(1, QFormLayout.ItemRole.FieldRole, self.groupBox_4_Tip)
            
            self.verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
            self.verticalLayout.addItem(self.verticalSpacer)
            
            self.scrollArea.setWidget(self.scrollAreaWidgetContents)
            self.scrollArea.setWidgetResizable(True)
            
            app.registerRetranslateFunction(self.retranslateUI)
            self.retranslateUI()
        
        def retranslateUI(self):
            self.groupBox.setTitle("主题")
            self.groupBox_radioButton.setText("预设蓝")
            self.groupBox_radioButton.setToolTip("启动器的默认预设主题颜色！")
            self.groupBox_radioButton_2.setText("预设粉")
            self.groupBox_radioButton_2.setToolTip(
                "如果你觉得这个有点不像粉色……别问了，就是作者没调好。调了好几次才调成现在这个颜色的。")
            self.groupBox_radioButton_3.setText("预设紫")
            self.groupBox_radioButton_3.setToolTip("这个是我在切换蓝色与粉色时意外发现的调色。")
            self.groupBox_radioButton_4.setText("预设红")
            self.groupBox_2.setTitle("背景")
            self.groupBox_2_Label.setText("背景中心颜色（RGB）")
            self.groupBox_3.setTitle("动画")
            self.groupBox_4.setTitle("语言")
            self.form_1_Label.setText("界面语言")
            self.groupBox_4_Tip.setText("语言翻译未必 100% 准确")
        
        @staticmethod
        def setThemePreset(state, value, ani=True):
            if not state:
                return
            settings["LauncherSettings"]["Personalisation"]["CurrentThemePreset"] = value
            if value in themeColourDefines:
                define = themeColourDefines[value]
                for theme in define:
                    for role in define[theme]:
                        for highlight in define[theme][role]:
                            setThemeColour(
                                role,
                                False,
                                highlight,
                                theme,
                                Colour(*themeColourDefines[value][theme][role][highlight]),
                                ani
                            )
        
        @staticmethod
        def setBackgroundColour(red=False, green=False, blue=False, value=0):
            if red:
                window.centreColour.setRed(value)
            if green:
                window.centreColour.setGreen(value)
            if blue:
                window.centreColour.setBlue(value)
            settings["LauncherSettings"]["Personalisation"]["BackgroundColour"] = tuple(window.centreColour)
        
        def updateLanguagesList(self):
            self.form_1_ComboBox.clear()
            
            index = 0
            languagesSequence = sorted(languagesCodeMapping)
            for idx, lang in enumerate(languagesSequence):
                if lang == currentLanguage:
                    index = idx
                self.form_1_ComboBox.addItem(f"{languagesCodeMapping[lang]} ({lang})")
            
            self.form_1_ComboBox.setCurrentIndex(index)
        
        def setLanguage(self):
            global currentLanguage
            languagesSequence = sorted(languagesCodeMapping)
            langCode = languagesSequence[self.form_1_ComboBox.currentIndex()]
            currentLanguage = langCode
            app.retranslate()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.topNavigationPanel = Panel(self)
        self.horizontalLayout = QHBoxLayout(self.topNavigationPanel)
        self.page1 = PushButton(self.topNavigationPanel)
        self.page1.setMinimumHeight(32)
        self.page1.setCheckable(True)
        self.page1.setChecked(True)
        self.page1.setAutoExclusive(True)
        self.page1.released.connect(lambda: self.setCurrentPage(0))
        self.horizontalLayout.addWidget(self.page1)
        self.page2 = PushButton(self.topNavigationPanel)
        self.page2.setMinimumHeight(32)
        self.page2.setCheckable(True)
        self.page2.setAutoExclusive(True)
        self.page2.released.connect(lambda: self.setCurrentPage(1))
        self.horizontalLayout.addWidget(self.page2)
        self.horizontalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.horizontalLayout.addItem(self.horizontalSpacer)
        
        self.stackedWidget = AnimatedStackedWidget(self)
        
        self.page1Frame = self.LaunchSettings(self.stackedWidget)
        self.stackedWidget.addWidget(self.page1Frame)
        
        self.page2Frame = self.PersonalisationSettings(self.stackedWidget)
        self.stackedWidget.addWidget(self.page2Frame)
        
        app.registerRetranslateFunction(self.retranslateUI)
        self.retranslateUI()
    
    def retranslateUI(self):
        self.page1.setText("启动设置")
        self.page2.setText("个性化")
    
    def setCurrentPage(self, page_id=-1):
        page_seq = (self.page1, self.page2)
        page_frame_dict = {
            self.page1: self.page1Frame,
            self.page2: self.page2Frame
        }
        if -1 < page_id < len(page_seq):
            page = page_seq[page_id]
            page_frame = page_frame_dict[page]
            page.setChecked(True)
            self.stackedWidget.setCurrentWidget(page_frame)
    
    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        
        self.topNavigationPanel.move(QPoint(15, 15))
        
        sizeAnimation = QPropertyAnimation(self.topNavigationPanel, b"size", self)
        sizeAnimation.setStartValue(self.topNavigationPanel.size())
        sizeAnimation.setEndValue(QSize(self.width() - 30, 54))
        sizeAnimation.setDuration(100)
        sizeAnimation.setEasingCurve(QEasingCurve.Type.OutQuad)
        sizeAnimation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        
        self.stackedWidget.move(QPoint(15, 79))
        
        sizeAnimation = QPropertyAnimation(self.stackedWidget, b"size", self)
        sizeAnimation.setStartValue(self.stackedWidget.size())
        sizeAnimation.setEndValue(QSize(self.width() - 30, self.height() - 15 - 79))
        sizeAnimation.setDuration(100)
        sizeAnimation.setEasingCurve(QEasingCurve.Type.OutQuad)
        sizeAnimation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)


class AboutPage(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.mainLayout = QVBoxLayout(self)
        
        self.scrollArea = ScrollArea(self)
        self.scrollArea.setStyleSheet("background: transparent;")
        self.mainLayout.addWidget(self.scrollArea)
        self.scrollAreaWidgetContent = QWidget()
        
        self.verticalLayout = QVBoxLayout(self.scrollAreaWidgetContent)
        
        self.groupBox_CMCLVersion = GroupBox(self.scrollAreaWidgetContent)
        self.verticalLayout.addWidget(self.groupBox_CMCLVersion)
        
        self.horizontalLayout = QHBoxLayout(self.groupBox_CMCLVersion)
        
        self.CMCLIconLabel = ToolButton(self.groupBox_CMCLVersion)
        self.CMCLIconLabel.setFixedSize(QSize(74, 74))
        self.CMCLIconLabel.setIconSize(QSize(64, 64))
        self.CMCLIconLabel.setIcon(QIcon(":/CommonMinecraftLauncherIcon.svg"))
        self.horizontalLayout.addWidget(self.CMCLIconLabel)
        
        self.CMCLVersionLabel = Label(self.groupBox_CMCLVersion)
        self.horizontalLayout.addWidget(self.CMCLVersionLabel, 1)
        
        self.groupBox_authors = GroupBox(self.scrollAreaWidgetContent)
        self.verticalLayout.addWidget(self.groupBox_authors)
        
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_authors)
        
        self.card1 = Panel(self.groupBox_authors)
        self.verticalLayout_2.addWidget(self.card1)
        
        self.horizontalLayout = QHBoxLayout(self.card1)
        
        self.avatar1 = ToolButton(self.card1)
        self.avatar1.setFixedSize(QSize(42, 42))
        self.avatar1.setIconSize(QSize(32, 32))
        self.avatar1.setIcon(QIcon(":/chengwm_avatar.png"))
        self.horizontalLayout.addWidget(self.avatar1)
        
        self.intro1 = Label(self.card1)
        self.horizontalLayout.addWidget(self.intro1, 1)
        
        self.card2 = Panel(self.groupBox_authors)
        self.verticalLayout_2.addWidget(self.card2)
        
        self.horizontalLayout_2 = QHBoxLayout(self.card2)
        
        self.avatar2 = ToolButton(self.card2)
        self.avatar2.setFixedSize(QSize(42, 42))
        self.avatar2.setIconSize(QSize(32, 32))
        self.avatar2.setIcon(QIcon(":/mcdaotian_avatar.png"))
        self.horizontalLayout_2.addWidget(self.avatar2)
        
        self.intro2 = Label(self.card2)
        self.horizontalLayout_2.addWidget(self.intro2, 1)
        
        self.groupBox_thanks = GroupBox(self.scrollAreaWidgetContent)
        self.verticalLayout.addWidget(self.groupBox_thanks)
        
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_thanks)
        
        self.acks_card_1 = Panel(self)  # 以防有人不知道 ack 取自 acknowledgement 的前三个字母
        self.verticalLayout_3.addWidget(self.acks_card_1)
        
        self.horizontalLayout_acks_1 = QHBoxLayout(self.acks_card_1)
        
        self.acks_avatar_1 = ToolButton(self.acks_card_1)
        self.acks_avatar_1.setFixedSize(QSize(42, 42))
        self.acks_avatar_1.setIconSize(QSize(32, 32))
        self.horizontalLayout_acks_1.addWidget(self.acks_avatar_1)
        
        self.acks_intro1 = Label(self.acks_card_1)
        self.horizontalLayout_acks_1.addWidget(self.acks_intro1, 1)
        
        self.acks_card_2 = Panel(self)  # 以防有人不知道 ack 取自 acknowledgement 的前三个字母
        self.verticalLayout_3.addWidget(self.acks_card_2)
        
        self.horizontalLayout_acks_2 = QHBoxLayout(self.acks_card_2)
        
        self.acks_avatar_2 = ToolButton(self.acks_card_2)
        self.acks_avatar_2.setFixedSize(QSize(42, 42))
        self.acks_avatar_2.setIconSize(QSize(32, 32))
        self.horizontalLayout_acks_2.addWidget(self.acks_avatar_2)
        
        self.acks_intro2 = Label(self.acks_card_2)
        self.horizontalLayout_acks_2.addWidget(self.acks_intro2, 2)
        
        self.groupBox_disclaimer = GroupBox(self.scrollAreaWidgetContent)
        disclaimer_font = self.groupBox_disclaimer.font()
        disclaimer_font.setWeight(1000)
        self.groupBox_disclaimer.setFont(disclaimer_font)
        self.verticalLayout.addWidget(self.groupBox_disclaimer)
        
        self.verticalLayout_4 = QVBoxLayout(self.groupBox_disclaimer)
        
        self.disclaimer = Label(self.groupBox_disclaimer)
        self.disclaimer.setFont(disclaimer_font)
        
        self.verticalLayout_4.addWidget(self.disclaimer)
        
        self.groupBox_lawInfomation = GroupBox(self)
        self.verticalLayout.addWidget(self.groupBox_lawInfomation)
        
        self.verticalLayout_5 = QVBoxLayout(self.groupBox_lawInfomation)
        
        self.lawInfomation = Label(self.groupBox_lawInfomation)
        self.verticalLayout_5.addWidget(self.lawInfomation)
        
        self.verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(self.verticalSpacer)
        
        self.scrollArea.setWidget(self.scrollAreaWidgetContent)
        self.scrollArea.setWidgetResizable(True)
        
        app.registerRetranslateFunction(self.retranslateUI)
        self.retranslateUI()
    
    def retranslateUI(self):
        self.groupBox_CMCLVersion.setTitle("Common Minecraft Launcher")
        self.CMCLVersionLabel.setText(
            f"Common Minecraft Launcher\n版本：{CMCLVersion[0]} ({CMCLVersion[1]})\n语言：{languagesCodeMapping[currentLanguage]} ({currentLanguage})")
        self.groupBox_authors.setTitle("关于开发组")
        self.intro1.setText("chengwm (chengwm123456)\n启动器的作者！也是造成启动器彩蛋非常多的罪魁祸首。")
        self.intro2.setText("mcdaotian / Minecraft_稻田\n启动器的策划！可谓是为启动器一起提供了许多改进！")
        self.groupBox_thanks.setTitle("致谢")
        
        # 致谢文本翻译 / Acknowledgements text translations
        self.acks_intro1.setText("Minecraft Wiki\n启动器编写时资料参考处！（仅作为参考，位于中文 MCW）")
        self.acks_intro2.setText(
            "龙腾猫跃 (LTCat)\n据野史（并非）记载，启动器作者在自主编写启动部分时，使用了某不知名启动器生成的命令作为标准命令。")
        
        self.groupBox_disclaimer.setTitle("免责声明")
        self.disclaimer.setText(
            "本产品非 Minecraft 官方产品。\n未经 Mojang Studios 或 Microsoft 批准，亦与 Mojang Studios 或 Microsoft 无任何从属关系。\nMinecraft 官方网站请见：https://www.minecraft.net/")
        
        self.groupBox_lawInfomation.setTitle("法律信息")
        self.lawInfomation.setText("""Copyright (C) 2025 chengwm123456
本程序为自由软件，在 Free Software Foundation 发布的 GNU General Public License 的约束下，你可以对其进行再发布及修改。协议版本为第三版。
我们希望发布的这款程序有用，但不确定，甚至不保证它有经济价值和适合特定用途。详情参见 GNU General Public License。""")
    
    def showEvent(self, a0):
        pos1 = self.groupBox_CMCLVersion.pos()
        pos2 = self.groupBox_authors.pos()
        pos3 = self.groupBox_thanks.pos()
        pos4 = self.groupBox_disclaimer.pos()
        pos5 = self.groupBox_lawInfomation.pos()
        super().showEvent(a0)
        
        self.groupBox_CMCLVersion.hide()
        self.groupBox_authors.hide()
        self.groupBox_thanks.hide()
        self.groupBox_disclaimer.hide()
        self.groupBox_lawInfomation.hide()
        
        self.verticalLayout.removeWidget(self.groupBox_CMCLVersion)
        self.verticalLayout.removeWidget(self.groupBox_authors)
        self.verticalLayout.removeWidget(self.groupBox_thanks)
        self.verticalLayout.removeWidget(self.groupBox_disclaimer)
        self.verticalLayout.removeWidget(self.groupBox_lawInfomation)
        
        ani1 = QPropertyAnimation(self.groupBox_CMCLVersion, b"pos", self)
        ani1.setStartValue(pos1 + QPoint(self.width(), 0))
        ani1.setEndValue(pos1)
        ani1.setDuration(1000)
        ani1.setEasingCurve(QEasingCurve.Type.OutQuint)
        QTimer.singleShot(550, lambda: self.groupBox_CMCLVersion.show())
        QTimer.singleShot(500, lambda: ani1.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
        ani1.finished.connect(lambda: self.verticalLayout.insertWidget(0, self.groupBox_CMCLVersion))
        
        ani2 = QPropertyAnimation(self.groupBox_authors, b"pos", self)
        ani2.setStartValue(pos2 + QPoint(self.width(), 0))
        ani2.setEndValue(pos2)
        ani2.setDuration(1000)
        ani2.setEasingCurve(QEasingCurve.Type.OutQuint)
        QTimer.singleShot(650, lambda: self.groupBox_authors.show())
        QTimer.singleShot(600, lambda: ani2.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
        ani2.finished.connect(lambda: self.verticalLayout.insertWidget(1, self.groupBox_authors))
        
        ani3 = QPropertyAnimation(self.groupBox_thanks, b"pos", self)
        ani3.setStartValue(pos3 + QPoint(self.width(), 0))
        ani3.setEndValue(pos3)
        ani3.setDuration(1000)
        ani3.setEasingCurve(QEasingCurve.Type.OutQuint)
        QTimer.singleShot(750, lambda: self.groupBox_thanks.show())
        QTimer.singleShot(700, lambda: ani3.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
        ani3.finished.connect(lambda: self.verticalLayout.insertWidget(2, self.groupBox_thanks))
        
        ani4 = QPropertyAnimation(self.groupBox_disclaimer, b"pos", self)
        ani4.setStartValue(pos4 + QPoint(self.width(), 0))
        ani4.setEndValue(pos4)
        ani4.setDuration(1000)
        ani4.setEasingCurve(QEasingCurve.Type.OutQuint)
        QTimer.singleShot(850, lambda: self.groupBox_disclaimer.show())
        QTimer.singleShot(800, lambda: ani4.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
        ani4.finished.connect(lambda: self.verticalLayout.insertWidget(3, self.groupBox_disclaimer))
        
        ani5 = QPropertyAnimation(self.groupBox_lawInfomation, b"pos", self)
        ani5.setStartValue(pos5 + QPoint(self.width(), 0))
        ani5.setEndValue(pos5)
        ani5.setDuration(1000)
        ani5.setEasingCurve(QEasingCurve.Type.OutQuint)
        QTimer.singleShot(950, lambda: self.groupBox_lawInfomation.show())
        QTimer.singleShot(900, lambda: ani5.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
        ani5.finished.connect(lambda: self.verticalLayout.insertWidget(4, self.groupBox_lawInfomation))


class OfflinePlayerCreationDialogue(MaskedDialogue):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(5, 32, 5, 5)
        
        self.playerNameInput = LineEdit(self)
        self.playerNameInput.setValidator(QRegularExpressionValidator(QRegularExpression(r"\w+"), self.playerNameInput))
        self.playerNameInput.setClearButtonEnabled(True)
        self.playerNameInput.returnPressed.connect(self.generatePlayer)
        self.verticalLayout.addWidget(self.playerNameInput)
        
        self.horizontalLayout = QHBoxLayout()
        
        self.OKButton = PushButton(self)
        self.OKButton.pressed.connect(self.generatePlayer)
        self.OKButton.setFocus()
        self.horizontalLayout.addWidget(self.OKButton)
        
        self.CancelButton = PushButton(self)
        self.CancelButton.pressed.connect(self.close)
        self.horizontalLayout.addWidget(self.CancelButton)
        
        self.verticalLayout.addLayout(self.horizontalLayout)
        
        self.retranslateUI()
    
    def retranslateUI(self):
        self.setWindowTitle("创建离线玩家")
        self.playerNameInput.setPlaceholderText("请输入玩家名")
        self.OKButton.setText("确定")
        self.CancelButton.setText("取消")
    
    def generatePlayer(self):
        player = create_offline_player(self.playerNameInput.text(), currentPlayer.player_hasMC)
        window.playerPageFrame.appendPlayer(player)
        self.close()


class PlayerPage(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        
        self.playerList = []
        self.currentIndex = 0
        self.isLogining = False
        
        self.actionsPanel = Panel(self)
        shadow = QGraphicsDropShadowEffect(self.actionsPanel)
        shadow.setBlurRadius(32)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 32))
        self.actionsPanel.setGraphicsEffect(shadow)
        self.horizontalLayout = QHBoxLayout(self.actionsPanel)
        
        self.selectPlayerButton = PushButton(self)
        self.horizontalLayout.addWidget(self.selectPlayerButton)
        
        self.addPlayerButton = PushButton(self)
        self.horizontalLayout.addWidget(self.addPlayerButton)
        
        self.horizontalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.horizontalLayout.addItem(self.horizontalSpacer)
        
        self.verticalLayout = QVBoxLayout(self)
        
        self.topPanel = Panel(self)
        self.topPanel.setMinimumHeight(84)
        self.verticalLayout.addWidget(self.topPanel)
        
        self.leftButton = ToolButton(self.topPanel)
        self.leftButton.setFixedSize(QSize(32, 32))
        
        self.middleButton = ToolButton(self.topPanel)
        self.middleButton.setMinimumWidth(128)
        
        self.rightButton = ToolButton(self.topPanel)
        self.rightButton.setFixedSize(QSize(32, 32))
        
        self.tableWidget = TableWidget(self)
        self.tableWidget.setHorizontalHeaderLabels(["玩家名称", "玩家账户类型", "是否购买 Minecraft"])
        self.tableWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableWidget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.verticalLayout.addWidget(self.tableWidget)
        
        app.registerRetranslateFunction(self.retranslateUI)
        self.retranslateUI()
        
        self.updatePlayerList()
    
    def retranslateUI(self):
        self.selectPlayerButton.setText("选择玩家")
        self.addPlayerButton.setText("创建/登录")
        menu = RoundedMenu(self.addPlayerButton)
        action1 = QAction(menu)
        action1.setText("登录 Microsoft 账户")
        action1.triggered.connect(self.loginMicrosoft)
        menu.addAction(action1)
        action2 = QAction(menu)
        action2.setText("创建离线玩家")
        action2.triggered.connect(self.createOfflinePlayer)
        menu.addAction(action2)
        self.addPlayerButton.setMenu(menu)
        
        self.leftButton.setToolTip("上一个")
        self.rightButton.setToolTip("下一个")
        
        if not self.isLogining and self.playerList:
            currentPlayer = self.playerList[self.currentIndex]
            self.middleButton.setText(
                f"{currentPlayer.player_playerName}\n类型：{'msa'}\n{'已购买 Minecraft' if currentPlayer.player_hasMC else '未购买 Minecraft'}")
        else:
            self.middleButton.setText("\n正在登录中\n")
        
        self.tableWidget.clear()
        self.tableWidget.setHorizontalHeaderLabels(["玩家名称", "玩家类型", "是否购买 Minecraft"])
        self.tableWidget.setColumnCount(3)
        
        self.tableWidget.setRowCount(len(self.playerList))
        for i, player in enumerate(self.playerList):
            self.tableWidget.setItem(i, 0, QTableWidgetItem(player.player_playerName))
            self.tableWidget.setItem(i, 1, QTableWidgetItem('msa'))
            self.tableWidget.setItem(i, 2, QTableWidgetItem("是" if player.player_hasMC else "否"))
    
    def setLogining(self, state):
        self.isLogining = bool(state)
        self.middleButton.setDisabled(self.isLogining)
        self.retranslateUI()
    
    def updatePlayer(self, player):
        self.playerList.append(player)
        self.setLogining(False)
        self.retranslateUI()
        self.updatePlayerList()
    
    def appendPlayer(self, player, select=True):
        self.playerList.append(player)
        if select:
            self.currentIndex = self.playerList.index(player)
            self.selectPlayer(player)
        self.retranslateUI()
        self.updatePlayerList()
    
    def selectPlayer(self, player=None):
        global currentPlayer
        if not player:
            player = self.playerList[self.currentIndex]
        if isinstance(player, str):
            for e, p in enumerate(self.playerList):
                if p.player_playerName == player and p != currentPlayer:
                    player = p
                    break
        if player and player in self.playerList:
            currentPlayer = player
            self.currentIndex = self.playerList.index(player)
        self.retranslateUI()
        self.updatePlayerList()
    
    def updatePlayerList(self):
        def parseName(name):
            for player in self.playerList:
                if player.player_playerName == name and player != currentPlayer:
                    self.selectPlayer(player)
                    break
        
        menu = QMenu(self.selectPlayerButton)
        menu.addAction("")
        
        listWidget = ListWidget(menu)
        listWidget.itemDoubleClicked.connect(lambda x: (parseName(x.text()), menu.close()))
        for player in self.playerList:
            item = QListWidgetItem(player.player_playerName, listWidget)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setSizeHint(QSize(0, 24))
            listWidget.addItem(item)
        
        listWidget.adjustSize()
        menu.setFixedSize(listWidget.size())
        self.selectPlayerButton.setMenu(menu)
    
    def loginMicrosoft(self):
        window = LoginWindow(self.window())
        window.show()
    
    def createOfflinePlayer(self):
        dialogue = OfflinePlayerCreationDialogue(self.window())
        dialogue.show()
    
    def mouseMoveEvent(self, a0):
        super().mouseMoveEvent(a0)
        
        if self.mapFromGlobal(QCursor.pos()).y() <= 15 or self.actionsPanel.underMouse():
            y = 10
            self.actionsPanel.raise_()
        else:
            y = -self.actionsPanel.height() - 10
        
        self.posAnimation = QPropertyAnimation(self.actionsPanel, b"pos", self)
        self.posAnimation.setStartValue(self.actionsPanel.pos())
        self.posAnimation.setEndValue(QPoint(30, y))
        self.posAnimation.setDuration(100)
        self.posAnimation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.posAnimation.start()
    
    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        
        if self.mapFromGlobal(QCursor.pos()).y() <= 10 or self.topPanel.underMouse():
            y = 10
        else:
            y = -self.topPanel.height() - 10
        
        self.posAnimation = QPropertyAnimation(self.actionsPanel, b"pos", self)
        self.posAnimation.setStartValue(self.actionsPanel.pos())
        self.posAnimation.setEndValue(QPoint(30, y))
        self.posAnimation.setDuration(100)
        self.posAnimation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.posAnimation.start()
        self.sizeAnimation = QPropertyAnimation(self.actionsPanel, b"size", self)
        self.sizeAnimation.setStartValue(self.actionsPanel.size())
        self.sizeAnimation.setEndValue(QSize(self.width() - 60, 62))
        self.sizeAnimation.setDuration(100)
        self.sizeAnimation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.sizeAnimation.start()
        
        self.leftButton.move(QPoint(16, (self.topPanel.height() // 2) - (self.leftButton.height() // 2)))
        self.rightButton.move(
            QPoint(
                self.topPanel.width() - self.rightButton.width() - 16,
                (self.topPanel.height() // 2) - (self.rightButton.height() // 2)
            )
        )
        
        self.middleButton.adjustSize()
        self.middleButton.setGeometry(QRect(
            self.topPanel.width() // 2 - self.middleButton.width() // 2,
            self.topPanel.height() // 2 - self.middleButton.height() // 2,
            self.middleButton.width(), self.middleButton.height()
        ))


class MainLauncherWindow(MainWindow):
    class ContentPanel(AnimatedStackedWidget, Panel):
        pass
    
    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)
        
        self.resize(800, 600)
        self.moveCentre()
        
        self.setWindowTitle("Common Minecraft Launcher")
        self.setWindowIcon(QIcon(":/CommonMinecraftLauncherIcon.svg"))
        
        self.topNavigationPanel = Panel(self)
        shadow = QGraphicsDropShadowEffect(self.topNavigationPanel)
        shadow.setBlurRadius(32)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 32))
        self.topNavigationPanel.setGraphicsEffect(shadow)
        
        self.horizontalLayout = QHBoxLayout(self.topNavigationPanel)
        self.homePage = ToolButton(self.topNavigationPanel)
        self.homePage.setFixedSize(QSize(42, 42))
        self.homePage.setCheckable(True)
        self.homePage.setChecked(True)
        self.homePage.setAutoExclusive(True)
        self.homePage.released.connect(lambda: self.setCurrentPage(0))
        self.homePage.setIcon(QIcon(""))
        self.homePage.setIconSize(QSize(32, 32))
        self.horizontalLayout.addWidget(self.homePage)
        self.downloadPage = ToolButton(self.topNavigationPanel)
        self.downloadPage.setFixedSize(QSize(42, 42))
        self.downloadPage.setCheckable(True)
        self.downloadPage.setAutoExclusive(True)
        self.downloadPage.released.connect(lambda: self.setCurrentPage(1))
        self.downloadPage.setIcon(QIcon(""))
        self.downloadPage.setIconSize(QSize(32, 32))
        self.horizontalLayout.addWidget(self.downloadPage)
        self.settingsPage = ToolButton(self.topNavigationPanel)
        self.settingsPage.setFixedSize(QSize(42, 42))
        self.settingsPage.setCheckable(True)
        self.settingsPage.setAutoExclusive(True)
        self.settingsPage.released.connect(lambda: self.setCurrentPage(2))
        self.settingsPage.setIcon(QIcon(""))
        self.settingsPage.setIconSize(QSize(32, 32))
        self.horizontalLayout.addWidget(self.settingsPage)
        self.aboutPage = ToolButton(self.topNavigationPanel)
        self.aboutPage.setFixedSize(QSize(42, 42))
        self.aboutPage.setCheckable(True)
        self.aboutPage.setAutoExclusive(True)
        self.aboutPage.released.connect(lambda: self.setCurrentPage(3))
        self.aboutPage.setIcon(QIcon(""))
        self.aboutPage.setIconSize(QSize(32, 32))
        self.horizontalLayout.addWidget(self.aboutPage)
        self.horizontalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.horizontalLayout.addItem(self.horizontalSpacer)
        self.playerPage = ToolButton(self.topNavigationPanel)
        self.playerPage.setFixedSize(QSize(42, 42))
        self.playerPage.setCheckable(True)
        self.playerPage.setAutoExclusive(True)
        self.playerPage.released.connect(lambda: self.setCurrentPage(4))
        self.playerPage.setIcon(QIcon(""))
        self.playerPage.setIconSize(QSize(32, 32))
        self.horizontalLayout.addWidget(self.playerPage)
        self.toggleTheme = ToolButton(self.topNavigationPanel)
        self.toggleTheme.setFixedSize(QSize(42, 42))
        self.toggleTheme.setIcon(QIcon(""))
        self.toggleTheme.setIconSize(QSize(32, 32))
        self.toggleTheme.pressed.connect(self.toggleThemeFunction)
        self.horizontalLayout.addWidget(self.toggleTheme)
        
        self.updateIcon()
        
        self.centralwidget = self.ContentPanel(self)
        
        self.homePageFrame = HomePage(self.centralwidget)
        self.centralwidget.addWidget(self.homePageFrame)
        
        self.downloadPageFrame = DownloadPage(self.centralwidget)
        self.centralwidget.addWidget(self.downloadPageFrame)
        
        self.settingsPageFrame = SettingsPage(self.centralwidget)
        self.centralwidget.addWidget(self.settingsPageFrame)
        
        self.aboutPageFrame = AboutPage(self.centralwidget)
        self.centralwidget.addWidget(self.aboutPageFrame)
        
        self.playerPageFrame = PlayerPage(self.centralwidget)
        self.centralwidget.addWidget(self.playerPageFrame)
        
        self.topNavigationPanel.raise_()
        self.topNavigationPanel.move(QPoint(30, self.height() + 10))
        
        self.centreColour = Colour(*settings["LauncherSettings"]["Personalisation"]["BackgroundColour"])
        self.posAnimation = None
        self.sizeAnimation = None
    
    def updateIcon(self):
        colour = "black" if getTheme() == Theme.Light else "white"
        self.homePage.setIcon(QIcon(f":/Home-{colour}.svg"))
        self.downloadPage.setIcon(QIcon(f":/Download-{colour}.svg"))
        self.settingsPage.setIcon(QIcon(f":/Settings-{colour}.svg"))
        self.aboutPage.setIcon(QIcon(f":/About-{colour}.svg"))
        self.playerPage.setIcon(QIcon(f":/user_icon-{colour}.svg"))
        self.toggleTheme.setIcon(QIcon(f":/light.svg" if colour == "black" else f":/dark.svg"))
    
    def postToggleTheme(self):
        self.updateIcon()
        self.homePageFrame.postToggleTheme()
    
    def moveCentre(self):
        screenGeometry = QGuiApplication.primaryScreen().geometry()
        pos = screenGeometry.center() - QPoint(self.width() // 2, self.height() // 2)
        self.move(pos)
    
    @staticmethod
    def toggleGlobalTheme():
        if getTheme() == Theme.Light:
            setTheme(Theme.Dark, True)
            settings["LauncherSettings"]["Personalisation"]["CurrentTheme"] = "Dark"
        elif getTheme() == Theme.Dark:
            setTheme(Theme.Light, True)
            settings["LauncherSettings"]["Personalisation"]["CurrentTheme"] = "Light"
        for window in QGuiApplication.allWindows():
            window.requestUpdate()
    
    def toggleThemeFunction(self):
        self.toggleGlobalTheme()
        self.postToggleTheme()
    
    def setCurrentPage(self, page_id=-1):
        page_seq = (self.homePage, self.downloadPage, self.settingsPage, self.aboutPage, self.playerPage)
        page_frame_dict = {
            self.homePage: self.homePageFrame,
            self.downloadPage: self.downloadPageFrame,
            self.settingsPage: self.settingsPageFrame,
            self.aboutPage: self.aboutPageFrame,
            self.playerPage: self.playerPageFrame
        }
        if -1 < page_id < len(page_seq):
            page = page_seq[page_id]
            page_frame = page_frame_dict[page]
            page.setChecked(True)
            self.centralwidget.setCurrentWidget(page_frame)
    
    def showEvent(self, a0):
        self.topNavigationPanel.move(QPoint(30, self.height() + 10))
        super().showEvent(a0)
    
    def leaveEvent(self, a0):
        super().leaveEvent(a0)
        if self.topNavigationPanel.y() >= self.height() + 10:
            return
        
        if self.posAnimation:
            self.posAnimation.stop()
            self.posAnimation.deleteLater()
        self.posAnimation = QPropertyAnimation(self.topNavigationPanel, b"pos", self)
        self.posAnimation.setStartValue(self.topNavigationPanel.pos())
        self.posAnimation.setEndValue(QPoint(30, self.height() + 10))
        self.posAnimation.setDuration(100)
        self.posAnimation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.posAnimation.start()
    
    def mouseMoveEvent(self, a0):
        super().mouseMoveEvent(a0)
        if hasattr(self, "posAnimation"):
            if self.mapFromGlobal(QCursor.pos()).y() >= self.height() - 35 or self.topNavigationPanel.underMouse():
                y = self.height() - 30 - 62
            else:
                y = self.height() + 10
            
            if (not self.posAnimation or self.posAnimation.endValue() != y) and y != self.topNavigationPanel.y():
                if self.posAnimation:
                    self.posAnimation.stop()
                    self.posAnimation.deleteLater()
                self.posAnimation = QPropertyAnimation(self.topNavigationPanel, b"pos", self)
                self.posAnimation.setStartValue(self.topNavigationPanel.pos())
                self.posAnimation.setEndValue(QPoint(30, y))
                self.posAnimation.setDuration(100)
                self.posAnimation.setEasingCurve(QEasingCurve.Type.OutQuad)
                self.posAnimation.start()
    
    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        if hasattr(self, "titleBar"):
            self.titleBar.setGeometry(QRect(0, 0, self.width(), self.height()))
        
        if hasattr(self, "posAnimation") and hasattr(self, "sizeAnimation"):
            if self.posAnimation:
                self.posAnimation.stop()
                self.posAnimation.deleteLater()
                self.posAnimation = None
            if self.sizeAnimation:
                self.sizeAnimation.stop()
                self.sizeAnimation.deleteLater()
                self.sizeAnimation = None
            
            if self.mapFromGlobal(QCursor.pos()).y() >= self.height() - 30 or self.topNavigationPanel.underMouse():
                y = self.height() - 30 - 62
            else:
                y = self.height() + 10
            
            self.posAnimation = QPropertyAnimation(self.topNavigationPanel, b"pos", self)
            self.posAnimation.setStartValue(self.topNavigationPanel.pos())
            self.posAnimation.setEndValue(QPoint(30, y))
            self.posAnimation.setDuration(100)
            self.posAnimation.setEasingCurve(QEasingCurve.Type.OutQuad)
            self.posAnimation.start()
            self.sizeAnimation = QPropertyAnimation(self.topNavigationPanel, b"size", self)
            self.sizeAnimation.setStartValue(self.topNavigationPanel.size())
            self.sizeAnimation.setEndValue(QSize(self.width() - 60, 62))
            self.sizeAnimation.setDuration(100)
            self.sizeAnimation.setEasingCurve(QEasingCurve.Type.OutQuad)
            self.sizeAnimation.start()
        
        if hasattr(self, "centralwidget"):
            self.centralwidget.setGeometry(QRect(35, 35, self.width() - 70, self.height() - 70))
    
    def paintEvent(self, a0):
        super().paintEvent(a0)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        gradient = QRadialGradient(QRectF(self.rect()).center(), min(self.width(), self.height()) / 2)
        gradient.setColorAt(0.0, self.centreColour)
        gradient.setColorAt(1.0, getBackgroundColour().darker(200))
        painter.fillRect(self.rect(), gradient)
        
        titleColour = getBackgroundColour()
        titleGradient = QLinearGradient(QPointF(0, 0), QPointF(0, self.titleBar.height()))
        titleGradient.setColorAt(0.0, Colour(*titleColour, 128))
        titleGradient.setColorAt(1.0, Colour(*titleColour, 32))
        painter.fillRect(self.titleBar.rect(), titleGradient)


def login_user(name_or_token=b"", is_refresh_login=False):
    try:
        playerDatas = json.loads(base64.b64decode(Path(".players").read_bytes()).decode())
    except:
        playerDatas = {}
    try:
        if is_refresh_login:
            token = base64.b64decode(
                playerDatas.get(name_or_token.decode(), {}).get("refreshToken", "").encode()).decode()
        else:
            token = name_or_token
        status, player, refresh_token = MicrosoftPlayerLogin(token, is_refresh_login)
        if is_refresh_login:
            data = playerDatas[player.player_playerName]
        else:
            data = {}
        data["accessToken"] = "eyJ" + base64.b64encode(player.player_accessToken[::-1].encode(), b"-\\").decode()
        data["refreshToken"] = base64.b64encode(refresh_token.encode()).decode()
        data["uuid"] = player.player_playerUUID
        playerDatas[player.player_playerName] = data
        Path(".players").write_bytes(base64.b64encode(json.dumps(playerDatas, indent=4).encode()))
        with open("current_user.DAT", "wb") as file:
            file.write(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" + r"\x0".join(
                [str(i) for i in list(
                    player.player_playerName)]).encode() + b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
        return player
    except requests.exceptions.ConnectionError as e:
        if is_refresh_login:
            data = playerDatas[name_or_token.decode()]
            accessToken = base64.b64encode(data["accessToken"][3:][::-1].encode(), b"-\\").decode()
            playerUUID = data["uuid"]
            return MicrosoftPlayer(name_or_token.decode(), playerUUID, accessToken, True)
        else:
            return MicrosoftPlayer(None, None, None, False)
    except:
        traceback.print_exc()
        return MicrosoftPlayer(None, None, None, False)


class LoginThread(QThread):
    loginFinished = pyqtSignal(MicrosoftPlayer)
    
    def run(self):
        try:
            data = Path("current_user.DAT").read_bytes().replace(
                b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00", b"").replace(br"\x0", b"")
            if not data:
                self.loginFinished.emit(MicrosoftPlayer(None, None, None, False))
                return
            data = login_user(data, True)
            self.loginFinished.emit(data)
        except FileNotFoundError:
            Path("current_user.DAT").touch(exist_ok=True)
            self.loginFinished.emit(MicrosoftPlayer(None, None, None, False))
        except:
            self.loginFinished.emit(MicrosoftPlayer(None, None, None, False))


def updatePlayer(data):
    global currentPlayer
    currentPlayer = data
    window.playerPageFrame.setLogining(False)
    window.playerPageFrame.updatePlayer(currentPlayer)


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
            try:
                function()
            except RuntimeError:
                self.removeRetranslateFunction(function)


Path("error.log").write_text("", encoding="utf-8")
Path("latest.log").write_text("", encoding="utf-8")


def excepthook(*args, **kwargs):
    exception_information = "".join(traceback.format_exception(*args, **kwargs))
    with Path("error.log").open("a", encoding="utf-8") as file:
        file.write(exception_information + "\n")


sys.excepthook = excepthook


def init():
    global app, window, currentPlayer, settings, minecraft_path, currentLanguage
    settings = loadSettings()
    
    match settings["LauncherSettings"]["Personalisation"]["CurrentTheme"]:
        case "Light":
            setTheme(Theme.Light)
        case "Dark":
            setTheme(Theme.Dark)
    
    minecraft_path = Path(settings["LauncherSettings"]["MinecraftPath"]).absolute()
    
    if os.environ.get("LANG"):
        currentLanguage = os.environ.get("LANG").split(".")[0]
    else:
        currentLanguage = subprocess.check_output(["powershell.exe", "(Get-WinSystemLocale).Name"]).decode().strip()
    currentLanguage = currentLanguage.lower().replace("_", "-")
    
    # QApplication.setDesktopSettingsAware(False)
    app = Application(sys.argv)
    font = QFont("HarmonyOS Sans SC", 10)
    font.setHintingPreference(QFont.HintingPreference.PreferFullHinting)
    app.setFont(font)
    currentPlayer = create_online_player(None, None, None, False)
    thread = LoginThread()
    thread.loginFinished.connect(updatePlayer)
    thread.start()
    window = MainLauncherWindow()
    window.playerPageFrame.setLogining(True)
    
    app.lastWindowClosed.connect(lambda: saveSettings(settings))


with Path("latest.log").open("w", encoding="utf-8") as out:
    with redirect_stdout(out), redirect_stderr(out):
        cProfile.run("init()", "initAnalysis.log")
        window.show()
        QTimer.singleShot(5000, lambda: out.flush())
        app.exec()
