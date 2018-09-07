from BSTrade.Widgets.Exchange import ExchangeInfo


class WidgetStore:
    def __init__(self, api, parent=None):
        self.api = api
        self.ExchangeInfo = ExchangeInfo(api, parent)
