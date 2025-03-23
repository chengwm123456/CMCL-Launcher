# -*- coding: utf-8 -*-
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from CMCLWidgets import *
from CMCLWidgets.Windows import RoundedDialogue
import time


class TextDialogueBase(RoundedDialogue):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(8, 40, 8, 8)
        self.label = Label(self)
        self.layout.addWidget(self.label)

    def paintEvent(self, a0, **kwargs):
        painter = QPainter(self)
        painter.fillRect(
            QRect(-self.geometry().x(), -self.geometry().y(), QGuiApplication.primaryScreen().geometry().width(),
                  QGuiApplication.primaryScreen().geometry().height()),
            QGradient(QGradient.Preset.LandingAircraft if getTheme() == Theme.Light else QGradient.Preset.NightSky))


def creeper():
    class Creeper(TextDialogueBase):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.label.setText("Creeper?")
            self.input = LineEdit(self)
            self.layout.addWidget(self.input)
            self.input.returnPressed.connect(self.verifyText)

        def verifyText(self):
            text = self.input.text()
            if text == "Aw man":
                self.close()
            else:
                exit(1975848830)

    dialog = Creeper()
    dialog.exec()
