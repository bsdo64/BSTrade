import numpy as np

from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal, Qt, QRectF, QSize
from PyQt5.QtGui import QColor, QTransform
from PyQt5.QtWidgets import QGraphicsView, QFrame, QGraphicsScene

from BSTrade.Opt.math import nb_max_min, cache_scale_x, cache_scale_y
from BSTrade.util.fn import attach_timer
from ..Item import CandleStick, Line, GridXItem, GridYItem


class ChartView(QGraphicsView):
    sig_chart_wheel = pyqtSignal(object)
    sig_chart_resize = pyqtSignal(object)
    sig_chart_mouse_move = pyqtSignal(object)
    sig_chart_key_press = pyqtSignal(object)

    def __init__(self, model, parent=None):
        QGraphicsView.__init__(self, parent)
        self.setFrameStyle(QFrame.NoFrame)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 0, 0, 0)
        self.setBackgroundBrush(QColor('#1B1D27'))

        self.model = model
        self.open_file_finished = False
        self.rect = QRectF(0, 0, 0, 0)

        if model.CHART_TYPE == 'candle':
            self.chart_item = CandleStick(self.model, self)
        elif model.CHART_TYPE == 'indicator':
            self.chart_item = Line(self.model, self)

        self.set_scene()

    def set_scene(self):
        scene = QGraphicsScene()
        scene.addItem(GridXItem(self.model, self))
        scene.addItem(GridYItem(self.model, self))
        scene.addItem(self.chart_item)

        self.setScene(scene)
        self.open_file_finished = True

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        pos = self.mapToScene(event.pos())
        x, y = pos.x(), pos.y()

        x = int(x) - int(x) % 50

        d = self.model.c_data
        ts = d['time_axis_scaled']
        close = d['close']
        idx = np.where(ts == x)[0]
        if len(idx) > 0:
            print(x, close[idx])

        super().mouseMoveEvent(event)
        self.sig_chart_mouse_move.emit(event)

    def resizeEvent(self, event: QtGui.QResizeEvent):
        delta: QSize = (event.size() - event.oldSize())

        if hasattr(self, 'chart_item'):
            self.model.change_x(delta.width(), 0)
            self.model.c_model.set_size(self.size())

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
            delta_x = event.angleDelta().x()
            delta_y = event.angleDelta().y()

            self.model.change_x(delta_x, -delta_y)
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
            # update scene rect
            scene.setSceneRect(self.make_scene_rect(data))


attach_timer(ChartView)