# -*- coding: utf-8 -*-
"""
project start time:1693310592
|-time.struct_time(tm_year=2023, tm_mon=8, tm_mday=29, tm_hour=20, tm_min=3, tm_sec=12, tm_wday=1, tm_yday=241, tm_isdst=0)
|-2023/08/29 20:03:12, Tuesday, August, Zone:中国标准时间(UTC+8), 一年的第241天
"""
import base64
import ctypes
import datetime

import psutil
import re
import sqlite3
import traceback
import webbrowser
from subprocess import PIPE
import subprocess
import sys

import pytz
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtWidgets import *
from qfluentwidgets import *
from qfluentwidgets.common.translator import FluentTranslator
from qfluentwidgets.common.config import *
from qfluentwidgets.common.style_sheet import Theme, isDarkTheme, setTheme
from qfluentwidgets.components.widgets.acrylic_label import AcrylicBrush, AcrylicLabel

import get_os
from launch import launch
from login import get_user_data
from download_version import *
from player import Player
from get_os import getOperationSystemName

version = ("Alpha-24001", "Alpha-24001")

conv_table = {
    "msa": "Microsoft 账户",
    None: "无"
}

state = {
    "online": "在线",
    "offline": "离线",
    None: "无"
}


class LoadingSvgSplash(QFrame):
    class HideAnimation(QThread):
        def run(self):
            import time
            time.sleep(1)
            self.parent().hide()
    
    class TransparencyAnimation(QVariantAnimation):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setStartValue(255)
            self.setEndValue(0)
            self.setDuration(1000)
            self.valueChanged.connect(self.update_opacity)
        
        def update_opacity(self, value):
            colour = value
            self.parent().setStyleSheet(
                f"background: rgba({'249, 249, 249' if not isDarkTheme() else '43, 43, 43'}, {colour / 255})")
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setStyleSheet(f"background: {'rgb(249, 249, 249)' if not isDarkTheme() else 'rgb(43, 43, 43)'};")
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
        self.statusLabel = BodyLabel(self)
        self.statusLabel.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    
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
    
    def hideEvent(self, *args, **kwargs):
        super().hideEvent(*args, **kwargs)
        try:
            self.deleteLater()
        except RuntimeError:
            pass
    
    def start(self):
        self.setStyleSheet(f"background: {'rgb(249, 249, 249)' if not isDarkTheme() else 'rgb(43, 43, 43)'};")
        self.statusLabel.setText(app.translate("LoadingSvgSplash", "LoadingSvgSplash.statusText.loading"))
        self.svgWidget.load("CMCL_loading.svg")
        self.failedSvg.load("CMCL_loading_failed.svg")
        self.failedSvg.hide()
        self.show()
    
    def finish(self, failed=False):
        try:
            if not failed:
                self.TransparencyAnimation(self).start()
                self.HideAnimation(self).start()
                self.statusLabel.setText(
                    app.translate("LoadingSvgSplash", "LoadingSvgSplash.statusText.loadsuccess"))
                self.failedSvg.hide()
            else:
                self.setStyleSheet(f"background: {'rgb(255, 200, 200)' if not isDarkTheme() else 'rgb(100, 43, 43)'};")
                self.statusLabel.setText(
                    app.translate("LoadingSvgSplash", "LoadingSvgSplash.statusText.loadfailed"))
                self.failedSvg.show()
        except RuntimeError:
            pass


class ToolBox(QToolBox):
    def addItem(self, item, *__args):
        self.insertItem(-1, item, *__args)
    
    def insertItem(self, index, item, *__args):
        class ToolBoxButton(PillPushButton):
            def __init__(self, btn_parent, btn_index=0, btn_icon=QIcon(), btn_text=None):
                super().__init__(btn_parent)
                self.setCheckable(True)
                self.setAutoExclusive(True)
                self.index = btn_index
                self.setIcon(btn_icon)
                self.setText(btn_text)
            
            def mouseReleaseEvent(self, e):
                self.parent().setCurrentIndex(self.index)
                super().mouseReleaseEvent(e)
                self.setChecked(True)
        
        if len(__args) >= 1:
            if len(__args) >= 2:
                if isinstance(__args[1], QIcon):
                    icon = __args[1]
                    text = __args[2]
                else:
                    icon = QIcon()
                    text = __args[1]
            else:
                icon = QIcon()
                text = __args[0]
        else:
            icon = QIcon()
            text = None
        btn = ToolBoxButton(self, (len(self.children()) - 1) // 2, icon, text)
        btn.installEventFilter(ToolTipFilter(btn))
        pos = index * 2
        self.layout().insertWidget(pos, btn)
        self.layout().insertWidget(pos + 1, item)
    
    def setItemText(self, index, text):
        if len(self.children()) > 1:
            self.children()[(index * 2) + 1 if index >= 0 else (index * 2)].setText(text)
    
    def setItemIcon(self, index, icon):
        if len(self.children()) > 1:
            self.children()[(index * 2) + 1 if index >= 0 else (index * 2)].setIcon(icon)
    
    def setItemToolTip(self, index, toolTip):
        if len(self.children()) > 1:
            self.children()[(index * 2) + 1 if index >= 0 else (index * 2)].setTooltip(toolTip)
    
    def setItemEnabled(self, index, enabled):
        if len(self.children()) > 1:
            self.children()[(index * 2) + 1 if index >= 0 else (index * 2)].setEnabled(enabled)
    
    def isItemEnabled(self, index):
        if len(self.children()) > 1:
            return self.children()[(index * 2) + 1 if index >= 0 else (index * 2)].isEnabled()
    
    def indexOf(self, widget):
        if len(self.children()) > 1:
            for i in range(2, len(self.children()), 2):
                if self.children()[i] == widget:
                    return (i - 2) // 2
            else:
                return -1
        else:
            return -1
    
    def setCurrentIndex(self, index):
        if len(self.children()) > 1:
            for i in range(1, len(self.children()) - 1, 2):
                if (i - 1) // 2 == index:
                    self.children()[i].setChecked(True)
                    self.children()[i + 1].setVisible(True)
                    self.currentChanged.emit((i - 1) // 2)
                    self.changeEvent(QEvent(QEvent.Type.ActivationChange))
                else:
                    self.children()[i].setChecked(False)
                    self.children()[i + 1].setVisible(False)
    
    def setCurrentWidget(self, widget):
        if len(self.children()) > 1:
            if widget not in self.children()[2::2]:
                return
            index = self.children().index(widget) - 1
            for i in range(1, len(self.children()) - 1, 2):
                if (i - 1) // 2 == index:
                    self.children()[i].setChecked(True)
                    self.children()[i + 1].setVisible(True)
                else:
                    self.children()[i].setChecked(False)
                    self.children()[i + 1].setVisible(False)
    
    def removeItem(self, index):
        if len(self.children()) > 1:
            pos = index * 2 + 1
            btn = self.children()[pos]
            btn.hide()
            btn.deleteLater()
            self.layout().removeWidget(btn)
            item = self.children()[pos + 1]
            item.hide()
            self.layout().removeWidget(item)
    
    def removeAllItem(self):
        if len(self.children()) > 1:
            for i in range(1, len(self.children())):
                self.layout().removeWidget(self.children()[i])
    
    def itemIcon(self, index):
        if len(self.children()) > 1:
            pos = index * 2 + 1
            return self.children()[pos].icon()
    
    def itemText(self, index):
        if len(self.children()) > 1:
            pos = index * 2 + 1
            return self.children()[pos].text()
    
    def itemToolTip(self, index):
        if len(self.children()) > 1:
            pos = index * 2 + 1
            return self.children()[pos].tooltip()
    
    def showEvent(self, e):
        if len(self.children()) > 1:
            for i in range(1, len(self.children()) - 1, 2):
                if self.children()[i].isChecked():
                    break
            else:
                self.setCurrentIndex(0)
        super().showEvent(e)


class GroupBox(QGroupBox):
    def paintEvent(self, *args, **kwargs):
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setStyleSheet(f"""GroupBox{{
        border: 1px solid gray;
        border-radius: 10px;
        padding: 15px;
    }}
    GroupBox::title{{
        border: 1px solid rgba{(255, 255, 255, 18) if isDarkTheme() else (0, 0, 0, 15)};
        border-radius: 10px;
        padding: 2px;
    }}""")
        return super().paintEvent(*args, **kwargs)


# class PythonTextEdit(HighlightTextEdit, AutoIndentTextEdit, AutoMatchTextEdit, AutocompleteTextEdit,
#                      LineNumberTextEdit):
#     class Highlighter(HighlightTextEdit.Highlighter):
#         def __init__(self, document):
#             super().__init__(document)
#
#             import keyword as k
#
#             keyword = QTextCharFormat()
#             keyword.setForeground(QColor(255, 119, 0))
#
#             builtin = QTextCharFormat()
#             builtin.setForeground(QColor(144, 0, 144))
#
#             string = QTextCharFormat()
#             string.setForeground(QColor(0, 170, 9))
#
#             comment = QTextCharFormat()
#             comment.setForeground(QColor(221, 0, 0))
#
#             self.highlight_styles["keyword"] = keyword
#             self.highlight_styles["builtin"] = builtin
#             self.highlight_styles["string"] = string
#             self.highlight_styles["comment"] = comment
#
#             import builtins
#
#             builtin = dir(builtins)
#             builtin = [i for i in builtin if i not in k.kwlist and i not in k.softkwlist]
#             stringprefix = r"(?i:r|u|f|fr|rf|b|br|rb)?"
#             sqstring = stringprefix + r"'[^'\\\n]*(\\.[^'\\\n]*)*'?"
#             dqstring = stringprefix + r'"[^"\\\n]*(\\.[^"\\\n]*)*"?'
#             sq3string = stringprefix + r"'''[^'\\]*((\\.|'(?!''))[^'\\]*)*(''')?"
#             dq3string = stringprefix + r'"""[^"\\]*((\\.|"(?!""))[^"\\]*)*(""")?'
#             string = "|".join([sqstring, dqstring, sq3string, dq3string])
#             self.rules.extend([
#                 (r"([+-]?[0-9_]+[lLjJ]?\b|\b\.[0-9_]+[jJ]?)", 0, self.highlight_styles["numbers"]),
#                 (r"\b(" + "|".join(k.kwlist) + "|" + "|".join(k.softkwlist) + r")\b", 0,
#                  self.highlight_styles["keyword"]),
#                 (r"\b(" + "|".join(builtin) + r")\b", 0, self.highlight_styles["builtin"]),
#                 (string, 0, self.highlight_styles["string"]),
#                 (r"#.*", 0, self.highlight_styles["comment"])
#             ])
#
#     Default_Highlighter = Highlighter
#     Indent_Pattern = r"(if .+:|else:|elif .+:|while .+:|for .+:|def .+:|class .+:|match .+:|case .+:)"
#     Indent_Length = 4
#     need_match = {
#         '"': '"',
#         "'": "'",
#         "(": ")",
#         "[": "]",
#         "{": "}",
#     }
#     Complete_List = ['False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue',
#                      'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from', 'global', 'if', 'import', 'in',
#                      'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try', 'while', 'with',
#                      'yield', 'case', 'match', 'ArithmeticError', 'AssertionError', 'AttributeError',
#                      'BaseException', 'BaseExceptionGroup', 'BlockingIOError', 'BrokenPipeError', 'BufferError',
#                      'BytesWarning', 'ChildProcessError', 'ConnectionAbortedError', 'ConnectionError',
#                      'ConnectionRefusedError', 'ConnectionResetError', 'DeprecationWarning', 'EOFError', 'Ellipsis',
#                      'EncodingWarning', 'EnvironmentError', 'Exception', 'ExceptionGroup', 'FileExistsError',
#                      'FileNotFoundError', 'FloatingPointError', 'FutureWarning', 'GeneratorExit', 'IOError',
#                      'ImportError', 'ImportWarning', 'IndentationError', 'IndexError', 'InterruptedError',
#                      'IsADirectoryError', 'KeyError', 'KeyboardInterrupt', 'LookupError', 'MemoryError',
#                      'ModuleNotFoundError', 'NameError', 'NotADirectoryError', 'NotImplemented', 'NotImplementedError',
#                      'OSError', 'OverflowError', 'PendingDeprecationWarning', 'PermissionError', 'ProcessLookupError',
#                      'RecursionError', 'ReferenceError', 'ResourceWarning', 'RuntimeError', 'RuntimeWarning',
#                      'StopAsyncIteration', 'StopIteration', 'SyntaxError', 'SyntaxWarning', 'SystemError', 'SystemExit',
#                      'TabError', 'TimeoutError', 'TypeError', 'UnboundLocalError', 'UnicodeDecodeError',
#                      'UnicodeEncodeError', 'UnicodeError', 'UnicodeTranslateError', 'UnicodeWarning', 'UserWarning',
#                      'ValueError', 'Warning', 'WindowsError', 'ZeroDivisionError', '__build_class__', '__debug__',
#                      '__doc__', '__import__', '__loader__', '__name__', '__package__', '__spec__', 'abs', 'aiter',
#                      'all', 'anext', 'any', 'ascii', 'bin', 'bool', 'breakpoint', 'bytearray', 'bytes', 'callable',
#                      'chr', 'classmethod', 'compile', 'complex', 'copyright', 'credits', 'delattr', 'dict', 'dir',
#                      'divmod', 'enumerate', 'eval', 'exec', 'exit', 'filter', 'float', 'format', 'frozenset', 'getattr',
#                      'globals', 'hasattr', 'hash', 'help', 'hex', 'id', 'input', 'int', 'isinstance', 'issubclass',
#                      'iter', 'len', 'license', 'list', 'locals', 'map', 'max', 'memoryview', 'min', 'next', 'object',
#                      'oct', 'open', 'ord', 'pow', 'print', 'property', 'quit', 'range', 'repr', 'reversed', 'round',
#                      'set', 'setattr', 'slice', 'sorted', 'staticmethod', 'str', 'sum', 'super', 'tuple', 'type',
#                      'vars', 'zip']
#     Default_Complete_Panel = RoundMenu


class TopBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
    
    def event(self, a0):
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        return super().event(a0)
    
    def paintEvent(self, a0):
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setOpacity(self.windowOpacity())
        painter.setPen(QColor(255, 255, 255, 18) if isDarkTheme() else QColor(0, 0, 0, 15))
        painter.setBrush(self.palette().color(self.backgroundRole()))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)


class PillTopBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
    
    def event(self, a0):
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        return super().event(a0)
    
    def paintEvent(self, a0):
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setOpacity(self.windowOpacity())
        painter.setPen(QColor(255, 255, 255, 18) if isDarkTheme() else QColor(0, 0, 0, 15))
        painter.setBrush(self.palette().color(self.backgroundRole()))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), self.height() // 2, self.height() // 2)


