import datetime as dt
import os
import sqlite3

import pandas as pd
import ciso8601

from PyQt5.QtCore import QTimer, pyqtSignal, QObject, pyqtSlot, QCoreApplication

from BSTrade.util.fn import attach_timer
from BSTrade.Api.auth import bitmex as bm_auth
from BSTrade.Api.auth.bitmex import api_keys
from BSTrade.Api import BitmexHttpClient, BitmexWsClient
from BSTrade.Data.const import Provider
from BSTrade.Data.bitmex import sqls as q

PATH = os.path.dirname(os.path.abspath(__file__))


class BitmexRequester(QObject):
    sig_finish = pyqtSignal()

    def __init__(self, until=None, inst=None):
        super().__init__()

        self.until = until
        self.inst = inst

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

        self.client.sig_ended.connect(self.slt_get_data)

        self.timer = QTimer()

    def parse_str_iso(self, date) -> dt.datetime:
        return ciso8601.parse_datetime(date)

    def add_min(self, time, mins):
        if type(time) == str:
            time = self.parse_str_iso(time)
            new_t = time + dt.timedelta(minutes=mins)
            return self.format_str_iso(new_t)
        else:
            return time + dt.timedelta(minutes=mins)

    def format_str_iso(self, str_time: dt.datetime) -> str:
        return str_time.isoformat(timespec='milliseconds') \
                       .replace('+00:00', 'Z')

    def request(self, option):
        params = option['params']

        self.client.Trade.get_bucketed(**params)

    def request_loop(self, params=None):
        if params is None:
            params = self.params
        else:
            self.params = params

        self.client.Trade.get_bucketed(**params)

        self.params['start_time'] = self.add_min(self.params['start_time'], 500)
        self.requested += 1

    def slt_get_data(self, ended: bool):
        j = self.client.json()
        self.rate_limit = self.client.header('x-ratelimit-remaining')
        print('Get data, rate-limit : ', self.rate_limit)

        if len(j) > 0:
            new_df = pd.DataFrame(j)
            self.df = self.df.append(new_df, ignore_index=True, sort=False)
            self.timer.singleShot(1000, self.request_loop)

        elif (self.count < len(j)) or \
                (len(j) == 0) or \
                (self.until < self.count * self.requested if self.until else False):
            self.save_to_sql()

            print('saved !')
            print("Last index : {}".format(self.df.shape[0]))
            self.sig_finish.emit()

    def read_sql(self, length):

        with sqlite3.connect(PATH + '/bitmex/bitmex.db') as conn:
            c = conn.cursor()

            self.check_tables(c)

            c.execute(q.select_last('tradebin1m', length))
            data = c.fetchall()

            c.execute(q.get_col_names('tradebin1m'))
            col_data = c.fetchall()

            cols = [x[1] for x in col_data]
            df = pd.DataFrame(data, columns=cols)

        return df

    def check_tables(self, cursor: sqlite3.Cursor):
        query = q.create_table('tradebin1m')
        cursor.execute(query)

        query = q.create_index('tradebin1m', 'timestamp', uniq=False)
        cursor.execute(query)

        query = q.create_index('tradebin1m', 'id', uniq=True)
        cursor.execute(query)

    def save_to_sql(self):
        conn = sqlite3.connect(PATH + '/bitmex/bitmex.db')
        c = conn.cursor()

        new_data = self.df[self.start_length:]
        new_rows = [tuple(s) for s in new_data.values]

        c.executemany(
            q.ignore_insert('tradebin1m', list(self.df.keys())),
            new_rows
        )

        conn.commit()
        conn.close()

    def trade_bin(self, min):
        self.df = self.read_sql(10000)
        self.start_length = len(self.df)
        if self.start_length > 0:
            self.start_time = self.add_min(self.df['timestamp'].iloc[-1], 1)
        else:
            self.start_time = "2017-01-01T00:00:00.000Z"

        self.last_time = self.start_time

        self.request_loop({
                'bin_size': '1m',
                'symbol': self.inst,
                'count': 500,
                'start_time': self.last_time
            })


http_client = {
    Provider.BITMEX: BitmexRequester(),
    Provider.UPBIT: BitmexRequester(),
}

ws_client = {
    Provider.BITMEX: BitmexWsClient(
        test=False,
        api_key=api_keys['real']['order']['key'],
        api_secret=api_keys['real']['order']['secret']
    ),
    Provider.UPBIT: BitmexWsClient(
        test=False,
        api_key=api_keys['real']['order']['key'],
        api_secret=api_keys['real']['order']['secret']
    ),
}


class DataReader(QObject):
    sig_http_finish = pyqtSignal(object)

    def __init__(self, provider: Provider):
        super().__init__()
        self.provider = provider
        self.r = http_client[provider]
        self.ws = ws_client[provider]
        self.auth_success = False

        self.setup_signals()

    def setup_signals(self):
        self.r.sig_finish.connect(self.on_finished)
        self.ws.sig_auth_success.connect(self.on_ws_authed)

        self.ws.start()

    @pyqtSlot()
    def on_ws_authed(self):
        self.auth_success = True

    @pyqtSlot(object)
    def on_finished(self, data):
        self.sig_http_finish.emit({
            'provider': self.provider,
            'symbol': self.instrument,
            'data_type': 'tradebin1m',
            'data': self.r.df
        })


attach_timer(BitmexRequester, limit=10)
attach_timer(DataReader, limit=10)


if __name__ == '__main__':
    app = QCoreApplication([])

    req = BitmexRequester(inst='XBTUSD')
    req.trade_bin(10)

    app.exec()
