from BSTrade.Widgets.CentralMain import CentralWidget
from BSTrade.Widgets.Exchange import ExchangeInfo
from BSTrade.Widgets.LoadingDialog import LoadingDialog


class WidgetStore:
    def __init__(self, parent=None):
        self.ExchangeInfo = ExchangeInfo(parent)
        self.CentralWidget = CentralWidget(parent)
        self.LoadingDialog = LoadingDialog(parent)
