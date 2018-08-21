import talib
from PyQt5.QtCore import pyqtSignal, QSize, QRect, Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QWidget, QHBoxLayout, QLabel,\
    QPushButton, QTreeWidget, QSizePolicy, QTreeWidgetItem


class IndicatorDialog(QDialog):
    sig_open_indicator = pyqtSignal(str)

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        self.main_vbox = QVBoxLayout(self)
        self.title_box = QWidget(self)
        self.content_box = QHBoxLayout()

        self.contents = QWidget(self)
        self.contents_vbox = QVBoxLayout()
        self.menu = QWidget(self)

        self.setup_ui()

    def setup_ui(self):
        if self.objectName():
            self.setObjectName("IndicatorDialog")

        self.resize(640, 480)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setMinimumSize(self.size())
        self.setMaximumSize(self.size())
        self.setSizeGripEnabled(False)

        self.main_vbox.setSpacing(0)
        self.main_vbox.setObjectName("MainVbox")
        self.main_vbox.setContentsMargins(0, 0, 0, 0)

        self.title_box.setObjectName("TitleBox")
        self.title_box.setMaximumSize(QSize(16777215, 40))
        self.title_box.setStyleSheet("""
            border-bottom: 1px solid gray;
        """)

        title_lb = QLabel(self.title_box)
        title_lb.setObjectName("title_lb")
        title_lb.setText("Indicator")
        title_lb.setGeometry(QRect(20, 10, 59, 16))
        title_lb.setLineWidth(0)
        title_lb.setScaledContents(False)
        title_lb.setAlignment(Qt.AlignCenter)
        title_lb.setIndent(0)
        title_lb.setTextInteractionFlags(Qt.NoTextInteraction)

        self.main_vbox.addWidget(self.title_box)

        self.content_box.setSpacing(0)
        self.content_box.setObjectName("ContentBox")

        self.menu.setObjectName("Menu")
        self.menu.setMaximumSize(QSize(120, 16777215))
        self.menu.setStyleSheet("""
            border-right: 1px solid gray;
        """)
        talib_btn = QPushButton(self.menu)
        talib_btn.setText("Ta-Lib")
        talib_btn.setObjectName("pushButton")
        talib_btn.setGeometry(QRect(10, 10, 100, 32))
        talib_btn.setIconSize(QSize(0, 0))
        talib_btn.setCheckable(False)
        talib_btn.setAutoDefault(False)

        self.content_box.addWidget(self.menu)

        self.contents.setObjectName("Contents")
        self.contents.setLayout(self.contents_vbox)

        self.contents_vbox.setSpacing(0)
        self.contents_vbox.setObjectName("verticalLayout")
        self.contents_vbox.setContentsMargins(0, 0, 0, 0)

        self.content_box.addWidget(self.contents)

        self.main_vbox.addLayout(self.content_box)

        talib_btn.clicked.connect(self.slt_list_widget)

    def slt_list_widget(self, checked):

        if not hasattr(self, 'treeWidget'):
            self.treeWidget = QTreeWidget(self.contents)

            self.treeWidget.setSizePolicy(QSizePolicy.Preferred,
                                          QSizePolicy.Preferred)
            self.treeWidget.setAutoExpandDelay(0)
            self.treeWidget.setIndentation(15)
            self.treeWidget.setRootIsDecorated(False)
            self.treeWidget.setItemsExpandable(True)
            self.treeWidget.setAllColumnsShowFocus(True)
            self.treeWidget.setExpandsOnDoubleClick(False)
            self.treeWidget.header().setVisible(False)

            self.contents_vbox.addWidget(self.treeWidget)

            # add items
            talib_funcs = talib.get_function_groups()
            for key, values in talib_funcs.items():

                tree_title_item = QTreeWidgetItem()
                tree_title_item.setText(0, key)
                tree_title_item.setFlags(tree_title_item.flags() & ~Qt.ItemIsSelectable)

                for k, v in enumerate(values):
                    tree_item = QTreeWidgetItem()
                    tree_item.setText(0, v)
                    tree_title_item.addChild(tree_item)

                self.treeWidget.addTopLevelItem(tree_title_item)

            self.treeWidget.expandAll()
            self.treeWidget.itemDoubleClicked.connect(self.slt_add_chart)

    def slt_add_chart(self, item: QTreeWidgetItem):
        if item.parent():
            self.sig_open_indicator.emit(item.text(0))
            self.close()
