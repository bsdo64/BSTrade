import numpy as np

from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QPainter, QPen, QPainterPath, QColor
from PyQt5.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem


class GridXItem(QGraphicsItem):
    def __init__(self, model, view, parent=None):
        QGraphicsItem.__init__(self, parent)
        self.model = model
        self.view = view

    def paint(self,
              painter: QPainter,
              option: QStyleOptionGraphicsItem,
              widget=None):

        painter.save()
        pen = QPen()
        pen.setColor(QColor('#2A2D3A'))
        pen.setCosmetic(True)
        painter.setPen(pen)
        # painter.setRenderHint(painter.Antialiasing)

        # first time position (min * gap(50)) ex) 1277958000
        first_time_pos = self.model.x_axis.x_time_pos
        # first time position ex) 1277958000 - 1277961034.0
        first = first_time_pos
        # time position gap
        gap = self.model.x_axis.x_time_gap

        line_path = QPainterPath()
        r: QRectF = self.view.rect
        for v in np.arange(first, first + self.model.x_axis.x_range, gap):
            line_path.moveTo(v, r.y())
            line_path.lineTo(v, r.y() + r.height())

        painter.drawPath(line_path)
        painter.restore()

    def boundingRect(self):
        return self.view.rect


class GridYItem(QGraphicsItem):
    def __init__(self, model, view, parent=None):
        QGraphicsItem.__init__(self, parent)
        self.model = model
        self.view = view

    def paint(self,
              painter: QPainter,
              option: QStyleOptionGraphicsItem,
              widget=None):

        painter.save()
        pen = QPen()
        pen.setColor(QColor('#2A2D3A'))
        pen.setCosmetic(True)
        painter.setPen(pen)
        # painter.setRenderHint(painter.Antialiasing)

        r: QRectF = self.view.rect
        # first time position ex) 1277958000 - 1277961034.0
        first = self.model.y_val_pos
        # time position gap
        gap = self.model.y_val_gap

        line_path = QPainterPath()
        for v in np.arange(first, first + r.height(), gap):
            line_path.moveTo(r.x(), v)
            line_path.lineTo(r.x() + r.width(), v)

        painter.drawPath(line_path)
        painter.restore()

    def boundingRect(self):
        return self.view.rect
