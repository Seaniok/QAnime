from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal


class WorkerSignals(QObject):
    finished = Signal(object)
    error = Signal(str)


class Worker(QRunnable):
    """Run fn(*args) on the global thread pool; report via signals."""

    def __init__(self, fn, *args):
        super().__init__()
        self.fn = fn
        self.args = args
        self.signals = WorkerSignals()

    def run(self):
        try:
            result = self.fn(*self.args)
        except Exception as e:  # noqa: BLE001
            self.signals.error.emit(str(e))
            return
        self.signals.finished.emit(result)


def run_async(fn, *args, on_done=None, on_error=None):
    w = Worker(fn, *args)
    if on_done:
        w.signals.finished.connect(on_done)
    if on_error:
        w.signals.error.connect(on_error)
    QThreadPool.globalInstance().start(w)
    return w
