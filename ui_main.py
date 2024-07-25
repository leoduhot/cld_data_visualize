# -*- coding: UTF-8 -*-
from ttkbootstrap.scrolled import ScrolledFrame
# from ttkbootstrap.toast import ToastNotification
from ui_utility import *
from my_logger import MyLogger
from datetime import datetime
from tkinter import filedialog
import pandas as pd
from tkinterdnd2 import DND_FILES, TkinterDnD
from data_visualization_utility import DataVisualization, ErrorCode
from data_parser import RawDataParser

ErrorMsg = {
    f"{ErrorCode.ERR_BAD_FILE}": "ErrorCode.ERR_BAD_FILE",
    f"{ErrorCode.ERR_BAD_DATA}": "ErrorCode.ERR_BAD_DATA",
    f"{ErrorCode.ERR_BAD_TYPE}": "ErrorCode.ERR_BAD_DATA",
    f"{ErrorCode.ERR_BAD_ARGS}": "ErrorCode.ERR_BAD_ARGS",
    f"{ErrorCode.ERR_BAD_UNKNOWN}": "ErrorCode.ERR_BAD_UNKNOWN",
}


class SensorDataVisualizationUI(MyTtkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        try:
            self.logger = kwargs['logger']
            # self.pack(fill=ttk.BOTH, expand=True)
            # self.logger.info(f"\n{tver}\n{tag}\nstart...")
            self.master.iconbitmap(os.path.join(self.resource_path("resource"), "icon.ico"))

            self.data_file = None
            self.df_data = None
            self.rdp = RawDataParser(self.logger)
            self.dv = DataVisualization(self.logger)
            # main_frm = ttk.Frame(args[0])
            main_frm = ScrolledFrame(args[0], bootstyle='round')
            # main_frm.pack(fill=BOTH, padx=5, pady=5)

            frm = ttk.Frame(main_frm)
            frm.pack(expand=True, fill=X, padx=5, pady=5)
            self.file_frm = FileFrm(frm, text="File Path", command=self.on_button_browser,
                                      drop=self.on_drop, root=args[0])
            self.file_frm.pack(side=LEFT, fill=X, expand=True, padx=5, pady=5)

            frm = ttk.Frame(main_frm)
            frm.pack(fill=X, expand=True, padx=5, pady=5, anchor='w')

            _values = ["EMG", "PPG", "IMU", "ALT", "MAG", "BTI"]
            self.parameter_frm = ParameterFrm(frm, logger=self.logger,
                                              _combobox=[
                                                        ["Sensor Type", _values,
                                                          self._on_sensor_type_change, [10, 10], ""],
                                                        ["Data Type", ["Raw Data", "Tester Data"],
                                                           self.on_data_type_change, [10, 10], ""],
                                                         ],
                                              _entry=[["Data Rate", [10, 12], 8192, ""],
                                                      ["Data Drop", [10, 12], "0;-1",
                                                       "valid input:<start>;<end>\n-1: the last one"],
                                                      ],
                                              columns=3)
            self.parameter_frm.pack(side=LEFT)
            self.parameter_frm.state_config(0)

            frm = ttk.Frame(main_frm)
            frm.pack(fill=X, padx=5, pady=5)
            _filter_type = ["lfilter", "filtfilt"]
            self.filter_frm = FilterFrm(frm, logger=self.logger,
                                            parameters={
                                                "High PASS Filter": [
                                                    ["combobox", "type", [5, 6], "", _filter_type],
                                                    ["entry", "order", [5, 6], "", ""],
                                                    ["entry", "freq", [5, 10], "",
                                                        "valid value: scalar value"]
                                                ],
                                                "Low PASS Filter ": [
                                                    ["combobox", "type", [5,6], "", _filter_type],
                                                    ["entry", "order", [5,6], "", ""],
                                                    ["entry", "freq", [5,10], "", "valid value: scalar value"]
                                                ],
                                                "Notch Filter 1": [
                                                    ["entry", "freq", [5, 10], "", ""],
                                                    ["entry", "q value", [8, 10], "", ""]
                                                ],
                                                "Notch Filter 2": [
                                                    ["entry", "freq", [5, 10], "", ""],
                                                    ["entry", "q value", [8, 10], "", ""]
                                                ],
                                                "Notch Filter 3": [
                                                    ["entry", "freq", [5, 10], "", ""],
                                                    ["entry", "q value", [8, 10], "", ""]
                                                ],
                                                "FFT Scale X-axis": [
                                                    ["entry", "start", [5, 10], "", ""],
                                                    ["entry", "end", [5, 10], "", ""]
                                                ],
                                                "FFT Scale Y-axis": [
                                                    ["entry", "start", [5, 10], "", ""],
                                                    ["entry", "end", [5, 10], "", ""]
                                                ],
                                                })
            self.filter_frm.pack(side=LEFT)
            self.filter_frm.state_config(0)

            frm = ttk.Frame(main_frm)
            frm.pack(fill=X, padx=5, pady=5)
            self.channel_frm = ChannelFrm(frm, logger=self.logger)
            self.channel_frm.pack(side=LEFT)
            # self.channel_frm.show_channels([val for val in range(21)[1:]])

            frm = ttk.Frame(main_frm)
            frm.pack(fill=X, padx=5, pady=5)
            analysis_btn = ttk.Button(frm, bootstyle='primary-outline', text="GO", command=self.on_button_go)
            analysis_btn.pack(padx=5)

            main_frm.pack(fill=BOTH, expand=YES, padx=5, pady=5)

            self.channel_name = []
            self.data_type = None
            self.sensor_type = None

            # # logo
            # imgpath = os.path.join(self.resource_path("resource"), "logo.png")s
            # self.logger.debug(f"imgpath:{imgpath}")
            # self.img = ttk.PhotoImage(name='logo', file=imgpath)
            # frm = ttk.Frame(right_panel)
            # frm.pack(fill=X)
            # lab = ttk.Label(frm, image=self.img.name)
            # lab.pack(side=RIGHT, padx=5, pady=2)
        except Exception as exp:
            print(f"Excetpion: {str(exp)}:{str(exp.__traceback__.tb_lineno)}")

    def on_button_browser(self):
        self.data_file = filedialog.askopenfilename(title="Select a File",
                                                    filetypes=(("Text files", "*.txt"), ("CSV files", "*.csv")))
        self.logger.info(f"on_button_browser, file path: {self.data_file}")
        self.parameter_state_config(0)
        self.filter_state_config(0)
        self.sensor_type = None
        self.file_frm.set(os.path.basename(self.data_file))
        self.set_parameter("Sensor Type", "")
        self.set_parameter("Data Type", "")
        self.show_data_columns("")

        self.parameter_state_config(1)
        self.filter_state_config(1)
        pass

    def on_drop(self):
        self.data_file = self.file_frm.get_filepath()
        self.logger.info(f"on_drop, file path:{self.data_file}")
        self.parameter_state_config(0)
        self.filter_state_config(0)
        self.sensor_type = None
        # self.file_frm.entry.delete(0, END)
        # self.file_frm.entry.insert(0, os.path.basename(self.data_file))
        self.file_frm.set(os.path.basename(self.data_file))
        self.set_parameter("Sensor Type", "")
        self.set_parameter("Data Type", "")
        self.show_data_columns("")

        self.parameter_state_config(1)
        self.filter_state_config(1)
        pass

    def get_parameter(self, name):
        return self.parameter_frm.get(name)

    def set_parameter(self, name, val):
        self.parameter_frm.set(name, val)

    def parameter_state_config(self, s):
        self.parameter_frm.state_config(s)

    def get_data_type(self):
        return self.get_parameter("Data Type")

    def _get_rate(self):
        return self.get_parameter("Data Rate")

    def _set_rate(self, val):
        return self.parameter_frm.set("Data Rate", val)

    def get_drop_samples(self):
        return self.get_parameter("Data Drop")

    def set_drop_samples(self, val):
        return self.parameter_frm.set("Data Drop", val)

    def get_filter(self, name):
        return self.filter_frm.get(name)

    # check or uncheck filter
    def set_filter(self, name, val):
        self.filter_frm.set(name, val)

    def get_filter_parameters(self, name):
        return self.filter_frm.get_parameters(name)

    def set_filter_parameters(self, name, params):
        self.filter_frm.set_parameters(name, params)

    def filter_state_config(self, s):
        self.filter_frm.state_config(s)

    def show_data_columns(self, sensor_type):
        self.logger.debug(f"show_data_columns: sensor type:{sensor_type}")
        _list_filter = self.channel_name
        if sensor_type == "EMG":
            _columns = 3
        elif sensor_type == "PPG":
            _columns = 4
        elif sensor_type == "IMU":
            _columns = 3
        elif sensor_type == "ALT":
            _columns = 2
        elif sensor_type == "MAG":
            _columns = 2
        elif sensor_type == "BTI":
            _columns = 2
        else:
            _list_filter = []
            _columns = 0

        # _list = [val for val in _list_filter if val in self.channel_name]
        # self.logger.info(f"{_list}")
        self.channel_frm.show_channels(_list_filter, _columns)

    def refresh_parameter_default(self, sensor_type):
        self.set_filter("High PASS Filter", False)
        self.set_filter("Low PASS Filter ", False)
        self.set_filter("Notch Filter 1", False)
        self.set_filter("Notch Filter 2", False)
        self.set_filter("Notch Filter 3", False)
        if sensor_type == "EMG":
            self._set_rate(8192)
            self.set_drop_samples("0;-1")
            pass
        elif sensor_type == "PPG":
            self._set_rate(25)
            self.set_drop_samples("125;500")
            self.set_filter("High PASS Filter", True)
            self.set_filter_parameters("High PASS Filter", {"type":"lfilter", "order":3, "freq":0.5})
            pass
        elif sensor_type == "IMU":
            self._set_rate(120)
            self.set_drop_samples("10;490")
            pass
        elif sensor_type == "ALT":
            self._set_rate(10)
            self.set_drop_samples("0;-1")
            pass
        elif sensor_type == "Compass":
            self._set_rate(50)
            self.set_drop_samples("0;-1")
            pass
        elif sensor_type == "BTI":
            self._set_rate(31.25)
            self.set_drop_samples("10;72")
            pass
        else:

            pass

    def on_data_type_change(self, event):
        self.logger.info(f"on_data_type_change, {event}")
        if self.sensor_type is None:
            self.message_box("Error", f"Select sensor type first!!")
            return

        self.data_type = self.get_data_type()
        try:
            if self.data_type == "Tester Data":
                self.df_data = pd.read_csv(self.data_file, index_col=False)
                # self.df_data = pd.read_csv(self.data_file)
            elif self.data_type == "Raw Data":
                err, self.df_data = self.rdp.extract_sensor_data(self.data_file, self.sensor_type.lower())
                if err != ErrorCode.ERR_NO_ERROR:
                    self.message_box("Error", f"Bad raw data!! {err}")
                    return
            else:
                self.message_box("Error", "Not supported data type!!")
                return
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            self.message_box("Error", "File is not correct!!")
            return

        self.channel_name = [val for val in self.df_data.columns.tolist() if 'Unnamed: ' not in val]
        self.logger.info(f"available columns: {self.channel_name}")
        # self.logger.info(f"{self.df_data[self.channel_name[0]]}")
        self.show_data_columns(self.sensor_type)
        self.refresh_parameter_default(self.sensor_type)

    def _on_sensor_type_change(self, event):
        self.logger.info(f"{event}")
        self.sensor_type = self.get_parameter("Sensor Type")
        self.set_parameter("Data Type", "")
        self.show_data_columns("others")
        # self.show_data_columns(sensor_type)
        self.refresh_parameter_default(self.sensor_type)
        pass

    def on_button_go(self):
        _sensor = self.get_parameter("Sensor Type")
        self.logger.info(f"Sensor: {_sensor}")
        _rate = float(self.get_parameter("Data Rate"))
        self.logger.info(f"Data rate: {_rate}")
        _drop = [int(val) for val in self.get_drop_samples().split(";")]
        self.logger.info(f"Drop samples: {_drop}")
        _channels = self.channel_frm.get_channels()
        self.logger.info(f"Selected: {_channels}")
        if self.get_filter("High PASS Filter"):
            _highpassfilter = self.get_filter_parameters("High PASS Filter")
        else:
            _highpassfilter = {"type": "", "order": 0, "freq": 0}
        self.logger.info(f"High PASS Filter: {_highpassfilter}")
        if self.get_filter("Low PASS Filter "):
            _lowpassfilter = self.get_filter_parameters("Low PASS Filter ")
        else:
            _lowpassfilter = {"type": "", "order": 0, "freq": 0}
        self.logger.info(f"Low PASS Filter: {_lowpassfilter}")
        if self.get_filter("Notch Filter 1"):
            _params = self.get_filter_parameters("Notch Filter 1")
            _notchfilter1 = [float(_params[key].strip()) for key in _params]
        else:
            _notchfilter1 = [0,0]
        self.logger.info(f"Notch Filter 1: {_notchfilter1}")
        if self.get_filter("Notch Filter 2"):
            _params = self.get_filter_parameters("Notch Filter 2")
            _notchfilter2 = [float(_params[key].strip()) for key in _params]
        else:
            _notchfilter2 = [0, 0]
            self.logger.info(f"Notch Filter 2: {_notchfilter2}")
        if self.get_filter("Notch Filter 3"):
            _params = self.get_filter_parameters("Notch Filter 3")
            _notchfilter3 = [float(_params[key].strip()) for key in _params]
        else:
            _notchfilter3 = [0, 0]
        self.logger.info(f"Notch Filter 3: {_notchfilter3}")
        if self.get_filter("FFT Scale X-axis"):
            _params = self.get_filter_parameters("FFT Scale X-axis")
            _fft_scale_x = [float(_params[key].strip()) for key in _params]
        else:
            _fft_scale_x = []
        if self.get_filter("FFT Scale Y-axis"):
            _params = self.get_filter_parameters("FFT Scale Y-axis")
            self.logger.info(_params)
            _fft_scale_y = [float(_params[key].strip()) for key in _params]
        else:
            _fft_scale_y = []

        if len(_channels):
            _err_code = self.dv.visualize(data=self.df_data, logger=self.logger,
                                          sensor=_sensor, channels=_channels, rate=_rate,
                                          drop=_drop, highpassfilter=_highpassfilter, lowpassfilter=_lowpassfilter,
                                          notchfilter=[_notchfilter1, _notchfilter2, _notchfilter3],
                                          fftscale=[_fft_scale_x, _fft_scale_y])
            if _err_code != ErrorCode.ERR_NO_ERROR:
                self.message_box("Error", ErrorMsg[f"{_err_code}"])
        else:
            self.message_box("info", "Select at least one channel!!")
        pass

    def on_filters_check(self):
        pass


class MyDnDWindow(ttk.Window, TkinterDnD.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        TkinterDnD.__init__("DnD")

