import numpy as np
from datetime import datetime, timezone

from PyQt5.QtCore import Qt, QPoint, QRectF, QPointF
from PyQt5.QtGui import QPainterPath, QPainter, QFont, QPen
from PyQt5.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem

from BSTrade.data.model import Model


class TimeAxisItem(QGraphicsItem):
    def __init__(self, model, view, parent=None):
        QGraphicsItem.__init__(self, parent)
        self.model: Model = model
        self.view = view

        self.time_path = QPainterPath()

        self.cache = {
            'time_path': QPainterPath(),
        }

    def paint(self,
              painter: QPainter,
              option: QStyleOptionGraphicsItem,
              widget=None):

        painter.save()
        pen = QPen()
        pen.setColor(Qt.white)
        pen.setCosmetic(True)

        painter.setBrush(Qt.white)
        painter.setPen(pen)
        painter.setRenderHint(painter.Antialiasing)

        t = self.model.c_data['time_axis']
        t_s = self.model.c_data['time_axis_scaled']
        t2 = t_s[t * 60 % 3600 == 0]
        ratio = self.view.width() / self.model.x_range
        l = np.linspace(0, self.view.width(), len(t2))

        if len(t2) > 0 and (t2[-1] - t2[0] > 0):
            t3 = (t2 - t2[0]) * self.view.width() / (t2[-1] - t2[0])

            print()
            print(t3)
            # print(self.model.rect_x() //)
            path = QPainterPath()
            path2 = QPainterPath()
            for i, v in enumerate(t3):
                font = QFont('Arial')
                font.setPixelSize(12)

                print('ratio : ', ratio)
                print('v * ratio : ', v * ratio)
                print('t2[i] : ', t2[i])
                print('v : ', v)

                t = datetime.fromtimestamp(t2[i] * 12 // 10, tz=timezone.utc)

                path.addText(v, 15,
                             font,
                             "{:02d}:{:02d}".format(t.hour, t.minute))
                print("{:02d}:{:02d}".format(t.hour, t.minute))

                painter.drawPoint(v, 10)
                path2.moveTo(v, 0)
                path2.lineTo(v, 20)

            if path.length() > 0:
                print(path.elementAt(0).x, path.elementAt(0).y)
                print(path2.elementAt(0).x, path2.elementAt(0).y)

            painter.drawPath(path)
            painter.drawPath(path2)

        painter.restore()

    def boundingRect(self):
        return self.view.rect
