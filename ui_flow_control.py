import re

from mainWin_ui import Ui_MainWindow
import os
from ui_utility import *
from data_visualization_utility import *
from plot_summary_data import *
from data_parser_utility import *
import time
from threading import Thread


project_name = {
            "01":   "malibu",
            "02":   "ceres",
            "03":   "bali",
            "04":   "tycho",
            "05":   "gen2"
        }
sensor_name = {
    "malibu": ["alt", "bti", "emg", "imu", "mag", "ppg", "others"],
    "bali": ["alt", "emg", "imu", "mag", "ppg", "others"],
    "tycho": ["emg", "others"],
    "ceres": ["emg", "others"],
    "gen2": ["emg", "others"]
}

# data rate and data drops default settings
# [<data rate>, <drop start>, <drop end>]
defaultSettings = {"alt": {"rate": 10, "drop start": 0, "drop end": -1, "gain": 1},
                   "bti": {"rate": 31.25, "drop start": 10, "drop end": 72, "gain": 1},
                   "emg": {"rate": 8192, "drop start": 0, "drop end": 0, "gain": 1, "convert_type": 0},
                   "imu": {"rate": 128, "drop start": 25, "drop end": 0, "gain": 1},
                   "mag": {"rate": 64, "drop start": 0, "drop end": 0, "gain": 1},
                   "ppg": {"rate": 32, "drop start": 160, "drop end": 0, "gain": 1},
                   "others": {"rate": 1, "drop start": 0, "drop end": 0, "gain": 1},
                   }

bali_defaultSettings = {"alt": {"rate": 10, "drop start": 0, "drop end": 0, "gain": 1},
                        "bti": {"rate": 31.25, "drop start": 10, "drop end": 72, "gain": 1},
                        "emg": {"rate": 2048, "drop start": 200, "drop end": 0, "gain": 1, "convert_type": 1},
                        "imu": {"rate": 30, "drop start": 20, "drop end": 0, "gain": 1},
                        "mag": {"rate": 50, "drop start": 25, "drop end": 25, "gain": 1},
                        "ppg": {"rate": 32, "drop start": 160, "drop end": 0, "gain": 1},
                        "others": {"rate": 1, "drop start": 0, "drop end": 0, "gain": 1},
                        }

ceres_defaultSettings = {"alt": {"rate": 10, "drop start": 0, "drop end": 0, "gain": 1},
                         "bti": {"rate": 31.25, "drop start": 10, "drop end": 72, "gain": 1},
                         "emg": {"rate": 8192, "drop start": 0, "drop end": 0, "gain": 1, "convert_type": 0},
                         "imu": {"rate": 120, "drop start": 10, "drop end": 10, "gain": 1},
                         "mag": {"rate": 50, "drop start": 0, "drop end": 0, "gain": 1},
                         "ppg": {"rate": 25, "drop start": 125, "drop end": 0, "gain": 1},
                         "others": {"rate": 1, "drop start": 0, "drop end": 0, "gain": 1},
                         }

gen2_defaultSettings = {"alt": {"rate": 10, "drop start": 0, "drop end": 0, "gain": 1},
                        "bti": {"rate": 31.25, "drop start": 10, "drop end": 72, "gain": 1},
                        "emg": {"rate": 2048, "drop start": 500, "drop end": 0, "gain": 1, "convert_type": 1},
                        "imu": {"rate": 128, "drop start": 25, "drop end": 0, "gain": 1},
                        "mag": {"rate": 64, "drop start": 0, "drop end": 0, "gain": 1},
                        "ppg": {"rate": 32, "drop start": 160, "drop end": 0, "gain": 1},
                        "others": {"rate": 1, "drop start": 0, "drop end": 0, "gain": 1},
                        }

project_defaultSettings = {
    "malibu":   defaultSettings,
    "ceres":    ceres_defaultSettings,
    "bali":     bali_defaultSettings,
    "tycho":    bali_defaultSettings,
    "gen2":     gen2_defaultSettings,
}


