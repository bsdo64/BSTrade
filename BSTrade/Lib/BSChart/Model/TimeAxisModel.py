import time

import numpy as np
from PyQt5.QtCore import QObject

from BSTrade.Opt import vec
from BSTrade.Opt.math import cache_x_range, cache_x_pos
from . import ChartModel


class TimeAxisModel(QObject):
    DEFAULT_X_RANGE = 1000
    AXIS_TYPE = 'time'
    X_TIME = (time.time() // 60) * 50  # (sec // 60s) * marker_gap -> scaled min

    def __init__(self, c_model: ChartModel):
        QObject.__init__(self)

        self.c_model = c_model
        self.series = c_model.get_data()
        self.store = c_model.get_store()

        self.x_pos = 0
        self.x_range = self.DEFAULT_X_RANGE
        self.x_range_prev = self.DEFAULT_X_RANGE
        self.x_ratio = self.c_model.view_width / self.x_range
        self.x_time_pos = self.X_TIME
        self.x_time_gap = 60

        self.marker_gap = 50

        self.minutes = [
            1, 2, 3, 5, 10, 15, 30,  # 1m, 2m, 3m, 5m, 10m, 30m,
            60, 120, 180, 240, 360, 480, 720,  # 1h, 2h, 3h, 4h, 6h, 8h, 12h,
            1440, 2880, 5760,  # 1d, 2d, 4d,
            10080, 20160, 40320,  # 1w, 2w, 4w,
        ]
        self.minute_pos = 7  # default 1h
        self.months = [
            '', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
        ]

        self.init_axis_data()

    def init_axis_data(self):
        ts = self.series['timestamp'].astype(np.int64)
        self.series['time_axis'] = vec.ts_to_axis(ts, 60)
        self.series['time_axis_scaled'] = vec.mult(self.series['time_axis'],
                                                   self.marker_gap)

    def change_axis(self, pos, rng):
        chart = self.c_model

        # limit pos
        # -> 640 + (-430) = 210 > 50 * 4
        if chart.view_width + self.x_pos > self.marker_gap * 10:
            # change pos
            self.x_pos += pos

        # limit rng
        # -> 1000 + n > 1000
        if self.x_range + rng > self.DEFAULT_X_RANGE:
            # change x_range
            self.x_range += rng

        self.change_ratio(chart.view_width / self.x_range)

    def change_ratio(self, ratio):
        self.x_ratio = ratio

    def current_x_range(self) -> int:
        return cache_x_range(self.x_pos,
                             self.x_range,
                             self.marker_gap)  # (num1 + num2) // num3

    def current_x_pos(self) -> int:
        return cache_x_pos(self.x_pos, self.marker_gap)  # num1 // num2

    def calc_marker(self, axis_data):
        start = axis_data[0]  # min
        remain = start % self.minutes[self.minute_pos]
        self.x_time_pos = (start - remain) * self.marker_gap
        self.x_time_gap = self.minutes[self.minute_pos] * self.marker_gap
        self.set_time_gap(self.x_time_gap * self.x_ratio)

    def set_time_gap(self, gap):
        if 0 <= self.minute_pos < len(self.minutes):
            if 0 < gap < 75:
                self.minute_pos = self.minute_pos + 1
            elif 150 < gap:
                self.minute_pos = self.minute_pos - 1

    def get_month(self, m):
        return self.months[m]

    def get_minute(self):
        return self.minutes[self.minute_pos]

    def get_rectx(self):
        return self.X_TIME - self.x_pos - self.x_range