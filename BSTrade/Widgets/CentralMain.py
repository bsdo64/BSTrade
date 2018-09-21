from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QWidget, QHBoxLayout, \
    QPlainTextEdit, QAction

from BSTrade.Data.const import Exchange
from BSTrade.Widgets.Exchange import ExchangeInfo
from BSTrade.util.fn import attach_timer


class ExchangeList(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.setMaximumWidth(100)

        for prov in Exchange:
            QListWidgetItem(prov.name, self)


class CentralWidget(QWidget):
    def __init__(self, parent: 'Main'):
        super().__init__(parent)
        self.parent = parent
        self.setContentsMargins(0, 0, 0, 0)

        self.hbox = QHBoxLayout(self)
        self.hbox.setContentsMargins(0, 0, 0, 0)
        self.hbox.setSizeConstraint(self.hbox.SetDefaultConstraint)
        self.hbox.setSpacing(0)

        self.hbox.addWidget(QPlainTextEdit())

    def toggle_left_pane(self, b):
        pane_at = 0
        if b:
            exchange_list = ExchangeList(self)
            exchange_list.itemClicked.connect(self.select_provider)
            self.hbox.insertWidget(pane_at, exchange_list)
        else:
            btn: QWidget = self.hbox.itemAt(pane_at).widget()
            self.hbox.removeWidget(btn)
            btn.deleteLater()

    def select_provider(self, item: QListWidgetItem):
        prov = Exchange[item.text()]
        action: QAction = self.parent.findChild(QAction, 'ex_action')
        action.trigger()

        self.set_exchange_view()
        self.parent.view_store.ExchangeInfo.exchange_selected(prov)

    def set_exchange_view(self):
        layout_item = self.hbox.itemAt(0)
        center_widget = layout_item.widget()
        if isinstance(center_widget, ExchangeInfo):
            return
        else:
            center_widget.deleteLater()
            self.hbox.removeItem(layout_item)
            self.hbox.addWidget(self.parent.view_store.ExchangeInfo)


attach_timer(CentralWidget)