import datetime as dt
import os
import sqlite3

import pandas as pd
import ciso8601

from PyQt5.QtCore import QTimer, pyqtSignal, QObject

from BSTrade.util.fn import attach_timer
from BSTrade.Api.auth import bitmex as bm_auth
from BSTrade.Api.auth.bitmex import api_keys
from BSTrade.Api import BitmexHttpClient, BitmexWsClient
from .const import Provider
from .bitmex import sqls as q
from BSTrade.Data.instruments import inst as bm_inst

PATH = os.path.dirname(os.path.abspath(__file__))
DATA = {
    Provider.BITMEX: bm_inst
}


class BitmexRequest(QObject):
    sig_finish = pyqtSignal()

    def __init__(self, until=None, inst=None, data=pd.DataFrame()):
        super().__init__()

        self.until = until
        self.inst = inst
        self.df = data
        self.start_length = len(self.df)

        if self.start_length > 0:
            self.start_time = self.add_min(data['timestamp'].iloc[-1], 1)
        else:
            self.start_time = "2017-01-01T00:00:00.000Z"

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

    def request_loop(self, option):
        params = option['params']

        self.client.Trade.get_bucketed(**params)

        self.last_time = self.add_min(self.last_time, 500)
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

    def save_to_sql(self):
        conn = sqlite3.connect(PATH + '/bitmex.db')
        c = conn.cursor()

        new_data = self.df[self.start_length:]
        new_rows = [tuple(s) for s in new_data.values]

        c.executemany(
            q.ignore_insert('tradebin1m', list(self.df.keys())),
            new_rows
        )

        conn.commit()
        conn.close()


class DataReader(QObject):
    sig_http_finish = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.r = {
            Provider.BITMEX: BitmexRequest(),
            Provider.UPBIT: None,
        }
        self.ws = {
            Provider.BITMEX: BitmexWsClient(
                test=False,
                api_key=api_keys['real']['order']['key'],
                api_secret=api_keys['real']['order']['secret']),
            Provider.UPBIT: None,
        }

        self.r.sig_finish.connect(self.slt_finish)

    def request(self, option):
        self.r[option['provider']].request(option)

    def request_loop(self, option):
        self.r[option['provider']].request_loop(option)

    def setup_ws(self, config):
        provider = config.get('provider')
        if provider == Provider.BITMEX:
            self.ws = BitmexWsClient(
                test=False,
                api_key=api_keys['real']['order']['key'],
                api_secret=api_keys['real']['order']['secret']
            )
        else:
            # default provider == Provider.BITMEX
            self.ws = BitmexWsClient(
                test=False,
                api_key=api_keys['real']['order']['key'],
                api_secret=api_keys['real']['order']['secret']
            )

        self.ws.sig_auth_success.connect(self.slt_ws_subscribe)
        self.ws.start()

    def slt_ws_subscribe(self):
        # web socket client connected with auth
        self.ws.subscribe('trade:XBTUSD',
                          'tradeBin1m:XBTUSD',
                          'orderBookL2:XBTUSD')

    def read_sql(self, length):

        with sqlite3.connect(PATH + '/bitmex.db') as conn:
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

    def slt_finish(self):
        self.sig_http_finish.emit({
            'provider': self.provider,
            'symbol': self.instrument,
            'data_type': 'tradebin1m',
            'data': self.r.df
        })


attach_timer(BitmexRequest, limit=10)
attach_timer(DataReader, limit=10)
