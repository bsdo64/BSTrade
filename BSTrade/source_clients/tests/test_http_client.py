import json
from pytestqt.plugin import qtbot
from BSTrade.source_clients.httpclient import HttpClient

client = HttpClient()


class TestHttpClient(object):

    def test_http_request(self, qtbot):

        with qtbot.waitSignal(client.sig_reply, timeout=10000) as blocking:
            client.get('https://www.bitmex.com/api/v1/quote?symbol=XBTUSD&count=1&reverse=false')

        msg = blocking.args[0]

        assert blocking.signal_triggered
        assert type(msg) == str

    def test_set_header(self):

        header = {
            'Hello': 'world'
        }
        client.set_header(header)

        assert client.request.hasRawHeader(b'accept')
        assert client.request.hasRawHeader(b'user-agent')
        assert client.request.hasRawHeader(b'Hello')
        assert not client.request.hasRawHeader(b'False')
