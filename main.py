from PySide6.QtWidgets import QApplication, QMainWindow
from mainWin_ui import Ui_MainWindow
from ui_flow_control import FlowControl
from my_logger import *
import sys

VERSION = "v0.4.000"
tag = "2024/12/23 10:00"


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.verion = VERSION
        self.logger = MyLogger(level='debug')
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle(f"Sensor Data Visualize {self.verion} {tag}")

        self.uiCtl = FlowControl(root=self, ui=self.ui, logger=self.logger)


if __name__ == "__main__":
    app = QApplication([])
    window = MyApp()
    # window.showMaximized()
    window.show()
    # app.exec()
    sys.exit(app.exec())