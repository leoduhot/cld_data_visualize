# -*- coding: UTF-8 -*-
import numpy as np
import pandas as pd
import scipy.fftpack
from scipy import signal
from scipy.signal import butter, lfilter, filtfilt
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.table import Table
from matplotlib.widgets import CheckButtons
import math
import logging
from enum import IntEnum
import time


class ErrorCode(IntEnum):
    ERR_NO_ERROR = 0,
    ERR_BAD_FILE = -1,
    ERR_BAD_DATA = -2,
    ERR_BAD_TYPE = -3,
    ERR_BAD_ARGS = -4,
    ERR_BAD_UNKNOWN = -255,


class DataVisualization:
    def __init__(self, *args, **kwargs):
        self.logger = kwargs["logger"] if 'logger' in kwargs else logging.getLogger()
        self.figure_canvas = kwargs['canvas'] if 'canvas' in kwargs else None
        self.list = []   # column name
        self.bad_channel = []
        self.sensor = None
        self.sample_rate = 1
        self.data_drop = [0, -1]
        self.data_file = None
        self.high_pass_filter = {"type": '', "order": 0, "freq": 0}
        self.low_pass_filter = {"type": '', "order": 0, "freq": 0}
        self.notch_filter = [[0, 0], [0, 0], [0, 0]]
        self.df_data = None
        self.check_btn = None
        self.fft_scale = [[], []]
        self.markers = list()
        self.fig = None
        self.plot_name = None
        self.figsize = None
        self.txt_fontsize = 10
        self.channel_lines = dict()  #save {ax:[lines]) for click event

        self.process_func = {
            "emg": self.emg_data,
            "ppg": self.ppg_data,
            "imu": self.imu_data,
            "alt": self.alt_data,
            "mag": self.compass_data,
            "bti": self.bti_data,
            "others": self.others_data,
        }

    def visualize(self, *args, **kwargs):
        self.logger.info(f"start visualize ...")
        self.list = kwargs["channels"] if "channels" in kwargs else []
        self.sensor = kwargs["sensor"] if "sensor" in kwargs else "others"
        self.sample_rate = float(kwargs["rate"]) if "rate" in kwargs else 1
        self.data_drop = kwargs["drop"] if "drop" in kwargs else [0, -1]
        self.data_file = kwargs["file"] if "file" in kwargs else None
        self.high_pass_filter = kwargs["highpassfilter"] if "highpassfilter" in kwargs else {"type": '', "order": 0, "freq": 0}
        self.low_pass_filter = kwargs["lowpassfilter"] if "lowpassfilter" in kwargs else {"type": '', "order": 0, "freq": 0}
        self.notch_filter = kwargs["notchfilter"] if "notchfilter" in kwargs else [[0,0], [0,0], [0,0]]
        self.fft_scale = kwargs["fftscale"] if "fftscale" in kwargs else [[], []]
        self.plot_name = kwargs["name"] if "name" in kwargs else self.sensor
        self.markers = []
        if self.fig is not None:
            for ax in self.fig.axes:
                ax.cla()
        self.fig = None
        self.channel_lines = {}

        if self.plot_name is None or not len(self.plot_name.strip()):
            self.plot_name = self.sensor

        if self.data_file is not None:
            try:
                self.df_data = pd.read_csv(self.data_file)
            except Exception as ex:
                self.logger.error(f"Exception: {str(ex)}")
                return ErrorCode.ERR_BAD_FILE
        else:
            self.df_data = kwargs["data"] if "data" in kwargs else None

        if self.df_data is None:
            return ErrorCode.ERR_BAD_DATA

        return self.process_func[self.sensor.lower()]()

    def adjust_color(self, origin, diff=(-32, 32, -16)):
        self.logger.debug(f"origin:{origin}, diff:{diff}")
        r = min(max(0, int(origin[1:3], 16) + diff[0]), 255)
        g = min(max(0, int(origin[3:5], 16) + diff[1]), 255)
        b = min(max(0, int(origin[5:7], 16) + diff[2]), 255)
        # self.logger.info(f"new: #{r:02x}{g:02x}{b:02x}")
        return f"#{r:02x}{g:02x}{b:02x}"

    def others_data(self, *args, **kwargs):
        self.logger.debug(f"Nothing to do!!")
        pass

    def do_notch_filter(self, _sig):
        try:
            if self.notch_filter is None or not len(self.notch_filter):
                self.logger.info(f"notch filer parameter is empty, do nothing")
                return
            self.logger.info(f"do_notch_filter")
            _new_sig = _sig
            for f in self.notch_filter:
                if f is not None and f != [0, 0] and f != []:
                    self.logger.info(f"notch parameters: {f}")
                    try:
                        b1, a1 = signal.iirnotch(w0=float(f[0]), Q=float(f[1]), fs=self.sample_rate)
                    except Exception as ex:
                        self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
                        return ErrorCode.ERR_BAD_ARGS, _sig
                    _new_sig = signal.lfilter(b1, a1, _new_sig)
            return ErrorCode.ERR_NO_ERROR, _new_sig
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_UNKNOWN, _sig

    def do_fft(self, _sig):
        try:
            if len(_sig) == 0:
                self.logger.error(f"signal is empty!!")
                return ErrorCode.ERR_BAD_DATA, [], [], []
            else:
                fft_size = 2 ** int(np.ceil(np.log2(len(_sig))))
                fft_freq = np.fft.rfftfreq(fft_size, d=1 / self.sample_rate)
                fft_amplitude = np.abs(np.fft.rfft(_sig, fft_size))
                fft_dbv = 20 * np.log10(fft_amplitude / 1)  # Convert to dBV
            return ErrorCode.ERR_BAD_ARGS, fft_freq, fft_amplitude, fft_dbv
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_UNKNOWN, [], [], []

    def do_statistics(self, _sig):
        # ToDo :: TBD
        pass

    def do_high_pass_filter(self, sig_list, axis=-1):
        try:
            self.logger.info(f"do_high_pass_filter ...")
            if self.high_pass_filter is None or self.high_pass_filter["type"] == "":
                self.logger.info(f"bad high pass filter parameters, do nothing!")
                return ErrorCode.ERR_NO_ERROR, sig_list
            order = int(self.high_pass_filter["order"])
            freq1 = float(self.high_pass_filter["freq"])
            sig = np.asarray(sig_list, dtype=np.float32)
            sig = sig - sig[0]
            nyq = 0.5 * self.sample_rate  # Nyquist frequency
            high = freq1 / nyq
            b, a = butter(order, high, btype='high')
            # apply filter
            if self.high_pass_filter["type"] == 'lfilter':
                sig_filt = lfilter(b, a, sig, axis=axis)
            elif self.high_pass_filter["type"] == 'filtfilt':
                sig_filt = filtfilt(b, a, sig, axis=axis)
            else:
                self.logger.error(f"filter type is invalid, do nothing")
                return ErrorCode.ERR_BAD_ARGS, sig_list

            return ErrorCode.ERR_NO_ERROR, sig_filt.tolist()
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_UNKNOWN, sig_list

    def do_low_pass_filter(self, sig_list, axis=-1):
        try:
            self.logger.info(f"do_low_pass_filter ...")
            if self.low_pass_filter is None or self.low_pass_filter["type"] == "":
                self.logger.info(f"bad low pass filter parameters, do nothing!")
                return ErrorCode.ERR_NO_ERROR, sig_list
            order = int(self.low_pass_filter["order"])
            freq1 = int(self.low_pass_filter["freq"])
            sig = np.asarray(sig_list, dtype=np.float32)
            sig = sig - sig[0]
            nyq = 0.5 * self.sample_rate  # Nyquist frequency
            high = freq1 / nyq
            b, a = butter(order, high, btype='low')
            # apply filter
            if self.low_pass_filter["type"] == 'lfilter':
                sig_filt = lfilter(b, a, sig, axis=axis)
            elif self.low_pass_filter["type"] == 'filtfilt':
                sig_filt = filtfilt(b, a, sig, axis=axis)
            else:
                self.logger.error(f"filter type is invalid, do nothing")
                return ErrorCode.ERR_BAD_ARGS, sig_list

            return ErrorCode.ERR_NO_ERROR, sig_filt.tolist()
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_UNKNOWN, sig_list

    def do_data_conversion(self, _sensor=None, b_snr=False):
        self.logger.info(f"do_data_conversion ...")
        if _sensor == "emg":
            return self._convert_emg_data()
        elif _sensor == "ppg":
            return self._convert_ppg_data()
        else:
            return self._convert_other_sensors_data(b_snr)

    def _convert_other_sensors_data(self, b_snr=False):
        keys = ["channel", "avg", "sig", "noise", "time", "sum_vector", "snr"]
        _data = {key: [] for key in keys}
        self.bad_channel = []
        for channel in self.list:
            try:
                if int(self.data_drop[1]) > 0:
                    _sig = self.df_data[channel].iloc[int(self.data_drop[0]):int(self.data_drop[1])]
                else:
                    _sig = self.df_data[channel].iloc[int(self.data_drop[0]):]
                avg = np.mean(_sig)
                _sig_ac = _sig - avg

                _err_code, _sig_ac = self.do_high_pass_filter(_sig_ac)
                if _err_code != ErrorCode.ERR_NO_ERROR:
                    return _err_code, _data
                _err_code, _sig_ac = self.do_low_pass_filter(_sig_ac)
                if _err_code != ErrorCode.ERR_NO_ERROR:
                    return _err_code, _data
                _err_code, _sig_ac = self.do_notch_filter(_sig_ac)
                if _err_code != ErrorCode.ERR_NO_ERROR:
                    return _err_code, _data

                noise = np.std(_sig_ac)

                self.logger.debug(f"{avg}, {noise}")
                timex = np.linspace(0, len(_sig_ac) / self.sample_rate, len(_sig_ac))
                sum_vector = np.array(_sig_ac)
                _data["channel"].append(channel)
                _data["avg"].append(avg)
                _data["sig"].append(_sig_ac)
                _data["noise"].append(noise)
                _data["time"].append(timex)
                _data["sum_vector"].append(sum_vector)
                if b_snr:
                    snr = 20 * math.log10(avg / noise)
                    _data["snr"].append(snr)
            except Exception as ex:
                self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
                self.logger.error(f"this channel have problem: {channel}")
                self.bad_channel.append(channel)
                continue
        return ErrorCode.ERR_NO_ERROR, _data

    def on_click(self, event):
        if event.button != 3:  #  1: left key, 2: middle key, 3: right key
            # self.logger.info("not right key, do nothing ...")
            return
        if event.inaxes not in self.channel_lines:  # axis is not in tracker
            return
        x = event.xdata
        y = event.ydata
        ax = event.inaxes
        self.logger.info(f"click on: {x}, {y}")

        _line = self.channel_lines[ax][0]
        x_length = len(_line.get_data()[0])
        for line in self.channel_lines[ax]:
            x_data, y_data = list(line.get_data())
            if x_length < len(x_data):
                x_length = len(x_data)
                _line = line
        # find most close x point
        x_data, y_data = list(_line.get_data())
        idx = np.argmin(np.abs(x_data - x))
        # find the most close y point
        y_distance = np.abs(y - y_data[idx])
        for line in self.channel_lines[ax]:
            x_data, y_data = list(line.get_data())
            if idx < len(y_data) and np.abs(y - y_data[idx]) < y_distance:
                y_distance = np.abs(y - y_data[idx])
                _line = line

        x_data, y_data = list(_line.get_data())
        for point in self.markers:  # remove duplicate marker
            if point[0] == _line and point[1] == idx:
                point[2].remove()
                point[3].remove()
                self.markers.remove(point)
                self.fig.canvas.draw_idle()
                self.logger.info(f"remove duplicate point!!")
                return
        # Add a new marker
        marker = ax.plot(x_data[idx], y_data[idx], 'ro')[0]
        text = ax.annotate(f'({x_data[idx]:.4f}, {y_data[idx]:.4f})',
                           xy=(x_data[idx], y_data[idx]))
        self.markers.append((_line, idx, marker, text))
        self.fig.canvas.draw_idle()
        self.logger.info(f"add a new mark on:{x_data[idx]},{y_data[idx]}")
        return

    def draw_checkbutton(self, _plt, _lines, _colors):
        _h = 0.025*len(self.list)
        # _w = len(max(self.list, key=len))
        # 0.62*_w/self.fig.dpi
        rax = _plt.axes((0.91, 0.88-_h, 0.08, _h))
        self.check_btn = CheckButtons(
            ax=rax,
            labels=self.list,
            actives=[True for _ in range(len(self.list))],
            label_props={'color': _colors},
            frame_props={'edgecolor': _colors},
            check_props={'facecolor': _colors},
        )

        def callback(label):
            for line in _lines[label]:
                line.set_visible(not line.get_visible())
                line.figure.canvas.draw_idle()
            if self.figure_canvas is not None:
                self.figure_canvas.canvas.draw_idle()
        self.check_btn.on_clicked(callback)

    def _draw_table(self, _plt, _table_data):
        try:
            self.logger.info(f"_draw_table..")
            _plt.axis('off')
            table = Table(_plt, bbox=[0, 0, 1, 1])
            table.set_fontsize(8)
            nrow = len(_table_data)
            ncol = len(_table_data[0])
            for i in range(nrow):
                for j in range(ncol):
                    table.add_cell(i, j, 1, 1, text=str(_table_data[i, j]), loc='center')
            colors = ["#f8f8ff", "#f5f5f5"]
            for (row, col), cell in table.get_celld().items():
                self.logger.debug(f"{row}, {col}")
                cell.set_linewidth(0.3)
                cell.set_text_props(fontsize=8)
                cell.set_edgecolor("white")
                if row == 0:
                    cell.set_facecolor("#e6e6fa")
                else:
                    cell.set_facecolor(colors[row%2])
            _plt.add_table(table)
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")

    def do_plot_list(self, data):
        self.logger.info(f"do_plot_list..")
        plt.clf()
        plt.close("all")
        _nrows = len(self.list) + 1
        self.fig = plt.figure(self.plot_name, figsize=(20, 10))
        self.fig.suptitle(self.sensor, fontsize=16)
        self.figsize = self.fig.get_size_inches()
        if self.figure_canvas is not None:
            self.figure_canvas.create_canvas(self.fig)
        self.fig.subplots(_nrows, 2)
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        # plt.subplots(_nrows, 2, figsize=(20, 20))
        plt.subplots_adjust(hspace=0.6)
        colors = ["#00cd00", "#0000ff"]
        # plt.figtext(.3, .9, 'Aggressor:{}'.format(aggressor_name), fontsize=20, ha='center')
        # plt.figtext(.7, .9, 'Victim:IMU', fontsize=20, ha='center')
        for i in range(0, _nrows-1):
            try:
                if self.list[i] in self.bad_channel:
                    self.logger.error(f"skip bad channel: {self.list[i]}")
                    continue
                # Time domain
                ax = plt.subplot(_nrows, 2, i * 2 + 1)
                plt.text(-0.05, 1.05, self.list[i], fontsize=10, transform=plt.gca().transAxes)
                _line, = plt.plot(data["time"][i], data["sig"][i], color=colors[0])
                if ax in self.channel_lines:
                    self.channel_lines[ax].append(_line)
                else:
                    self.channel_lines.update({ax: [_line]})
                plt.xlabel('Time [s]', fontsize=10)
                plt.xticks(fontsize=8)
                plt.yticks(fontsize=8)

                # Frequency domain
                ax = plt.subplot(_nrows, 2, i * 2 + 2)
                plt.text(-0.05, 1.05, f"{self.list[i]}[unit/sqrt(Hz)]",
                         fontsize=10, transform=plt.gca().transAxes)
                FFT = 2.0 / len(data["sum_vector"][i]) * abs(scipy.fft.fft(data["sum_vector"][i]))
                _freqs = scipy.fftpack.fftfreq(len(data["time"][i]), data["time"][i][1] - data["time"][i][0])
                _line, = plt.plot(_freqs[1:int(len(_freqs) / 2)], (FFT[1:int(len(_freqs) / 2)]), color=colors[1])
                if ax in self.channel_lines:
                    self.channel_lines[ax].append(_line)
                else:
                    self.channel_lines.update({ax: [_line]})
                # Peak
                peak_index = np.argmax(FFT[1:int(len(_freqs) / 2)])
                _line, = plt.plot(_freqs[1:int(len(_freqs) / 2)][peak_index],
                         FFT[1:int(len(_freqs) / 2)][peak_index], 'o', color="#ff0000")
                plt.axvline(_freqs[1:int(len(_freqs) / 2)][peak_index], color="#ff0000", linestyle='--')
                if len(self.fft_scale[0]):
                    _start, _end = list(self.fft_scale[0])
                    _end = self.sample_rate / 2 if _end == -1 else _end
                    plt.xlim(_start, _end)
                if len(self.fft_scale[1]):
                    _start, _end = list(self.fft_scale[1])
                    plt.ylim([_start, _end])
                # plt.xlim([0.1, fs / 2])
                plt.xlabel('Frequency [Hz]')
                plt.xticks(fontsize=8)
                plt.yticks(fontsize=8)
                # plt.ylabel('{}\n[unit/sqrt(Hz)]'.format(self.list[i]), fontsize=10, rotation=0, loc="top")
            except Exception as ex:
                self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
                self.logger.error(f"this channel have problem:{self.list[i]}")
                plt.axis("off")
                continue

        # statistics table
        table_ax = plt.subplot(_nrows, 2, (_nrows-1) * 2 + 1)

        # plt.rcParams.update({'font.size': 10})
        table_data = np.array(
            [["Signal"] + self.list,
             ["Average"] + ["{:.8f}".format(val) for val in data["avg"]],
             ["Noise"] + ["{:.8f}".format(val) for val in data["noise"]]
             ]).T
        self._draw_table(table_ax, table_data)

        plt.subplot(_nrows, 2, (_nrows-1) * 2 + 2)
        plt.axis("off")

        self.fig.canvas.mpl_connect('resize_event', self.update_text_size)
        _postfix = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        _png_file = f"{self.plot_name}_{_postfix}.png"
        plt.savefig(_png_file)
        if self.figure_canvas is not None and len(self.list):
            self.figure_canvas.show_plot()
        return ErrorCode.ERR_NO_ERROR

    def do_plot_together(self, time_data, freq_data, statistics_data):
        pass

    def _convert_emg_data(self):
        self.bad_channel = []
        keys = ["channel", "time", "sig", "rms", "avg_p2p", "cycle", "cycle_time",
                "max", "min", "fft_freq", "peak_freq", "fft_dbv", "peak_dbv", "bias"]
        _data = {key: [] for key in keys}
        for channel in self.list:
            if int(self.data_drop[1]) > 0:
                voltage = self.df_data[channel].iloc[int(self.data_drop[0]):int(self.data_drop[1])]
            else:
                voltage = self.df_data[channel].iloc[int(self.data_drop[0]):]
            # voltage = self.df_data[channel].iloc[int(self.data_drop[0]):int(self.data_drop[1])]
            # Calculate DC bias
            # self.logger.debug(f"voltage[0]: {voltage[0]} {+len(voltage)}")
            # self.logger.debug(f"voltage:\n{voltage}")
            # return
            dc_bias = np.mean(voltage)
            # Remove DC bias from waveform
            ac_signal = voltage - dc_bias
            _err_code, ac_signal = self.do_high_pass_filter(ac_signal)
            if _err_code != ErrorCode.ERR_NO_ERROR:
                return _err_code, _data
            _err_code, ac_signal = self.do_low_pass_filter(ac_signal)
            if _err_code != ErrorCode.ERR_NO_ERROR:
                return _err_code, _data
            _err_code, ac_signal = self.do_notch_filter(ac_signal)
            if _err_code != ErrorCode.ERR_NO_ERROR:
                return _err_code, _data
            # Create time axis
            time = np.arange(len(voltage)) / self.sample_rate
            # Calculate FFT of AC signal
            if len(ac_signal) == 0:
                self.logger.error(f"bad channel data: {channel}")
                self.bad_channel.append(channel)
                continue
            else:
                fft_size = 2 ** int(np.ceil(np.log2(len(ac_signal))))
                fft_freq = np.fft.rfftfreq(fft_size, d=1/self.sample_rate)
                fft_amplitude = np.abs(np.fft.rfft(ac_signal, fft_size))
                fft_dbv = 20 * np.log10(fft_amplitude / 1) # Convert to dBV

            # Find peak value of AC signal in FFT plot
            # print(str(fft_amplitude))
            ac_peak_index = np.argmax(fft_amplitude)
            # print(str(ac_peak_index))
            ac_peak_freq = fft_freq[ac_peak_index]
            ac_peak_dbv = fft_dbv[ac_peak_index]
            ac_peak_coord = (ac_peak_freq, ac_peak_dbv)
            self.logger.info(f"peak:{ac_peak_freq},{ac_peak_dbv}")
            # Find cycle time and max/min values in each cycle
            cycle_time = 1 / ac_peak_freq
            num_cycles = int(len(ac_signal) / (cycle_time * self.sample_rate))
            max_vals = np.zeros(num_cycles)
            min_vals = np.zeros(num_cycles)
            for i in range(num_cycles):
                cycle_start = int(i * cycle_time * self.sample_rate)
                cycle_end = int((i+1) * cycle_time * self.sample_rate)
                cycle_vals = ac_signal[cycle_start:cycle_end]
                max_val = np.max(cycle_vals)
                min_val = np.min(cycle_vals)
                max_vals[i] = max_val
                min_vals[i] = min_val

            # Calculate peak-to-peak value for each cycle
            peak_to_peak_vals = max_vals - min_vals

            # Compute average peak-to-peak value
            avg_peak_to_peak_val = np.mean(peak_to_peak_vals)

            # Calculate RMS level value
            rms_val = np.sqrt(np.mean(np.array(ac_signal) ** 2))
            _data["channel"].append(channel)
            _data["time"].append(time)
            _data["sig"].append(ac_signal)
            _data["rms"].append(rms_val)
            _data["avg_p2p"].append(avg_peak_to_peak_val)
            _data["cycle"].append(num_cycles)
            _data["cycle_time"].append(cycle_time)
            _data["max"].append(max_vals)
            _data["min"].append(min_vals)
            _data["fft_freq"].append(fft_freq)
            _data["peak_freq"].append(ac_peak_freq)
            _data["fft_dbv"].append(fft_dbv)
            _data["peak_dbv"].append(ac_peak_dbv)
            _data["bias"].append(dc_bias)
        return ErrorCode.ERR_NO_ERROR, _data

    def emg_data(self, *args, **kwargs):
        self.logger.info(f"process {self.sensor} data")
        _err_code, _data = self.do_data_conversion(_sensor="emg")
        if _err_code != ErrorCode.ERR_NO_ERROR:
            return _err_code
        plt.clf()
        plt.close("all")
        self.fig = plt.figure(f"{self.sensor}", figsize=(20, 10))
        self.fig.suptitle(self.sensor, fontsize=16)
        self.figsize = self.fig.get_size_inches()
        if self.figure_canvas is not None:
            self.figure_canvas.create_canvas(self.fig)
        plt.subplots_adjust(hspace=0.6)
        self.fig.subplots(2, 2)
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        ax = plt.subplot(2, 2, 1)
        plt.rcParams.update({'font.size': 10})
        # ax = axes[0][0]
        channel_lines = {key: [] for key in self.list}
        channel_colors = {}
        _shift = np.amax(_data["sig"])-np.amin(_data["sig"])
        # print(_shift)
        for i in range(0, len(self.list)):
            if self.list[i] in self.bad_channel:
                self.logger.error(f"skip bad channel: {self.list[i]}")
                continue
            plt.rcParams.update({'font.size': 10})
            _line, = plt.plot(_data["time"][i], _data["sig"][i]+i*_shift, label=f'{self.list[i]} AC Signal')
            channel_colors[self.list[i]] = _line.get_color()
            if ax in self.channel_lines:
                self.channel_lines[ax].append(_line)
            else:
                self.channel_lines.update({ax: [_line]})

        plt.text(-0.05, 1.05, f"Signal (V)", fontsize=10, transform=plt.gca().transAxes)
        plt.xlabel('Time (S)', fontsize=10)
        plt.yticks([_shift*i for i in np.arange(0, len(self.list))])
        ax.set_yticklabels(self.list)
        # ax.legend()

        table_ax = plt.subplot(2, 2, 3)
        # plt.rcParams.update({'font.size': 10})
        table_data = np.array([["Signal"]+self.list, ["RMS Level(V)"]+["{:.8f}".format(val) for val in _data["rms"]],
                    ["Average Peak-to-Peak"]+["{:.8f}".format(val) for val in _data["avg_p2p"]],
                    ["DC bias"]+["{:.8f}".format(val) for val in _data["bias"]]]).T
        self._draw_table(table_ax, table_data)
        # _table = plt.table(cellText=table_data, cellLoc='center', loc='center', fontsize=[10,10,10])
        # for (row, col), cell in _table.get_celld().items():
        #     cell.set_linewidth(0.3)
        # plt.axis('off')

        ax = plt.subplot(2, 2, 2)
        harmonics = [2, 3, 4, 5]
        harmonic_data = [[(0, 0)]*len(self.list) for _ in range(len(harmonics))]
        for i in range(0, len(self.list)):
            if self.list[i] in self.bad_channel:
                self.logger.error(f"skip bad channel: {self.list[i]}")
                continue
            # Find harmonics of AC signal in FFT plot
            harmonic_coords = []
            # for h in harmonics:
            for k, h in enumerate(harmonics):
                harmonic_index = np.argmin(np.abs(_data["fft_freq"][i] - h * _data["peak_freq"][i]))
                harmonic_freq = _data["fft_freq"][i][harmonic_index]
                harmonic_dbv = _data["fft_dbv"][i][harmonic_index]
                harmonic_coords.append((harmonic_freq, harmonic_dbv))
                harmonic_data[k][i] = (harmonic_freq, harmonic_dbv)

            # Plot FFT of AC signal
            _line, = plt.plot(_data["fft_freq"][i], _data["fft_dbv"][i])
            channel_lines[self.list[i]].append(_line)
            if ax in self.channel_lines:
                self.channel_lines[ax].append(_line)
            else:
                self.channel_lines.update({ax: [_line]})

            _line, = plt.plot(_data["peak_freq"][i], _data["peak_dbv"][i], 'o',
                              color=self.adjust_color(channel_colors[self.list[i]]))
            channel_lines[self.list[i]].append(_line)

            _line = plt.axvline(float(_data["peak_freq"][i]), linestyle='--',
                               color=self.adjust_color(channel_colors[self.list[i]]))
            channel_lines[self.list[i]].append(_line)

            for k, h in enumerate(harmonics):
                _line, = plt.plot(harmonic_coords[k][0], harmonic_coords[k][1], 'x',
                                  color=self.adjust_color(channel_colors[self.list[i]]),
                                  label=f'Harmonic {h} ({harmonic_coords[k][0]:.2f},{harmonic_coords[k][1]:.2f})')
                channel_lines[self.list[i]].append(_line)

        plt.xlabel('Frequency (Hz)', fontsize=10)
        # plt.ylabel('Amplitude (dBV)', fontsize=10)
        plt.text(-0.05, 1.05, f"Amplitude (dBV)",
                fontsize=10, transform=plt.gca().transAxes)
        # plt.xlim(1, self.sample_rate/2)
        if len(self.fft_scale[0]):
            _start, _end = list(self.fft_scale[0])
            _end = self.sample_rate/2 if _end == -1 else _end
            plt.xlim(_start, _end)
        if len(self.fft_scale[1]):
            _start, _end = list(self.fft_scale[1])
            plt.ylim(_start, _end)
        table_ax = plt.subplot(2, 2, 4)
        # plt.rcParams.update({'font.size': 10})
        table_data = np.array([["Signal"]+self.list,
                               ["Peak"]+["({:.2f}, {:.2f})".format(val1, val2) for val1, val2 in
                                         zip(_data["peak_freq"], _data["peak_dbv"])],
                               ["Harmonic 2"]+["({:.2f}, {:.2f})".format(val1, val2) for val1, val2 in
                               harmonic_data[0]],
                               ["Harmonic 3"]+["({:.2f}, {:.2f})".format(val1, val2) for val1, val2 in
                                                 harmonic_data[1]],
                               ["Harmonic 4"] + ["({:.2f}, {:.2f})".format(val1, val2) for val1, val2 in
                                                 harmonic_data[2]],
                               ["Harmonic 5"] + ["({:.2f}, {:.2f})".format(val1, val2) for val1, val2 in
                                                 harmonic_data[3]],
                               ]).T
        self._draw_table(table_ax, table_data)
        # _table = plt.table(cellText=table_data, cellLoc='center', loc='center', fontsize=[10,10,10])
        # for (row, col), cell in _table.get_celld().items():
        #     cell.set_linewidth(0.3)
        # plt.axis('off')

        self.draw_checkbutton(plt, channel_lines, list(channel_colors.values()))

        # plt.tight_layout(rect=(0.1, 0.0, 0.9, 0.95))
        self.fig.canvas.mpl_connect('resize_event', self.update_text_size)
        _postfix = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        _png_file = f"{self.plot_name}_{_postfix}.png"
        plt.savefig(_png_file)
        if self.figure_canvas is not None and len(self.list):
            self.figure_canvas.show_plot()
        # if len(self.list):
        #     plt.show()
        # #plt.cla()
        # plt.clf()
        # plt.close("all")
        self.logger.info(f"finish: {self.sensor}")
        return ErrorCode.ERR_NO_ERROR

    def _convert_ppg_data(self):
        self.bad_channel = []
        keys = ["channel", "time", "sig", "avg", "noise", "sum_vector", "snr"]
        _data = {key: [] for key in keys}

        data = self.df_data
        self.bad_channel = []
        fs = self.sample_rate
        start = int(self.data_drop[0])
        end = int(self.data_drop[1])
        for channel in self.list:
            try:
                if end > 0:
                    _sig = data[channel].iloc[start:end]
                else:
                    _sig = data[channel].iloc[start:]
                _avg = abs(np.mean(_sig))
                _sig_ac = _sig - _avg
                _err_code, _sig_ac = self.do_high_pass_filter(_sig_ac)
                if _err_code != ErrorCode.ERR_NO_ERROR:
                    return _err_code, _data
                _err_code, _sig_ac = self.do_low_pass_filter(_sig_ac)
                if _err_code != ErrorCode.ERR_NO_ERROR:
                    return _err_code, _data
                _err_code, _sig_ac = self.do_high_pass_filter(_sig_ac, axis=-1)
                if _err_code != ErrorCode.ERR_NO_ERROR:
                    return _err_code, _data
                _noise = np.std(_sig_ac)
                _snr = 20 * math.log10(_avg / _noise)

                self.logger.debug(f"{_avg}, {_noise}, {_snr}")

                timex = np.linspace(0, len(_sig_ac) / fs, len(_sig_ac))
                sum_vector = np.array(_sig_ac)
                _data["channel"].append(channel)
                _data["avg"].append(_avg)
                _data["time"].append(timex)
                _data["sig"].append(_sig_ac)
                _data["sum_vector"].append(sum_vector)
                _data["noise"].append(_noise)
                _data["snr"].append(_snr)
            except Exception as ex:
                self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
                self.logger.error("this channel have problem:" + channel)
                self.bad_channel.append(channel)
                continue
        return ErrorCode.ERR_NO_ERROR, _data

    def ppg_data(self, *args, **kwargs):
        self.logger.info(f"process {self.sensor} data")
        _err_code, _data = self.do_data_conversion(_sensor="ppg")
        if _err_code != ErrorCode.ERR_NO_ERROR:
            return _err_code
        plt.clf()
        plt.close("all")
        self.fig = plt.figure(f"{self.plot_name}", figsize=(20, 10))
        self.fig.suptitle(self.sensor, fontsize=16)
        self.figsize = self.fig.get_size_inches()
        if self.figure_canvas is not None:
            self.figure_canvas.create_canvas(self.fig)
        # plt.subplots_adjust(hspace=0.6)
        plt.rcParams.update({'font.size': 10})
        self.fig.subplots(2, 2)
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        channel_lines = {key: [] for key in self.list}
        channel_colors = {}
        _shift = np.amax(_data["sig"]) - np.amin(_data["sig"])

        ax = plt.subplot(2, 2, 1)
        # plt.rcParams.update({'font.size': 10})
        # ax = axes[0][0]
        for i in range(0, len(self.list)):
            if self.list[i] in self.bad_channel:
                self.logger.error(f"skip bad channel: {self.list[i]}")
                continue
            try:
                plt.rcParams.update({'font.size': 10})
                _line, = plt.plot(_data["time"][i], _data["sig"][i]+i*_shift)
                if ax in self.channel_lines:
                    self.channel_lines[ax].append(_line)
                else:
                    self.channel_lines.update({ax: [_line]})
                channel_colors[self.list[i]] = _line.get_color()
            except Exception as ex:
                self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
                continue
        # ax.set_ylabel('Raw Cnt', fontsize=10)
        plt.text(-0.05, 1.05, f"Raw Cnt",
                 fontsize=10, transform=plt.gca().transAxes)
        plt.xlabel('Time (s)', fontsize=10)
        plt.yticks([_shift * i for i in np.arange(0, len(self.list))])
        ax.set_yticklabels(self.list, fontsize=10)

        ax = plt.subplot(2, 2, 2)
        for i in range(0, len(self.list)):
            if self.list[i] in self.bad_channel:
                self.logger.error(f"skip bad channel: {self.list[i]}")
                continue
            try:
                plt.rcParams.update({'font.size': 10})
                FFT = 2.0 / len(_data["sum_vector"][i]) * abs(scipy.fft.fft(_data["sum_vector"][i]))
                timex = _data["time"][i]
                freqs = scipy.fftpack.fftfreq(len(timex), timex[1] - timex[0])

                print(f"freq length:{len(freqs)}")
                _line, = plt.plot(freqs[1:int(len(freqs) / 2)], (FFT[1:int(len(freqs) / 2)]),
                                  color=channel_colors[self.list[i]])
                channel_lines[self.list[i]].append(_line)
                if ax in self.channel_lines:
                    self.channel_lines[ax].append(_line)
                else:
                    self.channel_lines.update({ax: [_line]})
                # Peak
                peak_index = np.argmax(FFT[1:int(len(freqs) / 2)])
                _line, = plt.plot(freqs[1:int(len(freqs) / 2)][peak_index],
                         FFT[1:int(len(freqs) / 2)][peak_index], 'o', color="#ff0000")
                channel_lines[self.list[i]].append(_line)
                _line = plt.axvline(freqs[1:int(len(freqs) / 2)][peak_index], color="#ff0000", linestyle='--')
                channel_lines[self.list[i]].append(_line)
            except Exception as ex:
                self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
                continue
        # plt.ylabel('FFT[cnt/sqrt(Hz)]', fontsize=10)
        plt.text(-0.05, 1.05, f"FFT[cnt/sqrt(Hz)]",
                 fontsize=10, transform=plt.gca().transAxes)
        plt.xlabel('Frequency [Hz]', fontsize=10)
        if len(self.fft_scale[0]):
            _x_start, _x_end = list(self.fft_scale[0])
            _x_end = self.sample_rate / 2 if _x_end == -1 else _x_end
            plt.xlim(_x_start, _x_end)

        if len(self.fft_scale[1]):
            _y_start, _y_end = list(self.fft_scale[1])
            plt.ylim(_y_start, _y_end)
        # plt.xlim([0.1, fs / 2])
        # plt.ylim([-0.1, 5])

        table_ax = plt.subplot(2, 2, 3)
        # plt.rcParams.update({'font.size': 10})
        table_data = np.array(
            [["Signal"] + self.list,
             ["Average"] + ["{:.8f}".format(val) for val in _data["avg"]],
             ["Noise"] + ["{:.8f}".format(val) for val in _data["noise"]],
             ["SNR"] + ["{:.8f}".format(val) for val in _data["snr"]]
             ]).T
        self._draw_table(table_ax, table_data)
        # table = plt.table(cellText=table_data, cellLoc='center', loc='center', fontsize=[10,10,10])
        # # table.auto_set_font_size(False)
        # table.scale(1, 2.5)
        # for (row, col), cell in table.get_celld().items():
        #     cell.set_linewidth(0.3)
        # plt.axis('off')

        plt.subplot(2, 2, 4)
        plt.axis('off')
        self.draw_checkbutton(plt, channel_lines, list(channel_colors.values()))
        self.fig.canvas.mpl_connect('resize_event', self.update_text_size)
        _postfix = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        _png_file = f"{self.plot_name}_{_postfix}.png"
        # plt.tight_layout(rect=[0, 0, 1, 1])
        plt.savefig(_png_file)
        if self.figure_canvas is not None and len(self.list):
            self.figure_canvas.show_plot()
        # plt.show()
        # # plt.cla()
        # plt.clf()
        # plt.close("all")
        self.logger.info(f"finish: {self.sensor}")
        return ErrorCode.ERR_NO_ERROR

    def imu_data(self):
        try:
            self.logger.info(f"process {self.sensor} data")
            _err_code, _data = self.do_data_conversion()
            if _err_code != ErrorCode.ERR_NO_ERROR:
                return _err_code
            _err_code = self.do_plot_list(_data)
            self.logger.info(f"finish: {self.sensor}, {_err_code}")
            return _err_code
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_UNKNOWN

    def alt_data(self):
        try:
            self.logger.info(f"process {self.sensor} data")
            _err_code, _data = self.do_data_conversion()
            if _err_code != ErrorCode.ERR_NO_ERROR:
                return _err_code
            _err_code = self.do_plot_list(_data)
            self.logger.info(f"finish: {self.sensor}, {_err_code}")
            return _err_code
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_UNKNOWN

    def compass_data(self):
        try:
            self.logger.info(f"process {self.sensor} data")
            _err_code, _data = self.do_data_conversion()
            if _err_code != ErrorCode.ERR_NO_ERROR:
                return _err_code
            _err_code = self.do_plot_list(_data)
            self.logger.info(f"finish: {self.sensor}, {_err_code}")
            return _err_code
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_UNKNOWN

    def bti_data(self):
        try:
            self.logger.info(f"process {self.sensor} data")
            _err_code, _data = self.do_data_conversion()
            if _err_code != ErrorCode.ERR_NO_ERROR:
                return _err_code
            _err_code = self.do_plot_list(_data)
            self.logger.info(f"finish: {self.sensor}, {_err_code}")
            return _err_code
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_UNKNOWN

    def update_text_size(self, event):
        newsize = self.fig.get_size_inches()
        rate = min(newsize[0]/self.figsize[0], newsize[1]/self.figsize[1])
        self.logger.debug(f"fig size, now: {newsize}, old: {self.figsize}")
        for ax in self.fig.axes:
            for text in ax.texts:
                # fontsize = text.get_fontsize()
                text.set_fontsize(10*rate)
            for child in ax.get_children():
                if isinstance(child, matplotlib.table.Table):
                    child.set_fontsize(8*rate)
            ax.xaxis.label.set_fontsize(10*rate)
            ax.yaxis.label.set_fontsize(10 * rate)
            ax.tick_params(axis='x', labelsize=8*rate)
            ax.tick_params(axis='y', labelsize=8*rate)
        self.fig.canvas.draw()
