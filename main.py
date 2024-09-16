# -*- coding: utf-8 -*-
"""
project start time:1693310592
|-time.struct_time(tm_year=2023, tm_mon=8, tm_mday=29, tm_hour=20, tm_min=3, tm_sec=12, tm_wday=1, tm_yday=241, tm_isdst=0)
|-2023/08/29 20:03:12, Tuesday, August, Zone:中国标准时间(UTC+8), 一年的第241天
"""
import sqlite3
import base64
import hashlib
import datetime
import pytz
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

from CMCLCore.Launch import LaunchMinecraft
from CMCLCore.Login import get_user_data
from CMCLCore.Player import create_online_player, create_offline_player
from CMCLCore.GetVersion import GetVersionByScanDirectory, GetVersionByMojangApi

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
        
        def __del__(self):
            self.wait()
    
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
                f"background: rgba({str(getBackgroundColour(tuple=True)).replace('(', '').replace(')', '')}, {colour / 255})")
    
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
        return super().paintEvent(a0)
    
    def __updateText(self):
        self.__counter += 1
        self.__statusLabel.setText("加载中" + "." * (self.__counter % 4))
    
    def start(self, ani=True):
        self.setStyleSheet(
            f"background: rgb({str(getBackgroundColour(tuple=True)).replace('(', '').replace(')', '')});")
        self.__statusLabel.setText("加载中")
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
            self.__statusLabel.setText("已加载完成")
            self.__failedSvg.hide()
        else:
            self.setStyleSheet("background: rgb(255, 200, 200);")
            self.__statusLabel.setText("加载失败，请重试")
            self.__failedSvg.show()
    
    def hideEvent(self, *args, **kwargs):
        try:
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
        self.hide()
    
    def open_new_login(self):
        self.hide()
        w = LoginWindow()
        w.exec()
    
    def paintEvent(self, a0, **kwargs):
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
        self.progress = LoadingAnimation(self)
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
        self.progress.start(ani=bool(self.view.url().toString()))
    
    def loadFinished(self):
        self.progress.finish()
    
    def resizeEvent(self, a0, **kwargs):
        super().resizeEvent(a0)
        self.view.setGeometry(self.rect())
    
    def paintEvent(self, a0, **kwargs):
        painter = QPainter(self)
        painter.fillRect(
            QRect(-self.geometry().x(), -self.geometry().y(), QGuiApplication.primaryScreen().geometry().width(),
                  QGuiApplication.primaryScreen().geometry().height()), QGradient(QGradient.Preset.PerfectWhite))


# class MultiPageBase(QFrame):
#     def __init__(self, parent):
#         super().__init__(parent)
#         self.verticalLayout = QVBoxLayout(self)
#         self.verticalLayout.setObjectName(u"verticalLayout")
#         self.frame = Panel(self)
#         self.horizontalLayout = QHBoxLayout(self.frame)
#         self.horizontalLayout.setObjectName(u"horizontalLayout")
#         self.pushButton = PushButton(self.frame)
#         self.pushButton.setObjectName(u"pushButton")
#         self.pushButton.setCheckable(True)
#         self.pushButton.setChecked(True)
#         self.pushButton.setAutoExclusive(True)
#
#         self.horizontalLayout.addWidget(self.pushButton)
#
#         self.pushButton_2 = PushButton(self.frame)
#         self.pushButton_2.setObjectName(u"pushButton_2")
#         self.pushButton_2.setCheckable(True)
#         self.pushButton_2.setAutoExclusive(True)
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
#         self.page_2 = QWidget()
#         self.page_2.setObjectName(u"page_2")
#         self.stackedWidget.addWidget(self.page_2)
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
#         self.pushButton.setText("Page2")
#         self.pushButton_2.setText("Page2")
#     # retranslateUi


