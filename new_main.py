# -*- coding: utf-8 -*-
"""
project start time:1693310592
|-time.struct_time(tm_year=2023, tm_mon=8, tm_mday=29, tm_hour=20, tm_min=3, tm_sec=12, tm_wday=1, tm_yday=241, tm_isdst=0)
|-2023/08/29 20:03:12, Tuesday, August, Zone:中国标准时间(UTC+8), 一年的第241天
"""
import sqlite3
import base64
import hashlib
import subprocess
import sys
import traceback
import re
import ctypes
import webbrowser as webb
from pathlib import Path
from io import StringIO
import logging
import time

from CWMWidgets import *
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from CWMWidgets.CWMWindows import *
from qframelesswindow import StandardTitleBar

from launch import launch
from login import get_user_data
from player import Player
from getversion import get_version_by_scan_dir

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
        bg = QGraphicsBlurEffect(self)
        bg.setBlurRadius(self.blurRadius)
        self.setGraphicsEffect(bg)
        painter = QPainter(self)
        brush = self.createTexture()
        painter.drawImage(self.img)
        painter.fillRect(self.img.rect(), brush)
    
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


class ContentPanel(Panel):
    def event(self, a0):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        for i in self.children():
            i.setGeometry(self.rect().adjusted(5, 5, -5, -5))
            i.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        return super().event(a0)


