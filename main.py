# -*- coding: UTF-8 -*-
from ttkbootstrap.scrolled import ScrolledFrame
# from ttkbootstrap.toast import ToastNotification
from ui_utility import *
from threading import Thread
from my_logger import MyLogger
from datetime import datetime
from tkinter import filedialog
import pandas as pd
from data_visualization_utility import DataVisualization, ErrorCode

tver = "v0.1.002"
tag = "2024/07/12 12:00 +0800"

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
            self.logger.info(f"\n{tver}\n{tag}\nstart...")
            # self.master.iconbitmap(os.path.join(self.resource_path("resource"), "icon.ico"))

            self.data_file = None
            self.dv = DataVisualization(self.logger)
            # main_frm = ttk.Frame(args[0])
            main_frm = ScrolledFrame(args[0], bootstyle='round')
            # main_frm.pack(fill=BOTH, padx=5, pady=5)

            # frm = ttk.Frame(main_frm)
            # frm.pack(fill=X, padx=5, pady=5)
            # analysis_btn = ttk.Button(frm, bootstyle='primary-outline', text="Browser", command=self.on_button_browser)
            # analysis_btn.pack(padx=5)

            frm = ttk.Frame(main_frm)
            frm.pack(expand=True, fill=X, padx=5, pady=5)
            self.file_frm = FileFrm(frm, text="File Path", command=self.on_button_browser)
            self.file_frm.pack(side=LEFT, fill=X, expand=True, padx=5, pady=5)

            frm = ttk.Frame(main_frm)
            frm.pack(fill=X, padx=5, pady=5, anchor='w')

            _values = ["EMG", "PPG", "IMU", "ALT", "Compass", "BTI"]
            self.parameter_frm = ParameterFrm(frm, logger=self.logger,
                                              _combobox=[["Sensor Type", _values,
                                                          self._on_sensor_type_change, [10, 10], ""],
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
                                                    ["combobox", "type", [5,6], "", ["", ""]],
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
        self.parameter_frm.state_config(0)
        self.filter_frm.state_config(0)
        self.file_frm.entry.delete(0, END)
        self.file_frm.entry.insert(0, os.path.basename(self.data_file))
        self.parameter_frm.set("Sensor Type", "")
        self.channel_frm.show_channels([], 0)

        try:
            data = pd.read_csv(self.data_file)
        except Exception as ex:
            self.logger.error(f"Exception: {ex}")
            self.message_box("Error", "File is not correct!!")
            return
        self.parameter_frm.state_config(1)
        self.filter_frm.state_config(1)
        self.channel_name = data.columns.tolist()  # [val for val in data]
        self.logger.info(f"available columns: {self.channel_name}")
        pass

    def _get_sensor_type(self):
        return self.parameter_frm.get("Sensor Type")

    def _get_rate(self):
        return self.parameter_frm.get("Data Rate")

    def _set_rate(self, val):
        return self.parameter_frm.set("Data Rate", val)

    def get_drop_samples(self):
        return self.parameter_frm.get("Data Drop")

    def set_drop_samples(self, val):
        return self.parameter_frm.set("Data Drop", val)

    def get_filter(self, name):
        return self.filter_frm.get(name)

    def set_filter(self, name, val):
        self.filter_frm.set(name, val)

    def get_filter_parameters(self, name):
        return self.filter_frm.get_parameters(name)

    def set_filter_parameters(self, name, params):
        self.filter_frm.set_parameters(name, params)

    def _get_channels(self):
        return self.channel_frm.get_channels()

    def _on_filter_type_change(self, event):
        pass

    def _get_filter_type(self):
        return self.parameter_frm.get("Filter Type")

    def show_data_columns(self, sensor_type):

        self.logger.debug(f"sensor type:{sensor_type}")
        if sensor_type == "EMG":
            _list_filter = ['CH1', 'CH2', 'CH3', 'CH5', 'CH6', 'CH7', 'CH11', 'CH13']
            _columns = 3
        elif sensor_type == "PPG":
            _list_filter = ["MES0_pd1", "MES0_pd2", "MES0_pd3", "MES0_pd4", "MES1_pd1", "MES1_pd2", "MES1_pd3",
                            "MES1_pd4",
                            "MES2_pd1", "MES2_pd2", "MES2_pd3", "MES2_pd4", "MES3_pd1", "MES3_pd2", "MES3_pd3",
                            "MES3_pd4",
                            "MES4_pd1", "MES4_pd2", "MES4_pd3", "MES4_pd4", "MES5_pd1", "MES5_pd2", "MES5_pd3",
                            "MES5_pd4",
                            "MES6_pd1", "MES6_pd2", "MES6_pd3", "MES6_pd4", "MES7_pd1", "MES7_pd2", "MES7_pd3",
                            "MES7_pd4"]
            _columns = 4
        elif sensor_type == "IMU":
            _list_filter = ['ACC_X-Axis', 'ACC_Y-Axis', 'ACC_Z-Axis', 'GYRO_X-Axis', 'GYRO_Y-Axis', 'GYRO_Z-Axis']
            _columns = 3
        elif sensor_type == "ALT":
            _list_filter = ['Pressure', 'Temperature']
            _columns = 2

        elif sensor_type == "Compass":
            _list_filter = ['Compass X', 'Compass Y', 'Compass Z', 'Temperature']
            _columns = 2
        elif sensor_type == "BTI":
            _list_filter = ['Force_sensor0', 'Temperature_sensor0', 'Force_sensor1', 'Temperature_sensor1']
            _columns = 2
        else:
            _list_filter = []
            _columns = 0

        _list = [val for val in _list_filter if val in self.channel_name]
        self.logger.info(f"{_list}")
        self.channel_frm.show_channels(_list, _columns)

    def refresh_parameter_default(self, sensor_type):
        if sensor_type == "EMG":
            '''
                rate: 8192
                drop: 0;-1
                hpf: uncheck,
                lpf: uncheck
                notch filter1: 2430;10
                notch filter2: 3130;10
                notch filter3: 2400;50  
            '''
            self._set_rate(8192)
            self.set_drop_samples("0;-1")
            self.set_filter("High PASS Filter", False)
            self.set_filter("Low PASS Filter ", False)
            self.set_filter("Notch Filter 1", True)
            self.set_filter("Notch Filter 1", True)
            self.set_filter_parameters("Notch Filter 1", {"freq":2430, "q value":10})
            self.set_filter("Notch Filter 2", True)
            self.set_filter_parameters("Notch Filter 2", {"freq":3130, "q value":10})
            self.set_filter("Notch Filter 3", True)
            self.set_filter_parameters("Notch Filter 3", {"freq":2400, "q value":50})
            pass
        elif sensor_type == "PPG":
            '''
                rate: 25
                drop: 5;20
                hpf: check, "lfilter", 3, 0.5,
                lpf: uncheck
                notch filter1: uncheck
                notch filter2: uncheck
                notch filter3: uncheck 
            '''
            self._set_rate(25)
            self.set_drop_samples("125;500")
            self.set_filter("High PASS Filter", True)
            self.set_filter_parameters("High PASS Filter", {"type":"lfilter", "order":3, "freq":0.5})
            self.set_filter("Low PASS Filter ", False)
            self.set_filter("Notch Filter 1", False)
            self.set_filter("Notch Filter 2", False)
            self.set_filter("Notch Filter 3", False)
            pass
        elif sensor_type == "IMU":
            '''
                rate: 120
                drop: 10;490
                hpf: uncheck
                lpf: uncheck
                notch filter1: uncheck
                notch filter2: uncheck
                notch filter3: uncheck 
            '''
            self._set_rate(120)
            self.set_drop_samples("10;490")
            self.set_filter("High PASS Filter", False)
            self.set_filter("Low PASS Filter ", False)
            self.set_filter("Notch Filter 1", False)
            self.set_filter("Notch Filter 2", False)
            self.set_filter("Notch Filter 3", False)
            pass
        elif sensor_type == "ALT":
            '''
               rate: 10
               drop: 0;-1
               hpf: uncheck
               lpf: uncheck
               notch filter1: uncheck
               notch filter2: uncheck
               notch filter3: uncheck 
           '''
            self._set_rate(10)
            self.set_drop_samples("0;-1")
            self.set_filter("High PASS Filter", False)
            self.set_filter("Low PASS Filter ", False)
            self.set_filter("Notch Filter 1", False)
            self.set_filter("Notch Filter 2", False)
            self.set_filter("Notch Filter 3", False)
            pass
        elif sensor_type == "Compass":
            '''
               rate: 50
               drop: 0;-1
               hpf: uncheck
               lpf: uncheck
               notch filter1: uncheck
               notch filter2: uncheck
               notch filter3: uncheck 
           '''
            self._set_rate(50)
            self.set_drop_samples("0;-1")
            self.set_filter("High PASS Filter", False)
            self.set_filter("Low PASS Filter ", False)
            self.set_filter("Notch Filter 1", False)
            self.set_filter("Notch Filter 2", False)
            self.set_filter("Notch Filter 3", False)
            pass
        elif sensor_type == "BTI":
            '''
               rate: 31.25
               drop: 10;-1
               hpf: uncheck
               lpf: uncheck
               notch filter1: uncheck
               notch filter2: uncheck
               notch filter3: uncheck 
           '''
            self._set_rate(31.25)
            self.set_drop_samples("10;72")
            self.set_filter("High PASS Filter", False)
            self.set_filter("Low PASS Filter ", False)
            self.set_filter("Notch Filter 1", False)
            self.set_filter("Notch Filter 2", False)
            self.set_filter("Notch Filter 3", False)
            pass
        else:

            pass

    def _on_sensor_type_change(self, event):
        self.logger.info(f"{event}")
        sensor_type = self._get_sensor_type()
        self.show_data_columns(sensor_type)
        self.refresh_parameter_default(sensor_type)
        pass

    def on_button_go(self):
        _sensor = self._get_sensor_type()
        self.logger.info(f"Sensor: {_sensor}")
        _rate = float(self._get_rate())
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

        if len(_channels):
            _err_code = self.dv.visualize(file=self.data_file, logger=self.logger,
                                          sensor=_sensor, channels=_channels, rate=_rate,
                                          drop=_drop, highpassfilter=_highpassfilter, lowpassfilter=_lowpassfilter,
                                          notchfilter=[_notchfilter1, _notchfilter2, _notchfilter3])
            if _err_code != ErrorCode.ERR_NO_ERROR:
                self.message_box("Error", ErrorMsg[f"{_err_code}"])
        else:
            self.message_box("info", "Select at least one channel!!")
        pass

    def on_filters_check(self):
        pass


if __name__ == '__main__':
    log_path = os.path.join(os.path.abspath("."), 'log')
    if not os.path.exists(log_path):
        try:
            os.makedirs(log_path, True)
            os.chmod(log_path, 0o755)
        except Exception as ret:
            print(str(ret))
            sys.exit(-1)
    try:
        dt = datetime.now()
        filename = dt.strftime("%Y%m%d_%H%M%S")

        _logger = MyLogger(True, os.path.join(log_path, f"log_{filename}.log"), "info")

        wm = ttk.Window(
            title=f'Sensor Data Visualization {tver} ({tag})',
            themename="litera",
        )
        wm.geometry(f"{int(wm.winfo_screenwidth()*0.4)}x{int(wm.winfo_screenheight()*0.6)}"
                    f"+{int(wm.winfo_screenwidth()*0.3)}+{int(wm.winfo_screenheight()*0.2)}")

        t = SensorDataVisualizationUI(wm, logger=_logger)
        wm.mainloop()
    except Exception as e:
        print(f"Excetpion: {str(e)}:{str(e.__traceback__.tb_lineno)}")
        sys.exit(-1)
