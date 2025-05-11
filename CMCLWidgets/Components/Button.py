# -*- coding: utf-8 -*-
from typing import overload

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from ..ThemeController import *

from .Widget import Widget


class PushButton(QPushButton, Widget):
    @overload
    def __init__(self, parent=None):
        ...
    
    @overload
    def __init__(self, text, parent=None):
        ...
    
    @overload
    def __init__(self, icon, text, parent=None):
        ...
    
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
    
    def paintEvent(self, a0):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self)
        painter.setOpacity(self.property("widgetOpacity"))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        borderColour = getBorderColour(
            is_highlight=(self.isDown() or self.isChecked()) or
                         ((self.isDown() or self.isChecked() or self.underMouse() or self.hasFocus()) and
                          self.isEnabled())
        )
        backgroundColour = getBackgroundColour(
            is_highlight=(self.isDown() or self.isChecked()) or (
                    (self.isDown() or self.isChecked()) and self.isEnabled())
        )
        painter.save()
        painter.setOpacity((((max(painter.opacity(), 0.6) - 0.6) * 10) / 4))
        borderGradient = QLinearGradient(QPointF(0, 0), QPointF(0, self.height()))
        borderGradient.setColorAt(0.0, Colour(*getBorderColour(), 64))
        borderGradient.setColorAt(1.0, borderColour)
        painter.setPen(QPen(QBrush(borderGradient), 1))
        painter.setBrush(Qt.GlobalColor.transparent)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 12, 12)
        painter.restore()
        painter.save()
        painter.setOpacity(self.property("widgetOpacity"))
        borderGradient = QLinearGradient(QPointF(3, 3), QPointF(3, self.height() - 3))
        borderGradient.setColorAt(0.0, borderColour)
        borderGradient.setColorAt(1.0, Colour(*getBorderColour(), 64))
        backgroundGradient = QLinearGradient(QPointF(3, 3), QPointF(self.width() - 3, 3))
        backgroundGradient.setColorAt(0.0, backgroundColour)
        backgroundGradient.setColorAt(0.5, Colour(*backgroundColour, 230))
        backgroundGradient.setColorAt(1.0, backgroundColour)
        painter.setPen(QPen(QBrush(borderGradient), 1))
        painter.setBrush(QBrush(backgroundGradient))
        painter.drawRoundedRect(self.rect().adjusted(3, 3, -3, -3), 10, 10)
        painter.restore()
        if self.menu():
            painter.save()
            rect = self.rect().adjusted(3, 3, -3, -3)
            x = (rect.width() - 5) - 3 + rect.x()
            y = rect.height() / 2 - 2 + rect.y()
            if self.isDown():
                y += 2
            painter.setPen(QPen(
                QBrush(borderGradient),
                1.0,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin
            ))
            painter.translate(x, y)
            painter.drawLines([QLineF(QPointF(0, 0), QPointF(3, 4)), QLineF(QPointF(3, 4), QPointF(6, 0))])
            painter.restore()
        op = QStyleOptionButton()
        op.initFrom(self)
        self.initStyleOption(op)
        op.rect.adjust(4, 4, -4, -4)
        op.palette.setColor(self.foregroundRole(), getForegroundColour())
        self.style().drawControl(QStyle.ControlElement.CE_PushButtonLabel, op, painter, self)
        self.setStyleSheet("padding: 5px;")
    
    def keyPressEvent(self, *__args):
        super().keyPressEvent(*__args)
        if __args[0].key() == 16777220 and self.hasFocus() and self.isVisible():
            self.setDown(True)
            if self.isCheckable():
                self.setChecked(not self.isChecked())
            self.repaint()
    
    def keyReleaseEvent(self, *__args):
        super().keyReleaseEvent(*__args)
        if __args[0].key() == 16777220 and self.hasFocus() and self.isVisible():
            self.setDown(False)
            self.pressed.emit()
            self.repaint()


