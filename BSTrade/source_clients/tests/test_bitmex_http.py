from BSTrade.source_clients.auth.bitmex import api_keys
from BSTrade.source_clients.httpclient import HttpClient
from BSTrade.source_clients.bitmexhttpclient import BitmexHttpClient

api_key = api_keys['test']['order']['key']
api_secret = api_keys['test']['order']['secret']
isWithdraw = api_keys['test']['order']['withdraw']

client = BitmexHttpClient(test=True,
                          api_key=api_key,
                          api_secret=api_secret, )


class TestBitmexHttpClient(object):
    def test_is_http_instance(self):
        assert issubclass(BitmexHttpClient, HttpClient)

    def test_instance(self):
        assert isinstance(client, BitmexHttpClient)
        assert client.test is True
        assert client.api_key is api_key
        assert client.api_secret is api_secret

    def test_instance_by_api_key(self):
        client1 = BitmexHttpClient(test=True, api_key='abc', api_secret='abc')

        assert isinstance(client1, BitmexHttpClient)
        assert client1.test is True
        assert client1.api_key is 'abc'
        assert client1.api_secret is 'abc'

    def test_base_uri(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.get_base_uri()

        assert blocking.signal_triggered

        assert client.status() == 200
        assert type(client.json()) == dict

        j = client.json()

        assert 'name' in j
        assert 'version' in j
        assert 'timestamp' in j


class TestBitmexAnnouncement(object):
    def test_get(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Announcement.get()

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == list

    def test_get_urgent(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Announcement.get_urgent()

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == list


class TestBitmexApiKey(object):
    def test_get(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.ApiKey.get()

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == list


class TestBitmexChat(object):
    def test_get_1(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Chat.get()

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == list

    def test_get_2(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Chat.get(count=10)

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == list
        assert len(j) == 10

    def test_post(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Chat.post(" ", channel_id=1)

        j = client.json()

        assert blocking.signal_triggered
        assert type(j) == dict
        # assert 'channelID' in j
        # assert 'date' in j
        # assert 'fromBot' in j
        # assert 'html' in j
        # assert 'id' in j
        # assert 'message' in j
        # assert 'user' in j

        assert 'error' in j
        assert 'message' in j.get('error')
        assert 'name' in j.get('error')

    def test_get_channels(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Chat.get_channels()

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == list
        assert len(j) == 7

    def test_get_connected(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Chat.get_connected()

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == dict
        assert 'users' in j
        assert 'bots' in j


class TestBitmexExecution(object):
    def test_get(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Execution.get('XBTUSD')

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == list

    def test_get_trade_history(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Execution.get_trade_history('XBTUSD')

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == list


class TestBitmexFunding(object):
    def test_get(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Funding.get('XBTUSD')

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == list


class TestBitmexInstrument(object):
    def test_get(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Instrument.get('XBTUSD')

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == list

    def test_get_active(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Instrument.get_active()

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == list

    def test_get_active_and_indices(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Instrument.get_active_and_indices()

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == list

    def test_get_active_intervals(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Instrument.get_active_intervals()

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == dict

    def test_get_composite_index(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Instrument.get_composite_index()

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == list

    def test_get_indices(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Instrument.get_indices()

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == list


class TestBitmexInsurance(object):
    def test_get(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Insurance.get()

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == list


class TestBitmexLeaderboard(object):
    def test_get(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Leaderboard.get()

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == list

    def test_get_name(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Leaderboard.get_name()

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == dict


class TestBitmexLiquidation(object):
    def test_get(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Liquidation.get('XBTUSD')

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == list


class TestBitmexNotification(object):
    """
        /notification

        Not supported yet
    """

    def test_get(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Notification.get()

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 403
        assert type(j) == dict

        assert 'error' in j
        assert 'message' in j['error']
        assert 'name' in j['error']


class TestBitmexOrder(object):
    def test_get(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Order.get('XBTUSD')

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == list

    def test_put(self, qtbot):
        # Set position cross
        with qtbot.waitSignal(client.sig_ended, timeout=10000):
            client.Position.post_isolate('XBTUSD', enabled=False)

        # Post order
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Order.post('XBTUSD', order_qty=3, price=1000)

        ordered = client.json()
        assert blocking.signal_triggered
        assert client.status() == 200

        order_id = ordered['orderID']

        # Put(amend) order
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Order.put(order_id=order_id, order_qty=3, price=1100)

        j = client.json()
        assert blocking.signal_triggered
        assert client.status() == 200
        assert j['orderID'] == order_id
        assert j['orderQty'] == 3
        assert j['price'] == 1100

        # delete order
        with qtbot.waitSignal(client.sig_ended, timeout=10000):
            client.Order.delete(order_id=order_id)

        deleted = client.json()
        assert blocking.signal_triggered
        assert client.status() == 200
        assert deleted[0]['orderID'] == order_id
        assert deleted[0]['orderQty'] == 3
        assert deleted[0]['price'] == 1100

    def test_post(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Order.post('XBTUSD', order_qty=3, price=1000)

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == dict

    def test_delete(self, qtbot):
        # pre-order
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Order.post('XBTUSD', order_qty=3, price=1000)

        ordered = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(ordered) == dict

        # test_delete
        order_id = ordered['orderID']
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Order.delete(order_id=order_id)

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == list
        assert j[0]['orderID'] == order_id

    def test_delete_all(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Order.delete_all()

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == list

    def test_put_bulk(self, qtbot):
        # Post bulk order
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Order.post_bulk(orders=[{"symbol":"XBTUSD","price": 1000,"orderQty": 3}])

        ordered = client.json()
        ordered_id = ordered[0]['orderID']

        # Put bulk order
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Order.put_bulk(orders=[{"orderID": ordered_id, "price": 1000, "orderQty": 4}])

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == list
        assert j[0]['orderID'] == ordered_id

        # delete order
        with qtbot.waitSignal(client.sig_ended, timeout=10000):
            client.Order.delete(order_id=ordered_id)

        deleted = client.json()
        assert blocking.signal_triggered
        assert client.status() == 200
        assert deleted[0]['orderID'] == ordered_id
        assert deleted[0]['orderQty'] == 4
        assert deleted[0]['price'] == 1000

    def test_post_bulk(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Order.post_bulk(orders=[{"symbol":"XBTUSD","price": 1000,"orderQty": 3}])

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == list

    def test_post_cancel_all_after(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Order.post_cancel_all_after(0)

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == dict


class TestBitmexOrderBook(object):
    def test_get_l2(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.OrderBook.get_l2('XBTUSD')

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == list


class TestBitmexPosition(object):
    def test_get(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Position.get()

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == list

    def test_post_isolate_1(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Position.post_isolate('XBTUSD', enabled=True)

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == dict
        assert not bool(j['crossMargin'])

    def test_post_isolate_2(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Position.post_isolate('XBTUSD', enabled=False)

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == dict
        assert bool(j['crossMargin'])

    def test_post_leverage_1(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Position.post_leverage('XBTUSD', 0)

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == dict
        assert bool(j['crossMargin'])

    def test_post_leverage_2(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Position.post_leverage('XBTUSD', 0.01)

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == dict
        assert not bool(j['crossMargin'])
        assert j['leverage'] == 0.01

    def test_post_leverage_3(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Position.post_leverage('XBTUSD', 100)

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == dict
        assert not bool(j['crossMargin'])
        assert j['leverage'] == 100

    def test_post_risk_limit(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Position.post_risk_limit('XBTUSD', 500 * 100000000)

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == dict
        assert j['riskLimit'] == 500 * 100000000

        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Position.post_risk_limit('XBTUSD', 200 * 100000000)

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == dict
        assert not bool(j['crossMargin'])
        assert j['riskLimit'] == 200 * 100000000

    def test_post_transfer_margin(self, qtbot):
        # Set leverage x1
        with qtbot.waitSignal(client.sig_ended, timeout=10000):
            client.Position.post_leverage('XBTUSD', 1)

        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Position.post_transfer_margin('XBTUSD', 10000)

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == dict

        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Position.post_transfer_margin('XBTUSD', -9000)

        j = client.json()

        assert blocking.signal_triggered
        assert 200 == client.status()
        assert type(j) == dict


class TestBitmexQuote(object):
    def test_get(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Quote.get('XBTUSD', count=10)

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == list
        assert len(j) == 10

    def test_get_bucketed(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Quote.get_bucketed('1m', 'XBTUSD', count=10)

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == list
        assert len(j) == 10


class TestBitmexSchema(object):
    def test_get(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Schema.get()

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == dict

    def test_get_websocket_help(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Schema.get_websocket_help()

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == dict


class TestBitmexSettlement(object):
    def test_get(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Settlement.get('XBTUSD')

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == list


class TestBitmexStats(object):
    def test_get(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Stats.get()

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == list

    def test_get_history(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Stats.get_history()

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == list

    def test_get_history_usd(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Stats.get_history_usd()

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == list


class TestBitmexTrade(object):
    def test_get(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Trade.get('XBTUSD', count=10)

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == list
        assert len(j) == 10

    def test_get_bucketed(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.Trade.get_bucketed('1m', symbol='XBTUSD', count=10)

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == list
        assert len(j) == 10


class TestBitmexUser(object):
    tmp_id = None

    def test_get(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.User.get()

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == dict
        assert 'id' in j
        assert 'ownerId' in j
        assert 'firstname' in j
        assert 'lastname' in j
        assert 'username' in j
        assert 'email' in j

    def test_put(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.User.put(firstname='hello')

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 403
        assert type(j) == dict

        assert 'error' in j
        assert 'message' in j.get('error')
        assert 'name' in j.get('error')

        assert j['error']['message'] == 'Access Denied'
        assert j['error']['name'] == 'HTTPError'

    def test_get_affiliate_status(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.User.get_affiliate_status()

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == dict

    def test_post_cancel_withdrawal(self, qtbot):
        if not isWithdraw:
            assert True
            return

        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.User.post_cancel_withdrawal('token')

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == dict

    def test_get_check_referral_code(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.User.get_check_referral_code()

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 404
        assert type(j) == dict

    def test_get_commission(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.User.get_commission()

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == dict

    def test_post_confirm_email(self, qtbot):
        if not isWithdraw:
            assert True
            return

        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.User.post_confirm_email('token')

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == dict

    def test_post_confirm_enable_tfa(self, qtbot):
        if not isWithdraw:
            assert True
            return

        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.User.post_confirm_enable_tfa('token')

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == dict

    def test_post_confirm_withdrawal(self, qtbot):
        if not isWithdraw:
            assert True
            return

        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.User.post_confirm_withdrawal('token')

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == dict

    def test_get_deposit_address(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.User.get_deposit_address()

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == str

    def test_post_disable_tfa(self, qtbot):
        if not isWithdraw:
            assert True
            return

        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.User.post_disable_tfa('token')

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == dict

    def test_post_logout(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.User.post_logout()

        assert blocking.signal_triggered
        assert client.status() == 204  # No content

    def test_post_logout_all(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.User.post_logout_all()

        j = client.json()

        assert blocking.signal_triggered
        if client.status() == 200:
            assert 'count' in j
            assert isinstance(j['count'], int)

        elif client.status() == 403:
            assert dict == type(j)

    def test_get_min_withdrawal_fee(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.User.get_min_withdrawal_fee('XBt')

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == dict

    def test_get_margin(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.User.get_margin('XBt')

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == dict

    def test_post_preference(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.User.post_preferences(prefs='{"hello": "world"}', overwrite=True)

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == dict
        assert 'hello' in j['preferences']
        assert 'world' == j['preferences']['hello']

    def test_post_request_enable_tfa(self, qtbot):
        if not isWithdraw:
            assert True
            return

        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.User.post_request_enable_tfa()

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == dict

    def test_post_request_withdrawal(self, qtbot):
        if not isWithdraw:
            assert True
            return

        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.User.post_request_withdrawal('XBt', 1, 'abcde')

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == dict

    def test_get_wallet(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.User.get_wallet()

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == dict

    def test_get_wallet_history(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.User.get_wallet_history()

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == list

    def test_get_wallet_summary(self, qtbot):
        with qtbot.waitSignal(client.sig_ended, timeout=10000) as blocking:
            client.User.get_wallet_summary()

        j = client.json()

        assert blocking.signal_triggered
        assert client.status() == 200
        assert type(j) == list
