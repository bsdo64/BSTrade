import sys
import pandas as pd

from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QTransform
from PyQt5.QtWidgets import QGraphicsView

from util.fn import attach_timer

pd.set_option('display.precision', 20)


class Model:
    _DEFAULT_X_RANGE = 100
    INT_MAX = sys.maxsize // 10 ** 6
    _DEFAULT_NEXT_X_RANGE = 500

    def __init__(self,
                 data: pd.DataFrame,
                 view: QGraphicsView):

        self.series = data
        self.view = view

        self.x_range = self._DEFAULT_X_RANGE
        self.next_x_len = self._DEFAULT_NEXT_X_RANGE

        self.marker_gap = 50
        self.max_x_range = 100_000

        self._init_printing_data()

    def _init_printing_data(self):
        self.series['time_axis'] = (
            self.series['timestamp'].astype('int64') // 10 ** 9 // 60
        )  # timestamp by minute
        self.series['time_axis_scaled'] = (
            self.series['time_axis'] * self.marker_gap
        )  # 1262304000 ~ 1276503350

        for i in ['close', 'open', 'low', 'high']:
            self.series['r_' + i] = self.INT_MAX - self.series[i]

    def default_x_range(self) -> int:
        return self._DEFAULT_X_RANGE

    def next_x_range(self) -> int:
        return self.next_x_len

    def current_x_range(self) -> int:
        return self.x_range // self.marker_gap  # 100 // 50 = 2

    def change_x_range(self, factor):
        # Time axis range must be positive.
        if self.x_range + factor > self._DEFAULT_X_RANGE:
            self.x_range += factor
            self.next_x_len = min(self.x_range // 15, 2000)  # 15% of x_range

            # Scale view after change x-range to fit view
            trans = QTransform()
            trans.scale(*self.scale())
            self.view.setTransform(trans)

            # Change scene rect to fit view
            scene = self.view.scene()
            scene.setSceneRect(self.make_scene_rect())  # update scene rect

    def make_scene_rect(self):
        data = self.current_data()

        return QRectF(
            data['time_axis_scaled'].max() - self.x_range,
            data['r_high'].min(),
            self.x_range,
            data['high'].max() - data['low'].min()
        )

    def current_data(self, add=0) -> pd.DataFrame:
        return self.series[-(self.current_x_range()+add):]

    def next_data(self, data_range=None) -> pd.DataFrame:
        next_data_size = data_range or self.next_x_len  # 500
        v = self.current_x_range() // next_data_size  # 2 // 500
        origin_gap = self._DEFAULT_X_RANGE // self.marker_gap
        return self.series[
            -(next_data_size * (v + 1) + origin_gap):  # 500 * 1 + 2 = 500 + 2
            -(next_data_size * v + origin_gap)  # 500 * 0 + 2 = 2
        ]

    def scale(self) -> (float, float):
        model_data = self.current_data(add=0)
        scale_x = self.view.width() / self.x_range
        scale_y = self.view.height() / (model_data['r_low'].max() -
                                        model_data['r_high'].min())
        return scale_x, scale_y

    def scale_x(self):
        return self.view.width() / self.x_range


attach_timer(Model)
