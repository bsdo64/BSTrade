import pandas as pd
from PyQt5.QtCore import pyqtSignal

from BSTrade.util.thread import Thread
from BSTrade.data.model import Model


class Manager:
    sig_file_opened = pyqtSignal(object)

    def __init__(self, parent=None):
        self.open_file_finished = False

    def open_file(self):
        th = Thread()
        w = th.make_worker(self.th_open_file,
                           'BSTrade/data/bitmex_1m_2018.pkl')
        w.sig.finished.connect(self.slt_set_scene)
        th.start(w)

    def th_open_file(self, filename):
        self.df = pd.read_pickle(filename)

    def slt_set_scene(self):
        self.chart_model = Model(self.df)
