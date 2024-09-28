# -*- coding: utf-8 -*-
from typing import overload

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from .CWMThemeControl import *
from .CWMToolTip import ToolTip


class PushButton(QPushButton):
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
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.installEventFilter(ToolTip(self))
    
    def paintEvent(self, a0):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self)
        painter.setOpacity(1.0 if self.underMouse() or self.hasFocus() else 0.6)
        if not self.isEnabled():
            painter.setOpacity(0.3)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getBorderColour(
            highlight=(self.isDown() or self.isChecked() or self.underMouse() or self.hasFocus()) and self.isEnabled()))
        painter.setBrush(getBackgroundColour(highlight=(self.isDown() or self.isChecked()) and self.isEnabled()))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)
        if self.menu():
            painter.save()
            painter.setPen(QPen(getBorderColour(
                highlight=self.isEnabled()) if self.isDown() or self.isChecked() or self.hasFocus() or self.underMouse() else getForegroundColour(),
                                1.0,
                                Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            painter.setBrush(
                getBorderColour(
                    highlight=self.isEnabled()) if self.isDown() or self.isChecked() else getForegroundColour())
            painter.translate((self.width() - 8) - 3, self.height() / 2 - 4)
            painter.drawPolygon([QPoint(0, 0), QPoint(4, 8), QPoint(8, 0)])
            painter.restore()
        op = QStyleOptionButton()
        op.initFrom(self)
        self.initStyleOption(op)
        op.palette.setColor(self.foregroundRole(), getForegroundColour())
        self.style().drawControl(QStyle.ControlElement.CE_PushButtonLabel, op, painter, self)
        self.setStyleSheet("padding: 5px;")
    
    def keyPressEvent(self, *__args):
        super().keyPressEvent(*__args)
        if __args[0].key() == 16777220 and self.hasFocus() and self.isVisible():
            self.setDown(True)
            self.repaint()
    
    def keyReleaseEvent(self, *__args):
        super().keyReleaseEvent(*__args)
        if __args[0].key() == 16777220 and self.hasFocus() and self.isVisible():
            self.setDown(False)
            self.pressed.emit()
            self.repaint()


class ToolButton(QToolButton):
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.installEventFilter(ToolTip(self))
    
    def paintEvent(self, a0):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self)
        painter.setOpacity(1.0 if self.underMouse() or self.hasFocus() else 0.6)
        if not self.isEnabled():
            painter.setOpacity(0.3)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getBorderColour(
            highlight=(self.isDown() or self.isChecked() or self.underMouse() or self.hasFocus()) and self.isEnabled()))
        painter.setBrush(getBackgroundColour(highlight=(self.isDown() or self.isChecked()) and self.isEnabled()))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)
        if self.menu():
            painter.save()
            painter.setPen(QPen(getBorderColour(
                highlight=self.isEnabled()) if self.isDown() or self.isChecked() or self.hasFocus() or self.underMouse() else getForegroundColour(),
                                1.0,
                                Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            painter.setBrush(
                getBorderColour(
                    highlight=self.isEnabled()) if self.isDown() or self.isChecked() else getForegroundColour())
            painter.translate((self.width() - 8) - 3, self.height() / 2 - 4)
            painter.drawPolygon([QPoint(0, 0), QPoint(4, 8), QPoint(8, 0)])
            painter.restore()
        op = QStyleOptionToolButton()
        op.initFrom(self)
        self.initStyleOption(op)
        op.palette.setColor(self.foregroundRole(), getForegroundColour())
        self.style().drawControl(QStyle.ControlElement.CE_ToolButtonLabel, op, painter, self)
        self.setStyleSheet("padding: 5px;")
    
    def keyPressEvent(self, *__args):
        super().keyPressEvent(*__args)
        if __args[0].key() == 16777220 and self.hasFocus() and self.isVisible():
            self.setDown(True)
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
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setFixedSize(QSize(32, 32))
    
    def paintEvent(self, a0):
        super().paintEvent(a0)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getForegroundColour())
        painter.translate(QPoint(8, 8))
        painter.drawLines([QLine(QPoint(0, 0), QPoint(16, 16)), QLine(QPoint(16, 0), QPoint(0, 16))])


class CheckBox(QCheckBox):
    @overload
    def __init__(self, parent=None):
        ...
    
    @overload
    def __init__(self, text, parent=None):
        ...
    
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.installEventFilter(ToolTip(self))
    
    def paintEvent(self, a0):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self)
        painter.setOpacity(1.0 if self.underMouse() or self.hasFocus() else 0.6)
        if not self.isEnabled():
            painter.setOpacity(0.3)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getBorderColour())
        painter.setBrush(getBackgroundColour())
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)
        painter.setPen(getBorderColour(
            highlight=(self.isDown() or self.isChecked()) or ((
                                                                      self.isDown() or self.isChecked() or self.underMouse() or self.hasFocus()) and self.isEnabled())))
        painter.setBrush(getBackgroundColour(highlight=(self.isDown() or self.isChecked()) or (
                (self.isDown() or self.isChecked()) and self.isEnabled())))
        painter.drawRoundedRect(QRect(1, (self.height() - 24) // 2, 24, 24), 10, 10)
        painter.save()
        painter.setPen(getForegroundColour())
        painter.setBrush(Qt.GlobalColor.transparent)
        match self.checkState():
            case Qt.CheckState.Checked:
                painter.drawLines([QLine(
                    QPoint(6 + 1, ((self.height() - 24) // 2) + 12),
                    QPoint(12 + 1, ((self.height() - 24) // 2) + 18)),
                    QLine(
                        QPoint(12 + 1, ((self.height() - 24) // 2) + 18),
                        QPoint(18 + 1, ((self.height() - 24) // 2) + 6))])
            case Qt.CheckState.PartiallyChecked:
                painter.drawLine(QLine(
                    QPoint(6 + 1, ((self.height() - 24) // 2) + 12),
                    QPoint(18 + 1, ((self.height() - 24) // 2) + 12)
                ))
        painter.restore()
        op = QStyleOptionButton()
        op.initFrom(self)
        self.initStyleOption(op)
        op.palette.setColor(self.foregroundRole(), getForegroundColour())
        op.rect.setX(28)
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


class RadioButton(QRadioButton):
    @overload
    def __init__(self, parent=None):
        ...
    
    @overload
    def __init__(self, text, parent=None):
        ...
    
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.installEventFilter(ToolTip(self))
    
    def paintEvent(self, a0):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self)
        painter.setOpacity(1.0 if self.underMouse() or self.hasFocus() else 0.6)
        if not self.isEnabled():
            painter.setOpacity(0.3)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getBorderColour())
        painter.setBrush(getBackgroundColour())
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)
        painter.setPen(getBorderColour(
            highlight=(self.isDown() or self.isChecked()) or ((
                                                                      self.isDown() or self.isChecked() or self.underMouse() or self.hasFocus()) and self.isEnabled())))
        painter.setBrush(getBackgroundColour(highlight=(self.isDown() or self.isChecked()) or (
                (self.isDown() or self.isChecked()) and self.isEnabled())))
        painter.drawRoundedRect(QRect(1, (self.height() - 24) // 2, 24, 24), 10, 10)
        op = QStyleOptionButton()
        op.initFrom(self)
        self.initStyleOption(op)
        op.palette.setColor(self.foregroundRole(), getForegroundColour())
        op.rect.setX(28)
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


class SwitchButton(QAbstractButton):
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
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.installEventFilter(ToolTip(self))
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
            self.switchOffText()).width()), 24)
        painter = QPainter(self)
        painter.setOpacity(1.0 if self.underMouse() or self.hasFocus() else 0.6)
        if not self.isEnabled():
            painter.setOpacity(0.3)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(getBorderColour())
        painter.setBrush(getBackgroundColour())
        painter.drawRoundedRect(QRect(1, (self.height() - 22) // 2, 50, 21),
                                self.height() // 2 - 1, self.height() // 2 - 1)
        painter.setPen(getBorderColour(
            highlight=(self.isDown() or self.isChecked()) or ((
                                                                      self.isDown() or self.isChecked() or self.underMouse() or self.hasFocus()) and self.isEnabled())))
        painter.setBrush(getBackgroundColour(highlight=(self.isDown() or self.isChecked()) or (
                (self.isDown() or self.isChecked()) and self.isEnabled())))
        painter.drawEllipse(QRect(3 if not self.isChecked() else 49 - 17, (self.height() - 22) // 2 + 2, 17, 17))
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
