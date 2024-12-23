from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QLabel, QMessageBox,
                               QFileDialog, QLineEdit, QPushButton, QCheckBox,
                               QComboBox, QGridLayout, QScrollArea)
from PySide6.QtCore import QEvent, QObject
import logging
import numpy as np
import functools
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import \
    NavigationToolbar2QT as NavigationToolbar


class EventFilter(QObject):
    # QEvent.Type.Drop
    def __init__(self, _object: QObject, _event: QEvent.Type, _func):
        super().__init__()
        self.targetOjb = _object
        self.targetEvent = _event
        self.targetFunc = _func

    def eventFilter(self, obj, event):
        # print(f"on event: {event.type()}, target: {self.targetEvent}")
        if obj == self.targetOjb and event.type() == self.targetEvent:
            if self.targetFunc:
                self.targetFunc(event)
            return True
        return False


class FileSelector:
    def __init__(self, root, pathObj: QLineEdit = None, browserObj: QPushButton = None, **kwargs):
        self.filePathEntry = pathObj
        self.browseBtn = browserObj
        self.logger = kwargs['logger'] if 'logger' in kwargs else logging.getLogger()
        # self.click_func = kwargs['func'] if 'func' in kwargs else None
        self.root = root

        if not self.filePathEntry or not self.browseBtn or not self.root:
            self.logger.error("Invalid arguments!!")
            return

        self.browseBtn.clicked.connect(self.on_button_clicked)
        # self.filePathEntry.dropEvent = self.on_drop_event
        # self.filePathEntry.dragEnterEvent = self.on_dragEnter
        self.filePathEntry.editingFinished.connect(self.on_finish_debug)
        self.filepath = None
        self.extra_finish_func = None

    def on_button_clicked(self):
        self.filepath, _ = QFileDialog.getOpenFileName(self.root, "Select a file", "", "All file (*.*)")
        if self.filepath:
            self.filePathEntry.setText(self.filepath)
            self.logger.info(f"selected file: {self.filepath}")
            if self.extra_finish_func is not None:
                self.extra_finish_func()

    def on_drop_event(self, event):
        self.logger.debug("on drop event")
        mime_data = event.mimeData()
        if mime_data.hasUrls():
            url = mime_data.urls()[0]
            self.filePathEntry.setText(url.toLocalFile())
            self.filepath = url.toLocalFile()
        event.acceptProposedAction()

    def on_finish_debug(self):
        self.logger.debug("finish editing file path")
        self.filePathEntry.clearFocus()
        self.filepath = self.filePathEntry.text()
        if self.extra_finish_func is not None:
            self.extra_finish_func()

    def add_finish_edit_func(self, func):
        self.extra_finish_func = func
        # self.filePathEntry.editingFinished.connect(func)

    def state_configure(self, val):
        self.filePathEntry.setEnabled(val)

    def get_file_path(self):
        return self.filePathEntry.text()


class ParameterKeeper:
    def __init__(self, root, chkb_obj: QCheckBox = None, btn_obj: QPushButton = None, **kwargs):
        self.logger = kwargs['logger'] if 'logger' in kwargs else logging.getLogger()
        self.click_func = kwargs['func'] if 'func' in kwargs else None
        self.root = root
        self.chkb = chkb_obj
        self.btn = btn_obj
        self.isChecked = False

        if not self.chkb or not self.btn:
            self.logger.error("Invalid parameters!!")
            return
        self.btn.setEnabled(False)
        self.chkb.toggled.connect(self.on_check_event)
        if self.click_func:
            self.btn.clicked.connect(self.click_func)

    def on_check_event(self, checked: bool):
        self.logger.debug(f"is checked: {checked}")
        self.isChecked = checked
        self.btn.setEnabled(checked)

    def state_configure(self, val):
        self.chkb.setEnabled(val)
        if val:
            self.btn.setEnabled(self.isChecked)
        else:
            self.btn.setEnabled(val)


