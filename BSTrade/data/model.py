import sys
import time
import pandas as pd
import numpy as np

from PyQt5.QtCore import QRectF

from BSTrade.util.fn import attach_timer
from BSTrade.optimize.vec import to_time_axis, to_time_scale, make_r_data
from BSTrade.optimize.math import cache_x_range, cache_x_pos


class Model:
    _DEFAULT_X_RANGE = 1000
    _DEFAULT_NEXT_X_RANGE = 1000
    INT_MAX = sys.maxsize // 10 ** 10
    X_TIME = time.time() // 60 * 50  # sec // 60s * marker_gap -> scaled min

    def __init__(self, data: pd.DataFrame):
        self.series = data

        self.x_pos = 0
        self.x_range = self._DEFAULT_X_RANGE
        self.x_range_next = self._DEFAULT_NEXT_X_RANGE
        self.rect = QRectF(0, 0, 0, 0)

        self.marker_gap = 50

        self.c_data = {}
        self.np_data = {}

        self._init_printing_data()

    def _init_printing_data(self):
        self.series['timestamp'] = self.series['timestamp']\
            .astype('datetime64')
        ts = self.series['timestamp'].values.astype(np.int64)
        self.series['time_axis'] = pd.Series(to_time_axis(ts, 60))

        self.np_data['time_axis'] = self.series['time_axis'].values
        self.np_data['time_axis_scaled'] = to_time_scale(
            self.np_data['time_axis'], self.marker_gap
        )
        self.series['time_axis_scaled'] = pd.Series(
            self.np_data['time_axis_scaled'])

        for i in ['close', 'open', 'low', 'high']:
            self.np_data['r_' + i] = make_r_data(self.INT_MAX,
                                                 self.series[i].values)
            self.np_data[i] = self.series[i].values

        self.DATA_LEN = self.np_data['time_axis_scaled'].shape[0]

        self.c_data = self.current_data()

    def change_x(self, x, y):
        self.x_pos += x

        if self.x_range + y > self._DEFAULT_X_RANGE:
            self.x_range += y

    def current_x_range(self) -> int:
        return cache_x_range(self.x_pos,
                             self.x_range,
                             self.marker_gap)  # (num1 + num2) // num3

    def current_x_pos(self) -> int:
        return cache_x_pos(self.x_pos, self.marker_gap)  # num1 // num2

    def current_data(self):

        if hasattr(self, 'np_data'):
            s = -self.current_x_range()
            p = self.current_x_pos()
            e = -p if 0 < p else None

            if 0 < -s < self.DATA_LEN:
                self.c_data = self._create_data(s, e)

        return self.c_data

    def rect_x(self):
        return self.X_TIME - self.x_pos - self.x_range

    def next_data(self, d_s, d_len=1000):
        s = -(d_s+d_len)
        e = -d_s or None

        return self._create_data(s, e)

    def _create_data(self, start, end):
        return {
            'time_axis_scaled': self.np_data['time_axis_scaled'][start: end],
            'time_axis': self.np_data['time_axis'][start: end],
            'high': self.np_data['high'][start: end],
            'r_high': self.np_data['r_high'][start: end],
            'low': self.np_data['low'][start: end],
            'r_low': self.np_data['r_low'][start: end],
            'close': self.np_data['close'][start: end],
            'r_close': self.np_data['r_close'][start: end],
            'open': self.np_data['open'][start: end],
            'r_open': self.np_data['r_open'][start: end],
            'len': len(self.np_data['r_open'][start: end])
        }


attach_timer(Model)
