from PyQt5.QtCore import Qt, QRectF, QTimer
from PyQt5.QtGui import QColor, QWheelEvent
from PyQt5.QtWidgets import QGraphicsView, QFrame, QGraphicsScene

from ..Item.YAxisItem import YItem
from BSTrade.util.fn import attach_timer


class YAxisView(QGraphicsView):
    def __init__(self, model, parent=None):
        super().__init__(parent)

        # ------ Init Data
        self.model = model
        self.rect = QRectF(0, 0, 0, 0)
        self.item = YItem(model, self)
        self.need_update = False
        self.timer = QTimer()

        # ------ Init UI Components
        self.setup_ui()

        # ------ Init setup
        self.init_signals()

    def setup_ui(self):
        self.setFixedWidth(56)
        self.setFrameStyle(QFrame.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 0, 0, 0)
        self.setBackgroundBrush(QColor('#1B1D27'))

        scene = QGraphicsScene()
        scene.addItem(self.item)
        self.setScene(scene)

    def init_signals(self):
        self.timer.setInterval(16)  # 60 fps = 16.666 ms  (60 fps / 2)
        self.timer.timeout.connect(self.update_view)
        self.timer.start()

    def wheelEvent(self, ev: QWheelEvent):
        self.need_update = True
        self.fit_view()

    def fit_view(self):
        scene: QGraphicsScene = self.scene()
        scene.setSceneRect(self.make_scene_rect())

        self.item.make_path()

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


attach_timer(YAxisView)
