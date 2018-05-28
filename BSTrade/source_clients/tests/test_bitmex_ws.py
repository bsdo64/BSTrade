import time

from PyQt5.QtWidgets import QApplication

from BSTrade.source_clients.auth.bitmex import api_keys
from BSTrade.source_clients.wsclient import WsClient
from BSTrade.source_clients.bitmexwsclient import BitmexWsClient

api_key = api_keys['test']['order']['key']
api_secret = api_keys['test']['order']['secret']
isWithdraw = api_keys['test']['order']['withdraw']


class TestBitmexWsClient(object):
    def test_is_http_instance(self):
        client = BitmexWsClient(test=True, api_key=api_key, api_secret=api_secret, )

        assert issubclass(BitmexWsClient, WsClient)

        client.close()

    def test_instance(self):
        client = BitmexWsClient(test=True, api_key=api_key, api_secret=api_secret, )
        assert isinstance(client, BitmexWsClient)
        assert client.test is True
        assert client.api_key is api_key
        assert client.api_secret is api_secret
        client.close()

    def test_instance_by_api_key(self):
        client = BitmexWsClient(test=True, api_key=api_key, api_secret=api_secret)

        assert isinstance(client, BitmexWsClient)
        assert client.test is True
        assert client.api_key is api_key
        assert client.api_secret is api_secret

        client.close()

    def test_connect(self, qtbot):
        client = BitmexWsClient(test=True, api_key=api_key, api_secret=api_secret)

        with qtbot.waitSignals([client.sig_message], order="strict", timeout=10000) as blocking:
            client.start()

        assert blocking.signal_triggered

        data = client.data()
        assert type(data) == str

        data = client.json()
        assert type(data) == dict
        assert 'info' in data
        assert 'version' in data
        assert 'timestamp' in data
        assert 'docs' in data
        assert 'limit' in data
        client.close()

    def test_pong(self, qtbot):
        client = BitmexWsClient(test=True, api_key=api_key, api_secret=api_secret)
        with qtbot.waitSignal(client.sig_message, timeout=10000) as blocking:
            client.start()

        assert blocking.signal_triggered

        connected = client.json()
        assert type(connected) == dict
        assert 'info' in connected
        assert 'version' in connected
        assert 'timestamp' in connected
        assert 'docs' in connected
        assert 'limit' in connected

        with qtbot.waitSignal(client.sig_message, timeout=10000) as blocking:
            client.ping()

        assert blocking.signal_triggered
        assert type(client.data()) == str
        assert client.data() == 'pong'

    def test_data(self, qtbot):
        client = BitmexWsClient(test=True, api_key=api_key, api_secret=api_secret)
        with qtbot.waitSignal(client.sig_message, timeout=10000) as blocking:
            client.start()

        assert blocking.signal_triggered

        connected = client.json()
        assert type(connected) == dict
        assert 'info' in connected
        assert 'version' in connected
        assert 'timestamp' in connected
        assert 'docs' in connected
        assert 'limit' in connected

        with qtbot.waitSignal(client.sig_message, timeout=10000) as blocking:
            client.send({"op": "subscribe", "args": ["trade:XBTUSD"]})

        assert blocking.signal_triggered

        print(client.data())