class ParameterEntry:
    def __init__(self, root, _combo: dict, _entry: dict, **kwargs):
        self.combDict = _combo
        self.entryDict = _entry
        self.logger = kwargs['logger'] if 'logger' in kwargs else logging.getLogger()
        self.root = root

        if not self.combDict and not self.entryDict:
            self.logger.error("Invalid arguments!!")
            return

    def set(self, _combIndex: dict = None, _entry: dict = None):
        if _entry and self.entryDict:
            for key in _entry:
                if key in self.entryDict:
                    self.entryDict[key].setText(str(_entry[key]))
                else:
                    self.logger.error(f"entry {key} is not found")
        if _combIndex and self.combDict:
            for key in _combIndex:
                if key in self.combDict:
                    self.combDict[key].setCurrentIndex(int(_combIndex[key]))
                else:
                    self.logger.error(f"entry {key} is not found")

    def get(self, _comb=None, _entry=None):
        if _entry and self.entryDict:
            if _entry in self.entryDict:
                return self.entryDict[_entry].text()
            else:
                self.logger.error(f"entry {_entry} is not found")
                return None

        if _comb and self.combDict:
            if _comb in self.combDict:
                return self.combDict[_comb].currentText()
            else:
                self.logger.error(f"combobox {_entry} is not found")
                return None

    def state_configure(self, _comb: dict = None, _entry: dict = None):
        if _entry and self.entryDict:
            for key in _entry:
                if key in self.entryDict:
                    self.entryDict[key].setEnabled(_entry[key])
        if _comb and self.combDict:
            for key in _comb:
                if key in self.combDict:
                    self.combDict[key].setEnabled(_comb[key])

    def clear(self):
        for key in self.combDict:
            self.combDict[key].setCurrentIndex(-1)
        for key in self.entryDict:
            self.entryDict[key].setText("")


class FilterEntry:
    def __init__(self, checkbox_obj: QCheckBox, combobox_objs: dict[str, QComboBox] = None,
                 edit_objs: dict[str, QLineEdit] = None, label_objs: list[QLabel] = None, **kwargs):
        self.logger = kwargs['logger'] if 'logger' in kwargs else logging.getLogger()
        self.root = kwargs['root'] if 'root' in kwargs else None
        self.checkbox_obj = checkbox_obj
        self.comb_dict = combobox_objs if combobox_objs is not None else dict()
        self.edit_dict = edit_objs if edit_objs is not None else dict()
        self.label_list = label_objs if label_objs is not None else list()
        self.isChecked = False
        self.name = self.checkbox_obj.text()

        if self.checkbox_obj is None:
            self.logger.error("checkbox obj is None!!")
            return

        self.checkbox_obj.toggled.connect(self.on_check_event)

    def set_checked(self, checked: bool):
        self.checkbox_obj.setChecked(checked)

    def set_enabled(self, enabled: bool):
        self.checkbox_obj.setEnabled(enabled)

    def set(self, comb: dict[str, int] = None, edit: dict = None):
        if comb is not None:
            for key in comb:
                if key in self.comb_dict:
                    self.comb_dict[key].setCurrentIndex(int(comb[key]))
        if edit is not None:
            for key in edit:
                if key in self.edit_dict:
                    self.edit_dict[key].setText(str(edit[key]))

    def get(self, names: list[str] = None):
        comb = dict()
        edit = dict()
        if names is not None:
            for n in names:
                if n in self.comb_dict:
                    comb[n] = self.comb_dict[n].currentText()
                if n in self.edit_dict:
                    edit[n] = self.edit_dict[n].text()
        else:
            for n in self.comb_dict:
                comb[n] = self.comb_dict[n].currentText()
            for n in self.edit_dict:
                edit[n] = self.edit_dict[n].text()
        self.logger.debug(f"{self.name} get values: {comb}, {edit}")
        return {**comb, **edit}

    def state_configure(self, val):
        for key in self.comb_dict:
            self.comb_dict[key].setEnabled(val)
        for key in self.edit_dict:
            self.edit_dict[key].setEnabled(val)
        for i in range(len(self.label_list)):
            self.label_list[i].setEnabled(val)

    def on_check_event(self, checked: bool):
        self.logger.debug(f"{self.name} is checked: {checked}")
        self.isChecked = checked
        self.state_configure(checked)