class ToolButton(QToolButton, Widget):
    @overload
    def __init__(self, parent=None):
        ...
    
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
    
    def paintEvent(self, a0):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self)
        painter.setOpacity(self.property("widgetOpacity"))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        borderColour = getBorderColour(
            is_highlight=(self.isDown() or self.isChecked()) or
                         ((self.isDown() or self.isChecked() or self.underMouse() or self.hasFocus()) and
                          self.isEnabled())
        )
        backgroundColour = getBackgroundColour(
            is_highlight=(self.isDown() or self.isChecked()) or (
                    (self.isDown() or self.isChecked()) and self.isEnabled())
        )
        painter.save()
        painter.setOpacity((((max(painter.opacity(), 0.6) - 0.6) * 10) / 4))
        borderGradient = QLinearGradient(QPointF(0, 0), QPointF(0, self.height()))
        borderGradient.setColorAt(0.0, Colour(*getBorderColour(), 64))
        borderGradient.setColorAt(1.0, borderColour)
        painter.setPen(QPen(QBrush(borderGradient), 1))
        painter.setBrush(Qt.GlobalColor.transparent)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 12, 12)
        painter.restore()
        painter.save()
        painter.setOpacity(self.property("widgetOpacity"))
        borderGradient = QLinearGradient(QPointF(3, 3), QPointF(3, self.height() - 3))
        borderGradient.setColorAt(0.0, borderColour)
        borderGradient.setColorAt(1.0, Colour(*getBorderColour(), 64))
        backgroundGradient = QLinearGradient(QPointF(3, 3), QPointF(self.width() - 3, 3))
        backgroundGradient.setColorAt(0.0, backgroundColour)
        backgroundGradient.setColorAt(0.5, Colour(*backgroundColour, 230))
        backgroundGradient.setColorAt(1.0, backgroundColour)
        painter.setPen(QPen(QBrush(borderGradient), 1))
        painter.setBrush(QBrush(backgroundGradient))
        painter.drawRoundedRect(self.rect().adjusted(3, 3, -3, -3), 10, 10)
        painter.restore()
        if self.menu():
            painter.save()
            rect = self.rect().adjusted(3, 3, -3, -3)
            x = (rect.width() - 5) - 3 + rect.x()
            y = rect.height() / 2 - 2 + rect.y()
            if self.isDown():
                y += 2
            painter.setPen(QPen(
                QBrush(borderGradient),
                1.0,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin
            ))
            painter.translate(x, y)
            painter.drawLines([QLineF(QPointF(0, 0), QPointF(3, 4)), QLineF(QPointF(3, 4), QPointF(6, 0))])
            painter.restore()
        op = QStyleOptionToolButton()
        op.initFrom(self)
        self.initStyleOption(op)
        op.rect.adjust(4, 4, -4, -4)
        op.palette.setColor(self.foregroundRole(), getForegroundColour())
        self.style().drawControl(QStyle.ControlElement.CE_ToolButtonLabel, op, painter, self)
        self.setStyleSheet("padding: 5px;")
    
    def keyPressEvent(self, *__args):
        super().keyPressEvent(*__args)
        if __args[0].key() == 16777220 and self.hasFocus() and self.isVisible():
            self.setDown(True)
            if self.isCheckable():
                self.setChecked(not self.isChecked())
            self.repaint()
    
    def keyReleaseEvent(self, *__args):
        super().keyReleaseEvent(*__args)
        if __args[0].key() == 16777220 and self.hasFocus() and self.isVisible():
            self.setDown(False)
            self.pressed.emit()
            self.repaint()


