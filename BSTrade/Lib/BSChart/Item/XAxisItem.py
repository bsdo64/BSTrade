from datetime import datetime, timezone

import numpy as np
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainterPath, QPainter, QPen, QFont
from PyQt5.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem

from BSTrade.Lib.BSChart.Model.PlotModel import CandleModel
from BSTrade.util.fn import attach_timer


class TimeItem(QGraphicsItem):
    def __init__(self, model, view, parent=None):
        QGraphicsItem.__init__(self, parent)
        self.model: CandleModel = model
        self.view = view

        self.time_arr = []
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

        for i in self.time_arr:
            painter.drawText(QRectF(i[0] - 50, 3, 100, 17), Qt.AlignCenter,
                             i[1])

        painter.drawPath(self.line_path)
        painter.restore()

    def make_path(self):
        width = self.model.view_width
        # first time position (min * gap(50)) ex) 1277958000
        first_time_pos = self.model.x_time_pos

        # time pos -> real time (min * 60s // gap) ex) 1533535200
        time = first_time_pos * 60 // self.model.marker_gap
        # first time position ex) 1277958000 - 1277961034.0
        first = (first_time_pos - self.model.rect_x()) * self.model.x_ratio
        # time position gap
        gap = self.model.x_time_gap * self.model.x_ratio

        a = []
        line_path = QPainterPath()
        # print(first_time_pos,
        #       self.model.rect_x(),
        #       self.model.x_ratio,
        #       first, width, gap, time)

        for v in np.arange(first, width, gap):
            t = datetime.fromtimestamp(time, tz=timezone.utc)

            if t.day == 1 and t.hour == 0 and t.minute == 0:
                a.append((v, "{}".format(self.model.get_month(t.month)), 'M'))
            elif t.hour == 0 and t.minute == 0:
                a.append((v, "{:02d}".format(t.day), 'd'))
            else:
                a.append((v, "{:02d}:{:02d}".format(t.hour, t.minute), 'm'))

            line_path.moveTo(v, 0)
            line_path.lineTo(v, 3)

            time = time + self.model.get_minute() * 60  # min * 60sec

        self.time_arr = a
        self.line_path = line_path

    def boundingRect(self):
        return self.view.rect


attach_timer(TimeItem, limit=1)