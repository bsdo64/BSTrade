from PyQt5.QtWidgets import QApplication

from BSTrade.Data.Models import Store
from BSTrade.Data.const import Exchange


class Api:
    def __init__(self, parent):
        self._store: Store = Store(parent)

    @property
    def store(self) -> 'Store':
        return self._store

    def exchanges(self):
        return self._store.markets.keys()

    def markets(self, prov):
        return self._store.markets[prov]

    def update_markets(self, prov):
        market = self._store.market(prov)
        market.update()

        return market


bs_api = Api(None)


if __name__ == '__main__':
    app = QApplication([])

    api = Api(parent=None)
    print(api.store)

    mrk = api.markets(Exchange.BITMEX)
    print(mrk)

    def print_markets():
        print(api.markets(Exchange.BITMEX).symbol('XBTUSD'))

    markets = api.update_markets(Exchange.BITMEX)
    markets.sig.symbol_updated.connect(print_markets)

    app.exec()