class TogglePushButton(PushButton):
    @overload
    def __init__(self, parent=None):
        ...
    
    @overload
    def __init__(self, text, parent=None):
        ...
    
    @overload
    def __init__(self, icon, text, parent=None):
        ...
    
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setCheckable(True)
    
    def toggleState(self):
        return self.isChecked()
    
    def setToggleState(self, value):
        self.setChecked(value)
    
    def keyPressEvent(self, *__args):
        super().keyPressEvent(*__args)
        if __args[0].key() == 16777220 and self.hasFocus() and self.isVisible():
            self.repaint()
    
    def keyReleaseEvent(self, *__args):
        super().keyReleaseEvent(*__args)
        if __args[0].key() == 16777220 and self.hasFocus() and self.isVisible():
            self.setChecked(not self.isChecked())
            self.pressed.emit()
            self.repaint()


class ToggleToolButton(ToolButton):
    @overload
    def __init__(self, parent):
        ...
    
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setCheckable(True)
    
    def toggleState(self):
        return self.isChecked()
    
    def setToggleState(self, value):
        self.setChecked(value)
    
    def keyPressEvent(self, *__args):
        super().keyPressEvent(*__args)
        if __args[0].key() == 16777220 and self.hasFocus() and self.isVisible():
            self.repaint()
    
    def keyReleaseEvent(self, *__args):
        super().keyReleaseEvent(*__args)
        if __args[0].key() == 16777220 and self.hasFocus() and self.isVisible():
            self.setChecked(not self.isChecked())
            self.pressed.emit()
            self.repaint()


class CloseButton(ToolButton):
    @overload
    def __init__(self, parent):
        ...
    
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setFixedSize(QSize(32, 32))
    
    def paintEvent(self, a0):
        super().paintEvent(a0)
        painter = QPainter(self)
        painter.setOpacity(self.property("widgetOpacity"))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getForegroundColour())
        painter.translate(QPointF(self.width() / 4, self.width() / 4))
        painter.drawLines([QLineF(QPointF(0, 0), QPointF(self.width() / 2, self.height() / 2)),
                           QLineF(QPointF(self.width() / 2, 0), QPointF(0, self.height() / 2))])


