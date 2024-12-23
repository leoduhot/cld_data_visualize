from mainWin_ui import Ui_MainWindow
import os
from ui_utility import *
from data_visualization_utility import DataVisualization
from plot_summary_data import *
from data_parser import *
import time


# data rate and data drops default settings
defaultSettings = {"alt": [10, 0, -1],
                   "bti": [31.25, 10, 72],
                   "emg": [8192, 0, -1],
                   "imu": [120, 10, 490],
                   "mag": [50, 0, -1],
                   "ppg": [25, 125, 500],
                   }


class FlowControl:
    def __init__(self, root, ui: Ui_MainWindow, **kwargs):
        self.ui = ui
        self.root = root
        self.logger = kwargs['logger'] if 'logger' in kwargs else logging.getLogger()

        self.messagebox = MessageBox(self.root, self.logger)
        self.fileSelector = FileSelector(pathObj=self.ui.fileEntry, browserObj=self.ui.browserBtn,
                                         root=self.root, logger=self.logger)
        self.fileSelector.add_finish_edit_func(self.on_finish_path_edit)
        self.paramKeeper = ParameterKeeper(root=self.root, chkb_obj=self.ui.keepParamCkb,
                                           btn_obj=self.ui.refreshDataBtn, logger=self.logger,
                                           func=self.on_fresh_data_button_clicked)
        self.paramKeeper.state_configure(0)
        self.plotName = LabelEntry(labObj=self.ui.plotNameLab, entryObj=self.ui.plotNameEntry,
                                   root=self.root, logger=self.logger)
        self.plotName.state_configure(0)
        self.paramEntry = ParameterEntry(root=self.root, logger=self.logger,
                                         _combo={"sensor_type": self.ui.sensorTypeComb,
                                                 "data_type": self.ui.dataTypeComb},
                                         _entry={"data_rate": self.ui.dataRateEntry,
                                                 "data_drop_start": self.ui.dataDropStartEntry,
                                                 "data_drop_end": self.ui.dataDropEndEntry})
        self.paramEntry.state_configure(_comb={"sensor_type": 0, "data_type": 0},
                                        _entry={"data_rate": 0, "data_drop_start": 0, "data_drop_end": 0})
        self.ui.sensorTypeComb.currentIndexChanged.connect(self.on_sensor_type_changed)
        self.ui.dataTypeComb.currentIndexChanged.connect(self.on_data_type_changed)

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

        self.channelsSelector = ChannelSelector(root=self.root, logger=self.logger, containObj=self.ui.channelFrm)
        self.goButton = SingleButton(root=self.root, logger=self.logger, btnObj=self.ui.goBtn, command=self.on_button_go)
        self.plotCanvas = PlotCanvas(logger=self.logger)
        self.root.dropEvent = self._drop_event
        self.root.dragEnterEvent = self._drag_enter_event

        self.rdp = RawDataParser(logger=self.logger)
        self.dv = DataVisualization(logger=self.logger, canvas=self.plotCanvas)
        self.sdp = SummaryDataParser(root=self.root, logger=self.logger, canvas=self.plotCanvas)
        self.file_path = None
        self.sensor_type = None
        self.data_type = None
        self.df_data = None
        self.plot_name = None
        self.data_drops = [0, -1]

    def _drop_event(self, event):
        self.fileSelector.on_drop_event(event)
        self.on_finish_path_edit()

    def _drag_enter_event(self, event):
        self.logger.debug("on drag enter event")
        event.acceptProposedAction()

    def on_finish_path_edit(self):
        self.logger.debug("finished editing extra process ...")
        self.paramKeeper.state_configure(1)
        self.plotName.state_configure(1)
        val = self.fileSelector.get_file_path()
        if val is not None and not os.path.exists(val):
            self.messagebox.warning("Error", "File is not exist!!")
            return

        if not self.paramKeeper.isChecked:
            self.logger.debug("Keeper is not checked, clear parameters")
            self.file_path = val
            self.paramEntry.clear()
            self.sensor_type = None
            self.data_type = None
            self.df_data = None
            self.data_drops = [0, -1]
            self.toggle_parameters_chkb(False)
            self.paramEntry.state_configure(_comb={"sensor_type": 1, "data_type": 0},
                                            _entry={"data_rate": 0, "data_drop_start": 0, "data_drop_end": 0})
            self.channelsSelector.show_channels()
        elif val != self.file_path and self.data_type and self.sensor_type:
            self.logger.debug(f"file changed, update df_data, [{self.sensor_type}], [{self.data_type}]")
            self.file_path = val
            if self.data_type.lower() == 'raw data':
                self.convert_raw_data_to_csv()
            else:
                self.get_df_data()

    def toggle_parameters_chkb(self, checked: bool):
        self.highPassFilter.set_checked(checked)
        self.lowPassFilter.set_checked(checked)
        self.notchFilter3.set_checked(checked)
        self.fftXScale.set_checked(checked)
        self.fftYScale.set_checked(checked)

    def set_default_values(self, sensor):
        if not len(sensor):
            self.logger.debug(f"sensor type is empty, do nothing!!")
            return
        settings = defaultSettings[sensor[:3].lower()]
        self.paramEntry.set(_entry={"data_rate": settings[0],
                                    "data_drop_start": settings[1],
                                    "data_drop_end": settings[2]})
        self.highPassFilter.set_checked(False)
        if sensor[:3].lower() == 'ppg':
            self.highPassFilter.set_checked(True)
            self.highPassFilter.set(comb={"type": 1}, edit={"order": 3, "freq": 0.5})
            # self.highPassFilter.set_type(1)  # 0 -- blank, 1 -- lfilter, 2 -- filtfilt
            # self.highPassFilter.set_order(3)
            # self.highPassFilter.set_freq(0.5)

    def on_sensor_type_changed(self, index):
        self.logger.debug(f"sensor type, selected index: {index}")
        val = self.paramEntry.get(_comb='sensor_type')
        # if val is None or not len(val):
        if val is None:
            self.logger.error("Invalid sensor type!! do nothing")
            return
        if self.sensor_type != val:
            self.sensor_type = val
            self.set_default_values(self.sensor_type.strip())
            self.paramEntry.state_configure(_comb={"sensor_type": 1, "data_type": 1},
                                            _entry={"data_rate": 1, "data_drop_start": 1, "data_drop_end": 1})
        if self.data_type is not None and self.data_type.lower() == "summary data":
            self.refresh_data_channels()

    def on_data_type_changed(self, index):
        self.logger.debug(f"data type, selected index: {index}")
        self.data_type = self.paramEntry.get(_comb='data_type')
        if self.data_type is None or not len(self.data_type.strip()):
            self.logger.error("Invalid data type!! do nothing")
            return
        ret = False
        if self.data_type.lower() == 'raw data':
            ret = self.convert_raw_data_to_csv()
        else:
            ret = self.get_df_data()

        self.refresh_data_channels(ret)

    def convert_raw_data_to_csv(self) -> bool:
        val = self.fileSelector.get_file_path()
        # if val is not None and val == self.file_path and self.df_data is None:
        #     self.logger.error(f"file is not changed")
        #     return True
        self.file_path = val
        if self.file_path is None or not os.path.exists(self.file_path):
            self.logger.error(f"{self.file_path} is not exist!!")
            self.messagebox.warning("Error", "File is not exist!!")
            return False
        _err, self.df_data = self.rdp.extract_sensor_data(_file=self.file_path, _sensor=self.sensor_type.lower())
        if _err != ErrorCode.ERR_NO_ERROR:
            self.logger.error(f"Error during extract data, {_err}")
            self.messagebox.warning("Error", f"Data invalid, {_err}")
            return False
        _path = os.path.dirname(self.file_path)
        _time_now = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        _name = f"{self.sensor_type.lower()}_data_{_time_now}.csv"
        self.df_data.to_csv(os.path.join(_path, _name), index=False)
        self.logger.info(f"save data to csv file: {_name}")
        return True

    def get_df_data(self):
        try:
            self.df_data = pd.read_csv(self.file_path, index_col=False)
            ret = True
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            ret = False
        if not ret:
            self.messagebox.warning("Error", "Error during read from csv file!!")
        return ret

    def on_fresh_data_button_clicked(self):
        self.logger.debug("refresh data button clicked")
        self.refresh_data_channels()
        pass

    def get_pass_filer_parameters(self, filter_obj: FilterEntry):
        val = filter_obj.get() if filter_obj.isChecked else None
        if val is not None:
            val['order'] = float(val['order'])
            val['freq'] = float(val['freq'])
        self.logger.debug(f"{filter_obj.name} get values: {val}")
        return val

    def get_notch_filer_parameters(self, filter_obj: FilterEntry):
        val = filter_obj.get() if filter_obj.isChecked else None
        if val is not None:
            val['qvalue'] = float(val['qvalue'])
            val['freq'] = float(val['freq'])
        self.logger.debug(f"{filter_obj.name} get values: {val}")
        return [val['freq'], val['qvalue']] if val else []

    def get_scale_filer_parameters(self, filter_obj: FilterEntry):
        val = filter_obj.get() if filter_obj.isChecked else None
        if val is not None:
            val['start'] = int(val['start'])
            val['end'] = int(val['end'])
        self.logger.debug(f"{filter_obj.name} get values: {val}")
        return [val['start'], val['end']] if val else []

    def on_button_go(self):
        _file = self.fileSelector.get_file_path()
        if _file is None or not os.path.exists(_file):
            self.logger.error(f"{_file} is not exist!!")
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
        if self.file_path != _file and self.data_type is not None and self.data_type.lower() == 'raw data':
            if not self.convert_raw_data_to_csv():
                return
        data_rate = self.paramEntry.get(_entry='data_rate')
        self.logger.debug(f"data rate: {data_rate}")
        self.data_drops[0] = int(self.paramEntry.get(_entry='data_drop_start'))
        self.data_drops[1] = int(self.paramEntry.get(_entry='data_drop_end'))
        self.logger.debug(f"data drops: {self.data_drops}")
        self.plot_name = self.plotName.get()
        self.logger.debug(f"plot name: {self.plot_name}")
        # _highpassfilter = self.highPassFilter.get_parameters() if self.highPassFilter.isChecked else None
        _highpassfilter = self.get_pass_filer_parameters(self.highPassFilter)
        _lowpassfilter = self.get_pass_filer_parameters(self.lowPassFilter)
        _notchfilter1 = self.get_notch_filer_parameters(self.notchFilter1)
        _notchfilter2 = self.get_notch_filer_parameters(self.notchFilter2)
        _notchfilter3 = self.get_notch_filer_parameters(self.notchFilter3)
        _fft_scale_x = self.get_scale_filer_parameters(self.fftXScale)
        _fft_scale_y = self.get_scale_filer_parameters(self.fftYScale)

        selected_channels = self.channelsSelector.get_checked_list()
        self.logger.debug(f"selected channels: {selected_channels}")

        if selected_channels is not None and len(selected_channels):
            if self.data_type == "Summary Data":
                _err_code = self.sdp.summary_data_visualize(data=self.df_data, sensor=self.sensor_type,
                                                            channels=selected_channels, name=self.plot_name)
            else:
                _err_code = self.dv.visualize(data=self.df_data, logger=self.logger, name=self.plot_name,
                                              sensor=self.sensor_type, channels=selected_channels, rate=data_rate,
                                              drop=self.data_drops, highpassfilter=_highpassfilter,
                                              lowpassfilter=_lowpassfilter,
                                              notchfilter=[_notchfilter1, _notchfilter2, _notchfilter3],
                                              fftscale=[_fft_scale_x, _fft_scale_y])
            if _err_code != ErrorCode.ERR_NO_ERROR:
                self.messagebox.warning("Error", ErrorMsg[f"{_err_code}"])
        else:
            self.messagebox.information("info", "Select at least one channel!!")

    def refresh_data_channels(self, show: bool = True):
        if not show:
            self.channelsSelector.show_channels()
            return
        if self.df_data is None:
            self.messagebox.warning("Error", "No data available!!")
            return
        self.logger.debug(f"refresh: [{self.sensor_type}], [{self.data_type}]")
        columns = self.df_data.columns.dropna().tolist()
        if self.sensor_type is not None and len(self.sensor_type.strip()) and self.data_type.lower() == "summary data":
            columns = [val for val in columns if val.startswith(self.sensor_type)]
        self.channelsSelector.show_channels(columns, self.data_type)
