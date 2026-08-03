# -*- coding: utf-8 -*-
from typing import overload

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from ..ThemeController import *
from .ToolTip import ToolTip
from ..Windows import RoundedMenu

from .Widget import Widget


class ScrollBar(QScrollBar, Widget):
    @overload
    def __init__(self, parent=None):
        ...
    
    @overload
    def __init__(self, orientation, parent=None):
        ...
    
    def __init__(self, *__args):
        super().__init__(*__args)
        self.sliderPressed.connect(lambda: self.setSliderDown(True))
        self.sliderReleased.connect(lambda: self.setSliderDown(False))
        
        self.setStyleSheet("ScrollBar { width: 13px; }")
    
    def mousePressEvent(self, ev):
        super().mousePressEvent(ev)
        if ev.button() == Qt.MouseButton.LeftButton:
            self.setSliderDown(True)
    
    def mouseReleaseEvent(self, ev):
        super().mouseReleaseEvent(ev)
        self.setSliderDown(False)
    
    def keyPressEvent(self, ev):
        super().keyPressEvent(ev)
        if ev.key() in [16777234, 16777235, 16777236, 16777237]:
            self.setSliderDown(True)
    
    def keyReleaseEvent(self, ev):
        super().keyPressEvent(ev)
        self.setSliderDown(False)
    
    def paintEvent(self, e):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        
        op = QStyleOptionSlider()
        op.initFrom(self)
        self.initStyleOption(op)
        
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing)
        
        rect = self.rect()
        baseOpacity = self.property("baseOpacity") or 0.85
        frameOpacity = self.property("frameOpacity") or 0.0
        
        painter.save()
        painter.setOpacity(baseOpacity * 0.7)
        
        shadowColor1 = QColor(0, 0, 0, int(12 * baseOpacity))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(shadowColor1)
        shadowRect1 = rect.adjusted(6, 6, -6, -6)
        painter.drawRoundedRect(shadowRect1, 18, 18)
        
        shadowColor2 = QColor(0, 0, 0, int(8 * baseOpacity))
        painter.setBrush(shadowColor2)
        shadowRect2 = rect.adjusted(4, 4, -4, -4)
        painter.drawRoundedRect(shadowRect2, 16, 16)
        
        shadowColor3 = QColor(0, 0, 0, int(5 * baseOpacity))
        painter.setBrush(shadowColor3)
        shadowRect3 = rect.adjusted(2, 2, -2, -2)
        painter.drawRoundedRect(shadowRect3, 14, 14)
        painter.restore()
        
        painter.save()
        painter.setOpacity(baseOpacity)
        
        bgGradient = QLinearGradient(QPointF(rect.topLeft()), QPointF(rect.bottomRight()))
        bgColor = getBackgroundColour()
        
        bgColorLight = QColor(
            min(255, bgColor.red() + 20),
            min(255, bgColor.green() + 20),
            min(255, bgColor.blue() + 20)
        )
        bgColorMid = QColor(
            min(255, bgColor.red() + 10),
            min(255, bgColor.green() + 10),
            min(255, bgColor.blue() + 10)
        )
        
        bgGradient.setColorAt(0.0, bgColorLight)
        bgGradient.setColorAt(0.3, bgColorMid)
        bgGradient.setColorAt(0.7, bgColorMid)
        bgGradient.setColorAt(1.0, bgColor)
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(bgGradient)
        painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 16, 16)
        painter.restore()
        
        painter.save()
        painter.setOpacity(baseOpacity * 0.3)
        
        glowColor = QColor(255, 255, 255, int(180 * baseOpacity))
        painter.setPen(QPen(glowColor, 1.5))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect.adjusted(2, 2, -2, -2), 14, 14)
        painter.restore()
        
        painter.save()
        painter.setOpacity(baseOpacity * 0.9)
        
        borderGradient = QLinearGradient(QPointF(rect.topLeft()), QPointF(rect.bottomLeft()))
        borderColor = getBorderColour()
        borderColorDarker = QColor(
            max(0, borderColor.red() - 20),
            max(0, borderColor.green() - 20),
            max(0, borderColor.blue() - 20)
        )
        
        borderGradient.setColorAt(0.0, borderColorDarker)
        borderGradient.setColorAt(0.5, borderColor)
        borderGradient.setColorAt(1.0, borderColor)
        
        penBorder = QPen(borderGradient, 1.0)
        painter.setPen(penBorder)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 16, 16)
        painter.restore()
        
        # 方向箭头
        if self.property("frameOpacity"):
            painter.save()
            painter.setOpacity(self.property("frameOpacity"))
            borderColour = getBorderColour(is_highlight=True)
            painter.setPen(QPen(
                borderColour,
                1.0,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin
            ))
            match self.orientation():
                case Qt.Orientation.Horizontal:
                    painter.translate(QPoint(0, 0))
                    painter.drawLines(
                        [QLineF(QPointF(self.height() - 4.5, 3), QPointF(3, self.height() / 2)),
                         QLineF(QPointF(3, self.height() / 2), QPointF(self.height() - 4.5, self.height() - 3))])
                    painter.translate(QPoint(self.width() - self.height(), 0))
                    painter.drawLines(
                        [QLineF(QPointF(3, 3), QPointF(self.height() - 4.5, self.height() / 2)),
                         QLineF(QPointF(self.height() - 4.5, self.height() / 2), QPointF(3, self.height() - 3))])
                case Qt.Orientation.Vertical:
                    painter.translate(QPoint(0, 0))
                    painter.drawLines(
                        [QLineF(QPointF(3, self.width() - 3), QPointF(self.width() / 2, 4.5)),
                         QLineF(QPointF(self.width() / 2, 4.5),
                                QPointF(self.width() - 3, self.width() - 3))])
                    painter.translate(QPoint(0, self.height() - self.width() - 2))
                    painter.drawLines(
                        [QLineF(QPointF(3, 4.5), QPointF(self.width() / 2, self.width() - 3)),
                         QLineF(QPointF(self.width() / 2, self.width() - 3),
                                QPointF(self.width() - 3, 4.5))])
            painter.restore()
        
        sliderRect = self.style().subControlRect(QStyle.ComplexControl.CC_ScrollBar, op,
                                           QStyle.SubControl.SC_ScrollBarSlider).adjusted(2, 2, -2, -2)
        
        painter.save()
        painter.setOpacity(
            self.property("baseOpacity") + (self.property("frameOpacity") * (1.0 - self.property("baseOpacity"))))
        painter.setPen(getBorderColour(is_highlight=self.isSliderDown() and self.isEnabled()))
        
        sliderBgColor = getBackgroundColour(is_highlight=self.isSliderDown() and self.isEnabled())
        sliderGradient = QLinearGradient(QPointF(sliderRect.topLeft()), QPointF(sliderRect.bottomLeft()))
        sliderBgColorLighter = QColor(
            min(255, sliderBgColor.red() + 10),
            min(255, sliderBgColor.green() + 10),
            min(255, sliderBgColor.blue() + 10)
        )
        sliderGradient.setColorAt(0.0, sliderBgColorLighter)
        sliderGradient.setColorAt(1.0, sliderBgColor)
        painter.setBrush(sliderGradient)
        painter.drawRoundedRect(sliderRect.adjusted(1, 1, -1, -1), 16, 16)
        painter.restore()
    
    def contextMenuEvent(self, a0):
        def updateContextMenu(self):
            menus = self.findChildren(QMenu)
            if menus:
                menu = menus[-1]
                RoundedMenu.updateQSS(menu)
                menu.popup(QCursor.pos())
        
        QTimer.singleShot(0, lambda: updateContextMenu(self))
        super().contextMenuEvent(a0)


class ScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.installEventFilter(ToolTip(self))
        self.setHorizontalScrollBar(ScrollBar(Qt.Orientation.Horizontal, self))
        self.setVerticalScrollBar(ScrollBar(Qt.Orientation.Vertical, self))
        self.setCornerWidget(QWidget(self))
