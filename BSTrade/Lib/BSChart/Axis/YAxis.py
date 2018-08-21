import numpy as np
from PyQt5.QtCore import Qt, QRectF, QTimer
from PyQt5.QtGui import QColor, QWheelEvent, QPainterPath, QPainter, QPen, QFont
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QFrame, \
    QGraphicsItem, QStyleOptionGraphicsItem

from BSTrade.util.fn import attach_timer


class Item(QGraphicsItem):
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


attach_timer(Item)


class AxisView(QGraphicsView):
    def __init__(self, model, parent=None):
        QGraphicsView.__init__(self, parent)
        self.setFixedWidth(56)
        self.setFrameStyle(QFrame.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 0, 0, 0)
        self.setBackgroundBrush(QColor('#1B1D27'))

        self.model = model
        self.rect = QRectF(0, 0, 0, 0)
        self.chart_axis = Item(model, self)
        self.set_scene()

        self.timer = QTimer()
        self.timer.setInterval(16)  # 60 fps = 16.666 ms  (60 fps / 2)
        self.timer.timeout.connect(self.update_view)
        self.timer.start()

        self.need_update = False

    def set_scene(self):
        scene = QGraphicsScene()
        scene.addItem(self.chart_axis)
        self.setScene(scene)

    def wheelEvent(self, ev: QWheelEvent):
        self.fit_view()
        self.need_update = True

    def fit_view(self):
        scene: QGraphicsScene = self.scene()
        scene.setSceneRect(self.make_scene_rect())

        self.chart_axis.make_path()

    def make_scene_rect(self):
        self.rect = QRectF(
            0, 0,
            self.width(), self.height()
        )

        return self.rect

    def update_view(self):
        if self.need_update:
            self.viewport().update()
            self.need_update = False


attach_timer(AxisView)