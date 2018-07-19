from .wsclient import WsClient
from PyQt5.QtCore import pyqtSignal


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
        self.set_data(msg)

        schema = self.json()
        if schema.get('types'):
            self.sig_subscribed.emit(schema)
