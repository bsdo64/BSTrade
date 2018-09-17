from PyQt5.QtWidgets import QDialog, QListWidgetItem

from BSTrade.Component.Model.App import AppModel
from BSTrade.Component.conf import load_ui
from BSTrade.Component.View.Ui import ui_start_dialog

_ui: ui_start_dialog.Ui_App = load_ui('start_dialog')


class StartDialogView(QDialog, _ui):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setupUi(self)
        self.model = None

    def set_model(self, model: AppModel):
        self.model = model

        for item in model.exchanges:
            i = QListWidgetItem(item.name)
            self.exchangeList.addItem(i)