class LoginDialogue(MessageBoxBase):
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
            frame.updateUser(QIcon(), player.player_name)
            self.loginFinished.emit()
    
    loginFinished = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = TitleLabel(self)
        self.titleLabel.setText(app.translate("LoginDialogue", "LoginDialogue.title"))
        self.viewLayout.addWidget(self.titleLabel)
        self.contentLabel = BodyLabel(self)
        self.contentLabel.setText(app.translate("LoginDialogue",
                                                "LoginDialogue.content").format(
            f"color: rgb({themeColor().red()}, {themeColor().green()}, {themeColor().blue()});", "{code}"))
        self.contentLabel.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.viewLayout.addWidget(self.contentLabel)
        self.login_input = LineEdit(self)
        self.login_input.setInputMask("X.XXXX_XXX.X.X.XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX;X")
        self.viewLayout.addWidget(self.login_input)
        self.reopenButton = PushButton(self.buttonGroup)
        self.reopenButton.pressed.connect(lambda: webbrowser.open(
            "https://login.live.com/oauth20_authorize.srf?client_id=00000000402b5328&response_type=code&scope=service%3A%3Auser.auth.xboxlive.com%3A%3AMBI_SSL&redirect_uri=https%3A%2F%2Flogin.live.com%2Foauth20_desktop.srf"))
        self.buttonLayout.addWidget(self.reopenButton)
        self.yesButton.setText(MessageBox.tr("OK"))
        self.cancelButton.setText(MessageBox.tr("Cancel"))
        self.reopenButton.setText(app.translate("LoginDialogue", "LoginDialogue.reopenButton"))
        self.yesButton.pressed.connect(self.__startLogin)
        webbrowser.open(
            "https://login.live.com/oauth20_authorize.srf?client_id=00000000402b5328&response_type=code&scope=service%3A%3Auser.auth.xboxlive.com%3A%3AMBI_SSL&redirect_uri=https%3A%2F%2Flogin.live.com%2Foauth20_desktop.srf")
    
    def __startLogin(self):
        token = self.login_input.text()
        token = token.split(".")[-1]
        print(token)
        thread = self.LoginThread(token, self)
        thread.loginFinished.connect(self.loginFinished.emit)
        thread.start()


class OfflineUserCreationDialogue(MessageBoxBase):
    createFinished = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = TitleLabel(self)
        self.titleLabel.setText(
            app.translate("OfflineUserCreationDialogue", "OfflineUserCreationDialogue.title"))
        self.viewLayout.addWidget(self.titleLabel)
        self.horizontalLayout = QHBoxLayout(self)
        self.label = BodyLabel(self)
        self.label.setText(
            app.translate("OfflineUserCreationDialogue", "OfflineUserCreationDialogue.form1.prompt"))
        self.horizontalLayout.addWidget(self.label)
        self.lineEdit = LineEdit(self)
        validator = QRegularExpressionValidator(self.lineEdit)
        validator.setRegularExpression(QRegularExpression(r"\w+"))
        self.horizontalLayout.addWidget(self.lineEdit)
        self.viewLayout.addLayout(self.horizontalLayout)
        self.yesButton.setText(MessageBox.tr("OK"))
        self.cancelButton.setText(MessageBox.tr("Cancel"))
        self.yesButton.pressed.connect(self.register_user)
    
    def register_user(self):
        if self.lineEdit.text():
            global player
            player = Player.create_offline_player(self.lineEdit.text(), player.player_hasMC)
        self.createFinished.emit()


class ErrorDialogue(MessageBoxBase):
    def __init__(self, parent=None, exc=""):
        super().__init__(parent)
        self.titleLabel = TitleLabel(self)
        self.titleLabel.setText(app.translate("ErrorDialogue", "ErrorDialogue.title"))
        self.viewLayout.addWidget(self.titleLabel)
        self.scrollArea = ScrollArea(self)
        self.scrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.scrollArea.setFrameShadow(QFrame.Shadow.Plain)
        self.contentLabel = BodyLabel(self)
        
        font = QFont("Consolas")
        font.setPointSize(13)
        self.contentLabel.setFont(font)
        self.contentLabel.setText(exc)
        self.scrollArea.setWidget(self.contentLabel)
        self.viewLayout.addWidget(self.scrollArea)
        self.yesButton.setText(app.translate("ErrorDialogue", "ErrorDialogue.yesButton"))
        # self.yesButton.pressed.connect(lambda: webbrowser.open("[CMCL_Issue_Report_URL]"))
        self.cancelButton.setText(app.translate("ErrorDialogue", "ErrorDialogue.cancelButton"))


