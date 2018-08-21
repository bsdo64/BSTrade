import datetime as dt
import os
import sqlite3

import numpy as np
import pandas as pd
import ciso8601

from PyQt5.QtCore import QTimer, QCoreApplication, pyqtSignal, QObject

from BSTrade.Data.bitmex.sqls import select_last, get_col_names, ignore_insert
from BSTrade.Api.bitmexhttpclient import BitmexHttpClient
from BSTrade.Api.auth import bitmex as bm_auth
from BSTrade.util.fn import attach_timer
from BSTrade.Data.bitmex.instruments import inst as bm_inst


PATH = os.path.dirname(os.path.abspath(__file__))
DATA = {
    'bitmex': bm_inst
}


class Request(QObject):
    sig_finish = pyqtSignal()

    def __init__(self, parent=None, inst=None, data=pd.DataFrame()):
        QObject.__init__(self)

        self.parent = parent
        self.inst = inst
        self.df = data
        self.start_length = len(self.df)
        self.start_time = data['timestamp'].iloc[-1]
        self.last_time = self.start_time

        self.now = dt.datetime.now(tz=dt.timezone.utc)

        self.one_year_min = 525600
        self.rate_limit = 300
        self.requested = 0
        self.count = 500

        self.client = BitmexHttpClient(
            test=False,
            api_key=bm_auth.api_keys['real']['order']['key'],
            api_secret=bm_auth.api_keys['real']['order']['secret']
        )

        # 525600
        self.year_first = dt.datetime(self.now.year, 1, 1, tzinfo=dt.timezone.utc)
        # 880000 - 525600
        self.now_to_min = (self.now - self.year_first).total_seconds() // 60
        # 880000 - (525600 + 100000)

        self.client.sig_ended.connect(self.get_data)

        self.timer = QTimer()

    def parse_str_iso(self, date) -> dt.datetime:
        return ciso8601.parse_datetime(date)

    def add_min(self, time, mins):
        return time + dt.timedelta(minutes=mins)

    def format_str_iso(self, str_time: dt.datetime) -> str:
        return str_time.isoformat(timespec='milliseconds') \
                       .replace('+00:00', 'Z')

    def request_data(self):

        self.client.Trade.get_bucketed(
            '1m',
            symbol=self.inst['symbol'],
            count=self.count,
            start_time=self.last_time
        )

        time = self.parse_str_iso(self.last_time)
        new_time = self.add_min(time, 500)
        self.last_time = self.format_str_iso(new_time)
        self.requested += 1

    def get_data(self, ended: bool):
        print('get data')
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

        else:
            self.save_to_sql()

            print('saved !')
            print("Last index : {}".format(self.df.shape[0]))
            self.sig_finish.emit()

    def save_to_sql(self):
        conn = sqlite3.connect(PATH + '/bitmex.db')
        c = conn.cursor()

        new_data = self.df[self.start_length:]
        new_rows = [tuple(s) for s in new_data.values]

        c.executemany(ignore_insert('tradebin1m', 13), new_rows)

        conn.commit()
        conn.close()


class DataReader(QObject):
    sig_finished = pyqtSignal(object)

    def __init__(self, provider, instrument, parent=None):
        QObject.__init__(self)
        self.parent = parent
        self.provider = provider
        self.instrument = instrument
        inst = DATA[provider][instrument]
        self.r = Request(self.parent,
                         inst,
                         self.read_store_data(10000))

        self.r.sig_finish.connect(self.slt_finish)

    def start(self):
        self.r.request_data()

    def read_store_data(self, length):

        with sqlite3.connect(PATH + '/bitmex.db') as conn:
            c = conn.cursor()

            c.execute(select_last('tradebin1m', length))
            data = c.fetchall()

            c.execute(get_col_names('tradebin1m'))
            col_data = c.fetchall()

            cols = [x[1] for x in col_data]
            df = pd.DataFrame(data, columns=cols)

        return df

    def slt_finish(self):
        self.sig_finished.emit({
            'provider': self.provider,
            'symbol': self.instrument,
            'data_type': 'tradebin1m',
            'data': self.r.df
        })


attach_timer(Request, limit=10)
attach_timer(DataReader, limit=10)

if __name__ == '__main__':
    app = QCoreApplication([])

    handler = DataReader('bitmex', 'XBTUSD')
    handler.start()

    app.exec()
