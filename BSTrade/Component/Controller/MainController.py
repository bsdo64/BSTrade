from BSTrade.Component.View import MainWindowView
from BSTrade.Component.ViewModel.MainWindow import MainWindowViewModel
from BSTrade.Data.source import bs_ws, bs_req


class MainController:
    def __init__(self, exchange):
        self.view_model = MainWindowViewModel(exchange)
        self.view = MainWindowView(self.view_model)

        self.view.screenBtn.clicked.connect(self.add_symbols)

    def open(self):
        self.view.show()

        print('init data')
        self.init_data()

    def init_data(self):
        print('request data')
        bs_req.get_symbols(self.view_model.exchange.provider, {
            'count': 500
        })

        bs_req.sig.finished.connect(self.receive_data)
        # bs_ws.start_all()
        # bs_ws.open_auth()

    def receive_data(self, data):
        print(data)

    def add_symbols(self):
        self.view_model.append_smb('test')
        print(self.view_model.exchange.symbols)