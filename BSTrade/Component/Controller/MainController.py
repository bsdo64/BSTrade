from PyQt5.QtWidgets import QApplication, QWidget

from BSTrade.Component.Model.App import AppModel
from BSTrade.Component.View.App import StartDialogView
from BSTrade.Component.View.MainWindow import MainWindowView


class MainController:
    def __init__(self):

        self.view = StartDialogView()
        self.model = AppModel()
        self.view.set_model(self.model)

        self.view.exchangeList.itemClicked.connect(self.select_exchange)
        self.view.exchangeList.itemEntered.connect(self.select_exchange)
        self.view.openBtn.clicked.connect(self.open_main)

    def open(self):
        self.view.show()

    def select_exchange(self, item):
        self.model.selected_exchange = self.model.exchanges[item.text()]
        self.view.exchangeTitle.setText(item.text())

    def open_main(self):
        self.w = MainWindowView(self.model)
        self.w.show()
        self.view.close()