class CheckBox(QCheckBox, Widget):
    @overload
    def __init__(self, parent=None):
        ...
    
    @overload
    def __init__(self, text, parent=None):
        ...
    
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
    
    def paintEvent(self, a0):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        op = QStyleOptionButton()
        op.initFrom(self)
        self.initStyleOption(op)
        op.rect.adjust(min(5, self.width()), min(5, self.height()), -min(5, self.width()), -min(5, self.height()))
        op.rect.adjust(4, 4, -4, -4)
        painter = QPainter(self)
        painter.setOpacity(self.property("widgetOpacity"))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        borderColour = getBorderColour()
        backgroundColour = getBackgroundColour()
        painter.save()
        painter.setOpacity((((max(painter.opacity(), 0.6) - 0.6) * 10) / 4))
        borderGradient = QLinearGradient(QPointF(0, 0), QPointF(0, self.height()))
        borderGradient.setColorAt(0.0, Colour(*getBorderColour(), 64))
        borderGradient.setColorAt(1.0, borderColour)
        painter.setPen(QPen(QBrush(borderGradient), 1))
        painter.setBrush(Qt.GlobalColor.transparent)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 12, 12)
        painter.restore()
        painter.save()
        painter.setOpacity(self.property("widgetOpacity"))
        borderGradient = QLinearGradient(QPointF(3, 3), QPointF(3, self.height() - 3))
        borderGradient.setColorAt(0.0, borderColour)
        borderGradient.setColorAt(1.0, Colour(*getBorderColour(), 64))
        backgroundGradient = QLinearGradient(QPointF(3, 3), QPointF(self.width() - 3, 3))
        backgroundGradient.setColorAt(0.0, backgroundColour)
        backgroundGradient.setColorAt(0.5, Colour(*backgroundColour, 230))
        backgroundGradient.setColorAt(1.0, backgroundColour)
        painter.setPen(QPen(QBrush(borderGradient), 1))
        painter.setBrush(QBrush(backgroundGradient))
        painter.drawRoundedRect(self.rect().adjusted(3, 3, -3, -3), 10, 10)
        painter.restore()
        rect = self.style().subElementRect(QStyle.SubElement.SE_CheckBoxIndicator, op).adjusted(-2, -2, 2, 2)
        borderColour = getBorderColour(
            is_highlight=(self.isDown() or self.isChecked()) or
                         ((self.isDown() or self.isChecked() or self.underMouse() or self.hasFocus()) and
                          self.isEnabled())
        )
        backgroundColour = getBackgroundColour(
            is_highlight=(self.isDown() or self.isChecked()) or (
                    (self.isDown() or self.isChecked()) and self.isEnabled())
        )
        painter.save()
        painter.setOpacity((((max(painter.opacity(), 0.6) - 0.6) * 10) / 4))
        borderGradient = QLinearGradient(QPointF(rect.x(), rect.y()), QPointF(rect.x(), rect.y() + rect.height()))
        borderGradient.setColorAt(0.0, Colour(*getBorderColour(), 64))
        borderGradient.setColorAt(1.0, borderColour)
        painter.setPen(QPen(QBrush(borderGradient), 1))
        painter.setBrush(Qt.GlobalColor.transparent)
        painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 12, 12)
        painter.restore()
        painter.save()
        painter.setOpacity(self.property("widgetOpacity"))
        borderGradient = QLinearGradient(QPointF(rect.x() + 3, rect.y() + 3),
                                         QPointF(rect.x() + 3, rect.height() - 3 + rect.y()))
        borderGradient.setColorAt(0.0, borderColour)
        borderGradient.setColorAt(1.0, Colour(*getBorderColour(), 64))
        backgroundGradient = QLinearGradient(QPointF(rect.x() + 3, rect.y() + 3),
                                             QPointF(self.width() - 3, 3 + rect.y()))
        backgroundGradient.setColorAt(0.0, backgroundColour)
        backgroundGradient.setColorAt(0.5, Colour(*backgroundColour, 230))
        backgroundGradient.setColorAt(1.0, backgroundColour)
        painter.setPen(QPen(QBrush(borderGradient), 1))
        painter.setBrush(QBrush(backgroundGradient))
        painter.drawRoundedRect(rect.adjusted(3, 3, -3, -3), 10, 10)
        painter.restore()
        painter.save()
        painter.setPen(getForegroundColour())
        painter.setBrush(Qt.GlobalColor.transparent)
        rect = self.style().subElementRect(QStyle.SubElement.SE_CheckBoxIndicator, op).adjusted(1, 1, -1, -1)
        match self.checkState():
            case Qt.CheckState.Checked:
                painter.drawLines([QLine(
                    QPoint(4 + rect.x(), rect.y() + 8),
                    QPoint(rect.width() // 2 + rect.x(), rect.y() + 10)),
                    QLine(
                        QPoint(rect.width() // 2 + rect.x(), rect.y() + 10),
                        QPoint(9 + rect.x(), rect.y() + 4))])
            case Qt.CheckState.PartiallyChecked:
                painter.drawLine(QLine(
                    QPoint(4 + rect.x(), rect.y() + rect.height() // 2),
                    QPoint(rect.x() + rect.width() - 4, rect.y() + rect.height() // 2)
                ))
        painter.restore()
        op.palette.setColor(self.foregroundRole(), getForegroundColour())
        op.rect = self.style().subElementRect(QStyle.SubElement.SE_CheckBoxContents, op)
        self.style().drawControl(QStyle.ControlElement.CE_CheckBoxLabel, op, painter, self)
        self.setStyleSheet("padding: 5px;")
    
    def keyPressEvent(self, *__args):
        super().keyPressEvent(*__args)
        if __args[0].key() == 16777220 and self.hasFocus() and self.isVisible():
            self.repaint()
    
    def keyReleaseEvent(self, *__args):
        super().keyReleaseEvent(*__args)
        if __args[0].key() == 16777220 and self.hasFocus() and self.isVisible():
            self.nextCheckState()
            self.pressed.emit()
            self.repaint()


class RadioButton(QRadioButton, Widget):
    @overload
    def __init__(self, parent=None):
        ...
    
    @overload
    def __init__(self, text, parent=None):
        ...
    
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
    
    def paintEvent(self, a0):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        op = QStyleOptionButton()
        op.initFrom(self)
        self.initStyleOption(op)
        op.rect.adjust(min(5, self.width()), min(5, self.height()), -min(5, self.width()), -min(5, self.height()))
        op.rect.adjust(4, 4, -4, -4)
        painter = QPainter(self)
        painter.setOpacity(self.property("widgetOpacity"))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        borderColour = getBorderColour()
        backgroundColour = getBackgroundColour()
        painter.save()
        painter.setOpacity((((max(painter.opacity(), 0.6) - 0.6) * 10) / 4))
        borderGradient = QLinearGradient(QPointF(0, 0), QPointF(0, self.height()))
        borderGradient.setColorAt(0.0, Colour(*getBorderColour(), 64))
        borderGradient.setColorAt(1.0, borderColour)
        painter.setPen(QPen(QBrush(borderGradient), 1))
        painter.setBrush(Qt.GlobalColor.transparent)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 12, 12)
        painter.restore()
        painter.save()
        painter.setOpacity(self.property("widgetOpacity"))
        borderGradient = QLinearGradient(QPointF(3, 3), QPointF(3, self.height() - 3))
        borderGradient.setColorAt(0.0, borderColour)
        borderGradient.setColorAt(1.0, Colour(*getBorderColour(), 64))
        backgroundGradient = QLinearGradient(QPointF(3, 3), QPointF(self.width() - 3, 3))
        backgroundGradient.setColorAt(0.0, backgroundColour)
        backgroundGradient.setColorAt(0.5, Colour(*backgroundColour, 230))
        backgroundGradient.setColorAt(1.0, backgroundColour)
        painter.setPen(QPen(QBrush(borderGradient), 1))
        painter.setBrush(QBrush(backgroundGradient))
        painter.drawRoundedRect(self.rect().adjusted(3, 3, -3, -3), 10, 10)
        painter.restore()
        rect = self.style().subElementRect(QStyle.SubElement.SE_CheckBoxIndicator, op).adjusted(-2, -2, 2, 2)
        borderColour = getBorderColour(
            is_highlight=(self.isDown() or self.isChecked()) or
                         ((self.isDown() or self.isChecked() or self.underMouse() or self.hasFocus()) and
                          self.isEnabled())
        )
        backgroundColour = getBackgroundColour(
            is_highlight=(self.isDown() or self.isChecked()) or (
                    (self.isDown() or self.isChecked()) and self.isEnabled())
        )
        painter.save()
        painter.setOpacity((((max(painter.opacity(), 0.6) - 0.6) * 10) / 4))
        borderGradient = QLinearGradient(QPointF(rect.x(), rect.y()), QPointF(rect.x(), rect.y() + rect.height()))
        borderGradient.setColorAt(0.0, Colour(*getBorderColour(), 64))
        borderGradient.setColorAt(1.0, borderColour)
        painter.setPen(QPen(QBrush(borderGradient), 1))
        painter.setBrush(Qt.GlobalColor.transparent)
        painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 12, 12)
        painter.restore()
        painter.save()
        painter.setOpacity(self.property("widgetOpacity"))
        borderGradient = QLinearGradient(QPointF(rect.x() + 3, rect.y() + 3),
                                         QPointF(rect.x() + 3, rect.height() - 3 + rect.y()))
        borderGradient.setColorAt(0.0, borderColour)
        borderGradient.setColorAt(1.0, Colour(*getBorderColour(), 64))
        backgroundGradient = QLinearGradient(QPointF(rect.x() + 3, rect.y() + 3),
                                             QPointF(self.width() - 3, 3 + rect.y()))
        backgroundGradient.setColorAt(0.0, backgroundColour)
        backgroundGradient.setColorAt(0.5, Colour(*backgroundColour, 230))
        backgroundGradient.setColorAt(1.0, backgroundColour)
        painter.setPen(QPen(QBrush(borderGradient), 1))
        painter.setBrush(QBrush(backgroundGradient))
        painter.drawRoundedRect(rect.adjusted(3, 3, -3, -3), 10, 10)
        painter.restore()
        op.palette.setColor(self.foregroundRole(), getForegroundColour())
        op.rect = self.style().subElementRect(QStyle.SubElement.SE_RadioButtonContents, op)
        self.style().drawControl(QStyle.ControlElement.CE_RadioButtonLabel, op, painter, self)
        self.setStyleSheet("padding: 5px;")
    
    def keyPressEvent(self, *__args):
        super().keyPressEvent(*__args)
        if __args[0].key() == 16777220 and self.hasFocus() and self.isVisible():
            self.repaint()
    
    def keyReleaseEvent(self, *__args):
        super().keyReleaseEvent(*__args)
        if __args[0].key() == 16777220 and self.hasFocus() and self.isVisible():
            self.setChecked(not self.isChecked())
            self.pressed.emit()
            self.repaint()


class SwitchButton(QAbstractButton, Widget):
    switched = pyqtSignal(bool)
    
    @overload
    def __init__(self, parent=None):
        ...
    
    @overload
    def __init__(self, on, parent=None):
        ...
    
    @overload
    def __init__(self, on, off, parent=None):
        ...
    
    def __init__(self, *__args):
        super().__init__(__args[-1])
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.setCheckable(True)
        self.setProperty("switchOnText", __args[0] if len(__args) > 2 else "On")
        self.setProperty("switchOffText", __args[1] if len(__args) > 2 else "Off")
        self.setMinimumSize(52, 24)
    
    def switchOnText(self):
        return self.property("switchOnText")
    
    def setSwitchOnText(self, text):
        self.setProperty("switchOnText", text)
    
    def switchOffText(self):
        return self.property("switchOffText")
    
    def setSwitchOffText(self, text):
        self.setProperty("switchOffText", text)
    
    def setText(self, text):
        if self.isChecked():
            self.setSwitchOnText(text)
        else:
            self.setSwitchOffText(text)
    
    def switchState(self):
        return self.isChecked()
    
    def setSwitchState(self, state):
        self.setChecked(state)
    
    def paintEvent(self, a0):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setMinimumSize(52 + 2 + max(self.fontMetrics().boundingRect(
            self.switchOnText()).width(), self.fontMetrics().boundingRect(
            self.switchOffText()).width()) + 6, 24 + 6)
        painter = QPainter(self)
        painter.setOpacity(self.property("widgetOpacity"))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        borderColour = getBorderColour()
        backgroundColour = getBackgroundColour()
        outerRect = QRect(1, (self.height() - 27) // 2, 50, 27)
        painter.save()
        painter.setOpacity((((max(painter.opacity(), 0.6) - 0.6) * 10) / 4))
        borderGradient = QLinearGradient(QPointF(outerRect.x(), outerRect.y()),
                                         QPointF(outerRect.x(), outerRect.y() + self.height()))
        borderGradient.setColorAt(0.0, Colour(*getBorderColour(), 64))
        borderGradient.setColorAt(1.0, borderColour)
        painter.setPen(QPen(QBrush(borderGradient), 1))
        painter.setBrush(Qt.GlobalColor.transparent)
        painter.drawRoundedRect(outerRect.adjusted(1, 1, -1, -1), self.height() // 2 - 1, self.height() // 2 - 1)
        painter.restore()
        painter.save()
        painter.setOpacity(self.property("widgetOpacity"))
        borderGradient = QLinearGradient(QPointF(outerRect.x() + 3, outerRect.y() + 3),
                                         QPointF(outerRect.x() + 3, outerRect.y() + self.height() - 3))
        borderGradient.setColorAt(0.0, borderColour)
        borderGradient.setColorAt(1.0, Colour(*getBorderColour(), 64))
        backgroundGradient = QLinearGradient(QPointF(outerRect.x() + 3, outerRect.y() + 3),
                                             QPointF(outerRect.x() + self.width() - 3, outerRect.y() + 3))
        backgroundGradient.setColorAt(0.0, backgroundColour)
        backgroundGradient.setColorAt(0.5, Colour(*backgroundColour, 230))
        backgroundGradient.setColorAt(1.0, backgroundColour)
        painter.setPen(QPen(QBrush(borderGradient), 1))
        painter.setBrush(QBrush(backgroundGradient))
        painter.drawRoundedRect(outerRect.adjusted(3, 3, -3, -3), self.height() // 2 - 3, self.height() // 2 - 3)
        painter.restore()
        rect = QRect(3 if not self.isChecked() else outerRect.width() - 4 - 22, (self.height() - 27) // 2 + 2, 23, 23)
        borderColour = getBorderColour(
            is_highlight=(self.isDown() or self.isChecked()) or
                         ((self.isDown() or self.isChecked() or self.underMouse() or self.hasFocus()) and
                          self.isEnabled())
        )
        backgroundColour = getBackgroundColour(
            is_highlight=(self.isDown() or self.isChecked()) or (
                    (self.isDown() or self.isChecked()) and self.isEnabled())
        )
        painter.save()
        painter.setOpacity((((max(painter.opacity(), 0.6) - 0.6) * 10) / 4))
        borderGradient = QLinearGradient(QPointF(rect.x(), rect.y()), QPointF(rect.x(), rect.y() + rect.height()))
        borderGradient.setColorAt(0.0, Colour(*getBorderColour(), 64))
        borderGradient.setColorAt(1.0, borderColour)
        painter.setPen(QPen(QBrush(borderGradient), 1))
        painter.setBrush(Qt.GlobalColor.transparent)
        painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 12, 12)
        painter.restore()
        painter.save()
        painter.setOpacity(self.property("widgetOpacity"))
        borderGradient = QLinearGradient(QPointF(rect.x() + 3, rect.y() + 3),
                                         QPointF(rect.x() + 3, rect.height() - 3 + rect.y()))
        borderGradient.setColorAt(0.0, borderColour)
        borderGradient.setColorAt(1.0, Colour(*getBorderColour(), 64))
        backgroundGradient = QLinearGradient(QPointF(rect.x() + 3, rect.y() + 3),
                                             QPointF(self.width() - 3, 3 + rect.y()))
        backgroundGradient.setColorAt(0.0, backgroundColour)
        backgroundGradient.setColorAt(0.5, Colour(*backgroundColour, 230))
        backgroundGradient.setColorAt(1.0, backgroundColour)
        painter.setPen(QPen(QBrush(borderGradient), 1))
        painter.setBrush(QBrush(backgroundGradient))
        painter.drawRoundedRect(rect.adjusted(3, 3, -3, -3), 10, 10)
        painter.restore()
        painter.setPen(getForegroundColour())
        painter.setBrush(Qt.GlobalColor.transparent)
        painter.drawText(QRect(54, 0, self.width() - 52, self.height()), Qt.AlignmentFlag.AlignCenter,
                         self.switchOnText() if self.isChecked() else self.switchOffText())
        self.setStyleSheet("padding: 5px;")
    
    def keyPressEvent(self, *__args):
        super().keyPressEvent(*__args)
        if __args[0].key() == 16777220 and self.hasFocus() and self.isVisible():
            self.repaint()
    
    def keyReleaseEvent(self, *__args):
        super().keyReleaseEvent(*__args)
        if __args[0].key() == 16777220 and self.hasFocus() and self.isVisible():
            self.setChecked(not self.isChecked())
            self.pressed.emit()
            self.switched.emit(self.isChecked())
            self.repaint()
