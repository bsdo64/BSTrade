from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QColor, QWheelEvent
from PyQt5.QtWidgets import QGraphicsView, QFrame

from BSTrade.util.fn import attach_timer
from BSTrade.widgets.chart.graphic_items import TimeAxisItem
from BSTrade.widgets.chart.graphic_scenes.time_scene import TimeScene


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
        self.rect = QRectF(0, 0, 0, 0)
        self.time_axis = TimeAxisItem(model, self)
        self.set_scene()

    def set_scene(self):
        scene = TimeScene()
        scene.addItem(self.time_axis)
        self.setScene(scene)

    def slot_wheel_re_model(self, ev: QWheelEvent):
        self.fit_view()
        self.viewport().update()

    def fit_view(self):
        scene: TimeScene = self.scene()
        scene.setSceneRect(self.make_scene_rect())

        self.time_axis.make_path()

    def make_scene_rect(self):
        self.rect = QRectF(
            0, 0,
            self.width(), self.height()
        )

        return self.rect


attach_timer(TimeAxisView)
