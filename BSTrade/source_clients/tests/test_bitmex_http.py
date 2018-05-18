import json
import pprint

from pytestqt.plugin import qtbot
from BSTrade.source_clients.bitmexhttpclient import BitmexHttpClient

client = BitmexHttpClient()


class TestBitmexHttp(object):
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

    # def test_post_apikey(self, qtbot):
    #     with qtbot.waitSignal(client.sig_reply, timeout=10000) as blocking:
    #         client.ApiKey.post("Hello", permissions=['order'])
    #
    #     msg = blocking.args[0]
    #     j = json.loads(msg)
    #     pprint.pprint(j)
    #
    #     assert blocking.signal_triggered
    #     assert type(msg) == str
    #     assert type(j) == list

    def test_post_chat(self, qtbot):
        with qtbot.waitSignal(client.sig_reply, timeout=10000) as blocking:
            client.Chat.post("Hm,,")

        msg = blocking.args[0]
        j = json.loads(msg)
        pprint.pprint(j)

        assert blocking.signal_triggered
        assert type(msg) == str
        assert type(j) == list
