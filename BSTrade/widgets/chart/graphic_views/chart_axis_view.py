from PyQt5.QtCore import Qt, QRectF, QTimer
from PyQt5.QtGui import QColor, QWheelEvent
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QFrame

from BSTrade.widgets.chart.graphic_items import ChartAxisItem
from BSTrade.util.fn import attach_timer


class ChartAxisView(QGraphicsView):
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
        self.chart_axis = ChartAxisItem(model, self)
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

    def slot_wheel_re_model(self, ev: QWheelEvent):
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


attach_timer(ChartAxisView)