class MainPage(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.version = None
        
        self.verticalLayout = QVBoxLayout(self)
        self.scrollArea = ScrollArea(self)
        self.verticalLayout.addWidget(self.scrollArea)
        self.scrollAreaContentWidget = QWidget()
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaContentWidget)
        tip = Tip(self, False)
        self.tlabel = Label(tip)
        self.tlabel.setText('''<a href="https://www.bilibili.com/v/topic/detail/?topic_id=53624&topic_name=2233%E7%94%9F%E6%97%A5%E5%BF%AB%E4%B9%90&spm_id_from=333.999.list.card_topic.click" style="text-decoration: none">#2233生日快乐#</a><br/>
                                (都说了全网带话题 <a href="https://www.bilibili.com/v/topic/detail/?topic_id=53624&topic_name=2233%E7%94%9F%E6%97%A5%E5%BF%AB%E4%B9%90&spm_id_from=333.999.list.card_topic.click" style="text-decoration: none">#2233生日快乐#</a>。这不，<small style="font-size: xx-small"><del style='text-decoration: line-through'>{}</del></small>的我也带了这个话题了。都别针对我呀，<small style="font-size: xx-small"><del style='text-decoration: line-through'>我是无辜的</del></small>。)'''.format(
            "远在地球另一边无法赶回来") if time.localtime().tm_mon == 8 and time.localtime().tm_mday == 16 else f"敬请等待{time.localtime().tm_year + 1}年8月16号<br/>{time.strftime('还有%M个月%d天', time.gmtime(time.mktime((time.gmtime().tm_year + 1, 9, 16, 19, 30, 0, 0, 0, 0)) - time.time()))}")
        # 2024: 远在地球另一边无法赶回来
        tip.setCentralWidget(self.tlabel)
        
        def updateTime(self):
            year = time.localtime().tm_year if time.localtime().tm_mon < 8 or (
                    time.localtime().tm_mon == 8 and time.localtime().tm_mday < 16) else (
                    time.localtime().tm_year + 1)
            time_s = time.gmtime(time.mktime((year, 8, 16, 0, 0, 0, 0, 0, 0)) - time.time())
            time_text = f"还有{time_s.tm_mon - 1}个月{time_s.tm_mday}天"
            wait_text = f"敬请等待{year}年8月16号<br/>{time_text}"
            topic_text = f'<a href="{"https://www.bilibili.com/v/topic/detail/?topic_id=53624"}" style="text-decoration: none">#{"2233生日快乐"}#</a><br/>(都说了全网带话题 <a href="{"https://www.bilibili.com/v/topic/detail/?topic_id=53624"}" style="text-decoration: none">#{"2233生日快乐"}#</a>。这不，<small style="font-size: xx-small"><del style="text-decoration: line-through">{"远在地球另一边无法赶回来"}</del></small>的我也带了这个话题了。都别针对我呀，<small style="font-size: xx-small"><del style="text-decoration: line-through">我是无辜的</del></small>。)'
            self.tlabel.setText(
                topic_text if time.localtime().tm_mon == 8 and time.localtime().tm_mday == 16 else wait_text)
        
        t = QTimer(self)
        t.timeout.connect(lambda: updateTime(self))
        t.start(1000)
        self.verticalLayout_2.addWidget(tip)
        # popupTip = PopupTip(self, close_enabled=False)
        # label2 = Label(tip)
        # label2.setText("#2233生日快乐#")
        # popupTip.setCentralWidget(label2)
        # popupTip.tip()
        self.label2 = Label(self.scrollAreaContentWidget)
        self.label2.setText((f"""<!DOCTYPE html>
                        <html>
                            <head/>
                            <body>
                                <p>
                                <hr/>
                                <h2>开头</h2>
                                ---------<br/>
                                你知道 22 和 33 吗？<br/>
                                <small style="font-size: xx-small"><del style='text-decoration: line-through'>我知道你不知道她们</del></small>(并不) <br/>
                                22 和 33: 给你一次重新组织语言的机会，你知不知道我们？<br/>
                                <a href='https://space.bilibili.com/68559'>她们的官方账号(https://space.bilibili.com/68559)</a><br/>
                                然后呢？<br/>
                                她们的生日在8月多少日来着？？？<br/>
                                22 和 33: 你号没了！去小黑屋罚抄“2233生日在8月16号*100遍！！！”<br/>
                                由此可得知她们都是狮子座。<br/>
                                <h2>设定</h2>
                                ---------<br/>
                                让我们先说 22 吧 <br/>
                                <h3>22 的设定</h3>
                                身高：160cm <br/>
                                体重：48KG<br/>
                                生日：8月16日<br/>
                                <small style="font-size: xx-small"><del style='text-decoration: line-through'>绰号：F22<br/>想知道更多可以去<a href="https://www.bilibili.com/video/BV1wJ411J7JK/">https://www.bilibili.com/video/BV1wJ411J7JK/</a>一探究竟。</del></small><br/>
                                声优：{{ <br/>
                                    柴刀娘木木（2015）<br/>
                                    幽舞越山（2016--）<br/>
                                    <del style='text-decoration: line-through'>AI（2024年唱歌）</del><br/>
                                }}<br/>
                                <br/><br/>
                                再来说 33 吧 <br/>
                                <h3>33 的设定</h3>
                                身高：148cm <br/>
                                体重：？？？（怕 33 咬我，可以告诉你们 2 开头）<br/>
                                生日：8月16日<br/>
                                声优：{{<br/>
                                    柴刀娘木木（2015）<br/>
                                    少愿愿（2016-2018）<br/>
                                    李姗姗（2019--）<br/>
                                    Hanser（部分歌曲？）<br/>
                                    <del style='text-decoration: line-through'>AI（2024年唱歌）</del><br/>
                                }}<br/>
                                <br/><br/>
                                <h2>概述</h2>
                                ---------<br/>
                                22娘为姐姐，33娘为妹妹，于2010年8月16日由Bilibili站娘投票结果产生。<br/>
                                <h2>属性</h2>
                                ---------<br/>
                                <h3>22娘的属性</h3>
                                <ul>
                                    <li style="display: list-item;">姐姐是个阳光元气娘，非常活泼有精神，对人热情，热心帮忙。但有些冒冒失失。</li>
                                    <li style="display: list-item;">偶尔还会心血来潮做点发明改造，有时改进下播放器等等，<small style="font-size: xx-small"><del style='text-decoration: line-through'>但是她做出来东西经常是会有BUG的，往往需要妹妹二次修复，而且因为姐姐的冒失，妹妹经常腹黑的吐槽。<br/>(感兴趣的，可以去 <a href="https://mzh.moegirl.org.cn/File:%E8%A6%81%E5%B8%AE%E5%BF%99%E5%90%97.jpg">https://mzh.moegirl.org.cn/File:%E8%A6%81%E5%B8%AE%E5%BF%99%E5%90%97.jpg</a> 看一下)</del></small><br/>(仅供娱乐，请勿当真)</li>
                                    <li style="display: list-item;">姐姐充满干劲，而且这种表现常常会感染到周遭的人，妹妹最喜欢姐姐这点了。</li>
                                    <li style="display: list-item;">性格上很乐观，<small style="font-size: xx-small"><del style='text-decoration: line-through'>但也会因某些事儿消极</del></small>(就当刚才那句我胡说)，偶尔傲娇一下，比较喜欢跟妹妹傲娇。</li>
                                    <li style="display: list-item;"><small style="font-size: xx-small"><del style='text-decoration: line-through'>姐姐很害怕猎奇、恐怖类事物，每每审核到这类型视频，都会被吓哭，结果这部分视频都是交由妹妹帮忙审核。</del></small>(这条我编的，都别信，我号还要)</li>
                                    <li style="display: list-item;">毕竟是姐姐，常常有保护妹妹的欲望，<small style="font-size: xx-small"><del style='text-decoration: line-through'>但往往需要被保护的都是自己。</del></small>(刚才那句我瞎说)</li>
                                </ul>
                                <br/>
                                <h3>33娘的属性</h3>
                                <ul>
                                    <li style="display: list-item;">妹妹是个机娘，个性沉默寡言，情感冷静少起伏且表情缺乏变化。</li>
                                    <li style="display: list-item;">别看是妹妹，平时都是她来给网站维护服务器和鼓弄网站各种程序。有着惊人的知识量，记忆力。<small style="font-size: xx-small"><del style='text-decoration: line-through'>(chengwm（CMCL启动器作者）： 33，请问我能......)</del></small></li>
                                    <li style="display: list-item;">爱发明和创造物品，<small style="font-size: xx-small"><del style='text-decoration: line-through'>但大多数都是奇奇怪怪的，就比如<a href="https://mzh.moegirl.org.cn/File:%E5%A5%87%E5%A5%87%E6%80%AA%E6%80%AA.jpg">https://mzh.moegirl.org.cn/File:%E5%A5%87%E5%A5%87%E6%80%AA%E6%80%AA.jpg</a>这张图片。</del></small>(仅供娱乐，请勿当真)</li>
                                    <li style="display: list-item;">妹妹需要充电，在身后（臀部）插入插头形状的“尾巴”，连上插座即可充电,当然也可以吃电池来充电。<del style='text-decoration: line-through'>(难道这就是呆毛事故的原因吗？)</del></li>
                                    <li style="display: list-item;">妹妹有两个怪癖，一是平时没事喜欢啃插座<del style='text-decoration: line-through'>(22: 啊疼疼疼疼疼)</del>；二是虽说是个机娘，但是睡觉的时候不抱着东西，就无法入睡。</li>
                                    <li style="display: list-item;">妹妹虽然经常会因为姐姐的冒失而吐槽，但是心里还是很十分喜欢姐姐的。妹妹虽然经常会因为姐姐的冒失而吐槽，但是心里还是很十分喜欢姐姐的。</li>
                                    <li style="display: list-item;">据说33不会被蚊子咬？</li>
                                </ul>
                                <br/>
                                <h2>目前为止可以公开(或者不会被封号)的情报</h2>
                                ---------<br/>
                                <ul>
                                    <li style="display: list-item;">22的腰包有好几种，四次元腰包可以装的下任何东西（类似于哆啦A梦的口袋）。(见<a href="https://mzh.moegirl.org.cn/File:22%E7%9A%84%E8%85%B0%E5%8C%85.jpg">https://mzh.moegirl.org.cn/File:22%E7%9A%84%E8%85%B0%E5%8C%85.jpg</a>)</li>
                                    <li style="display: list-item;">22身高160cm，33身高146cm，这个身高极其萌。(见<a href="https://mzh.moegirl.org.cn/File:2233%E8%BA%AB%E9%AB%98%E5%B7%AE.jpg">https://mzh.moegirl.org.cn/File:2233%E8%BA%AB%E9%AB%98%E5%B7%AE.jpg</a>)</li>
                                    <li style="display: list-item;">两位都有呆毛，貌似可当天线使用，但没有验证过。</li>
                                    <li style="display: list-item;">22娘是闪电型呆毛，33是月牙形呆毛，因为“bilibili”一名的来源为“电击使”御坂美琴，于是22的呆毛形状被设计成与电相关(见<a href="https://mzh.moegirl.org.cn/File:2233%E5%91%86%E6%AF%9B.jpg">https://mzh.moegirl.org.cn/File:2233%E5%91%86%E6%AF%9B.jpg</a>)</li>
                                    <li style="display: list-item;">两姐妹头发上都夹着个一样的小电视发夹（有时在左边有时在右边，并不是一般的发夹，小电视发夹上的表情是与2233同步变化）。(见<a href="https://mzh.moegirl.org.cn/File:%E5%8F%91%E5%A4%B9%E7%9A%84%E7%A7%98%E5%AF%86.jpg">https://mzh.moegirl.org.cn/File:%E5%8F%91%E5%A4%B9%E7%9A%84%E7%A7%98%E5%AF%86.jpg</a>)</li>
                                    <li style="display: list-item;">有时候33娘没有小电视发夹，只有播放按钮发夹，而且发夹自称是精灵球。(见<a href="https://mzh.moegirl.org.cn/File:%E7%B2%BE%E7%81%B5%E7%90%83%E5%8F%91%E5%A4%B9.jpg">https://mzh.moegirl.org.cn/File:%E7%B2%BE%E7%81%B5%E7%90%83%E5%8F%91%E5%A4%B9.jpg</a>)</li>
                                    <li style="display: list-item;">33在工作时喜欢穿白大褂，额头上有投影装置，还可以扫描解析，使用AR眼镜或额头上的投影装置都可以让33浮现操作面板，以更改自身设置以及浏览互联网等操作。(见<a href="https://mzh.moegirl.org.cn/File:%E5%85%B3%E4%BA%8E33%E5%A8%98.jpg">https://mzh.moegirl.org.cn/File:%E5%85%B3%E4%BA%8E33%E5%A8%98.jpg</a>)</li>
                                    <li style="display: list-item;">两姐妹都是ACG爱好者，也会追新番，也喜欢看各种神技术搞笑带弹幕吐槽的视频。（两人审核时，偶尔会被特别喜好的视频吸引住眼球，而忘记正在审核……）</li>
                                    <li style="display: list-item;">两姐妹都会审核视频，姐姐对着宠物小电视审核；妹妹则是从自己额头的成像仪投影出视频来审核。由于，网站视频的投稿量大，两人常常忙得不亦乐乎。其他方面，网站服务器维护以及各种程序基本都是由妹妹来完成，姐姐则多处理各种BILI众的意见或BUG的反馈。(PS：根据B站视频<a href="https://mzh.moegirl.org.cn/%E5%B9%B8%E7%A6%8F%E5%B0%B1%E5%9C%A8%E4%BD%A0%E8%BA%AB%E8%BE%B9">《Bilibili耶》</a>中，可以看出妹妹略带攻属性。)</li>
                                    <li style="display: list-item;">33左臂装有能量炮，可以向任意物体发射。(见<a href="https://mzh.moegirl.org.cn/File:Bilibili%E6%BC%AB%E7%94%BB%E5%AE%B3%E6%80%95.webp">https://mzh.moegirl.org.cn/File:Bilibili%E6%BC%AB%E7%94%BB%E5%AE%B3%E6%80%95.webp</a>)</li>
                                    <li style="display: list-item;">据说33的右臂是爱心飞拳？可以分离？还可以抓住物体？(见<a href="https://manga.bilibili.com/mc28173/455648">https://manga.bilibili.com/mc28173/455648</a>)</li>
                                </ul>
                                <br/>
                                <h2>趣闻</h2>
                                ---------<br/>
                                <ul>
                                    <li style="display: list-item;"><small style="font-size: xx-small"><del style='text-decoration: line-through'>22有一次审核恐怖视频时被吓到了，晚上不敢去洗手间，结果第二天一早醒来发现自己尿床了(⊙o⊙)。结果晒床单时被妹妹33娘看见……</del></small>(都懂的......)</li>
                                    <li style="display: list-item;"><small style="font-size: xx-small"><del style='text-decoration: line-through'>22近期迷上了哲♂学、兄♂贵、摔♂跤以及FA♂乐器，用33的手机看了之后留下了喜好推荐被33发现，结果亲身体♂验了一番。</del></small>(仅供娱乐)</li>
                                </ul>
                                <br/>
                                <h2>一些不好说的东西</h2>
                                ---------<br/>
                                <small style="font-size: xx-small"><del style='text-decoration: line-through'>热知识：在2017年，2233 以 98 亿（9876547210.33元）被卖身。（雾）</del></small><br/>
                                <small style="font-size: xx-small"><del style='text-decoration: line-through'>震惊，Bilibili的98亿竟被两个员工花完。（2021年拜年纪）</del></small>
                              </p>
                              <p>更多信息请前往<a href="https://mzh.moegirl.org.cn/Bilibili%E5%A8%98">此处</a>了解。</p>
                              <h2>声明</h2>
                              <p>---------</p>
                              <p>
                                以上为测试文本，为启动器测试文本显示、HTML样式测试、模板填空测试以及排版测试文本。著作权归原编辑者所有。<br/>
                                还有，很多地方我瞎说的，别信！<br/>
                              </p>
                              <p>此文本介绍部分内容及数据引自萌娘百科(mzh.moegirl.org.cn)，具体链接：<a href="https://mzh.moegirl.org.cn/Bilibili%E5%A8%98">*</a>，<strong>内容不可商用，著作权归原编辑者所有</strong></p>
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
        self.launch_btn.setText("启动")
        self.select_version_btn.setText(self.version or "选择版本")
        self.change_dir_btn.setText("切换文件夹")
    
    def select_version(self, version):
        self.version = version
        self.select_version_btn.setText(self.version or "选择版本")
    
    def launch(self):
        result = LaunchMinecraft(minecraft_path, self.version, None,
                                 "server",
                                 CMCL_version[0], None, None, None, "", None, None,
                                 player)
        print(result)
    
    def setMinecraftDir(self):
        global minecraft_path
        path = QFileDialog(self).getExistingDirectory(self, "选择文件夹", str(minecraft_path))
        if path:
            minecraft_path = Path(path)
            self.update_menu()
    
    def update_menu(self):
        menu = RoundedMenu()
        versions = GetVersionByScanDirectory(minecraft_path=minecraft_path)
        if isinstance(versions, list):
            for version in versions:
                action = QAction(menu)
                action.setText(version)
                action.triggered.connect(lambda _, v=version: self.select_version(v))
                menu.addAction(action)
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
            def __init__(self, parent):
                super().__init__(parent)
        
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
            # self.tableView.clicked.connect(self.turn_to_download_page)
            self.versionModel = QStandardItemModel(self.tableView)
            self.versionModel.setHorizontalHeaderLabels(["版本", "类型", "发布时间"])
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
            self.comboBox.addItem("官方源")
            # self.comboBox.setEditable(True)
            
            self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.comboBox)
            
            self.horizontalLayout.addLayout(self.formLayout)
            
            self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
            
            self.horizontalLayout.addItem(self.horizontalSpacer)
            
            self.verticalLayout.addWidget(self.frame)
            
            self.retranslateUi()
            
            self.loadingAnimation = None
            self.getVersionThread = None
            
            # QMetaObject.connectSlotsByName(self)
            # setupUi
        
        def retranslateUi(self):
            self.label.setText(u"\u4e0b\u8f7d\u6e90\uff1a")
            self.versionModel.setHorizontalHeaderLabels(["版本", "类型", "发布时间"])
        
        # retranslateUi
        
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
                    zone = int((datetime.datetime.now() - datetime.datetime.utcnow()).seconds / 60 / 60)
                    release_time = datetime.datetime.strptime(unformatted_release_time,
                                                              "%Y-%m-%dT%H:%M:%S+00:00").replace(
                        tzinfo=datetime.UTC).astimezone(pytz.timezone(f"Etc/GMT-{zone}")).strftime(
                        "%Y-%m-%d %H:%M:%S")
                    time_1 = datetime.datetime.strptime(release_time, "%Y-%m-%d %H:%M:%S")
                    if time_1.month == 4 and time_1.day == 1:
                        version_type = "愚人节版本"
                        version_type_real = "april_fool"
                    for e2, i2 in enumerate([version, version_type, release_time]):
                        self.versionModel.setItem(e, e2, QStandardItem(i2))
                    self.versions[version] = {"VersionId": version, "VersionType": version_type_real,
                                              "releaseTime": release_time}
                    completer_l.append(version)
                self.lineEdit.setCompleter(QCompleter(completer_l, self.lineEdit))
                self.versionModel.setHorizontalHeaderLabels(["版本", "类型", "发布时间"])
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
                    release_time = value["releaseTime"]
                    time_1 = datetime.datetime.strptime(release_time, "%Y-%m-%d %H:%M:%S")
                    if time_1.month == 4 and time_1.day == 1:
                        version_type = "愚人节版本"
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
                    release_time = value["releaseTime"]
                    for e2, i2 in enumerate([version, version_type, release_time]):
                        self.versionModel.setItem(i, e2, QStandardItem(i2))
                    i += 1
                else:
                    try:
                        if re.match(version_d, key, re.UNICODE) or re.match(version_d, value["VersionType"],
                                                                            re.UNICODE) or re.match(version_d, value[
                            "releaseTime"], re.UNICODE):
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
                            release_time = value["releaseTime"]
                            time_1 = datetime.datetime.strptime(release_time, "%Y-%m-%d %H:%M:%S")
                            if time_1.month == 4 and time_1.day == 1:
                                version_type = "愚人节版本"
                            for e2, i2 in enumerate([version, version_type, release_time]):
                                self.versionModel.setItem(i, e2, QStandardItem(i2))
                            i += 1
                    except re.error:
                        pass
            self.versionModel.setHorizontalHeaderLabels(["版本", "类型", "发布时间"])
            self.tableView.setModel(self.versionModel)
            self.tableView.setSelectionMode(QTableView.SelectionMode.SingleSelection)
            self.tableView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            self.tableView.horizontalHeader().setVisible(True)
            self.tableView.verticalHeader().setVisible(False)
    
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
        self.stackedWidget.currentChanged.connect(self.update_navigation)
        
        self.verticalLayout.addWidget(self.stackedWidget)
        
        self.retranslateUi()
        #
        # QMetaObject.connectSlotsByName(Form)
    
    # setupUi
    
    def retranslateUi(self):
        self.pushButton.setText("原版")
        # self.pushButton_2.setText("")
    
    # retranslateUi
    
    def update_page(self, btn):
        self.stackedWidget.setCurrentWidget(self.pages[btn])
    
    def update_navigation(self, _):
        print(_)
        print(self.stackedWidget.currentIndex())


class UserPage(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.user_datas = []
        self.current_user = 0
        
        # DEBUG: ON#
        self.user_datas.append(create_online_player("2233", "68559", "TheFengHaoDouLuoOfBiZhan", True))
        self.user_datas.append(create_online_player("22和33", "68559", "TheSameAsAbove", True))
        self.user_datas.append(player)
        self.user_datas.append(create_online_player("chengwm_CMCL", "100000000", "NoAccessToken", False))
        self.current_user = 2
        # DEBUG: END#
        
        self.verticalLayout = QVBoxLayout(self)
        self.topPanel = Panel(self)
        self.horizontalLayout = QHBoxLayout(self.topPanel)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.leftUserIcon = ToolButton(self.topPanel)
        self.leftUserIcon.setIcon(QIcon("user_icon-black.svg"))
        self.leftUserIcon.setIconSize(QSize(32, 32))
        left_user = self.user_datas[min(max(self.current_user - 1, 0), len(self.user_datas) - 1)]
        self.leftUserIcon.setToolTip(
            f"用户名称：{left_user.player_name}\n类型：{left_user.player_accountType[1]}账户（在线）\n是否拥有Minecraft: {left_user.player_hasMC}")
        self.leftUserIcon.pressed.connect(lambda: self.select_new_user(self.current_user - 1))
        self.horizontalLayout.addWidget(self.leftUserIcon)
        spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacer)
        self.UserIcon = ToolButton(self.topPanel)
        self.UserIcon.setIcon(QIcon("user_icon-black.svg"))
        self.UserIcon.setIconSize(QSize(32, 32))
        current_user = self.user_datas[self.current_user]
        self.UserIcon.setText(
            f"用户名称：{current_user.player_name}\n类型：{current_user.player_accountType[1]}账户（在线）\n是否拥有Minecraft: {current_user.player_hasMC}")
        self.UserIcon.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.horizontalLayout.addWidget(self.UserIcon)
        spacer2 = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacer2)
        self.rightUserIcon = ToolButton(self.topPanel)
        self.rightUserIcon.setIcon(QIcon("user_icon-black.svg"))
        self.rightUserIcon.setIconSize(QSize(32, 32))
        right_user = self.user_datas[min(max(self.current_user + 1, 0), len(self.user_datas) - 1)]
        self.rightUserIcon.setToolTip(
            f"用户名称：{right_user.player_name}\n类型：{right_user.player_accountType[1]}账户（在线）\n是否拥有Minecraft: {right_user.player_hasMC}")
        self.rightUserIcon.pressed.connect(lambda: self.select_new_user(self.current_user + 1))
        self.horizontalLayout.addWidget(self.rightUserIcon)
        self.verticalLayout.addWidget(self.topPanel)
        
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
        self.userModel.setHorizontalHeaderLabels(["用户名", "类型"])
        self.userTabel.setModel(self.userModel)
        self.userModel.clear()
        self.userModel.setHorizontalHeaderLabels(["用户名", "类型"])
        for e, i in enumerate(self.user_datas):
            self.userModel.setItem(e, 0, QStandardItem(i.player_name))
            self.userModel.setItem(e, 1, QStandardItem(i.player_accountType[1]))
        # self.userModel.setItem(0, 0, QStandardItem("22&33"))
        # self.userModel.setItem(0, 1, QStandardItem("Bilibili账户"))
        # self.userModel.setItem(1, 0, QStandardItem("22和33"))
        # self.userModel.setItem(1, 1, QStandardItem("Bilibili账户"))
        # self.userModel.setItem(2, 0, QStandardItem("chengwm"))
        # self.userModel.setItem(2, 1, QStandardItem("Microsoft账户"))
        # self.userModel.setItem(3, 0, QStandardItem("chengwm_CMCL"))
        # self.userModel.setItem(3, 1, QStandardItem("Bilibili账户"))
        
        self.retranslateUI()
    
    def retranslateUI(self):
        left_user = self.user_datas[min(max(self.current_user - 1, 0), len(self.user_datas) - 1)]
        self.leftUserIcon.setToolTip(
            f"用户名称：{left_user.player_name}\n类型：{left_user.player_accountType[1]}账户（在线）\n是否拥有Minecraft: {left_user.player_hasMC}")
        current_user = self.user_datas[self.current_user]
        self.UserIcon.setText(
            f"用户名称：{current_user.player_name}\n类型：{current_user.player_accountType[1]}账户（在线）\n是否拥有Minecraft: {current_user.player_hasMC}")
        right_user = self.user_datas[min(max(self.current_user + 1, 0), len(self.user_datas) - 1)]
        self.rightUserIcon.setToolTip(
            f"用户名称：{right_user.player_name}\n类型：{right_user.player_accountType[1]}账户（在线）\n是否拥有Minecraft: {right_user.player_hasMC}")
        self.userModel.clear()
        self.userModel.setHorizontalHeaderLabels(["用户名", "类型"])
        for e, i in enumerate(self.user_datas):
            self.userModel.setItem(e, 0, QStandardItem(i.player_name))
            self.userModel.setItem(e, 1, QStandardItem(i.player_accountType[1]))
    
    def select_new_user(self, id):
        self.current_user = id
        self.current_user = max(0, min(len(self.user_datas) - 1, self.current_user))
        self.retranslateUI()


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
        self.titleBar.titleLabel.setText(self.windowTitle(), )
        self.titleBar.titleLabel.setStyleSheet(
            "background: transparent; padding: 0 4px; font: 13px 'Segoe UI'; color: black")
        self.setStyleSheet("background: transparent")
        self.centralwidget = QWidget(self)
        self.horizontalLayout = QVBoxLayout(self.centralwidget)
        self.horizontalLayout.setContentsMargins(5, 37, 5, 5)
        self.horizontalLayout.setSpacing(10)
        self.topWidget = FoldableNavigationPanel(self.centralwidget)
        self.HomePage = MainPage(self)
        self.topWidget.addItem(self.HomePage, "Home.svg", "主页")
        self.DownloadPage = DownloadPage(self)
        self.topWidget.addItem(self.DownloadPage, "Download.svg", "下载")
        self.UserPage = UserPage(self)
        self.topWidget.addItem(self.UserPage, "user_icon-black.svg", "用户",
                               pos=NavigationPanel.NavigationItemPosition.Right)
        self.topWidget.addButton("auto_black.svg", "浅色", selectable=False,
                                 pos=NavigationPanel.NavigationItemPosition.Right)
        self.horizontalLayout.addWidget(self.topWidget)
        self.content = ContentPanel(self.centralwidget)
        self.horizontalLayout.addWidget(self.content, 1)
        self.topWidget.setContentWidget(self.content)
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
        self.show()
    
    def start_login(self):
        dialogue = LoginDialogue()
        dialogue.exec()
    
    def paintEvent(self, a0, **kwargs):
        painter = QPainter(self)
        painter.fillRect(
            QRect(-self.geometry().x(), -self.geometry().y(), QGuiApplication.primaryScreen().geometry().width(),
                  QGuiApplication.primaryScreen().geometry().height()),
            QGradient(QGradient.Preset.PerfectWhite if getTheme() == Theme.Light else QGradient.Preset.PerfectBlue))


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
        self.setWindowTitle("日志窗口")
        self.titleBar.hide()
        self.titleBar = StandardTitleBar(self)
        self.titleBar.show()
        self.titleBar.raise_()
        self.titleBar.iconLabel.setPixmap(self.windowIcon().pixmap(20, 20))
        self.titleBar.iconLabel.setStyleSheet("background: transparent;")
        self.titleBar.titleLabel.setText(self.windowTitle(), )
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
        self.inputtext.setFont(font)
        # self.inputtext.setToolTip("Enter command below and press 'Return' to execute command.")
        self.canOutput = True
        self.retranslateUI()
        self.cmd = self.Executer({"frame": frame, "player": player})
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
    
    def paintEvent(self, a0, **kwargs):
        painter = QPainter(self)
        painter.fillRect(
            QRect(-self.geometry().x(), -self.geometry().y(), QGuiApplication.primaryScreen().geometry().width(),
                  QGuiApplication.primaryScreen().geometry().height()),
            QGradient(QGradient.Preset.PerfectWhite if getTheme() == Theme.Light else QGradient.Preset.PerfectBlue))


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
#             QGradient(QGradient.Preset.PerfectWhite if getTheme() == Theme.Light else QGradient.Preset.PerfectBlue))


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
player = create_online_player(None, None, None, False)
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
#       "[2009/??/??][??:??:?? ??][INFO]:某个叫 Mikufans 的网站创建！（Mikufans 就是今天的 Bilibili！）\n"
#       "[2008/??/??][??:??:?? ??][INFO]:Minecraft 前身 RubyDung 被 Markus Persson 创建！\n"
#       "[2009/05/10][17:36:00 PM][INFO]:Minecraft 最早版本 rd-131655 的视频被上传！\n"
#       "[2011/11/17][22:00:00 PM][INFO]:Minecraft 1.0.0 发布！")
# END Text
# Mid-Autumn Dialogue Test
# dialogue = MidAutumnMsgDialogue()
# dialogue.show()
# END Test
thread = LoginThread()
thread.loginFinished.connect(update_user)
thread.start()
app.exec()
