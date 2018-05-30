import json
import time

from BSTrade.source_clients.auth.bitmex import api_keys
from BSTrade.source_clients.wsclient import WsClient

client = WsClient()


class TestWsClient(object):

    def test_connect(self, qtbot):
        with qtbot.waitSignal(client.websocket.connected, timeout=10000) as blocking:
            client.open("wss://testnet.bitmex.com/realtime")

        is_connected = client.is_connected()

        assert blocking.signal_triggered
        assert is_connected

    def test_message(self, qtbot):
        with qtbot.waitSignal(client.sig_message, timeout=10000) as blocking:
            client.send({"op": "subscribe", "args": ["orderBookL2:XBTUSD"]})

        data = blocking.args[0]
        assert blocking.signal_triggered
        assert isinstance(data, str)

        json_data = json.loads(data)

        assert json_data['success']
        assert json_data['subscribe'] == 'orderBookL2:XBTUSD'

        with qtbot.waitSignal(client.sig_message, timeout=10000):
            client.send({"op": "unsubscribe", "args": ["orderBookL2:XBTUSD"]})

    def test_ping(self, qtbot):
        with qtbot.waitSignal(client.sig_message, timeout=10000) as blocking:
            client.send('ping')

        data = blocking.args[0]
        assert blocking.signal_triggered
        assert isinstance(data, str)

        assert data == 'pong'

    def test_disconnect(self, qtbot):
        with qtbot.waitSignal(client.websocket.disconnected, timeout=10000) as blocking:
            client.close()

        assert blocking.signal_triggered
        assert not client.is_connected()