class PassFilter:
    def __init__(self, filter_obj: QCheckBox = None, type_obj: QComboBox = None,
                 order_obj: QLineEdit = None, freq_obj: QLineEdit = None, label_objs: list[QLabel] = None,
                 **kwargs):
        self.logger = kwargs['logger'] if 'logger' in kwargs else logging.getLogger()
        self.root = kwargs['root'] if 'root' in kwargs else None
        self.filterCkb = filter_obj
        self.typeComb = type_obj
        self.orderEntry = order_obj
        self.freqEntry = freq_obj
        self.labels = label_objs
        self.isChecked = False

        if not self.filterCkb or not self.typeComb or not self.orderEntry or not self.freqEntry:
            self.logger.error("Invalid parameters!!")
            return

        self.filterCkb.toggled.connect(self.on_check_event)

    def set_checked(self, checked: bool):
        self.filterCkb.setChecked(checked)

    def get_parameters(self):
        return {"type": self.get_type(),
                "order": self.get_order(),
                "freq": self.get_freq()}

    def set_type(self, idx):
        self.typeComb.setCurrentIndex(int(idx))

    def get_type(self):
        val = self.typeComb.currentText()
        return val if val is not None and len(val) else ""

    def set_order(self, value):
        self.orderEntry.setText(str(value))

    def get_order(self):
        val = self.orderEntry.text()
        return float(val) if len(val) else 0

    def set_freq(self, value):
        self.freqEntry.setText(str(value))

    def get_freq(self):
        val = self.freqEntry.text()
        return float(val) if len(val) else 0

    def state_configure(self, val):
        self.typeComb.setEnabled(val)
        self.orderEntry.setEnabled(val)
        self.freqEntry.setEnabled(val)
        if self.labels:
            for lab in self.labels:
                lab.setEnabled(val)

    def on_check_event(self, checked: bool):
        self.logger.debug(f"is checked: {checked}")
        self.isChecked = checked
        self.state_configure(checked)


class NotchFilter:
    def __init__(self, filter_obj: QCheckBox = None, qvalue_obj: QLineEdit = None,
                 freq_obj: QLineEdit = None, label_objs: list[QLabel] = None,
                 **kwargs):
        self.logger = kwargs['logger'] if 'logger' in kwargs else logging.getLogger()
        self.root = kwargs['root'] if 'root' in kwargs else None
        self.filterCkb = filter_obj
        self.qvalueEntry = qvalue_obj
        self.freqEntry = freq_obj
        self.labels = label_objs
        self.isChecked = False

        if not self.filterCkb or not self.qvalueEntry or not self.freqEntry:
            self.logger.error("Invalid parameters!!")
            return
        self.filterCkb.toggled.connect(self.on_check_event)

    def set_checked(self, checked: bool):
        self.filterCkb.setChecked(checked)

    def get_parameters(self):
        return [self.get_freq(), self.get_qvalue()]

    def set_qvalue(self, value):
        self.qvalueEntry.setText(str(value))

    def get_qvalue(self):
        val = self.qvalueEntry.text()
        return float(val) if len(val) else None

    def set_freq(self, value):
        self.freqEntry.setText(str(value))

    def get_freq(self):
        val = self.freqEntry.text()
        return float(val) if len(val) else None

    def state_configure(self, val):
        self.qvalueEntry.setEnabled(val)
        self.freqEntry.setEnabled(val)
        if self.labels:
            for lab in self.labels:
                lab.setEnabled(val)

    def on_check_event(self, checked: bool):
        self.logger.debug(f"is checked: {checked}")
        self.isChecked = checked
        self.state_configure(checked)


