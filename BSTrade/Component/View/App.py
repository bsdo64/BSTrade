from PyQt5.QtWidgets import QDialog, QListWidgetItem

from BSTrade.Component.ViewModel.StartDialog import StartDialogViewModel
from BSTrade.Component.conf import load_ui
from BSTrade.Component.View.Ui import ui_start_dialog

_ui: ui_start_dialog.Ui_App = load_ui('start_dialog')


class StartDialogView(QDialog, _ui):
    def __init__(self, model: StartDialogViewModel, parent=None):
        super().__init__(parent)

        self.setupUi(self)
        self.model = model
        self.create_list()

    def create_list(self):
        for ex_model in self.model.exchanges:
            i = QListWidgetItem(ex_model.name)
            self.exchangeList.addItem(i)
