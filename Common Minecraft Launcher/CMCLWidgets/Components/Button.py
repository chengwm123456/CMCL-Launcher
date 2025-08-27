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
        
        self.setProperty("dropdownIndicatorRotation", 0.0)
    
    def paintEvent(self, a0):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.save()
        painter.setOpacity(self.property("baseOpacity"))
        painter.setPen(getBorderColour(
            is_highlight=(self.isDown() or self.isChecked()) or (
                    (self.isDown() or self.isChecked()) and self.isEnabled())
        ))
        painter.setBrush(getBackgroundColour(
            is_highlight=(self.isDown() or self.isChecked()) or (
                    (self.isDown() or self.isChecked()) and self.isEnabled())
        ))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 16, 16)
        painter.restore()
        
        if self.property("frameOpacity"):
            painter.save()
            painter.setOpacity(self.property("frameOpacity"))
            painter.setPen(getBorderColour(is_highlight=True))
            painter.setBrush(getBackgroundColour(
                is_highlight=(self.isDown() or self.isChecked()) or (
                        (self.isDown() or self.isChecked()) and self.isEnabled())
            ))
            painter.drawRoundedRect(
                self.rect().adjusted(
                    1 + self.property("frameRectAdjustment"),
                    1 + self.property("frameRectAdjustment"),
                    -(1 + self.property("frameRectAdjustment")),
                    -(1 + self.property("frameRectAdjustment"))
                ), 16, 16
            )
            painter.restore()
        
        if self.menu():
            painter.save()
            x = (self.width() - 8) - 3 + 4
            y = self.height() / 2 - 2 + 2
            painter.setOpacity(self.property("baseOpacity"))
            painter.setPen(getBorderColour(
                is_highlight=(self.isDown() or self.isChecked()) or (
                        (self.isDown() or self.isChecked()) and self.isEnabled())
            ))
            painter.translate(x, y)
            painter.rotate(self.property("dropdownIndicatorRotation"))
            painter.drawLines([QLineF(QPointF(-4, -2), QPointF(0, 2)), QLineF(QPointF(0, 2), QPointF(4, -2))])
            painter.restore()
            
            if self.property("frameOpacity"):
                painter.save()
                rect2 = self.rect().adjusted(
                    self.property("frameRectAdjustment"),
                    self.property("frameRectAdjustment"),
                    -self.property("frameRectAdjustment"),
                    -self.property("frameRectAdjustment")
                )
                adjustmentScaleRatio = 1 - (self.property("frameRectAdjustment") / min(
                    32, min(self.width() // 2, self.height() // 2)))
                x2 = (rect2.width() - 8) - 3 + 4 + rect2.x()
                y2 = rect2.height() / 2 - 2 + 2 + rect2.y()
                painter.setOpacity(self.property("frameOpacity"))
                painter.setPen(getBorderColour(is_highlight=True))
                painter.translate(x2, y2)
                painter.rotate(self.property("dropdownIndicatorRotation"))
                painter.drawLines(
                    [
                        QLineF(QPointF(-4 * adjustmentScaleRatio, -2 * adjustmentScaleRatio),
                               QPointF(0, 2 * adjustmentScaleRatio)),
                        QLineF(QPointF(0, 2 * adjustmentScaleRatio),
                               QPointF(4 * adjustmentScaleRatio, -2 * adjustmentScaleRatio))
                    ]
                )
                painter.restore()
        
        op = QStyleOptionButton()
        op.initFrom(self)
        self.initStyleOption(op)
        op.palette.setColor(self.foregroundRole(), getForegroundColour())
        painter.save()
        painter.setOpacity(
            self.property("baseOpacity") + (self.property("frameOpacity") * (1.0 - self.property("baseOpacity"))))
        self.style().drawControl(QStyle.ControlElement.CE_PushButtonLabel, op, painter, self)
        painter.restore()
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
    
    def mousePressEvent(self, a0):
        super().mousePressEvent(a0)
        if self.menu():
            def closeFunc():
                rotationAnimation = QPropertyAnimation(self, b"dropdownIndicatorRotation", self)
                rotationAnimation.setStartValue(self.property("dropdownIndicatorRotation"))
                rotationAnimation.setEndValue(0.0)
                rotationAnimation.setDuration(500)
                rotationAnimation.setEasingCurve(QEasingCurve.Type.OutExpo)
                rotationAnimation.start()
                self.menu().aboutToHide.disconnect(closeFunc)
            
            rotationAnimation = QPropertyAnimation(self, b"dropdownIndicatorRotation", self)
            rotationAnimation.setStartValue(self.property("dropdownIndicatorRotation"))
            rotationAnimation.setEndValue(180.0)
            rotationAnimation.setDuration(500)
            rotationAnimation.setEasingCurve(QEasingCurve.Type.OutExpo)
            rotationAnimation.start()
            self.menu().aboutToHide.connect(closeFunc)


class CommandLinkButton(QCommandLinkButton, PushButton):
    pass


class ToolButton(QToolButton, Widget):
    @overload
    def __init__(self, parent=None):
        ...
    
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        
        self.setProperty("dropdownIndicatorRotation", 0.0)
    
    def paintEvent(self, a0):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.save()
        painter.setOpacity(self.property("baseOpacity"))
        painter.setPen(getBorderColour(
            is_highlight=(self.isDown() or self.isChecked()) or (
                    (self.isDown() or self.isChecked()) and self.isEnabled())
        ))
        painter.setBrush(getBackgroundColour(
            is_highlight=(self.isDown() or self.isChecked()) or (
                    (self.isDown() or self.isChecked()) and self.isEnabled())
        ))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 16, 16)
        painter.restore()
        
        if self.property("frameOpacity"):
            painter.save()
            painter.setOpacity(self.property("frameOpacity"))
            painter.setPen(getBorderColour(is_highlight=True))
            painter.setBrush(getBackgroundColour(
                is_highlight=(self.isDown() or self.isChecked()) or (
                        (self.isDown() or self.isChecked()) and self.isEnabled())
            ))
            painter.drawRoundedRect(
                self.rect().adjusted(
                    1 + self.property("frameRectAdjustment"),
                    1 + self.property("frameRectAdjustment"),
                    -(1 + self.property("frameRectAdjustment")),
                    -(1 + self.property("frameRectAdjustment"))
                ), 16, 16
            )
            painter.restore()
        
        if self.menu():
            painter.save()
            x = (self.width() - 8) - 3 + 4
            y = self.height() / 2 - 2 + 2
            painter.setOpacity(self.property("baseOpacity"))
            painter.setPen(getBorderColour(
                is_highlight=(self.isDown() or self.isChecked()) or (
                        (self.isDown() or self.isChecked()) and self.isEnabled())
            ))
            painter.translate(x, y)
            painter.rotate(self.property("dropdownIndicatorRotation"))
            painter.drawLines([QLineF(QPointF(-4, -2), QPointF(0, 2)), QLineF(QPointF(0, 2), QPointF(4, -2))])
            painter.restore()
            
            if self.property("frameOpacity"):
                painter.save()
                rect2 = self.rect().adjusted(
                    self.property("frameRectAdjustment"),
                    self.property("frameRectAdjustment"),
                    -self.property("frameRectAdjustment"),
                    -self.property("frameRectAdjustment")
                )
                adjustmentScaleRatio = 1 - (self.property("frameRectAdjustment") / min(
                    32, min(self.width() // 2, self.height() // 2)))
                x2 = (rect2.width() - 8) - 3 + 4 + rect2.x()
                y2 = rect2.height() / 2 - 2 + 2 + rect2.y()
                painter.setOpacity(self.property("frameOpacity"))
                painter.setPen(getBorderColour(is_highlight=True))
                painter.translate(x2, y2)
                painter.rotate(self.property("dropdownIndicatorRotation"))
                painter.drawLines(
                    [
                        QLineF(QPointF(-4 * adjustmentScaleRatio, -2 * adjustmentScaleRatio),
                               QPointF(0, 2 * adjustmentScaleRatio)),
                        QLineF(QPointF(0, 2 * adjustmentScaleRatio),
                               QPointF(4 * adjustmentScaleRatio, -2 * adjustmentScaleRatio))
                    ]
                )
                painter.restore()
        
        op = QStyleOptionToolButton()
        op.initFrom(self)
        self.initStyleOption(op)
        op.palette.setColor(self.foregroundRole(), getForegroundColour())
        painter.save()
        painter.setOpacity(
            self.property("baseOpacity") + (self.property("frameOpacity") * (1.0 - self.property("baseOpacity"))))
        self.style().drawControl(QStyle.ControlElement.CE_ToolButtonLabel, op, painter, self)
        painter.restore()
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
    
    def mousePressEvent(self, a0):
        super().mousePressEvent(a0)
        if self.menu():
            def closeFunc():
                rotationAnimation = QPropertyAnimation(self, b"dropdownIndicatorRotation", self)
                rotationAnimation.setStartValue(self.property("dropdownIndicatorRotation"))
                rotationAnimation.setEndValue(0.0)
                rotationAnimation.setDuration(500)
                rotationAnimation.setEasingCurve(QEasingCurve.Type.OutExpo)
                rotationAnimation.start()
                self.menu().aboutToHide.disconnect(closeFunc)
            
            rotationAnimation = QPropertyAnimation(self, b"dropdownIndicatorRotation", self)
            rotationAnimation.setStartValue(self.property("dropdownIndicatorRotation"))
            rotationAnimation.setEndValue(180.0)
            rotationAnimation.setDuration(500)
            rotationAnimation.setEasingCurve(QEasingCurve.Type.OutExpo)
            rotationAnimation.start()
            self.menu().aboutToHide.connect(closeFunc)


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
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.save()
        painter.setOpacity(
            self.property("baseOpacity") + (self.property("frameOpacity") * (1.0 - self.property("baseOpacity"))))
        painter.setPen(getForegroundColour())
        painter.translate(QPointF(self.width() / 4, self.width() / 4))
        painter.drawLines([QLineF(QPointF(0, 0), QPointF(self.width() / 2, self.height() / 2)),
                           QLineF(QPointF(self.width() / 2, 0), QPointF(0, self.height() / 2))])
        painter.restore()


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
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.save()
        painter.setOpacity(self.property("baseOpacity"))
        painter.setPen(getBorderColour())
        painter.setBrush(getBackgroundColour())
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 16, 16)
        painter.restore()
        
        if self.property("frameOpacity"):
            painter.save()
            painter.setOpacity(self.property("frameOpacity"))
            painter.setPen(getBorderColour())
            painter.setBrush(getBackgroundColour())
            painter.drawRoundedRect(
                self.rect().adjusted(
                    1 + self.property("frameRectAdjustment"),
                    1 + self.property("frameRectAdjustment"),
                    -(1 + self.property("frameRectAdjustment")),
                    -(1 + self.property("frameRectAdjustment"))
                ), 16, 16
            )
            painter.restore()
        
        rect = self.style().subElementRect(QStyle.SubElement.SE_CheckBoxIndicator, op).adjusted(1, 1, -1, -1)
        painter.save()
        painter.setOpacity(self.property("baseOpacity"))
        painter.setPen(getBorderColour(
            is_highlight=(self.isDown() or self.isChecked()) or (
                    (self.isDown() or self.isChecked()) and self.isEnabled())
        ))
        painter.setBrush(getBackgroundColour(
            is_highlight=(self.isDown() or self.isChecked()) or (
                    (self.isDown() or self.isChecked()) and self.isEnabled())
        ))
        painter.drawRoundedRect(rect, 16, 16)
        painter.restore()
        if self.property("frameOpacity"):
            painter.save()
            op2 = QStyleOptionButton()
            op2.initFrom(self)
            self.initStyleOption(op2)
            op2.rect = self.rect().adjusted(
                self.property("frameRectAdjustment"),
                self.property("frameRectAdjustment"),
                -self.property("frameRectAdjustment"),
                -self.property("frameRectAdjustment")
            )
            op2.rect.adjust(min(5, self.width()), min(5, self.height()), -min(5, self.width()), -min(5, self.height()))
            rect2 = self.style().subElementRect(QStyle.SubElement.SE_CheckBoxIndicator, op2).adjusted(1, 1, -1, -1)
            adjustmentScaleRatio = min(rect2.width() // 2, rect2.height() // 2) / min(
                32, min(self.width() // 2, self.height() // 2))
            rect2.adjust(
                int(self.property("frameRectAdjustment") * adjustmentScaleRatio),
                int(self.property("frameRectAdjustment") * adjustmentScaleRatio),
                -int(self.property("frameRectAdjustment") * adjustmentScaleRatio),
                -int(self.property("frameRectAdjustment") * adjustmentScaleRatio)
            )
            painter.setOpacity(self.property("frameOpacity"))
            painter.setPen(getBorderColour(is_highlight=True))
            painter.setBrush(getBackgroundColour(
                is_highlight=(self.isDown() or self.isChecked()) or (
                        (self.isDown() or self.isChecked()) and self.isEnabled())
            ))
            painter.drawRoundedRect(rect2, 16, 16)
            painter.restore()
        
        painter.save()
        painter.setPen(getForegroundColour())
        painter.setBrush(Qt.GlobalColor.transparent)
        match self.checkState():
            case Qt.CheckState.Checked:
                painter.setOpacity(self.property("baseOpacity"))
                painter.drawLines([
                    QLine(QPoint(4 + rect.x(), rect.y() + 8), QPoint(rect.width() // 2 + rect.x(), rect.y() + 10)),
                    QLine(QPoint(rect.width() // 2 + rect.x(), rect.y() + 10), QPoint(9 + rect.x(), rect.y() + 4))
                ])
                if self.property("frameOpacity"):
                    painter.setOpacity(self.property("frameOpacity"))
                    painter.drawLines([
                        QLine(QPoint(4 + rect2.x(), rect2.y() + 8),
                              QPoint(rect2.width() // 2 + rect2.x(), rect2.y() + 10)),
                        QLine(QPoint(rect2.width() // 2 + rect2.x(), rect2.y() + 10),
                              QPoint(9 + rect2.x(), rect2.y() + 4))
                    ])
            case Qt.CheckState.PartiallyChecked:
                painter.setOpacity(self.property("baseOpacity"))
                painter.drawLine(QLine(
                    QPoint(4 + rect.x(), rect.y() + rect.height() // 2),
                    QPoint(rect.x() + rect.width() - 4, rect.y() + rect.height() // 2)
                ))
                if self.property("frameOpacity"):
                    painter.setOpacity(self.property("frameOpacity"))
                    painter.drawLine(QLine(
                        QPoint(4 + rect2.x(), rect2.y() + rect2.height() // 2),
                        QPoint(rect2.x() + rect2.width() - 4, rect2.y() + rect2.height() // 2)
                    ))
        painter.restore()
        painter.save()
        op.palette.setColor(self.foregroundRole(), getForegroundColour())
        op.rect = self.style().subElementRect(QStyle.SubElement.SE_CheckBoxContents, op)
        painter.setOpacity(
            self.property("baseOpacity") + (self.property("frameOpacity") * (1.0 - self.property("baseOpacity"))))
        self.style().drawControl(QStyle.ControlElement.CE_CheckBoxLabel, op, painter, self)
        painter.restore()
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
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.save()
        painter.setOpacity(self.property("baseOpacity"))
        painter.setPen(getBorderColour())
        painter.setBrush(getBackgroundColour())
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 16, 16)
        painter.restore()
        
        if self.property("frameOpacity"):
            painter.save()
            painter.setOpacity(self.property("frameOpacity"))
            painter.setPen(getBorderColour())
            painter.setBrush(getBackgroundColour())
            painter.drawRoundedRect(
                self.rect().adjusted(
                    1 + self.property("frameRectAdjustment"),
                    1 + self.property("frameRectAdjustment"),
                    -(1 + self.property("frameRectAdjustment")),
                    -(1 + self.property("frameRectAdjustment"))
                ), 16, 16
            )
            painter.restore()
        
        rect = self.style().subElementRect(QStyle.SubElement.SE_RadioButtonIndicator, op).adjusted(1, 1, -1, -1)
        painter.save()
        painter.setOpacity(self.property("baseOpacity"))
        painter.setPen(getBorderColour(
            is_highlight=(self.isDown() or self.isChecked()) or (
                    (self.isDown() or self.isChecked()) and self.isEnabled())
        ))
        painter.setBrush(getBackgroundColour(
            is_highlight=(self.isDown() or self.isChecked()) or (
                    (self.isDown() or self.isChecked()) and self.isEnabled())
        ))
        painter.drawRoundedRect(rect, 16, 16)
        painter.restore()
        if self.property("frameOpacity"):
            painter.save()
            op2 = QStyleOptionButton()
            op2.initFrom(self)
            self.initStyleOption(op2)
            op2.rect = self.rect().adjusted(
                self.property("frameRectAdjustment"),
                self.property("frameRectAdjustment"),
                -self.property("frameRectAdjustment"),
                -self.property("frameRectAdjustment")
            )
            op2.rect.adjust(min(5, self.width()), min(5, self.height()), -min(5, self.width()), -min(5, self.height()))
            rect2 = self.style().subElementRect(QStyle.SubElement.SE_CheckBoxIndicator, op2).adjusted(1, 1, -1, -1)
            adjustmentScaleRatio = min(rect2.width() // 2, rect2.height() // 2) / min(
                32, min(self.width() // 2, self.height() // 2))
            rect2.adjust(
                int(self.property("frameRectAdjustment") * adjustmentScaleRatio),
                int(self.property("frameRectAdjustment") * adjustmentScaleRatio),
                -int(self.property("frameRectAdjustment") * adjustmentScaleRatio),
                -int(self.property("frameRectAdjustment") * adjustmentScaleRatio)
            )
            painter.setOpacity(self.property("frameOpacity"))
            painter.setPen(getBorderColour(is_highlight=True))
            painter.setBrush(getBackgroundColour(
                is_highlight=(self.isDown() or self.isChecked()) or (
                        (self.isDown() or self.isChecked()) and self.isEnabled())
            ))
            painter.drawRoundedRect(rect2, 16, 16)
            painter.restore()
        painter.save()
        op.palette.setColor(self.foregroundRole(), getForegroundColour())
        op.rect = self.style().subElementRect(QStyle.SubElement.SE_RadioButtonContents, op)
        painter.setOpacity(
            self.property("baseOpacity") + (self.property("frameOpacity") * (1.0 - self.property("baseOpacity"))))
        self.style().drawControl(QStyle.ControlElement.CE_RadioButtonLabel, op, painter, self)
        painter.restore()
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
        super().__init__(*__args[-1:])
        self.setCheckable(True)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.setProperty("switchOnText", __args[0] if len(__args) > 2 else self.tr("On"))
        self.setProperty("switchOffText", __args[1] if len(__args) > 2 else self.tr("Off"))
        self.setProperty("textPrefix", "")
        self.setProperty("textSuffix", "")
        self.setMinimumSize(52, 24)
    
    def switchOnText(self):
        return self.property("switchOnText")
    
    def setSwitchOnText(self, text):
        self.setProperty("switchOnText", text)
    
    def switchOffText(self):
        return self.property("switchOffText")
    
    def setSwitchOffText(self, text):
        self.setProperty("switchOffText", text)
    
    def textPrefix(self):
        return self.property("textPrefix")
    
    def setTextPrefix(self, text):
        self.setProperty("textPrefix", text)
    
    def textSuffix(self):
        return self.property("textSuffix")
    
    def setTextSuffix(self, text):
        self.setProperty("textSuffix", text)
    
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
        self.setMinimumSize(
            52 + 2 + max(
                self.fontMetrics().boundingRect(self.switchOnText()).width(),
                self.fontMetrics().boundingRect(self.switchOffText()).width()
            ),
            24
        )
        rectAdjustmentRatio = min(1, 10 / min(32, min(self.width() // 2, self.height() // 2)))
        outerRect = QRect(1, (self.height() - 22) // 2, 50, 21)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # TODO: rewrite this thing / 重写这个鬼东西 (Note: Half-rewrote but still need rewrite / 虽说半重写过了，但是还要重写)
        painter.save()
        painter.setOpacity(self.property("baseOpacity"))
        painter.setPen(getBorderColour())
        painter.setBrush(getBackgroundColour())
        painter.drawRoundedRect(outerRect, outerRect.height() // 2 + 1, outerRect.height() // 2 + 1)
        painter.restore()
        
        if self.property("frameOpacity"):
            rect2 = outerRect.adjusted(
                int(self.property("frameRectAdjustment") * rectAdjustmentRatio),
                int(self.property("frameRectAdjustment") * rectAdjustmentRatio),
                -int(self.property("frameRectAdjustment") * rectAdjustmentRatio),
                -int(self.property("frameRectAdjustment") * rectAdjustmentRatio)
            )
            painter.save()
            painter.setOpacity(self.property("frameOpacity"))
            painter.setPen(getBorderColour())
            painter.setBrush(getBackgroundColour())
            painter.drawRoundedRect(rect2, rect2.height() // 2 + 1, rect2.height() // 2 + 1)
            painter.restore()
        rect = QRect(3 if not self.isChecked() else 49 - 17, (self.height() - 22) // 2 + 2, 17, 17)
        painter.save()
        painter.setOpacity(self.property("baseOpacity"))
        painter.setPen(getBorderColour(
            is_highlight=(self.isDown() or self.isChecked()) or
                         ((self.isDown() or self.isChecked()) and
                          self.isEnabled())
        ))
        painter.setBrush(getBackgroundColour(
            is_highlight=(self.isDown() or self.isChecked()) or (
                    (self.isDown() or self.isChecked()) and self.isEnabled())
        ))
        painter.drawEllipse(rect)
        painter.restore()
        if self.property("frameOpacity"):
            or2 = outerRect.adjusted(
                int(self.property("frameRectAdjustment") * rectAdjustmentRatio),
                int(self.property("frameRectAdjustment") * rectAdjustmentRatio),
                -int(self.property("frameRectAdjustment") * rectAdjustmentRatio),
                -int(self.property("frameRectAdjustment") * rectAdjustmentRatio)
            )
            rect2 = QRect(
                or2.x() + 2 if not self.isChecked() else or2.x() + or2.width() - 2 - round(
                    17 * self.property("frameOpacity")),
                or2.y() + 2,
                round(17 * self.property("frameOpacity")),
                round(17 * self.property("frameOpacity"))
            )
            painter.save()
            painter.setOpacity(self.property("frameOpacity"))
            painter.setPen(getBorderColour(is_highlight=True))
            painter.setBrush(getBackgroundColour(
                is_highlight=(self.isDown() or self.isChecked()) or (
                        (self.isDown() or self.isChecked()) and self.isEnabled())
            ))
            painter.drawEllipse(rect2)
            painter.restore()
        painter.setPen(getForegroundColour())
        painter.setBrush(Qt.GlobalColor.transparent)
        painter.save()
        painter.setOpacity(
            self.property("baseOpacity") + (self.property("frameOpacity") * (1.0 - self.property("baseOpacity"))))
        painter.drawText(
            QRect(54, 0, self.width() - 52, self.height()),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            self.textPrefix()
            + (self.switchOnText() if self.isChecked() else self.switchOffText())
            + self.textSuffix()
        )
        painter.restore()
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
            self.toggled.emit(self.isChecked())
            self.repaint()
