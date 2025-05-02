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
        borderGradient = QRadialGradient(QPointF(self.mapFromGlobal(QCursor.pos())),
                                         max(self.width(), self.height()))
        borderGradient.setColorAt(0.0, borderColour)
        borderGradient.setColorAt(1.0, Colour(*borderColour, 32))
        painter.setPen(QPen(QBrush(borderGradient), 1))
        backgroundGradient = QLinearGradient(QPointF(0, 0), QPointF(0, self.height()))
        backgroundGradient.setColorAt(0.0, backgroundColour)
        backgroundGradient.setColorAt(1.0, Colour(*backgroundColour, 210))
        painter.setBrush(QBrush(backgroundGradient))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)
        match self.orientation():
            case Qt.Orientation.Horizontal:
                painter.drawLines([QLine(QPoint(self.height(), 2), QPoint(self.height(), self.height() - 2)),
                                   QLine(QPoint(self.width() - self.height(), 2),
                                         QPoint(self.width() - self.height(), self.height() - 2))])
            case Qt.Orientation.Vertical:
                painter.drawLines([QLine(QPoint(2, self.width()), QPoint(self.width() - 2, self.width())),
                                   QLine(QPoint(2, self.height() - self.width()),
                                         QPoint(self.width() - 2, self.height() - self.width()))])
        painter.restore()
        painter.save()
        painter.setPen(
            QPen(
                getBorderColour(is_highlight=True) \
                    if ((self.underMouse() or self.hasFocus()) or self.isSliderDown()) and self.isEnabled() \
                    else getForegroundColour(),
                1.0,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin
            )
        )
        painter.setBrush(
            getBorderColour(is_highlight=True) \
                if (self.isSliderDown() or self.hasFocus()) and self.isEnabled() \
                else getForegroundColour()
        )
        match self.orientation():
            case Qt.Orientation.Horizontal:
                painter.translate(QPoint(0, 0))
                painter.drawPolygon(
                    [QPoint(3, self.height() // 2), QPoint(self.height() - 3, self.height() - 3),
                     QPoint(self.height() - 3, 3)])
                painter.translate(QPoint(self.width() - self.height(), 0))
                painter.drawPolygon(
                    [QPoint(self.height() - 3, self.height() // 2), QPoint(3, self.height() - 3),
                     QPoint(3, 3)])
            case Qt.Orientation.Vertical:
                painter.translate(QPoint(0, 0))
                painter.drawPolygon(
                    [QPoint(3, self.width() - 3), QPoint(self.width() // 2, 3),
                     QPoint(self.width() - 3, self.width() - 3)])
                painter.translate(QPoint(0, self.height() - self.width()))
                painter.drawPolygon(
                    [QPoint(3, 3), QPoint(self.width() // 2, self.width() - 3), QPoint(self.width() - 3, 3)])
        painter.restore()
        painter.save()
        rect = self.style().subControlRect(QStyle.ComplexControl.CC_ScrollBar, op,
                                           QStyle.SubControl.SC_ScrollBarSlider).adjusted(2, 2, -2,
                                                                                          -2)
        borderColour = getBorderColour(is_highlight=self.isEnabled())
        backgroundColour = getBackgroundColour(is_highlight=self.isEnabled())
        borderGradient = QRadialGradient(QPointF(self.mapFromGlobal(QCursor.pos())),
                                         max(rect.width(), rect.height()))
        borderGradient.setColorAt(0.0, borderColour)
        borderGradient.setColorAt(1.0, Colour(*borderColour, 32))
        painter.setPen(QPen(QBrush(borderGradient), 1))
        backgroundGradient = QLinearGradient(QPointF(0, 0), QPointF(0, rect.height()))
        backgroundGradient.setColorAt(0.0, backgroundColour)
        backgroundGradient.setColorAt(1.0, Colour(*backgroundColour, 210))
        painter.setBrush(QBrush(backgroundGradient))
        painter.drawRoundedRect(rect, 10, 10)
        painter.restore()
    
    def contextMenuEvent(self, a0):
        menu = RoundedMenu(self)
        menu.addAction("Scroll Here",
                       lambda: self.setValue(
                           int(self.style().sliderValueFromPosition(
                               self.minimum(),
                               self.maximum(),
                               self.mapFromGlobal(
                                   QCursor.pos()).x() if self.orientation() == Qt.Orientation.Horizontal else self.mapFromGlobal(
                                   QCursor.pos()).y(),
                               self.width() if self.orientation() == Qt.Orientation.Horizontal else self.height(),
                           ))))
        menu.addSeparator()
        menu.addAction("Top", lambda: self.setValue(0))
        menu.addAction("Bottom", lambda: self.setValue(self.maximum()))
        menu.addSeparator()
        menu.addAction("Page up", lambda: self.setValue(max(0, self.value() - self.pageStep())))
        menu.addAction("Page down", lambda: self.setValue(min(self.maximum(), self.value() + self.pageStep())))
        menu.addSeparator()
        menu.addAction("Scroll up", lambda: self.setValue(max(0, self.value() - 20)))
        menu.addAction("Scroll down", lambda: self.setValue(min(self.maximum(), self.value() + 20)))
        menu.popup(QCursor.pos())


class ScrollArea(QScrollArea):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.installEventFilter(ToolTip(self))
        self.setHorizontalScrollBar(ScrollBar(Qt.Orientation.Horizontal, self))
        self.setVerticalScrollBar(ScrollBar(Qt.Orientation.Vertical, self))
        self.setCornerWidget(QWidget(self))