class HomePage(QFrame):
    class LaunchFailedDialogue(MessageBoxBase):
        def __init__(self, parent, reason):
            super().__init__(parent)
            self.titleLabel = TitleLabel(self)
            self.titleLabel.setText(
                app.translate("HomePage.LaunchFailedDialogue", "HomePage.LaunchFailedDialogue.title"))
            self.viewLayout.addWidget(self.titleLabel)
            self.contentLabel = BodyLabel(self)
            self.contentLabel.setText(reason)
            self.viewLayout.addWidget(self.contentLabel)
            self.yesButton.setText(MessageBox.tr("OK"))
            self.cancelButton.setText(MessageBox.tr("Cancel"))
    
    class VersionSettings(QFrame):
        closeSignal = pyqtSignal()
        
        def __init__(self, parent, version):
            super().__init__(parent)
            self.version = version
            self.verticalLayout = QVBoxLayout(self)
            self.verticalLayout.setObjectName(u"verticalLayout")
            self.frame = PillTopBar(self)
            self.frame.setObjectName(u"frame")
            self.horizontalLayout = QHBoxLayout(self.frame)
            self.horizontalLayout.setSpacing(0)
            self.horizontalLayout.setObjectName(u"horizontalLayout")
            self.horizontalLayout.setContentsMargins(3, 4, 3, 3)
            self.toolButton = QToolButton(self.frame)
            self.toolButton.setObjectName(u"toolButton")
            self.toolButton.setStyleSheet("background: transparent; border: none;")
            self.toolButton.pressed.connect(self.closeSignal.emit)
            
            self.horizontalLayout.addWidget(self.toolButton)
            
            self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
            
            self.horizontalLayout.addItem(self.horizontalSpacer)
            
            self.verticalLayout.addWidget(self.frame)
            
            self.toolBox = ToolBox(self)
            self.toolBox.setObjectName(u"toolBox")
            self.page = QWidget()
            self.page.setObjectName(u"page")
            self.page.setGeometry(QRect(0, 0, 412, 270))
            self.verticalLayout_3 = QVBoxLayout(self.page)
            self.verticalLayout_3.setObjectName(u"verticalLayout_3")
            self.toolBox_2 = ToolBox(self.page)
            self.toolBox_2.setObjectName(u"toolBox_2")
            self.page1 = QWidget()
            self.page1.setObjectName(u"page1")
            self.page1.setGeometry(QRect(0, 0, 394, 200))
            self.verticalLayout_4 = QVBoxLayout(self.page1)
            self.verticalLayout_4.setObjectName(u"verticalLayout_4")
            self.horizontalLayout_2 = QHBoxLayout()
            self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
            self.label = BodyLabel(self.page1)
            self.label.setObjectName(u"label")
            
            self.horizontalLayout_2.addWidget(self.label)
            
            self.lineEdit = LineEdit(self.page1)
            self.lineEdit.setObjectName(u"lineEdit")
            
            self.horizontalLayout_2.addWidget(self.lineEdit)
            
            self.verticalLayout_4.addLayout(self.horizontalLayout_2)
            
            self.verticalSpacer = QSpacerItem(20, 152, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
            
            self.verticalLayout_4.addItem(self.verticalSpacer)
            
            self.toolBox_2.addItem(self.page1)
            self.page_2 = QWidget()
            self.page_2.setObjectName(u"page_2")
            self.page_2.setGeometry(QRect(0, 0, 394, 200))
            self.verticalLayout_5 = QVBoxLayout(self.page_2)
            self.verticalLayout_5.setObjectName(u"verticalLayout_5")
            self.horizontalLayout_3 = QHBoxLayout()
            self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
            self.label_2 = BodyLabel(self.page_2)
            self.label_2.setObjectName(u"label_2")
            
            self.horizontalLayout_3.addWidget(self.label_2)
            
            self.lineEdit_2 = LineEdit(self.page_2)
            self.lineEdit_2.setObjectName(u"lineEdit_2")
            
            self.horizontalLayout_3.addWidget(self.lineEdit_2)
            
            self.pushButton = TogglePushButton(self.page_2)
            self.pushButton.setObjectName(u"checkBox")
            
            self.horizontalLayout_3.addWidget(self.pushButton)
            
            self.verticalLayout_5.addLayout(self.horizontalLayout_3)
            
            self.verticalSpacer_2 = QSpacerItem(20, 152, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
            
            self.verticalLayout_5.addItem(self.verticalSpacer_2)
            
            self.toolBox_2.addItem(self.page_2)
            
            self.verticalLayout_3.addWidget(self.toolBox_2)
            
            self.toolBox.addItem(self.page)
            
            self.verticalLayout.addWidget(self.toolBox)
            
            self.pushButton_2 = PushButton(self)
            self.pushButton_2.setObjectName(u"pushButton")
            
            self.verticalLayout.addWidget(self.pushButton_2)
            
            self.retranslateUi()
            
            self.toolBox.setCurrentIndex(0)
            self.toolBox_2.setCurrentIndex(0)
            
            self.acrylic_label = AcrylicLabel(0, QColor(43, 43, 43, 150) if isDarkTheme() else QColor(249, 249, 249,
                                                                                                      150),
                                              QColor(255, 255, 255, 10), parent=self)
            self.acrylic_grabbed = False
            
            QMetaObject.connectSlotsByName(self)
            # setupUi
        
        def retranslateUi(self):
            self.toolButton.setIcon(Icon(FluentIcon.RETURN))
            self.label.setText(
                QCoreApplication.translate("HomePage.VersionSettings", "HomePage.VersionSettings.label.text"))
            self.toolBox_2.setItemText(self.toolBox_2.indexOf(self.page1),
                                       QCoreApplication.translate("HomePage.VersionSettings",
                                                                  "HomePage.VersionSettings.Page1.Page1.title"))
            self.label_2.setText(
                QCoreApplication.translate("HomePage.VersionSettings", "HomePage.VersionSettings.label_2.text"))
            self.pushButton.setText(
                QCoreApplication.translate("HomePage.VersionSettings", "HomePage.VersionSettings.pushButton.text"))
            self.toolBox_2.setItemText(self.toolBox_2.indexOf(self.page_2),
                                       QCoreApplication.translate("HomePage.VersionSettings",
                                                                  "HomePage.VersionSettings.Page1.Page2.title"))
            self.toolBox.setItemText(self.toolBox.indexOf(self.page),
                                     QCoreApplication.translate("HomePage.VersionSettings",
                                                                "HomePage.VersionSettings.Page1.title"))
            self.pushButton_2.setText(
                QCoreApplication.translate("HomePage.VersionSettings", "HomePage.VersionSettings.pushButton_2.text"))
            
            # retranslateUi
        
        def showEvent(self, a0):
            if not self.acrylic_grabbed:
                self.acrylic_label.setImage(
                    self.parent().screen().grabWindow(self.parent().winId(), 0, 0, self.parent().width(),
                                                      self.parent().height()))
                self.acrylic_grabbed = True
        
        def paintEvent(self, a0):
            super().paintEvent(a0)
            painter = QPainter(self)
            painter.fillRect(self.rect(), QColor(43, 43, 43) if isDarkTheme() else QColor(249, 249, 249))
            self.acrylic_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            self.acrylic_label.setTintColor(
                QColor(43, 43, 43, 150) if isDarkTheme() else QColor(249, 249, 249, 150))
            self.acrylic_label.setGeometry(self.rect())
            self.acrylic_label.lower()
            blur = QGraphicsBlurEffect(self)
            blur.setBlurRadius(30)
            self.acrylic_label.setGraphicsEffect(blur)
        
        def event(self, e):
            if hasattr(self, "frame"):
                self.frame.setStyleSheet(
                    f"background: {'rgb(249, 249, 249)' if not isDarkTheme() else 'rgb(43, 43, 43)'};")
            if hasattr(self, "toolButton"):
                self.toolButton.setIcon(Icon(FluentIcon.RETURN))
            return super().event(e)
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("HomePage")
        
        self.version = None
        
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollArea = ScrollArea(self)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.scrollArea.setFrameShadow(QFrame.Shadow.Plain)
        self.scrollArea.setStyleSheet("background: transparent;")
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        
        self.topBar = TopBar(self.scrollAreaWidgetContents)
        
        self.topBar.setObjectName(u"topBar")
        self.topBar.setStyleSheet(
            f"background: {'rgb(249, 249, 249)' if not isDarkTheme() else 'rgb(43, 43, 43)'};")
        self.verticalLayout_3 = QVBoxLayout(self.topBar)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalSpacer = QSpacerItem(180, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        self.horizontalLayout.addItem(self.verticalSpacer)
        
        self.pushButton = PrimaryPushButton(self.topBar)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.pressed.connect(self.start_launch)
        
        self.horizontalLayout.addWidget(self.pushButton)
        
        self.pushButton_2 = SplitPushButton(self.topBar)
        self.pushButton_2.clicked.connect(self.version_settings)
        menu = RoundMenu(None)
        versions = get_version_by_scan_dir(minecraft_path=minecraft_path)
        if isinstance(versions, list):
            self.version = versions[0]
            for i in versions:
                action = QAction(i)
                action.triggered.connect(lambda _, v=i: self.changeVersion(v))
                menu.addAction(action)
        else:
            menu.addAction(
                QAction(app.translate("HomePage", "HomePage.versionNotFound")))
        self.pushButton_2.setFlyout(menu)
        self.pushButton_2.setObjectName(u"pushButton_2")
        
        self.horizontalLayout.addWidget(self.pushButton_2)
        
        self.toolButton = ToolButton(self.topBar)
        self.toolButton.setObjectName(u"toolButton")
        self.toolButton.installEventFilter(ToolTipFilter(self.toolButton, position=ToolTipPosition.BOTTOM))
        self.toolButton.pressed.connect(self.refresh_version)
        
        self.horizontalLayout.addWidget(self.toolButton)
        
        self.verticalSpacer_2 = QSpacerItem(180, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        self.horizontalLayout.addItem(self.verticalSpacer_2)
        
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout")
        self.verticalSpacer_3 = QSpacerItem(180, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        self.horizontalLayout_2.addItem(self.verticalSpacer_3)
        
        self.label = BodyLabel(self.topBar)
        self.label.setObjectName(u"label")
        
        self.horizontalLayout_2.addWidget(self.label)
        
        self.pushButton_3 = PushButton(self.topBar)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.pressed.connect(self.change_Minecraft_dir)
        
        self.horizontalLayout_2.addWidget(self.pushButton_3)
        #
        # self.verticalSpacer_4 = QSpacerItem(180, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        #
        # self.horizontalLayout_2.addItem(self.verticalSpacer_4)
        #
        # self.label_2 = BodyLabel(self.topBar)
        # self.label_2.setObjectName(u"label_2")
        #
        # self.horizontalLayout_2.addWidget(self.label_2)
        
        self.verticalSpacer_5 = QSpacerItem(180, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        self.horizontalLayout_2.addItem(self.verticalSpacer_5)
        
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        
        self.topBar.setLayout(self.verticalLayout_3)
        
        self.verticalLayout_2.addWidget(self.topBar)
        
        self.verticalSpacer_6 = QSpacerItem(20, 186, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        
        self.verticalLayout_2.addItem(self.verticalSpacer_6)
        
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        
        self.verticalLayout.addWidget(self.scrollArea)
        
        self.retranslateUi()
        
        self.version_settings_panel = None
        self.version_settings_panel_anix = None
        self.version_settings_panel_anid = None
        
        QMetaObject.connectSlotsByName(self)
    
    def retranslateUi(self):
        self.pushButton.setText(app.translate("HomePage", u"HomePage.pushButton.text"))
        self.pushButton_2.setText(
            self.version or app.translate("HomePage", u"HomePage.pushButton2.text"))
        self.toolButton.setIcon(FluentIcon.SYNC)
        self.toolButton.setToolTip(app.translate("HomePage", "HomePage.toolButton.toolTip"))
        self.label.setText(
            app.translate("HomePage", u"HomePage.label.text"))
        self.pushButton_3.setText(str(minecraft_path.absolute()))
    
    def changeVersion(self, version):
        self.version = version
        
        self.retranslateUi()
    
    def start_launch(self):
        if not player:
            dialogue = MessageBox(app.translate("HomePage", "HomePage.tiptitle"),
                                  app.translate("HomePage", "HomePage.content1"), frame)
            dialogue.exec()
        else:
            if self.version:
                if not player.player_hasMC:
                    dialogue = MessageBox(app.translate("HomePage", "HomePage.tiptitle"),
                                          app.translate("HomePage", "HomePage.content2"),
                                          frame)
                    dialogue.show()
                result = launch(minecraft_path, self.version, cfg.get(cfg.JavaPath),
                                cfg.get(cfg.JVMLaunchMode),
                                version[0], None, None, None, cfg.get(cfg.extraGameCommand), PIPE, PIPE,
                                player)
                if result[0] == "Unsuccessfully":
                    error_dialogue = self.LaunchFailedDialogue(frame, result[1])
                    error_dialogue.exec()
                if result[0] == "Successfully":
                    InfoBar.info(app.translate("HomePage", "HomePage.tiptitle"),
                                 app.translate("HomePage", "HomePage.content3"),
                                 parent=self)
            else:
                dialogue = MessageBox(app.translate("HomePage", "HomePage.tiptitle"),
                                      app.translate("HomePage", "HomePage.content4"), frame)
                dialogue.exec()
    
    def change_Minecraft_dir(self):
        global minecraft_path
        filedialogue = QFileDialog(self)
        result = filedialogue.getExistingDirectory(self, app.translate("HomePage", "HomePage.selectdir.title"),
                                                   str(minecraft_path))
        if result:
            minecraft_path = Path(result)
            cfg.set(cfg.MinecraftPath, str(minecraft_path))
            menu = RoundMenu(None, self.pushButton_2)
            versions = get_version_by_scan_dir(minecraft_path=minecraft_path)
            if isinstance(versions, list):
                self.version = versions[0]
                for i in versions:
                    action = QAction(i)
                    action.triggered.connect(lambda _, v=i: self.changeVersion(v))
                    menu.addAction(action)
            else:
                menu.addAction(QAction(app.translate("HomePage", "HomePage.versionNotFound")))
                self.version = None
            self.pushButton_2.setFlyout(menu)
        self.retranslateUi()
    
    def refresh_version(self):
        menu = RoundMenu(None, self.pushButton_2)
        versions = get_version_by_scan_dir(minecraft_path=minecraft_path)
        if isinstance(versions, list):
            self.version = versions[0]
            for i in versions:
                action = QAction(i)
                action.triggered.connect(lambda _, v=i: self.changeVersion(v))
                menu.addAction(action)
        else:
            menu.addAction(QAction(app.translate("HomePage", "HomePage.versionNotFound")))
            self.version = None
        self.pushButton_2.setFlyout(menu)
        self.retranslateUi()
    
    def version_settings(self):
        version = self.pushButton_2.text()
        self.version_settings_panel = self.VersionSettings(self, version)
        self.version_settings_panel_anix = self.width()
        self.version_settings_panel_anid = "in"
        self.version_settings_panel.closeSignal.connect(self.close_settings)
        self.version_settings_panel.show()
    
    def close_settings(self):
        self.version_settings_panel_anid = "out"
        self.version_settings_panel_anix = 0
    
    def event(self, e):
        if hasattr(self, "topBar"):
            self.topBar.setStyleSheet(
                f"background: {'rgb(249, 249, 249)' if not isDarkTheme() else 'rgb(43, 43, 43)'};")
        if hasattr(self, "version_settings_panel"):
            if self.version_settings_panel:
                if self.version_settings_panel_anix >= 0 and self.version_settings_panel_anid == "in":
                    self.version_settings_panel_anix -= self.version_settings_panel_anix // 4
                if self.version_settings_panel_anix <= self.width() and self.version_settings_panel_anid == "out":
                    self.version_settings_panel_anix += 100
                if self.version_settings_panel_anix > self.width() and self.version_settings_panel_anid == "out":
                    self.version_settings_panel.deleteLater()
                    self.version_settings_panel = None
                    self.version_settings_panel_anix = None
                if self.version_settings_panel:
                    self.version_settings_panel.setGeometry(self.version_settings_panel_anix or 0, 0, self.width(),
                                                            self.height())
                    self.version_settings_panel.raise_()
        return super().event(e)


class DownloadPage(QFrame):
    class DownloadMinecraft(QFrame):
        class GetVersionThread(QThread):
            gotVersion = pyqtSignal(dict)
            
            def run(self):
                try:
                    response = get_version_by_api(returns="RETURN_JSON")
                    if response:
                        self.gotVersion.emit({"status": "successfully", "result": response})
                    else:
                        self.gotVersion.emit({"status": "failed", "result": None})
                except:
                    self.gotVersion.emit({"status": "failed", "result": None})
        
        class DownloadVersion(QFrame):
            class DownloadVersionThread(QThread):
                def __init__(self, parent, version=None, minecraft_path=".", state_tooltip=None):
                    super().__init__(parent)
                    self.version = version
                    self.minecraft_path = Path(minecraft_path)
                    self.state_tooltip = state_tooltip
                
                def run(self):
                    if self.version:
                        download_game(version=self.version, minecraft_path=self.minecraft_path)
                    if self.state_tooltip:
                        self.state_tooltip.setState(True)
            
            closeSignal = pyqtSignal()
            
            def __init__(self, parent, version_name):
                super().__init__(parent)
                self.version = version_name
                self.verticalLayout = QVBoxLayout(self)
                self.verticalLayout.setObjectName(u"verticalLayout")
                self.frame = PillTopBar(self)
                self.frame.setObjectName(u"frame")
                self.horizontalLayout = QHBoxLayout(self.frame)
                self.horizontalLayout.setSpacing(0)
                self.horizontalLayout.setObjectName(u"horizontalLayout")
                self.horizontalLayout.setContentsMargins(3, 4, 3, 3)
                self.toolButton = QToolButton(self.frame)
                self.toolButton.setObjectName(u"toolButton")
                self.toolButton.setStyleSheet("background: transparent; border: none;")
                self.toolButton.pressed.connect(self.closeSignal.emit)
                
                self.horizontalLayout.addWidget(self.toolButton)
                
                self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
                
                self.horizontalLayout.addItem(self.horizontalSpacer)
                
                self.verticalLayout.addWidget(self.frame)
                
                self.scrollArea = ScrollArea(self)
                self.scrollArea.setObjectName(u"scrollArea")
                self.scrollArea.setWidgetResizable(True)
                self.scrollArea.setFrameShape(QFrame.Shape.NoFrame)
                self.scrollArea.setFrameShadow(QFrame.Shadow.Plain)
                self.scrollAreaWidgetContents = QWidget()
                self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
                self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
                self.verticalLayout_2.setObjectName(u"verticalLayout_2")
                self.toolBox = ToolBox(self.scrollAreaWidgetContents)
                self.toolBox.setObjectName(u"toolBox")
                self.page = QWidget()
                self.page.setObjectName(u"page")
                self.verticalLayout_3 = QVBoxLayout(self.page)
                self.verticalLayout_3.setObjectName(u"verticalLayout_3")
                self.horizontalLayout_3 = QHBoxLayout()
                self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
                self.label_2 = BodyLabel(self.page)
                self.label_2.setObjectName(u"label_2")
                
                self.horizontalLayout_3.addWidget(self.label_2)
                
                self.pushButton_2 = PushButton(self.page)
                self.pushButton_2.setObjectName(u"pushButton_2")
                sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
                sizePolicy.setHorizontalStretch(1)
                sizePolicy.setVerticalStretch(0)
                sizePolicy.setHeightForWidth(self.pushButton_2.sizePolicy().hasHeightForWidth())
                self.pushButton_2.setSizePolicy(sizePolicy)
                # self.pushButton_2.setStyleSheet("background: transparent")
                
                self.horizontalLayout_3.addWidget(self.pushButton_2)
                
                self.verticalLayout_3.addLayout(self.horizontalLayout_3)
                
                self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
                
                self.verticalLayout_3.addItem(self.verticalSpacer)
                
                self.toolBox.addItem(self.page)
                
                self.page_2 = QWidget()
                self.page_2.setObjectName(u"page_2")
                self.verticalLayout_4 = QVBoxLayout(self.page_2)
                self.verticalLayout_4.setObjectName(u"verticalLayout_4")
                self.horizontalLayout_2 = QHBoxLayout()
                self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
                self.label = BodyLabel(self.page_2)
                self.label.setObjectName(u"label")
                
                self.horizontalLayout_2.addWidget(self.label)
                
                self.lineEdit = LineEdit(self.page_2)
                self.lineEdit.setObjectName(u"lineEdit")
                self.lineEdit.setText(str(minecraft_path.absolute()))
                
                self.horizontalLayout_2.addWidget(self.lineEdit)
                
                self.pushButton_3 = PushButton(self.page_2)
                self.pushButton_3.setObjectName(u"pushButton_3")
                self.pushButton_3.pressed.connect(self.explore_path)
                
                self.horizontalLayout_2.addWidget(self.pushButton_3)
                
                self.verticalLayout_4.addLayout(self.horizontalLayout_2)
                
                self.label_3 = BodyLabel(self.page_2)
                self.label_3.setObjectName(u"label_3")
                
                self.verticalLayout_4.addWidget(self.label_3)
                
                self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
                
                self.verticalLayout_4.addItem(self.verticalSpacer_2)
                
                self.verticalLayout_2.addWidget(self.toolBox)
                
                self.scrollArea.setWidget(self.scrollAreaWidgetContents)
                
                self.verticalLayout.addWidget(self.scrollArea)
                
                self.pushButton = PrimaryPushButton(self)
                self.pushButton.setObjectName(u"pushButton")
                self.pushButton.pressed.connect(self.download_minecraft)
                
                self.verticalLayout.addWidget(self.pushButton)
                
                self.toolBox.addItem(self.page_2)
                
                self.retranslateUi()
                
                self.toolBox.setCurrentIndex(0)
                
                self.acrylic_label = AcrylicLabel(0, QColor(43, 43, 43, 150) if isDarkTheme() else QColor(249, 249, 249,
                                                                                                          150),
                                                  QColor(255, 255, 255, 10), parent=self)
                self.acrylic_grabbed = False
                # self.image = None
                
                QMetaObject.connectSlotsByName(self)
            
            def retranslateUi(self):
                self.toolButton.setIcon(Icon(FluentIcon.RETURN))
                self.label_2.setText(
                    app.translate("DownloadPage.DownloadMinecraft.DownloadVersion",
                                  "DownloadPage.DownloadMinecraft.DownloadVersion.label_2.text"))
                self.pushButton_2.setText(self.version)
                self.toolBox.setItemText(self.toolBox.indexOf(self.page),
                                         app.translate("DownloadPage.DownloadMinecraft.DownloadVersion",
                                                       "DownloadPage.DownloadMinecraft.DownloadVersion.Page1.title",
                                                       ))
                self.label.setText(
                    app.translate("DownloadPage.DownloadMinecraft.DownloadVersion",
                                  "DownloadPage.DownloadMinecraft.DownloadVersion.label.text"))
                self.lineEdit.setText(str(minecraft_path.absolute()))
                self.pushButton_3.setText(app.translate("DownloadPage.DownloadMinecraft.DownloadVersion",
                                                        u"DownloadPage.DownloadMinecraft.DownloadVersion.pushButton_3.text",
                                                        ))
                self.label_3.setText(app.translate("DownloadPage.DownloadMinecraft.DownloadVersion",
                                                   "DownloadPage.DownloadMinecraft.DownloadVersion.label_3.text"))
                self.toolBox.setItemText(self.toolBox.indexOf(self.page_2),
                                         app.translate("DownloadPage.DownloadMinecraft.DownloadVersion",
                                                       "DownloadPage.DownloadMinecraft.DownloadVersion.Page2.title",
                                                       ))
                self.pushButton.setText(app.translate("DownloadPage.DownloadMinecraft.DownloadVersion",
                                                      "DownloadPage.DownloadMinecraft.DownloadVersion.pushButton.text",
                                                      ))
            
            def showEvent(self, a0):
                if not self.acrylic_grabbed:
                    self.acrylic_label.setImage(
                        self.parent().screen().grabWindow(self.parent().winId(), 0, 0, self.parent().width(),
                                                          self.parent().height()))
                    self.acrylic_grabbed = True
            
            #         self.image = self.acrylic_brush.image
            #
            # def moveEvent(self, a0):
            #     if self.image:
            #         self.acrylic_brush.setImage(
            #             self.image.copy(QRect(-self.x(), 0, self.image.width() + self.x(), self.image.height())))
            
            def paintEvent(self, a0):
                super().paintEvent(a0)
                painter = QPainter(self)
                painter.fillRect(self.rect(), QColor(43, 43, 43) if isDarkTheme() else QColor(249, 249, 249))
                self.acrylic_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
                self.acrylic_label.setTintColor(
                    QColor(43, 43, 43, 150) if isDarkTheme() else QColor(249, 249, 249, 150))
                # self.acrylic_label.setImage(self.acrylic_brush.image)
                self.acrylic_label.setGeometry(self.rect())
                self.acrylic_label.lower()
                blur = QGraphicsBlurEffect(self)
                blur.setBlurRadius(30)
                self.acrylic_label.setGraphicsEffect(blur)
            
            def event(self, e):
                if hasattr(self, "frame"):
                    self.frame.setStyleSheet(
                        f"background: {'rgb(249, 249, 249)' if not isDarkTheme() else 'rgb(43, 43, 43)'};")
                if hasattr(self, "toolButton"):
                    self.toolButton.setIcon(Icon(FluentIcon.RETURN))
                return super().event(e)
            
            def explore_path(self):
                path = QFileDialog.getExistingDirectory(self,
                                                        app.translate("DownloadPage.DownloadMinecraft.DownloadVersion",
                                                                      "DownloadPage.DownloadMinecraft.DownloadVersion.selectdir.title"),
                                                        str(minecraft_path))
                if path:
                    self.lineEdit.setText(path)
            
            def download_minecraft(self):
                version = self.pushButton_2.text()
                path = self.lineEdit.text()
                print(version, path)
                state_tooltip = StateToolTip("正在下载中", "请稍等", parent=frame)
                pos = state_tooltip.getSuitablePos()
                state_tooltip.move(pos)
                state_tooltip.show()
                self.DownloadVersionThread(frame, version, path, state_tooltip).start()
                # download_game(version=version, minecraft_path=path)
                self.closeSignal.emit()
        
        def __init__(self, parent=None):
            super().__init__(parent)
            self.verticalLayout_2 = QVBoxLayout(self)
            self.verticalLayout_2.setObjectName(u"verticalLayout_2")
            self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
            self.scrollArea = ScrollArea(self)
            self.scrollArea.setObjectName(u"scrollArea")
            self.scrollArea.setWidgetResizable(True)
            self.scrollArea.setFrameShape(QFrame.Shape.NoFrame)
            self.scrollArea.setFrameShadow(QFrame.Shadow.Plain)
            self.scrollAreaWidgetContents = QWidget()
            self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
            self.verticalLayout_3 = QVBoxLayout(self.scrollAreaWidgetContents)
            self.verticalLayout_3.setObjectName(u"verticalLayout_3")
            self.lineEdit = LineEdit(self.scrollAreaWidgetContents)
            self.lineEdit.setObjectName(u"lineEdit")
            self.lineEdit.installEventFilter(ToolTipFilter(self.lineEdit, position=ToolTipPosition.BOTTOM))
            self.lineEdit.textChanged.connect(self.searchVersion)
            
            self.verticalLayout_3.addWidget(self.lineEdit)
            
            self.tableView = TableView(self.scrollAreaWidgetContents)
            self.tableView.setObjectName(u"listWidget")
            self.tableView.setSelectionMode(QTableView.SelectionMode.SingleSelection)
            self.tableView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            self.tableView.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.tableView.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
            self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.tableView.horizontalHeader().setVisible(True)
            self.tableView.verticalHeader().setVisible(False)
            self.tableView.clicked.connect(self.turn_to_download_page)
            self.versionModel = QStandardItemModel(self.tableView)
            self.versionModel.setHorizontalHeaderLabels(
                [app.translate("DownloadPage.DownloadMinecraft", "DownloadPage.DownloadMinecraft.TabelHeader.1"),
                 app.translate("DownloadPage.DownloadMinecraft", "DownloadPage.DownloadMinecraft.TabelHeader.2"),
                 app.translate("DownloadPage.DownloadMinecraft",
                               "DownloadPage.DownloadMinecraft.TabelHeader.3")])
            self.tableView.setModel(self.versionModel)
            self.versions = {}
            self.tableView.setSelectionMode(QTableView.SelectionMode.SingleSelection)
            self.tableView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            self.tableView.horizontalHeader().setVisible(True)
            self.tableView.verticalHeader().setVisible(False)
            
            self.verticalLayout_3.addWidget(self.tableView)
            
            self.scrollArea.setWidget(self.scrollAreaWidgetContents)
            
            self.verticalLayout_2.addWidget(self.scrollArea)
            
            self.retranslateUi()
            
            QMetaObject.connectSlotsByName(self)
            
            self.splash = None
            self.version_download = None
            self.version_download_anid = None
            self.version_download_anix = None
        
        def retranslateUi(self):
            self.lineEdit.setPlaceholderText(
                app.translate("DownloadPage.DownloadMinecraft",
                              "DownloadPage.DownloadMinecraft.lineEdit.placeHolder"))
            self.lineEdit.setToolTip(
                app.translate("DownloadPage.DownloadMinecraft", "DownloadPage.DownloadMinecraft.lineEdit.toolTip"))
            self.versionModel.setHorizontalHeaderLabels(
                [app.translate("DownloadPage.DownloadMinecraft", "DownloadPage.DownloadMinecraft.TabelHeader.1"),
                 app.translate("DownloadPage.DownloadMinecraft", "DownloadPage.DownloadMinecraft.TabelHeader.2"),
                 app.translate("DownloadPage.DownloadMinecraft",
                               "DownloadPage.DownloadMinecraft.TabelHeader.3")])
        
        def event(self, e):
            if hasattr(self, "version_download"):
                if self.version_download:
                    if self.version_download_anix >= 0 and self.version_download_anid == "in":
                        self.version_download_anix -= self.version_download_anix // 4
                    if self.version_download_anix <= self.width() and self.version_download_anid == "out":
                        self.version_download_anix += 100
                    if self.version_download_anix > self.width() and self.version_download_anid == "out":
                        self.version_download.deleteLater()
                        self.version_download = None
                        self.version_download_anix = None
                    if self.version_download:
                        self.version_download.setGeometry(self.version_download_anix or 0, 0, self.width(),
                                                          self.height())
                        self.version_download.raise_()
            if hasattr(self, "groupBox"):
                self.groupBox.setPalette(self.label.palette())
            return super().event(e)
        
        def showEvent(self, *args, **kwargs):
            super().showEvent(*args, **kwargs)
            if not self.versions:
                t = self.GetVersionThread(self)
                t.gotVersion.connect(self.displayVersion)
                t.start()
                self.startSplash()
        
        def startSplash(self):
            self.splash = LoadingSvgSplash(self)
            self.splash.start()
        
        def finishSplash(self, success=True):
            if self.splash:
                self.splash.finish(not success)
        
        def displayVersion(self, data):
            if data["status"] == "successfully":
                data = data["result"]
                self.finishSplash()
                completer_l = []
                for e, i in enumerate(data["versions"]):
                    version = i["id"]
                    version_type_real = i["type"]
                    match version_type_real:
                        case "release":
                            version_type = app.translate("DownloadPage.DownloadMinecraft",
                                                         "DownloadPage.DownloadMinecraft.Type.release")
                        case "snapshot":
                            version_type = app.translate("DownloadPage.DownloadMinecraft",
                                                         "DownloadPage.DownloadMinecraft.Type.snapshot")
                        case "old_beta":
                            version_type = app.translate("DownloadPage.DownloadMinecraft",
                                                         "DownloadPage.DownloadMinecraft.Type.old_beta")
                        case "old_alpha":
                            version_type = app.translate("DownloadPage.DownloadMinecraft",
                                                         "DownloadPage.DownloadMinecraft.Type.old_alpha")
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
                        version_type = app.translate("DownloadPage.DownloadMinecraft",
                                                     "DownloadPage.DownloadMinecraft.Type.april_fool")
                        version_type_real = "april_fool"
                    for e2, i2 in enumerate([version, version_type, release_time]):
                        self.versionModel.setItem(e, e2, QStandardItem(i2))
                    self.versions[version] = {"VersionId": version, "VersionType": version_type_real,
                                              "releaseTime": release_time}
                    completer_l.append(version)
                self.lineEdit.setCompleter(QCompleter(completer_l, self.lineEdit))
                self.versionModel.setHorizontalHeaderLabels(
                    [app.translate("DownloadPage.DownloadMinecraft", "DownloadPage.DownloadMinecraft.TabelHeader.1"),
                     app.translate("DownloadPage.DownloadMinecraft", "DownloadPage.DownloadMinecraft.TabelHeader.2"),
                     app.translate("DownloadPage.DownloadMinecraft",
                                   "DownloadPage.DownloadMinecraft.TabelHeader.3")])
                self.tableView.setModel(self.versionModel)
                self.tableView.setSelectionMode(QTableView.SelectionMode.SingleSelection)
                self.tableView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
                self.tableView.horizontalHeader().setVisible(True)
                self.tableView.verticalHeader().setVisible(False)
            else:
                self.finishSplash(False)
        
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
                            version_type = app.translate("DownloadPage.DownloadMinecraft",
                                                         "DownloadPage.DownloadMinecraft.Type.release")
                        case "snapshot":
                            version_type = app.translate("DownloadPage.DownloadMinecraft",
                                                         "DownloadPage.DownloadMinecraft.Type.snapshot")
                        case "old_beta":
                            version_type = app.translate("DownloadPage.DownloadMinecraft",
                                                         "DownloadPage.DownloadMinecraft.Type.old_beta")
                        case "old_alpha":
                            version_type = app.translate("DownloadPage.DownloadMinecraft",
                                                         "DownloadPage.DownloadMinecraft.Type.old_alpha")
                        case _:
                            version_type = version_type
                    release_time = value["releaseTime"]
                    time_1 = datetime.datetime.strptime(release_time, "%Y-%m-%d %H:%M:%S")
                    if time_1.month == 4 and time_1.day == 1:
                        version_type = app.translate("DownloadPage.DownloadMinecraft",
                                                     "DownloadPage.DownloadMinecraft.Type.april_fool")
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
                            version_type = app.translate("DownloadPage.DownloadMinecraft",
                                                         "DownloadPage.DownloadMinecraft.Type.release")
                            latest_release = True
                        case "snapshot":
                            if latest_snapshot:
                                continue
                            version_type = app.translate("DownloadPage.DownloadMinecraft",
                                                         "DownloadPage.DownloadMinecraft.Type.snapshot")
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
                                    version_type = app.translate("DownloadPage.DownloadMinecraft",
                                                                 "DownloadPage.DownloadMinecraft.Type.release")
                                case "snapshot":
                                    version_type = app.translate("DownloadPage.DownloadMinecraft",
                                                                 "DownloadPage.DownloadMinecraft.Type.snapshot")
                                case "old_beta":
                                    version_type = app.translate("DownloadPage.DownloadMinecraft",
                                                                 "DownloadPage.DownloadMinecraft.Type.old_beta")
                                case "old_alpha":
                                    version_type = app.translate("DownloadPage.DownloadMinecraft",
                                                                 "DownloadPage.DownloadMinecraft.Type.old_alpha")
                                case _:
                                    version_type = version_type
                            release_time = value["releaseTime"]
                            time_1 = datetime.datetime.strptime(release_time, "%Y-%m-%d %H:%M:%S")
                            if time_1.month == 4 and time_1.day == 1:
                                version_type = app.translate("DownloadPage.DownloadMinecraft",
                                                             "DownloadPage.DownloadMinecraft.Type.april_fool")
                            for e2, i2 in enumerate([version, version_type, release_time]):
                                self.versionModel.setItem(i, e2, QStandardItem(i2))
                            i += 1
                    except re.error:
                        pass
            self.versionModel.setHorizontalHeaderLabels(
                [app.translate("DownloadPage.DownloadMinecraft", "DownloadPage.DownloadMinecraft.TabelHeader.1"),
                 app.translate("DownloadPage.DownloadMinecraft", "DownloadPage.DownloadMinecraft.TabelHeader.2"),
                 app.translate("DownloadPage.DownloadMinecraft",
                               "DownloadPage.DownloadMinecraft.TabelHeader.3")])
            self.tableView.setModel(self.versionModel)
            self.tableView.setSelectionMode(QTableView.SelectionMode.SingleSelection)
            self.tableView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            self.tableView.horizontalHeader().setVisible(True)
            self.tableView.verticalHeader().setVisible(False)
        
        def turn_to_download_page(self, value):
            print(self.tableView.model().item(value.row(), 0).text())
            try:
                row = self.tableView.selectionModel().selectedRows()[0]
                data = self.tableView.model().itemData(row)[0]
            except IndexError:
                print(self.tableView.selectionModel().selectedRows()[0], self.tableView.model().itemData(row)[0])
            self.version_download = self.DownloadVersion(self, data)
            self.version_download_anid = "in"
            self.version_download_anix = self.width()
            self.version_download.closeSignal.connect(self.turn_back)
            self.version_download.show()
        
        def turn_back(self):
            self.version_download_anid = "out"
            self.version_download_anix = 0
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("DownloadPage")
        self.setStyleSheet("background: transparent")
        
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.scrollArea = ScrollArea(self)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.scrollArea.setFrameShadow(QFrame.Shadow.Plain)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.verticalLayout_2 = QVBoxLayout(self)
        self.verticalLayout_2.setObjectName(u"verticalLayout")
        self.toolBox = ToolBox(self.scrollAreaWidgetContents)
        self.toolBox.setObjectName(u"toolBox")
        self.page = self.DownloadMinecraft()
        self.page.setObjectName(u"page")
        self.toolBox.addItem(self.page)
        
        self.verticalLayout_2.addWidget(self.toolBox)
        
        self.scrollAreaWidgetContents.setLayout(self.verticalLayout_2)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)
        
        self.retranslateUi()
        
        self.toolBox.setCurrentIndex(0)
        
        QMetaObject.connectSlotsByName(self)
    
    def retranslateUi(self):
        self.toolBox.setItemText(self.toolBox.indexOf(self.page),
                                 app.translate("DownloadPage", u"DownloadPage.Page1.title"))
    
    def event(self, e):
        return super().event(e)


class MultiplayerPage(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("MultiplayerPage")


class ToolsPage(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("ToolsPage")


class SettingsPage(QFrame):
    class LaunchSettings(QFrame):
        class SearchJava(QThread):
            finishDisplay = pyqtSignal()
            
            def run(self):
                self.parent().lineEdit_2.clear()
                import subprocess
                try:
                    java_path = subprocess.check_output(
                        ["which" if get_os.getOperationSystemName()[0] != "Windows" else "where", "java"],
                        stderr=subprocess.STDOUT,
                        creationflags=subprocess.CREATE_NO_WINDOW).decode().splitlines()
                except subprocess.CalledProcessError:
                    try:
                        version_data = \
                            subprocess.check_output([java_path, "-version"], stderr=subprocess.STDOUT,
                                                    creationflags=subprocess.CREATE_NO_WINDOW).decode().splitlines()[
                                0].split(
                                " ")[1]
                    except subprocess.CalledProcessError:
                        self.parent().lineEdit_2.addItem(
                            app.translate("SettingsPage.LaunchSettings.SearchJava",
                                          "SettingsPage.LaunchSettings.NoJava"))
                    else:
                        if len(java_path) >= 2 and not java_path[-1]:
                            del java_path[-1]
                        if Path(java_path[0]).exists():
                            for i in java_path:
                                if Path(i).is_file():
                                    try:
                                        version_data = \
                                            subprocess.check_output([i, "--version"], stderr=subprocess.STDOUT,
                                                                    creationflags=subprocess.CREATE_NO_WINDOW).decode().splitlines()[
                                                0].split(
                                                " ")[1]
                                    except subprocess.CalledProcessError:
                                        pass
                                    else:
                                        self.parent().lineEdit_2.addItem(f"\"{i}\" ({version_data})")
                        else:
                            self.parent().lineEdit_2.addItem(
                                app.translate("SettingsPage.LaunchSettings.SearchJava",
                                              "SettingsPage.LaunchSettings.NoJava"))
                
                else:
                    if len(java_path) >= 2 and not java_path[-1]:
                        del java_path[-1]
                    if Path(java_path[0]).exists():
                        for i in java_path:
                            if Path(i).is_file():
                                try:
                                    version_data = \
                                        subprocess.check_output([i, "--version"], stderr=subprocess.STDOUT,
                                                                creationflags=subprocess.CREATE_NO_WINDOW).decode().splitlines()[
                                            0].split(
                                            " ")[1]
                                except subprocess.CalledProcessError:
                                    pass
                                else:
                                    self.parent().lineEdit_2.addItem(f"\"{i}\" ({version_data})")
                    else:
                        self.parent().lineEdit_2.addItem(
                            app.translate("SettingsPage.LaunchSettings.SearchJava",
                                          "SettingsPage.LaunchSettings.NoJava"))
                finally:
                    self.finishDisplay.emit()
        
        def __init__(self, parent=None):
            super().__init__(parent)
            
            self.verticalLayout = QVBoxLayout(self)
            self.verticalLayout.setObjectName(u"verticalLayout")
            self.scrollArea = ScrollArea(self)
            self.scrollArea.setObjectName(u"scrollArea")
            self.scrollArea.setWidgetResizable(True)
            self.scrollArea.setFrameShape(QFrame.Shape.NoFrame)
            self.scrollArea.setFrameShadow(QFrame.Shadow.Plain)
            self.scrollAreaWidgetContents = QWidget()
            self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
            self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
            self.verticalLayout_2.setObjectName(u"verticalLayout_2")
            self.toolBox = ToolBox(self.scrollAreaWidgetContents)
            self.toolBox.setObjectName(u"toolBox")
            self.page = QWidget()
            self.page.setObjectName(u"page")
            self.verticalLayout_3 = QVBoxLayout(self.page)
            self.verticalLayout_3.setObjectName(u"verticalLayout_3")
            self.horizontalLayout = QHBoxLayout()
            self.horizontalLayout.setObjectName(u"horizontalLayout")
            self.label = BodyLabel(self.page)
            self.label.setObjectName(u"label")
            
            self.horizontalLayout.addWidget(self.label)
            
            self.lineEdit = LineEdit(self.page)
            self.lineEdit.setObjectName(u"lineEdit")
            command_font = QFont("Consolas", 13)
            self.lineEdit.setFont(command_font)
            self.lineEdit.setClearButtonEnabled(True)
            self.lineEdit.setText(cfg.get(cfg.extraGameCommand))
            self.lineEdit.textEdited.connect(self.update_command_text)
            
            self.horizontalLayout.addWidget(self.lineEdit)
            
            self.verticalLayout_3.addLayout(self.horizontalLayout)
            
            self.groupBox = GroupBox(self.page)
            self.groupBox.setObjectName(u"groupBox")
            self.gridLayout = QGridLayout(self.groupBox)
            self.gridLayout.setObjectName(u"gridLayout")
            self.checkBox = CheckBox(self.groupBox)
            self.checkBox.setObjectName(u"checkBox")
            self.checkBox.stateChanged.connect(lambda value, text="-demo": self.update_example_text(text, value))
            
            self.gridLayout.addWidget(self.checkBox, 1, 0, 1, 1)
            
            self.checkBox_2 = CheckBox(self.groupBox)
            self.checkBox_2.setObjectName(u"checkBox_2")
            self.checkBox_2.stateChanged.connect(
                lambda value, text="-fullscreen": self.update_example_text(text, value))
            
            self.gridLayout.addWidget(self.checkBox_2, 2, 0, 1, 1)
            
            self.update_example_state(self.lineEdit.text())
            
            self.verticalLayout_3.addWidget(self.groupBox)
            
            self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
            
            self.verticalLayout_3.addItem(self.verticalSpacer)
            
            self.toolBox.addItem(self.page)
            self.page_2 = QWidget()
            self.page_2.setObjectName(u"page_2")
            self.verticalLayout_4 = QVBoxLayout(self.page_2)
            self.verticalLayout_4.setObjectName(u"verticalLayout_4")
            self.groupBox_2 = GroupBox(self.page_2)
            self.groupBox_2.setObjectName(u"groupBox_2")
            self.horizontalLayout_3 = QHBoxLayout(self.groupBox_2)
            self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
            self.radioButton = RadioButton(self.groupBox_2)
            self.radioButton.setObjectName(u"radioButton")
            self.radioButton.setChecked(cfg.get(cfg.JVMLaunchMode) == "client")
            self.radioButton.toggled.connect(
                lambda value, change_mode="client": self.change_jvm_mode(change_mode, value))
            
            self.horizontalLayout_3.addWidget(self.radioButton)
            
            self.radioButton_2 = RadioButton(self.groupBox_2)
            self.radioButton_2.setObjectName(u"radioButton_2")
            self.radioButton_2.setChecked(cfg.get(cfg.JVMLaunchMode) == "server")
            self.radioButton_2.toggled.connect(
                lambda value, change_mode="server": self.change_jvm_mode(change_mode, value))
            
            self.horizontalLayout_3.addWidget(self.radioButton_2)
            
            self.verticalLayout_4.addWidget(self.groupBox_2)
            
            self.horizontalLayout_7 = QHBoxLayout()
            
            self.label_3 = BodyLabel(self.page_2)
            
            self.horizontalLayout_7.addWidget(self.label_3)
            
            self.lineEdit_2 = ComboBox(self.page_2)
            match cfg.get(cfg.JavaIsAutoSearch):
                case True:
                    cfg.set(cfg.JavaPath, None)
                    self.lineEdit_2.clear()
                    self.lineEdit_2.setText(
                        app.translate("SettingsPage.LaunchSettings",
                                      "SettingsPage.LaunchSettings.AutoSearchJava"))
                    self.lineEdit_2.setEnabled(False)
                case False:
                    self.lineEdit_2.setEnabled(True)
                    sj = self.SearchJava(self)
                    sj.finishDisplay.connect(self.set_java_path)
                    sj.start()
            
            self.horizontalLayout_7.addWidget(self.lineEdit_2, 1)
            
            self.pushButton = TogglePushButton(self.page_2)
            self.pushButton.setChecked(cfg.get(cfg.JavaIsAutoSearch))
            self.pushButton.toggled.connect(self.change_java)
            
            self.horizontalLayout_7.addWidget(self.pushButton)
            
            self.verticalLayout_4.addLayout(self.horizontalLayout_7)
            
            self.pushButton_2 = PushButton(self.page_2)
            self.pushButton_2.pressed.connect(self.manual_apply_java)
            
            self.verticalLayout_4.addWidget(self.pushButton_2)
            
            self.infoBar = InfoBar.warning("", "", isClosable=False, duration=-1, parent=self,
                                           position=InfoBarPosition.TOP)
            self.infoBar.setObjectName(u"widget")
            
            self.verticalLayout_4.addWidget(self.infoBar)
            
            self.horizontalLayout_2 = QHBoxLayout()
            self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
            self.label_2 = BodyLabel(self.page_2)
            self.label_2.setObjectName(u"label_2")
            
            self.horizontalLayout_2.addWidget(self.label_2)
            
            self.lineEdit_3 = LineEdit(self.page_2)
            self.lineEdit_3.setObjectName(u"lineEdit_2")
            self.lineEdit_3.setFont(command_font)
            
            self.horizontalLayout_2.addWidget(self.lineEdit_3)
            
            self.pushButton_3 = TogglePushButton(self.page_2)
            self.pushButton_3.setObjectName(u"checkBox_3")
            self.pushButton_3.toggled.connect(self.set_jvm_args_mode)
            
            self.horizontalLayout_2.addWidget(self.pushButton_3)
            
            self.verticalLayout_4.addLayout(self.horizontalLayout_2)
            
            self.verticalSpacer_2 = QSpacerItem(20, 141, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
            
            self.verticalLayout_4.addItem(self.verticalSpacer_2)
            
            self.toolBox.addItem(self.page_2)
            self.page_3 = QWidget()
            self.page_3.setObjectName(u"page_3")
            self.verticalLayout_5 = QVBoxLayout(self.page_3)
            self.verticalLayout_5.setObjectName(u"verticalLayout_5")
            self.horizontalLayout_4 = QHBoxLayout()
            self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
            self.radioButton_3 = RadioButton(self.page_3)
            self.radioButton_3.setObjectName(u"radioButton_3")
            self.radioButton_3.setChecked(True)
            
            self.horizontalLayout_4.addWidget(self.radioButton_3)
            
            self.radioButton_4 = RadioButton(self.page_3)
            self.radioButton_4.setObjectName(u"radioButton_4")
            
            self.horizontalLayout_4.addWidget(self.radioButton_4)
            
            self.verticalLayout_5.addLayout(self.horizontalLayout_4)
            
            self.horizontalLayout_5 = QHBoxLayout()
            self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
            self.horizontalSlider = Slider(self.page_3)
            self.horizontalSlider.setObjectName(u"horizontalSlider")
            self.horizontalSlider.setMaximum(psutil.virtual_memory().total // 1024 // 1024)
            self.horizontalSlider.setOrientation(Qt.Orientation.Horizontal)
            self.horizontalSlider.valueChanged.connect(self.update_digit)
            
            self.horizontalLayout_5.addWidget(self.horizontalSlider)
            
            self.lcdNumber = QLCDNumber(self.page_3)
            self.lcdNumber.setObjectName(u"lcdNumber")
            self.lcdNumber.setFrameShape(QFrame.Shape.NoFrame)
            self.lcdNumber.setFrameShadow(QFrame.Shadow.Plain)
            self.lcdNumber.setDigitCount(0)
            
            self.horizontalLayout_5.addWidget(self.lcdNumber)
            
            self.label_4 = BodyLabel(self.page_3)
            self.label_4.setObjectName(u"label_4")
            
            self.horizontalLayout_5.addWidget(self.label_4)
            
            self.lcdNumber_2 = QLCDNumber(self.page_3)
            self.lcdNumber_2.setObjectName(u"lcdNumber_2")
            self.lcdNumber_2.setFrameShape(QFrame.Shape.NoFrame)
            self.lcdNumber_2.setFrameShadow(QFrame.Shadow.Plain)
            self.lcdNumber_2.setDigitCount(0)
            
            self.horizontalLayout_5.addWidget(self.lcdNumber_2)
            
            self.label_5 = BodyLabel(self.page_3)
            self.label_5.setObjectName(u"label_6")
            
            self.horizontalLayout_5.addWidget(self.label_5)
            
            self.verticalLayout_5.addLayout(self.horizontalLayout_5)
            
            self.horizontalLayout_6 = QHBoxLayout()
            self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
            self.label_6 = BodyLabel(self.page_3)
            self.label_6.setObjectName(u"label_5")
            
            self.horizontalLayout_6.addWidget(self.label_6)
            
            self.lineEdit_4 = LineEdit(self.page_3)
            self.lineEdit_4.setObjectName(u"lineEdit_3")
            validator = QRegularExpressionValidator(self.lineEdit_4)
            validator.setRegularExpression(QRegularExpression(r"\d+"))
            self.lineEdit_4.setValidator(validator)
            self.lineEdit_4.setText("0")
            self.lineEdit_4.textEdited.connect(self.update_text)
            
            self.horizontalLayout_6.addWidget(self.lineEdit_4)
            
            self.verticalLayout_5.addLayout(self.horizontalLayout_6)
            
            self.verticalSpacer_3 = QSpacerItem(20, 160, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
            
            self.verticalLayout_5.addItem(self.verticalSpacer_3)
            
            self.toolBox.addItem(self.page_3)
            self.page_4 = QWidget()
            self.page_4.setObjectName(u"page_4")
            self.verticalLayout_6 = QVBoxLayout(self.page_4)
            self.verticalLayout_6.setObjectName(u"verticalLayout_6")
            self.widget_2 = InfoBar.info("提示",
                                         "这里会包括 Minecraft 启动或游玩的一些高级设置或实验性功能",
                                         isClosable=False, duration=-1,
                                         parent=self.page_4, position=InfoBarPosition.TOP)
            self.widget_2.setObjectName(u"widget_2")
            
            self.verticalLayout_6.addWidget(self.widget_2)
            
            self.verticalSpacer_4 = QSpacerItem(20, 236, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
            
            self.verticalLayout_6.addItem(self.verticalSpacer_4)
            
            self.toolBox.addItem(self.page_4)
            
            self.verticalLayout_2.addWidget(self.toolBox)
            
            self.scrollArea.setWidget(self.scrollAreaWidgetContents)
            
            self.verticalLayout.addWidget(self.scrollArea)
            
            self.retranslateUi()
            
            self.toolBox.setCurrentIndex(0)
            
            QMetaObject.connectSlotsByName(self)
        
        def retranslateUi(self):
            self.label.setText(
                app.translate("SettingsPage.LaunchSettings", "SettingsPage.LaunchSettings.label.text"))
            self.groupBox.setTitle(
                app.translate("SettingsPage.LaunchSettings", "SettingsPage.LaunchSettings.groupBox.title"))
            self.checkBox.setText(
                app.translate("SettingsPage.LaunchSettings", "SettingsPage.LaunchSettings.checkBox.text"))
            self.checkBox_2.setText(
                app.translate("SettingsPage.LaunchSettings", "SettingsPage.LaunchSettings.checkBox_2.text"))
            self.toolBox.setItemText(self.toolBox.indexOf(self.page),
                                     app.translate("SettingsPage.LaunchSettings",
                                                   "SettingsPage.LaunchSettings.Page1.title"))
            self.groupBox_2.setTitle(
                app.translate("SettingsPage.LaunchSettings", "SettingsPage.LaunchSettings.groupBox_2.title"))
            self.radioButton.setText(
                app.translate("SettingsPage.LaunchSettings",
                              "SettingsPage.LaunchSettings.radioButton.text"))
            self.radioButton_2.setText(
                app.translate("SettingsPage.LaunchSettings",
                              "SettingsPage.LaunchSettings.radioButton_2.text"))
            self.label_3.setText(
                app.translate("SettingsPage.LaunchSettings", "SettingsPage.LaunchSettings.label_3.text"))
            self.pushButton.setText(
                app.translate("SettingsPage.LaunchSettings",
                              "SettingsPage.LaunchSettings.pushButton.text"))
            self.pushButton_2.setText(
                app.translate("SettingsPage.LaunchSettings",
                              "SettingsPage.LaunchSettings.pushButton_2.text")
            )
            self.infoBar.title = app.translate("SettingsPage.LaunchSettings",
                                               "SettingsPage.LaunchSettings.Warning1.title")
            self.infoBar.content = app.translate("SettingsPage.LaunchSettings",
                                                 "SettingsPage.LaunchSettings.Warning1.content")
            self.infoBar.titleLabel.setVisible(True)
            self.infoBar.contentLabel.setVisible(True)
            if self.pushButton_3.isChecked():
                text = app.translate("SettingsPage.LaunchSettings", "SettingsPage.LaunchSettings.label_2.override")
                enabled = False
            else:
                text = app.translate("SettingsPage.LaunchSettings", "SettingsPage.LaunchSettings.label_2.extra")
                enabled = True
            self.label_2.setText(text)
            self.lineEdit_3.setClearButtonEnabled(enabled)
            self.pushButton_3.setText(
                app.translate("SettingsPage.LaunchSettings",
                              "SettingsPage.LaunchSettings.pushButton_3.text"))
            self.toolBox.setItemText(self.toolBox.indexOf(self.page_2),
                                     app.translate("SettingsPage.LaunchSettings",
                                                   "SettingsPage.LaunchSettings.Page2.title"))
            self.radioButton_3.setText(
                app.translate("SettingsPage.LaunchSettings", "SettingsPage.LaunchSettings.radioButton_3.text"))
            self.radioButton_4.setText(
                app.translate("SettingsPage.LaunchSettings", "SettingsPage.LaunchSettings.radioButton_4.text"))
            self.label_4.setText("/")
            self.label_5.setText("MB")
            self.label_6.setText(
                app.translate("SettingsPage.LaunchSettings", "SettingsPage.LaunchSettings.label_5.text"))
            self.toolBox.setItemText(self.toolBox.indexOf(self.page_3),
                                     app.translate("SettingsPage.LaunchSettings",
                                                   "SettingsPage.LaunchSettings.Page3.text"))
            self.toolBox.setItemText(self.toolBox.indexOf(self.page_4),
                                     app.translate("SettingsPage.LaunchSettings",
                                                   "SettingsPage.LaunchSettings.Page4.text"))
        
        def event(self, e):
            if hasattr(self, "horizontalSlider"):
                total_memory = psutil.virtual_memory().free // 8 // 1024 // 1024
                self.horizontalSlider.setMaximum(total_memory)
                digit_count = len(str(total_memory))
                if hasattr(self, "lcdNumber"):
                    self.lcdNumber.setDigitCount(digit_count)
                    self.lcdNumber.setProperty("intValue", self.horizontalSlider.value())
                if hasattr(self, "lcdNumber_2"):
                    self.lcdNumber_2.setDigitCount(digit_count)
                    self.lcdNumber_2.setProperty("intValue", self.horizontalSlider.maximum())
                if hasattr(self, "lineEdit_4"):
                    if isinstance(self.lineEdit_4.validator(), QRegularExpressionValidator):
                        validator = self.lineEdit_4.validator()
                        validator.setRegularExpression(QRegularExpression(r"[0-9]+"))
                        self.lineEdit_4.setValidator(validator)
            if hasattr(self, "groupBox"):
                self.groupBox.setPalette(self.label.palette())
                if hasattr(self, "groupBox_2"):
                    self.groupBox_2.setPalette(self.groupBox.palette())
            return super().event(e)
        
        def update_digit(self, value):
            self.lcdNumber.setProperty("intValue", value)
            self.lcdNumber_2.setProperty("intValue", self.horizontalSlider.maximum())
            self.lineEdit_4.setText(str(value))
        
        def update_text(self, value):
            if not value:
                value = 0
            if int(value) <= 9:
                value = str(int(value))
            if int(value) > self.horizontalSlider.maximum():
                value = self.horizontalSlider.maximum()
            self.horizontalSlider.setValue(int(value))
            self.update_digit(value)
        
        def update_example_text(self, text, value):
            texts = self.lineEdit.text().split(" ")
            if text not in texts:
                if value:
                    texts.append(text)
            else:
                if not value:
                    texts.remove(text)
            self.lineEdit.setText(" ".join(texts).lstrip(" "))
            cfg.set(cfg.extraGameCommand, self.lineEdit.text() or None)
        
        def update_command_text(self, value):
            self.update_example_state(value)
            cfg.set(cfg.extraGameCommand, value or None)
        
        def update_example_state(self, value):
            self.lineEdit.setText(self.lineEdit.text().lstrip(" "))
            texts = value.split(" ")
            self.checkBox.setChecked('-demo' in texts)
            self.checkBox_2.setChecked('-fullscreen' in texts)
        
        @staticmethod
        def change_jvm_mode(mode, value):
            if value:
                cfg.set(cfg.JVMLaunchMode, mode)
        
        def change_java(self, value):
            if value:
                cfg.set(cfg.JavaIsAutoSearch, True)
                cfg.set(cfg.JavaPath, None)
                self.lineEdit_2.clear()
                self.lineEdit_2.setText(
                    app.translate("SettingsPage.LaunchSettings", "SettingsPage.LaunchSettings.AutoSearchJava"))
                self.lineEdit_2.setEnabled(False)
            else:
                cfg.set(cfg.JavaIsAutoSearch, False)
                cfg.set(cfg.JavaPath, None)
                self.lineEdit_2.setEnabled(True)
                sj = self.SearchJava(self)
                sj.finishDisplay.connect(self.set_java_path)
                sj.start()
        
        @staticmethod
        def update_java_path(value):
            qre = QRegularExpression(r'\".+\"')
            result = qre.match(value)
            java_path = result.captured(0).strip('"')
            cfg.set(cfg.JavaPath, java_path or None)
        
        def set_java_path(self):
            idx = 0
            for i in self.lineEdit_2.items:
                qre = QRegularExpression(r'\".+\"')
                result = qre.match(i.text)
                text = result.captured(0)
                if text.strip('"') == cfg.get(cfg.JavaPath):
                    self.lineEdit_2.setCurrentIndex(idx)
                    break
                idx += 1
            else:
                java_path = cfg.get(cfg.JavaPath)
                try:
                    version_data = \
                        subprocess.check_output([java_path, "--version"], stderr=subprocess.STDOUT,
                                                creationflags=subprocess.CREATE_NO_WINDOW).decode().splitlines()[
                            0].split(
                            " ")[1]
                except subprocess.CalledProcessError:
                    try:
                        version_data = \
                            subprocess.check_output([java_path, "-version"], stderr=subprocess.STDOUT,
                                                    creationflags=subprocess.CREATE_NO_WINDOW).decode().splitlines()[
                                0].split(
                                " ")[2]
                    except subprocess.CalledProcessError:
                        pass
                    else:
                        for i in self.lineEdit_2.items:
                            qre = QRegularExpression(r'\".+\"')
                            result = qre.match(i.text)
                            text = result.captured(0)
                            if Path(text.strip('"')) == Path(java_path):
                                break
                        else:
                            self.lineEdit_2.addItem(f"\"{Path(java_path)}\" ({version_data.strip(chr(34))})")
                            self.lineEdit_2.setCurrentText(f"\"{Path(java_path)}\" ({version_data.strip(chr(34))})")
                else:
                    for i in self.lineEdit_2.items:
                        qre = QRegularExpression(r'\".+\"')
                        result = qre.match(i.text)
                        text = result.captured(0)
                        if Path(text.strip('"')) == Path(java_path):
                            break
                    else:
                        self.lineEdit_2.addItem(f"\"{Path(java_path)}\" ({version_data.strip(chr(34))})")
                        self.lineEdit_2.setCurrentText(f"\"{Path(java_path)}\" ({version_data.strip(chr(34))})")
            self.lineEdit_2.currentTextChanged.connect(self.update_java_path)
        
        def set_jvm_args_mode(self):
            if self.pushButton_3.isChecked():
                text = app.translate("SettingsPage.LaunchSettings", "SettingsPage.LaunchSettings.label_2.override")
                enabled = False
            else:
                text = app.translate("SettingsPage.LaunchSettings", "SettingsPage.LaunchSettings.label_2.extra")
                enabled = True
            self.label_2.setText(text)
            self.lineEdit_3.setClearButtonEnabled(enabled)
            cfg.set(cfg.JVMOverrideArgs, self.pushButton_3.isChecked())
        
        def manual_apply_java(self):
            dialogue = QFileDialog(self)
            result = dialogue.getOpenFileName(self, app.translate("SettingsPage.LaunchSettings",
                                                                  "SettingsPage.LaunchSettings.applyjava.title"),
                                              str(minecraft_path),
                                              "java.exe")  # , QFileDialog.Option
            if result[0]:
                java_path = result[0]
                cfg.set(cfg.JavaPath, java_path)
                try:
                    version_data = \
                        subprocess.check_output([java_path, "--version"], stderr=subprocess.STDOUT,
                                                creationflags=subprocess.CREATE_NO_WINDOW).decode().splitlines()[
                            0].split(
                            " ")[1]
                except subprocess.CalledProcessError:
                    try:
                        version_data = \
                            subprocess.check_output([java_path, "-version"], stderr=subprocess.STDOUT,
                                                    creationflags=subprocess.CREATE_NO_WINDOW).decode().splitlines()[
                                0].split(
                                " ")[2]
                    except subprocess.CalledProcessError:
                        pass
                    else:
                        for i in self.lineEdit_2.items:
                            qre = QRegularExpression(r'\".+\"')
                            result = qre.match(i.text)
                            text = result.captured(0)
                            if Path(text.strip('"')) == Path(java_path):
                                break
                        else:
                            self.lineEdit_2.addItem(f"\"{Path(java_path)}\" ({version_data.strip(chr(34))})")
                            self.lineEdit_2.setCurrentText(f"\"{Path(java_path)}\" ({version_data.strip(chr(34))})")
                else:
                    for i in self.lineEdit_2.items:
                        qre = QRegularExpression(r'\".+\"')
                        result = qre.match(i.text)
                        text = result.captured(0)
                        if Path(text.strip('"')) == Path(java_path):
                            break
                    else:
                        self.lineEdit_2.addItem(f"\"{Path(java_path)}\" ({version_data.strip(chr(34))})")
                        self.lineEdit_2.setCurrentText(f"\"{Path(java_path)}\" ({version_data.strip(chr(34))})")
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("SettingsPage")
        self.setStyleSheet("background: transparent;")
        
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.scrollArea = ScrollArea(self)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.scrollArea.setFrameShadow(QFrame.Shadow.Plain)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.toolBox = ToolBox(self.scrollAreaWidgetContents)
        self.toolBox.setObjectName(u"toolBox")
        self.page = self.LaunchSettings()
        self.page.setObjectName(u"page")
        self.toolBox.addItem(self.page)
        
        self.verticalLayout_2.addWidget(self.toolBox)
        
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        
        self.verticalLayout.addWidget(self.scrollArea)
        
        self.retranslateUi()
        
        self.toolBox.setCurrentIndex(0)
        
        QMetaObject.connectSlotsByName(self)
    
    def retranslateUi(self):
        self.toolBox.setItemText(self.toolBox.indexOf(self.page),
                                 app.translate("SettingsPage", "SettingsPage.Page1.title"))


class AboutPage(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("AboutPage")
        self.setStyleSheet("background: transparent;")
        
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.scrollArea = ScrollArea(self)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.scrollArea.setFrameShadow(QFrame.Shadow.Plain)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.toolBox = ToolBox(self.scrollAreaWidgetContents)
        self.toolBox.setObjectName(u"toolBox")
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.verticalLayout_3 = QVBoxLayout(self.page)
        
        self.card_1 = CardWidget(self.page)
        self.horizontalLayout = QHBoxLayout(self.card_1)
        
        self.user_icon = QLabel(self.card_1)
        self.user_icon.setFixedSize(QSize(64, 64))
        
        self.horizontalLayout.addWidget(self.user_icon)
        
        self.user_name = StrongBodyLabel(self.card_1)
        
        self.horizontalLayout.addWidget(self.user_name)
        
        self.introduction_label = BodyLabel(self.card_1)
        
        self.horizontalLayout.addWidget(self.introduction_label)
        
        self.verticalLayout_3.addWidget(self.card_1)
        
        self.card_2 = CardWidget(self.page)
        self.horizontalLayout_2 = QHBoxLayout(self.card_2)
        
        self.user_icon_2 = QLabel(self.card_1)
        self.user_icon_2.setFixedSize(QSize(64, 64))
        
        self.horizontalLayout_2.addWidget(self.user_icon_2)
        
        self.user_name_2 = StrongBodyLabel(self.card_2)
        
        self.horizontalLayout_2.addWidget(self.user_name_2)
        
        self.introduction_label_2 = BodyLabel(self.card_2)
        
        self.horizontalLayout_2.addWidget(self.introduction_label_2)
        
        self.verticalLayout_3.addWidget(self.card_2)
        
        self.verticalSpacer = QSpacerItem(20, 236, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        
        self.verticalLayout_3.addItem(self.verticalSpacer)
        
        self.toolBox.addItem(self.page)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        
        self.verticalLayout_4 = QVBoxLayout(self.page_2)
        
        self.card_3 = CardWidget(self.page_2)
        
        self.horizontalLayout_3 = QHBoxLayout(self.card_3)
        
        self.CMCL_icon = QSvgWidget(self.card_3)
        self.CMCL_icon.setFixedSize(QSize(64, 64))
        
        self.horizontalLayout_3.addWidget(self.CMCL_icon)
        
        self.introduction_label_3 = BodyLabel(self.card_3)
        
        self.horizontalLayout_3.addWidget(self.introduction_label_3)
        
        self.verticalLayout_4.addWidget(self.card_3)
        
        self.verticalSpacer_2 = QSpacerItem(20, 236, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        
        self.verticalLayout_4.addItem(self.verticalSpacer_2)
        
        self.toolBox.addItem(self.page_2)
        self.page_3 = QWidget()
        self.page_3.setObjectName(u"page_3")
        self.verticalLayout_5 = QVBoxLayout(self.page_3)
        
        self.tip_widget = InfoBar.info("", "", isClosable=False, duration=-1, parent=self.page_3,
                                       position=InfoBarPosition.TOP)
        self.verticalLayout_5.addWidget(self.tip_widget)
        
        # badge_colour = "B4D2FF"
        self.thank_cards = {}
        data = json.loads(Path("Thanks_data.json").read_text(encoding="utf-8"))
        for idx in range(1, data["values"] + 1):
            i = data[f"{idx}"]
            thank_icon = i["icon"]
            thank_name = i["name"]
            thank_text = i["info"]
            thank_badge_data = i["badges"]
            card = CardWidget(self.page_3)
            
            horizontalLayout = QHBoxLayout(card)
            
            user_icon = QLabel(card)
            user_icon.setFixedSize(QSize(64, 64))
            if thank_icon['type'] and thank_icon['value']:
                icon_type = thank_icon['type']
                icon_value = thank_icon['value']
                match icon_type:
                    case "local_path":
                        user_icon.setPixmap(QPixmap(icon_value))
                    case "web_url":
                        pass
                    case _:
                        user_icon.setPixmap(QPixmap())
            else:
                user_icon.setPixmap(QPixmap())
            
            horizontalLayout.addWidget(user_icon)
            
            user_name = StrongBodyLabel(card)
            user_name.setText(thank_name)
            badges = []
            
            for i in range(1, int(thank_badge_data["values"]) + 1):
                content = thank_badge_data[str(i)]
                badges.append(content)
            
            if badges:
                infobadge = InfoBadge.info("/".join(badges), parent=card, target=user_name,
                                           position=InfoBadgePosition.TOP_RIGHT)
            else:
                infobadge = None
            
            horizontalLayout.addWidget(user_name)
            
            introduction_label = BodyLabel(card)
            introduction_label.setText(thank_text)
            
            horizontalLayout.addWidget(introduction_label)
            
            self.verticalLayout_5.addWidget(card)
            
            self.thank_cards[thank_name] = {
                "card_widget": card,
                "icon_widgets": {
                    "icon": user_icon,
                    "data": thank_icon
                },
                "badge_widget": {
                    "badge": infobadge,
                    "data": thank_badge_data
                },
                "name_widgets": {
                    "label": user_name,
                    "data": thank_name
                },
                "intro_widgets": {
                    "label": introduction_label,
                    "data": thank_text
                }
            }
        
        self.verticalSpacer_3 = QSpacerItem(20, 236, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        
        self.verticalLayout_5.addItem(self.verticalSpacer_3)
        
        self.toolBox.addItem(self.page_3)
        
        self.verticalLayout_2.addWidget(self.toolBox)
        
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        
        self.verticalLayout.addWidget(self.scrollArea)
        
        self.retranslateUi()
        
        self.toolBox.setCurrentIndex(0)
        
        QMetaObject.connectSlotsByName(self)
    
    def retranslateUi(self):
        self.user_icon.setPixmap(QPixmap("chengwm_headimage.png"))
        self.user_name.setText("chengwm")
        self.user_name.adjustSize()
        self.introduction_label.setText(
            app.translate('AboutPage', 'AboutPage.author_introduction.text'))
        self.user_name_2.setText("mcdt")
        self.introduction_label_2.setText(
            "为 CMCL 启动器提供了超级多的建议。（CMCL 策划）"
        )
        self.toolBox.setItemText(self.toolBox.indexOf(self.page),
                                 app.translate("AboutPage", "AboutPage.Page1.title"))
        self.CMCL_icon.load("CMCL_icon.svg")
        self.introduction_label_3.setText(
            f"{app.translate('AboutPage', 'AboutPage.introduction_label_2.text')}{version[0]}({version[1]})"
        )
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_2),
                                 f"CMCL{app.translate('AboutPage', 'AboutPage.Page2.title')}")
        self.tip_widget.title = app.translate("AboutPage", "AboutPage.Info.title")
        self.tip_widget.content = app.translate("AboutPage",
                                                "AboutPage.Info.content")
        self.tip_widget.titleLabel.setVisible(True)
        self.tip_widget.contentLabel.setVisible(True)
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_3),
                                 app.translate("AboutPage", "AboutPage.Page3.title"))


class UserPage(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("UserPage")
        self.verticalLayout_2 = QVBoxLayout(self)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.widget = TopBar(self)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.widget_2 = AvatarWidget(self.widget)
        self.widget_2.setBorderRadius(100, 100, 100, 100)
        self.widget_2.setImage(f"user_icon-{getIconColor()}.svg")
        self.widget_2.setObjectName(u"widget_2")
        
        self.horizontalLayout.addWidget(self.widget_2)
        
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = BodyLabel(self.widget)
        self.label.setObjectName(u"label")
        
        self.verticalLayout.addWidget(self.label)
        
        self.label_2 = BodyLabel(self.widget)
        self.label_2.setObjectName(u"label_2")
        
        self.verticalLayout.addWidget(self.label_2)
        
        self.label_3 = BodyLabel(self.widget)
        self.label_3.setObjectName(u"label_3")
        
        self.verticalLayout.addWidget(self.label_3)
        
        self.horizontalLayout.addLayout(self.verticalLayout)
        
        self.verticalLayout_2.addWidget(self.widget)
        
        self.widget_3 = TopBar(self)
        self.widget_3.setObjectName(u"widget_3")
        self.horizontalLayout_2 = QHBoxLayout(self.widget_3)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.pushButton = DropDownPushButton(self.widget_3)
        self.pushButton.setObjectName(u"pushButton")
        menu = RoundMenu(self.pushButton)
        for i in (
                (app.translate("UserPage", "UserPage.pushButton.dropdown.1.text"),
                 lambda _: self.start_login()),
                
                (app.translate("UserPage", "UserPage.pushButton.dropdown.2.text"),
                 lambda _: self.create_offline_user())):
            text = i[0]
            action = QAction(text, menu)
            action.triggered.connect(i[1])
            menu.addAction(action)
        self.pushButton.setMenu(menu)
        
        self.horizontalLayout_2.addWidget(self.pushButton)
        
        self.pushButton_2 = PushButton(self.widget_3)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.pressed.connect(self.start_login)
        
        self.horizontalLayout_2.addWidget(self.pushButton_2)
        
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        self.horizontalLayout_2.addItem(self.horizontalSpacer)
        
        self.verticalLayout_2.addWidget(self.widget_3)
        
        self.tableView = TableView(self)
        self.tableView.setObjectName(u"tableView")
        self.tableView.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.tableView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableView.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tableView.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tableView.horizontalHeader().setVisible(True)
        self.tableView.verticalHeader().setVisible(False)
        self.versionModel = QStandardItemModel(self.tableView)
        self.versionModel.setHorizontalHeaderLabels(
            [app.translate("UserPage", "UserPage.TabelHeader.1"), "账户类型", "Minecraft 获取状态"])
        self.tableView.setModel(self.versionModel)
        self.versions = {}
        self.tableView.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.tableView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableView.horizontalHeader().setVisible(True)
        self.tableView.verticalHeader().setVisible(False)
        
        self.verticalLayout_2.addWidget(self.tableView)
        
        self.retranslateUi()
        
        QMetaObject.connectSlotsByName(self)
    
    def retranslateUi(self):
        try:
            frame.updateUser(QIcon(), player.player_name)
        except NameError:
            pass
        self.label.setText(
            app.translate("UserPage",
                          f"{app.translate('UserPage', 'UserPage.label.text')}{player.player_name or '无'}"))
        self.label_2.setText(
            app.translate("UserPage",
                          f"{app.translate('UserPage', 'UserPage.label_2.text')}{conv_table[player.player_accountType[1]]}（{state[player.player_accountType[0]]}）"))
        self.label_3.setText(
            app.translate("UserPage",
                          f"Minecraft {app.translate('UserPage', 'UserPage.label_3.text')}{'已获取' if player.player_hasMC else '未获取'}"))
        self.pushButton.setText(app.translate("UserPage", "UserPage.pushButton.text"))
        self.pushButton_2.setText(app.translate("UserPage", u"UserPage.pushButton_2.text"))
        menu = RoundMenu(self.pushButton)
        for i in (
                (app.translate("UserPage", "UserPage.pushButton.dropdown.1.text"),
                 lambda _: self.start_login()),
                
                (app.translate("UserPage", "UserPage.pushButton.dropdown.2.text"),
                 lambda _: self.create_offline_user())):
            text = i[0]
            action = QAction(text, menu)
            action.triggered.connect(i[1])
            menu.addAction(action)
        self.pushButton.setMenu(menu)
        self.versionModel.setHorizontalHeaderLabels(
            [app.translate("UserPage", "UserPage.TabelHeader.1"), "账户类型", "Minecraft 获取状态"])
    
    def event(self, e):
        if hasattr(self, "widget_2"):
            self.widget_2.setImage(f"user_icon-{getIconColor()}.svg")
        return super().event(e)
    
    def showEvent(self, *args, **kwargs):
        self.retranslateUi()
        super().showEvent(*args, **kwargs)
    
    def start_login(self):
        dialogue = LoginDialogue(frame)
        dialogue.loginFinished.connect(self.retranslateUi)
        dialogue.exec()
    
    def create_offline_user(self):
        dialogue = OfflineUserCreationDialogue(frame)
        dialogue.createFinished.connect(self.retranslateUi)
        dialogue.exec()


class MainWindow(MSFluentWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowIcon(QIcon("CMCL_icon.svg"))
        self.setWindowTitle("Common Minecraft Launcher")
        self.resize(800, 600)
        
        self.homepage = HomePage(self)
        self.downloadpage = DownloadPage(self)
        self.multiplayerpage = MultiplayerPage(self)
        self.toolspage = ToolsPage(self)
        self.settingspage = SettingsPage(self)
        self.aboutpage = AboutPage(self)
        self.userpage = UserPage(self)
        self.addSubInterface(self.homepage, FluentIcon.HOME,
                             app.translate("MainWindow", "MainWindow.Page1.title"), selectedIcon=FluentIcon.HOME_FILL)
        self.addSubInterface(self.downloadpage, FluentIcon.DOWNLOAD,
                             app.translate("MainWindow", "MainWindow.Page2.title"))
        self.addSubInterface(self.multiplayerpage, FluentIcon.WIFI,
                             app.translate("MainWindow", "MainWindow.Page3.title"))
        self.addSubInterface(self.toolspage, FluentIcon.APPLICATION,
                             app.translate("MainWindow", "MainWindow.Page4.title"))
        self.addSubInterface(self.settingspage, FluentIcon.SETTING,
                             app.translate("MainWindow", "MainWindow.Page5.title"))
        self.addSubInterface(self.aboutpage, FluentIcon.QUESTION,
                             app.translate("MainWindow", "MainWindow.Page6.title"))
        self.addSubInterface(self.userpage, f"user_icon-{getIconColor()}.svg",
                             app.translate("MainWindow", "MainWindow.UserPage.title"),
                             selectedIcon=f"user_icon-{getIconColor()}-selected.svg",
                             position=NavigationItemPosition.BOTTOM)
        self.navigationInterface.addWidget(
            routeKey="toggle_theme",
            widget=NavigationToolButton(QIcon(f"auto_{getIconColor()}.svg")),
            onClick=toggleTheme,
            position=NavigationItemPosition.BOTTOM
        )
        # self.navigationInterface.setAcrylicEnabled(True)
        # self.navigationInterface.setMinimumExpandWidth(16777216)
        self.setMicaEffectEnabled(False)
        # self.windowEffect.setMicaEffect(int(self.winId()), isAlt=True)
    
    def showCentre(self):
        screenSize = QGuiApplication.primaryScreen().geometry()
        pos = QPoint(screenSize.width() // 2 - self.width() // 2, screenSize.height() // 2 - self.height() // 2)
        self.move(pos)
        self.show()
    
    def updateUser(self, picture, username=None):
        widget = self.navigationInterface.widget("UserPage")
        if picture.isNull():
            widget.setIcon(QIcon(f"user_icon-{getIconColor()}.svg"))
            widget.setSelectedIcon(QIcon(f"user_icon-{getIconColor()}-selected.svg"))
        else:
            widget.setIcon(QIcon(picture))
        widget.setText(username or app.translate("MainWindow", "MainWindow.UserPage.title"))
        # widget.setToolTip(username or app.translate("MainWindow", "MainWindow.UserPage.title"))
    
    def exception(self, traceback_r):
        dialogue = ErrorDialogue(self, traceback_r)
        dialogue.show()
        dialogue.exec()
    
    # def _onThemeChangedFinished(self):
    #     super()._onThemeChangedFinished()
    #     self.windowEffect.setMicaEffect(int(self.winId()), isAlt=True, isDarkMode=isDarkTheme())
    
    def paintEvent(self, e):
        try:
            match theme():
                case Theme.LIGHT:
                    icon = QIcon("light.svg")
                case Theme.DARK:
                    icon = QIcon("dark.svg")
                case Theme.AUTO:
                    icon = QIcon(f"auto_{getIconColor()}.svg")
                case _:
                    icon = QIcon(f"auto_{getIconColor()}.svg")
            self.navigationInterface.widget("toggle_theme").setIcon(icon)
            self.navigationInterface.widget("UserPage").setIcon(QIcon(f"user_icon-{getIconColor()}.svg"))
            self.navigationInterface.widget("UserPage").setSelectedIcon(
                QIcon(f"user_icon-{getIconColor()}-selected.svg"))
        except:
            pass
        super().paintEvent(e)


class CConfig(QConfig):
    extraGameCommand = ConfigItem("LaunchSettings", "extraGameCommand", "")
    JavaIsAutoSearch = ConfigItem("LaunchSettings", "JavaIsAutoSearch", True, BoolValidator())
    JavaPath = ConfigItem("LaunchSettings", "JavaPath", None)
    JVMLaunchMode = OptionsConfigItem("LaunchSettings", "JVMLaunchMode", "client",
                                      OptionsValidator(["client", "server"]))
    JVMIsArgsDefault = ConfigItem("LaunchSettings", "JVMIsArgsDefault", True, BoolValidator())
    JVMOverrideArgs = ConfigItem("LaunchSettings", "JVMOverrideArgs", False, BoolValidator())
    JVMLaunchArgs = ConfigItem("LaunchSettings", "JVMLaunchArgs", None)
    
    MinecraftPath = ConfigItem("Environment", "MinecraftPath", ".")


class LoginThread(QThread):
    loginFinished = pyqtSignal(tuple)
    
    def run(self):
        try:
            data = Path("current_user.DAT").read_bytes().strip(
                b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
            datas = login_user(data, True)
        except FileNotFoundError:
            Path("current_user.DAT").write_text("", encoding="utf-8")
        finally:
            try:
                self.loginFinished.emit(datas)
            except NameError:
                self.loginFinished.emit((None, None, None, False))
            finally:
                splash.finish()


class ExceptionCall(QObject):
    slot = pyqtSignal(str)
    
    def call(self, arg1):
        self.slot.emit(arg1)


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
            file.write(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" + hashlib.sha512(
                name.encode(
                    "utf-8")).hexdigest().encode() + b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
        
        return name, uuid, access_token, has_mc
    except:
        return None, None, None, False


def update_user(datas):
    global player
    if datas:
        player.player_name = datas[0]
        player.player_uuid = datas[1]
        player.player_accessToken = datas[2]
        player.player_hasMC = datas[3]


if __name__ == "__main__":
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        sys.exit(0)
    player = Player.create_online_player(None, None, None, False, True)
    
    cfg = CConfig()
    qconfig.load("config/config.json", cfg)
    minecraft_path = Path(cfg.get(cfg.MinecraftPath))
    # setTheme(cfg.theme)
    app = QApplication([])
    app.setAttribute(Qt.ApplicationAttribute.AA_UseStyleSheetPropagationInWidgetStyles)
    app.setAttribute(Qt.ApplicationAttribute.AA_Use96Dpi)
    translator = FluentTranslator(QLocale(QLocale.Language.Chinese, QLocale.Country.China))
    ctranslator = QTranslator(app)
    ctranslator.load("CMCL-zh-cn.qm")
    app.installTranslator(translator)
    app.installTranslator(ctranslator)
    frame = MainWindow()
    
    
    def excepthook(*args, **kwargs):
        traceback.print_exception(*args, **kwargs)
        traceback_r = "".join(traceback.format_exception(*args, **kwargs))
        c = ExceptionCall()
        c.slot.connect(frame.exception)
        c.call(traceback_r)
    
    
    sys.excepthook = excepthook
    splash = SplashScreen(QIcon("CMCL_icon.svg"), frame)
    splash.show()
    frame.showCentre()
    
    
    def loginFinished(datas):
        update_user(datas)
        splash.finish()
        frame.updateUser(QIcon(), player.player_name)
    
    
    lt = LoginThread()
    lt.loginFinished.connect(loginFinished)
    lt.start()
    app.exec()
    qconfig.save()
