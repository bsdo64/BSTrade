from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QWheelEvent
from PyQt5.QtWidgets import QGraphicsView, QFrame

from BSTrade.widgets.chart.graphic_scenes.time_scene import TimeScene
from BSTrade.widgets.chart.graphic_items.time_axis import TimeAxisItem


class TimeAxisView(QGraphicsView):
    def __init__(self, model, parent=None):
        QGraphicsView.__init__(self, parent)
        self.setFixedHeight(20)
        self.setFrameStyle(QFrame.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 0, 0, 0)
        self.setBackgroundBrush(QColor('#1B1D27'))

        self.model = model
        self.time_axis = TimeAxisItem(model)
        self.set_scene()

    def set_scene(self):
        scene = TimeScene()
        scene.addItem(self.time_axis)
        self.setScene(scene)

    def wheelEvent(self, event: QWheelEvent):

        super().wheelEvent(event)

    def slot_wheel_re_model(self, ev: QWheelEvent):
        t = self.model.c_data['time_axis']
        # print()
        # print(ev.pos())
        # print(len(t))
        # print(t[0], t[-1])
        # print(t * 60 % 3600)
