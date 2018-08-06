import datetime as dt
import os
import numpy as np

import ciso8601
from PyQt5.QtCore import QTimer, QCoreApplication, pyqtSignal, QObject
from BSTrade.source_clients.bitmexhttpclient import BitmexHttpClient
from BSTrade.source_clients.auth import bitmex

import pandas as pd

from BSTrade.util.fn import attach_timer


class Request(QObject):
    sig_finish = pyqtSignal()

    def __init__(self, parent=None, start=0, data=pd.DataFrame()):
        QObject.__init__(self)

        self.parent = parent
        # self.start = 0  # 2017 - 01- 01
        self.start = start
        self.df = data

        self.now = dt.datetime.now(tz=dt.timezone.utc)
        self.one_year_min = 525600
        self.rate_limit = 300
        self.requested = 0
        self.count = 500

        self.client = BitmexHttpClient(
            test=False,
            api_key=bitmex.api_keys['real']['order']['key'],
            api_secret=bitmex.api_keys['real']['order']['secret']
        )

        # 525600
        self.year_first = dt.datetime(self.now.year, 1, 1, tzinfo=dt.timezone.utc)
        # 880000 - 525600
        self.now_to_min = (self.now - self.year_first).total_seconds() // 60
        # 880000 - (525600 + 100000)

        self.client.sig_ended.connect(self.get_data)

        self.timer = QTimer()

    def request_data(self):
        start = self.start
        n = self.requested
        s = self.count

        self.client.Trade.get_bucketed(
            '1m',
            symbol='XBTUSD',
            count=self.count,
            start=n * s + start
        )
        self.requested += 1

    def get_data(self, ended: bool):
        start = self.start
        n = self.requested
        s = self.count
        j = self.client.json()
        self.rate_limit = self.client.headers()['x-ratelimit-remaining']
        current = (len(j) + len(self.df))  # 100000

        print('now: {}, current: {}, percent: {:.2f}%, rate_limit: {}'.format(
            self.now_to_min,
            current,
            current/self.now_to_min * 100,
            self.rate_limit
        ))

        if len(j) > 0:
            new_df = pd.DataFrame(j)
            self.df = self.df.append(new_df, ignore_index=True, sort=False)

            self.timer.singleShot(1000, self.request_data)

        elif len(j) == 0:
            self.refine_data()

            self.df.to_pickle('bitmex_1m_2018.pkl')
            print('saved !')
            print("Last index : {}".format(self.df.shape[0]))
            self.sig_finish.emit()

        if s * n >= 525600 * 2:
            self.refine_data()

            self.df.to_pickle('bitmex_1m_2018_end.pkl')
            print('saved to the end of {}!'.format(self.now.year))
            self.sig_finish.emit()

    def refine_data(self):
        self.df = self.df\
            .sort_values(by=["timestamp"], ascending=True)\
            .reset_index(drop=True)

        if 'index' in self.df:
            del self.df['index']

        if 'level_0' in self.df:
            del self.df['level_0']

        print()
        print('Checking Data')
        print('----------------------------------------')
        ts_date = self.df['timestamp'].astype('datetime64')
        v = ts_date.diff().astype(np.int64)
        print('Un sorted : ', v[v != 60000000000][1:])

        rng = pd.date_range('01-01-2018',
                            periods=len(ts_date),
                            freq='min')
        v = rng.difference(ts_date).format()
        print('Missing data : ', v)
        print('----------------------------------------')
        print()


class Requester(QObject):
    sig_finished = pyqtSignal(object)

    def __init__(self, parent=None):
        QObject.__init__(self)
        self.parent = parent
        self.r = Request(self.parent, *self.check_current_data())
        self.r.sig_finish.connect(self.slt_finish)

    def start(self):
        self.r.request_data()

    def check_current_data(self):
        now = dt.datetime.now()
        total_min = 525600  # one-year-min
        filename = 'bitmex_1m_{}.pkl'.format(now.year)

        if os.path.isfile(filename):
            df = pd.read_pickle(filename)
            print(df.dtypes)
            saved_last_time = ciso8601.parse_datetime(df['timestamp'][df.shape[0] - 1])
            expect_last_time = (
                dt.datetime(now.year, 1, 1, tzinfo=dt.timezone.utc)
                + dt.timedelta(minutes=df.shape[0] - 1)
            )

            if expect_last_time.timestamp() == saved_last_time.timestamp():
                start_from = df.shape[0] + total_min * (now.year - 2017)
                print("Now : ", now)
                print("Last time : ", saved_last_time)
                print("Start from ...{}".format(start_from))
                print()
            else:
                raise Exception("Not correct expected last time")
        else:
            df = pd.DataFrame()
            start_from = total_min * (now.year - 2017)
            print("Now : ", now)
            print("Start from ...{}".format(start_from))
            print()

        return start_from, df

    def slt_finish(self):
        self.sig_finished.emit(self.r.df)


attach_timer(Request, limit=1)
attach_timer(Requester, limit=1)

if __name__ == '__main__':
    app = QCoreApplication([])

    handler = Requester(app)
    handler.start()

    app.exec()
