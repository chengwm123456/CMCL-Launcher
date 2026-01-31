# -*- coding: utf-8 -*-
from typing import overload

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from ..ThemeController import *

from .Widget import Widget


class ImageWidget(Widget):
    @overload
    def __init__(self, parent=None):
        ...
    
    @overload
    def __init__(self, image, parent=None):
        ...
    
    def __init__(self, *__args):
        super().__init__(__args[-1])
        self.setProperty("image", None)
        if len(__args) > 1:
            image = __args[0]
            self.setProperty("image", QImage(image).convertToFormat(QImage.Format.Format_ARGB32_Premultiplied))
        self.setProperty("borderRadius", 0)
    
    def setImage(self, image):
        if image:
            self.setProperty("image", QImage(image).convertToFormat(QImage.Format.Format_ARGB32_Premultiplied))
        else:
            self.setProperty("image", None)
    
    def setBorderRadius(self, radius):
        if isinstance(radius, float):
            self.setProperty("borderRadius", float(radius))
        else:
            self.setProperty("borderRadius", int(radius))
    
    def sizeHint(self):
        if self.property("image"):
            return self.property("image").size()
        return QSize(-1, -1)
    
    def paintEvent(self, a0):
        super().paintEvent(a0)
        if self.property("image"):
            painter = QPainter(self)
            painter.setOpacity(
                self.property("baseOpacity") + (self.property("frameOpacity") * (1.0 - self.property("baseOpacity"))))
            painter.setRenderHints(
                QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing | QPainter.RenderHint.SmoothPixmapTransform)
            
            if self.property("borderRadius"):
                pp = QPainterPath()
                pp.addRoundedRect(self.rect().toRectF(), self.property("borderRadius"), self.property("borderRadius"))
                painter.setClipPath(pp)
            
            painter.drawImage(self.rect().toRectF(), self.property("image"), self.property("image").rect().toRectF())
