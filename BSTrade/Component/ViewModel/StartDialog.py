from BSTrade.Component.Model.Exchange import ExchangeModel
from BSTrade.Data.const import Exchange


class StartDialogViewModel:
    def __init__(self):
        self.exchanges = [ExchangeModel(exchange) for exchange in Exchange]
        self.selected = self.exchanges[0]

    def select_exchange(self, idx):
        self.selected = self.exchanges[idx]
        return self.selected
