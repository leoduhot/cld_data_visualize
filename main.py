from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QIcon
from mainWin_ui import Ui_MainWindow
from ui_flow_control import FlowControl
from my_logger import *
import sys
import os

VERSION = "v0.4.000"
tag = "2024/12/23 10:00"


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.verion = VERSION
        self.logger = MyLogger(level='info')
        self.resource = self.resource_path("resource")
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle(f"Sensor Data Visualize {self.verion} {tag}")

        self.uiCtl = FlowControl(root=self, ui=self.ui, logger=self.logger)

    def resource_path(self, _path):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        self.logger.debug(f"base path: {base_path}")
        return os.path.join(base_path, _path)


if __name__ == "__main__":
    app = QApplication([])
    app.setStyle("Fusion")

    window = MyApp()
    icon = QIcon(os.path.join(window.resource, "icon.ico"))
    app.setWindowIcon(icon)
    # app.setStyleSheet("background-color: #ffe4e1;")
    # palette = QPalette()
    # palette.setColor(QPalette.ColorRole.AlternateBase, QColor(255, 0, 0))
    # window.setPalette(palette)

    # window.showMaximized()
    window.show()
    # app.exec()
    sys.exit(app.exec())