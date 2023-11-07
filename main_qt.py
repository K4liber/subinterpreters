from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QProgressBar, QMainWindow, QApplication, QPushButton, QVBoxLayout

from functools import partial


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")
        self._layout = QVBoxLayout()
        self._start_button = QPushButton('Start job')
        self._start_button.clicked.connect(self._start_job)
        self._layout.addWidget(self._start_button)
        self._progress_bars = []
        self._create_progress_bar()

        for progres_bar in self._progress_bars:
            self._layout.addWidget(progres_bar)

        self.setLayout(self._layout)
        

    def _start_job(self) -> None:
        pass

    def _advance_progress_bar(self, index: int) -> None:
        progress_bar = self._progress_bars[index]
        current_value = progress_bar.value()
        max_value = progress_bar.maximum()
        progress_bar.setValue(current_value + (max_value - current_value) / 100)

    def _create_progress_bar(self):
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 10000)
        progress_bar.setValue(0)
        index = len(self._progress_bars)
        self._progress_bars.append(progress_bar)
        timer = QTimer(self)
        update_function = partial(self._advance_progress_bar, index)
        timer.timeout.connect(update_function)
        timer.start(200)


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
