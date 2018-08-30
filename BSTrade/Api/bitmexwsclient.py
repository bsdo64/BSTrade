import time

from BSTrade.util.fn import attach_timer
from .wsclient import WsClient
from .auth.bitmex import generate_signature
from PyQt5.QtCore import pyqtSignal


class BitmexWsClient(WsClient):
    sig_subscribed = pyqtSignal(dict)
    sig_auth_success = pyqtSignal()

    def __init__(self, test=False, api_key=None, api_secret=None):
        super().__init__()

        self.test = test
        self.api_key = api_key
        self.api_secret = api_secret
        self.subscribes = set()

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

    def auth(self):
        if self.api_key:
            expires = int(round(time.time()) + 5)
            sign = generate_signature(
                self.api_secret,
                'GET',
                '/realtime',
                expires,
                ''
            )

            data = {
                "op": "authKeyExpires",
                "args": [self.api_key, expires, sign]
            }
            self.send(data)

    def get_subscribes(self) -> set:
        return self.subscribes

    def subscribe(self, *argv: str):
        self.subscribes.update(argv)
        data = {"op": "subscribe", "args": list(argv)}
        self.send(data)

    def unsubscribe(self, *argv: str):
        self.subscribes -= set(argv)
        data = {"op": "unsubscribe", "args": list(argv)}
        self.send(data)

    def slot_message(self, msg: str):
        j = self.json()

        if j.get('version'):
            # connected success -> auth
            self.auth()
        elif j.get('success'):
            if j.get('request').get('op') == 'authKeyExpires':
                # auth success
                self.sig_auth_success.emit()


attach_timer(BitmexWsClient)
