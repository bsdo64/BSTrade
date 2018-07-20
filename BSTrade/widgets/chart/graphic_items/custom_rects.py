import typing

import numpy as np
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainterPath, QPen
from PyQt5.QtWidgets import QGraphicsItem, QWidget, QStyleOptionGraphicsItem


class CustomRectsItem(QGraphicsItem):
    def __init__(self, parent=None):
        QGraphicsItem.__init__(self, parent)
        self.path = QPainterPath()
        self.data_size = 1000

    def paint(self,
              painter: QtGui.QPainter,
              option: 'QStyleOptionGraphicsItem',
              widget: typing.Optional[QWidget] = ...):

        if not self.path.length():

            path = QPainterPath()
            path.moveTo(0, 0)
            rand = np.random.rand(self.data_size) * 100
            for i in np.arange(self.data_size):
                path.lineTo(i, rand[i])

            self.path = path

        painter.save()
        pen = QPen()
        pen.setCosmetic(True)
        pen.setColor(Qt.darkBlue)
        painter.setPen(pen)
        painter.drawPath(self.path)
        painter.restore()

    def boundingRect(self):
        return QRectF(0, 0, self.data_size, 100)