class FFTScaler:
    def __init__(self, filter_obj: QCheckBox = None, start_obj: QLineEdit = None,
                 end_obj: QLineEdit = None, label_objs: list[QLabel] = None,
                 **kwargs):
        self.logger = kwargs['logger'] if 'logger' in kwargs else logging.getLogger()
        self.root = kwargs['root'] if 'root' in kwargs else None
        self.filterCkb = filter_obj
        self.startEntry = start_obj
        self.endEntry = end_obj
        self.labels = label_objs
        self.isChecked = False

        if not self.filterCkb or not self.startEntry or not self.endEntry:
            self.logger.error("Invalid parameters!!")
            return
        self.filterCkb.toggled.connect(self.on_check_event)

    def set_checked(self, checked: bool):
        self.filterCkb.setChecked(checked)

    def get_parameters(self):
        return [self.get_start(), self.get_end()]

    def set_start(self, value):
        self.startEntry.setText(str(value))

    def get_start(self):
        val = self.startEntry.text()
        return float(val) if len(val) else None

    def set_end(self, value):
        self.endEntry.setText(str(value))

    def get_end(self):
        val = self.endEntry.text()
        return float(val) if len(val) else None

    def state_configure(self, val):
        self.startEntry.setEnabled(val)
        self.endEntry.setEnabled(val)
        if self.labels:
            for lab in self.labels:
                lab.setEnabled(val)

    def on_check_event(self, checked: bool):
        self.logger.debug(f"is checked: {checked}")
        self.isChecked = checked
        self.state_configure(checked)


class MessageBox:
    def __init__(self, root, logger):
        self.root = root
        self.logger = logger
        # QMessageBox.setStandardIcon(QMessageBox.Icon.NoIcon)

    def warning(self, title, text):
        msgBox = QMessageBox()
        msgBox.warning(self.root, title, text,
                       QMessageBox.StandardButton.NoButton, QMessageBox.StandardButton.NoButton)

    def information(self, title, text):
        msgBox = QMessageBox()
        msgBox.information(self.root, title, text,
                           QMessageBox.StandardButton.NoButton, QMessageBox.StandardButton.NoButton)


class ChannelSelector:
    def __init__(self, containObj = None, **kwargs):
        self.frm = containObj
        self.logger = kwargs['logger'] if 'logger' in kwargs else logging.getLogger()
        self.root = kwargs['root'] if 'root' in kwargs else None
        self.type = None
        self.channel_list = list()
        self.cols = self.rows = 0
        self.check_boxes = dict()
        self.chkb_all = None
        self.selected_list = list()
        self.selected_count = 0

        self.grid_layout = QGridLayout()
        self.frm.setLayout(self.grid_layout)

    def show_channels(self, channels: list[str] = None, data_type: str = None):
        # delete old data:
        if self.chkb_all is not None:
            self.chkb_all.deleteLater()
            self.chkb_all = None
        if len(self.check_boxes):
            for ch in self.check_boxes:
                self.check_boxes[ch].deleteLater()
        self.check_boxes = dict()
        self.selected_count = 0
        self.type = data_type
        self.channel_list = channels
        if self.channel_list is None or not len(self.channel_list):
            self.logger.error("channels list is empty!!")
            return
        if self.type.lower() == "summary data":
            self.cols = 4
        else:
            self.cols = 3
        self.rows = np.ceil(len(self.channel_list) / 4) + 1

        # delete old data:
        if self.chkb_all is not None:
            self.chkb_all.deleteLater()
            self.chkb_all = None
        if len(self.check_boxes):
            for ch in self.check_boxes:
                self.check_boxes[ch].deleteLater()
        self.check_boxes = dict()
        row = 1
        col = 0
        self.chkb_all = QCheckBox("All")
        self.chkb_all.clicked.connect(self.on_all_clicked)
        self.grid_layout.addWidget(self.chkb_all, 0, 0)
        for ch in self.channel_list:
            self.check_boxes[ch] = QCheckBox(ch)
            self.check_boxes[ch].stateChanged.connect(functools.partial(self.on_check_box_state_changed, self.check_boxes[ch]))
            self.grid_layout.addWidget(self.check_boxes[ch], row, col)
            row = row + 1 if col == self.cols - 1 else row
            col = 0 if col == self.cols - 1 else col + 1

    def on_all_clicked(self, clicked):
        for ch in self.check_boxes:
            self.check_boxes[ch].setChecked(clicked)

    def on_check_box_state_changed(self, ckb, state):
        if state == 2:
            self.logger.info(f"selected [{ckb.text()}]")
            self.selected_count += 1
            if self.selected_count == len(self.channel_list):
                self.chkb_all.setChecked(True)
        else:
            self.logger.info(f"unselected [{ckb.text()}]")
            self.selected_count -= 1
            self.chkb_all.setChecked(False)

    def get_checked_list(self):
        if self.chkb_all is None:
            self.logger.debug(f"No check box available")
            return
        if self.chkb_all.isChecked():
            return self.channel_list
        else:
            _channel_list = list()
            for ch in self.check_boxes:
                if self.check_boxes[ch].isChecked():
                    _channel_list.append(ch)
            return _channel_list


