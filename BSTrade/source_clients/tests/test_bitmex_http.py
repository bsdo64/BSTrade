import json
import pprint

from pytestqt.plugin import qtbot
from BSTrade.source_clients.httpclient import HttpClient
from BSTrade.source_clients.bitmexhttpclient import BitmexHttpClient

client = BitmexHttpClient()
tmp_api_key_id = None


class TestBitmexHttp(object):
    def test_http_instance(self):
        assert issubclass(BitmexHttpClient, HttpClient)

    def test_client_instance(self):
        assert isinstance(client, BitmexHttpClient)
        assert client.test is False
        assert client.api_key is None
        assert client.api_secret is None

    def test_client_instance_by_api_key(self):
        client1 = BitmexHttpClient(test=True, api_key=None, api_secret=None)

        assert isinstance(client1, BitmexHttpClient)
        assert client.test is False
        assert client.api_key is None
        assert client.api_secret is None

    def test_base_uri(self, qtbot):
        with qtbot.waitSignal(client.sig_reply, timeout=10000) as blocking:
            client.get_base_uri()

        msg = blocking.args[0]
        j = json.loads(msg)

        assert blocking.signal_triggered
        assert type(msg) == str
        assert 'name' in j
        assert 'version' in j
        assert 'timestamp' in j

    def test_get_announcement(self, qtbot):
        with qtbot.waitSignal(client.sig_reply, timeout=10000) as blocking:
            client.Announcement.get()

        msg = blocking.args[0]
        j = json.loads(msg)

        assert blocking.signal_triggered
        assert type(msg) == str
        assert type(j) == list

    def test_get_announcement_urgent(self, qtbot):
        with qtbot.waitSignal(client.sig_reply, timeout=10000) as blocking:
            client.Announcement.get_urgent()

        msg = blocking.args[0]
        j = json.loads(msg)

        assert blocking.signal_triggered
        assert type(msg) == str
        assert type(j) == list

    def test_get_apikey(self, qtbot):
        with qtbot.waitSignal(client.sig_reply, timeout=10000) as blocking:
            client.ApiKey.get()

        msg = blocking.args[0]
        j = json.loads(msg)

        assert blocking.signal_triggered
        assert type(msg) == str
        assert type(j) == list

    def test_get_chat(self, qtbot):
        with qtbot.waitSignal(client.sig_reply, timeout=10000) as blocking:
            client.Chat.get()

        msg = blocking.args[0]
        j = json.loads(msg)

        assert blocking.signal_triggered
        assert type(msg) == str
        assert type(j) == list

    def test_post_chat(self, qtbot):
        with qtbot.waitSignal(client.sig_reply, timeout=10000) as blocking:
            client.Chat.post("캬", channelID=4.0)

        msg = blocking.args[0]
        j = json.loads(msg)

        assert blocking.signal_triggered
        assert type(msg) == str
        assert type(j) == dict
        assert 'channelID' in j
        assert 'date' in j
        assert 'fromBot' in j
        assert 'html' in j
        assert 'id' in j
        assert 'message' in j
        assert 'user' in j

    def test_get_chat_channels(self, qtbot):
        with qtbot.waitSignal(client.sig_reply, timeout=10000) as blocking:
            client.Chat.get_channels()

        msg = blocking.args[0]
        j = json.loads(msg)

        assert blocking.signal_triggered
        assert type(msg) == str
        assert type(j) == list
        assert len(j) == 7

    def test_get_chat_connected(self, qtbot):
        with qtbot.waitSignal(client.sig_reply, timeout=10000) as blocking:
            client.Chat.get_connected()

        msg = blocking.args[0]
        j = json.loads(msg)

        assert blocking.signal_triggered
        assert type(msg) == str
        assert type(j) == dict
        assert 'users' in j
        assert 'bots' in j
