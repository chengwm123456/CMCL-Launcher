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
        painter = QPainter(self)
        painter.setOpacity(self.property("widgetOpacity"))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        op = QStyleOptionSlider()
        op.initFrom(self)
        self.initStyleOption(op)
        painter.save()
        borderColour = getBorderColour()
        backgroundColour = getBackgroundColour()
        borderGradient = QLinearGradient(QPointF(0, 0), QPointF(0, self.height()))
        borderGradient.setColorAt(0.0, borderColour)
        borderGradient.setColorAt(1.0, Colour(*borderColour,
                                              int(255 * ((max(0.6, self.property("widgetOpacity")) - 0.6) * 10) / 4)))
        backgroundGradient = QRadialGradient(QPointF(self.rect().bottomRight()), min(self.width(), self.height()))
        backgroundGradient.setColorAt(0.0, backgroundColour)
        backgroundGradient.setColorAt(1.0, Colour(*backgroundColour, 190))
        painter.setPen(QPen(QBrush(borderGradient), 1))
        painter.setBrush(QBrush(backgroundGradient))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)
        painter.restore()
        painter.save()
        borderColour = getBorderColour(is_highlight=True) \
            if ((self.underMouse() or self.hasFocus()) or self.isSliderDown()) and self.isEnabled() \
            else getForegroundColour()
        painter.setPen(QPen(
            QBrush(Colour(*borderColour, int(255 * ((max(0.6, self.property(
                "widgetOpacity")) - 0.6) * 10) / 4))),
            1.0,
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap,
            Qt.PenJoinStyle.RoundJoin
        ))
        match self.orientation():
            case Qt.Orientation.Horizontal:
                painter.translate(QPoint(0, 0))
                painter.drawLines(
                    [QLineF(QPointF(self.height() - 4.5, 3), QPointF(3, self.height() // 2)),
                     QLineF(QPointF(3, self.height() // 2), QPointF(self.height() - 4.5, self.height() - 3))])
                painter.translate(QPoint(self.width() - self.height(), 0))
                painter.drawLines(
                    [QLineF(QPointF(3, 3), QPointF(self.height() - 4.5, self.height() // 2)),
                     QLineF(QPointF(self.height() - 4.5, self.height() // 2), QPointF(3, self.height() - 3))])
            case Qt.Orientation.Vertical:
                painter.translate(QPoint(0, 0))
                painter.drawLines(
                    [QLineF(QPointF(3, self.width() - 3), QPointF(self.width() // 2, 4.5)),
                     QLineF(QPointF(self.width() // 2, 4.5),
                            QPointF(self.width() - 3, self.width() - 3))])
                painter.translate(QPoint(0, self.height() - self.width()))
                painter.drawLines(
                    [QLineF(QPointF(3, 4.5), QPointF(self.width() // 2, self.width() - 3)),
                     QLineF(QPointF(self.width() // 2, self.width() - 3),
                            QPointF(self.width() - 3, 4.5))])
        painter.restore()
        painter.save()
        rect = self.style().subControlRect(QStyle.ComplexControl.CC_ScrollBar, op,
                                           QStyle.SubControl.SC_ScrollBarSlider).adjusted(2, 2, -2, -2)
        borderColour = getBorderColour(is_highlight=self.isEnabled())
        backgroundColour = getBackgroundColour(is_highlight=self.isEnabled())
        borderGradient = QLinearGradient(QPointF(rect.x(), rect.y()), QPointF(rect.x(), rect.y() + rect.height()))
        borderGradient.setColorAt(0.0, borderColour)
        borderGradient.setColorAt(1.0, Colour(*borderColour,
                                              int(255 * ((max(0.6, self.property("widgetOpacity")) - 0.6) * 10) / 4)))
        backgroundGradient = QRadialGradient(QPointF(rect.bottomRight()), min(rect.width(), rect.height()))
        backgroundGradient.setColorAt(0.0, backgroundColour)
        backgroundGradient.setColorAt(1.0, Colour(*backgroundColour, 190))
        painter.setPen(QPen(QBrush(borderGradient), 1))
        painter.setBrush(QBrush(backgroundGradient))
        painter.drawRoundedRect(rect, 10, 10)
        painter.restore()
    
    def contextMenuEvent(self, a0):
        def updateContextMenu(self):
            menus = self.findChildren(QMenu)
            if menus:
                menu = menus[-1]
                menu.BORDER_RADIUS = RoundedMenu.BORDER_RADIUS
                RoundedMenu.updateQSS(menu)
                menu.popup(QCursor.pos())
        
        QTimer.singleShot(1, lambda: updateContextMenu(self))
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
