from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool


class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        `tuple` (exctype, value, traceback.format_exc() )

    result
        `object` data returned from processing, anything

    progress
        `int` indicating % progress

    """
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        QRunnable.__init__(self)

        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.sig = WorkerSignals()

    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)

            self.sig.result.emit(result)
        finally:
            self.sig.finished.emit()


class Thread:
    def __init__(self):
        self.threadpool = QThreadPool()

    def make_worker(self, fn, *args, **kwargs) -> Worker:
        return Worker(fn, *args, **kwargs)

    def connect_sig(self, worker: Worker, signal, fn):
        worker.sig[signal].connect(fn)

    def start(self, worker):
        self.threadpool.start(worker)
