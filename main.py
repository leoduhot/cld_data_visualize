from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QIcon
from mainWin_ui import Ui_MainWindow
from ui_flow_control import FlowControl
from my_logger import *
import sys
import os

VERSION = "v0.5.322"
tag = "2025/11/07 12:00"


class MyApp(QMainWindow):
    def __init__(self, **kwargs):
        super().__init__()
        self.verion = VERSION
        self.logger = kwargs['logger'] if 'logger' in kwargs else logging.getLogger()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle(f"Sensor Data Visualize {self.verion} {tag}")

        self.uiCtl = FlowControl(root=self, ui=self.ui, logger=self.logger)


if __name__ == "__main__":
    app = QApplication([])
    app.setStyle("Fusion")
    _level = 'info' if VERSION[-1] == '0' else 'debug'
    logger = MyLogger(level=_level, save=True)
    window = MyApp(logger=logger)
    icon = QIcon(os.path.join(logger.resource_path, "icon.ico"))
    app.setWindowIcon(icon)
    window.show()
    # app.exec()
    sys.exit(app.exec())
