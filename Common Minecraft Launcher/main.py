#!/usr/bin/env python3
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
import os
import re
import subprocess
import sys
import traceback
import tempfile
import webbrowser
import time
import shlex
import math

import random
import logging

from CMCLWidgets import *
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCharts import QChart, QChartView, QPieSeries

from CMCLCore.Launch import LaunchMinecraft, LaunchError
from CMCLCore.Login import MicrosoftPlayerLogin
from CMCLCore.Player import create_online_player, create_offline_player, MicrosoftPlayer
from CMCLCore.GetVersion import (GetVersionsByIterDirectory, GetVersionsByMojangAPI,
                                 GetMinecraftClientDownloadUrl, GetMinecraftServerDownloadUrl)
from CMCLCore.CMCLGameDownloading import DownloadMinecraft
from CMCLCore.GetOperationSystem import GetOperationSystemName
from CMCLCore.CMCLMirrorMappings import MirrorSourceName, MirrorSourceEnabled

import requests

import psutil

from CMCLModding.GetMods import GetMods, SearchMods, ListModVersions, GetOneMod
from CMCLModding.GetFabric import GetFabricLoaderVersions, GetFabricApiVersions
from CMCLModding.GetForge import GetNeoForgeVersions
from CMCLModding.DownloadMods import DownloadMod
from CMCLModding.DownloadFabric import DownloadFabricFull
from CMCLModding.DownloadForge import DownloadNeoForgeFull
from CMCLModding.ModManagement import GetLoader, GetLoaderType, ListMods

from CMCLSaveEditing.LevelDat import LoadData
import nbtlib

from CMCLPlayerManagement.GetAttribute import *
from CMCLPlayerManagement.SetAttribute import *

import resources
from launcherConfig import *
import json

import markdown2

CMCLVersion = ("AlphaDev-26002", "Alpha Development-26002")
minecraft_path = Path(".")

#                -------------------- Monospace --------------------  ---- Fallback ----
fixedFontList = ["Jetbrains Mono", "Consolas", "Ubuntu", "Monospace", "HarmonyOS Sans SC"]
fixedFont = QFont(fixedFontList)
fixedFont.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
fixedFont.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)

UIFontList = ["HarmonyOS Sans SC", "Segoe UI Emoji"]
UIFont = QFont(UIFontList)
UIFont.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
UIFont.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)

themeColourDefines = {
    "PresetBlue": {
        Theme.Light: {
            ColourRole.Background: {
                False: {
                    True: (163, 213, 255)
                },
                True: {
                    False: (203, 234, 255),
                    True: (223, 248, 255)
                }
            },
            ColourRole.Border: {
                False: {
                    True: (135, 206, 255)
                },
                True: {
                    False: (131, 182, 255),
                    True: (153, 203, 255)
                }
            }
        },
        Theme.Dark: {
            ColourRole.Background: {
                False: {
                    True: (80, 146, 255),
                },
                True: {
                    False: (87, 126, 219),
                    True: (94, 146, 255),
                }
            },
            ColourRole.Border: {
                False: {
                    True: (93, 167, 255)
                },
                True: {
                    False: (105, 157, 235),
                    True: (103, 163, 255)
                }
            },
        }
    },
    "PresetPink": {
        Theme.Light: {
            ColourRole.Background: {
                False: {
                    True: (255, 150, 220)
                },
                True: {
                    False: (253, 165, 235),
                    True: (255, 135, 235),
                }
            },
            ColourRole.Border: {
                False: {
                    True: (255, 150, 209)
                },
                True: {
                    False: (245, 153, 255),
                    True: (255, 125, 245)
                }
            }
        },
        Theme.Dark: {
            ColourRole.Background: {
                False: {
                    True: (255, 142, 193),
                },
                True: {
                    False: (193, 67, 153),
                    True: (255, 153, 165),
                }
            },
            ColourRole.Border: {
                False: {
                    True: (255, 79, 200)
                },
                True: {
                    False: (233, 103, 153),
                    True: (255, 153, 185),
                }
            }
        }
    },
    "PresetPurple": {
        Theme.Light: {
            ColourRole.Background: {
                False: {
                    True: (190, 150, 255)
                },
                True: {
                    False: (232, 165, 255),
                    True: (243, 175, 255)
                }
            },
            ColourRole.Border: {
                False: {
                    True: (163, 143, 255)
                },
                True: {
                    False: (195, 153, 255),
                    True: (207, 163, 255)
                }
            }
        },
        Theme.Dark: {
            ColourRole.Background: {
                False: {
                    True: (143, 102, 215),
                },
                True: {
                    False: (153, 105, 189),
                    True: (165, 98, 230)
                }
            },
            ColourRole.Border: {
                False: {
                    True: (132, 79, 208)
                },
                True: {
                    False: (183, 120, 201),
                    True: (195, 135, 250)
                }
            }
        }
    },
    "PresetRed": {
        Theme.Light: {
            ColourRole.Background: {
                False: {
                    True: (250, 176, 176)
                }
            },
            ColourRole.Border: {
                False: {
                    True: (250, 135, 135)
                }
            }
        },
        Theme.Dark: {
            ColourRole.Background: {
                False: {
                    True: (252, 142, 142),
                }
            },
            ColourRole.Border: {
                False: {
                    True: (254, 79, 79)
                }
            }
        }
    }
}

languagesCodeMapping = QFile(":/languagesCodeMapping.json")
languagesCodeMapping.open(QIODeviceBase.OpenModeFlag.ReadOnly)
languagesCodeMapping = json.loads(QTextStream(languagesCodeMapping).readAll())

if random.randint(3, 10) == 4:
    languagesCodeMapping["en-gb"] = "English (The United Kingdom of Great Britain and Northern Ireland)"


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
        if self.currentWidget() == w:
            return
        
        def func1():
            super(AnimatedStackedWidget, self).setCurrentWidget(w)
            if hasattr(self.currentWidget(), "changeAnimation"):
                self.currentWidget().changeAnimation("in", None)
        
        if hasattr(self.currentWidget(), "changeAnimation"):
            self.currentWidget().changeAnimation("out", func1)
        else:
            func1()


class LoadingAnimation(QWidget):
    class TransparencyAnimation(QVariantAnimation):
        def __init__(self, parent=None, variant="in"):
            super().__init__(parent)
            self.setStartValue(0)
            self.setEndValue(255)
            self.setDirection(
                QPropertyAnimation.Direction.Forward if variant == "in" else QPropertyAnimation.Direction.Backward)
            self.setDuration(1000)
            self.setEasingCurve(QEasingCurve.Type.OutQuad)
            self.valueChanged.connect(self.update_opacity)
        
        def update_opacity(self, value):
            colour = value
            self.parent().setProperty("backgroundOpacity", value)
    
    class SizingAnimation(QVariantAnimation):
        def __init__(self, parent=None, variant="in"):
            super().__init__(parent)
            size = parent.size()
            self.setStartValue(QSize(0, 0))
            self.setEndValue(size)
            self.setDirection(
                QPropertyAnimation.Direction.Forward if variant == "in" else QPropertyAnimation.Direction.Backward)
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
                    self.parent().property("beingRed")
                )
            )
            gradient.setColorAt(
                1.0,
                self.adjustRed(
                    getBackgroundColour(is_highlight=True),
                    self.parent().property("beingRed")
                )
            )
            painter.setPen(Qt.GlobalColor.transparent)
            painter.setBrush(QBrush(gradient))
            painter.drawEllipse(self.rect())
        
        @staticmethod
        def adjustRed(colour, percent=25):
            if not percent:
                return colour
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
        self.__reloadButton.setText(self.tr("LoadingAnimation.Actions.Reload.Text"))
        self.__reloadTextChanged = False
        self.__loadingTimer = QTimer(self)
        self.__loadingTimer.timeout.connect(self.__updateText)
        self.destroyed.connect(lambda: self.__loadingTimer.stop())
        self.__counter = 0
        self.hide()
        app.registerRetranslateFunction(self.retranslateUI)
        
        self.setProperty("beingRed", 0)
        self.setProperty("backgroundOpacity", 255)
        self.setProperty("backgroundClipPath", None)
    
    def retranslateUI(self):
        if not self.__reloadTextChanged:
            self.__reloadButton.setText(self.tr("LoadingAnimation.Actions.Reload.Text"))
    
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
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self.property("backgroundClipPath"):
            painter.setPen(Colour(*self.__centreAnimation.adjustRed(getBackgroundColour(), self.property("beingRed")),
                                  self.property("backgroundOpacity")))
            painter.setBrush(Colour(*self.__centreAnimation.adjustRed(getBackgroundColour(), self.property("beingRed")),
                                    self.property("backgroundOpacity")))
            painter.drawPath(self.property("backgroundClipPath"))
        else:
            painter.fillRect(self.rect(),
                             Colour(*self.__centreAnimation.adjustRed(getBackgroundColour(), self.property("beingRed")),
                                    self.property("backgroundOpacity")))
    
    def __updateText(self):
        self.__counter += 1
        self.__statusLabel.setText(self.tr("LoadingAnimation.Status.Loading.Text") + "." * (self.__counter % 7))
    
    def start(self, ani=True):
        self.__centreAnimation.setFixedSize(96, 96)
        self.__centreAnimation.setError(False)
        self.__statusLabel.setText(self.tr("LoadingAnimation.Status.Loading.Text"))
        self.__reloadButton.hide()
        self.__reloadButton.setDown(False)
        if ani:
            self.TransparencyAnimation(self, "in").start()
            self.SizingAnimation(self.__centreAnimation, "in").start()
        self.__counter = 0
        self.__loadingTimer.start(1000)
        self.show()
        if self.property("beingRed"):
            ani = QPropertyAnimation(self, b"beingRed", self)
            ani.setStartValue(self.property("beingRed"))
            ani.setEndValue(0)
            ani.setDuration(500)
            ani.start()
    
    def finish(self, ani=True, failed=False):
        try:
            self.__loadingTimer.moveToThread(self.thread())
            self.__loadingTimer.stop()
            if not failed:
                if ani:
                    self.TransparencyAnimation(self, "out").start()
                    self.SizingAnimation(self.__centreAnimation, "out").start()
                    QTimer.singleShot(1000, lambda: self.hide())
                else:
                    self.hide()
                self.__statusLabel.setText(self.tr("LoadingAnimation.Status.LoadingSuccess.Text"))
            else:
                self.__statusLabel.setText(self.tr("LoadingAnimation.Status.Failure.Text"))
                self.__reloadButton.show()
                self.__centreAnimation.setError()
                ani = QPropertyAnimation(self, b"beingRed", self)
                ani.setStartValue(self.property("beingRed"))
                ani.setEndValue(50)
                ani.setDuration(500)
                ani.start()
        except RuntimeError:
            pass
    
    def addReloadFunction(self, function):
        self.__reloadButton.pressed.connect(function)
    
    def setReloadText(self, text):
        self.__reloadButton.setText(text)
        self.__reloadTextChanged = True
    
    def setBackgroundClipPath(self, backgroundClipPath):
        self.setProperty("backgroundClipPath", backgroundClipPath)
    
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
                window.playerPageFrame.setLoggingIn(True)
                datas = login_user(bytes(self.token, encoding="utf-8"))
                updatePlayer(datas)
            except:
                traceback.print_exc()
            window.playerPageFrame.setLoggingIn(False)
            self.loginFinished.emit()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("LoginWindow.Title.Text"))
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
            pos = re.search(r"code=(.+?)&", self.view.url().toString())
            if pos:
                code = pos.group(1)
                token = code.split("=")[1]
                token = token.split("&")[0]
                thread = self.LoginThread(token, self.window())
                thread.start()
                self.progress.finish(ani=False)
                self.close()
    
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


