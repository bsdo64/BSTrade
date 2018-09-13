from BSTrade.Widgets.Exchange import ExchangeInfo


class WidgetStore:
    def __init__(self, parent=None):
        self.ExchangeInfo = ExchangeInfo(parent)
