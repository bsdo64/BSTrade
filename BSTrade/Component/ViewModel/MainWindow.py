from BSTrade.Component.Model.Exchange import ExchangeModel
from BSTrade.Component.Model.QListModel import QListModel


class MainWindowViewModel:
    def __init__(self, exchange: ExchangeModel):
        self._exchange = exchange
        self._sym_list_model = QListModel(exchange.symbols)

    @property
    def exchange(self):
        return self._exchange

    @property
    def sym_list_model(self):
        return self._sym_list_model

    def append_smb(self, smb):
        self._exchange.symbols.append(smb)