class HomePage(QFrame):
    class VersionManagementPage(QWidget):
        minecraft_path_changed = pyqtSignal()
        
        class VersionInfoPage(AcrylicBackground):
            class RightPanel(AnimatedStackedWidget, Panel):
                pass
            
            class GeneralPage(QFrame):
                def __init__(self, parent, version):
                    super().__init__(parent)
                    self.version = version
                    
                    versionConfig = Path(minecraft_path / "versions" / version / "version.cfg")
                    if versionConfig.exists():
                        self.cfg = yaml.safe_load(Path(versionConfig).read_text(encoding="utf-8"))
                    else:
                        createVersionConfigFile(minecraft_path / "versions" / version, self.version,
                                                self.version, ":/missingno.png")
                        self.cfg = yaml.safe_load(Path(versionConfig).read_text(encoding="utf-8"))
                    
                    self.versionName = self.cfg["Version"]
                    self.versionAlias = self.cfg["VersionAlias"]
                    if self.versionName == self.versionAlias:
                        self.versionAlias = None
                    
                    self.mainLayout = QVBoxLayout(self)
                    
                    self.scrollArea = ScrollArea(self)
                    self.mainLayout.addWidget(self.scrollArea)
                    
                    self.scrollAreaWidgetContents = QWidget()
                    
                    self.verticalLayout = QVBoxLayout(self.scrollAreaWidgetContents)
                    
                    self.versionInfoCard = Panel(self.scrollAreaWidgetContents)
                    self.verticalLayout.addWidget(self.versionInfoCard)
                    
                    self.horizontalLayout = QHBoxLayout(self.versionInfoCard)
                    
                    self.iconWidget = ImageWidget(self.versionInfoCard)
                    self.iconWidget.setFixedSize(QSize(64, 64))
                    self.iconWidget.setImage(QImage(self.cfg["Personalisation"]["Icon"]))
                    self.horizontalLayout.addWidget(self.iconWidget)
                    
                    self.versionInfoLabel = Label(self.versionInfoCard)
                    self.horizontalLayout.addWidget(self.versionInfoLabel)
                    
                    self.versionPersonalisation = None
                    
                    self.versionShortcuts = GroupBox(self.scrollAreaWidgetContents)
                    self.verticalLayout.addWidget(self.versionShortcuts)
                    
                    self.gridLayout = QGridLayout(self.versionShortcuts)
                    
                    self.openVersionInstallationDir = CommandLinkButton(self.versionShortcuts)
                    self.openVersionInstallationDir.pressed.connect(self.doOpenVersionInstallationDir)
                    self.gridLayout.addWidget(self.openVersionInstallationDir)
                    
                    self.openMinecraftDirectory = CommandLinkButton(self.versionShortcuts)
                    self.gridLayout.addWidget(self.openMinecraftDirectory)
                    
                    self.openSettingsFile = CommandLinkButton(self.versionShortcuts)
                    self.gridLayout.addWidget(self.openSettingsFile)
                    
                    self.verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
                    self.verticalLayout.addItem(self.verticalSpacer)
                    
                    self.scrollArea.setWidget(self.scrollAreaWidgetContents)
                    self.scrollArea.setWidgetResizable(True)
                    
                    app.registerRetranslateFunction(self.retranslateUI)
                    self.retranslateUI()
                
                def retranslateUI(self):
                    versionNameDisplay = self.versionName
                    if self.versionAlias:
                        versionNameDisplay = f"{self.versionAlisa} ({self.versionName})"
                    self.versionInfoLabel.setText(f"{versionNameDisplay}")
                    self.versionShortcuts.setTitle(self.tr(
                        "HomePage.VersionManagementPage.VersionInfoPage.GeneralPage.VersionShortcuts.Title"))  # 版本快捷方式
                    self.openVersionInstallationDir.setText(self.tr(
                        "HomePage.VersionManagementPage.VersionInfoPage.GeneralPage.VersionShortcuts.OpenVersionInstallationDir.Text"))  # 打开版本下载文件夹
                    self.openVersionInstallationDir.setToolTip(self.tr(
                        "HomePage.VersionManagementPage.VersionInfoPage.GeneralPage.VersionShortcuts.OpenVersionInstallationDir.ToolTip"))  # 如果你开启了版本隔离，这也是游戏的运行目录。
                    self.openMinecraftDirectory.setText("打开游戏主文件夹")
                    self.openMinecraftDirectory.setToolTip(
                        "这个文件夹有版本文件夹 <code>versions/...</code>。<br>"
                        "如果没有开启版本隔离的话，这个文件夹里面还会有存档文件夹 <code>saves</code>，资源包文件夹 <code>resourcepacks</code> ")
                    self.openSettingsFile.setText("打开设置文件")
                    self.openSettingsFile.setToolTip(
                        "如果想要修改设置，除了打开游戏，还可以编辑 <code>options.txt</code> 文件。<br>"
                        "如果看不懂什么意思，请自行上网查资料。")
                
                def doOpenVersionInstallationDir(self):
                    if platform.system().lower() == "windows":
                        os.startfile(str((minecraft_path / 'versions' / self.version).absolute()))
                    elif platform.system().lower() == "linux":
                        os.system(
                            f"xdg-open {shlex.quote(str((minecraft_path / 'versions' / self.version).absolute()))}")
                
                def changeAnimation(self, variant, function):
                    if variant == "in":
                        self.changeAnimationIn()
                    else:
                        QTimer.singleShot(300, function)
                        self.changeAnimationOut()
                
                def changeAnimationIn(self):
                    ani1 = QPropertyAnimation(self.versionInfoCard, b"pos", self)
                    pos1 = self.versionInfoCard.pos()
                    ani1.setStartValue(pos1 + QPoint(100, 0))
                    ani1.setEndValue(pos1)
                    ani1.setDuration(500)
                    ani1.setEasingCurve(QEasingCurve.Type.OutQuint)
                    ani1.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                    ani11 = OpacityAnimation(self.versionInfoCard)
                    ani11.setStartValue(0)
                    ani11.setEndValue(100)
                    ani11.setDuration(500)
                    ani11.setEasingCurve(QEasingCurve.Type.OutQuint)
                    ani11.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                    QTimer.singleShot(50, lambda: self.versionInfoCard.show())
                    # ani2 = QPropertyAnimation(self.versionInfoCard, b"pos", self)
                    # pos2 = self.versionInfoCard.pos()
                    # ani2.setStartValue(pos1 + QPoint(100, 0))
                    # ani2.setEndValue(pos1)
                    # ani2.setDuration(500)
                    # ani2.setEasingCurve(QEasingCurve.Type.OutQuint)
                    # QTimer.singleShot(100, lambda: ani2.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
                    # ani22 = OpacityAnimation(self.versionInfoCard)
                    # ani22.setStartValue(0)
                    # ani22.setEndValue(100)
                    # ani22.setDuration(500)
                    # ani22.setEasingCurve(QEasingCurve.Type.OutQuint)
                    # QTimer.singleShot(100, lambda: ani22.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
                    # QTimer.singleShot(150, lambda: self.versionInfoCard.show())
                    ani3 = QPropertyAnimation(self.versionShortcuts, b"pos", self)
                    pos3 = self.versionShortcuts.pos()
                    ani3.setStartValue(pos3 + QPoint(100, 0))
                    ani3.setEndValue(pos3)
                    ani3.setDuration(500)
                    ani3.setEasingCurve(QEasingCurve.Type.OutQuint)
                    QTimer.singleShot(200, lambda: ani3.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
                    ani33 = OpacityAnimation(self.versionShortcuts)
                    ani33.setStartValue(0)
                    ani33.setEndValue(100)
                    ani33.setDuration(500)
                    ani33.setEasingCurve(QEasingCurve.Type.OutQuint)
                    QTimer.singleShot(200, lambda: ani33.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
                    QTimer.singleShot(250, lambda: self.versionShortcuts.show())
                
                def changeAnimationOut(self):
                    ani11 = OpacityAnimation(self.versionInfoCard)
                    ani11.setStartValue(100)
                    ani11.setEndValue(0)
                    ani11.setDuration(500)
                    ani11.setEasingCurve(QEasingCurve.Type.OutQuint)
                    ani11.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                    ani11.finished.connect(lambda: self.versionInfoCard.hide())
                    # ani11 = OpacityAnimation(self.versionInfoCard)
                    # ani11.setStartValue(100)
                    # ani11.setEndValue(0)
                    # ani11.setDuration(500)
                    # ani11.setEasingCurve(QEasingCurve.Type.OutQuint)
                    # ani11.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                    # ani11.finished.connect(lambda: self.versionInfoCard.hide())
                    ani33 = OpacityAnimation(self.versionShortcuts)
                    ani33.setStartValue(100)
                    ani33.setEndValue(0)
                    ani33.setDuration(500)
                    ani33.setEasingCurve(QEasingCurve.Type.OutQuint)
                    ani33.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                    ani33.finished.connect(lambda: self.versionShortcuts.hide())
            
            class VerSettingsPage(QFrame):
                def __init__(self, parent, version):
                    super().__init__(parent)
                    self.version = version
                
                def changeAnimation(self, variant, function):
                    if variant == "in":
                        self.changeAnimationIn()
                    else:
                        QTimer.singleShot(300, function)
                        self.changeAnimationOut()
                
                def changeAnimationIn(self):
                    pass
                    # ani1 = QPropertyAnimation(self.versionInfoCard, b"pos", self)
                    # pos1 = self.versionInfoCard.pos()
                    # ani1.setStartValue(pos1 + QPoint(100, 0))
                    # ani1.setEndValue(pos1)
                    # ani1.setDuration(500)
                    # ani1.setEasingCurve(QEasingCurve.Type.OutQuint)
                    # ani1.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                    # ani11 = OpacityAnimation(self.versionInfoCard)
                    # ani11.setStartValue(0)
                    # ani11.setEndValue(100)
                    # ani11.setDuration(500)
                    # ani11.setEasingCurve(QEasingCurve.Type.OutQuint)
                    # ani11.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                    # QTimer.singleShot(50, lambda: self.versionInfoCard.show())
                    # # ani2 = QPropertyAnimation(self.versionInfoCard, b"pos", self)
                    # # pos2 = self.versionInfoCard.pos()
                    # # ani2.setStartValue(pos1 + QPoint(100, 0))
                    # # ani2.setEndValue(pos1)
                    # # ani2.setDuration(500)
                    # # ani2.setEasingCurve(QEasingCurve.Type.OutQuint)
                    # # QTimer.singleShot(100, lambda: ani2.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
                    # # ani22 = OpacityAnimation(self.versionInfoCard)
                    # # ani22.setStartValue(0)
                    # # ani22.setEndValue(100)
                    # # ani22.setDuration(500)
                    # # ani22.setEasingCurve(QEasingCurve.Type.OutQuint)
                    # # QTimer.singleShot(100, lambda: ani22.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
                    # # QTimer.singleShot(150, lambda: self.versionInfoCard.show())
                    # ani3 = QPropertyAnimation(self.versionShortcuts, b"pos", self)
                    # pos3 = self.versionShortcuts.pos()
                    # ani3.setStartValue(pos3 + QPoint(100, 0))
                    # ani3.setEndValue(pos3)
                    # ani3.setDuration(500)
                    # ani3.setEasingCurve(QEasingCurve.Type.OutQuint)
                    # QTimer.singleShot(200, lambda: ani3.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
                    # ani33 = OpacityAnimation(self.versionShortcuts)
                    # ani33.setStartValue(0)
                    # ani33.setEndValue(100)
                    # ani33.setDuration(500)
                    # ani33.setEasingCurve(QEasingCurve.Type.OutQuint)
                    # QTimer.singleShot(200, lambda: ani33.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
                    # QTimer.singleShot(250, lambda: self.versionShortcuts.show())
                
                def changeAnimationOut(self):
                    pass
                    # ani11 = OpacityAnimation(self.versionInfoCard)
                    # ani11.setStartValue(100)
                    # ani11.setEndValue(0)
                    # ani11.setDuration(500)
                    # ani11.setEasingCurve(QEasingCurve.Type.OutQuint)
                    # ani11.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                    # ani11.finished.connect(lambda: self.versionInfoCard.hide())
                    # # ani11 = OpacityAnimation(self.versionInfoCard)
                    # # ani11.setStartValue(100)
                    # # ani11.setEndValue(0)
                    # # ani11.setDuration(500)
                    # # ani11.setEasingCurve(QEasingCurve.Type.OutQuint)
                    # # ani11.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                    # # ani11.finished.connect(lambda: self.versionInfoCard.hide())
                    # ani33 = OpacityAnimation(self.versionShortcuts)
                    # ani33.setStartValue(100)
                    # ani33.setEndValue(0)
                    # ani33.setDuration(500)
                    # ani33.setEasingCurve(QEasingCurve.Type.OutQuint)
                    # ani33.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                    # ani33.finished.connect(lambda: self.versionShortcuts.hide())
            
            class ModConfigPage(QFrame):
                def __init__(self, parent, version):
                    super().__init__(parent)
                    self.version = version
                    self.loader = GetLoader(minecraft_path, version)
                    
                    self.verticalLayout = QVBoxLayout(self)
                    
                    self.topPanel = Panel(self)
                    self.verticalLayout.addWidget(self.topPanel)
                    
                    self.verticalLayout_2 = QVBoxLayout(self.topPanel)
                    
                    self.modCount = Label(self.topPanel)
                    self.verticalLayout_2.addWidget(self.modCount)
                    
                    self.horizontalLayout = QHBoxLayout()
                    self.verticalLayout_2.addLayout(self.horizontalLayout)
                    
                    self.enableAll = PushButton(self.topPanel)
                    self.enableAll.pressed.connect(lambda: self.enableSelectedMods(-1))
                    self.horizontalLayout.addWidget(self.enableAll)
                    
                    self.disableAll = PushButton(self.topPanel)
                    self.disableAll.pressed.connect(lambda: self.disableSelectedMods(-1))
                    self.horizontalLayout.addWidget(self.disableAll)
                    
                    self.updateAll = PushButton(self.topPanel)
                    self.updateAll.setDisabled(True)  # Since we haven't already written this function.
                    self.horizontalLayout.addWidget(self.updateAll)
                    
                    self.selectAll = PushButton(self.topPanel)
                    self.selectAll.pressed.connect(self.selectAllMods)
                    self.horizontalLayout.addWidget(self.selectAll)
                    
                    self.horizontalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding,
                                                        QSizePolicy.Policy.Preferred)
                    self.horizontalLayout.addItem(self.horizontalSpacer)
                    
                    self.listWidget = ListWidget(self)
                    self.listWidget.setSelectionMode(ListWidget.SelectionMode.MultiSelection)
                    self.listWidget.itemSelectionChanged.connect(self.itemSelectionChanged)
                    self.verticalLayout.addWidget(self.listWidget, 1)
                    
                    self.bottomPanel = Panel(self)
                    self.verticalLayout_3 = QVBoxLayout(self.bottomPanel)
                    
                    self.selectedModCount = Label(self.bottomPanel)
                    self.verticalLayout_3.addWidget(self.selectedModCount)
                    
                    self.horizontalLayout_2 = QHBoxLayout()
                    self.verticalLayout_3.addLayout(self.horizontalLayout_2)
                    
                    self.enableSelected = PushButton(self.bottomPanel)
                    self.enableSelected.pressed.connect(lambda: self.enableSelectedMods(0))
                    self.horizontalLayout_2.addWidget(self.enableSelected)
                    
                    self.disableSelected = PushButton(self.bottomPanel)
                    self.disableSelected.pressed.connect(lambda: self.disableSelectedMods(0))
                    self.horizontalLayout_2.addWidget(self.disableSelected)
                    
                    self.bottomPanel.adjustSize()
                    self.bottomPanel.move(0, self.height() + self.bottomPanel.height() + 10)
                    
                    self.bottomPanelAnimation = None
                    
                    self.enabledModsCount = 0
                    self.disabledModsCount = 0
                    self.selectedModsCount = 0
                    self.mods = []
                    
                    if not self.loader:
                        self.topPanel.hide()
                        self.listWidget.hide()
                        self.noLoader = Label(self)
                        self.noLoader.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    else:
                        self.noLoader = None
                        self.loadModList()
                    
                    app.registerRetranslateFunction(self.retranslateUI)
                    self.retranslateUI()
                    
                    self.displayMods()
                
                def retranslateUI(self):
                    selectedItems = self.listWidget.selectedItems()
                    self.modCount.setText(
                        f'共 <span style="color: skyblue">{len(self.mods)}</span> 个模组，启用：<span style="color: green">{self.enabledModsCount}</span> / 禁用：<span style="color: red">{self.disabledModsCount}</span>')
                    self.enableAll.setText("启用全部")
                    self.disableAll.setText("禁用全部")
                    self.updateAll.setText("全部升级（暂未支持）")
                    self.selectAll.setText("全选" if len(selectedItems) != self.listWidget.count() else "全不选")
                    self.selectedModCount.setText(
                        f"已选择 <span style=\"color: skyblue\">{len(selectedItems)}</span> 个模组")
                    self.enableSelected.setText("启用选中")
                    self.disableSelected.setText("禁用选中")
                    if self.noLoader:
                        self.noLoader.setText(
                            "<span style='color: red; font-size: 20px'>未安装模组加载器</span><br>该版本为原版。请先前往下载页面，安装模组加载器。<br>如果你确信是启动器检测模组加载器的问题，可以提交 Issue。")
                
                def displayMods(self):
                    if not self.loader:
                        return
                    for mod in self.mods:
                        name = mod.getModInfo()['name']
                        version = mod.getModInfo()['version']
                        displayName = f"{name}\n{version}"
                        if not mod.isEnabled:
                            displayName = f"（已禁用）{displayName}"
                        item = QListWidgetItem(displayName)
                        item.setData(1, mod)
                        self.listWidget.addItem(item)
                    self.retranslateUI()
                
                def loadModList(self):
                    if not self.loader:
                        return
                    self.mods = []
                    for mod in ListMods(minecraft_path):
                        self.mods.append(mod)
                        if mod.isEnabled:
                            self.enabledModsCount += 1
                        else:
                            self.disabledModsCount += 1
                    self.retranslateUI()
                
                def selectAllMods(self):
                    selected = len(self.listWidget.selectedItems()) != self.listWidget.count()
                    for i in range(self.listWidget.count()):
                        item = self.listWidget.item(i)
                        item.setSelected(selected)
                
                def deselectAll(self):
                    for i in range(self.listWidget.count()):
                        item = self.listWidget.item(i)
                        item.setSelected(False)
                
                def itemSelectionChanged(self):
                    selectedItems = self.listWidget.selectedItems()
                    if len(selectedItems) and self.bottomPanel.y() > self.height():
                        self.bottomPanelPopup()
                    elif not len(selectedItems) and self.bottomPanel.y() <= self.height():
                        self.bottomPanelClose()
                    self.retranslateUI()
                
                def enableSelectedMods(self, items=-1):
                    if items == 0:
                        items = self.listWidget.selectedItems()
                    elif items == -1:
                        items = [self.listWidget.item(item) for item in range(self.listWidget.count())]
                    for item in items:
                        mod = item.data(1)
                        mod.isEnabled = True
                        modFile = mod.modFile
                        if modFile.suffixes[-2:] == [".jar", ".disabled"]:
                            newModFile = modFile.parent / modFile.stem  # remove the last suffix `.disabled`
                            modFile.rename(newModFile)
                            mod.modFile = newModFile
                        self.disabledModsCount = max(0, self.disabledModsCount - 1)
                        self.enabledModsCount = min(self.listWidget.count(), self.enabledModsCount + 1)
                    self.deselectAll()
                    self.displayMods()
                
                def disableSelectedMods(self, items=-1):
                    if items == 0:
                        items = self.listWidget.selectedItems()
                    elif items == -1:
                        items = [self.listWidget.item(item) for item in range(self.listWidget.count())]
                    for item in items:
                        mod = item.data(1)
                        mod.isEnabled = False
                        modFile = mod.modFile
                        if modFile.suffix == ".jar":
                            newModFile = modFile.with_suffix(".jar.disabled")
                            modFile.rename(newModFile)
                            mod.modFile = newModFile
                        self.enabledModsCount = max(0, self.enabledModsCount - 1)
                        self.disabledModsCount = min(self.listWidget.count(), self.disabledModsCount + 1)
                    self.deselectAll()
                    self.displayMods()
                
                def resizeEvent(self, event):
                    super().resizeEvent(event)
                    if hasattr(self, "noLoader") and self.noLoader:
                        self.noLoader.setFixedWidth(self.width())
                        self.noLoader.setFixedHeight(self.height())
                    self.bottomPanel.adjustSize()
                    self.bottomPanel.move(self.width() // 2 - self.bottomPanel.width() // 2,
                                          self.height() + self.bottomPanel.height() + 10)
                
                def bottomPanelPopup(self):
                    if self.bottomPanelAnimation:
                        self.bottomPanelAnimation.stop()
                        self.bottomPanelAnimation.deleteLater()
                        del self.bottomPanelAnimation
                    self.bottomPanelAnimation = QPropertyAnimation(self.bottomPanel, b"pos", self)
                    self.bottomPanelAnimation.setStartValue(self.bottomPanel.pos())
                    self.bottomPanelAnimation.setEndValue(
                        QPoint(self.bottomPanel.x(), self.height() - self.bottomPanel.height() - 10))
                    self.bottomPanelAnimation.setDuration(100)
                    self.bottomPanelAnimation.setEasingCurve(QEasingCurve.Type.OutQuad)
                    self.bottomPanelAnimation.start()
                
                def bottomPanelClose(self):
                    if self.bottomPanelAnimation:
                        self.bottomPanelAnimation.stop()
                        self.bottomPanelAnimation.deleteLater()
                        del self.bottomPanelAnimation
                    self.bottomPanelAnimation = QPropertyAnimation(self.bottomPanel, b"pos", self)
                    self.bottomPanelAnimation.setStartValue(self.bottomPanel.pos())
                    self.bottomPanelAnimation.setEndValue(
                        QPoint(self.bottomPanel.x(), self.height() + self.bottomPanel.height() + 10))
                    self.bottomPanelAnimation.setDuration(100)
                    self.bottomPanelAnimation.setEasingCurve(QEasingCurve.Type.OutQuad)
                    self.bottomPanelAnimation.start()
                
                def changeAnimation(self, variant, function):
                    if not self.loader:
                        if function:
                            function()
                        return
                    if variant == "in":
                        self.changeAnimationIn()
                    else:
                        QTimer.singleShot(300, function)
                        self.changeAnimationOut()
                
                def changeAnimationIn(self):
                    if not self.loader:
                        return
                    ani1 = QPropertyAnimation(self.topPanel, b"pos", self)
                    pos1 = self.topPanel.pos()
                    ani1.setStartValue(pos1 + QPoint(100, 0))
                    ani1.setEndValue(pos1)
                    ani1.setDuration(500)
                    ani1.setEasingCurve(QEasingCurve.Type.OutQuint)
                    ani1.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                    ani11 = OpacityAnimation(self.topPanel)
                    ani11.setStartValue(0)
                    ani11.setEndValue(100)
                    ani11.setDuration(500)
                    ani11.setEasingCurve(QEasingCurve.Type.OutQuint)
                    ani11.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                    QTimer.singleShot(50, lambda: self.topPanel.show())
                    ani2 = QPropertyAnimation(self.listWidget, b"pos", self)
                    pos2 = self.listWidget.pos()
                    ani2.setStartValue(pos2 + QPoint(100, 0))
                    ani2.setEndValue(pos2)
                    ani2.setDuration(500)
                    ani2.setEasingCurve(QEasingCurve.Type.OutQuint)
                    QTimer.singleShot(100, lambda: ani2.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
                    ani22 = OpacityAnimation(self.listWidget)
                    ani22.setStartValue(0)
                    ani22.setEndValue(100)
                    ani22.setDuration(500)
                    ani22.setEasingCurve(QEasingCurve.Type.OutQuint)
                    QTimer.singleShot(100, lambda: ani22.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
                    QTimer.singleShot(150, lambda: self.listWidget.show())
                    # ani3 = QPropertyAnimation(self.versionShortcuts, b"pos", self)
                    # pos3 = self.versionShortcuts.pos()
                    # ani3.setStartValue(pos3 + QPoint(100, 0))
                    # ani3.setEndValue(pos3)
                    # ani3.setDuration(500)
                    # ani3.setEasingCurve(QEasingCurve.Type.OutQuint)
                    # QTimer.singleShot(200, lambda: ani3.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
                    # ani33 = OpacityAnimation(self.versionShortcuts)
                    # ani33.setStartValue(0)
                    # ani33.setEndValue(100)
                    # ani33.setDuration(500)
                    # ani33.setEasingCurve(QEasingCurve.Type.OutQuint)
                    # QTimer.singleShot(200, lambda: ani33.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
                    # QTimer.singleShot(250, lambda: self.versionShortcuts.show())
                
                def changeAnimationOut(self):
                    if not self.loader:
                        return
                    ani11 = OpacityAnimation(self.topPanel)
                    ani11.setStartValue(100)
                    ani11.setEndValue(0)
                    ani11.setDuration(500)
                    ani11.setEasingCurve(QEasingCurve.Type.OutQuint)
                    ani11.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                    ani11.finished.connect(lambda: self.topPanel.hide())
                    ani22 = OpacityAnimation(self.listWidget)
                    ani22.setStartValue(100)
                    ani22.setEndValue(0)
                    ani22.setDuration(500)
                    ani22.setEasingCurve(QEasingCurve.Type.OutQuint)
                    ani22.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                    ani22.finished.connect(lambda: self.listWidget.hide())
                    # ani33 = OpacityAnimation(self.versionShortcuts)
                    # ani33.setStartValue(100)
                    # ani33.setEndValue(0)
                    # ani33.setDuration(500)
                    # ani33.setEasingCurve(QEasingCurve.Type.OutQuint)
                    # ani33.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                    # ani33.finished.connect(lambda: self.versionShortcuts.hide())
            
            def __init__(self, parent, version):
                super().__init__(parent, getBackgroundColour(), QColor(0, 0, 255, 200), 10)
                self.setMouseTracking(True)
                self.version = version
                
                self.closeButton = CloseButton(self)
                self.closeButton.move(QPoint(3, 3))
                self.closeButton.hide()
                self.closeButton.pressed.connect(self.parent().closeVersionInfoPage)
                self.setProperty("closeButtonOpacity", 0.0)
                
                self.horizontalLayout = QHBoxLayout(self)
                
                self.leftPanel = Panel(self)
                self.horizontalLayout.addWidget(self.leftPanel)
                
                self.verticalLayout = QVBoxLayout(self.leftPanel)
                
                self.generalPage = PushButton(self.leftPanel)
                self.generalPage.setWidgetAttribute("outlinedButton")
                self.generalPage.setCheckable(True)
                self.generalPage.setChecked(True)
                self.generalPage.setAutoExclusive(True)
                self.generalPage.released.connect(lambda: self.setCurrentPage(0))
                self.verticalLayout.addWidget(self.generalPage)
                
                self.verSettingsPage = PushButton(self.leftPanel)
                self.verSettingsPage.setWidgetAttribute("outlinedButton")
                self.verSettingsPage.setCheckable(True)
                self.verSettingsPage.setAutoExclusive(True)
                self.verSettingsPage.released.connect(lambda: self.setCurrentPage(1))
                self.verticalLayout.addWidget(self.verSettingsPage)
                
                self.modConfigPage = PushButton(self.leftPanel)
                self.modConfigPage.setWidgetAttribute("outlinedButton")
                self.modConfigPage.setCheckable(True)
                self.modConfigPage.setAutoExclusive(True)
                self.modConfigPage.released.connect(lambda: self.setCurrentPage(2))
                self.verticalLayout.addWidget(self.modConfigPage)
                
                self.verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
                self.verticalLayout.addItem(self.verticalSpacer)
                
                self.rightPanel = self.RightPanel(self)
                self.horizontalLayout.addWidget(self.rightPanel, 1)
                
                self.generalPageFrame = self.GeneralPage(self.rightPanel, self.version)
                self.rightPanel.addWidget(self.generalPageFrame)
                
                self.verSettingsPageFrame = self.VerSettingsPage(self.rightPanel, self.version)
                self.rightPanel.addWidget(self.verSettingsPageFrame)
                
                self.modConfigPageFrame = self.ModConfigPage(self.rightPanel, self.version)
                self.rightPanel.addWidget(self.modConfigPageFrame)
                
                app.registerRetranslateFunction(self.retranslateUI)
                self.retranslateUI()
            
            def retranslateUI(self):
                self.generalPage.setText(
                    self.tr("HomePage.VersionManagementPage.VersionInfoPage.GeneralPage.Title"))
                self.verSettingsPage.setText(
                    self.tr("HomePage.VersionManagementPage.VersionInfoPage.VerSettingsPage.Title"))
                self.modConfigPage.setText("⚙️模组管理")
            
            def setCurrentPage(self, page_id=-1):
                page_seq = (self.generalPage, self.verSettingsPage, self.modConfigPage)
                page_frame_dict = {
                    self.generalPage: self.generalPageFrame,
                    self.verSettingsPage: self.verSettingsPageFrame,
                    self.modConfigPage: self.modConfigPageFrame
                }
                if -1 < page_id < len(page_seq):
                    page = page_seq[page_id]
                    page_frame = page_frame_dict[page]
                    page.setChecked(True)
                    self.rightPanel.setCurrentWidget(page_frame)
            
            def mouseMoveEvent(self, a0):
                super().mouseMoveEvent(a0)
                
                if self.closeButton.rect().contains(self.mapFromGlobal(QCursor().pos())):
                    if not self.property("closeButtonOpacity"):
                        ani = OpacityAnimation(self.closeButton)
                        ani.setStartValue(0)
                        ani.setEndValue(100)
                        ani.setDuration(500)
                        ani.setEasingCurve(QEasingCurve.Type.OutQuint)
                        ani.valueChanged.connect(lambda value: self.setProperty("closeButtonOpacity", value / 100))
                        ani.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                        self.closeButton.show()
                    self.closeButton.raise_()
                else:
                    if self.property("closeButtonOpacity") >= 1.0:
                        ani = OpacityAnimation(self.closeButton)
                        ani.setStartValue(100)
                        ani.setEndValue(0)
                        ani.setDuration(500)
                        ani.setEasingCurve(QEasingCurve.Type.OutQuint)
                        ani.valueChanged.connect(lambda value: self.setProperty("closeButtonOpacity", value / 100))
                        ani.finished.connect(lambda: self.closeButton.hide())
                        ani.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        
        def __init__(self, parent, isVersionsShown=True):
            super().__init__(parent)
            self.horizontalLayout = QHBoxLayout(self)
            self.leftPanel = Panel(self)
            self.horizontalLayout.addWidget(self.leftPanel)
            self.verticalLayout = QVBoxLayout(self.leftPanel)
            
            isCurrentPathSaved = False
            for dire in settings["LauncherSettings"]["SavedMinecraftPaths"]:
                if Path(dire).resolve() == Path(minecraft_path).resolve():
                    isCurrentPathSaved = True
                newBtn = PushButton(self.leftPanel)
                newBtn.setCheckable(True)
                newBtn.setToolTip(dire)
                newBtn.setChecked(Path(dire) == Path(minecraft_path))
                newBtn.setAutoExclusive(True)
                newBtn.setText(dire[-min(len(str(Path(dire).resolve())), 15):])
                newBtn.pressed.connect(lambda d=dire: self.selectDir(str(Path(d).resolve())))
                self.verticalLayout.addWidget(newBtn)
            
            if not isCurrentPathSaved:
                dire = str(minecraft_path)
                newBtn = PushButton(self.leftPanel)
                newBtn.setCheckable(True)
                newBtn.setToolTip(dire)
                newBtn.setChecked(True)
                newBtn.setAutoExclusive(True)
                newBtn.setText(dire[-min(len(str(Path(dire).resolve())), 15):])
                newBtn.pressed.connect(lambda d=dire: self.selectDir(str(Path(d).resolve())))
                self.verticalLayout.addWidget(newBtn)
            
            self.addNewDirectoryButton = PushButton(self.leftPanel)
            self.addNewDirectoryButton.released.connect(self.selectNewMinecraftDir)
            self.verticalLayout.addWidget(self.addNewDirectoryButton)
            
            self.verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
            self.verticalLayout.addItem(self.verticalSpacer)
            
            self.versionsPanel = Panel(self)
            self.horizontalLayout.addWidget(self.versionsPanel, 1)
            
            self.verticalLayout_2 = QVBoxLayout(self.versionsPanel)
            
            self.currentDir = Label(self.versionsPanel)
            self.verticalLayout_2.addWidget(self.currentDir)
            
            self.listWidget = ListWidget(self.versionsPanel)
            self.listWidget.itemDoubleClicked.connect(
                lambda x: self.openVersionInfoPage(x.data(Qt.ItemDataRole.UserRole)))
            self.verticalLayout_2.addWidget(self.listWidget)
            
            self.versionAliasConv = {}
            self.updateVersionsList()
            
            self.versionInfoPage = None
            
            app.registerRetranslateFunction(self.retranslateUI)
            self.retranslateUI()
        
        def retranslateUI(self):
            self.addNewDirectoryButton.setText(
                self.tr("HomePage.VersionManagementPage.addNewDirectoryButton.Text"))
            self.currentDir.setText(self.tr("HomePage.VersionManagementPage.currentDir.Text").format(
                str(minecraft_path)))
        
        def selectNewMinecraftDir(self):
            global minecraft_path
            dirDialogue = QFileDialog.getExistingDirectory(self, self.tr(
                "HomePage.VersionManagementPage.SelectFolderDialogue.Title"), str(minecraft_path))
            if dirDialogue:
                minecraft_path = Path(dirDialogue).resolve()
                settings["LauncherSettings"]["MinecraftPath"] = str(minecraft_path.absolute())
                if str(minecraft_path) not in settings["LauncherSettings"]["SavedMinecraftPaths"]:
                    settings["LauncherSettings"]["SavedMinecraftPaths"].append(str(minecraft_path))
                    dire = str(minecraft_path)
                    newBtn = PushButton(self.leftPanel)
                    newBtn.setCheckable(True)
                    newBtn.setToolTip(dire)
                    newBtn.setAutoExclusive(True)
                    newBtn.setChecked(True)
                    newBtn.setText(dire[-min(len(str(Path(dire).resolve())), 15):])
                    newBtn.pressed.connect(lambda d=dire: self.selectDir(str(Path(d).resolve())))
                    newBtn.setCheckable(True)
                    self.verticalLayout.insertWidget(
                        max(len(settings["LauncherSettings"]["SavedMinecraftPaths"]) - 1, 1),
                        newBtn
                    )
                self.minecraft_path_changed.emit()
            self.retranslateUI()
            self.updateVersionsList()
        
        def selectDir(self, dir):
            global minecraft_path
            minecraft_path = Path(dir).resolve()
            settings["LauncherSettings"]["MinecraftPath"] = str(minecraft_path)
            self.minecraft_path_changed.emit()
            self.retranslateUI()
            self.updateVersionsList()
        
        def updateVersionsList(self):
            # self.listWidget.itemDoubleClicked.connect(lambda x: (self.selectVersion(x.text()), menu.close()))
            self.listWidget.clear()
            
            self.versionAliasConv.clear()
            
            versionList = GetVersionsByIterDirectory(minecraft_path)
            if versionList:
                versionList = sorted(versionList, key=lambda x: x[1].stat().st_mtime, reverse=True)
                for version in versionList:
                    versionConfig = Path(version[1] / "version.cfg")
                    versionName = version[0]
                    if versionConfig.exists():
                        cfg = loadVersionConfig(minecraft_path, version[0])
                        versionName = cfg["VersionAlias"]
                    item = QListWidgetItem(versionName, self.listWidget)
                    item.setData(Qt.ItemDataRole.UserRole, version[0])
                    item.setSizeHint(QSize(0, 32))
                    self.listWidget.addItem(item)
        
        def openVersionInfoPage(self, version):
            self.versionInfoPage = self.VersionInfoPage(self, version)
            rect = self.rect().adjusted(1, 1, -1, -1)
            self.versionInfoPage.setGeometry(rect)
            self.versionInfoPage.grabBehind()
            self.versionInfoPage.move(QPoint(0, self.height()))
            ani = QPropertyAnimation(self.versionInfoPage, b"pos", self)
            ani.setStartValue(QPoint(0, self.height()))
            ani.setEndValue(QPoint(0, 0))
            ani.setKeyValueAt(0.8, QPoint(0, 50))
            ani.setDuration(500)
            ani.setEasingCurve(QEasingCurve.Type.OutQuad)
            ani.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
            self.versionInfoPage.show()
        
        def closeVersionInfoPage(self):
            if not self.versionInfoPage:
                return
            ani = QPropertyAnimation(self.versionInfoPage, b"pos", self)
            ani.setStartValue(QPoint(0, 0))
            ani.setEndValue(QPoint(0, self.height()))
            ani.setKeyValueAt(0.8, QPoint(0, self.height() - 50))
            ani.setDuration(500)
            ani.setEasingCurve(QEasingCurve.Type.OutQuad)
            ani.finished.connect(self.closingFinished)
            ani.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        
        def closingFinished(self):
            self.versionInfoPage.close()
            self.versionInfoPage.deleteLater()
            del self.versionInfoPage
            self.versionInfoPage = None
        
        def resizeEvent(self, a0):
            super().resizeEvent(a0)
            if self.versionInfoPage:
                self.versionInfoPage.resize(self.size())
    
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
                    createVersionConfigFile(cfg_path, self.version, self.version, ":/missingno.png")
                cfg = json.loads(Path(cfg_path).read_text(encoding="utf-8"))
                syncWithDefault = cfg["LaunchConfig"]["SyncWithDefault"]
            
            if self.jar_path:
                curVerDir = self.jar_path.parent
            else:
                curVerDir = minecraft_path / "versions" / self.version
            
            jsonFile = json.loads(
                Path(curVerDir / f"{self.version}.json").read_text(encoding="utf-8"))
            
            separationMode = getVersionConfig(minecraft_path, curVerDir, settings, "LaunchSettings.VersionSeparation")
            match separationMode:
                case 0:
                    separationRequired = False
                case 1:
                    separationRequired = True
                case 2:
                    separationRequired = GetLoaderType(minecraft_path, self.version) is not None
                case 3:
                    versionType = jsonFile["type"]
                    separationRequired = versionType != "release"
                case _:
                    separationRequired = False
            
            if separationRequired:
                if separationMode == 3:
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
                    if separationMode == 1:
                        (curVerDir / "saves").mkdir(parents=True, exist_ok=True)
                        
                        versionType = jsonFile["type"]
                        if versionType == "release":
                            savesDir = (minecraft_path / f"saves")
                        else:
                            savesDir = (minecraft_path / f".{versionType}.saves")
                        for save in savesDir.iterdir():
                            if not save.is_dir():
                                continue
                            version = str(nbtlib.load(save / "level.dat")["Data"].get("Version", {}).get("Name"))
                            versionName = jsonFile["id"]
                            if version == versionName:
                                save.rename(curVerDir / "saves" / save.name)
            
            if separationRequired:
                if settings["LaunchSettings"]["VersionSeparationConfig"]["ShareVersionOptions"]:
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
                
                if settings["LaunchSettings"]["VersionSeparationConfig"]["ShareVersionResourcePacks"]:
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
                settings["LaunchSettings"]["MemoryAllocation"]["AllocationConfig"]["InitialHeapSize"] if not
                settings["LaunchSettings"]["MemoryAllocation"]["AutoAllocate"] else None,
                settings["LaunchSettings"]["MemoryAllocation"]["AllocationConfig"]["MaxHeapSize"] if not
                settings["LaunchSettings"]["MemoryAllocation"]["AutoAllocate"] else None,
                settings["LaunchSettings"]["Java"]["JVM"]["JVMArguments"]["Arguments"],
                settings["LaunchSettings"]["ExtraGameCommand"],
                currentPlayer,
                game_separation=separationRequired
            )
            self.launchFinished.emit(result)
    
    class UntilProcessExitedThread(QThread):
        processExited = pyqtSignal(int)
        
        def __init__(self, parent, process):
            super().__init__(parent)
            self.process = process
        
        def run(self):
            while self.process.poll() is None:
                pass
            self.processExited.emit(self.process.returncode)
    
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
        self.launchButton.setWidgetAttribute("primaryButton")
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
        self.selectNewMinecraftDirButton.released.connect(self.selectNewMinecraftDir)
        self.horizontalLayout.addWidget(self.selectNewMinecraftDirButton)
        self.versionsManageButton = PushButton(self.topPanel)
        self.versionsManageButton.setMinimumWidth(60)
        self.versionsManageButton.setMinimumHeight(32)
        self.versionsManageButton.setCheckable(True)
        self.versionsManageButton.pressed.connect(self.toggleManagementPageVisibility)
        self.horizontalLayout.addWidget(self.versionsManageButton)
        self.horizontalSpacer_2 = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.horizontalLayout.addItem(self.horizontalSpacer_2)
        
        self.versionsManagementPage = self.VersionManagementPage(self)
        self.versionsManagementPage.hide()
        self.versionsManagementPage.minecraft_path_changed.connect(self.updateVersionList)
        
        self.stopMinecraftProcess = ToolButton(self)
        self.stopMinecraftProcess.setFixedSize(QSize(32, 32))
        self.stopMinecraftProcess.pressed.connect(self.showTerminationMenu)
        
        self.version = None
        self.versionAliasConv = {}
        self.displayVersion = None
        
        self.versionsPopen = {}
        
        app.registerRetranslateFunction(self.retranslateUI)
        self.retranslateUI()
        self.updateVersionList()
        self.updateIcon()
    
    def retranslateUI(self):
        self.launchButton.setText(self.tr("HomePage.launchButton.Text"))
        self.launchButton.setToolTip(
            self.tr("HomePage.launchButton.ToolTip.0").format(self.displayVersion) if self.displayVersion else self.tr(
                "HomePage.launchButton.ToolTip.1"))
        self.selectVersionButton.setText(
            self.displayVersion if self.displayVersion else self.tr("HomePage.selectVersionButton.Text"))
        self.selectVersionButton.setToolTip(
            self.tr("HomePage.selectVersionButton.ToolTip.0").format(
                self.displayVersion) if self.displayVersion else self.tr(
                "HomePage.selectVersionButton.ToolTip.1"))
        self.reloadButton.setToolTip(self.tr("HomePage.reloadButton.Text"))
        self.selectNewMinecraftDirButton.setText(self.tr("HomePage.selectNewMinecraftDirButton.Text"))
        self.selectNewMinecraftDirButton.setToolTip(
            self.tr("HomePage.selectNewMinecraftDirButton.ToolTip").format(str(minecraft_path)))
        self.versionsManageButton.setText(self.tr("HomePage.versionsManageButton.Text"))
        self.stopMinecraftProcess.setToolTip(self.tr("HomePage.stopMinecraftProcess.ToolTip"))
    
    def updateVersionList(self):
        menu = QMenu(self.selectVersionButton)
        menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        listWidget = ListWidget(menu)
        listWidget.itemDoubleClicked.connect(lambda x: (self.selectVersion(x.text()), menu.close()))
        menu.addAction(QAction(""))
        
        self.versionAliasConv.clear()
        
        versionList = GetVersionsByIterDirectory(minecraft_path)
        if versionList:
            versionList = sorted(versionList, key=lambda x: x[1].stat().st_mtime, reverse=True)
            for version in versionList:
                versionConfig = Path(version[1] / "version.cfg")
                versionName = version[0]
                if versionConfig.exists():
                    cfg = yaml.safe_load(Path(versionConfig).read_text(encoding="utf-8"))
                    versionName = cfg["VersionAlias"]
                    self.versionAliasConv[versionName] = version[0]
                item = QListWidgetItem(versionName, listWidget)
                item.setData(Qt.ItemDataRole.UserRole, version[0])
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
        
        self.launchButton.setEnabled(bool(self.displayVersion))
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
        if not result[0]:
            self.versionsPopen[result[1]] = self.version
            tip = PopupTip(window)
            label = Label(tip)
            label.setText(self.tr("HomePage.launchSuccess"))  # 启动成功，请等待游戏窗口显示
            tip.setCentralWidget(label)
            tip.tip(duration=1000, topMargin=32)
            thread = self.UntilProcessExitedThread(self, result[1])
            thread.processExited.connect(
                lambda code: self.afterGameExited(code, result[1], settings["LaunchSettings"]["LauncherVisibility"]))
            thread.start()
            match settings["LaunchSettings"]["LauncherVisibility"]:
                case 0:
                    pass
                case 1:
                    self.window().hide()
                    self.window().systemTrayIcon.show()
                case 2:
                    self.window().close()
                case 3:
                    self.window().hide()
                    self.window().systemTrayIcon.show()
                case 4:
                    self.window().hide()
        else:
            tip = PopupTip(window)
            label = Label(tip)
            match result[1]:
                case 1:
                    label.setText(self.tr("HomePage.launchFailed.1"))
                case 2:
                    label.setText(self.tr("HomePage.launchFailed.2"))
                case 3:
                    label.setText(self.tr("HomePage.launchFailed.3"))
                    label.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse)
                case 4:
                    label.setText(self.tr("HomePage.launchFailed.4"))
                    label.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse)
                    window.centralwidget.setCurrentWidget(window.settingsPageFrame)
                    window.settingsPageFrame.page1.setChecked(True)
                    window.settingsPageFrame.stackedWidget.setCurrentWidget(window.settingsPageFrame.page1Frame)
                    window.settingsPage.setChecked(True)
                case 5:
                    if window.playerPageFrame.isLoggingIn:
                        label.setText(self.tr("HomePage.launchFailed.5.1"))
                    else:
                        label.setText(self.tr("HomePage.launchFailed.5.2"))
                        window.centralwidget.setCurrentWidget(window.playerPageFrame)
                        window.playerPage.setChecked(True)
                        window.playerPageFrame.loginMicrosoft()
                case _:
                    label.setText(self.tr("HomePage.launchFailed"))
            tip.setCentralWidget(label)
            tip.tip(duration=1000, topMargin=32)
    
    def afterGameExited(self, returncode, process, visibility):
        if not visibility:
            return
        if not returncode:
            # The game's probably crashed.
            return
        match visibility:
            case 3:
                self.window().show()
            case 4:
                self.window().close()
    
    def selectNewMinecraftDir(self):
        if not self.versionsManagementPage.isVisible():
            self.openManagementPage()
            QTimer.singleShot(500, self.selectNewMinecraftDir2)
        else:
            self.selectNewMinecraftDir2(False)
    
    def selectNewMinecraftDir2(self, close=True):
        self.versionsManagementPage.selectNewMinecraftDir()
        self.updateVersionList()
        if close:
            self.closeManagementPage()
    
    def showTerminationMenu(self):
        self.stopMinecraftProcess.setDown(False)
        if not self.versionsPopen:
            return
        
        menu = RoundedMenu(self.stopMinecraftProcess)
        
        def func(popen, action):
            popen.terminate()
            del self.versionsPopen[popen]
            menu.removeAction(action)
        
        for popen in self.versionsPopen:
            action = QAction(menu)
            action.setText(self.versionsPopen[popen])
            action.triggered.connect(lambda _=None, p=popen, a=action: func(p, a))
            menu.addAction(action)
        
        menu.exec(QCursor.pos())
    
    def toggleManagementPageVisibility(self):
        if self.versionsManagementPage.isVisible():
            self.closeManagementPage()
        else:
            self.openManagementPage()
    
    def openManagementPage(self):
        if self.versionsManagementPage.isVisible():
            return
        
        if self.stopMinecraftProcess.isVisible():
            ani33 = OpacityAnimation(self.stopMinecraftProcess)
            ani33.setStartValue(100)
            ani33.setEndValue(0)
            ani33.setDuration(500)
            ani33.setEasingCurve(QEasingCurve.Type.OutQuint)
            ani33.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
            ani33.finished.connect(lambda: self.stopMinecraftProcess.hide())
        
        ani22 = OpacityAnimation(self.versionsManagementPage)
        ani22.setStartValue(0)
        ani22.setEndValue(100)
        ani22.setDuration(500)
        ani22.setEasingCurve(QEasingCurve.Type.OutQuint)
        ani22.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        self.versionsManagementPage.show()
    
    def closeManagementPage(self):
        if not self.versionsManagementPage.isVisible():
            return
        
        if not self.stopMinecraftProcess.isVisible():
            ani33 = OpacityAnimation(self.stopMinecraftProcess)
            ani33.setStartValue(0)
            ani33.setEndValue(100)
            ani33.setDuration(500)
            ani33.setEasingCurve(QEasingCurve.Type.OutQuint)
            ani33.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
            QTimer.singleShot(50, lambda: self.stopMinecraftProcess.show())
        
        ani22 = OpacityAnimation(self.versionsManagementPage)
        ani22.setStartValue(100)
        ani22.setEndValue(0)
        ani22.setDuration(500)
        ani22.setEasingCurve(QEasingCurve.Type.OutQuint)
        ani22.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        QTimer.singleShot(500, lambda: self.versionsManagementPage.hide())
        QTimer.singleShot(500, lambda: self.versionsManageButton.setChecked(False))
        QTimer.singleShot(500,
                          lambda: (self.stopMinecraftProcess.show(), self.stopMinecraftProcess.setGraphicsEffect(None)))
        self.versionsManagementPage.closeVersionInfoPage()
    
    def changeAnimation(self, variant, function):
        if variant == "in":
            self.changeAnimationIn()
        else:
            QTimer.singleShot(300, function)
            self.changeAnimationOut()
    
    def changeAnimationIn(self):
        ani1 = QPropertyAnimation(self.topPanel, b"pos", self)
        pos1 = self.topPanel.pos()
        ani1.setStartValue(QPoint(15, 15) + QPoint(100, 0))
        ani1.setEndValue(QPoint(15, 15))
        ani1.setDuration(500)
        ani1.setEasingCurve(QEasingCurve.Type.OutQuint)
        ani1.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        ani11 = OpacityAnimation(self.topPanel)
        ani11.setStartValue(0)
        ani11.setEndValue(100)
        ani11.setDuration(500)
        ani11.setEasingCurve(QEasingCurve.Type.OutQuint)
        ani11.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        QTimer.singleShot(50, lambda: self.topPanel.show())
        if self.versionsManagementPage.isVisible():
            ani22 = OpacityAnimation(self.versionsManagementPage)
            ani22.setStartValue(0)
            ani22.setEndValue(100)
            ani22.setDuration(500)
            ani22.setEasingCurve(QEasingCurve.Type.OutQuint)
            QTimer.singleShot(100, lambda: ani22.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
        
        if self.stopMinecraftProcess.isVisible():
            ani33 = OpacityAnimation(self.stopMinecraftProcess)
            ani33.setStartValue(0)
            ani33.setEndValue(100)
            ani33.setDuration(500)
            ani33.setEasingCurve(QEasingCurve.Type.OutQuint)
            QTimer.singleShot(200, lambda: ani33.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
    
    def changeAnimationOut(self):
        ani11 = OpacityAnimation(self.topPanel)
        ani11.setStartValue(100)
        ani11.setEndValue(0)
        ani11.setDuration(500)
        ani11.setEasingCurve(QEasingCurve.Type.OutQuint)
        ani11.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        ani11.finished.connect(lambda: self.topPanel.show())
        if self.versionsManagementPage.isVisible():
            ani22 = OpacityAnimation(self.versionsManagementPage)
            ani22.setStartValue(100)
            ani22.setEndValue(0)
            ani22.setDuration(500)
            ani22.setEasingCurve(QEasingCurve.Type.OutQuint)
            QTimer.singleShot(100, lambda: ani22.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
        
        if self.stopMinecraftProcess.isVisible():
            ani33 = OpacityAnimation(self.stopMinecraftProcess)
            ani33.setStartValue(100)
            ani33.setEndValue(0)
            ani33.setDuration(500)
            ani33.setEasingCurve(QEasingCurve.Type.OutQuint)
            QTimer.singleShot(200, lambda: ani33.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
    
    def postToggleTheme(self):
        self.updateIcon()
    
    def updateIcon(self):
        colour = "black" if getTheme() == Theme.Light else "white"
        self.reloadButton.setIcon(QIcon(f":/Reload-{colour}.svg"))
        self.stopMinecraftProcess.setIcon(QIcon(f":/StopGame-{colour}.svg"))
    
    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        self.topPanel.move(QPoint(15, 15))
        self.topPanel.resize(QSize(self.width() - 30, 54))
        self.stopMinecraftProcess.move(QPoint(self.width() - 48, self.height() - 48))
        self.versionsManagementPage.move(QPoint(15, 79))
        self.versionsManagementPage.resize(QSize(self.width() - 30, self.height() - 79 - 15))


class DownloadPage(QFrame):
    class DownloadVanilla(QFrame):
        class FetchVersionThread(QThread):
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
            
            class FetchModLoadersThread(QThread):
                fetched = pyqtSignal(dict)
                
                def run(self):
                    result = {}
                    result["NeoForge"] = GetNeoForgeVersions()
                    result["Fabric"] = GetFabricLoaderVersions()
                    result["FabricAPI"] = GetFabricApiVersions()
                    self.fetched.emit(result)
            
            class DownloadVersionThread(QThread):
                def __init__(self, parent, minecraft_pth=minecraft_path, version=None,
                             neoforge_loader=None, fabric_loader=None, fabric_api=None,
                             icon_path=":/missingno.png"):
                    super().__init__(parent)
                    self.minecraft_path = minecraft_pth
                    self.version = version
                    self.neoforge_loader = neoforge_loader
                    self.fabric_loader = fabric_loader
                    self.fabric_api = fabric_api
                    self.icon_path = icon_path
                
                def run(self):
                    DownloadMinecraft(self.minecraft_path, self.version, self.version,
                                      max_workers=settings["LauncherSettings"]["DownloadSettings"][
                                          "DownloadThreadsCount"],
                                      chunk_size=settings["LauncherSettings"]["DownloadSettings"][
                                                     "DownloadChunkSize"] * 8 * 1024)
                    createVersionConfigFile(self.minecraft_path / "versions" / self.version, self.version, self.version,
                                            self.icon_path)
                    if self.neoforge_loader:
                        DownloadNeoForgeFull(self.version, self.neoforge_loader, self.minecraft_path,
                                             vanilla_download=False)
                    if self.fabric_loader:
                        DownloadFabricFull(self.version, self.fabric_loader, self.minecraft_path,
                                           vanilla_download=False)
                    if self.fabric_api:
                        DownloadMod("Fabric API", self.fabric_api, self.minecraft_path / "mods")
            
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
            
            def __init__(self, parent, version=None, icon_path=":/missingno.png"):
                super().__init__(parent, getBackgroundColour(), QColor(0, 0, 255, 200), 10)
                self.version = version
                self.icon_path = icon_path
                
                self.mainLayout = QVBoxLayout(self)
                self.mainLayout.setSpacing(8)
                self.mainLayout.setContentsMargins(12, 12, 12, 12)
                
                self.topPanel = Panel(self)
                self.mainLayout.addWidget(self.topPanel)
                
                self.horizontalLayout = QHBoxLayout(self.topPanel)
                self.horizontalLayout.setContentsMargins(8, 8, 8, 8)
                self.horizontalLayout.setSpacing(8)
                
                self.exitButton = CloseButton(self.topPanel)
                self.exitButton.setFixedSize(QSize(32, 32))
                self.exitButton.pressed.connect(self.closeFrame)
                self.horizontalLayout.addWidget(self.exitButton)
                
                self.groupBox4Btn = PushButton(self)
                self.groupBox4Btn.setCheckable(True)
                self.groupBox4Btn.setChecked(True)
                self.groupBox4Btn.setAutoExclusive(True)
                self.groupBox4Btn.setWidgetAttribute("outlinedButton")
                self.groupBox4Btn.pressed.connect(lambda: self.indexTo(0))
                self.horizontalLayout.addWidget(self.groupBox4Btn)
                
                self.groupBox2Btn = PushButton(self)
                self.groupBox2Btn.setCheckable(True)
                self.groupBox2Btn.setAutoExclusive(True)
                self.groupBox2Btn.setWidgetAttribute("outlinedButton")
                self.groupBox2Btn.pressed.connect(lambda: self.indexTo(1))
                self.horizontalLayout.addWidget(self.groupBox2Btn)
                
                self.groupBox3Btn = PushButton(self)
                self.groupBox3Btn.setCheckable(True)
                self.groupBox3Btn.setAutoExclusive(True)
                self.groupBox3Btn.setWidgetAttribute("outlinedButton")
                self.groupBox3Btn.pressed.connect(lambda: self.indexTo(2))
                self.horizontalLayout.addWidget(self.groupBox3Btn)
                
                self.horizontalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                self.horizontalLayout.addItem(self.horizontalSpacer)
                
                self.horizontalLayout_2 = QHBoxLayout()
                self.horizontalLayout_2.setSpacing(12)
                
                self.groupBox = Panel(self)
                self.groupBox.setMinimumWidth(140)
                self.groupBox.setMaximumWidth(160)
                self.groupBox.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
                self.horizontalLayout_2.addWidget(self.groupBox)
                
                self.verticalLayout_2 = QVBoxLayout(self.groupBox)
                self.verticalLayout_2.setContentsMargins(8, 16, 8, 16)
                self.verticalLayout_2.setSpacing(12)
                
                self.versionIcon = ImageWidget(self.groupBox)
                self.versionIcon.setFixedHeight(96)
                self.versionIcon.setImageAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)
                self.versionIcon.setImageScaleMode(ImageWidget.ImageScaleMode.AspectRatio)
                self.versionIcon.setImage(QImage(self.icon_path))
                
                self.verticalLayout_2.addWidget(self.versionIcon)
                
                self.versionName = Label(self.groupBox)
                self.versionName.setText(self.version)
                self.versionName.setWordWrap(True)
                font = self.versionName.font()
                font.setBold(True)
                font.setPointSize(font.pointSize() + 1)
                self.versionName.setFont(font)
                self.versionName.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
                self.verticalLayout_2.addWidget(self.versionName)
                
                self.versionSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
                self.verticalLayout_2.addItem(self.versionSpacer)
                
                self.rightArea = QWidget()
                self.rightLayout = QVBoxLayout(self.rightArea)
                self.rightLayout.setContentsMargins(0, 0, 0, 0)
                self.rightLayout.setSpacing(12)
                
                self.scrollArea = ScrollArea(self.rightArea)
                self.scrollArea.setWidgetResizable(True)
                self.scrollArea.setFrameShape(QFrame.Shape.NoFrame)
                self.scrollArea.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                self.rightLayout.addWidget(self.scrollArea, 1)
                
                self.buttonContainer = QWidget(self.rightArea)
                self.buttonLayout = QHBoxLayout(self.buttonContainer)
                self.buttonLayout.setContentsMargins(0, 0, 0, 0)
                self.buttonLayout.setSpacing(8)
                
                self.buttonSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                self.buttonLayout.addItem(self.buttonSpacer)
                
                self.startDownloadBtn = PushButton(self.buttonContainer)
                self.startDownloadBtn.setMinimumHeight(40)
                self.startDownloadBtn.setMinimumWidth(120)
                self.startDownloadBtn.pressed.connect(self.downloadVersion)
                self.startDownloadBtn.pressed.connect(self.closeFrame)
                self.startDownloadBtn.setWidgetAttribute("primaryButton")
                self.buttonLayout.addWidget(self.startDownloadBtn)
                
                self.rightLayout.addWidget(self.buttonContainer)
                
                self.horizontalLayout_2.addWidget(self.rightArea, 1)
                
                self.mainLayout.addLayout(self.horizontalLayout_2, 1)
                
                self.scrollAreaWidgetContents = QWidget()
                self.verticalLayout = QVBoxLayout(self.scrollAreaWidgetContents)
                self.verticalLayout.setSpacing(12)
                self.verticalLayout.setContentsMargins(0, 0, 0, 8)
                
                self.groupBox_4 = GroupBox(self.scrollAreaWidgetContents)
                self.verticalLayout.addWidget(self.groupBox_4)
                
                self.form_3 = QFormLayout(self.groupBox_4)
                self.form_3.setContentsMargins(12, 12, 12, 12)
                self.form_3.setSpacing(8)
                self.form_3.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self.form_3.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
                
                # (Neo)Forge
                self.form_5_Label = Label(self.groupBox_4)
                self.form_3.setWidget(0, QFormLayout.ItemRole.LabelRole, self.form_5_Label)
                
                self.form_5_ComboBox = ComboBox(self.groupBox_4)
                self.form_5_ComboBox.setMinimumHeight(32)
                self.form_5_ComboBox.addItem(None, None)
                self.form_5_ComboBox.currentIndexChanged.connect(self.updateModLoadersAvailability)
                self.form_3.setWidget(0, QFormLayout.ItemRole.FieldRole, self.form_5_ComboBox)
                
                # Fabric & Fabric API
                self.form_6_Label = Label(self.groupBox_4)
                self.form_3.setWidget(1, QFormLayout.ItemRole.LabelRole, self.form_6_Label)
                
                self.form_6_ComboBox = ComboBox(self.groupBox_4)
                self.form_6_ComboBox.setMinimumHeight(32)
                self.form_6_ComboBox.addItem(None, None)
                self.form_6_ComboBox.currentIndexChanged.connect(self.updateModLoadersAvailability)
                self.form_3.setWidget(1, QFormLayout.ItemRole.FieldRole, self.form_6_ComboBox)
                
                self.form_7_Label = Label(self.groupBox_4)
                self.form_3.setWidget(2, QFormLayout.ItemRole.LabelRole, self.form_7_Label)
                
                self.form_7_ComboBox = ComboBox(self.groupBox_4)
                self.form_7_ComboBox.setMinimumHeight(32)
                self.form_7_ComboBox.addItem(None, None)
                self.form_7_ComboBox.setDisabled(True)
                self.form_7_ComboBox.currentIndexChanged.connect(self.updateModLoadersAvailability)
                self.form_3.setWidget(2, QFormLayout.ItemRole.FieldRole, self.form_7_ComboBox)
                
                self.groupBox_2 = GroupBox(self.scrollAreaWidgetContents)
                self.verticalLayout.addWidget(self.groupBox_2)
                
                self.form_2 = QFormLayout(self.groupBox_2)
                self.form_2.setContentsMargins(12, 12, 12, 12)
                self.form_2.setSpacing(8)
                self.form_2.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self.form_2.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
                
                self.form_3_Label = Label(self.groupBox_2)
                self.form_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.form_3_Label)
                
                self.form_3_LineEdit = LineEdit(self.groupBox_2)
                self.form_3_LineEdit.setMinimumHeight(32)
                self.form_3_LineEdit.setPlaceholderText(str(minecraft_path.absolute()))
                self.form_3_LineEdit.setText(str(minecraft_path.absolute()))
                self.form_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.form_3_LineEdit)
                
                self.form_4_Label = Label(self.groupBox_2)
                self.form_2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.form_4_Label)
                
                self.form_4_LineEdit = LineEdit(self.groupBox_2)
                self.form_4_LineEdit.setMinimumHeight(32)
                self.form_4_LineEdit.setPlaceholderText(str(self.version))
                self.form_4_LineEdit.setText(str(self.version))
                self.form_2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.form_4_LineEdit)
                
                self.groupBox_3 = GroupBox(self.scrollAreaWidgetContents)
                self.verticalLayout.addWidget(self.groupBox_3)
                
                self.gridLayout = QGridLayout(self.groupBox_3)
                self.gridLayout.setContentsMargins(12, 12, 12, 12)
                self.gridLayout.setSpacing(8)
                
                self.wikiVersionPage = CommandLinkButton(self.groupBox_3)
                self.wikiVersionPage.setMinimumHeight(32)
                self.wikiVersionPage.pressed.connect(self.openWiki)
                self.gridLayout.addWidget(self.wikiVersionPage, 0, 0)
                
                self.clientJarURL = CommandLinkButton(self.groupBox_3)
                self.clientJarURL.setMinimumHeight(32)
                self.clientJarURL.pressed.connect(self.openClientURL)
                self.gridLayout.addWidget(self.clientJarURL, 1, 0)
                
                self.serverJarURL = CommandLinkButton(self.groupBox_3)
                self.serverJarURL.setMinimumHeight(32)
                self.serverJarURL.pressed.connect(self.openServerURL)
                self.gridLayout.addWidget(self.serverJarURL, 1, 1)
                
                self.verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
                self.verticalLayout.addItem(self.verticalSpacer)
                
                self.scrollArea.setWidget(self.scrollAreaWidgetContents)
                
                self.scrollArea.verticalScrollBar().valueChanged.connect(self.updateTopSelections)
                
                self.fetchModLoadersThread = self.FetchModLoadersThread(self)
                self.fetchModLoadersThread.fetched.connect(self.modLoadersFetched)
                self.fetchModLoadersThread.start()
                
                self.updateModLoadersAvailability()
                
                self.loaders = None
                
                app.registerRetranslateFunction(self.retranslateUI)
                self.retranslateUI()
            
            def retranslateUI(self):
                self.groupBox4Btn.setText(
                    self.tr("DownloadPage.DownloadVanilla.DownloadOptions.GroupBox4.Title"))
                self.groupBox2Btn.setText(
                    self.tr("DownloadPage.DownloadVanilla.DownloadOptions.GroupBox2.Title"))
                self.groupBox3Btn.setText(
                    self.tr("DownloadPage.DownloadVanilla.DownloadOptions.GroupBox3.Title"))
                self.groupBox_4.setTitle(self.tr("DownloadPage.DownloadVanilla.DownloadOptions.GroupBox4.Title"))
                self.form_5_Label.setText("NeoForge")
                self.form_6_Label.setText("Fabric")
                self.form_7_Label.setText("Fabric API")
                self.updateModLoadersAvailability()
                self.groupBox_2.setTitle(self.tr("DownloadPage.DownloadVanilla.DownloadOptions.GroupBox2.Title"))
                self.form_3_Label.setText(
                    self.tr("DownloadPage.DownloadVanilla.DownloadOptions.Form.3.Label.Text"))
                self.form_3_LineEdit.setToolTip("""注意：这不是版本 jar 文件的下载路径。
比如说你填的是：
① G:\\.minecraft
② /home/mc/.minecraft
jar 下载位置在：
① G:\\.minecraft\\versions\\{当前版本}\\{当前版本}.jar
② /home/mc/.minecraft/versions/{当前版本}/{当前版本}.jar
若存在与下载版本同名的文件夹，启动器会在下载前询问是否继续下载。""")
                self.form_4_Label.setText(
                    self.tr("DownloadPage.DownloadVanilla.DownloadOptions.Form.4.Label.Text"))
                self.form_4_LineEdit.setToolTip(
                    "默认是当前下载的版本，如果遇到版本已存在可以尝试修改此项。\n该选项不影响模组加载器依赖的原版版本的文件夹名。")
                self.groupBox_3.setTitle(self.tr("DownloadPage.DownloadVanilla.DownloadOptions.GroupBox3.Title"))
                self.wikiVersionPage.setText(
                    self.tr("DownloadPage.DownloadVanilla.DownloadOptions.OpenWiki"))
                self.clientJarURL.setText(
                    self.tr("DownloadPage.DownloadVanilla.DownloadOptions.DownloadClient"))
                self.serverJarURL.setText(
                    self.tr("DownloadPage.DownloadVanilla.DownloadOptions.DownloadServer"))
                self.startDownloadBtn.setText(self.tr("DownloadPage.DownloadVanilla.DownloadOptions.Download"))
                
                if self.loaders:
                    self.displayModLoaders()
                
                self.updateModLoadersAvailability()
            
            def updateTopSelections(self, value):
                if value + self.scrollArea.verticalScrollBar().pageStep() >= self.groupBox_3.y():
                    self.groupBox3Btn.setChecked(True)
                elif value + self.scrollArea.verticalScrollBar().pageStep() >= self.groupBox_2.y():
                    self.groupBox2Btn.setChecked(True)
                else:
                    self.groupBox1Btn.setChecked(True)
            
            def indexTo(self, index):
                widget = (self.groupBox_4, self.groupBox_2, self.groupBox_3)[index]
                animation = QPropertyAnimation(self.scrollArea.verticalScrollBar(), b"value", self)
                animation.setStartValue(self.scrollArea.verticalScrollBar().value())
                animation.setEndValue(widget.y())
                animation.setDuration(500)
                animation.setEasingCurve(QEasingCurve.Type.OutQuad)
                animation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
            
            def downloadVersion(self):
                thread = self.DownloadVersionThread(
                    self.window(),
                    Path(self.form_3_LineEdit.text() or minecraft_path),
                    self.version,
                    self.form_5_ComboBox.currentData(),
                    self.form_6_ComboBox.currentData(),
                    self.form_7_ComboBox.currentData(),
                    self.icon_path
                )
                thread.start()
            
            def modLoadersFetched(self, loaders):
                self.loaders = loaders
                self.displayModLoaders()
            
            def displayModLoaders(self):
                loaders = self.loaders
                for version in reversed(loaders["NeoForge"]["versions"]):
                    display_version = version
                    display_version = "NeoForge " + display_version
                    self.form_5_ComboBox.addItem(display_version, version)
                
                for loader in loaders["Fabric"]:
                    version = loader["version"]
                    version = "Fabric " + version.split(":")[-1]
                    self.form_6_ComboBox.addItem(
                        "{} ({})".format(version,
                                         self.tr("DownloadPage.DownloadVanilla.DownloadOptions.Loader.Stable") if
                                         loader["stable"] else self.tr(
                                             "DownloadPage.DownloadVanilla.DownloadOptions.Loader.Beta")),
                        loader["version"])
                for api in loaders["FabricAPI"]:
                    if self.version in api["game_versions"]:
                        version_number = api["version_number"]
                        version_number = "Fabric API " + version_number.split("+")[0]
                        self.form_7_ComboBox.addItem(version_number, api["version_number"])
            
            def updateModLoadersAvailability(self):
                if self.form_5_ComboBox.currentIndex() > 0:
                    self.form_6_ComboBox.setDisabled(True)
                    self.form_7_ComboBox.setDisabled(True)
                    self.form_6_ComboBox.setCurrentIndex(0)
                    self.form_7_ComboBox.setCurrentIndex(0)
                    self.form_6_ComboBox.setItemText(0, self.tr(
                        "DownloadPage.DownloadVanilla.DownloadOptions.State.Incompatible").format(
                        "NeoForge"))
                    self.form_7_ComboBox.setItemText(0, self.tr(
                        "DownloadPage.DownloadVanilla.DownloadOptions.State.Incompatible").format("NeoForge"))
                else:
                    self.form_6_ComboBox.setEnabled(True)
                    self.form_6_ComboBox.setItemText(0, self.tr(
                        "DownloadPage.DownloadVanilla.DownloadOptions.Actions.DoNotDownload"))
                    if self.form_6_ComboBox.currentIndex() > 0:
                        self.form_5_ComboBox.setDisabled(True)
                        self.form_5_ComboBox.setCurrentIndex(0)
                        self.form_5_ComboBox.setItemText(0, self.tr(
                            "DownloadPage.DownloadVanilla.DownloadOptions.State.Incompatible").format("Fabric"))
                        self.form_7_ComboBox.setEnabled(True)
                        self.form_7_ComboBox.setItemText(0, self.tr(
                            "DownloadPage.DownloadVanilla.DownloadOptions.Actions.DoNotDownload"))
                    else:
                        self.form_5_ComboBox.setEnabled(True)
                        self.form_5_ComboBox.setItemText(0, self.tr(
                            "DownloadPage.DownloadVanilla.DownloadOptions.Actions.DoNotDownload"))
                        self.form_7_ComboBox.setCurrentIndex(0)
                        self.form_7_ComboBox.setItemText(0, self.tr(
                            "DownloadPage.DownloadVanilla.DownloadOptions.State.SelectFabricFirst"))  # 请先选择一个 Fabric 版本
                        self.form_7_ComboBox.setDisabled(True)
            
            def openWiki(self):
                wikiUrls = {
                    "zh-cn": "https://zh.minecraft.wiki/w/{}",
                    "en-gb": "https://minecraft.wiki/w/{}",
                }
                webbrowser.open(
                    wikiUrls.get(currentLanguage, "https://minecraft.wiki/w/{}").format(self.version))
            
            def openClientURL(self):
                webbrowser.open(GetMinecraftClientDownloadUrl(self.version))
            
            def openServerURL(self):
                webbrowser.open(GetMinecraftServerDownloadUrl(self.version))
            
            def closeFrame(self):
                if self.fetchModLoadersThread:
                    self.fetchModLoadersThread.terminate()
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
            pp = QPainterPath()
            pp.addRoundedRect(self.rect().toRectF(), 10, 10)
            self.loader.setBackgroundClipPath(pp)
            self.loader.addReloadFunction(self.startLoad)
            self.getThread = None
            
            self.downloadOptions = None
            
            self.versionToDataMap = {}
            
            app.registerRetranslateFunction(self.retranslateUI)
            self.retranslateUI()
        
        def retranslateUI(self):
            self.topSearchPanel.setTitle(self.tr("DownloadPage.DownloadVanilla.TopSearchPanel.Title"))
            self.searchInput.setPlaceholderText(
                self.tr("DownloadPage.DownloadVanilla.SearchInput.Placeholder"))
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
            if self.versionData:
                self.searchVersions(self.searchInput.text())
            self.versionModel.setHorizontalHeaderLabels(
                [self.tr("DownloadPage.DownloadVanilla.VersionTable.HeaderLabel.1"),
                 self.tr("DownloadPage.DownloadVanilla.VersionTable.HeaderLabel.2"),
                 self.tr("DownloadPage.DownloadVanilla.VersionTable.HeaderLabel.3")])  # 版本 类型 发布日期
        
        def showEvent(self, a0):
            super().showEvent(a0)
            if not self.getThread and not self.versionData:
                self.startLoad()
        
        def startLoad(self, ani=False):
            self.getThread = self.FetchVersionThread(self)
            self.getThread.gettingFinished.connect(self.displayVersions)
            self.getThread.start()
            self.loader.start(ani)
        
        def resizeEvent(self, a0):
            super().resizeEvent(a0)
            if self.downloadOptions:
                self.downloadOptions.resize(self.size())
            
            if self.loader:
                pp = QPainterPath()
                pp.addRoundedRect(self.rect().toRectF(), 10, 10)
                self.loader.setBackgroundClipPath(pp)
        
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
        
        def localiseType(self, versionType):
            match versionType:
                case "release":
                    versionType = self.tr("DownloadPage.DownloadVanilla.VersionType.Release")
                case "snapshot":
                    versionType = self.tr("DownloadPage.DownloadVanilla.VersionType.Snapshot")
                case "old_beta":
                    versionType = self.tr("DownloadPage.DownloadVanilla.VersionType.OldBeta")
                case "old_alpha":
                    versionType = self.tr("DownloadPage.DownloadVanilla.VersionType.OldAlpha")
                case "april_fool":
                    versionType = self.tr("DownloadPage.DownloadVanilla.VersionType.AprilFool")
                case "classic":
                    versionType = self.tr("DownloadPage.DownloadVanilla.VersionType.Classic")
                case "pre_classic":
                    versionType = self.tr("DownloadPage.DownloadVanilla.VersionType.PreClassic")
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
                
                row = 0
                for version in self.versionData["versions"]:
                    self.versionToDataMap[version["id"]] = version
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
                            if version["type"] == "release":
                                pixmap = QPixmap(":/grass_block.png")
                            else:
                                pixmap = QPixmap(":/dirt_block.png")
                            versionIdItem = QStandardItem(QIcon(pixmap), version["id"])
                            versionIdItem.setData(version, 3)
                            versionTypeItem = QStandardItem(self.localiseType(version["type"]))
                            versionTypeItem.setData(version["type"], 3)
                            versionReleaseTimeItem = QStandardItem(
                                version["releaseTime"].astimezone().strftime("%Y-%m-%d %H:%M:%S")
                            )
                            versionReleaseTimeItem.setData(version["releaseTime"], 3)
                            self.versionModel.setItem(row, 0, versionIdItem)
                            self.versionModel.setItem(row, 1, versionTypeItem)
                            self.versionModel.setItem(row, 2, versionReleaseTimeItem)
                            row += 1
                        if version["type"] == "release" and not latest_release:
                            latest_release = True
                            if version["type"] == "release":
                                pixmap = QPixmap(":/grass_block.png")
                            else:
                                pixmap = QPixmap(":/dirt_block.png")
                            versionIdItem = QStandardItem(QIcon(pixmap), version["id"])
                            versionIdItem.setData(version, 3)
                            versionTypeItem = QStandardItem(self.localiseType(version["type"]))
                            versionTypeItem.setData(version["type"], 3)
                            versionReleaseTimeItem = QStandardItem(
                                version["releaseTime"].astimezone().strftime("%Y-%m-%d %H:%M:%S")
                            )
                            versionReleaseTimeItem.setData(version["releaseTime"], 3)
                            self.versionModel.setItem(row, 0, versionIdItem)
                            self.versionModel.setItem(row, 1, versionTypeItem)
                            self.versionModel.setItem(row, 2, versionReleaseTimeItem)
                            row += 1
                    elif re.match(text, version["id"], re.UNICODE):
                        if version["type"] == "release":
                            pixmap = QPixmap(":/grass_block.png")
                        else:
                            pixmap = QPixmap(":/dirt_block.png")
                        versionIdItem = QStandardItem(QIcon(pixmap), version["id"])
                        versionIdItem.setData(version, 3)
                        versionTypeItem = QStandardItem(self.localiseType(version["type"]))
                        versionTypeItem.setData(version["type"], 3)
                        versionReleaseTimeItem = QStandardItem(
                            version["releaseTime"].astimezone().strftime("%Y-%m-%d %H:%M:%S")
                        )
                        versionReleaseTimeItem.setData(version["releaseTime"], 3)
                        self.versionModel.setItem(row, 0, versionIdItem)
                        self.versionModel.setItem(row, 1, versionTypeItem)
                        self.versionModel.setItem(row, 2, versionReleaseTimeItem)
                        row += 1
                    elif re.match(text, version["type"], re.UNICODE):
                        if version["type"] == "release":
                            pixmap = QPixmap(":/grass_block.png")
                        else:
                            pixmap = QPixmap(":/dirt_block.png")
                        versionIdItem = QStandardItem(QIcon(pixmap), version["id"])
                        versionIdItem.setData(version, 3)
                        versionTypeItem = QStandardItem(self.localiseType(version["type"]))
                        versionTypeItem.setData(version["type"], 3)
                        versionReleaseTimeItem = QStandardItem(
                            version["releaseTime"].astimezone().strftime("%Y-%m-%d %H:%M:%S")
                        )
                        versionReleaseTimeItem.setData(version["releaseTime"], 3)
                        self.versionModel.setItem(row, 0, versionIdItem)
                        self.versionModel.setItem(row, 1, versionTypeItem)
                        self.versionModel.setItem(row, 2, versionReleaseTimeItem)
                        row += 1
                    elif re.match(text, version["releaseTime"].astimezone().strftime("%Y-%m-%d %H:%M:%S"), re.UNICODE):
                        if version["type"] == "release":
                            pixmap = QPixmap(":/grass_block.png")
                        else:
                            pixmap = QPixmap(":/dirt_block.png")
                        versionIdItem = QStandardItem(QIcon(pixmap), version["id"])
                        versionIdItem.setData(version, 3)
                        versionTypeItem = QStandardItem(self.localiseType(version["type"]))
                        versionTypeItem.setData(version["type"], 3)
                        versionReleaseTimeItem = QStandardItem(
                            version["releaseTime"].astimezone().strftime("%Y-%m-%d %H:%M:%S")
                        )
                        versionReleaseTimeItem.setData(version["releaseTime"], 3)
                        self.versionModel.setItem(row, 0, versionIdItem)
                        self.versionModel.setItem(row, 1, versionTypeItem)
                        self.versionModel.setItem(row, 2, versionReleaseTimeItem)
                        row += 1
            except re.error:
                self.versionModel.clear()
                row = 0
        
        def openDownloadOptions(self, item):
            match item.column():
                case 0:
                    versionData = self.versionModel.item(item.row(), 0).data(3)
                    versionName = versionData["id"]
                    versionType = versionData["type"]
                    
                    if versionType == "release":
                        path = ":/grass_block.png"
                    else:
                        path = ":/dirt_block.png"
                    
                    self.downloadOptions = self.DownloadOptions(self, versionName, path)
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
                    versionType = self.versionModel.item(item.row(), 1).data(3)
                    
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
            del self.downloadOptions
            self.downloadOptions = None
        
        def reloadVersions(self):
            if self.downloadOptions:
                return
            self.retranslateUI()
            self.startLoad(self.loader and not self.loader.isVisible())
        
        def changeAnimation(self, variant, function):
            if variant == "in":
                self.changeAnimationIn()
            else:
                self.changeAnimationOut()
                QTimer.singleShot(300, function)
        
        def changeAnimationIn(self):
            ani1 = QPropertyAnimation(self.topSearchPanel, b"pos", self)
            pos1 = self.topSearchPanel.pos()
            ani1.setStartValue(pos1 + QPoint(100, 0))
            ani1.setEndValue(pos1)
            ani1.setDuration(500)
            ani1.setEasingCurve(QEasingCurve.Type.OutQuint)
            ani1.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
            ani11 = OpacityAnimation(self.topSearchPanel)
            ani11.setStartValue(0)
            ani11.setEndValue(100)
            ani11.setDuration(500)
            ani11.setEasingCurve(QEasingCurve.Type.OutQuint)
            ani11.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
            ani2 = QPropertyAnimation(self.versionDisplayTable, b"pos", self)
            pos2 = self.versionDisplayTable.pos()
            ani2.setStartValue(pos2 + QPoint(100, 0))
            ani2.setEndValue(pos2)
            ani2.setDuration(500)
            ani2.setEasingCurve(QEasingCurve.Type.OutQuint)
            QTimer.singleShot(100, lambda: ani2.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
            ani22 = OpacityAnimation(self.versionDisplayTable)
            ani22.setStartValue(0)
            ani22.setEndValue(100)
            ani22.setDuration(500)
            ani22.setEasingCurve(QEasingCurve.Type.OutQuint)
            QTimer.singleShot(100, lambda: ani22.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
        
        def changeAnimationOut(self):
            ani11 = OpacityAnimation(self.topSearchPanel)
            ani11.setStartValue(100)
            ani11.setEndValue(0)
            ani11.setDuration(500)
            ani11.setEasingCurve(QEasingCurve.Type.OutQuint)
            ani11.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
            ani22 = OpacityAnimation(self.versionDisplayTable)
            ani22.setStartValue(100)
            ani22.setEndValue(0)
            ani22.setDuration(500)
            ani22.setEasingCurve(QEasingCurve.Type.OutQuint)
            QTimer.singleShot(100, lambda: ani22.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
    
    class DownloadMods(QFrame):
        class ModInfoPage(AcrylicBackground):
            class ModInfoPanel(QFrame):
                def changeAnimation(self, variant, function):
                    if variant == "in":
                        self.changeAnimationIn()
                    else:
                        QTimer.singleShot(300, function)
                        self.changeAnimationOut()
                
                def changeAnimationIn(self):
                    ani = QPropertyAnimation(self, b"pos", self)
                    ani.setStartValue(self.pos() + QPoint(100, 0))
                    ani.setEndValue(self.pos())
                    ani.setDuration(500)
                    ani.setEasingCurve(QEasingCurve.Type.OutQuint)
                    ani.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                    aniOpacity = OpacityAnimation(self)
                    aniOpacity.setStartValue(0)
                    aniOpacity.setEndValue(100)
                    aniOpacity.setDuration(500)
                    aniOpacity.setEasingCurve(QEasingCurve.Type.OutQuint)
                    aniOpacity.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                    QTimer.singleShot(50, lambda: self.show())
                
                def changeAnimationOut(self):
                    aniOpacity = OpacityAnimation(self)
                    aniOpacity.setStartValue(100)
                    aniOpacity.setEndValue(0)
                    aniOpacity.setDuration(500)
                    aniOpacity.setEasingCurve(QEasingCurve.Type.OutQuint)
                    aniOpacity.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                    aniOpacity.finished.connect(lambda: self.hide())
            
            class ModVersionsPanel(QFrame):
                def changeAnimation(self, variant, function):
                    if variant == "in":
                        self.changeAnimationIn()
                    else:
                        QTimer.singleShot(300, function)
                        self.changeAnimationOut()
                
                def changeAnimationIn(self):
                    ani = QPropertyAnimation(self, b"pos", self)
                    ani.setStartValue(self.pos() + QPoint(100, 0))
                    ani.setEndValue(self.pos())
                    ani.setDuration(500)
                    ani.setEasingCurve(QEasingCurve.Type.OutQuint)
                    ani.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                    aniOpacity = OpacityAnimation(self)
                    aniOpacity.setStartValue(0)
                    aniOpacity.setEndValue(100)
                    aniOpacity.setDuration(500)
                    aniOpacity.setEasingCurve(QEasingCurve.Type.OutQuint)
                    aniOpacity.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                    QTimer.singleShot(50, lambda: self.show())
                
                def changeAnimationOut(self):
                    aniOpacity = OpacityAnimation(self)
                    aniOpacity.setStartValue(100)
                    aniOpacity.setEndValue(0)
                    aniOpacity.setDuration(500)
                    aniOpacity.setEasingCurve(QEasingCurve.Type.OutQuint)
                    aniOpacity.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                    aniOpacity.finished.connect(lambda: self.hide())
            
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
                self.destroyed.connect(thread.terminate)
                
                self.mod_versions = []
                thread_2 = self.GetVersionsThread(self, self.mod_name)
                thread_2.requested.connect(self.updateVersions)
                thread_2.start()
                self.destroyed.connect(thread_2.terminate)
                
                self.mainLayout = QVBoxLayout(self)
                self.mainLayout.setSpacing(8)
                self.mainLayout.setContentsMargins(12, 12, 12, 12)
                
                self.topPanel = Panel(self)
                self.mainLayout.addWidget(self.topPanel)
                
                self.horizontalLayout = QHBoxLayout(self.topPanel)
                self.horizontalLayout.setContentsMargins(8, 8, 8, 8)
                self.horizontalLayout.setSpacing(8)
                
                self.exitButton = CloseButton(self.topPanel)
                self.exitButton.setFixedSize(QSize(32, 32))
                self.exitButton.pressed.connect(self.closeFrame)
                self.horizontalLayout.addWidget(self.exitButton)
                
                self.page1Btn = PushButton(self)
                self.page1Btn.setCheckable(True)
                self.page1Btn.setChecked(True)
                self.page1Btn.setAutoExclusive(True)
                self.page1Btn.setWidgetAttribute("outlinedButton")
                self.page1Btn.pressed.connect(lambda: self.setCurrentPage(0))
                self.horizontalLayout.addWidget(self.page1Btn)
                
                self.page2Btn = PushButton(self)
                self.page2Btn.setCheckable(True)
                self.page2Btn.setAutoExclusive(True)
                self.page2Btn.setWidgetAttribute("outlinedButton")
                self.page2Btn.pressed.connect(lambda: self.setCurrentPage(1))
                self.horizontalLayout.addWidget(self.page2Btn)
                
                self.horizontalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                self.horizontalLayout.addItem(self.horizontalSpacer)
                
                self.horizontalLayout_2 = QHBoxLayout()
                self.horizontalLayout_2.setSpacing(12)
                
                self.groupBox = Panel(self)
                self.groupBox.setMinimumWidth(140)
                self.groupBox.setMaximumWidth(160)
                self.groupBox.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
                self.horizontalLayout_2.addWidget(self.groupBox)
                
                self.verticalLayout_2 = QVBoxLayout(self.groupBox)
                self.verticalLayout_2.setContentsMargins(8, 16, 8, 16)
                self.verticalLayout_2.setSpacing(12)
                
                self.modIcon = ImageWidget(self.groupBox)
                self.modIcon.setFixedHeight(96)
                self.modIcon.setImageAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)
                self.modIcon.setImageScaleMode(ImageWidget.ImageScaleMode.AspectRatio)
                self.modIcon.setBorderRadius(10)
                self.verticalLayout_2.addWidget(self.modIcon)
                
                self.modName = Label(self.groupBox)
                self.modName.setText(self.mod_name)
                self.modName.setWordWrap(True)
                font = self.modName.font()
                font.setBold(True)
                font.setPointSize(font.pointSize() + 1)
                self.modName.setFont(font)
                self.modName.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
                self.verticalLayout_2.addWidget(self.modName)
                
                self.modDescription = Label(self.groupBox)
                self.modDescription.setText(self.mod_description)
                self.modDescription.setWordWrap(True)
                self.modDescription.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
                self.modDescription.setStyleSheet("color: #999;")
                self.verticalLayout_2.addWidget(self.modDescription)
                
                self.versionSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
                self.verticalLayout_2.addItem(self.versionSpacer)
                
                self.rightArea = QWidget()
                self.rightLayout = QVBoxLayout(self.rightArea)
                self.rightLayout.setContentsMargins(0, 0, 0, 0)
                self.rightLayout.setSpacing(12)
                
                self.stackedWidget = AnimatedStackedWidget(self.rightArea)
                self.rightLayout.addWidget(self.stackedWidget, 1)
                
                self.modInfoPanel = self.ModInfoPanel(self.stackedWidget)
                self.stackedWidget.addWidget(self.modInfoPanel)
                
                self.verticalLayout = QVBoxLayout(self.modInfoPanel)
                self.verticalLayout.setSpacing(12)
                
                self.modInfo = GroupBox(self.modInfoPanel)
                self.verticalLayout.addWidget(self.modInfo)
                
                self.verticalLayout_3 = QVBoxLayout(self.modInfo)
                self.verticalLayout_3.setContentsMargins(12, 12, 12, 12)
                self.verticalLayout_3.setSpacing(8)
                
                self.modLinks = Panel(self.modInfo)
                self.verticalLayout_3.addWidget(self.modLinks)
                
                self.horizontalLayout_3 = QHBoxLayout(self.modLinks)
                self.horizontalLayout_3.setSpacing(8)
                
                self.modAction_issues = None
                
                if self.mod_info_json.get("issues_url"):
                    self.modAction_issues = PushButton(self.modLinks)
                    self.modAction_issues.pressed.connect(lambda: self.openURL(self.mod_info_json.get("issues_url")))
                    self.horizontalLayout_3.addWidget(self.modAction_issues)
                
                self.horizontalSpacer_2 = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                self.horizontalLayout_3.addItem(self.horizontalSpacer_2)
                
                self.modBody = TextEdit(self.modInfo)
                self.modBody.setReadOnly(True)
                self.modBody.document().setDefaultStyleSheet(
                    f"code {{ font-family: {', '.join(map(lambda a: '"' + a + '"', fixedFontList))}; }} pre {{ background: #33445555; border-radius: 4px; }}")
                self.modBody.setHtml(
                    markdown2.markdown(self.mod_body,
                                       extras=['fenced-code-blocks', 'code-friendly', 'breaks-on-newline', 'table']))
                self.modBody.document().setBaseUrl(QUrl("https://cdn.modrinth.com/"))
                self.verticalLayout_3.addWidget(self.modBody, 1)
                
                self.modVersionsPanel = self.ModVersionsPanel(self.stackedWidget)
                self.stackedWidget.addWidget(self.modVersionsPanel)
                
                self.verticalLayout_4 = QVBoxLayout(self.modVersionsPanel)
                self.verticalLayout_4.setContentsMargins(12, 12, 12, 12)
                self.verticalLayout_4.setSpacing(8)
                
                self.modVersions = GroupBox(self.modVersionsPanel)
                self.verticalLayout_4.addWidget(self.modVersions)
                
                self.verticalLayout_5 = QVBoxLayout(self.modVersions)
                self.verticalLayout_5.setContentsMargins(12, 12, 12, 12)
                self.verticalLayout_5.setSpacing(8)
                
                self.listWidget = ListWidget(self.modVersions)
                self.listWidget.doubleClicked.connect(self.startDownloadMod)
                self.verticalLayout_5.addWidget(self.listWidget)
                
                self.horizontalLayout_2.addWidget(self.rightArea, 1)
                
                self.mainLayout.addLayout(self.horizontalLayout_2, 1)
                
                self.retranslateUI()
            
            def retranslateUI(self):
                self.modName.setText(self.mod_name)
                self.modDescription.setText(self.mod_description)
                self.page1Btn.setText(self.tr("DownloadPage.DownloadMods.ModInfoPage.ModInfo.Title"))
                self.page2Btn.setText(self.tr("DownloadPage.DownloadMods.ModInfoPage.ModVersions.Title"))
                self.modInfo.setTitle(self.tr("DownloadPage.DownloadMods.ModInfoPage.ModInfo.Title"))
                self.modVersions.setTitle(self.tr("DownloadPage.DownloadMods.ModInfoPage.ModVersions.Title"))
                if self.modAction_issues:
                    self.modAction_issues.setText(
                        self.tr("DownloadPage.DownloadMods.ModInfoPage.Actions.Issues"))
            
            def setCurrentPage(self, page_id=0):
                if page_id == 0:
                    self.page1Btn.setChecked(True)
                    self.stackedWidget.setCurrentWidget(self.modInfoPanel)
                else:
                    self.page2Btn.setChecked(True)
                    self.stackedWidget.setCurrentWidget(self.modVersionsPanel)
            
            def updateIcon(self, icon):
                try:
                    with tempfile.NamedTemporaryFile(mode="wb+", suffix=".png", delete=False) as self.icon_temp:
                        self.icon_temp.write(requests.get(self.mod_icon).content)
                        self.icon_temp.flush()
                except:
                    self.icon_temp = None
                    raise
                self.modIcon.setImage(QImage(self.icon_temp.name) if self.icon_temp else None)
            
            def updateVersions(self, versions):
                self.listWidget.clear()
                self.mod_versions = versions
                for version in versions:
                    self.listWidget.addItem(f"{version['name']}")
            
            def startDownloadMod(self, version):
                download_path = QFileDialog.getExistingDirectory(self, self.tr(
                    "DownloadPage.DownloadMods.ModInfoPage.AskDownloadPath.Title"), str(Path(".").absolute()))
                if download_path:
                    version_text = self.listWidget.model().itemData(version)[0]
                    thread = self.DownloadThread(self.window(), self.mod_name, version_text, download_path)
                    thread.start()
            
            def openURL(self, url):
                webbrowser.open(url)
            
            def closeFrame(self):
                if self.icon_temp:
                    Path(self.icon_temp.name).unlink(missing_ok=True)
                self.closePage.emit()
            
            def paintEvent(self, a0):
                self.setTintColour(getBackgroundColour())
                super().paintEvent(a0)
        
        class GetModThread(QThread):
            gotMod = pyqtSignal(dict)
            
            def __init__(self, parent=None, page=1, page_items=10, search=False, query=None):
                super().__init__(parent)
                self.page = page
                self.page_items = page_items
                self.search = search
                self.query = query
            
            def run(self):
                try:
                    if self.search:
                        response = SearchMods(
                            query=self.query,
                            limit=self.page_items,
                            offset=(self.page - 1) * self.page_items
                        )
                    else:
                        response = GetMods(
                            limit=self.page_items,
                            offset=(self.page - 1) * self.page_items
                        )
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
            self.searchLineEdit.editingFinished.connect(self.searchFinished)
            self.horizontalLayout.addWidget(self.searchLineEdit)
            
            self.verticalLayout.addWidget(self.filterPanel)
            
            self.contentTable = TableView(self)
            self.verticalLayout.addWidget(self.contentTable)
            self.contentTable.verticalHeader().setVisible(False)
            self.contentTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.contentTable.setEditTriggers(TableView.EditTrigger.NoEditTriggers)
            self.contentTable.doubleClicked.connect(self.modInfoPageOpen)
            self.model = QStandardItemModel()
            self.contentTable.setModel(self.model)
            
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
            self.totalModsCount = 0
        
        def retranslateUI(self):
            self.filterPanel.setTitle(self.tr("DownloadPage.DownloadMods.FilterPanel.Title"))
            self.searchLineEdit.setPlaceholderText(
                self.tr("DownloadPage.DownloadMods.SearchLineEdit.Placeholder"))
            # self.searchLineEdit.setToolTip("")
            self.previousButton.setText(self.tr("DownloadPage.DownloadMods.Actions.PrevPage"))
            self.nextButton.setText(self.tr("DownloadPage.DownloadMods.Actions.NextPage"))
            self.model.setHorizontalHeaderLabels([self.tr("DownloadPage.DownloadMods.ContentTable.HeaderLabel.1"),
                                                  self.tr("DownloadPage.DownloadMods.ContentTable.HeaderLabel.2"),
                                                  self.tr(
                                                      "DownloadPage.DownloadMods.ContentTable.HeaderLabel.3")])  # 模组名称 模组作者 最后修改时间
        
        def previousPage(self):
            self.currentPage -= 1
            self.currentPage = max(self.currentPage, 1)
            self.updatePage()
            self.loadPage()
        
        def nextPage(self):
            self.currentPage += 1
            if self.totalModsCount:
                self.currentPage = min(self.currentPage, math.ceil(self.totalModsCount / 10))
            self.updatePage()
            self.loadPage()
        
        def updatePage(self):
            pageText = str(self.currentPage)
            if self.totalModsCount:
                pageText += f" / {math.ceil(self.totalModsCount / 10)}"
            self.currentPageLabel.setText(pageText)
            self.previousButton.setEnabled(self.currentPage > 1)
            if self.totalModsCount:
                self.nextButton.setEnabled(self.currentPage < math.ceil(self.totalModsCount / 10))
            if self.searchLineEdit.text():
                self.nextButton.setEnabled(False)
            else:
                self.nextButton.setEnabled(True)
        
        def loadPage(self):
            if self.currentPage in self.mods:
                self.displayMods(None, self.currentPage)
            else:
                if self.searchLineEdit.text():
                    self.getModThread = self.GetModThread(self, page=self.currentPage, search=True,
                                                          query=self.searchLineEdit.text())
                else:
                    self.getModThread = self.GetModThread(self, page=self.currentPage)
                self.getModThread.gotMod.connect(lambda data: self.displayMods(data, self.currentPage))
                self.getModThread.start()
                self.loadingAnimation = LoadingAnimation(self)
                pp = QPainterPath()
                pp.addRoundedRect(self.rect().toRectF(), 10, 10)
                self.loadingAnimation.setBackgroundClipPath(pp)
                self.startAnimation(True)
        
        def resizeEvent(self, a0):
            super().resizeEvent(a0)
            if self.modInfoPage:
                self.modInfoPage.resize(self.size())
            
            if self.loadingAnimation:
                pp = QPainterPath()
                pp.addRoundedRect(self.rect().toRectF(), 10, 10)
                self.loadingAnimation.setBackgroundClipPath(pp)
        
        def showEvent(self, a0):
            super().showEvent(a0)
            if self.mods:
                pass
            else:
                self.getModThread = self.GetModThread(self)
                self.getModThread.gotMod.connect(self.displayMods)
                self.getModThread.start()
                self.loadingAnimation = LoadingAnimation(self)
                pp = QPainterPath()
                pp.addRoundedRect(self.rect().toRectF(), 10, 10)
                self.loadingAnimation.setBackgroundClipPath(pp)
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
                    print(data)
                    dat = data["result"]
                    self.mods[page] = dat
                    self.totalModsCount = dat["total_hits"]
                    self.finishAnimation(True, True)
                elif page in self.mods:
                    dat = self.mods[page]
                else:
                    self.finishAnimation(True, False)
                    return
                self.model.clear()
                for e, hit in enumerate(dat["hits"]):
                    titleItem = QStandardItem(hit["title"])
                    titleItem.setData(hit, 3)
                    self.model.setItem(e, 0, titleItem)
                    self.model.setItem(e, 1, QStandardItem(hit["author"]))
                    self.model.setItem(e, 2, QStandardItem(
                        datetime.datetime.fromisoformat(hit["date_modified"].split(".")[0]).astimezone().strftime(
                            "%Y-%m-%d %H:%M:%S")
                    ))
                self.retranslateUI()
                self.contentTable.setModel(self.model)
                self.updatePage()
            else:
                if self.mods:
                    self.currentPage -= 1
                    self.currentPage = max(self.currentPage, 1)
                    self.updatePage()
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
                                    datetime.datetime.fromisoformat(
                                        hit["date_modified"].split(".")[0]).astimezone().strftime("%Y-%m-%d %H:%M:%S")
                                ))
                                cnt += 1
                else:
                    self.displayMods(None, self.currentPage)
            except re.error:
                pass
            self.retranslateUI()
            self.contentTable.setModel(self.model)
        
        def searchFinished(self):
            self.getModThread = self.GetModThread(self, page=self.currentPage, search=True,
                                                  query=self.searchLineEdit.text())
            self.getModThread.gotMod.connect(lambda data: self.displayMods(data, self.currentPage))
            self.getModThread.start()
        
        def modInfoPageOpen(self, value):
            item = self.contentTable.model().item(value.row(), 0)
            data = item.text()
            hit_data = item.data(3)
            if hit_data:
                self.modInfoPage = self.ModInfoPage(self, data, hit_data["slug"])
                self.modInfoPage.closePage.connect(self.modInfoPageClose)
                rect = self.rect().adjusted(1, 1, -1, -1)
                self.modInfoPage.setGeometry(rect)
                self.modInfoPage.grabBehind()
                self.modInfoPage.move(QPoint(0, self.height()))
                ani = QPropertyAnimation(self.modInfoPage, b"pos", self)
                ani.setStartValue(QPoint(0, self.height()))
                ani.setEndValue(QPoint(0, 0))
                ani.setKeyValueAt(0.8, QPoint(0, 50))
                ani.setDuration(500)
                ani.setEasingCurve(QEasingCurve.Type.OutQuad)
                ani.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                self.modInfoPage.show()
        
        def modInfoPageClose(self):
            ani = QPropertyAnimation(self.modInfoPage, b"pos", self)
            ani.setStartValue(QPoint(0, 0))
            ani.setEndValue(QPoint(0, self.height()))
            ani.setKeyValueAt(0.8, QPoint(0, self.height() - 50))
            ani.setDuration(500)
            ani.setEasingCurve(QEasingCurve.Type.OutQuad)
            ani.finished.connect(self.closingFinished)
            ani.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        
        def closingFinished(self):
            self.modInfoPage.close()
            self.modInfoPage.deleteLater()
            del self.modInfoPage
            self.modInfoPage = None
        
        def changeAnimation(self, variant, function):
            if variant == "in":
                self.changeAnimationIn()
            else:
                QTimer.singleShot(300, function)
                self.changeAnimationOut()
        
        def changeAnimationIn(self):
            pass
            # ani1 = QPropertyAnimation(self.topNavigationPanel, b"pos", self)
            # pos1 = self.topNavigationPanel.pos()
            # ani1.setStartValue(pos1 + QPoint(100, 0))
            # ani1.setEndValue(pos1)
            # ani1.setDuration(500)
            # ani1.setEasingCurve(QEasingCurve.Type.OutQuint)
            # ani1.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
            # ani11 = OpacityAnimation(self.topNavigationPanel)
            # ani11.setStartValue(0)
            # ani11.setEndValue(100)
            # ani11.setDuration(500)
            # ani11.setEasingCurve(QEasingCurve.Type.OutQuint)
            # ani11.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
            # QTimer.singleShot(50, lambda: self.topNavigationPanel.show())
            # ani22 = OpacityAnimation(self.stackedWidget)
            # ani22.setStartValue(0)
            # ani22.setEndValue(100)
            # ani22.setDuration(500)
            # ani22.setEasingCurve(QEasingCurve.Type.OutQuint)
            # QTimer.singleShot(100, lambda: ani22.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
            # QTimer.singleShot(150, lambda: self.stackedWidget.show())
            ani1 = QPropertyAnimation(self.filterPanel, b"pos", self)
            pos1 = self.filterPanel.pos()
            ani1.setStartValue(pos1 + QPoint(100, 0))
            ani1.setEndValue(pos1)
            ani1.setDuration(500)
            ani1.setEasingCurve(QEasingCurve.Type.OutQuint)
            ani1.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
            ani11 = OpacityAnimation(self.filterPanel)
            ani11.setStartValue(0)
            ani11.setEndValue(100)
            ani11.setDuration(500)
            ani11.setEasingCurve(QEasingCurve.Type.OutQuint)
            ani11.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
            QTimer.singleShot(50, lambda: self.filterPanel.show())
            ani2 = QPropertyAnimation(self.contentTable, b"pos", self)
            pos2 = self.contentTable.pos()
            ani2.setStartValue(pos2 + QPoint(100, 0))
            ani2.setEndValue(pos2)
            ani2.setDuration(500)
            ani2.setEasingCurve(QEasingCurve.Type.OutQuint)
            QTimer.singleShot(100, lambda: ani2.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
            ani22 = OpacityAnimation(self.contentTable)
            ani22.setStartValue(0)
            ani22.setEndValue(100)
            ani22.setDuration(500)
            ani22.setEasingCurve(QEasingCurve.Type.OutQuint)
            QTimer.singleShot(100, lambda: ani22.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
            QTimer.singleShot(150, lambda: self.contentTable.show())
            ani3 = QPropertyAnimation(self.paginator, b"pos", self)
            pos3 = self.paginator.pos()
            ani3.setStartValue(pos3 + QPoint(100, 0))
            ani3.setEndValue(pos3)
            ani3.setDuration(500)
            ani3.setEasingCurve(QEasingCurve.Type.OutQuint)
            QTimer.singleShot(200, lambda: ani3.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
            ani33 = OpacityAnimation(self.paginator)
            ani33.setStartValue(0)
            ani33.setEndValue(100)
            ani33.setDuration(500)
            ani33.setEasingCurve(QEasingCurve.Type.OutQuint)
            QTimer.singleShot(200, lambda: ani33.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
            QTimer.singleShot(250, lambda: self.paginator.show())
        
        def changeAnimationOut(self):
            ani11 = OpacityAnimation(self.filterPanel)
            ani11.setStartValue(100)
            ani11.setEndValue(0)
            ani11.setDuration(500)
            ani11.setEasingCurve(QEasingCurve.Type.OutQuint)
            ani11.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
            ani22 = OpacityAnimation(self.contentTable)
            ani22.setStartValue(100)
            ani22.setEndValue(0)
            ani22.setDuration(500)
            ani22.setEasingCurve(QEasingCurve.Type.OutQuint)
            QTimer.singleShot(100, lambda: ani22.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
            ani33 = OpacityAnimation(self.paginator)
            ani33.setStartValue(100)
            ani33.setEndValue(0)
            ani33.setDuration(500)
            ani33.setEasingCurve(QEasingCurve.Type.OutQuint)
            QTimer.singleShot(200, lambda: ani33.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
            ani11.finished.connect(lambda: self.filterPanel.hide())
            ani22.finished.connect(lambda: self.contentTable.hide())
            ani33.finished.connect(lambda: self.paginator.hide())
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.topNavigationPanel = Panel(self)
        self.horizontalLayout = QHBoxLayout(self.topNavigationPanel)
        self.page1 = PushButton(self.topNavigationPanel)
        self.page1.setMinimumHeight(32)
        self.page1.setCheckable(True)
        self.page1.setChecked(True)
        self.page1.setAutoExclusive(True)
        self.page1.setWidgetAttribute("outlinedButton")
        self.page1.pressed.connect(lambda: self.setCurrentPage(0))
        self.horizontalLayout.addWidget(self.page1)
        self.page2 = PushButton(self.topNavigationPanel)
        self.page2.setMinimumHeight(32)
        self.page2.setMinimumWidth(64)
        self.page2.setCheckable(True)
        self.page2.setAutoExclusive(True)
        self.page2.setWidgetAttribute("outlinedButton")
        self.page2.released.connect(lambda: self.setCurrentPage(1))
        self.horizontalLayout.addWidget(self.page2)
        self.horizontalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.horizontalLayout.addItem(self.horizontalSpacer)
        
        self.stackedWidget = AnimatedStackedWidget(self)
        
        self.page1Frame = self.DownloadVanilla(self.stackedWidget)
        self.stackedWidget.addWidget(self.page1Frame)
        
        self.page2Frame = self.DownloadMods(self.stackedWidget)
        self.stackedWidget.addWidget(self.page2Frame)
        
        app.registerRetranslateFunction(self.retranslateUI)
        self.retranslateUI()
    
    def retranslateUI(self):
        self.page1.setText(self.tr("DownloadPage.Pages.1.Name"))  # 原版游戏
        menu = RoundedMenu(self.page1)
        action1 = QAction(menu)
        action1.setText(self.tr("DownloadPage.Pages.1.Actions.Reload"))  # 重新加载
        action1.triggered.connect(self.page1Frame.reloadVersions)
        menu.addAction(action1)
        self.page1.setMenu(menu)
        self.page2.setText(self.tr("DownloadPage.Pages.2.Name"))  # 模组
        
        self.updateIcon()
    
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
    
    def changeAnimation(self, variant, function):
        if variant == "in":
            self.changeAnimationIn()
        else:
            QTimer.singleShot(300, function)
            self.changeAnimationOut()
    
    def changeAnimationIn(self):
        ani1 = QPropertyAnimation(self.topNavigationPanel, b"pos", self)
        pos1 = self.topNavigationPanel.pos()
        ani1.setStartValue(pos1 + QPoint(100, 0))
        ani1.setEndValue(pos1)
        ani1.setDuration(500)
        ani1.setEasingCurve(QEasingCurve.Type.OutQuint)
        ani1.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        ani11 = OpacityAnimation(self.topNavigationPanel)
        ani11.setStartValue(0)
        ani11.setEndValue(100)
        ani11.setDuration(500)
        ani11.setEasingCurve(QEasingCurve.Type.OutQuint)
        ani11.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        QTimer.singleShot(50, lambda: self.topNavigationPanel.show())
        ani22 = OpacityAnimation(self.stackedWidget)
        ani22.setStartValue(0)
        ani22.setEndValue(100)
        ani22.setDuration(500)
        ani22.setEasingCurve(QEasingCurve.Type.OutQuint)
        QTimer.singleShot(100, lambda: ani22.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
        QTimer.singleShot(150, lambda: self.stackedWidget.show())
        
        if self.stackedWidget.currentWidget():
            try:
                self.stackedWidget.currentWidget().changeAnimationIn()
            except AttributeError:
                raise
    
    def changeAnimationOut(self):
        ani11 = OpacityAnimation(self.topNavigationPanel)
        ani11.setStartValue(100)
        ani11.setEndValue(0)
        ani11.setDuration(500)
        ani11.setEasingCurve(QEasingCurve.Type.OutQuint)
        ani11.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        ani22 = OpacityAnimation(self.stackedWidget)
        ani22.setStartValue(100)
        ani22.setEndValue(0)
        ani22.setDuration(500)
        ani22.setEasingCurve(QEasingCurve.Type.OutQuint)
        QTimer.singleShot(100, lambda: ani22.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
        ani11.finished.connect(lambda: self.topNavigationPanel.hide())
        ani22.finished.connect(lambda: self.stackedWidget.hide())
        
        if self.stackedWidget.currentWidget():
            try:
                self.stackedWidget.currentWidget().changeAnimationOut()
            except AttributeError:
                raise
    
    def postToggleTheme(self):
        self.updateIcon()
    
    def updateIcon(self):
        colour = "black" if getTheme() == Theme.Light else "white"
        page1Menu = self.page1.menu()
        page1Menu.actions()[0].setIcon(QIcon(f":/Reload-{colour}.svg"))
    
    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        
        self.topNavigationPanel.move(QPoint(15, 15))
        self.topNavigationPanel.resize(QSize(self.width() - 30, 54))
        
        self.stackedWidget.move(QPoint(15, 79))
        self.stackedWidget.resize(QSize(self.width() - 30, self.height() - 15 - 79))


class SettingsPage(QFrame):
    class LaunchSettings(QFrame):
        class GetJavaThread(QThread):
            gettingFinished = pyqtSignal(list)
            
            def run(self):
                java_list = []
                where_out = subprocess.run(
                    ["which" if GetOperationSystemName().lower() != "windows" else "where", "java"],
                    capture_output=True, check=False, creationflags=subprocess.CREATE_NO_WINDOW if hasattr(
                        subprocess, "CREATE_NO_WINDOW") else 0).stdout
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
            self.form_4_ComboBox.currentIndexChanged.connect(self.updateSeparationMode)
            self.form_4_VerticalLayout.addWidget(self.form_4_ComboBox)
            
            self.form_4_HorizontalLayout = QHBoxLayout()
            self.form_4_VerticalLayout.addLayout(self.form_4_HorizontalLayout)
            
            self.form_4_CheckBox = CheckBox(self.groupBox_Java)
            self.form_4_CheckBox.setChecked(
                settings["LaunchSettings"]["VersionSeparationConfig"]["ShareVersionOptions"])
            self.form_4_CheckBox.toggled.connect(self.updateSharingOptionsState)
            self.form_4_HorizontalLayout.addWidget(self.form_4_CheckBox)
            
            self.form_4_CheckBox_2 = CheckBox(self.groupBox_Java)
            self.form_4_CheckBox_2.setChecked(
                settings["LaunchSettings"]["VersionSeparationConfig"]["ShareVersionResourcePacks"])
            self.form_4_CheckBox_2.toggled.connect(self.updateSharingResourcePacksState)
            self.form_4_HorizontalLayout.addWidget(self.form_4_CheckBox_2)
            
            self.form_4_HorizontalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            self.form_4_HorizontalLayout.addItem(self.form_4_HorizontalSpacer)
            
            self.form_5_Label = Label(self.groupBox_Java)
            self.form_1.setWidget(1, QFormLayout.ItemRole.LabelRole, self.form_5_Label)
            
            self.form_5_ComboBox = ComboBox(self.groupBox_Java)
            self.form_5_ComboBox.currentIndexChanged.connect(self.updateVisibilityMode)
            self.form_1.setWidget(1, QFormLayout.ItemRole.FieldRole, self.form_5_ComboBox)
            
            self.form_1_Label = Label(self.groupBox_Java)
            self.form_1.setWidget(2, QFormLayout.ItemRole.LabelRole, self.form_1_Label)
            
            self.form_1_VerticalLayout = QVBoxLayout()
            self.form_1_VerticalLayout.setContentsMargins(0, 0, 0, 0)
            self.form_1_VerticalLayout.setSpacing(5)
            self.form_1.setLayout(2, QFormLayout.ItemRole.FieldRole, self.form_1_VerticalLayout)
            
            self.form_1_ComboBox = ComboBox(self.groupBox_Java)
            self.form_1_ComboBox.setEditable(True)
            self.form_1_ComboBox.setFont(fixedFont)
            self.form_1_ComboBox.addItem(settings["LaunchSettings"]["Java"]["JavaPath"],
                                         settings["LaunchSettings"]["Java"]["JavaPath"])
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
            
            self.groupBox_Allocation = GroupBox(self.scrollAreaWidgetContents)
            self.verticalLayout.addWidget(self.groupBox_Allocation)
            
            self.verticalLayout_2 = QVBoxLayout(self.groupBox_Allocation)
            
            self.horizontalLayout = QHBoxLayout()
            
            self.radioButton = RadioButton(self.groupBox_Allocation)
            self.radioButton.setChecked(settings["LaunchSettings"]["MemoryAllocation"]["AutoAllocate"])
            self.radioButton.toggled.connect(lambda state: self.updateAllocationMode(True))
            self.horizontalLayout.addWidget(self.radioButton)
            
            self.radioButton_2 = RadioButton(self.groupBox_Allocation)
            self.radioButton_2.setChecked(not settings["LaunchSettings"]["MemoryAllocation"]["AutoAllocate"])
            self.radioButton_2.toggled.connect(lambda state: self.updateAllocationMode(False))
            self.horizontalLayout.addWidget(self.radioButton_2)
            
            self.verticalLayout_2.addLayout(self.horizontalLayout)
            
            self.form_3 = QFormLayout()
            
            self.form_6_Label = Label(self.groupBox_Allocation)
            self.form_3.setWidget(0, QFormLayout.ItemRole.LabelRole, self.form_6_Label)
            
            self.form_6_HorizontalLayout = QHBoxLayout()
            self.form_3.setLayout(0, QFormLayout.ItemRole.FieldRole, self.form_6_HorizontalLayout)
            
            self.form_6_Slider = Slider(Qt.Orientation.Horizontal, self.groupBox_Allocation)
            self.form_6_Slider.setEnabled(self.radioButton_2.isChecked())
            self.form_6_Slider.valueChanged.connect(self.updateInitialMemory)
            self.form_6_HorizontalLayout.addWidget(self.form_6_Slider)
            
            self.form_6_ValueLabel = Label(self.groupBox_Allocation)
            self.form_6_HorizontalLayout.addWidget(self.form_6_ValueLabel)
            
            self.form_7_Label = Label(self.groupBox_Allocation)
            self.form_3.setWidget(1, QFormLayout.ItemRole.LabelRole, self.form_7_Label)
            
            self.form_7_HorizontalLayout = QHBoxLayout()
            self.form_3.setLayout(1, QFormLayout.ItemRole.FieldRole, self.form_7_HorizontalLayout)
            
            self.form_7_Slider = Slider(Qt.Orientation.Horizontal, self.groupBox_Allocation)
            self.form_7_Slider.setEnabled(self.radioButton_2.isChecked())
            self.form_7_Slider.valueChanged.connect(self.updateMaxMemory)
            self.form_7_HorizontalLayout.addWidget(self.form_7_Slider)
            
            self.form_7_ValueLabel = Label(self.groupBox_Allocation)
            self.form_7_HorizontalLayout.addWidget(self.form_7_ValueLabel)
            
            self.updateInitialMemory(self.form_6_Slider.value())
            self.updateMaxMemory(self.form_7_Slider.value())
            
            self.verticalLayout_2.addLayout(self.form_3)
            
            self.series = QPieSeries()
            self.series.setHoleSize(0.35)
            
            self.chart = QChart()
            self.chart.addSeries(self.series)
            self.chart.legend().hide()
            
            self.chart_view = QChartView(self.chart)
            self.chart_view.setRenderHints(self.chart_view.renderHints())
            
            self.chart_view.setFixedHeight(300)
            
            self.verticalLayout_2.addWidget(self.chart_view)
            
            self.groupBox_Advanced = GroupBox(self.scrollAreaWidgetContents)
            self.groupBox_Advanced.setCheckable(True)
            self.groupBox_Advanced.setChecked(
                bool(settings["LaunchSettings"]["Java"]["JVM"]["JVMArguments"]["Arguments"]))
            self.verticalLayout.addWidget(self.groupBox_Advanced)
            
            self.form_2 = QFormLayout(self.groupBox_Advanced)
            
            self.form_2_Label = Label(self.groupBox_Advanced)
            self.form_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.form_2_Label)
            
            self.form_2_TextEdit = TextEdit(self.groupBox_Advanced)
            self.form_2_TextEdit.setFont(fixedFont)
            self.form_2_TextEdit.setText(
                settings["LaunchSettings"]["Java"]["JVM"]["JVMArguments"][
                    "Arguments"] or "-XX:+UseZGC -Dfml.ignoreInvalidMinecraftCertificates=True -Dfml.ignorePatchDiscrepancies=True -Dlog4j2.formatMsgNoLookups=true -Dfile.encoding=UTF-8 -Dstdout.encoding=UTF-8 -Dstderr.encoding=UTF-8 -Dorg.lwjgl.util.DebugLoader=true -Dorg.lwjgl.util.Debug=true")
            self.form_2_TextEdit.textChanged.connect(self.setJVMArguments)
            self.form_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.form_2_TextEdit)
            
            self.form_3_Label = Label(self.groupBox_Advanced)
            self.form_2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.form_3_Label)
            
            self.form_3_TextEdit = TextEdit(self.groupBox_Advanced)
            self.form_3_TextEdit.setFont(fixedFont)
            self.form_3_TextEdit.textChanged.connect(self.setGameExtraArguments)
            self.form_2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.form_3_TextEdit)
            
            self.verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
            self.verticalLayout.addItem(self.verticalSpacer)
            
            self.scrollArea.setWidget(self.scrollAreaWidgetContents)
            self.scrollArea.setWidgetResizable(True)
            
            self.getJavaThread = None
            self.javaList = None
            self.updateJavaPathComboBox()
            
            timer = QTimer(self)
            timer.timeout.connect(self.updateMemDisplay)
            timer.start(1000)
            self.updateMemDisplay()
            
            app.registerRetranslateFunction(self.retranslateUI)
            self.retranslateUI()
        
        def retranslateUI(self):
            self.groupBox_Java.setTitle(self.tr("SettingsPage.LaunchSettings.GroupBox_Java.Title"))  # 启动设置
            self.form_4_Label.setText(self.tr("SettingsPage.LaunchSettings.Form.4.Label.Text"))  # 版本隔离
            index = settings["LaunchSettings"]["VersionSeparation"]
            self.form_4_ComboBox.clear()
            self.form_4_ComboBox.addItem(self.tr("SettingsPage.LaunchSettings.Form.4.ComboBox.Items.1"))  # 不隔离
            self.form_4_ComboBox.addItem(self.tr("SettingsPage.LaunchSettings.Form.4.ComboBox.Items.2"))  # 隔离所有版本
            self.form_4_ComboBox.addItem(self.tr("SettingsPage.LaunchSettings.Form.4.ComboBox.Items.3"))  # 隔离模组加载器与其他版本
            self.form_4_ComboBox.addItem(self.tr("SettingsPage.LaunchSettings.Form.4.ComboBox.Items.4"))  # 隔离正式版与测试版
            self.form_4_ComboBox.setCurrentIndex(index)
            self.form_4_ComboBox.setToolTip("""通过修改游戏的运行路径，使游戏的运行路径各不相同，从而避免模组冲突。
◉ 不隔离：所有版本都在同一文件夹下；
◉ 隔离所有版本：所有版本的文件各不互通，这可能会导致你电脑的 Ctrl、C 和 V 键的使用次数增多（人话：复制很麻烦）；
◉ 隔离模组加载器与其他版本：（暂未支持）模组加载器（如 Forge、Fabric）互相隔离，其他版本（如原版）则不隔离；
◉ 隔离正式版和测试版：隔离正式版和测试版（快照及远古版）。
除了第一种，其他的均会在版本文件夹下创建内容。
启动器处理方式根据版本有区别，请以游戏具体文件夹为准。""")
            self.form_4_CheckBox.setText(self.tr("SettingsPage.LaunchSettings.Form.4.CheckBox.Text"))  # 共用设置文件
            self.form_4_CheckBox.setToolTip(
                "所有版本使用同一个设置文件\n注意：这会覆盖当前版本设置！请先将设置文件复制到根目录，或者删除根目录的设置文件。")
            self.form_4_CheckBox_2.setText(self.tr("SettingsPage.LaunchSettings.Form.4.CheckBox_2.Text"))  # 共用资源包
            self.form_4_CheckBox_2.setToolTip(
                "所有版本使用同一个资源包文件夹\n注意：当前版本的资源包会被移动到全局资源包文件夹里。")
            self.form_5_Label.setText(self.tr("SettingsPage.LaunchSettings.Form.5.Label.Text"))  # 启动器可见性
            index = settings["LaunchSettings"]["LauncherVisibility"]
            self.form_5_ComboBox.clear()
            self.form_5_ComboBox.addItem(self.tr("SettingsPage.LaunchSettings.Form.5.ComboBox.Items.1"))  # 启动游戏后保持不变
            self.form_5_ComboBox.addItem(self.tr("SettingsPage.LaunchSettings.Form.5.ComboBox.Items.2"))  # 启动游戏后隐藏
            self.form_5_ComboBox.addItem(self.tr("SettingsPage.LaunchSettings.Form.5.ComboBox.Items.3"))  # 启动游戏后立即关闭
            self.form_5_ComboBox.addItem(
                self.tr("SettingsPage.LaunchSettings.Form.5.ComboBox.Items.4"))  # 启动游戏后隐藏，游戏结束后重新显示
            self.form_5_ComboBox.addItem(
                self.tr("SettingsPage.LaunchSettings.Form.5.ComboBox.Items.5"))  # 启动游戏后隐藏，游戏结束后关闭
            self.form_5_ComboBox.setCurrentIndex(index)
            self.form_5_ComboBox.setToolTip("""设置启动器启动后的可见性。
◉ 游戏启动后保持不变：启动器的窗口在启动后仍然保持显示；
◉ 游戏启动后隐藏：启动器的窗口在启动后隐藏，可以通过系统托盘（如果有的话）打开；
◉ 启动游戏后立即关闭：启动后启动器直接退出，需要重新打开；
◉ 启动游戏后隐藏，游戏结束后重新显示：同“游戏启动后隐藏”，只不会会在游戏结束后自动显示；
◉ 启动游戏后隐藏，游戏结束后关闭：启动器的窗口在启动后隐藏，游戏如果正常退出则关闭，未正常退出则显示。""")
            self.form_1_Label.setText(self.tr("SettingsPage.LaunchSettings.Form.1.Label.Text"))  # Java 路径
            if self.form_1_PushButton.isChecked():
                self.form_1_ComboBox.setCurrentText(
                    self.tr("SettingsPage.LaunchSettings.Form.1.ComboBox.AutoSelect"))  # 自动选择
            self.form_1_ComboBox.setToolTip("""手动输入 Java 路径，启动器自动检测版本号。
如果输入了版本号，请在路径左右打上英文半角双引号（\"...\"），以方便启动器检测路径。
启动器会自动纠正版本号，不用担心。而且版本号是给你看的，不是给我看的，不要糊弄人！！！
同时，启动器会自动补全相对路径，以启动器当前所在文件夹补全。""")
            self.form_1_PushButton.setText(self.tr("SettingsPage.LaunchSettings.Form.1.PushButton.Text"))  # 自动选择 Java
            self.form_1_PushButton.setToolTip("""让启动器自动选择 Java。
因技术原因，有的 Java 检测不出来。
如果无法启动，请尝试取消该选项。""")
            self.form_1_PushButton_2.setText(self.tr("SettingsPage.LaunchSettings.Form.1.PushButton_2.Text"))  # 添加 Java
            self.groupBox_Allocation.setTitle(self.tr("SettingsPage.LaunchSettings.GroupBox_Allocation.Title"))  # 内存分配
            self.radioButton.setText(self.tr("SettingsPage.LaunchSettings.RadioButton.Text"))  # 自动分配
            self.radioButton_2.setText(self.tr("SettingsPage.LaunchSettings.RadioButton_2.Text"))  # 手动分配
            self.form_6_Label.setText(self.tr("SettingsPage.LaunchSettings.Form.6.Label.Text"))  # 初始内存
            self.form_7_Label.setText(self.tr("SettingsPage.LaunchSettings.Form.7.Label.Text"))  # 最大内存
            self.groupBox_Advanced.setTitle(
                self.tr("SettingsPage.LaunchSettings.Form.1.GroupBox_Advanced.Text"))  # 高级启动设置
            self.form_2_Label.setText("JVM 启动参数头")
            self.form_2_TextEdit.setToolTip("""这一段参数会加在 JVM 参数的最前面，自动去除前后空格。
比如说你设置的是：
“-Dchengwm.CMCL.abc=true”
无论前后有没有空格：
“              -Dchengwm.CMCL.abc=true                                  ”
JVM 参数就是：
<code>\"{Java 路径}\" -Dchengwm.CMCL.abc=true {Minecraft 启动的其他 JVM 参数} -cp {一堆 jar 文件} {游戏参数}</code>。

<blockquote>注明：实际除了设置的参数位置以外，后面的参数根据版本的不同有所差异。</blockquote>


<strong>奉劝你去看一下 JVM 参数的相关文档，任何因为修改 JVM 参数引发的启动问题均不在启动器作者的受理范围内</strong>
（前提是你拿其他启动器也搞不了，如果确实是本启动器的问题，请附上你的 JVM 参数，你的 Java 版本以及你的游戏版本）""".replace(
                "\n", "<br>"))
            self.form_3_Label.setText("额外启动参数")
            self.form_3_TextEdit.setToolTip("""设置额外启动参数，加在游戏参数的末尾。
比如说，如果你想启动时全屏（不是最大化），你可以这样设置：
<code>-fullscreen</code>
自动去除前后空格，设置错误不影响启动（但是影响游玩）
同时，这是全局设置，请注意版本兼容性。""".replace(
                "\n", "<br>"))
            self.updateChart()
        
        def updateJavaPathComboBox(self, state=True):
            if self.form_1_PushButton.isChecked():
                self.form_1_ComboBox.setDisabled(True)
                self.form_1_ComboBox.clear()
                self.form_1_ComboBox.setFont(app.font())
                self.form_1_ComboBox.setCurrentText(self.tr("SettingsPage.LaunchSettings.Form.1.ComboBox.AutoSelect"))
                self.form_1_PushButton_2.setDisabled(True)
                if self.getJavaThread:
                    self.getJavaThread.terminate()
                    self.getJavaThread = None
                if self.javaList:
                    self.javaList = None
            else:
                self.form_1_ComboBox.setEnabled(True)
                self.form_1_ComboBox.setFont(fixedFont)
                self.form_1_PushButton_2.setEnabled(True)
                if not state:
                    self.form_1_ComboBox.setCurrentText("")
                if not self.getJavaThread:
                    self.getJavaThread = self.GetJavaThread(self)
                    self.getJavaThread.gettingFinished.connect(self.updateJavaPathSelections)
                    self.getJavaThread.start()
        
        def updateJavaPathSelections(self, java_list):
            path = self.form_1_ComboBox.currentData() or self.form_1_ComboBox.currentText()
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
            index = 0
            for idx, java in enumerate(java_list):
                if str(Path(java[0]).absolute()) == path:
                    index = idx
                self.form_1_ComboBox.addItem(f'"{str(Path(java[0]).absolute())}" ({java[1]})', Path(java[0]).absolute())
            self.form_1_ComboBox.setCurrentIndex(index)
        
        def updateJavaPath(self, text):
            if not self.form_1_PushButton.isChecked():
                settings["LaunchSettings"]["Java"]["AutoSelect"] = False
                settings["LaunchSettings"]["Java"]["JavaPath"] = str(
                    self.form_1_ComboBox.currentData() or "")
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
                text = str(Path(text).resolve())
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
                self.form_1_ComboBox.addItem(f'"{text}" ({version_data})', Path(text).absolute())
                self.form_1_ComboBox.setCurrentIndex(self.form_1_ComboBox.count() - 1)
        
        def updateJavaSelectState(self, state):
            self.updateJavaPathComboBox(state)
        
        def selectJava(self):
            self.form_1_PushButton_2.setDown(False)
            fileDialogue = QFileDialog.getOpenFileName(self, "选择 Java", str(Path(".").absolute()),
                                                       "java.exe javaw.exe")
            if any(fileDialogue):
                javaPath = str(Path(fileDialogue[0]).absolute())
                self.updateJavaPathCandidates(javaPath)
        
        def updateSeparationMode(self):
            if not self.form_4_ComboBox.count():
                return
            index = self.form_4_ComboBox.currentIndex()
            settings["LaunchSettings"]["VersionSeparation"] = index
            if index != 0:
                self.form_4_CheckBox.setEnabled(True)
                self.form_4_CheckBox_2.setEnabled(True)
            else:
                self.form_4_CheckBox.setDisabled(True)
                self.form_4_CheckBox_2.setDisabled(True)
                self.form_4_CheckBox.setChecked(False)
                self.form_4_CheckBox_2.setChecked(False)
        
        def updateSharingOptionsState(self, state):
            settings["LaunchSettings"]["VersionSeparationConfig"]["ShareVersionOptions"] = state
        
        def updateSharingResourcePacksState(self, state):
            settings["LaunchSettings"]["VersionSeparationConfig"]["ShareVersionResourcePacks"] = state
        
        def updateMemDisplay(self):
            self.updateChart()
            memory = psutil.virtual_memory()
            available = memory.available
            
            self.form_6_Slider.setMaximum(available // 1024 // 1024)
            self.form_7_Slider.setMaximum(available // 1024 // 1024)
            
            if self.radioButton.isChecked():
                max_memory = int(4294967296 * (psutil.virtual_memory().free / 4294967296))
                max_memory = min(max_memory, available)
                ani = QPropertyAnimation(self.form_6_Slider, b"value", self)
                ani.setStartValue(self.form_6_Slider.value())
                ani.setEndValue(max_memory // 1024 // 1024)
                ani.setDuration(1000)
                ani.setEasingCurve(QEasingCurve.Type.InOutQuad)
                ani.start()
                ani = QPropertyAnimation(self.form_7_Slider, b"value", self)
                ani.setStartValue(self.form_7_Slider.value())
                ani.setEndValue(max_memory // 1024 // 1024)
                ani.setDuration(1000)
                ani.setEasingCurve(QEasingCurve.Type.InOutQuad)
                ani.start()
        
        def updateChart(self):
            memory = psutil.virtual_memory()
            total = memory.total / (1024 ** 3)  # GB
            available = memory.available / (1024 ** 3)
            used = memory.used / (1024 ** 3)
            percent = memory.percent
            
            max_memory = self.form_7_Slider.value() / 1024
            max_memory = min(max_memory, available)
            available_percent = (available - max_memory) / total * 100
            
            self.chart.setTheme(
                QChart.ChartTheme.ChartThemeDark if getTheme() == Theme.Dark else QChart.ChartTheme.ChartThemeLight)
            self.chart.setBackgroundBrush(QBrush(QColor(0, 0, 0, 0)))
            
            self.series.clear()
            
            used_slice = self.series.append(
                self.tr("SettingsPage.LaunchSettings.UsedMemory").format(used, percent),
                used
            )  # 已使用 {:.2f}GB ({:.1f}%)
            allocable_slice = self.series.append(
                self.tr("SettingsPage.LaunchSettings.AllocableMemory").format(max_memory, max_memory / total * 100),
                max_memory
            )  # 游戏分配 {:.2f}GB ({:.1f}%)
            if available_percent > 0:
                available_slice = self.series.append(
                    self.tr("SettingsPage.LaunchSettings.AvailableMemory").format(available - max_memory,
                                                                                  available_percent),
                    available - max_memory)  # 可用 {:.2f}GB ({:.1f}%)
            used_slice.setLabelVisible(True)
            allocable_slice.setLabelVisible(True)
            if available_percent > 3:
                available_slice.setLabelVisible(True)
            
            used_slice.setColor(QColor(255, 99, 132))
            allocable_slice.setColor(QColor(132, 164, 235))
            if available_percent > 0:
                available_slice.setColor(QColor(75, 192, 192))
            
            allocable_slice.setExploded(True)
        
        def updateAllocationMode(self, mode):
            settings["LaunchSettings"]["MemoryAllocation"]["AutoAllocate"] = mode
            if not mode:
                self.form_6_Slider.setEnabled(True)
                self.form_7_Slider.setEnabled(True)
                self.updateMaxMemory(self.form_7_Slider.value())
                self.updateInitialMemory(self.form_6_Slider.value())
            else:
                self.form_6_Slider.setEnabled(False)
                self.form_7_Slider.setEnabled(False)
        
        def updateInitialMemory(self, value):
            if value > self.form_7_Slider.value():
                value = self.form_7_Slider.value()
                self.form_6_Slider.setValue(value)
            if settings["LaunchSettings"]["MemoryAllocation"]["AutoAllocate"]:
                settings["LaunchSettings"]["MemoryAllocation"]["AllocationConfig"]["InitialHeapSize"] = None
            else:
                settings["LaunchSettings"]["MemoryAllocation"]["AllocationConfig"][
                    "InitialHeapSize"] = value * 1024 * 1024
            self.form_6_ValueLabel.setText(f"{value}MB")
        
        def updateMaxMemory(self, value):
            if self.form_6_Slider.value() > self.form_7_Slider.value():
                self.form_6_Slider.setValue(self.form_7_Slider.value())
            if settings["LaunchSettings"]["MemoryAllocation"]["AutoAllocate"]:
                settings["LaunchSettings"]["MemoryAllocation"]["AllocationConfig"][
                    "MaximumHeapSize"] = value * 1024 * 1024
            else:
                settings["LaunchSettings"]["MemoryAllocation"]["AllocationConfig"][
                    "MaximumHeapSize"] = value * 1024 * 1024
            self.form_7_ValueLabel.setText(f"{value}MB")
        
        def setJVMArguments(self):
            settings["LaunchSettings"]["Java"]["JVM"]["JVMArguments"]["Arguments"] = self.form_2_TextEdit.toPlainText()
        
        def setGameExtraArguments(self):
            pass
        
        def updateVisibilityMode(self):
            if not self.form_5_ComboBox.count():
                return
            index = self.form_5_ComboBox.currentIndex()
            settings["LaunchSettings"]["LauncherVisibility"] = index
        
        def changeAnimation(self, variant, function):
            if variant == "in":
                self.changeAnimationIn()
            else:
                self.changeAnimationOut()
                QTimer.singleShot(300, function)
        
        def changeAnimationIn(self):
            ani1 = QPropertyAnimation(self.groupBox_Java, b"pos", self)
            pos1 = self.groupBox_Java.pos()
            ani1.setStartValue(pos1 + QPoint(100, 0))
            ani1.setEndValue(pos1)
            ani1.setDuration(500)
            ani1.setEasingCurve(QEasingCurve.Type.OutQuint)
            ani1.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
            ani11 = OpacityAnimation(self.groupBox_Java)
            ani11.setStartValue(0)
            ani11.setEndValue(100)
            ani11.setDuration(500)
            ani11.setEasingCurve(QEasingCurve.Type.OutQuint)
            ani11.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
            ani2 = QPropertyAnimation(self.groupBox_Allocation, b"pos", self)
            pos2 = self.groupBox_Allocation.pos()
            ani2.setStartValue(pos2 + QPoint(100, 0))
            ani2.setEndValue(pos2)
            ani2.setDuration(500)
            ani2.setEasingCurve(QEasingCurve.Type.OutQuint)
            QTimer.singleShot(100, lambda: ani2.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
            ani22 = OpacityAnimation(self.groupBox_Allocation)
            ani22.setStartValue(0)
            ani22.setEndValue(100)
            ani22.setDuration(500)
            ani22.setEasingCurve(QEasingCurve.Type.OutQuint)
            QTimer.singleShot(100, lambda: ani22.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
            ani3 = QPropertyAnimation(self.groupBox_Advanced, b"pos", self)
            pos3 = self.groupBox_Advanced.pos()
            ani3.setStartValue(pos3 + QPoint(100, 0))
            ani3.setEndValue(pos3)
            ani3.setDuration(500)
            ani3.setEasingCurve(QEasingCurve.Type.OutQuint)
            QTimer.singleShot(200, lambda: ani3.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
            ani33 = OpacityAnimation(self.groupBox_Advanced)
            ani33.setStartValue(0)
            ani33.setEndValue(100)
            ani33.setDuration(500)
            ani33.setEasingCurve(QEasingCurve.Type.OutQuint)
            QTimer.singleShot(200, lambda: ani33.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
        
        def changeAnimationOut(self):
            ani11 = OpacityAnimation(self.groupBox_Java)
            ani11.setStartValue(100)
            ani11.setEndValue(0)
            ani11.setDuration(500)
            ani11.setEasingCurve(QEasingCurve.Type.OutQuint)
            ani11.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
            ani22 = OpacityAnimation(self.groupBox_Allocation)
            ani22.setStartValue(100)
            ani22.setEndValue(0)
            ani22.setDuration(500)
            ani22.setEasingCurve(QEasingCurve.Type.OutQuint)
            QTimer.singleShot(100, lambda: ani22.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
            ani33 = OpacityAnimation(self.groupBox_Advanced)
            ani33.setStartValue(100)
            ani33.setEndValue(0)
            ani33.setDuration(500)
            ani33.setEasingCurve(QEasingCurve.Type.OutQuint)
            QTimer.singleShot(200, lambda: ani33.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
        
        def resizeEvent(self, a0):
            super().resizeEvent(a0)
            self.form_1_ComboBox.lineEdit().setMinimumHeight(
                self.form_1_ComboBox.height() - (self.form_1_ComboBox.lineEdit().y() * 2))
    
    class LauncherSettings(QFrame):
        def __init__(self, parent):
            super().__init__(parent)
            self.mainLayout = QVBoxLayout(self)
            self.scrollArea = ScrollArea(self)
            self.mainLayout.addWidget(self.scrollArea)
            
            self.scrollAreaWidgetContents = QWidget()
            
            self.verticalLayout = QVBoxLayout(self.scrollAreaWidgetContents)
            
            self.groupBox = GroupBox(self.scrollAreaWidgetContents)
            self.verticalLayout.addWidget(self.groupBox)
            
            self.formLayout = QFormLayout(self.groupBox)
            
            self.form_1_Label = Label(self.groupBox)
            self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.form_1_Label)
            
            self.form_1_Slider = Slider(Qt.Orientation.Horizontal, self.groupBox)
            self.form_1_Slider.setMinimum(1)
            self.form_1_Slider.setMaximum(max(1, psutil.cpu_count(logical=False) - 1))
            self.form_1_Slider.setValue(min(settings["LauncherSettings"]["DownloadSettings"]["DownloadThreadsCount"],
                                            self.form_1_Slider.maximum()))
            self.form_1_Slider.valueChanged.connect(self.downloadThreadsCountChanged)
            self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.form_1_Slider)
            
            self.form_2_Label = Label(self.groupBox)
            self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.form_2_Label)
            
            self.form_2_Slider = Slider(Qt.Orientation.Horizontal, self.groupBox)
            self.form_2_Slider.setMinimum(1)
            self.form_2_Slider.setMaximum(2048)
            self.form_2_Slider.setValue(
                settings["LauncherSettings"]["DownloadSettings"]["DownloadChunkSize"])
            self.form_2_Slider.valueChanged.connect(self.downloadChunkSizeChanged)
            self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.form_2_Slider)
            
            self.groupBox_2 = GroupBox(self)
            self.verticalLayout.addWidget(self.groupBox_2)
            
            self.formLayout_2 = QFormLayout(self.groupBox_2)
            
            self.form_3_Label = Label(self.groupBox_2)
            self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.form_3_Label)
            
            self.form_3_ComboBox = ComboBox(self.groupBox_2)
            self.form_3_ComboBox.currentIndexChanged.connect(self.selectMirrorSource)
            self.formLayout_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.form_3_ComboBox)
            
            self.verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
            self.verticalLayout.addItem(self.verticalSpacer)
            
            self.scrollArea.setWidget(self.scrollAreaWidgetContents)
            self.scrollArea.setWidgetResizable(True)
            
            app.registerRetranslateFunction(self.retranslateUI)
            self.retranslateUI()
        
        def retranslateUI(self):
            self.groupBox.setTitle(self.tr("SettingsPage.LauncherSettings.GroupBox.Title"))  # 下载设置
            self.form_1_Label.setText(self.tr("SettingsPage.LauncherSettings.Form.1.Label.Text").format(
                self.form_1_Slider.value()))
            self.form_1_Slider.setToolTip(
                f"设置下载游戏依赖库、资源以及多线程下载器下载时最多的线程数，默认为 {min(8, self.form_1_Slider.maximum())}。<br>这个的取值范围为 1 ~ {self.form_1_Slider.maximum()}，其中 1 表示单线程，也就是仅一条线程。<br>线程数拉的越高，理论上下载速度越快，但是线程数太高会造成<strong>严重的卡顿</strong>。")
            self.form_2_Label.setText(f"下载区块大小：{self.form_2_Slider.value():04}KB")
            self.form_2_Slider.setToolTip(
                "设置多线程下载器下载时每一个下载区块的大小，范围为 1KB ~ 2MB（2048KB）。\n区块大小越大，使用的线程会变少，同时下载单个区块的时间可能会变长，反之亦然。\n需要自行平衡，这里默认值为 1MB。")
            self.groupBox_2.setTitle("镜像源")
            self.form_3_Label.setText("镜像源")
            idx = max(self.form_3_ComboBox.currentIndex(), 0)
            self.form_3_ComboBox.clear()
            self.form_3_ComboBox.addItem("官方源")
            self.form_3_ComboBox.addItem("BMCLAPI")
            self.form_3_ComboBox.setCurrentIndex(idx)
        
        def downloadThreadsCountChanged(self, value):
            self.form_1_Label.setText(self.tr("SettingsPage.LauncherSettings.Form.1.Label.Text").format(
                self.form_1_Slider.value()))
            settings["LauncherSettings"]["DownloadSettings"]["DownloadThreadsCount"] = min(value,
                                                                                           self.form_1_Slider.maximum())
        
        def downloadChunkSizeChanged(self, value):
            self.form_2_Label.setText(f"下载区块大小：{self.form_2_Slider.value():04}KB")
            settings["LauncherSettings"]["DownloadSettings"]["DownloadChunkSize"] = value
        
        def selectMirrorSource(self):
            value = self.form_3_ComboBox.currentIndex()
            if value <= 0:
                MirrorSourceEnabled(False)
            else:
                MirrorSourceEnabled(True, value - 1)
        
        def changeAnimation(self, variant, function):
            if variant == "in":
                self.changeAnimationIn()
            else:
                self.changeAnimationOut()
                QTimer.singleShot(300, function)
        
        def changeAnimationIn(self):
            ani1 = QPropertyAnimation(self.groupBox, b"pos", self)
            pos1 = self.groupBox.pos()
            ani1.setStartValue(pos1 + QPoint(100, 0))
            ani1.setEndValue(pos1)
            ani1.setDuration(500)
            ani1.setEasingCurve(QEasingCurve.Type.OutQuint)
            ani1.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
            ani11 = OpacityAnimation(self.groupBox)
            ani11.setStartValue(0)
            ani11.setEndValue(100)
            ani11.setDuration(500)
            ani11.setEasingCurve(QEasingCurve.Type.OutQuint)
            ani11.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
            ani2 = QPropertyAnimation(self.groupBox_2, b"pos", self)
            pos2 = self.groupBox_2.pos()
            ani2.setStartValue(pos2 + QPoint(100, 0))
            ani2.setEndValue(pos2)
            ani2.setDuration(500)
            ani2.setEasingCurve(QEasingCurve.Type.OutQuint)
            QTimer.singleShot(100, lambda: ani2.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
            ani22 = OpacityAnimation(self.groupBox_2)
            ani22.setStartValue(0)
            ani22.setEndValue(100)
            ani22.setDuration(500)
            ani22.setEasingCurve(QEasingCurve.Type.OutQuint)
            QTimer.singleShot(100, lambda: ani22.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
        
        def changeAnimationOut(self):
            ani11 = OpacityAnimation(self.groupBox)
            ani11.setStartValue(100)
            ani11.setEndValue(0)
            ani11.setDuration(500)
            ani11.setEasingCurve(QEasingCurve.Type.OutQuint)
            ani11.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
            ani22 = OpacityAnimation(self.groupBox_2)
            ani22.setStartValue(100)
            ani22.setEndValue(0)
            ani22.setDuration(500)
            ani22.setEasingCurve(QEasingCurve.Type.OutQuint)
            QTimer.singleShot(100, lambda: ani22.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
    
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
            
            self.form_2 = QFormLayout()
            self.verticalLayout_2.addLayout(self.form_2)
            
            self.groupBox_2_Label = Label()
            self.form_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.groupBox_2_Label)
            
            self.horizontalLayout = QHBoxLayout()
            
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
            
            self.form_2.setLayout(0, QFormLayout.ItemRole.FieldRole, self.horizontalLayout)
            
            self.groupBox_3 = GroupBox(self.scrollAreaWidgetContents)
            self.verticalLayout.addWidget(self.groupBox_3)
            
            self.groupBox_4 = GroupBox(self.scrollAreaWidgetContents)
            self.verticalLayout.addWidget(self.groupBox_4)
            
            self.form_1 = QFormLayout(self.groupBox_4)
            
            self.form_1_Label = Label(self.groupBox_4)
            self.form_1.setWidget(0, QFormLayout.ItemRole.LabelRole, self.form_1_Label)
            
            self.form_1_ComboBox = ComboBox(self.groupBox_4)
            self.form_1_ComboBox.wheelEvent = lambda: None
            self.form_1_ComboBox.currentIndexChanged.connect(self.setLanguage)
            self.form_1.setWidget(0, QFormLayout.ItemRole.FieldRole, self.form_1_ComboBox)
            
            self.updatingLanguage = True
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
            self.groupBox_4.setTitle(self.tr("SettingsPage.PersonalisationSettings.GroupBox4.Title"))  # 语言
            self.form_1_Label.setText(self.tr("SettingsPage.PersonalisationSettings.Form.1.Label.Text"))  # 界面语言
            self.groupBox_4_Tip.setText(
                self.tr("SettingsPage.PersonalisationSettings.GroupBox4.Tip.Text"))  # 语言翻译未必 100% 准确
        
        @staticmethod
        def setThemePreset(state, value, ani=True):
            if not state:
                return
            settings["LauncherSettings"]["Personalisation"]["CurrentThemePreset"] = value
            if value in themeColourDefines:
                define = themeColourDefines[value]
                for theme in define:
                    for role in define[theme]:
                        for primary in define[theme][role]:
                            for highlight in define[theme][role][primary]:
                                continue
                                setThemeColour(
                                    role,
                                    highlight,
                                    primary,
                                    theme,
                                    Colour(*themeColourDefines[value][theme][role][primary][highlight]),
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
            self.updatingLanguage = True
            self.form_1_ComboBox.clear()
            
            index = 0
            languagesSequence = sorted(languagesCodeMapping)
            for idx, lang in enumerate(languagesSequence):
                if lang == currentLanguage:
                    index = idx
                self.form_1_ComboBox.addItem(f"{languagesCodeMapping[lang]} ({lang})", lang)
            
            self.form_1_ComboBox.setCurrentIndex(index)
            self.form_1_ComboBox.currentIndexChanged.connect(self.setLanguage)
            self.updatingLanguage = False
        
        def setLanguage(self):
            global currentLanguage
            if self.updatingLanguage:
                return
            langCode = self.form_1_ComboBox.currentData()
            currentLanguage = langCode
            settings["LauncherSettings"]["Language"] = currentLanguage
            app.translator.load(f":/CMCL_{currentLanguage}.qm")
            # app.installTranslator(app.translator)
            app.retranslate()
        
        def selectMirrorSource(self):
            value = self.form_3_ComboBox.currentIndex()
            if value <= 0:
                MirrorSourceEnabled(False)
            else:
                MirrorSourceEnabled(True, value - 1)
        
        def changeAnimation(self, variant, function):
            if variant == "in":
                self.changeAnimationIn()
            else:
                self.changeAnimationOut()
                QTimer.singleShot(300, function)
        
        def changeAnimationIn(self):
            ani1 = QPropertyAnimation(self.groupBox, b"pos", self)
            pos1 = self.groupBox.pos()
            ani1.setStartValue(pos1 + QPoint(100, 0))
            ani1.setEndValue(pos1)
            ani1.setDuration(500)
            ani1.setEasingCurve(QEasingCurve.Type.OutQuint)
            ani1.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
            ani11 = OpacityAnimation(self.groupBox)
            ani11.setStartValue(0)
            ani11.setEndValue(100)
            ani11.setDuration(500)
            ani11.setEasingCurve(QEasingCurve.Type.OutQuint)
            ani11.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
            ani2 = QPropertyAnimation(self.groupBox_2, b"pos", self)
            pos2 = self.groupBox_2.pos()
            ani2.setStartValue(pos2 + QPoint(100, 0))
            ani2.setEndValue(pos2)
            ani2.setDuration(500)
            ani2.setEasingCurve(QEasingCurve.Type.OutQuint)
            QTimer.singleShot(100, lambda: ani2.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
            ani22 = OpacityAnimation(self.groupBox_2)
            ani22.setStartValue(0)
            ani22.setEndValue(100)
            ani22.setDuration(500)
            ani22.setEasingCurve(QEasingCurve.Type.OutQuint)
            QTimer.singleShot(100, lambda: ani22.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
            ani3 = QPropertyAnimation(self.groupBox_3, b"pos", self)
            pos3 = self.groupBox_3.pos()
            ani3.setStartValue(pos3 + QPoint(100, 0))
            ani3.setEndValue(pos3)
            ani3.setDuration(500)
            ani3.setEasingCurve(QEasingCurve.Type.OutQuint)
            QTimer.singleShot(200, lambda: ani3.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
            ani33 = OpacityAnimation(self.groupBox_3)
            ani33.setStartValue(0)
            ani33.setEndValue(100)
            ani33.setDuration(500)
            ani33.setEasingCurve(QEasingCurve.Type.OutQuint)
            QTimer.singleShot(200, lambda: ani33.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
            ani4 = QPropertyAnimation(self.groupBox_4, b"pos", self)
            pos4 = self.groupBox_4.pos()
            ani4.setStartValue(pos4 + QPoint(100, 0))
            ani4.setEndValue(pos4)
            ani4.setDuration(500)
            ani4.setEasingCurve(QEasingCurve.Type.OutQuint)
            QTimer.singleShot(300, lambda: ani4.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
            ani4_ = OpacityAnimation(self.groupBox_4)
            ani4_.setStartValue(0)
            ani4_.setEndValue(100)
            ani4_.setDuration(500)
            ani4_.setEasingCurve(QEasingCurve.Type.OutQuint)
            QTimer.singleShot(300, lambda: ani4_.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
        
        def changeAnimationOut(self):
            ani11 = OpacityAnimation(self.groupBox)
            ani11.setStartValue(100)
            ani11.setEndValue(0)
            ani11.setDuration(500)
            ani11.setEasingCurve(QEasingCurve.Type.OutQuint)
            ani11.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
            ani22 = OpacityAnimation(self.groupBox_2)
            ani22.setStartValue(100)
            ani22.setEndValue(0)
            ani22.setDuration(500)
            ani22.setEasingCurve(QEasingCurve.Type.OutQuint)
            QTimer.singleShot(100, lambda: ani22.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
            ani33 = OpacityAnimation(self.groupBox_3)
            ani33.setStartValue(100)
            ani33.setEndValue(0)
            ani33.setDuration(500)
            ani33.setEasingCurve(QEasingCurve.Type.OutQuint)
            QTimer.singleShot(200, lambda: ani33.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
            ani4_ = OpacityAnimation(self.groupBox_4)
            ani4_.setStartValue(100)
            ani4_.setEndValue(0)
            ani4_.setDuration(500)
            ani4_.setEasingCurve(QEasingCurve.Type.OutQuint)
            QTimer.singleShot(300, lambda: ani4_.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.topNavigationPanel = Panel(self)
        self.horizontalLayout = QHBoxLayout(self.topNavigationPanel)
        self.page1 = PushButton(self.topNavigationPanel)
        self.page1.setMinimumHeight(32)
        self.page1.setCheckable(True)
        self.page1.setChecked(True)
        self.page1.setAutoExclusive(True)
        self.page1.setWidgetAttribute("outlinedButton")
        self.page1.released.connect(lambda: self.setCurrentPage(0))
        self.horizontalLayout.addWidget(self.page1)
        self.page2 = PushButton(self.topNavigationPanel)
        self.page2.setMinimumHeight(32)
        self.page2.setCheckable(True)
        self.page2.setAutoExclusive(True)
        self.page2.setWidgetAttribute("outlinedButton")
        self.page2.released.connect(lambda: self.setCurrentPage(1))
        self.horizontalLayout.addWidget(self.page2)
        self.page3 = PushButton(self.topNavigationPanel)
        self.page3.setMinimumHeight(32)
        self.page3.setCheckable(True)
        self.page3.setAutoExclusive(True)
        self.page3.setWidgetAttribute("outlinedButton")
        self.page3.released.connect(lambda: self.setCurrentPage(2))
        self.horizontalLayout.addWidget(self.page3)
        self.horizontalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.horizontalLayout.addItem(self.horizontalSpacer)
        
        self.stackedWidget = AnimatedStackedWidget(self)
        
        self.page1Frame = self.LaunchSettings(self.stackedWidget)
        self.stackedWidget.addWidget(self.page1Frame)
        
        self.page2Frame = self.LauncherSettings(self.stackedWidget)
        self.stackedWidget.addWidget(self.page2Frame)
        
        self.page3Frame = self.PersonalisationSettings(self.stackedWidget)
        self.stackedWidget.addWidget(self.page3Frame)
        
        app.registerRetranslateFunction(self.retranslateUI)
        self.retranslateUI()
    
    def retranslateUI(self):
        self.page1.setText(self.tr("SettingsPage.Page.1.Name"))  # 启动设置
        self.page2.setText(self.tr("SettingsPage.Page.2.Name"))  # 启动器设置
        self.page3.setText(self.tr("SettingsPage.Page.3.Name"))  # 个性化
    
    def setCurrentPage(self, page_id=-1):
        page_seq = (self.page1, self.page2, self.page3)
        page_frame_dict = {
            self.page1: self.page1Frame,
            self.page2: self.page2Frame,
            self.page3: self.page3Frame
        }
        if -1 < page_id < len(page_seq):
            page = page_seq[page_id]
            page_frame = page_frame_dict[page]
            page.setChecked(True)
            self.stackedWidget.setCurrentWidget(page_frame)
    
    def changeAnimation(self, variant, function):
        if variant == "in":
            self.changeAnimationIn()
        else:
            QTimer.singleShot(300, function)
            self.changeAnimationOut()
    
    def changeAnimationIn(self):
        ani1 = QPropertyAnimation(self.topNavigationPanel, b"pos", self)
        pos1 = self.topNavigationPanel.pos()
        ani1.setStartValue(pos1 + QPoint(100, 0))
        ani1.setEndValue(pos1)
        ani1.setDuration(500)
        ani1.setEasingCurve(QEasingCurve.Type.OutQuint)
        ani1.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        ani11 = OpacityAnimation(self.topNavigationPanel)
        ani11.setStartValue(0)
        ani11.setEndValue(100)
        ani11.setDuration(500)
        ani11.setEasingCurve(QEasingCurve.Type.OutQuint)
        ani11.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        QTimer.singleShot(50, lambda: self.topNavigationPanel.show())
        ani22 = OpacityAnimation(self.stackedWidget)
        ani22.setStartValue(0)
        ani22.setEndValue(100)
        ani22.setDuration(500)
        ani22.setEasingCurve(QEasingCurve.Type.OutQuint)
        QTimer.singleShot(100, lambda: ani22.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
        QTimer.singleShot(150, lambda: self.stackedWidget.show())
        
        if self.stackedWidget.currentWidget():
            try:
                self.stackedWidget.currentWidget().changeAnimationIn()
            except AttributeError:
                raise
    
    def changeAnimationOut(self):
        ani11 = OpacityAnimation(self.topNavigationPanel)
        ani11.setStartValue(100)
        ani11.setEndValue(0)
        ani11.setDuration(500)
        ani11.setEasingCurve(QEasingCurve.Type.OutQuint)
        ani11.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        ani22 = OpacityAnimation(self.stackedWidget)
        ani22.setStartValue(100)
        ani22.setEndValue(0)
        ani22.setDuration(500)
        ani22.setEasingCurve(QEasingCurve.Type.OutQuint)
        QTimer.singleShot(100, lambda: ani22.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
        ani11.finished.connect(lambda: self.topNavigationPanel.hide())
        ani22.finished.connect(lambda: self.stackedWidget.hide())
        
        if self.stackedWidget.currentWidget():
            try:
                self.stackedWidget.currentWidget().changeAnimationOut()
            except AttributeError:
                raise
    
    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        
        self.topNavigationPanel.move(QPoint(15, 15))
        self.topNavigationPanel.resize(QSize(self.width() - 30, 54))
        
        self.stackedWidget.move(QPoint(15, 79))
        self.stackedWidget.resize(QSize(self.width() - 30, self.height() - 15 - 79))


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
        
        self.CMCLIconLabel = ImageWidget(
            QImage(":/CommonMinecraftLauncherIcon.svg"),
            self.groupBox_CMCLVersion)
        self.CMCLIconLabel.setFixedSize(QSize(74, 74))
        self.horizontalLayout.addWidget(self.CMCLIconLabel)
        
        self.CMCLVersionLabel = Label(self.groupBox_CMCLVersion)
        self.horizontalLayout.addWidget(self.CMCLVersionLabel, 1)
        
        self.groupBox_authors = GroupBox(self.scrollAreaWidgetContent)
        self.verticalLayout.addWidget(self.groupBox_authors)
        
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_authors)
        
        self.card1 = Panel(self.groupBox_authors)
        self.verticalLayout_2.addWidget(self.card1)
        
        self.horizontalLayout = QHBoxLayout(self.card1)
        
        self.avatar1 = ImageWidget(QImage(":/chengwm_avatar.png"), self.card1)
        self.avatar1.setFixedSize(QSize(42, 42))
        self.avatar1.setBorderRadius(10)
        self.horizontalLayout.addWidget(self.avatar1)
        
        self.intro1 = Label(self.card1)
        self.horizontalLayout.addWidget(self.intro1, 1)
        
        self.card2 = Panel(self.groupBox_authors)
        self.verticalLayout_2.addWidget(self.card2)
        
        self.horizontalLayout_2 = QHBoxLayout(self.card2)
        
        self.avatar2 = ImageWidget(QImage(":/mcdaotian_avatar.png"), self.card2)
        self.avatar2.setFixedSize(QSize(42, 42))
        self.avatar2.setBorderRadius(10)
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
        self.acks_intro1.setWordWrap(True)
        self.horizontalLayout_acks_1.addWidget(self.acks_intro1, 1)
        
        self.acks_card_2 = Panel(self)  # 以防有人不知道 ack 取自 acknowledgement 的前三个字母
        self.verticalLayout_3.addWidget(self.acks_card_2)
        
        self.horizontalLayout_acks_2 = QHBoxLayout(self.acks_card_2)
        
        self.acks_avatar_2 = ToolButton(self.acks_card_2)
        self.acks_avatar_2.setFixedSize(QSize(42, 42))
        self.acks_avatar_2.setIconSize(QSize(32, 32))
        self.horizontalLayout_acks_2.addWidget(self.acks_avatar_2)
        
        self.acks_intro2 = Label(self.acks_card_2)
        self.acks_intro2.setWordWrap(True)
        self.horizontalLayout_acks_2.addWidget(self.acks_intro2, 2)
        
        self.acks_card_3 = Panel(self)  # 以防有人不知道 ack 取自 acknowledgement 的前三个字母
        self.verticalLayout_3.addWidget(self.acks_card_3)
        
        self.horizontalLayout_acks_3 = QHBoxLayout(self.acks_card_3)
        
        self.acks_avatar_3 = ToolButton(self.acks_card_3)
        self.acks_avatar_3.setFixedSize(QSize(42, 42))
        self.acks_avatar_3.setIconSize(QSize(32, 32))
        self.horizontalLayout_acks_3.addWidget(self.acks_avatar_3)
        
        self.acks_intro3 = Label(self.acks_card_3)
        self.acks_intro3.setWordWrap(True)
        self.horizontalLayout_acks_3.addWidget(self.acks_intro3, 2)
        
        self.groupBox_disclaimer = GroupBox(self.scrollAreaWidgetContent)
        disclaimer_font = self.groupBox_disclaimer.font()
        disclaimer_font.setWeight(1000)
        self.groupBox_disclaimer.setFont(disclaimer_font)
        self.verticalLayout.addWidget(self.groupBox_disclaimer)
        
        self.verticalLayout_4 = QVBoxLayout(self.groupBox_disclaimer)
        
        self.disclaimer = Label(self.groupBox_disclaimer)
        self.disclaimer.setFont(disclaimer_font)
        
        self.verticalLayout_4.addWidget(self.disclaimer)
        
        self.groupBox_lawInformation = GroupBox(self)
        self.verticalLayout.addWidget(self.groupBox_lawInformation)
        
        self.verticalLayout_5 = QVBoxLayout(self.groupBox_lawInformation)
        
        self.lawInformation = Label(self.groupBox_lawInformation)
        self.lawInformation.setWordWrap(True)
        self.verticalLayout_5.addWidget(self.lawInformation)
        
        self.verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(self.verticalSpacer)
        
        self.scrollArea.setWidget(self.scrollAreaWidgetContent)
        self.scrollArea.setWidgetResizable(True)
        
        app.registerRetranslateFunction(self.retranslateUI)
        self.retranslateUI()
    
    def retranslateUI(self):
        self.groupBox_CMCLVersion.setTitle("Common Minecraft Launcher")
        # Common Minecraft Launcher\n版本：{} ({})\n语言：{} ({})
        self.CMCLVersionLabel.setText(
            self.tr("AboutPage.CMCLVersionLabel.Text").format(CMCLVersion[0], CMCLVersion[1],
                                                              languagesCodeMapping[currentLanguage], currentLanguage))
        self.groupBox_authors.setTitle("关于开发组")
        self.intro1.setText(
            "<strong>chengwm (chengwm123456)</strong><br>启动器的作者！也是造成启动器彩蛋非常多的罪魁祸首。")
        self.intro2.setText(
            "<strong>mcdaotian / Minecraft_稻田</strong><br>启动器的策划！可谓是为启动器一起提供了许多改进！")
        self.groupBox_thanks.setTitle("致谢")
        
        # 致谢文本翻译 / Acknowledgements text translations
        self.acks_intro1.setText("<strong>Minecraft Wiki</strong><br>启动器编写时资料参考处！（仅作为参考，位于中文 MCW）")
        self.acks_intro2.setText(
            "<strong>龙腾猫跃 (LTCat)</strong><br>据野史（并非）记载，启动器作者在自主编写启动部分时，使用了某不知名启动器生成的命令作为标准命令。")
        self.acks_intro3.setText("<strong>bangbang93</strong><br>提供 BMCLAPI！https://bmclapidoc.bangbang93.com/")
        
        self.groupBox_disclaimer.setTitle("免责声明")
        self.disclaimer.setText(
            "本产品非 Minecraft 官方产品。\n未经 Mojang Studios 或 Microsoft 批准，亦与 Mojang Studios 或 Microsoft 无任何从属关系。\nMinecraft 官方网站请见：https://www.minecraft.net/")
        
        self.groupBox_lawInformation.setTitle("法律信息")
        self.lawInformation.setText("""Copyright (C) 2023-2026 chengwm
本程序是自由软件：你可以根据自由软件基金会发布的 GNU AGPL 的条款，即许可证的第 3 版重新发布它和/或修改它。
本程序的发布是希望它能起到作用。但没有任何保证；甚至没有隐含的保证。本程序的分发是希望它是有用的，但没有任何保证，甚至没有隐含的适销对路或适合某一特定目的的保证。 参见 GNU AGPL 了解更多细节。""")
    
    def changeAnimation(self, variant, function):
        if variant == "in":
            self.changeAnimationIn()
        else:
            QTimer.singleShot(500, function)
            self.changeAnimationOut()
    
    def changeAnimationIn(self):
        pos1 = self.groupBox_CMCLVersion.pos()
        pos2 = self.groupBox_authors.pos()
        pos3 = self.groupBox_thanks.pos()
        pos4 = self.groupBox_disclaimer.pos()
        pos5 = self.groupBox_lawInformation.pos()
        
        self.groupBox_CMCLVersion.hide()
        self.groupBox_authors.hide()
        self.groupBox_thanks.hide()
        self.groupBox_disclaimer.hide()
        self.groupBox_lawInformation.hide()
        
        self.verticalLayout.removeWidget(self.groupBox_CMCLVersion)
        self.verticalLayout.removeWidget(self.groupBox_authors)
        self.verticalLayout.removeWidget(self.groupBox_thanks)
        self.verticalLayout.removeWidget(self.groupBox_disclaimer)
        self.verticalLayout.removeWidget(self.groupBox_lawInformation)
        
        ani1 = QPropertyAnimation(self.groupBox_CMCLVersion, b"pos", self)
        ani1.setStartValue(pos1 + QPoint(100, 0))
        ani1.setEndValue(pos1)
        ani1.setDuration(500)
        ani1.setEasingCurve(QEasingCurve.Type.OutQuint)
        QTimer.singleShot(0, lambda: ani1.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
        ani1.finished.connect(lambda: self.verticalLayout.insertWidget(0, self.groupBox_CMCLVersion))
        ani11 = OpacityAnimation(self.groupBox_CMCLVersion)
        ani11.setStartValue(0)
        ani11.setEndValue(100)
        ani11.setDuration(500)
        ani11.setEasingCurve(QEasingCurve.Type.OutQuint)
        QTimer.singleShot(50, lambda: self.groupBox_CMCLVersion.show())
        QTimer.singleShot(0, lambda: ani11.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
        
        ani2 = QPropertyAnimation(self.groupBox_authors, b"pos", self)
        ani2.setStartValue(pos2 + QPoint(100, 0))
        ani2.setEndValue(pos2)
        ani2.setDuration(500)
        ani2.setEasingCurve(QEasingCurve.Type.OutQuint)
        QTimer.singleShot(100, lambda: ani2.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
        ani2.finished.connect(lambda: self.verticalLayout.insertWidget(1, self.groupBox_authors))
        ani22 = OpacityAnimation(self.groupBox_authors)
        ani22.setStartValue(0)
        ani22.setEndValue(100)
        ani22.setDuration(500)
        ani22.setEasingCurve(QEasingCurve.Type.OutQuint)
        QTimer.singleShot(150, lambda: self.groupBox_authors.show())
        QTimer.singleShot(100, lambda: ani22.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
        
        ani3 = QPropertyAnimation(self.groupBox_thanks, b"pos", self)
        ani3.setStartValue(pos3 + QPoint(100, 0))
        ani3.setEndValue(pos3)
        ani3.setDuration(500)
        ani3.setEasingCurve(QEasingCurve.Type.OutQuint)
        QTimer.singleShot(200, lambda: ani3.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
        ani3.finished.connect(lambda: self.verticalLayout.insertWidget(2, self.groupBox_thanks))
        ani33 = OpacityAnimation(self.groupBox_thanks)
        ani33.setStartValue(0)
        ani33.setEndValue(100)
        ani33.setDuration(500)
        ani33.setEasingCurve(QEasingCurve.Type.OutQuint)
        QTimer.singleShot(250, lambda: self.groupBox_thanks.show())
        QTimer.singleShot(200, lambda: ani33.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
        
        ani4 = QPropertyAnimation(self.groupBox_disclaimer, b"pos", self)
        ani4.setStartValue(pos4 + QPoint(100, 0))
        ani4.setEndValue(pos4)
        ani4.setDuration(500)
        ani4.setEasingCurve(QEasingCurve.Type.OutQuint)
        QTimer.singleShot(300, lambda: ani4.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
        ani4.finished.connect(lambda: self.verticalLayout.insertWidget(3, self.groupBox_disclaimer))
        ani4_ = OpacityAnimation(self.groupBox_disclaimer)
        ani4_.setStartValue(0)
        ani4_.setEndValue(100)
        ani4_.setDuration(500)
        ani4_.setEasingCurve(QEasingCurve.Type.OutQuint)
        QTimer.singleShot(350, lambda: self.groupBox_disclaimer.show())
        QTimer.singleShot(300, lambda: ani4_.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
        
        ani5 = QPropertyAnimation(self.groupBox_lawInformation, b"pos", self)
        ani5.setStartValue(pos5 + QPoint(100, 0))
        ani5.setEndValue(pos5)
        ani5.setDuration(500)
        ani5.setEasingCurve(QEasingCurve.Type.OutQuint)
        QTimer.singleShot(400, lambda: ani5.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
        ani5.finished.connect(lambda: self.verticalLayout.insertWidget(4, self.groupBox_lawInformation))
        ani55 = OpacityAnimation(self.groupBox_lawInformation)
        ani55.setStartValue(0)
        ani55.setEndValue(100)
        ani55.setDuration(500)
        ani55.setEasingCurve(QEasingCurve.Type.OutQuint)
        QTimer.singleShot(450, lambda: self.groupBox_lawInformation.show())
        QTimer.singleShot(400, lambda: ani55.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
    
    def changeAnimationOut(self):
        ani11 = OpacityAnimation(self.groupBox_CMCLVersion)
        ani11.setStartValue(100)
        ani11.setEndValue(0)
        ani11.setDuration(500)
        ani11.setEasingCurve(QEasingCurve.Type.OutQuint)
        QTimer.singleShot(0, lambda: ani11.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
        ani11.finished.connect(lambda: self.groupBox_CMCLVersion.hide())
        
        ani22 = OpacityAnimation(self.groupBox_authors)
        ani22.setStartValue(100)
        ani22.setEndValue(0)
        ani22.setDuration(500)
        ani22.setEasingCurve(QEasingCurve.Type.OutQuint)
        QTimer.singleShot(100, lambda: ani22.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
        ani11.finished.connect(lambda: self.groupBox_authors.hide())
        
        ani33 = OpacityAnimation(self.groupBox_thanks)
        ani33.setStartValue(100)
        ani33.setEndValue(0)
        ani33.setDuration(500)
        ani33.setEasingCurve(QEasingCurve.Type.OutQuint)
        QTimer.singleShot(200, lambda: ani33.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
        ani11.finished.connect(lambda: self.groupBox_thanks.hide())
        
        ani4_ = OpacityAnimation(self.groupBox_disclaimer)
        ani4_.setStartValue(100)
        ani4_.setEndValue(0)
        ani4_.setDuration(500)
        ani4_.setEasingCurve(QEasingCurve.Type.OutQuint)
        QTimer.singleShot(300, lambda: ani4_.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
        ani11.finished.connect(lambda: self.groupBox_disclaimer.hide())
        
        ani55 = OpacityAnimation(self.groupBox_lawInformation)
        ani55.setStartValue(100)
        ani55.setEndValue(0)
        ani55.setDuration(500)
        ani55.setEasingCurve(QEasingCurve.Type.OutQuint)
        QTimer.singleShot(400, lambda: ani55.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
        ani11.finished.connect(lambda: self.groupBox_lawInformation.hide())


class OfflinePlayerCreationDialogue(MaskedDialogue):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(5, 32, 5, 5)
        
        self.playerNameInput = LineEdit(self)
        self.playerNameInput.textChanged.connect(self.updateOKButtonAvailability)
        self.playerNameInput.setValidator(QRegularExpressionValidator(QRegularExpression(r"\w+"), self.playerNameInput))
        self.playerNameInput.setClearButtonEnabled(True)
        self.playerNameInput.returnPressed.connect(self.generatePlayer)
        self.verticalLayout.addWidget(self.playerNameInput)
        
        self.horizontalLayout = QHBoxLayout()
        
        self.OKButton = PushButton(self)
        self.OKButton.setDisabled(True)
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
    
    def updateOKButtonAvailability(self, text):
        self.OKButton.setEnabled(bool(text))
    
    def generatePlayer(self):
        player = create_offline_player(self.playerNameInput.text(), currentPlayer.player_hasMC)
        window.playerPageFrame.appendPlayer(player)
        self.close()


class ChangePlayerNameDialogue(MaskedDialogue):
    def __init__(self, parent, player):
        super().__init__(parent)
        self.currentPlayer = player
        
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(5, 32, 5, 5)
        
        self.playerNameInput = LineEdit(self)
        self.playerNameInput.setValidator(QRegularExpressionValidator(QRegularExpression(r"\w+"), self.playerNameInput))
        self.playerNameInput.setClearButtonEnabled(True)
        self.playerNameInput.editingFinished.connect(self.checkIsValid)
        # self.playerNameInput.returnPressed.connect(self.generatePlayer)
        self.playerNameInput.setPlaceholderText(player.player_playerName)
        self.playerNameInput.setText(player.player_playerName)
        self.verticalLayout.addWidget(self.playerNameInput)
        
        self.horizontalLayout = QHBoxLayout()
        
        self.OKButton = PushButton(self)
        # self.OKButton.pressed.connect(self.generatePlayer)
        self.OKButton.setFocus()
        self.OKButton.setEnabled(False)
        self.horizontalLayout.addWidget(self.OKButton)
        
        self.CancelButton = PushButton(self)
        self.CancelButton.pressed.connect(self.close)
        self.horizontalLayout.addWidget(self.CancelButton)
        
        self.verticalLayout.addLayout(self.horizontalLayout)
        
        self.retranslateUI()
    
    def retranslateUI(self):
        self.setWindowTitle("修改玩家名称")
        self.OKButton.setText("确定")
        self.CancelButton.setText("取消")
    
    def checkIsValid(self):
        playerName = self.playerNameInput.text()
        if playerName == "" or not playerName:
            self.OKButton.setDisabled(True)
            self.OKButton.setToolTip("玩家名不能为空")
            return
        if playerName == self.currentPlayer.player_playerName:
            self.OKButton.setDisabled(True)
            self.OKButton.setToolTip("这是目前的玩家名，请换一个")
            return
        try:
            is_allowed = PlayerNameChange(self.currentPlayer.player_accessToken)["nameChangeAllowed"]
            availability = CheckPlayerNameAvailability(self.currentPlayer.player_accessToken, playerName)
        except requests.exceptions.HTTPError:
            self.OKButton.setDisabled(True)
            self.OKButton.setToolTip("无法访问 Mojang API，请重试")
            return
        if is_allowed and availability == "AVAILABLE":
            self.OKButton.setEnabled(True)
            self.OKButton.setToolTip("该玩家名合法")
        else:
            self.OKButton.setDisabled(True)
            if not is_allowed:
                self.OKButton.setToolTip("当前玩家无法修改玩家名")
            elif availability == "DUPLICATE":
                self.OKButton.setToolTip("该玩家名已被占用")
            elif availability == "NOT_ALLOWED":
                self.OKButton.setToolTip("该玩家名不合法")
            else:
                self.OKButton.setToolTip("未知原因")
    
    def changePlayerName(self):
        self.checkIsValid()
        if self.OKButton.isEnabled():
            playerName = self.playerNameInput.text()
            ChangePlayerName(self.currentPlayer.player_accessToken, playerName)
            self.close()


class PlayerPage(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        
        self.playerList = []
        self.currentIndex = 0
        self.isLoggingIn = False
        self.isLoggedIn = False
        
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
        # self.leftButton.setWidgetAttribute("outlinedButton")
        self.leftButton.pressed.connect(self.selectPlayerLeft)
        self.leftButton.setFixedSize(QSize(32, 32))
        
        self.middleButton = ToolButton(self.topPanel)
        self.middleButton.setMinimumWidth(128)
        
        self.playerActions = ToolButton(self.topPanel)
        self.playerActions.setFixedSize(QSize(32, 32))
        self.playerActions.pressed.connect(self.showPlayerActionsMenu)
        
        self.rightButton = ToolButton(self.topPanel)
        # self.rightButton.setWidgetAttribute("outlinedButton")
        self.rightButton.pressed.connect(self.selectPlayerRight)
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
        self.updateIcon()
        
        self.updatePlayerList()
        self.actionsPanel.raise_()
    
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
        
        self.playerActions.setToolTip("当前玩家操作")
        
        playerTypes = {
            "msa": "Microsoft 账户",
            "authlib-injector": "通过 Authlib-Injector 验证",
            "littleskin": "Littleskin 皮肤站用户",
            "offline": "离线玩家"
        }
        
        if not self.isLoggedIn and not self.isLoggingIn:
            self.middleButton.setText("\n未登录\n")
        elif not self.isLoggingIn and self.playerList:
            currentPlayer = self.playerList[self.currentIndex]
            playerType = playerTypes[currentPlayer.player_accountType[
                1]] if currentPlayer.player_accountType[0] != "offline" else playerTypes["offline"]
            self.middleButton.setText(
                f"{currentPlayer.player_playerName}\n{playerType}\n{'已购买 Minecraft' if currentPlayer.player_hasMC else '未购买 Minecraft'}")
        else:
            self.middleButton.setText("\n正在登录中\n")
        
        self.tableWidget.clear()
        self.tableWidget.setHorizontalHeaderLabels(["玩家名称", "玩家账户类型", "是否拥有 Minecraft"])
        self.tableWidget.setColumnCount(3)
        
        self.tableWidget.setRowCount(len(self.playerList))
        for i, player in enumerate(self.playerList):
            self.tableWidget.setItem(i, 0, QTableWidgetItem(player.player_playerName))
            playerType = (playerTypes[player.player_accountType[1]] if player.player_accountType[0] != "offline" else \
                              playerTypes["offline"])
            self.tableWidget.setItem(i, 1, QTableWidgetItem(playerType))
            self.tableWidget.setItem(i, 2, QTableWidgetItem("已购买" if player.player_hasMC else "未购买"))
    
    def setLoggingIn(self, state):
        self.isLoggingIn = bool(state)
        self.middleButton.setDisabled(self.isLoggingIn or not self.isLoggedIn)
        self.playerActions.setDisabled(self.isLoggingIn or not self.isLoggedIn)
        self.retranslateUI()
    
    def setLoggedIn(self, state):
        self.isLoggedIn = state
        self.setLoggingIn(False)
        self.retranslateUI()
    
    def updatePlayer(self, player):
        if player is None:
            self.setLoggedIn(False)
            return
        self.playerList.append(player)
        self.setLoggingIn(False)
        self.setLoggedIn(True)
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
    
    def selectPlayerLeft(self):
        self.selectPlayer(self.playerList[max(self.currentIndex - 1, 0)])
    
    def selectPlayerRight(self):
        self.selectPlayer(self.playerList[min(self.currentIndex + 1, len(self.playerList) - 1)])
    
    def updatePlayerList(self):
        def parseName(name):
            for player in self.playerList:
                if player.player_playerName == name and player != currentPlayer:
                    self.selectPlayer(player)
                    break
        
        menu = QMenu(self.selectPlayerButton)
        menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        menu.addAction("")
        
        listWidget = ListWidget(menu)
        listWidget.itemDoubleClicked.connect(lambda x: (parseName(x.text()), menu.close()))
        for player in self.playerList:
            item = QListWidgetItem(player.player_playerName, listWidget)
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
    
    def showPlayerActionsMenu(self):
        self.playerActions.setDown(False)
        menu = RoundedMenu(self.playerActions)
        action1 = QAction(menu)
        action1.setText("修改玩家名称")
        action1.triggered.connect(self.changeCurrentPlayerName)
        menu.addAction(action1)
        menu.popup(QCursor.pos())
    
    def changeCurrentPlayerName(self):
        dialogue = ChangePlayerNameDialogue(self.window(), self.playerList[self.currentIndex])
        dialogue.show()
    
    def changeAnimation(self, variant, function):
        if variant == "in":
            self.changeAnimationIn()
        else:
            QTimer.singleShot(300, function)
            self.changeAnimationOut()
    
    def changeAnimationIn(self):
        ani1 = QPropertyAnimation(self.topPanel, b"pos", self)
        pos1 = self.topPanel.pos()
        ani1.setStartValue(pos1 + QPoint(100, 0))
        ani1.setEndValue(pos1)
        ani1.setDuration(500)
        ani1.setEasingCurve(QEasingCurve.Type.OutQuint)
        ani1.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        ani11 = OpacityAnimation(self.topPanel)
        ani11.setStartValue(0)
        ani11.setEndValue(100)
        ani11.setDuration(500)
        ani11.setEasingCurve(QEasingCurve.Type.OutQuint)
        ani11.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        QTimer.singleShot(50, lambda: self.topPanel.show())
        ani2 = QPropertyAnimation(self.tableWidget, b"pos", self)
        pos2 = self.tableWidget.pos()
        ani2.setStartValue(pos2 + QPoint(100, 0))
        ani2.setEndValue(pos2)
        ani2.setDuration(500)
        ani2.setEasingCurve(QEasingCurve.Type.OutQuint)
        QTimer.singleShot(100, lambda: ani2.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
        ani22 = OpacityAnimation(self.tableWidget)
        ani22.setStartValue(0)
        ani22.setEndValue(100)
        ani22.setDuration(500)
        ani22.setEasingCurve(QEasingCurve.Type.OutQuint)
        QTimer.singleShot(100, lambda: ani22.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
        QTimer.singleShot(150, lambda: self.tableWidget.show())
    
    def changeAnimationOut(self):
        ani11 = OpacityAnimation(self.topPanel)
        ani11.setStartValue(100)
        ani11.setEndValue(0)
        ani11.setDuration(500)
        ani11.setEasingCurve(QEasingCurve.Type.OutQuint)
        ani11.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        ani22 = OpacityAnimation(self.tableWidget)
        ani22.setStartValue(100)
        ani22.setEndValue(0)
        ani22.setDuration(500)
        ani22.setEasingCurve(QEasingCurve.Type.OutQuint)
        QTimer.singleShot(100, lambda: ani22.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))
        ani11.finished.connect(lambda: self.topPanel.hide())
        ani22.finished.connect(lambda: self.tableWidget.hide())
    
    def postToggleTheme(self):
        self.updateIcon()
    
    def updateIcon(self):
        colour = "black" if getTheme() == Theme.Light else "white"
        self.leftButton.setIcon(QIcon(f":/LeftArrow-{colour}.svg"))
        self.rightButton.setIcon(QIcon(f":/RightArrow-{colour}.svg"))
        self.playerActions.setIcon(QIcon(f":/MoreActions-{colour}.svg"))
    
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
        self.actionsPanel.resize(QSize(self.width() - 60, 62))
        
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
        
        self.playerActions.adjustSize()
        self.playerActions.move(QPoint(
            self.middleButton.x() + self.middleButton.width() + 10,
            self.topPanel.height() // 2 - 16
        ))


# Dialogue that show you the update log
class UpdateLogDialogue(MaskedDialogue):
    def __init__(self, parent):
        super().__init__(parent)
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(5, 32, 5, 5)
        self.scrollArea = ScrollArea(self)
        self.scrollArea.setStyleSheet("background: transparent; border: none;")
        self.label = Label(self)
        self.label.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse)
        self.scrollArea.setWidget(self.label)
        self.scrollArea.setWidgetResizable(True)
        self.verticalLayout.addWidget(self.scrollArea)
        self.retranslateUI()
    
    def retranslateUI(self):
        self.label.setText(
            f'''<!DOCTYPE html><html><head><style>code {{ font-family: \"Consolas\" }}</style></head><body>{markdown2.markdown("""<h1 align="center">Common Minecraft Launcher</h1>
<h2 align="center">Version AlphaDev-26002</h2>
### 添加
- 更多文本的翻译。

### 修改
- 优化部分文本的翻译；
- 优化启动器缓存存储；
- 修改启动器两个下载页面的布局。

### 修复
- 启动器启动处对于版本隔离的几个问题；
- 启动器“启动设置”中的“内存分配”中，图标的“可用”部分百分比显示的问题；
- 启动器“内存分配”中手动分配的内存未保存的问题；
- （有图形化界面的）Linux 上启动器创建的对话框可以被最大化的问题；
- 可以创建名字为空的离线用户的问题。

### 启动器仓库
[CMCL-Launcher](https://www.github.com/chengwm123456/CMCL-Launcher)

[CMCL-Launcher（针对无法访问 github 提供的镜像）](https://www.bgithub.xyz/chengwm123456/CMCL-Launcher)

启动器使用 AGPL-3.0 许可证开源，详情请参考启动器仓库下的 `LICENSE.md` 文件。

<small>Copyright (C) 2023-2026 [chengwm123456](https://www.github.com/chengwm123456)</small>""", extras=["fenced-code-blocks"])}</body></html>''')


class MainLauncherWindow(MainWindow):
    class ContentPanel(AnimatedStackedWidget, Panel):
        pass
    
    def __init__(self):
        super().__init__()
        self.setBorderAccentColourEnabled(True)
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
        shadow.setColor(QColor(0, 0, 0, 128))
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
        
        self.systemTrayIcon = QSystemTrayIcon(QIcon(":/CommonMinecraftLauncherIcon.svg"), app)
        self.systemTrayIcon.hide()
        self.systemTrayIcon.activated.connect(lambda reason: self.trayIconActivated(reason))
        
        self.topNavCloseTime = time.time()
        
        timer = QTimer(self)
        timer.setInterval(1000)
        timer.timeout.connect(self.updateAfterInterval)
        timer.start()
        
        app.registerRetranslateFunction(self.retranslateUI)
        self.retranslateUI()
    
    def retranslateUI(self):
        self.homePage.setToolTip("主页")
        self.downloadPage.setToolTip("下载")
        self.settingsPage.setToolTip("设置")
        self.aboutPage.setToolTip("关于")
        self.playerPage.setToolTip("玩家管理")
        self.toggleTheme.setToolTip("切换主题")
        self.systemTrayIcon.setToolTip("Common Minecraft Launcher\n单击左键显示窗口，单击右键弹出上下文菜单")
    
    def trayIconActivated(self, reason):
        match reason:
            case QSystemTrayIcon.ActivationReason.Trigger:
                self.show()
            case QSystemTrayIcon.ActivationReason.Context:
                self.showTrayIconMenu()
    
    def showTrayIconMenu(self):
        contextMenu = RoundedMenu(self)
        actionShow = QAction("显示窗口")
        actionShow.triggered.connect(self.show)
        contextMenu.addAction(actionShow)
        contextMenu.addSeparator()
        actionExit = QAction("退出")
        actionExit.triggered.connect(app.quit)
        contextMenu.addAction(actionExit)
        contextMenu.exec(QCursor.pos())
    
    def updateAfterInterval(self):
        if time.time() >= self.topNavCloseTime and not self.topNavigationPanel.underMouse():
            if self.posAnimation:
                self.posAnimation.stop()
                self.posAnimation.deleteLater()
                del self.posAnimation
            self.posAnimation = QPropertyAnimation(self.topNavigationPanel, b"pos", self)
            self.posAnimation.setStartValue(self.topNavigationPanel.pos())
            self.posAnimation.setEndValue(QPoint(30, self.height() + 10))
            self.posAnimation.setDuration(100)
            self.posAnimation.setEasingCurve(QEasingCurve.Type.OutQuad)
            self.posAnimation.start()
    
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
        self.downloadPageFrame.postToggleTheme()
        self.playerPageFrame.postToggleTheme()
    
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
            if isinstance(window, QWidget):
                window.update()
                for child in window.findChildren(QWidget):
                    child.update()
            else:
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
        self.systemTrayIcon.hide()
        super().showEvent(a0)
    
    def leaveEvent(self, a0):
        super().leaveEvent(a0)
        if self.topNavigationPanel.y() >= self.height() + 10:
            return
        
        if self.posAnimation:
            self.posAnimation.stop()
            self.posAnimation.deleteLater()
            del self.posAnimation
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
                self.topNavCloseTime = time.time() + 3
            else:
                y = self.height() + 10
            
            if (not self.posAnimation or self.posAnimation.endValue() != y) and y != self.topNavigationPanel.y():
                if self.posAnimation:
                    self.posAnimation.stop()
                    self.posAnimation.deleteLater()
                    del self.posAnimation
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
        
        if hasattr(self, "posAnimation"):
            if self.mapFromGlobal(QCursor.pos()).y() >= self.height() - 30 or self.topNavigationPanel.underMouse():
                y = self.height() - 30 - 62
                self.topNavCloseTime = time.time() + 3
            else:
                y = self.height() + 10
            self.topNavigationPanel.move(QPoint(30, y))
            self.topNavigationPanel.resize(QSize(self.width() - 60, 62))
        
        if hasattr(self, "centralwidget"):
            self.centralwidget.setGeometry(QRect(35, 35, self.width() - 70, self.height() - 70))
    
    def paintEvent(self, a0):
        self.setWindowBorderAccentColour(getBorderColour(is_highlight=True))
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
    if not data:
        currentPlayer = MicrosoftPlayer(None, None, None, False)
        # login failed
        tip = PopupTip(window)
        label = Label(tip)
        label.setText("登录失败，请手动登录")
        tip.setCentralWidget(label)
        tip.tip(duration=1000, topMargin=32)
    else:
        currentPlayer = data
    window.playerPageFrame.setLoggingIn(False)
    if not data:
        window.playerPageFrame.updatePlayer(None)
    else:
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
    post_except(*args, **kwargs)


def post_except(*args, **kwargs):
    _context_message = traceback._context_message
    traceback._context_message = "\n\033[3mDuring handling of the above exception, another exception occurred:\033[0m\n\n"
    traceback.print_exception(*args, **kwargs, colorize=True)
    traceback._context_message = _context_message


sys.excepthook = excepthook


def saveSettingsMain(settings):
    settingsFile = loadSettingsFile()
    settingsFile["Settings"] = settings
    settingsFile["Version"] = CMCLVersion[0]
    saveSettingsFile(settingsFile)


def init():
    global app, window, currentPlayer, settings, minecraft_path, currentLanguage
    settingsFile = loadSettingsFile()
    settings = settingsFile["Settings"]
    showUpdateLog = settingsFile.get("Version") != CMCLVersion[0]
    
    match settings["LauncherSettings"]["Personalisation"]["CurrentTheme"]:
        case "Light":
            setTheme(Theme.Light)
        case "Dark":
            setTheme(Theme.Dark)
    
    minecraft_path = Path(settings["LauncherSettings"]["MinecraftPath"]).absolute()
    
    currentLanguage = settings["LauncherSettings"].get("Language")
    if currentLanguage is None:
        if os.environ.get("LANG"):
            currentLanguage = os.environ.get("LANG").split(".")[0]
        else:
            currentLanguage = subprocess.run(["powershell.exe", "(Get-WinSystemLocale).Name"],
                                             creationflags=subprocess.CREATE_NO_WINDOW if hasattr(
                                                 subprocess, "CREATE_NO_WINDOW") else 0,
                                             capture_output=True).stdout.decode().strip()
        currentLanguage = currentLanguage.lower().replace("_", "-")
        settings["LauncherSettings"]["Language"] = currentLanguage
    
    # QApplication.setDesktopSettingsAware(False)
    app = Application(sys.argv)
    font = QFont(UIFontList, 10)
    font.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
    font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    app.setFont(font)
    app.fallback_translator = QTranslator()
    app.fallback_translator.load(f":/CMCL_zh-cn.qm")
    app.installTranslator(app.fallback_translator)
    app.qtranslator = QTranslator()
    app.qtranslator.load(f":/qt_{currentLanguage}.qm")
    app.installTranslator(app.qtranslator)
    app.translator = QTranslator()
    app.translator.load(f":/CMCL_{currentLanguage}.qm")
    app.installTranslator(app.translator)
    currentPlayer = create_online_player(None, None, None, False)
    thread = LoginThread()
    thread.loginFinished.connect(updatePlayer)
    thread.start()
    window = MainLauncherWindow()
    window.playerPageFrame.setLoggingIn(True)
    
    if showUpdateLog:
        dialogue = UpdateLogDialogue(window)
        window.updateDialogue = dialogue
    
    app.lastWindowClosed.connect(lambda: saveSettingsMain(settings))


with Path("latest.log").open("w", encoding="utf-8") as out:
    with redirect_stdout(out):
        logging.basicConfig(level=logging.DEBUG, format="[%(levelname)s] \033[3m%(name)s\033[0m: %(message)s")
        cProfile.run("init()", "initAnalysis.log")
        window.show()
        if hasattr(window, "updateDialogue"):
            window.updateDialogue.show()
        outUpd = QTimer(window)
        outUpd.timeout.connect(lambda: (out.flush(), saveSettingsMain(settings)))
        outUpd.setInterval(5000)
        outUpd.start()
        app.exec()

# "%appdata%\Python\Python311\Scripts\pyside6-rcc.exe" resources.qrc -o resources.py

# "%appdata%\Python\Python311\Scripts\pyside6-lupdate.exe" main.py -ts CMCL_zh-cn.ts
# "%appdata%\Python\Python311\Scripts\pyside6-lupdate.exe" main.py -ts CMCL_zh-hk.ts
# "%appdata%\Python\Python311\Scripts\pyside6-lupdate.exe" main.py -ts CMCL_zh-tw.ts
