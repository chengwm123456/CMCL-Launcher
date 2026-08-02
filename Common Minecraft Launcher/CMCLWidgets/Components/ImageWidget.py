# -*- coding: utf-8 -*-
from typing import overload
from enum import IntEnum

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from ..ThemeController import *

from .Widget import Widget


class ImageWidget(Widget):
    class ImageScaleMode(IntEnum):
        Stretch = 0
        AspectRatio = 1
        Crop = 2
        Original = 3
    
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
        self.setProperty("imageAlignment", Qt.AlignmentFlag.AlignCenter)
        self.setProperty("imageScaleMode", self.ImageScaleMode.Stretch)
    
    def setImage(self, image):
        if image:
            self.setProperty("image", QImage(image).convertToFormat(QImage.Format.Format_ARGB32_Premultiplied))
        else:
            self.setProperty("image", None)
    
    def setBorderRadius(self, radius):
        if isinstance(radius, float):
            radius = float(radius)
        else:
            radius = int(radius)
        self.setProperty("borderRadius", int(radius))
    
    def setImageAlignment(self, alignment):
        self.setProperty("imageAlignment", alignment)
    
    def setImageScaleMode(self, mode):
        self.setProperty("imageScaleMode", mode)
    
    def sizeHint(self):
        if self.property("image"):
            return self.property("image").size()
        return QSize(-1, -1)
    
    def paintEvent(self, a0):
        if self.property("image"):
            painter = QPainter(self)
            painter.setOpacity(
                self.property("baseOpacity") + (self.property("frameOpacity") * (1.0 - self.property("baseOpacity"))))
            painter.setRenderHints(
                QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing | QPainter.RenderHint.SmoothPixmapTransform)
            
            image = self.property("image")
            imageScaleMode = self.property("imageScaleMode")
            alignment = self.property("imageAlignment")
            widgetRect = self.rect().toRectF()
            
            if imageScaleMode == self.ImageScaleMode.Stretch:
                if self.property("borderRadius"):
                    pp = QPainterPath()
                    pp.addRoundedRect(widgetRect, self.property("borderRadius"), self.property("borderRadius"))
                    painter.setClipPath(pp)
                else:
                    painter.setClipRect(widgetRect)
                painter.drawImage(widgetRect, image, image.rect().toRectF())
            elif imageScaleMode == self.ImageScaleMode.AspectRatio:
                if widgetRect.width() <= 0 or widgetRect.height() <= 0:
                    return
                
                imageSize = image.size()
                scaleX = widgetRect.width() / imageSize.width()
                scaleY = widgetRect.height() / imageSize.height()
                scale = min(scaleX, scaleY)
                
                scaledWidth = imageSize.width() * scale
                scaledHeight = imageSize.height() * scale
                
                x = widgetRect.x()
                y = widgetRect.y()
                
                if alignment & Qt.AlignmentFlag.AlignLeft:
                    x = widgetRect.x()
                elif alignment & Qt.AlignmentFlag.AlignRight:
                    x = widgetRect.right() - scaledWidth
                elif alignment & Qt.AlignmentFlag.AlignHCenter:
                    x = widgetRect.center().x() - scaledWidth / 2
                else:
                    x = widgetRect.center().x() - scaledWidth / 2
                
                if alignment & Qt.AlignmentFlag.AlignTop:
                    y = widgetRect.y()
                elif alignment & Qt.AlignmentFlag.AlignBottom:
                    y = widgetRect.bottom() - scaledHeight
                elif alignment & Qt.AlignmentFlag.AlignVCenter:
                    y = widgetRect.center().y() - scaledHeight / 2
                else:
                    y = widgetRect.center().y() - scaledHeight / 2
                
                targetRect = QRectF(x, y, scaledWidth, scaledHeight)
                if self.property("borderRadius"):
                    pp = QPainterPath()
                    pp.addRoundedRect(targetRect, self.property("borderRadius"), self.property("borderRadius"))
                    painter.setClipPath(pp)
                else:
                    painter.setClipRect(targetRect)
                painter.drawImage(targetRect, image, image.rect().toRectF())
            elif imageScaleMode == self.ImageScaleMode.Crop:
                if widgetRect.width() <= 0 or widgetRect.height() <= 0:
                    return
                
                imageSize = image.size()
                scaleX = widgetRect.width() / imageSize.width()
                scaleY = widgetRect.height() / imageSize.height()
                scale = max(scaleX, scaleY)
                
                scaledWidth = imageSize.width() * scale
                scaledHeight = imageSize.height() * scale
                
                x = 0
                y = 0
                
                if alignment & Qt.AlignmentFlag.AlignLeft:
                    x = widgetRect.x()
                elif alignment & Qt.AlignmentFlag.AlignRight:
                    x = widgetRect.right() - scaledWidth
                elif alignment & Qt.AlignmentFlag.AlignHCenter:
                    x = widgetRect.center().x() - scaledWidth / 2
                else:
                    x = widgetRect.center().x() - scaledWidth / 2
                
                if alignment & Qt.AlignmentFlag.AlignTop:
                    y = widgetRect.y()
                elif alignment & Qt.AlignmentFlag.AlignBottom:
                    y = widgetRect.bottom() - scaledHeight
                elif alignment & Qt.AlignmentFlag.AlignVCenter:
                    y = widgetRect.center().y() - scaledHeight / 2
                else:
                    y = widgetRect.center().y() - scaledHeight / 2
                
                targetRect = QRectF(x, y, scaledWidth, scaledHeight)
                if self.property("borderRadius"):
                    pp = QPainterPath()
                    pp.addRoundedRect(targetRect, self.property("borderRadius"), self.property("borderRadius"))
                    painter.setClipPath(pp)
                else:
                    painter.setClipRect(targetRect)
                painter.drawImage(targetRect, image, image.rect().toRectF())
            else:
                imageSize = image.size()
                x = widgetRect.x()
                y = widgetRect.y()
                
                if alignment & Qt.AlignmentFlag.AlignLeft:
                    x = widgetRect.x()
                elif alignment & Qt.AlignmentFlag.AlignRight:
                    x = widgetRect.right() - imageSize.width()
                elif alignment & Qt.AlignmentFlag.AlignHCenter:
                    x = widgetRect.center().x() - imageSize.width() / 2
                else:
                    x = widgetRect.center().x() - imageSize.width() / 2
                
                if alignment & Qt.AlignmentFlag.AlignTop:
                    y = widgetRect.y()
                elif alignment & Qt.AlignmentFlag.AlignBottom:
                    y = widgetRect.bottom() - imageSize.height()
                elif alignment & Qt.AlignmentFlag.AlignVCenter:
                    y = widgetRect.center().y() - imageSize.height() / 2
                else:
                    y = widgetRect.center().y() - imageSize.height() / 2
                
                targetRect = QRectF(x, y, imageSize.width(), imageSize.height())
                if self.property("borderRadius"):
                    pp = QPainterPath()
                    pp.addRoundedRect(targetRect, self.property("borderRadius"), self.property("borderRadius"))
                    painter.setClipPath(pp)
                else:
                    painter.setClipRect(targetRect)
                painter.drawImage(targetRect, image, image.rect().toRectF())