class LoadingSvgSplash(QFrame):
    class LoadingTextAnimation(QThread):
        def __init__(self, target):
            super().__init__(target)
            self.dotnum = 0
            self.text = target.text()
            self.__next = True
        
        def setTargetText(self, text):
            self.text = text
        
        def run(self):
            import time
            self.dotnum = 0
            while True:
                self.parent().setText(self.text + ("." * (self.dotnum % 4)))
                self.dotnum += 1
                time.sleep(1)
        
        def __del__(self):
            try:
                self.terminate()
            except RuntimeError:
                pass
    
    class HideAnimation(QThread):
        def run(self):
            import time
            time.sleep(1)
            self.parent().hide()
        
        def __del__(self):
            try:
                self.terminate()
            except RuntimeError:
                pass
    
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
                f"background: rgba(249, 249, 249, {colour / 255})")
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setStyleSheet("background: rgb(249, 249, 249);")
        self.svgWidget = QSvgWidget(self)
        self.svgWidget.load("CMCL_loading.svg")
        self.svgWidget.setFixedSize(96, 96)
        self.svgWidget.setStyleSheet("background: transparent;")
        dsg = QGraphicsDropShadowEffect(self.svgWidget)
        dsg.setBlurRadius(30)
        dsg.setOffset(0, 4)
        dsg.setColor(QColor(0, 0, 0, 100))
        self.svgWidget.setGraphicsEffect(dsg)
        self.failedSvg = QSvgWidget(self.svgWidget)
        self.failedSvg.load("CMCL_loading_failed.svg")
        self.failedSvg.setFixedSize(96, 96)
        self.failedSvg.setStyleSheet("background: transparent;")
        self.failedSvg.hide()
        self.statusLabel = Label(self)
        self.statusLabel.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.loadingThread = self.LoadingTextAnimation(self.statusLabel)
        self.hide()
    
    def event(self, e):
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setGeometry(self.parent().rect())
        if hasattr(self, "svgWidget"):
            self.svgWidget.setGeometry(QRect(int(self.width() / 2 - (self.svgWidget.width() / 2)),
                                             int(self.height() / 2 - (self.svgWidget.height() / 2)),
                                             self.svgWidget.width(),
                                             self.svgWidget.height()))
            if hasattr(self, "failedSvg"):
                self.failedSvg.setGeometry(self.svgWidget.rect())
        if hasattr(self, "statusLabel"):
            self.statusLabel.adjustSize()
            self.statusLabel.setGeometry(QRect(int(self.width() / 2 - (self.statusLabel.width() / 2)),
                                               int(self.height() / 2 - (self.statusLabel.height() / 2)) + 96 + 30,
                                               self.statusLabel.width(),
                                               self.statusLabel.height()))
        self.raise_()
        return super().event(e)
    
    def paintEvent(self, a0):
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        return super().paintEvent(a0)
    
    def start(self, ani=True):
        self.setStyleSheet("background: rgb(249, 249, 249);")
        self.statusLabel.setText("加载中")
        self.loadingThread.setTargetText(self.statusLabel.text())
        self.svgWidget.load("CMCL_loading.svg")
        self.failedSvg.load("CMCL_loading_failed.svg")
        self.failedSvg.hide()
        if ani:
            self.setStyleSheet("background: transparent")
            self.TransparencyAnimation(self, "in").start()
        self.loadingThread.start()
        self.show()
        self.loadingThread.exec()
    
    def finish(self, ani=True, failed=False):
        self.loadingThread.terminate()
        if not failed:
            if ani:
                self.TransparencyAnimation(self, "out").start()
                _ = self.HideAnimation(self)
                _.start()
            else:
                self.hide()
            self.statusLabel.setText("已加载完成")
            self.failedSvg.hide()
            if ani:
                _.exec()
        else:
            self.setStyleSheet("background: rgb(255, 200, 200);")
            self.statusLabel.setText("加载失败，请重试")
            self.failedSvg.show()


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
                    player.player_uuid = datas[1]
                    player.player_name = datas[0]
                    player.player_accessToken = datas[2]
                    player.player_hasMC = datas[3]
            except:
                traceback.print_exc()
            self.loginFinished.emit()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: white")
        self.setWindowTitle("登录")
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(11, 43, 11, 11)
        self.content = Label(self)
        self.content.setText("""<html><head/><body style="margin: 0px"><p style="margin: 0px">
                登录步骤：</p>
                <p style="margin: 0px">1，启动器将打开一个网页，请在网页里登录您的账号。</p>
                <p style="margin: 0px">如果没有自动打开或者被关了，请点击下方的“重新打开网页”，或者手动打开：</p><br/>
                   <a href="https://login.live.com/oauth20_authorize.srf?client_id=00000000402b5328&response_type=code&scope=service%3A%3Auser.auth.xboxlive.com%3A%3AMBI_SSL&redirect_uri=https%3A%2F%2Flogin.live.com%2Foauth20_desktop.srf">
        https://login.live.com/oauth20_authorize.srf?<br/>
        client_id=00000000402b5328<br/>
        &response_type=code<br/>
        &scope=service%3A%3Auser.auth.xboxlive.com%3A%3AMBI_SSL<br/>
        &redirect_uri=https%3A%2F%2Flogin.live.com%2Foauth20_desktop.srf<br/>
                   </a>
                <p style="margin: 0px">2，如果用户名和密码正确，您应该会被重定向至一个网站，网址会类似这样：</p>
                <p style="margin: 0px">https://login.live.com/oauth20_desktop.srf?code={code}&lc=XXXX</p>
                <p style="margin: 0px">您需要将{code}部分的代码提取出来，填在下方的输入框</p>
                <p style="margin: 0px">（应该没有人会在下面乱输吧。。。。。。）<small><del style="text-decoration: line-through">（事实是：作者此时就在乱按）</del></small></p>
                <p style="margin: 0px">3，按下 继续 按钮，然后就静静的等等等等等等等等等等等等等等吧。<p>
                <br/>
                <p>可以尝试一下新版登录。只要点一下下方的 体验新登录 按钮，就可以尝试新登录了。<br/>
                Bug 和 建议 可以通过CMCL启动器的官方网站反馈。</p>
                </body></html>""")
        self.content.setWordWrap(True)
        self.content.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.TextSelectableByKeyboard)
        self.verticalLayout.addWidget(self.content)
        self.horizontalLayout = QHBoxLayout(self)
        self.lineEdit = LineEdit(self)
        self.lineEdit.setInputMask("X.XXXX_XXX.X.X.XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX;X")
        self.horizontalLayout.addWidget(self.lineEdit)
        self.toolButton = ToolButton(self)
        self.toolButton.setText("继续")
        self.toolButton.pressed.connect(self.process_login)
        self.horizontalLayout.addWidget(self.toolButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.pushButton = PushButton(self)
        self.pushButton.setText("重新打开网页")
        self.pushButton.pressed.connect(lambda: webb.open(
            "https://login.live.com/oauth20_authorize.srf?client_id=00000000402b5328&response_type=code&scope=service%3A%3Auser.auth.xboxlive.com%3A%3AMBI_SSL&redirect_uri=https%3A%2F%2Flogin.live.com%2Foauth20_desktop.srf"))
        self.verticalLayout.addWidget(self.pushButton)
        self.trybtn = PushButton(self)
        self.trybtn.setText("体验新登录")
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
        thread.exec()
        self.hide()
    
    def open_new_login(self):
        self.hide()
        w = LoginWindow()
        w.exec()
    
    def paintEvent(self, *args, **kwargs):
        painter = QPainter(self)
        painter.fillRect(
            QRect(-self.geometry().x(), -self.geometry().y(), QGuiApplication.primaryScreen().geometry().width(),
                  QGuiApplication.primaryScreen().geometry().height()), QGradient(QGradient.Preset.PerfectWhite))


class LoginWindow(RoundedDialogue):
    class LoginThread(QThread):
        loginFinished = pyqtSignal()
        
        def __init__(self, token, parent=None):
            super().__init__(parent)
            self.token = token
        
        def run(self):
            try:
                datas = login_user(bytes(self.token, encoding="utf-8"))
                if datas is not None:
                    player.player_uuid = datas[1]
                    player.player_name = datas[0]
                    player.player_accessToken = datas[2]
                    player.player_hasMC = datas[3]
            except:
                traceback.print_exc()
            self.loginFinished.emit()
    
    class QWebEngineView(QWebEngineView):
        def contextMenuEvent(self, a0):
            menu = RoundedMenu(self)
            reload = QAction(menu)
            reload.setText("重新加载")
            reload.triggered.connect(self.reload)
            menu.addAction(reload)
            menu.popup(self.mapToGlobal(a0.pos()))
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("登录")
        self.resize(800, 600)
        self.view = self.QWebEngineView(self)
        self.view.show()
        self.view.load(QUrl(
            "https://login.live.com/oauth20_authorize.srf?client_id=00000000402b5328&response_type=code&scope=service%3A%3Auser.auth.xboxlive.com%3A%3AMBI_SSL&redirect_uri=https%3A%2F%2Flogin.live.com%2Foauth20_desktop.srf"))
        self.view.urlChanged.connect(self.assert_url)
        self.view.loadStarted.connect(self.loadStarted)
        self.view.loadFinished.connect(self.loadFinished)
        self.view.page().profile().setHttpAcceptLanguage(language)
        self.progress = LoadingSvgSplash(self)
        self.progress.hide()
        self.titleBar.raise_()
        self.update()
        self.setResizeEnabled(True)
    
    def assert_url(self):
        result = re.match(r"https://login\.live\.com/oauth20_desktop\.srf\?code=.+&lc=.+", self.view.url().toString())
        if result:
            print(self.view.url().toString())
            pos = re.search(r"code=.+", self.view.url().toString())
            if pos:
                code = pos.string
                token = code.split("=")[1]
                token = token.split(".")[-1].split("&")[0]
                print(token)
                thread = self.LoginThread(token)
                thread.start()
                self.hide()
    
    def loadStarted(self):
        self.progress.start()
    
    def loadFinished(self):
        self.progress.finish()
    
    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        self.view.setGeometry(self.rect())
    
    def paintEvent(self, *args, **kwargs):
        painter = QPainter(self)
        painter.fillRect(
            QRect(-self.geometry().x(), -self.geometry().y(), QGuiApplication.primaryScreen().geometry().width(),
                  QGuiApplication.primaryScreen().geometry().height()), QGradient(QGradient.Preset.PerfectWhite))


class MultiPageBase(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame = Panel(self)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.pushButton = PushButton(self.frame)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setCheckable(True)
        self.pushButton.setChecked(True)
        self.pushButton.setAutoExclusive(True)
        
        self.horizontalLayout.addWidget(self.pushButton)
        
        self.pushButton_2 = PushButton(self.frame)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setCheckable(True)
        self.pushButton_2.setAutoExclusive(True)
        
        self.horizontalLayout.addWidget(self.pushButton_2)
        
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        self.horizontalLayout.addItem(self.horizontalSpacer)
        
        self.verticalLayout.addWidget(self.frame)
        
        self.stackedWidget = QStackedWidget(self)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.stackedWidget.addWidget(self.page_2)
        
        self.verticalLayout.addWidget(self.stackedWidget)
        
        self.retranslateUi(self)
        #
        # QMetaObject.connectSlotsByName(Form)
    
    # setupUi
    
    def retranslateUi(self, Form):
        self.pushButton.setText("Page2")
        self.pushButton_2.setText("Page2")
    # retranslateUi


class MainPage(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.version = None
        
        self.verticalLayout = QVBoxLayout(self)
        self.scrollArea = QScrollArea(self)
        self.verticalLayout.addWidget(self.scrollArea)
        self.scrollAreaContentWidget = QWidget()
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaContentWidget)
        self.label2 = Label(self.scrollAreaContentWidget)
        self.label2.setText((f"""<!DOCTYPE html>
                        <html>
                            <head/>
                            <body>
                                <p>
                                {'''<a href="https://www.bilibili.com/v/topic/detail/?topic_id=53624&topic_name=2233%E7%94%9F%E6%97%A5%E5%BF%AB%E4%B9%90&spm_id_from=333.999.list.card_topic.click" style="text-decoration: none">#2233生日快乐#</a><br/>
                                (都说了全网带话题 <a href="https://www.bilibili.com/v/topic/detail/?topic_id=53624&topic_name=2233%E7%94%9F%E6%97%A5%E5%BF%AB%E4%B9%90&spm_id_from=333.999.list.card_topic.click" style="text-decoration: none">#2233生日快乐#</a>。这不，<small style="font-size: xx-small"><del style='text-decoration: line-through'>{}</del></small>的我也带了这个话题了。都别针对我呀，<small style="font-size: xx-small"><del style='text-decoration: line-through'>我是无辜的</del></small>。)'''.format("远在地球另一边无法赶回来") if time.localtime().tm_mon == 8 and time.localtime().tm_mday == 16 else f"敬请等待{time.localtime().tm_year + 1}年8月16号"}
                                <hr/>
                                你知道 22 和 33 吗？<br/>
                                <small style="font-size: xx-small"><del style='text-decoration: line-through'>我知道你不知道她们</del></small>(并不) <br/>
                                22 和 33: ？？？ 你在说啥？ 你号没了！ <br/>
                                <a href='https://space.bilibili.com/68559'>她们的官方账号</a><br/>
                                然后呢？<br/><span style="font-weight: bold">她们的生日在 8 月 16 号！！！(请牢牢记住，或者提防你的账号，因为忘掉她们生日容易被封)</span><br/>由此可得知她们都是狮子座。<br/>
                                再然后呢？？？ <br/>
                                让我们先说 22 吧 <br/>
                                <h4>22 的设定</h4>
                                身高：160cm <br/>
                                体重：48KG<br/>
                                <small style="font-size: xx-small"><del style='text-decoration: line-through'>绰号：F22<br/>想知道更多可以去<a href="https://www.bilibili.com/video/BV1wJ411J7JK/">https://www.bilibili.com/video/BV1wJ411J7JK/</a>一探究竟。</del></small><br/>
                                声优：{{ <br/>
                                    柴刀娘木木（2015）<br/>
                                    幽舞越山（2016--）<br/>
                                    <small style="font-size: xx-small"><del style='text-decoration: line-through'>AI（2024年唱歌）</del></small><br/>
                                }}<br/>
                                <br/><br/>
                                再来说 33 吧 <br/>
                                <h4>33 的设定</h4>
                                身高：148cm <br/>
                                体重：？？？（怕 33 咬我，可以告诉你们 2 开头）<br/>
                                声优：{{<br/>
                                    柴刀娘木木（2015）<br/>
                                    少愿愿（2016-2018）<br/>
                                    李姗姗（2019--）<br/>
                                    Hanser（部分歌曲？）<br/>
                                    <small style="font-size: xx-small"><del style='text-decoration: line-through'>AI（2024年唱歌）</del></small><br/>
                                }}<br/>
                                <br/><br/>
                                然后。。。。。。<br/>
                                更多信息请前往<a href="https://mzh.moegirl.org.cn/Bilibili%E5%A8%98">此处</a>了解。<br/>
                                <small style="font-size: xx-small"><del style='text-decoration: line-through'>热知识：在2017年，2233 以 98 亿（9876547210.33元）被卖身。（雾）</del></small><br/>
                                <small style="font-size: xx-small"><del style='text-decoration: line-through'>震惊，Bilibili的98亿竟被两个员工花完。（2021年拜年纪）</del></small>
                              </p>
                              <p>
                                以上为测试文本，为启动器测试文本显示、HTML样式测试、模板填空测试以及排版测试文本。著作权归原编辑者所有。<br/>
                              </p>
                              <p>此文本部分内容引自萌娘百科(mzh.moegirl.org.cn)，具体链接：<a href="https://mzh.moegirl.org.cn/Bilibili%E5%A8%98">*</a>，内容不可商用</p>
                            </body>
                        </html>""" if time.localtime().tm_year != 2017 or time.localtime().tm_mon != 1 or time.localtime().tm_mday != 23 else "没有 98 亿还想知道 2233？") if time.localtime().tm_year > 2010 or (
                time.localtime().tm_year == 2010 and time.localtime().tm_mon > 8 or (
                time.localtime().tm_mon == 8 and time.localtime().tm_mday >= 16)) else "此条目不存在")
        self.label2.show()
        self.label2.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByKeyboard | Qt.TextInteractionFlag.TextSelectableByMouse)  # | Qt.TextInteractionFlag.TextEditable)
        self.label2.setWordWrap(True)
        self.verticalLayout_2.addWidget(self.label2)
        # spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        # self.verticalLayout_2.addItem(spacer)
        self.bottom_space = QSpacerItem(0, 80, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.verticalLayout_2.addItem(self.bottom_space)
        self.scrollArea.setWidget(self.scrollAreaContentWidget)
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
        menu = RoundedMenu()
        versions = get_version_by_scan_dir(minecraft_path=minecraft_path)
        if isinstance(versions, list):
            for version in versions:
                action = QAction(menu)
                action.setText(version)
                action.triggered.connect(lambda _, v=version: self.select_version(v))
                menu.addAction(action)
        self.select_version_btn.setMenu(menu)
        self.horizontalLayout.addWidget(self.select_version_btn)
        spacer2 = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.horizontalLayout.addItem(spacer2)
        self.retranslateUI()
        self.bottomPanelIsShow = True
    
    def retranslateUI(self):
        self.launch_btn.setText("启动")
        self.select_version_btn.setText(self.version or "选择版本")
    
    def select_version(self, version):
        self.version = version
        self.select_version_btn.setText(self.version or "选择版本")
    
    def launch(self):
        result = launch(minecraft_path, self.version, None,
                        "server",
                        CMCL_version[0], None, None, None, "", None, None,
                        player)
        print(result)
    
    def resizeEvent(self, *args, **kwargs):
        super().resizeEvent(*args, **kwargs)
        self.bottomPanel.setGeometry(
            QRect(5, (self.height() - 80 if self.bottomPanelIsShow else self.height() + 62), self.width() - 10, 62))
        if self.bottomPanelIsShow and not self.bottom_space in self.verticalLayout_2.children():
            self.verticalLayout_2.addItem(self.bottom_space)
        else:
            if self.bottom_space in self.verticalLayout_2.children():
                self.verticalLayout_2.removeItem(self.bottom_space)
        self.label2.adjustSize()


class MainWindow(RoundedWindow):
    def __init__(self):
        super().__init__()
        self.resize(800, 600)
        self.setWindowIcon(QIcon("CMCL_icon.svg"))
        self.setWindowTitle("Common Minecraft Launcher")
        # self.setWindowOpacity(0.5)
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
        self.topWidget = FoldableNavigationPanel(self.centralwidget)
        self.HomePage = MainPage(self)
        self.topWidget.addItem(self.HomePage, "Home.svg")
        self.DownloadPage = QFrame()
        self.topWidget.addItem(self.DownloadPage, "Download.svg")
        self.topWidget.addButton("user_icon-black.svg", selectable=False, pressed=self.start_login)
        self.topWidget.addButton("auto_black.svg", selectable=False)
        self.horizontalLayout.addWidget(self.topWidget)
        self.content = ContentPanel(self.centralwidget)
        self.horizontalLayout.addWidget(self.content, 1)
        self.topWidget.setContentWidget(self.content)
        # tip = Tip(self)
        # self.horizontalLayout.addWidget(tip)
        # popoutTip = PopoutTip(self)
        # popoutTip.tip()
        self.centralwidget.setLayout(self.horizontalLayout)
        self.setCentralWidget(self.centralwidget)
    
    def showCentre(self):
        geometry = QGuiApplication.primaryScreen().geometry()
        point = QPoint(geometry.width() // 2 - self.width() // 2, geometry.height() // 2 - self.height() // 2)
        self.move(point)
        self.show()
    
    def start_login(self):
        dialogue = LoginDialogue()
        dialogue.exec()
    
    def paintEvent(self, *args, **kwargs):
        painter = QPainter(self)
        painter.fillRect(
            QRect(-self.geometry().x(), -self.geometry().y(), QGuiApplication.primaryScreen().geometry().width(),
                  QGuiApplication.primaryScreen().geometry().height()), QGradient(QGradient.Preset.PerfectWhite))


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
                
                self.highlight_styles["state"] = state
                self.highlight_styles["string"] = string
                
                stringprefix = r"(?i:r|u|f|fr|rf|b|br|rb)?"
                sqstring = stringprefix + r"'[^'\\\n]*(\\.[^'\\\n]*)*'?"
                dqstring = stringprefix + r'"[^"\\\n]*(\\.[^"\\\n]*)*"?'
                sq3string = stringprefix + r"'''[^'\\]*((\\.|'(?!''))[^'\\]*)*(''')?"
                dq3string = stringprefix + r'"""[^"\\]*((\\.|"(?!""))[^"\\]*)*(""")?'
                string = "|".join([sqstring, dqstring, sq3string, dq3string])
                
                self.rules.extend([
                    (r"\[.+\]:", 0, self.highlight_styles["state"]),
                    (string, 0, self.highlight_styles["string"])
                ])
        
        Default_Highlighter = Highlighter
    
    class Executer:
        def __init__(self):
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
            
            self.globals = {"__import__": __import__, "exec": exec, "input": input, "sys": sys, "__builtins__": {},
                            "player": player,
                            "frame": frame}
            self.locals = {"__import__": __import__, "exec": exec, "input": input, "sys": sys, "__builtins__": {}}
        
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
        self.setWindowTitle("日志窗口")
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
        self.canOutput = True
        self.retranslateUI()
        self.cmd = self.Executer()
        self.history_command = []
        self.current_history = 0
    
    def retranslateUI(self):
        self.stopOutputBtn.setText("停止输出" if self.canOutput else "开始输出")
    
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
        self.stopOutputBtn.setText("停止输出" if self.canOutput else "开始输出")
    
    def process_command(self):
        if self.inputtext.text():
            self.history_command.append(self.inputtext.text())
            self.cmd.process_command(self.inputtext.text())
            self.inputtext.clear()
            self.current_history = 0
    
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
    
    def paintEvent(self, *args, **kwargs):
        painter = QPainter(self)
        painter.fillRect(
            QRect(-self.geometry().x(), -self.geometry().y(), QGuiApplication.primaryScreen().geometry().width(),
                  QGuiApplication.primaryScreen().geometry().height()), QGradient(QGradient.Preset.PerfectWhite))


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
        status, name, uuid, access_token, refresh_token, has_mc = get_user_data(token, is_refresh_login)
        if refresh_token:
            if not is_refresh_login:
                cursor.execute(
                    f'insert into users (refresh_token, player_name) values ("{base64.b64encode(bytes(refresh_token, encoding="utf-8")).decode()}", "{hashlib.sha512(bytes(name, encoding="utf-8")).hexdigest()}")')
            else:
                cursor.execute(
                    f'update users set refresh_token = "{base64.b64encode(bytes(refresh_token, encoding="utf-8")).decode()}" where player_name = "{hashlib.sha512(bytes(name, encoding="utf-8")).hexdigest()}"')
        cursor.close()
        conn.commit()
        conn.close()
        with open("current_user.DAT", "wb") as file:
            file.write(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" + r"\x0".join(list(hashlib.sha512(
                name.encode(
                    "utf-8")).hexdigest())).encode() + b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
        
        return name, uuid, access_token, has_mc
    except:
        return None, None, None, False


class LoginThread(QThread):
    loginFinished = pyqtSignal(tuple)
    
    def run(self):
        try:
            data = Path("current_user.DAT").read_bytes().replace(
                b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00", b"").replace(br"\x0", b"")
            datas = login_user(data, True)
        except FileNotFoundError:
            Path("current_user.DAT").write_text("", encoding="utf-8")
        finally:
            try:
                self.loginFinished.emit(datas)
            except NameError:
                self.loginFinished.emit((None, None, None, False))


def update_user(datas):
    global player
    if datas:
        player.player_name = datas[0]
        player.player_uuid = datas[1]
        player.player_accessToken = datas[2]
        player.player_hasMC = datas[3]


Path("error.log").write_text("", encoding="utf-8")
Path("latest.log").write_text("", encoding="utf-8")


def __excepthook__(*args, **kwargs):
    traceback.print_exception(*args, **kwargs)
    if DEBUG:
        Path("error.log").open("a", encoding="utf-8").write("".join(traceback.format_exception(*args, **kwargs)))


sys.excepthook = __excepthook__

if not ctypes.windll.shell32.IsUserAnAdmin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    sys.exit(0)
logging.basicConfig(
    level=logging.NOTSET,
    format="[%(asctime)s][%(levelname)s]:%(message)s",
    datefmt="%Y/%m/%d][%H:%M:%S %p"
)
app = QApplication(sys.argv)
app.setFont(QFont("Minecraft AE"))
player = Player.create_online_player(None, None, None, False)
frame = MainWindow()
frame.showCentre()
if DEBUG:
    debug = LoggingWindow()
    debug.show()
# w = LoginWindow()
# w.show()
# print("[2024/08/16][22:33:00 PM][INFO]:F22战斗姬！22是F！33也可以是F！\n"
#       "[2024/08/16][22:33:00 PM][INFO]:在刚毅云音乐上，22娘这个账号有九首歌，\n"
#       "[2024/08/16][22:33:00 PM][INFO]:33娘这个账号则有11首歌。\n"
#       "[2024/08/16][22:33:00 PM][INFO]:她们还有个叫 22和33 的账号。\n"
#       "[2024/08/16][22:33:00 PM][INFO]:让我们祝她们生日快乐！\n"
#       "[2023/08/29][20:03:12 PM][INFO]:启动器的第一个文件创建！\n"
#       "[2009/??/??][??:??:?? ??][INFO]:某个叫 Mikufans 的网站创建！（Mikufans 就是今天的 Bilibili！）\n"
#       "[2008/??/??][??:??:?? ??][INFO]:Minecraft 前身 RubyDung 被 Markus Persson 创建！\n"
#       "[2009/05/10][17:36:00 PM][INFO]:Minecraft 最早版本 rd-131655 的视频被上传！\n"
#       "[2011/11/17][22:00:00 PM][INFO]:Minecraft 1.0.0 发布！")
thread = LoginThread()
thread.loginFinished.connect(update_user)
thread.start()
app.exec()
