import json
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
    INT_MAX = sys.maxsize // 10 ** 11 * 10
    X_TIME = (time.time() // 60) * 50  # (sec // 60s) * marker_gap -> scaled min
    Y_VAL = 0  # (sec // 60s) * marker_gap -> scaled min

    def __init__(self, data: pd.DataFrame):
        self.series = data

        self.view_width = 640
        self.view_height = 480

        self.x_pos = 0
        self.x_range = self._DEFAULT_X_RANGE
        self.x_range_next = self._DEFAULT_NEXT_X_RANGE
        self.x_ratio = self.view_width / self.x_range
        self.x_time_pos = self.X_TIME
        self.x_time_gap = 60
        self.y_range = 100
        self.y_ratio = self.view_height / self.y_range  # 480 / 100 = 4.8
        self.y_val_pos = 9876540
        self.y_gap_pos = 2
        self.y_gaps = [2, 2, 2.5]
        self.y_val_gap = 50

        self.rect = QRectF(0, 0, 0, 0)
        self.marker_gap = 50

        self.c_data = {}
        self.np_data = {}
        self.minutes = [
            1, 2, 3, 5, 10, 15, 30,  # 1m, 2m, 3m, 5m, 10m, 30m,
            60, 120, 180, 240, 360, 480, 720,  # 1h, 2h, 3h, 4h, 6h, 8h, 12h,
            1440, 2880, 5760,  # 1d, 2d, 4d,
            10080, 20160, 40320,  # 1w, 2w, 4w,
        ]
        self.months = [
            '', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
        ]

        self.minute_pos = 7  # default 1h

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

    def change_x(self, pos, rng):

        # change x_pos
        self.x_pos += pos

        # change x_range
        if self.x_range + rng > self._DEFAULT_X_RANGE:
            self.x_range += rng

        # change ratio
        self.x_ratio = self.view_width / self.x_range

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

            ta = self.c_data['time_axis']
            rh = self.c_data['r_high']
            rl = self.c_data['r_low']

            if len(ta) > 0:
                first_time = ta[0]  # min
                remain = first_time % self.minutes[self.minute_pos]
                self.x_time_pos = (first_time - remain) * self.marker_gap
                self.x_time_gap = self.minutes[self.minute_pos] * self.marker_gap
                self.set_time_gap(self.x_time_gap * self.x_ratio)

                self.Y_VAL = np.min(rh)  # min value
                remain = self.Y_VAL % self.y_val_gap  # 9875421 % 50
                self.y_val_pos = (self.Y_VAL - remain)  # first y grid
                self.y_range = np.max(rl) - self.Y_VAL  # min value
                self.y_ratio = self.view_height / self.y_range
                self.set_y_gap(self.y_val_gap * self.y_ratio)  # y gap 50 * 4.8

        return self.c_data

    def rect_x(self):
        return self.X_TIME - self.x_pos - self.x_range

    def prev_data(self, d_s, d_len=1000):
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

    def set_time_gap(self, gap):
        if 0 <= self.minute_pos < len(self.minutes):
            if 0 < gap < 75:
                self.minute_pos = self.minute_pos + 1
            elif 150 < gap:
                self.minute_pos = self.minute_pos - 1

    def set_y_gap(self, gap):
        g = gap * 100

        if 0 < g <= 3000:
            """
                default = 50, 2.5(2)
                1. 50   *   2(0)   = 100
                2. 100  *   2(1)   = 200 
                3. 200  * 2.5(2)   = 500 
                4. 500  *   2(0)   = 1000 
                5. 1000 *   2(1)   = 2000 
                ...
            """
            self.y_gap_pos = (self.y_gap_pos+1) % len(self.y_gaps)  # 1 % 3 -> 1
            self.y_val_gap *= self.y_gaps[self.y_gap_pos]  # 50 * 2 -> 100
        elif 6000 < g:
            """
                default = 50, 2.5(2)
                1. 50   / 2.5(2)   = 20
                2. 20   /   2(1)   = 10 
                3. 10   /   2(0)   = 5 
                4. 5    / 2.5(2)   = 2
                5. 2    /   2(1)   = 1 
                ...
            """
            self.y_val_gap /= self.y_gaps[self.y_gap_pos]  # 50 / 2.5 -> 20.0
            self.y_gap_pos = (self.y_gap_pos-1) % len(self.y_gaps)  # -1 % 3 -> 2

    def set_view_width(self, width):
        self.view_width = width

    def set_view_height(self, height):
        self.view_height = height

    def get_month(self, m):
        return self.months[m]

    def get_minute(self):
        return self.minutes[self.minute_pos]

    def slt_ws_message(self, msg):
        j = json.loads(msg)

        table_name = j.get('table')
        if table_name == 'trade':
            items = j.get('data')
            # print(items)
        elif table_name == 'tradeBin1m':
            items = j.get('data')
            print(items)


attach_timer(Model, limit=1)
