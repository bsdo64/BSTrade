from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QColor, QWheelEvent, QTransform
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
        self.rect = QRectF(0, 0, 0, 0)
        self.time_axis = TimeAxisItem(model, self)
        self.set_scene()

    def set_scene(self):
        scene = TimeScene()
        scene.addItem(self.time_axis)
        self.setScene(scene)

    def wheelEvent(self, event: QWheelEvent):

        super().wheelEvent(event)

    def make_scene_rect(self):
        self.rect = QRectF(
            0, 0,
            self.width(), self.height()
        )

        return self.rect

    def slot_wheel_re_model(self, ev: QWheelEvent):

        self.fit_view()

    def fit_view(self):
        data = self.model.current_data()

        if data['len'] > 0:

            scene: TimeScene = self.scene()
            scene.setSceneRect(self.make_scene_rect())

            print(self.make_scene_rect())

            self.update()
