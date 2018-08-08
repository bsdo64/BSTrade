import numpy as np

from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QPainter, QPen, QPainterPath, QColor, QFont
from PyQt5.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem

from BSTrade.util.fn import attach_timer


class ChartAxisItem(QGraphicsItem):
    def __init__(self, model, view, parent=None):
        QGraphicsItem.__init__(self, parent)
        self.model = model
        self.view = view

        self.value_arr = []
        self.line_path = QPainterPath()

    def paint(self,
              painter: QPainter,
              option: QStyleOptionGraphicsItem,
              widget=None):

        painter.save()
        pen = QPen()
        pen.setColor(Qt.white)
        pen.setCosmetic(True)
        font = QFont('Arial')
        font.setPixelSize(12)
        painter.setFont(font)
        painter.setPen(pen)

        for i in self.value_arr:
            painter.drawText(QRectF(3, i[0]-10, 53, 20), Qt.AlignCenter, i[1])

        painter.drawPath(self.line_path)
        painter.restore()

    def make_path(self):
        height = self.model.view_height
        # first position ex) 984747362
        first_val_pos = self.model.y_val_pos

        # time pos -> real time (min * 60s // gap) ex) 1533535200
        val = self.model.INT_MAX - first_val_pos
        # first time position ex) 1277958000 - 1277961034.0
        first = (first_val_pos - self.model.Y_VAL) * self.model.y_ratio
        # time position gap
        gap = self.model.y_val_gap * self.model.y_ratio

        a = []
        line_path = QPainterPath()
        for v in np.arange(first, height, gap):
            a.append((v, "{}".format(val)))

            line_path.moveTo(0, v)
            line_path.lineTo(3, v)

            val = val - self.model.y_val_gap  # min * 60sec

        self.value_arr = a
        self.line_path = line_path

    def boundingRect(self):
        return self.view.rect


attach_timer(ChartAxisItem)