class SingleButton:
    def __init__(self, btnObj: QPushButton = None, command = None, **kwargs):
        self.root = kwargs['root'] if 'root' in kwargs else None
        self.logger = kwargs['logger'] if 'logger' in kwargs else logging.getLogger()

        self.btnObj = btnObj
        self.click_command = command
        self.btnObj.clicked.connect(self.on_button_clicked)

    def state_configure(self, val):
        self.btnObj.setEnabled(val)

    def on_button_clicked(self):
        self.logger.debug("button clicked")
        if self.click_command is not None:
            self.click_command()


class LabelEntry:
    def __init__(self, labObj: QLabel = None, entryObj: QLineEdit = None, **kwargs):
        self.root = kwargs['root'] if 'root' in kwargs else None
        self.logger = kwargs['logger'] if 'logger' in kwargs else logging.getLogger()
        self.labObj = labObj
        self.entryObj = entryObj

        if self.labObj is None or self.entryObj is None:
            self.logger.error(f"Parameter invalid!!")

    def set(self, value):
        self.entryObj.setText(str(value))

    def get(self):
        return self.entryObj.text()

    def state_configure(self, val):
        self.entryObj.setEnabled(val)
        self.labObj.setEnabled(val)


class PlotCanvas:
    def __init__(self, **kwargs):
        self.root = kwargs['root'] if 'root' in kwargs else None
        self.logger = kwargs['logger'] if 'logger' in kwargs else None
        self.canvas_window = QMainWindow()
        self.canvas_window.setContentsMargins(1, 1, 1, 1)
        self.fig = None
        self.canvas = None
        self.navBar = None

    def create_canvas(self, fig):
        self.fig = fig
        self.canvas = FigureCanvas(fig)

    def show_plot(self):
        # width, height = fig.get_size_inches() * fig.dpi
        # self.canvas.setFixedSize(int(width), int(height))
        self.canvas_window.setWindowTitle(f"{self.fig.get_suptitle()}")
        self.navBar = NavigationToolbar(self.canvas, self.canvas_window)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.navBar)
        layout.addWidget(self.canvas)

        widget = QWidget()
        widget.setLayout(layout)

        scroll_area = QScrollArea()
        scroll_area.setWidget(widget)
        scroll_area.setWidgetResizable(True)

        self.canvas_window.setCentralWidget(scroll_area)

        # self.canvas_window.show()
        self.canvas_window.showMaximized()
        # self.canvas_window.resizeEvent = self.resize_canvas

    def resize_canvas(self, event):
        width = event.size().width()
        height = event.size().height()
        fig_width, fig_height = self.fig.get_size_inches() * self.fig.dpi
        scale = min(width / fig_width, height / fig_height)
        self.canvas.setFixedSize(int(fig_width * scale), int(fig_height * scale))
        super().resizeEvent(event)