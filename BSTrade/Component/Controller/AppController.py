from PyQt5.QtWidgets import QApplication, QWidget

from BSTrade.Component.Controller import MainController
from BSTrade.Component.View.App import StartDialogView
from BSTrade.Component.ViewModel.StartDialog import StartDialogViewModel


class AppController:
    def __init__(self):
        self.model = StartDialogViewModel()
        self.view = StartDialogView(self.model)

        self.view.exchangeList.itemClicked.connect(self.select_exchange)
        self.view.exchangeList.itemSelectionChanged.connect(self.select_exchange)
        self.view.openBtn.clicked.connect(self.open_main)

    def open(self):
        self.view.show()

    def select_exchange(self):
        idx = self.view.exchangeList.selectedIndexes()[0]
        ex = self.model.select_exchange(idx.row())
        self.view.exchangeTitle.setText(ex.name)

    def open_main(self):
        self.main_c = MainController(self.model.selected)
        self.main_c.open()
        self.view.close()


if __name__ == '__main__':
    app = QApplication([])

    BSTrade = AppController()
    BSTrade.open()

    app.exec()