class FlowControl:
    def __init__(self, root, ui: Ui_MainWindow, **kwargs):
        self.ui = ui
        self.root = root
        self.logger = kwargs['logger'] if 'logger' in kwargs else logging.getLogger()

        self.messagebox = MessageBox(self.root, self.logger)
        self.signal = ProcessSignal()
        self.fileSelector = FileSelector(pathObj=self.ui.fileEntry, browserObj=self.ui.browserBtn,
                                         root=self.root, logger=self.logger)
        self.fileSelector.add_finish_edit_func(self.on_finish_path_edit)
        self.paramKeeper = ParameterKeeper(root=self.root, chkb_obj=self.ui.keepParamCkb,
                                           btn_obj=self.ui.refreshDataBtn, logger=self.logger,
                                           func=self.on_fresh_data_button_clicked)
        self.paramKeeper.state_configure(0)
        # self.plotName = LabelEntry(labObj=self.ui.plotNameLab, entryObj=self.ui.plotNameEntry,
        #                            root=self.root, logger=self.logger)
        # self.plotName.state_configure(0)
        self.paramEntry = ParameterEntry(root=self.root, logger=self.logger,
                                         _combo={"project": self.ui.projectComb,"sensor_type": self.ui.sensorTypeComb,
                                                 "data_type": self.ui.dataTypeComb,
                                                 "convert_type": self.ui.convertTypeComb},
                                         _entry={"data_rate": self.ui.dataRateEntry,
                                                 "data_drop_start": self.ui.dataDropStartEntry,
                                                 "data_drop_end": self.ui.dataDropEndEntry,
                                                 "gain": self.ui.gainEntry,
                                                 "plot_name": self.ui.plotNameEntry})
        self.paramEntry.add_items({"project": project_name.keys()})
        self.paramEntry.state_configure(_comb={"project": 0, "sensor_type": 0, "data_type": 0, "convert_type": 0},
                                        _entry={"data_rate": 0, "data_drop_start": 0, "data_drop_end": 0,
                                                "gain": 0, "plot_name": 0})
        self.ui.projectComb.currentIndexChanged.connect(self.on_project_type_changed)
        self.sensor_change_signal = self.ui.sensorTypeComb.currentIndexChanged.connect(self.on_sensor_type_changed)
        self.ui.dataTypeComb.currentIndexChanged.connect(self.on_data_type_changed)

        self.manualSearchPeak = FilterEntry(checkbox_obj=self.ui.mspChkb, edit_objs={"freq": self.ui.mspFreqEntry},
                                            label_objs=[self.ui.mspFreqLab])
        self.manualSearchPeak.state_configure(0)
        self.highPassFilter = FilterEntry(checkbox_obj=self.ui.hpfChkb, combobox_objs={"type": self.ui.hpfTypeComb},
                                          edit_objs={"order": self.ui.hpfOrdEntry, "freq": self.ui.hpfFreqEntry},
                                          label_objs=[self.ui.hpfTypeLab, self.ui.hpfOrdLab, self.ui.hpfFreqLab],
                                          root=self.root, logger=self.logger)
        self.highPassFilter.state_configure(0)

        self.lowPassFilter = FilterEntry(checkbox_obj=self.ui.lpfChkb, combobox_objs={"type": self.ui.lpfTypeComb},
                                         edit_objs={"order": self.ui.lpfOrdEntry, "freq": self.ui.lpfFreqEntry},
                                         label_objs=[self.ui.lpfTypeLab, self.ui.lpfOrdLab, self.ui.lpfFreqLab],
                                         root=self.root, logger=self.logger)
        self.lowPassFilter.state_configure(0)

        self.notchFilter1 = FilterEntry(checkbox_obj=self.ui.nf1Chkb,
                                        edit_objs={"freq": self.ui.nf1FreqEntry, "qvalue": self.ui.nf1QEntry},
                                        label_objs=[self.ui.nf1FreqLab, self.ui.nf1QLab],
                                        root=self.root, logger=self.logger)
        self.notchFilter1.state_configure(0)
        self.notchFilter2 = FilterEntry(checkbox_obj=self.ui.nf2Chkb,
                                        edit_objs={"freq": self.ui.nf2FreqEntry, "qvalue": self.ui.nf2QEntry},
                                        label_objs=[self.ui.nf2FreqLab, self.ui.nf2QLab],
                                        root=self.root, logger=self.logger)
        self.notchFilter2.state_configure(0)
        self.notchFilter3 = FilterEntry(checkbox_obj=self.ui.nf3Chkb,
                                        edit_objs={"freq": self.ui.nf3FreqEntry, "qvalue": self.ui.nf3QEntry},
                                        label_objs=[self.ui.nf3FreqLab, self.ui.nf3QLab],
                                        root=self.root, logger=self.logger)
        self.notchFilter3.state_configure(0)

        self.fftXScale = FilterEntry(checkbox_obj=self.ui.fftScaleXChkb,
                                     edit_objs={"start": self.ui.fftScaleXStartEntry, "end": self.ui.fftScaleXEndEntry},
                                     label_objs=[self.ui.fftScaleXStartLab, self.ui.fftScaleXEndLab],
                                     root=self.root, logger=self.logger)
        self.fftXScale.state_configure(0)

        self.fftYScale = FilterEntry(checkbox_obj=self.ui.fftScaleYChkb,
                                     edit_objs={"start": self.ui.fftScaleYStartEntry, "end": self.ui.fftScaleYEndEntry},
                                     label_objs=[self.ui.fftScaleYStartLab, self.ui.fftScaleYEndLab],
                                     root=self.root, logger=self.logger)
        self.fftYScale.state_configure(0)

        self.summPlotScale = FilterEntry(checkbox_obj=self.ui.summPlotLimitChkb,
                                     edit_objs={"lower": self.ui.summPlotLimitLowerEntry,
                                                "upper": self.ui.summPlotLimitUpperEntry},
                                     label_objs=[self.ui.summPlotLimitLowerLab, self.ui.summPlotLimitUpperLab],
                                     root=self.root, logger=self.logger)
        self.summPlotScale.state_configure(0)
        self.textFilter = TextFilter(editObj=self.ui.itemFilterEntry, labelObj=self.ui.itemFilterLabel,
                                     logger=self.logger, root=self.root,
                                     command=self.refresh_data_channels)
        self.textFilter.state_configure(0)
        self.snFilter = TextFilter(editObj=self.ui.snFilterEntry, labelObj=self.ui.snFilterLab,
                                   logger=self.logger, root=self.root,
                                   command=self.refresh_data_channels)
        self.snFilter.state_configure(0)
        self.stationFilter = TextFilter(editObj=self.ui.stationFilterEntry, labelObj=self.ui.stationFilterLab,
                                        logger=self.logger, root=self.root,
                                        command=self.refresh_data_channels)
        self.stationFilter.state_configure(0)
        self.channelsSelector = ChannelSelector(root=self.root, logger=self.logger, containObj=self.ui.channelFrm)
        self.goButton = SingleButton(root=self.root, logger=self.logger, btnObj=self.ui.goBtn, command=self.on_button_go)
        self.plotCanvas = PlotCanvas(logger=self.logger)
        self.root.dropEvent = self._drop_event
        self.root.dragEnterEvent = self._drag_enter_event

        self.status_bar = StatusBar(statusBarObj=self.ui.statusBar, click=self.on_statusbar_clicked)
        self.status_bar.show_message("By APAC HW Engineering Team")

        self.dv_params = VisualizeParameters()
        # self.rdp = RawDataParser(logger=self.logger)
        # self.dv = DataVisualization(logger=self.logger, canvas=self.plotCanvas)
        # self.sdp = SummaryDataParser(root=self.root, logger=self.logger, canvas=self.plotCanvas)
        self.dv = None
        self.rdp = None
        self.file_path = list()
        self.sensor_type = None
        self.data_type = None
        self.df_data = dict()
        self.plot_name = None
        self.data_drops = [0, -1]
        self.data_rate = 1
        self.popup = None
        self.item_filter = None
        self.project = "01"
        self.gain = 1.0

        self.signal.threadStateChanged.connect(self.on_thread_state_changed)

    def _drop_event(self, event):
        self.fileSelector.on_drop_event(event)
        self.on_finish_path_edit()

    def _drag_enter_event(self, event):
        self.logger.debug("on drag enter event")
        event.acceptProposedAction()

    def on_statusbar_clicked(self):
        msgbox = MessageBox(root=self.root, logger=self.logger)
        msgbox.information(title="Contact us",
                           text="wenzhao.li@oculus.com\neric.si@oculus.com\nduleo@meta.com")

    def on_finish_path_edit(self):
        self.logger.debug("finished editing extra process ...")
        self.paramKeeper.state_configure(1)
        # self.plotName.state_configure(1)
        self.paramEntry.state_configure(_entry={"plot_name": 1})
        self.textFilter.state_configure(1)
        _file_path = self.get_file_paths()
        if not len(_file_path):
            self.messagebox.warning("Error", "File is not exist!!")
            return

        if not self.paramKeeper.isChecked:
            self.logger.debug("Keeper is not checked, clear parameters")
            self.file_path = _file_path
            # disable first to avoid on_change event
            self.paramEntry.state_configure(_comb={"project": 0, "sensor_type": 0, "data_type": 0, "convert_type": 0},
                                            _entry={"data_rate": 0, "data_drop_start": 0, "data_drop_end": 0})
            self.paramEntry.clear()
            self.sensor_type = None
            self.data_type = None
            self.df_data = None
            self.dv_params.data_drop = [0, -1]
            self.toggle_parameters_chkb(False)
            self.paramEntry.state_configure(_comb={"project": 1})
            self.refresh_data_channels(False)
        elif _file_path != self.file_path and self.data_type and self.sensor_type:
            self.logger.debug(f"file changed, update df_data, [{self.sensor_type}], [{self.data_type}]")
            # self.file_path = _file_path
            self.read_data()
            self.refresh_data_channels(True)

    def get_file_paths(self) -> list:
        path_list = self.fileSelector.get_file_path()
        _file_path = list()
        result = list()
        if path_list is not None and len(path_list):
            # print(path_list)
            for val in path_list:
                if os.path.isdir(val):
                    files = os.listdir(val)
                    _file_path = [os.path.join(val, file) for file in files if file.lower().endswith('.csv')
                                  or file.lower().endswith('.txt') or file.lower().endswith('.log')]
                else:
                    _file_path.append(val)
            for val in _file_path:
                if not os.path.exists(val):
                    self.logger.error(f"[{val}] is not exist!!")
                else:
                    result.append(val)
            if not len(result):
                self.logger.error(f"Files are not exist!!")
            return sorted(result)
        else:
            self.logger.error(f"Files are not exist!!")
            return sorted(result)

    def toggle_parameters_chkb(self, checked: bool):
        self.manualSearchPeak.set_checked(checked)
        self.highPassFilter.set_checked(checked)
        self.lowPassFilter.set_checked(checked)
        self.notchFilter3.set_checked(checked)
        self.fftXScale.set_checked(checked)
        self.fftYScale.set_checked(checked)

    def set_default_values(self, sensor):
        self.project = self.get_parameter_project()
        if self.project in project_defaultSettings.keys():
            def_settings = project_defaultSettings[self.project]
        else:
            def_settings = defaultSettings
        if not len(sensor) or sensor[:3].lower() not in def_settings:
            _sensor = "others"
        else:
            _sensor = sensor[:3].lower()
        settings = def_settings[_sensor]
        self.paramEntry.set(_entry={"data_rate": settings["rate"],
                                    "data_drop_start": settings["drop start"],
                                    "data_drop_end": settings["drop end"],
                                    "gain": settings["gain"]})
        if "data_type" in settings:
            self.paramEntry.set(_combIndex={"data_type": settings["data_type"]})
        if "convert_type" in settings:
            self.paramEntry.set(_combIndex={"convert_type": settings["convert_type"]})
        # self.highPassFilter.set_checked(False)
        self.toggle_parameters_chkb(False)
        if sensor[:3].lower() == 'ppg':
            self.highPassFilter.set_checked(True)
            self.highPassFilter.set(comb={"type": 1}, edit={"order": 3, "freq": 0.5})

    def on_project_type_changed(self, index):
        self.logger.debug(f"project type, selected index: {index}")
        self.rdp = None
        val = self.get_parameter_project()
        if val is not None:
            self.rdp = RawDataParser(val, logger=self.logger)
            if self.sensor_change_signal is not None:
                self.ui.sensorTypeComb.currentIndexChanged.disconnect(self.sensor_change_signal)
            self.paramEntry.add_items({"sensor_type": [_s.upper() for _s in sensor_name[val]]})
            self.paramEntry.set(_combIndex={"sensor_type": -1})
            self.paramEntry.state_configure(_comb={"sensor_type": 1})
            self.paramEntry.set(_combIndex={"data_type": -1})
            self.paramEntry.state_configure(_comb={"data_type": 0})
            self.sensor_change_signal = self.ui.sensorTypeComb.currentIndexChanged.connect(self.on_sensor_type_changed)

    def on_sensor_type_changed(self, index):
        self.logger.debug(f"sensor type, selected index: {index}")
        val = self.paramEntry.get(_comb='sensor_type')
        # if val is None or not len(val):
        if val is None or len(val) == 0:
            self.logger.error("Invalid sensor type!! do nothing")
            return
        self.logger.debug(f"sensor: {val}")
        self.sensor_type = val
        self.set_default_values(self.sensor_type.strip().lower())
        self.paramEntry.state_configure(_comb={"data_type": 1},
                                        _entry={"data_rate": 1, "data_drop_start": 1, "data_drop_end": 1,
                                                "gain": 1})
        if val.lower() == "emg":
            self.paramEntry.state_configure(_comb={"convert_type": 1})
        else:
            self.paramEntry.state_configure(_comb={"convert_type": 0})
            self.paramEntry.set(_combIndex={"convert_type": -1})
        self.paramEntry.set(_combIndex={"data_type": self.determine_data_type_via_file_name()})
        # try to update channel table
        # self.refresh_data_channels(self.read_data())

    def determine_data_type_via_file_name(self) -> int:
        file_list = self.get_file_paths()
        if len(file_list) != 0:
            postfix = os.path.basename(file_list[0]).split(".")[-1]
            if postfix.lower() in ["txt", "log"]:
                return 0  # raw data
            elif postfix.lower() == "csv":
                return 1  # csv data
        return -1  # not select

    def on_data_type_changed(self, index):
        try:
            self.logger.debug(f"data type, selected index: {index}")
            self.data_type = self.paramEntry.get(_comb='data_type')
            if self.data_type is None or not len(self.data_type.strip()):
                self.logger.error("Invalid data type!! do nothing")
                return
            ret = self.read_data()
            if not ret:
                self.paramEntry.set(_combIndex={'data_type': -1}, )
                self.data_type = None
            self.refresh_data_channels(ret)
        except Exception as e:
            self.paramEntry.set(_combIndex={'data_type': -1}, )

    def read_data(self) -> bool:
        if not self.get_parameters():
            return False
        if self.data_type.lower() == 'raw data':
            ret = self.convert_raw_data_to_csv()
        else:
            ret = self.get_df_data()
        return ret

    #  from raw text to csv
    def convert_raw_data_to_csv(self) -> bool:
        file_list = self.get_file_paths()
        self.df_data = dict()
        self.file_path = list()
        for val in file_list:
            _path = os.path.dirname(val)
            _n = os.path.basename(val)
            _time_now = time.strftime("%Y%m%d_%H%M%S", time.localtime())
            _name = f"{_n}_tool_format_data_{_time_now}.csv"
            save_path = os.path.join(_path, _name)
            _err, df_data = self.rdp.extract_sensor_data(_source_file=val, _sensor=self.sensor_type.lower(),
                                                         _project=self.get_parameter_project(),
                                                         _target_file=save_path)
            if _err != ErrorCode.ERR_NO_ERROR:
                _answer = self.messagebox.query("Error", f"Data invalid, {_err}")
                self.logger.error(f"Error during extract data from {val}, {_err}, {_answer}")
                if _answer:
                    continue
                else:
                    self.df_data = dict()
                    self.file_path = list()
                    return False
            self.df_data.update({_name: df_data})
            self.file_path.append(save_path)
            self.logger.info(f"save raw data to csv file: {_name}")
        if len(self.file_path):
            return True
        else:
            return False

    # from csv to csv
    def convert_test_data(self, _project: str, _sensor: str):
        file_list = self.get_file_paths()
        self.df_data = dict()
        self.file_path = list()
        for val in file_list:
            _path = os.path.dirname(val)
            _n = os.path.basename(val)
            _time_now = time.strftime("%Y%m%d_%H%M%S", time.localtime())
            _name = f"{_n}_tool_format_data_{_time_now}.csv"
            save_path = os.path.join(_path, _name)
            _err, df_data = self.rdp.convert_sensor_data(_source_file=val, _sensor=_sensor,
                                                         _project=_project, _target_file=save_path)
            if _err != ErrorCode.ERR_NO_ERROR:
                _answer = self.messagebox.query("Error", f"Data invalid, {_err}")
                self.logger.error(f"Error during extract data from {val}, {_err}, {_answer}")
                if _answer:
                    continue
                else:
                    return False
            self.df_data.update({_name: df_data})
            self.file_path.append(save_path)
            self.logger.info(f"save data to csv file: {_name}")
        if len(self.file_path):
            return True
        else:
            return False

    def get_df_data(self):
        try:
            if self.get_parameter_project() == 'ceres' and self.data_type.lower() == "tester data":
                ret = self.convert_test_data("ceres", "emg")
            # if self.get_parameter_project() == 'bali' and self.data_type.lower() == "tester data":
            #     ret = self.convert_test_data("bali", "emg")
            else:
                file_path = self.get_file_paths()
                self.file_path = list()
                self.df_data = dict()
                for file in file_path:
                    _name = os.path.basename(file)
                    try:
                        data = pd.read_csv(file, index_col=False)
                    except Exception as e:
                        self.logger.error(f"Error during read csv file: {_name}")
                        self.logger.error(f"{str(e)}\nin {__file__}:{str(e.__traceback__.tb_lineno)}")
                        continue
                    self.file_path.append(file)
                    self.df_data.update({_name: data})
                    self.logger.debug(f"read csv: {_name}")
                ret = True
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            ret = False
        if not ret:
            self.messagebox.warning("Error", "Error during read from csv file!!")
        return ret

    def on_fresh_data_button_clicked(self):
        self.logger.debug("refresh data button clicked")
        if not self.get_parameters():
            self.logger.error("some parameters are not selected!!")
            self.messagebox.warning("Error", "Some parameters are not selected!!")
            self.refresh_data_channels(False)
            return
        self.refresh_data_channels(self.read_data())
        pass

    def get_parameter_project(self):
        p = self.paramEntry.get(_comb='project')
        self.logger.debug(f"project selected: {p}")
        return project_name[p] if p in project_name else None

    def get_filer_parameters_list(self, filter_obj: FilterEntry, keys: list = None):
        # keys: specify the keys whose value need to be converted
        val = filter_obj.get() if filter_obj.isChecked else None
        if val is not None:
            _keys = keys if keys is not None and set(keys).issubset(set(val.keys())) else val.keys()
            for key in _keys:
                val[key] = float(val[key])
        else:
            val = list()
        self.logger.debug(f"{filter_obj.name} get values: {val}")
        return [val[k] for k in val]

    def get_filer_parameters_dict(self, filter_obj: FilterEntry, keys: list = None):
        # keys: specify the keys whose value need to be converted
        val = filter_obj.get() if filter_obj.isChecked else None
        if val is not None:
            _keys = keys if keys is not None and set(keys).issubset(set(val.keys())) else val.keys()
            for key in _keys:
                val[key] = float(val[key])
        self.logger.debug(f"{filter_obj.name} get values: {val}")
        return val

    def on_button_go(self):
        # _file = self.fileSelector.get_file_path()
        _file = self.get_file_paths()
        if _file is None or not len(_file):
            self.logger.error(f"No files exist!!")
            self.messagebox.warning("Error", "File is not exist!!")
            return
        self.data_type = self.paramEntry.get(_comb='data_type')
        if self.data_type is None or not len(self.data_type):
            self.logger.error("Invalid data type!! do nothing")
            self.messagebox.warning("Error", "Invalid data type!!")
            return
        self.sensor_type = self.paramEntry.get(_comb='sensor_type')
        if (self.sensor_type is None or not len(self.sensor_type)) and self.data_type.lower() != "summary data":
            self.logger.error("Invalid sensor type!! do nothing")
            self.messagebox.warning("Error", "Invalid sensor type!!")
            return
        # if self.file_path != _file and self.data_type is not None and self.data_type.lower() == 'raw data':
        #     if not self.convert_raw_data_to_csv():
        #         return
        if self.df_data is None:
            self.logger.error("df_data is None!! do nothing")
            self.messagebox.warning("Error", "Data is NULL!!\nPlease press 'Refresh' button first")
            return

        self.get_data_visualize_parameters()
        self.dv = DataVisualize(params=self.dv_params, logger=self.logger, canvas=self.plotCanvas)

        if self.dv_params.selected_columns is not None and len(self.dv_params.selected_columns):
            if len(self.df_data.keys()) > 1:  # for multiple files
                self.popup = Popup(msg="Generating plot pictures ...", parent=self.root)
                _thread = Thread(
                    target=self.visualize_process,
                    args=(self.dv_params.selected_columns, ),
                    daemon=True
                )
                _thread.start()
            else:
                err_code, fig = self.do_visualize()
                if err_code != ErrorCode.ERR_NO_ERROR:
                    self.logger.error(f"Error during plot!! {err_code}")
                    self.messagebox.warning("Error", ErrorMsg[f"{err_code}"])
                else:
                    # self.plotCanvas.create_canvas(fig)
                    self.plotCanvas.show_plot()
        else:
            self.messagebox.information("info", "Select at least one channel!!")

    def do_visualize(self, show=True):
        try:
            _err_code = self.dv.visualize_data(self.dv_params)
            fig = self.dv.fig
            return _err_code, fig
        except Exception as e:
            self.logger.error(f"{str(e)}\nin {__file__}:{str(e.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_UNKNOWN, None

    def visualize_process(self, file_list: list):
        self.signal.threadStateChanged.emit([0, 0])
        for file in file_list:
            self.dv_params.df_data = self.df_data[file]
            self.dv_params.selected_columns = []
            self.dv_params.plot_name = file
            _err_code, _ = self.do_visualize(False)
            if _err_code != ErrorCode.ERR_NO_ERROR:
                # self.messagebox.warning("Error", ErrorMsg[f"{_err_code}"])
                self.signal.threadStateChanged.emit([-2, _err_code])
        self.signal.threadStateChanged.emit([1, 0])

    def on_thread_state_changed(self, data: list):
        self.logger.debug(f"thread state changed: {data}")
        state, err_code = data
        if state == 0:
            self.goButton.state_configure(0)
        elif state == -2:
            self.logger.error(f"Error during plot!! {err_code}")
            self.messagebox.warning("Error", ErrorMsg[f"{err_code}"])
        elif state == 1:
            if self.popup is not None:
                self.popup.close()
            self.goButton.state_configure(1)

    def refresh_data_channels(self, show: bool = True):
        if not show:
            self.channelsSelector.show_channels()
            return
        if self.df_data is None or len(self.df_data) == 0:
            self.messagebox.warning("Error", "No data available!!")
            return
        self.logger.debug(f"refresh: [{self.sensor_type}], [{self.data_type}]")
        self.item_filter = self.textFilter.get_text()
        keys = [val for val in self.df_data.keys()]
        if len(keys) == 1:
            columns = self.df_data[keys[0]].columns.dropna().tolist()
        else:
            columns = keys
        if self.item_filter is not None and len(self.item_filter.strip()):
            self.logger.debug(f"reg:{self.item_filter.strip()}")
            try:
                new_col = [val for val in columns if re.search(fr'{self.item_filter.strip()}', val)]
            except Exception as ex:
                self.messagebox.warning("Error", f"{ex}")
                return
            columns = new_col if len(new_col) else columns
        self.channelsSelector.show_channels(columns, self.data_type)

    def get_parameters(self) -> bool:
        self.project = self.get_parameter_project()
        self.sensor_type = self.paramEntry.get(_comb="sensor_type")
        self.data_type = self.paramEntry.get(_comb="data_type")
        if (self.project is not None
                and self.sensor_type is not None and len(self.sensor_type) != 0
                and self.data_type is not None and len(self.data_type) != 0):
            return True
        else:
            return False

    def get_data_visualize_parameters(self):
        self.dv_params.data_type = self.paramEntry.get(_comb='data_type')
        self.dv_params.sensor = self.paramEntry.get(_comb='sensor_type')
        self.dv_params.df_data = next(iter(self.df_data.values()))  # value of first key
        val = self.paramEntry.get(_entry='data_rate')
        self.dv_params.sample_rate = float(val) if val is not None and len(val) else 1
        self.logger.debug(f"data rate: {self.dv_params.sample_rate}")

        val = self.paramEntry.get(_entry='data_drop_start')
        self.dv_params.data_drop[0] = int(val) if val is not None and len(val) else 0

        val = self.paramEntry.get(_entry='data_drop_end')
        self.dv_params.data_drop[1] = int(val) if val is not None and len(val) else -1
        self.logger.debug(f"data drops: {self.dv_params.data_drop}")

        val = self.paramEntry.get(_entry='gain')
        self.dv_params.gain = float(val) if val is not None and len(val) else 1
        val = self.paramEntry.get(_comb='convert_type')
        self.dv_params.freq_convert_type = val.lower() if val is not None else "fft"
        self.logger.debug(f"freq_convert_type: {self.dv_params.freq_convert_type}")
        # self.dv_params.plot_name = self.plotName.get()
        self.dv_params.plot_name = self.paramEntry.get(_entry='plot_name')
        self.logger.debug(f"plot name: {self.dv_params.plot_name}")
        val = self.get_filer_parameters_dict(self.manualSearchPeak)
        self.dv_params.search_peak = float(val["freq"]) if val is not None else 0

        self.dv_params.high_pass_filter = self.get_filer_parameters_dict(self.highPassFilter, ['order', 'freq'])
        self.dv_params.low_pass_filter = self.get_filer_parameters_dict(self.lowPassFilter, ['order', 'freq'])
        self.dv_params.notch_filter["0"] = self.get_filer_parameters_dict(self.notchFilter1)
        self.dv_params.notch_filter["1"] = self.get_filer_parameters_dict(self.notchFilter2)
        self.dv_params.notch_filter["2"] = self.get_filer_parameters_dict(self.notchFilter3)

        self.dv_params.freq_scale["x"] = self.get_filer_parameters_dict(self.fftXScale)
        self.dv_params.freq_scale["y"] = self.get_filer_parameters_dict(self.fftYScale)

        # filters = dict()
        # filters.update({"summYScale": self.get_filer_parameters_list(self.summPlotScale)})
        self.dv_params.summary_scale = self.get_filer_parameters_list(self.summPlotScale)

        self.dv_params.selected_columns = self.channelsSelector.get_checked_list()
        self.logger.debug(f"selected channels: {self.dv_params.selected_columns}")
        self.dv_params.project = self.get_parameter_project()

