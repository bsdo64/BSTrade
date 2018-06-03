import json
from .wsclient import WsClient
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QObject, QUrl, pyqtSignal


class BitmexWsClient(WsClient):
    sig_subscribed = pyqtSignal(dict)

    def __init__(self, test = False, api_key = None, api_secret = None):
        super().__init__()

        self.test = test
        self.api_key = api_key
        self.api_secret = api_secret
        self.subscribes = []

        if test:
            self.endpoint = "wss://testnet.bitmex.com/realtime"
        else:
            self.endpoint = "wss://www.bitmex.com/realtime"

        self.sig_message.connect(self.slot_message)

        self.timer = QTimer()
        self.timer.timeout.connect(self.slot_timer_timeout)
        self.a = None

    def ping(self):
        self.send('ping')

    def start(self):
        self.open(self.endpoint)
        return self

    def subscribe(self, *argv):
        list_args = list(argv)
        self.subscribes.append(list_args)
        data = {"op": "subscribe", "args": list_args}
        self.send(data)

    def slot_message(self, msg: str):
        self.timer.start(5000)
        self.set_data(msg)

        schema = self.json()
        if schema.get('types'):
            self.sig_subscribed.emit(schema)

    def slot_timer_timeout(self):
        self.a = 'timeout'