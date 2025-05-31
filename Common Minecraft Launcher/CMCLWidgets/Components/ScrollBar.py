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
        borderGradient.setColorAt(1.0, Colour(
            *borderColour,
            (255 if self.hasFocus() and self.isEnabled() else 32)
        ))
        painter.setPen(QPen(QBrush(borderGradient), 1.0))
        backgroundGradient = QLinearGradient(QPointF(0, 0), QPointF(0, self.height()))
        backgroundGradient.setColorAt(0.0, backgroundColour)
        backgroundGradient.setColorAt(1.0, Colour(*backgroundColour, 210))
        painter.setBrush(QBrush(backgroundGradient))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)
        painter.restore()
        painter.save()
        borderColour = getBorderColour(is_highlight=True) \
            if ((self.underMouse() or self.hasFocus()) or self.isSliderDown()) and self.isEnabled() \
            else getForegroundColour()
        match self.orientation():
            case Qt.Orientation.Horizontal:
                painter.translate(QPoint(0, 0))
                borderGradient = QRadialGradient(QPointF(self.mapFromGlobal(QCursor.pos())),
                                                 max(self.width(), self.height()))
                borderGradient.setColorAt(0.0, borderColour)
                borderGradient.setColorAt(1.0, Colour(
                    *borderColour,
                    (255 if self.hasFocus() and self.isEnabled() else 32)
                ))
                painter.setPen(QPen(
                    QBrush(borderGradient),
                    1.0,
                    Qt.PenStyle.SolidLine,
                    Qt.PenCapStyle.RoundCap,
                    Qt.PenJoinStyle.RoundJoin
                ))
                painter.drawLines(
                    [QLineF(QPointF(self.height() - 4.5, 3), QPointF(3, self.height() // 2)),
                     QLineF(QPointF(3, self.height() // 2), QPointF(self.height() - 4.5, self.height() - 3))])
                painter.translate(QPoint(self.width() - self.height(), 0))
                borderGradient = QRadialGradient(
                    QPointF(self.mapFromGlobal(QCursor.pos())) - QPointF(self.width() - self.height(), 0),
                    max(self.width(), self.height()))
                borderGradient.setColorAt(0.0, borderColour)
                borderGradient.setColorAt(1.0, Colour(
                    *borderColour,
                    (255 if self.hasFocus() and self.isEnabled() else 32)
                ))
                painter.setPen(QPen(
                    QBrush(borderGradient),
                    1.0,
                    Qt.PenStyle.SolidLine,
                    Qt.PenCapStyle.RoundCap,
                    Qt.PenJoinStyle.RoundJoin
                ))
                painter.drawLines(
                    [QLineF(QPointF(3, 3), QPointF(self.height() - 4.5, self.height() // 2)),
                     QLineF(QPointF(self.height() - 4.5, self.height() // 2), QPointF(3, self.height() - 3))])
            case Qt.Orientation.Vertical:
                borderGradient = QRadialGradient(QPointF(self.mapFromGlobal(QCursor.pos())),
                                                 max(self.width(), self.height()))
                borderGradient.setColorAt(0.0, borderColour)
                borderGradient.setColorAt(1.0, Colour(
                    *borderColour,
                    (255 if self.hasFocus() and self.isEnabled() else 32)
                ))
                painter.setPen(QPen(
                    QBrush(borderGradient),
                    1.0,
                    Qt.PenStyle.SolidLine,
                    Qt.PenCapStyle.RoundCap,
                    Qt.PenJoinStyle.RoundJoin
                ))
                painter.translate(QPoint(0, 0))
                painter.drawLines(
                    [QLineF(QPointF(3, self.width() - 3), QPointF(self.width() // 2, 4.5)),
                     QLineF(QPointF(self.width() // 2, 4.5),
                            QPointF(self.width() - 3, self.width() - 3))])
                painter.translate(QPoint(0, self.height() - self.width()))
                borderGradient = QRadialGradient(
                    QPointF(self.mapFromGlobal(QCursor.pos())) - QPointF(0, self.height() - self.width()),
                    max(self.width(), self.height()))
                borderGradient.setColorAt(0.0, borderColour)
                borderGradient.setColorAt(1.0, Colour(
                    *borderColour,
                    (255 if self.hasFocus() and self.isEnabled() else 32)
                ))
                painter.setPen(QPen(
                    QBrush(borderGradient),
                    1.0,
                    Qt.PenStyle.SolidLine,
                    Qt.PenCapStyle.RoundCap,
                    Qt.PenJoinStyle.RoundJoin
                ))
                painter.drawLines(
                    [QLineF(QPointF(3, 4.5), QPointF(self.width() // 2, self.width() - 3)),
                     QLineF(QPointF(self.width() // 2, self.width() - 3),
                            QPointF(self.width() - 3, 4.5))])
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
        borderGradient.setColorAt(1.0, Colour(
            *borderColour,
            (255 if self.hasFocus() and self.isEnabled() else 32)
        ))
        painter.setPen(QPen(QBrush(borderGradient), 1.0))
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
