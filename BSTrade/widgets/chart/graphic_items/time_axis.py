from datetime import datetime, timezone

from PyQt5.QtCore import Qt, QPoint, QRectF
from PyQt5.QtGui import QPainterPath, QPainter, QFont
from PyQt5.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem

from BSTrade.data.model import Model


class TimeAxisItem(QGraphicsItem):
    def __init__(self, model, parent=None):
        QGraphicsItem.__init__(self, parent)
        self.model: Model = model

        self.time_path = QPainterPath()

        self.cache = {
            'time_path': QPainterPath(),
        }

        self.make_path()

    def paint(self,
              painter: QPainter,
              option: QStyleOptionGraphicsItem,
              widget=None):

        painter.save()
        painter.setBrush(Qt.white)
        painter.setPen(Qt.NoPen)
        painter.setRenderHint(painter.Antialiasing)

        painter.drawPath(self.time_path)

        painter.restore()

    def make_path(self):
        baseline = QPoint(0, 15)
        font = QFont('Arial')
        font.setPixelSize(12)

        d = self.model.c_data
        times = d['time_axis'] * 60
        print(times)
        t = datetime.fromtimestamp(1532335140, tz=timezone.utc)
        self.time_path.addText(baseline,
                               font,
                               "{:02d}:{:02d}".format(t.hour, t.minute))

    def boundingRect(self):
        return QRectF(0, 0, 499, 20)
