import pandas as pd

from PyQt5.QtCore import pyqtSignal, QObject

from BSTrade.Api.auth.bitmex import api_keys
from BSTrade.Api import BitmexWsClient
from BSTrade.Data.reader import DataReader
from BSTrade.Lib.BSChart.Model import ChartModel


class Store(QObject):
    sig_init = pyqtSignal()

    def __init__(self, config, parent=None):
        super().__init__(parent)

        self.config = config
        self.cache = {}
        self.chart_models = []
        self.data_len = 100000
        self.reader = DataReader()
        self.writer = DataWriter()
        self.ws: BitmexWsClient = None

        self.setup_ws(config)

    def get_data(self, provider, *args):

        d = self.cache.get(provider, {})
        for i in args:
            d = d.get(i, {})

        return d

    def request_initial_data(self):
        self.reader.request({
            'provider': 'bitmex',
            'endpoint': ['get', 'trade', 'bucketed'],
            'params': {'bin_size': '1m', 'symbol': 'XBTUSD', 'count': 500},
            'symbol': 'XBTUSD',
            'option': {}
        })
        self.reader.sig_finished.connect(self.slt_finish_init_data)

    def slt_finish_init_data(self, data: dict):
        df: pd.DataFrame = data['data']
        provider = data['provider']
        symbol = data['symbol']
        data_type = data['data_type']

        """
        Structure :
        data = {
            'provider': self.provider,
            'symbol': self.instrument,
            'data_type': 'tradebin1m',
            'data': self.r.df
        }
        """

        if hasattr(df, 'timestamp'):
            df['timestamp_str'] = df['timestamp']
            df['timestamp'] = df['timestamp'].astype('datetime64')

        np_data = {key: df[key].values for key in df.keys()}

        self.cache[provider] = {
            'price': {
                symbol: {
                    data_type: np_data
                },
            }
        }
        self.data_len = len(data['data'])
        self.sig_init.emit()

    def setup_ws(self, config):
        provider = config.get('provider')
        if provider == 'bitmex':
            self.ws = BitmexWsClient(
                test=False,
                api_key=api_keys['real']['order']['key'],
                api_secret=api_keys['real']['order']['secret']
            )
        else:
            # default provider == 'bitmex'
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

    def get_model(self, option):
        provider = option['provider']
        symbol = option['symbol']
        return self.cache[provider]['price'][symbol]

    def create_chart_model(self, idx: str, data_type: str):
        provider, symbol = idx.split(':')
        try:
            data = self.cache[provider]['price'][symbol][data_type]
        except KeyError:
            data = {}

        model = ChartModel(idx=idx, store=self, ws=self.ws)
        self.chart_models.append(model)
        return model
