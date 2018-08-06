import numpy as np
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QRectF
from PyQt5.QtGui import QColor, QTransform
from PyQt5.QtWidgets import QGraphicsView, QFrame

from BSTrade.data.model import Model
from BSTrade.optimize.math import cache_scale_x, cache_scale_y, nb_max_min
from BSTrade.util.fn import attach_timer
from BSTrade.widgets.chart.graphic_items import CandleStickItem
from BSTrade.widgets.chart.graphic_items import GridXItem
from BSTrade.widgets.chart.graphic_scenes.chart_scene import ChartScene


class ChartView(QGraphicsView):
    sig_chart_wheel = pyqtSignal(object)
    sig_chart_resize = pyqtSignal(object)
    sig_chart_mouse_move = pyqtSignal(object)
    sig_chart_key_press = pyqtSignal(object)

    def __init__(self, model: Model, parent=None):
        QGraphicsView.__init__(self, parent)
        self.setFrameStyle(QFrame.NoFrame)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 0, 0, 0)
        self.setBackgroundBrush(QColor('#1B1D27'))

        # self.setViewport(QOpenGLWidget())
        # self.setRenderHint(QPainter.Antialiasing)
        # self.setFrameStyle(QFrame.NoFrame)

        self.model = model
        self.open_file_finished = False
        self.rect = QRectF(0, 0, 0, 0)
        self.chart_item = CandleStickItem(self.model, self)
        self.chart_line = GridXItem(self.model, self)
        self.set_scene()

    def set_scene(self):
        scene = ChartScene()
        scene.addItem(self.chart_line)
        scene.addItem(self.chart_item)

        self.setScene(scene)
        self.open_file_finished = True

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        # print(self.scene().itemAt(self.mapToScene(event.pos()), QTransform()))
        print(self.mapToScene(event.pos()))
        print(event.pos())

        super().mouseMoveEvent(event)
        self.sig_chart_mouse_move.emit(event)

    def resizeEvent(self, event: QtGui.QResizeEvent):
        delta: QSize = (event.size() - event.oldSize())

        if hasattr(self, 'chart_item'):
            self.model.change_x(delta.width(), 0)
            self.model.set_view_width(self.width())
            self.model.set_view_height(self.height())

        super().resizeEvent(event)
        self.sig_chart_resize.emit(event)

    def wheelEvent(self, event: QtGui.QWheelEvent):
        """ ChartView's wheel event handler

        Handle mouse wheel event.
        This method must handle :
            1. Change range of model by y-axis
            2. Change translate of model by x-axis

        Parameters
        ----------
        event : QtGui.QWheelEvent
            QGraphicsView's wheel event.

        """
        if self.open_file_finished:
            # if platform == "darwin":
            #     delta_x = event.pixelDelta().x()
            #     delta_y = event.pixelDelta().y()
            #     print(delta_x, delta_y)
            # else:
            delta_x = event.angleDelta().x()
            delta_y = event.angleDelta().y()

            self.model.change_x(delta_x, delta_y)
            self.fit_view()

        super().wheelEvent(event)
        self.sig_chart_wheel.emit(event)

    def make_scene_rect(self, data):
        self.rect = QRectF(
            self.model.rect_x(),
            np.min(data['r_high']),
            self.model.x_range,
            nb_max_min(data['high'], data['low'])
        )

        return self.rect

    def fit_view(self):
        data = self.model.current_data()

        if data['len'] > 0:

            # Scale view after change xrange to fit view
            trans = QTransform()
            sc = (cache_scale_x(self.width(),
                                self.model.x_range),
                  cache_scale_y(self.height(),
                                data['high'],
                                data['low']))
            trans.scale(*sc)
            self.setTransform(trans)

            # Change scene rect to fit view
            scene = self.scene()
            scene.setSceneRect(self.make_scene_rect(data))  # update scene rect


attach_timer(ChartView)
