import json
from pytestqt.plugin import qtbot
from BSTrade.source_clients.httpclient import HttpClient

client = HttpClient()


class TestHttpClient(object):

    def test_get(self, qtbot):

        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.get('https://jsonplaceholder.typicode.com/posts')

        j = client.json()

        assert blocking.signal_triggered
        assert type(j) == list

    def test_post(self, qtbot):

        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            header = {
                "content-type":"application/json; charset=UTF-8"
            }
            data = {
                "title": "hello",
                "body": "world",
                "userId": 1
            }

            data_bytes = json.dumps(data).encode()

            client.set_header(header)
            client.post('https://jsonplaceholder.typicode.com/posts/1', data_bytes)

        j = client.json()
        print(j)

        assert blocking.signal_triggered
        assert type(j) == dict

    def test_set_header(self):

        header = {
            'Hello': 'world'
        }
        client.set_header(header)

        assert client.request.hasRawHeader(b'accept')
        assert client.request.hasRawHeader(b'user-agent')
        assert client.request.hasRawHeader(b'Hello')
        assert not client.request.hasRawHeader(b'False')
