# -*- coding: UTF-8 -*-
import numpy as np
import pandas as pd
import scipy.fftpack
from scipy import signal, stats
from scipy.signal import butter, lfilter, filtfilt
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.table import Table
from matplotlib.widgets import CheckButtons
import matplotlib.patches as patches
import matplotlib.ticker as ticker
from matplotlib.gridspec import GridSpec
import re
import math
import logging
from enum import IntEnum
import time
import os
import copy
import datetime


class ErrorCode(IntEnum):
    ERR_NO_ERROR = 0,
    ERR_BAD_FILE = -1,
    ERR_BAD_DATA = -2,
    ERR_BAD_TYPE = -3,
    ERR_BAD_ARGS = -4,
    ERR_BAD_UNKNOWN = -255,


class VisualizeParameters:
    def __init__(self):
        self.project = "malibu"
        self.sensor = None
        self.data_type = None
        self.sample_rate = 1
        self.data_drop = [0, -1]
        self.data_file = None
        self.df_data = None
        self.selected_columns = list()
        self.high_pass_filter = {"type": '', "order": 0, "freq": 0}
        self.low_pass_filter = {"type": '', "order": 0, "freq": 0}
        self.notch_filter = dict() # {"1": {"freq": 0, "qvalue": 0}, ...} #  [[0, 0], [0, 0], [0, 0]]
        self.fft_scale = dict()  # {"x": {"start": 0, "end": 0}, "y": {"start": 0, "end": 0}}
        self.summary_scale = dict()  # {"x": {"start": 0, "end": 0}, "y": {"start": 0, "end": 0}}
        self.plot_name = None
        self.show = True
        self.gain = 1.0

        self.canvas = None


class DataVisualization:
    def __init__(self, **kwargs):
        self.parameters = VisualizeParameters()
        self.logger = kwargs["logger"] if 'logger' in kwargs and kwargs["logger"] is not None else logging.getLogger()
        # self.figure_canvas = kwargs['canvas'] if 'canvas' in kwargs else None

        self.process_func = {
            "emg": self.visualize_emg_data,
            "ppg": self.visualize_ppg_data,
            "imu": self.visualize_imu_data,
            "alt": self.visualize_alt_data,
            "mag": self.visualize_mag_data,
            "bti": self.visualize_bti_data,
            "others": self.visualize_other_data,
        }

        self.bad_channel = list()
        self.target_channels = list()
        self.target_data = dict()
        self.main_lines = dict()  # save {ax:[lines]) for click event on the line
        self.all_lines = dict()  # for legend checkbox click event
        self.line_colors = dict()
        self.harmonic_data = None
        self.markers = list()
        self.check_btn = list()
        self.markers = list()
        self.fig = None
        self.figsize = None
        self.txt_fontsize = 10
        self.legend_rows = 16

    def visualize_data(self, params: VisualizeParameters):
        self.parameters = params
        self.bad_channel = list()
        self.target_channels = list()
        self.main_lines = dict()  # save {ax:[lines]) for click event on the line
        self.all_lines = dict()  # for legend checkbox click event
        self.line_colors = dict()
        self.harmonic_data = None
        self.markers = list()
        self.check_btn = list()
        self.markers = list()
        self.fig = None
        self.figsize = None

        if self.parameters.plot_name is None or not len(self.parameters.plot_name.strip()):
            self.parameters.plot_name = self.parameters.sensor

        if self.parameters.data_file is not None:
            try:
                self.parameters.df_data = pd.read_csv(self.parameters.data_file)
            except Exception as ex:
                self.logger.error(f"Exception: {str(ex)}")
                return ErrorCode.ERR_BAD_FILE

        if self.parameters.df_data is None:
            return ErrorCode.ERR_BAD_DATA

        return self.process_func[self.parameters.sensor.lower()]()

    def initialize_figure(self, rows: int = 2, cols: int = 2) -> ErrorCode:
        try:
            self.logger.debug("initialize figure")
            matplotlib.rcdefaults()
            plt.clf()
            plt.close("all")
            self.fig = plt.figure(f"{self.parameters.plot_name}", figsize=(20, 10))
            reserve_space = math.ceil(
                len(self.parameters.selected_columns) / self.legend_rows) * 0.1  # reserve space for legend
            plt.subplots_adjust(hspace=0.3, left=0.05, right=1 - reserve_space)
            self.fig.suptitle(self.parameters.plot_name, fontsize=16,
                              x=0.05 + (1 - reserve_space - 0.05) / 2)  # centralize title
            self.figsize = self.fig.get_size_inches()
            # if self.figure_canvas is not None and self.parameters.show:
            #     self.figure_canvas.create_canvas(self.fig)
            # plt.subplots_adjust(hspace=0.3)
            plt.rcParams['axes.prop_cycle'] = plt.cycler('color', plt.cm.tab20(np.linspace(0, 1, 20)))
            self.fig.subplots(rows, cols)
            self.fig.canvas.mpl_connect('button_press_event', self.on_legend_click)
            self.fig.canvas.mpl_connect('resize_event', self.update_text_size)
            return ErrorCode.ERR_NO_ERROR
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_UNKNOWN

    def draw_time_domain_chart(self, layout: dict, y_text: str = "", overlap: bool = False) -> ErrorCode:
        try:
            self.logger.debug("draw time domain chart ...")
            ax = plt.subplot(layout["rows"], layout["cols"], layout["index"])
            plt.rcParams.update({'font.size': self.txt_fontsize})
            # ax = axes[0][0]
            self.all_lines = {key: [] for key in self.target_channels}
            self.line_colors = {}
            if not overlap:
                _shift = np.amax(self.target_data["sig"]) - np.amin(self.target_data["sig"])
            else:
                _shift = 0
            # print(_shift)
            for i in range(0, len(self.target_channels)):
                plt.rcParams.update({'font.size': self.txt_fontsize})
                _line, = plt.plot(self.target_data["time"][i], self.target_data["sig"][i] + i * _shift,
                                  linewidth=0.5, alpha=0.7)
                if overlap:
                    self.all_lines[self.target_channels[i]].append(_line)
                self.line_colors[self.target_channels[i]] = _line.get_color()
                if ax in self.main_lines:
                    self.main_lines[ax].append(_line)
                else:
                    self.main_lines.update({ax: [_line]})

            plt.text(-0.05, 1.05, y_text, fontsize=self.txt_fontsize, transform=plt.gca().transAxes)
            plt.xlabel('Time (S)', fontsize=self.txt_fontsize)
            if not overlap:
                plt.yticks([_shift * i for i in np.arange(0, len(self.target_channels))])
                ax.set_yticklabels(self.target_channels)
            return ErrorCode.ERR_NO_ERROR
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_UNKNOWN

    def draw_freq_domain_chart(self, layout: dict, y_text: str = "", stype: str = "fft") -> ErrorCode:
        try:
            self.logger.debug("draw frequency domain chart ...")
            ax = plt.subplot(layout["rows"], layout["cols"], layout["index"])
            harmonics = [2, 3, 4, 5]
            self.harmonic_data = [[(0, 0)] * len(self.target_channels) for _ in range(len(harmonics))]
            for i in range(0, len(self.target_channels)):
                # Find harmonics of AC signal in FFT plot
                for k, h in enumerate(harmonics):
                    harmonic_index = np.argmin(np.abs(self.target_data["target_freq"][i] - h * self.target_data["target_freq_peak"][i]))
                    harmonic_freq = self.target_data["target_freq"][i][harmonic_index]
                    harmonic_sig = self.target_data["target_sig"][i][harmonic_index]
                    # harmonic_coords.append((harmonic_freq, harmonic_dbv))
                    self.harmonic_data[k][i] = (harmonic_freq, harmonic_sig)

                if stype == "psd":
                    # Plot FFT of AC signal
                    _line, = plt.semilogy(self.target_data["target_freq"][i], self.target_data["target_sig"][i], linewidth=0.5, alpha=0.7)
                else:
                    # Plot FFT of AC signal
                    _line, = plt.plot(self.target_data["target_freq"][i],
                                      self.target_data["target_sig"][i], linewidth=0.5, alpha=0.7)
                self.all_lines[self.target_channels[i]].append(_line)
                if ax in self.main_lines:
                    self.main_lines[ax].append(_line)
                else:
                    self.main_lines.update({ax: [_line]})

                _line, = plt.plot(self.target_data["target_freq_peak"][i],
                                  self.target_data["target_sig_peak"][i], 'o',
                                  color=self.line_colors[self.target_channels[i]],
                                  linewidth=0.5, alpha=0.9)
                self.all_lines[self.target_channels[i]].append(_line)

                _line = plt.axvline(float(self.target_data["target_freq_peak"][i]), linestyle='--',
                                    color=self.line_colors[self.target_channels[i]],
                                    linewidth=0.5, alpha=0.9)
                self.all_lines[self.target_channels[i]].append(_line)

                for k, h in enumerate(harmonics):
                    _line, = plt.plot(self.harmonic_data[k][i][0], self.harmonic_data[k][i][1], 'x',
                                      color=self.line_colors[self.target_channels[i]],
                                      label=f'Harmonic {h} ({self.harmonic_data[k][i][0]:.2f},'
                                            f'{self.harmonic_data[k][i][1]:.2f})',
                                      linewidth=0.5, alpha=0.9)
                    self.all_lines[self.target_channels[i]].append(_line)

            plt.xlabel('Frequency (Hz)', fontsize=self.txt_fontsize)
            # plt.ylabel('Amplitude (dBV)', fontsize=10)
            plt.text(-0.05, 1.05, y_text, fontsize=self.txt_fontsize, transform=plt.gca().transAxes)
            self.scale_fft_axis()
            return ErrorCode.ERR_NO_ERROR
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_UNKNOWN

    def draw_statistics_table(self, layout: dict) -> (ErrorCode, np.array):
        try:
            self.logger.debug("draw statistics table chart ...")
            table_ax = plt.subplot(layout["rows"], layout["cols"], layout["index"])
            # plt.rcParams.update({'font.size': 10})
            table_data = np.array(
                [["Signal"] + self.target_channels,
                 ["RMS Level(V)"] + ["{:.8f}".format(val) for val in self.target_data["total_rms"]],
                 ["Average Peak-to-Peak"] + ["{:.8f}".format(val) for val in self.target_data["avg_p2p"]],
                 ["DC bias"] + ["{:.8f}".format(val) for val in self.target_data["bias"]]]).T
            self._draw_table(table_ax, table_data)
            return ErrorCode.ERR_NO_ERROR, table_data
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_UNKNOWN, None

    def draw_harmonics_table(self, layout: dict, stype: str = "fft") -> (ErrorCode, np.array):
        try:
            self.logger.debug("draw harmonics table chart ...")
            table_ax = plt.subplot(layout["rows"], layout["cols"], layout["index"])
            # plt.rcParams.update({'font.size': 10})

            data_array = [["Signal"] + self.target_channels,
                                    ["Peak"] + ["({:.2f}, {:.2f})".format(val1, val2) for val1, val2 in
                                                zip(self.target_data["target_freq_peak"],
                                                    self.target_data["target_sig_peak"])],
                                    ["Harmonic 2"] + ["({:.2f}, {:.2f})".format(val1, val2) for val1, val2 in
                                                      self.harmonic_data[0]],
                                    ["Harmonic 3"] + ["({:.2f}, {:.2f})".format(val1, val2) for val1, val2 in
                                                      self.harmonic_data[1]],
                                    ["Harmonic 4"] + ["({:.2f}, {:.2f})".format(val1, val2) for val1, val2 in
                                                      self.harmonic_data[2]],
                                    ["Harmonic 5"] + ["({:.2f}, {:.2f})".format(val1, val2) for val1, val2 in
                                                      self.harmonic_data[3]],
                                    ]
            if stype == "psd":
                thd_power = [0.0 for _ in range(0, len(self.target_channels))]
                thd = [0.0 for _ in range(0, len(self.target_channels))]
                for i in range(len(self.target_channels)):
                    for j in range(4):
                        thd_power[i] += self.harmonic_data[j][i][1]
                    thd[i] = np.sqrt(thd_power[i]) / np.sqrt(self.target_data["target_sig_peak"][i]) \
                        if self.target_data["target_sig_peak"][i] > 0 else 0.0
                thd_array = ["THD(%)"] + [f"{float(val) * 100:.2f}" for val in thd]
                data_array.append(thd_array)
            table_data = np.array(data_array).T
            self._draw_table(table_ax, table_data)
            return ErrorCode.ERR_NO_ERROR, table_data
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_UNKNOWN, None

    def save_statistic_and_picture(self, t1: np.array = None, t2: np.array = None) -> ErrorCode:
        try:
            df = pd.DataFrame(t1[1:], columns=t1[0]) if t1 is not None else None
            df1 = pd.DataFrame(t2[1:], columns=t2[0]) if t2 is not None else None
            if df is not None and df1 is not None:
                df = pd.concat([df, df1[df1.columns[1:]]], axis=1)
            elif df1 is not None:
                df = df1
            _postfix = time.strftime("%Y%m%d_%H%M%S", time.localtime())
            # _png_file = f"{self.parameters.plot_name}_{_postfix}.png"
            _png_file = os.path.join(self.logger.log_path, f"{self.parameters.plot_name}_{_postfix}.png")
            if df is not None:
                df.to_csv(os.path.join(self.logger.log_path, f"{self.parameters.plot_name}_{_postfix}.csv"), index=False)
                self.logger.debug(
                    f"save data to: {self.parameters.plot_name}_{_postfix}.csv")
            plt.savefig(_png_file)
            self.logger.debug(f"save picture to: {self.parameters.plot_name}_{_postfix}.png")
            return ErrorCode.ERR_NO_ERROR
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_UNKNOWN

    def visualize_emg_data(self):
        try:
            self.logger.info(f"malibu_emg_data: process {self.parameters.sensor} data")
            # ToDo:: need to review which columns needed
            if not len(self.parameters.selected_columns):
                tmp = self.parameters.df_data.columns.dropna().tolist()
                self.parameters.selected_columns = [val for val in tmp if val.lower() not in ["timestamp"]]
            _err_code, self.target_data = self.calculate_emg_data()
            if _err_code != ErrorCode.ERR_NO_ERROR:
                return _err_code
            # 1. init figure
            if self.initialize_figure(2, 2) != ErrorCode.ERR_NO_ERROR:
                return ErrorCode.ERR_BAD_UNKNOWN
            # 2. Time domain
            if self.draw_time_domain_chart({"rows": 2, "cols": 2, "index": 1},
                                           "Signal (V)", False) != ErrorCode.ERR_NO_ERROR:
                return ErrorCode.ERR_BAD_UNKNOWN
            # 3. statistics table
            _err_code, table_data = self.draw_statistics_table({"rows": 2, "cols": 2, "index": 3})
            if _err_code != ErrorCode.ERR_NO_ERROR:
                return ErrorCode.ERR_BAD_UNKNOWN
            # 4. frequency domain
            if self.draw_freq_domain_chart({"rows": 2, "cols": 2, "index": 2},
                                           "Amplitude (dBV)") != ErrorCode.ERR_NO_ERROR:
                return ErrorCode.ERR_BAD_UNKNOWN
            # 5. harmonics table
            _err_code, table_data1 = self.draw_harmonics_table({"rows": 2, "cols": 2, "index": 4})
            if _err_code != ErrorCode.ERR_NO_ERROR:
                return _err_code
            # 6. legend
            if self.draw_checkbutton_2(plt, self.all_lines, list(self.line_colors.values())) != ErrorCode.ERR_NO_ERROR:
                return ErrorCode.ERR_BAD_UNKNOWN
            # self.fig.canvas.mpl_connect('resize_event', self.update_text_size)
            # 7. save to file
            self.save_statistic_and_picture(table_data, table_data1)

            self.logger.info(f"finish: {self.parameters.sensor}")
            return ErrorCode.ERR_NO_ERROR
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_UNKNOWN

    def visualize_ppg_data(self):
        try:
            self.logger.info(f"process {self.parameters.sensor} data")
            # ToDo:: need to review which columns needed
            if not len(self.parameters.selected_columns):
                tmp = self.parameters.df_data.columns.dropna().tolist()
                self.parameters.selected_columns = [val for val in tmp if "timestamp" not in val.lower()]
            self.convert_emg_adc_data()
            _err_code, self.target_data = self.calculate_ppg_data()
            if _err_code != ErrorCode.ERR_NO_ERROR:
                return _err_code
            # 1. init figure
            if self.initialize_figure(2, 2) != ErrorCode.ERR_NO_ERROR:
                return ErrorCode.ERR_BAD_UNKNOWN

            # 2. Time domain
            if self.draw_time_domain_chart({"rows": 2, "cols": 2, "index": 1},
                                           "Raw Cnt", False) != ErrorCode.ERR_NO_ERROR:
                return ErrorCode.ERR_BAD_UNKNOWN

            # 3. Freq domain
            ax = plt.subplot(2, 2, 2)
            for i in range(0, len(self.target_channels)):
                try:
                    plt.rcParams.update({'font.size': 10})
                    FFT = 2.0 / len(self.target_data["sum_vector"][i]) * abs(scipy.fft.fft(self.target_data["sum_vector"][i]))
                    timex = self.target_data["time"][i]
                    freqs = scipy.fftpack.fftfreq(len(timex), timex[1] - timex[0])

                    print(f"freq length:{len(freqs)}")
                    _line, = plt.plot(freqs[1:int(len(freqs) / 2)], (FFT[1:int(len(freqs) / 2)]),
                                      color=self.line_colors[self.target_channels[i]],
                                      linewidth=0.5, alpha=0.7)
                    self.all_lines[self.target_channels[i]].append(_line)
                    if ax in self.main_lines:
                        self.main_lines[ax].append(_line)
                    else:
                        self.main_lines.update({ax: [_line]})
                    # Peak
                    peak_index = np.argmax(FFT[1:int(len(freqs) / 2)])
                    _line, = plt.plot(freqs[1:int(len(freqs) / 2)][peak_index],
                                      FFT[1:int(len(freqs) / 2)][peak_index], 'o', color="#ff0000")
                    self.all_lines[self.target_channels[i]].append(_line)
                    _line = plt.axvline(freqs[1:int(len(freqs) / 2)][peak_index], color="#ff0000", linestyle='--')
                    self.all_lines[self.target_channels[i]].append(_line)
                except Exception as ex:
                    self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
                    continue
            # plt.ylabel('FFT[cnt/sqrt(Hz)]', fontsize=10)
            plt.text(-0.05, 1.05, f"FFT[cnt/sqrt(Hz)]",
                     fontsize=10, transform=plt.gca().transAxes)
            plt.xlabel('Frequency [Hz]', fontsize=10)
            self.scale_fft_axis()

            # if self.draw_freq_domain_chart({"rows": 2, "cols": 2, "index": 2},
            #                                "FFT[cnt/sqrt(Hz)]") != ErrorCode.ERR_NO_ERROR:
            #     return ErrorCode.ERR_BAD_UNKNOWN
            # 4. statistics table
            table_ax = plt.subplot(2, 2, 3)
            # plt.rcParams.update({'font.size': 10})
            table_data = np.array(
                [["Signal"] + self.target_channels,
                 ["Average"] + ["{:.8f}".format(val) for val in self.target_data["avg"]],
                 ["Noise"] + ["{:.8f}".format(val) for val in self.target_data["noise"]],
                 ["SNR"] + ["{:.8f}".format(val) for val in self.target_data["snr"]]
                 ]).T
            self._draw_table(table_ax, table_data)
            df = pd.DataFrame(table_data)
            # 5. blank
            plt.subplot(2, 2, 4)
            plt.axis('off')
            self.draw_checkbutton(plt, self.all_lines, list(self.line_colors.values()))
            # self.fig.canvas.mpl_connect('resize_event', self.update_text_size)

            self.save_statistic_and_picture(table_data)

            self.logger.info(f"finish: {self.parameters.sensor}")
            return ErrorCode.ERR_NO_ERROR
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_UNKNOWN

    def visualize_imu_data(self):
        return self.visualize_other_data()

    def visualize_alt_data(self):
        return self.visualize_other_data()

    def visualize_mag_data(self):
        return self.visualize_other_data()

    def visualize_bti_data(self):
        return self.visualize_other_data()

    def visualize_other_data(self):
        try:
            self.logger.info(f"process {self.parameters.sensor} data")
            # ToDo:: need to review which columns needed
            if not len(self.parameters.selected_columns):
                tmp = self.parameters.df_data.columns.dropna().tolist()
                self.parameters.selected_columns = [val for val in tmp if val.lower() not in ["timestamp"]]
            _err_code, _data = self.calculate_imu_data()
            if _err_code != ErrorCode.ERR_NO_ERROR:
                return _err_code
            _err_code = self.do_plot_list(_data)
            self.logger.info(f"finish: {self.parameters.sensor}, {_err_code}")
            return _err_code
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_UNKNOWN

    def convert_emg_adc_data(self) -> pd.DataFrame:
        # covert adc code to voltage
        self.parameters.df_data = self.parameters.df_data.div(self.parameters.gain)
        return self.parameters.df_data

    def convert_ppg_adc_data(self) -> pd.DataFrame:
        self.parameters.df_data = self.parameters.df_data.div(self.parameters.gain)
        return self.parameters.df_data

    def convert_imu_adc_data(self) -> pd.DataFrame:
        self.parameters.df_data = self.parameters.df_data.div(self.parameters.gain)
        return self.parameters.df_data

    def convert_mag_adc_data(self) -> pd.DataFrame:
        self.parameters.df_data = self.parameters.df_data.div(self.parameters.gain)
        return self.parameters.df_data

    def convert_bti_adc_data(self) -> pd.DataFrame:
        self.parameters.df_data = self.parameters.df_data.div(self.parameters.gain)
        return self.parameters.df_data

    def convert_alt_adc_data(self) -> pd.DataFrame:
        self.parameters.df_data = self.parameters.df_data.div(self.parameters.gain)
        return self.parameters.df_data

    def convert_als_adc_data(self) -> pd.DataFrame:
        self.parameters.df_data = self.parameters.df_data.div(self.parameters.gain)
        return self.parameters.df_data

    def calculate_emg_data(self):
        self.bad_channel = list()
        keys = ["channel", "time", "sig", "total_rms", "avg_p2p", "cycle", "cycle_time",
                "max", "min", "target_freq", "target_freq_peak", "target_sig", "target_sig_peak", "bias", "target_rms"]
        _data = {key: [] for key in keys}

        self.convert_emg_adc_data()
        drops = self.parameters.data_drop
        for channel in self.parameters.selected_columns:
            if int(drops[1]) > 0:
                voltage = self.parameters.df_data[channel].iloc[int(drops[0]):int(drops[1])]
            else:
                voltage = self.parameters.df_data[channel].iloc[int(drops[0]):]
            dc_bias = np.mean(voltage)
            # Remove DC bias from waveform
            ac_signal = voltage - dc_bias
            _err_code, ac_signal = self.filter_signals(ac_signal)
            if _err_code != ErrorCode.ERR_NO_ERROR:
                return _err_code, _data
            # Create time axis
            time = np.arange(len(voltage)) / self.parameters.sample_rate
            # Calculate FFT of AC signal
            if len(ac_signal) == 0:
                self.logger.error(f"bad channel data: {channel}")
                self.bad_channel.append(channel)
                continue
            target_size = 2 ** int(np.ceil(np.log2(len(ac_signal))))
            target_freq = np.fft.rfftfreq(target_size, d=1 / self.parameters.sample_rate)
            _amplitude = np.abs(np.fft.rfft(ac_signal, target_size))
            target_sig = 20 * np.log10(_amplitude / 1)  # Convert to dBV

            # Find peak value of AC signal in FFT plot
            peak_index = np.argmax(_amplitude)
            target_freq_peak = target_freq[peak_index]
            target_sig_peak = target_sig[peak_index]
            # ac_peak_coord = (ac_peak_freq, ac_peak_dbv)
            self.logger.info(f"peak:{target_freq_peak},{target_sig_peak}")
            # Find cycle time and max/min values in each cycle
            cycle_time = 1 / target_freq_peak
            num_cycles = int(len(ac_signal) / (cycle_time * self.parameters.sample_rate))
            max_vals = np.zeros(num_cycles)
            min_vals = np.zeros(num_cycles)
            for i in range(num_cycles):
                cycle_start = int(i * cycle_time * self.parameters.sample_rate)
                cycle_end = int((i + 1) * cycle_time * self.parameters.sample_rate)
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
            _data["total_rms"].append(rms_val)
            _data["avg_p2p"].append(avg_peak_to_peak_val)
            _data["cycle"].append(num_cycles)
            _data["cycle_time"].append(cycle_time)
            _data["max"].append(max_vals)
            _data["min"].append(min_vals)
            _data["target_freq"].append(target_freq)
            _data["target_freq_peak"].append(target_freq_peak)
            _data["target_sig"].append(target_sig)
            _data["target_sig_peak"].append(target_sig_peak)
            _data["bias"].append(dc_bias)
            self.target_channels = copy.deepcopy(_data["channel"])
        return ErrorCode.ERR_NO_ERROR, _data

    def calculate_ppg_data(self):
        return self.calculate_other_sensors_data(True)
        # self.bad_channel = []
        # keys = ["channel", "time", "sig", "avg", "noise", "sum_vector", "snr"]
        # _data = {key: [] for key in keys}
        #
        # data = self.parameters.df_data
        # self.bad_channel = []
        # fs = self.parameters.sample_rate
        # start = int(self.parameters.data_drop[0])
        # end = int(self.parameters.data_drop[1])
        # for channel in self.parameters.selected_columns:
        #     try:
        #         if end > 0:
        #             _sig = data[channel].iloc[start:end]
        #         else:
        #             _sig = data[channel].iloc[start:]
        #         _avg = abs(np.mean(_sig))
        #         _sig_ac = _sig - _avg
        #         _err_code, _sig_ac = self.filter_signals(_sig_ac)
        #         if _err_code != ErrorCode.ERR_NO_ERROR:
        #             return _err_code, _data
        #         _noise = np.std(_sig_ac)
        #         _snr = 20 * math.log10(_avg / _noise)
        #
        #         self.logger.debug(f"{_avg}, {_noise}, {_snr}")
        #
        #         timex = np.linspace(0, len(_sig_ac) / fs, len(_sig_ac))
        #         sum_vector = np.array(_sig_ac)
        #         _data["channel"].append(channel)
        #         _data["avg"].append(_avg)
        #         _data["time"].append(timex)
        #         _data["sig"].append(_sig_ac)
        #         _data["sum_vector"].append(sum_vector)
        #         _data["noise"].append(_noise)
        #         _data["snr"].append(_snr)
        #         self.target_channels = copy.deepcopy(_data["channel"])
        #     except Exception as ex:
        #         self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
        #         self.logger.error("this channel have problem:" + channel)
        #         self.bad_channel.append(channel)
        #         continue
        # return ErrorCode.ERR_NO_ERROR, _data

    def calculate_imu_data(self):
        return self.calculate_other_sensors_data()

    def calculate_alt_data(self):
        return self.calculate_other_sensors_data()

    def calculate_mag_data(self):
        return self.calculate_other_sensors_data()

    def calculate_bti_data(self):
        return self.calculate_other_sensors_data()

    def calculate_als_data(self):
        return self.calculate_other_sensors_data()

    def calculate_other_sensors_data(self, b_snr=False):
        keys = ["channel", "avg", "sig", "noise", "time", "sum_vector", "snr"]
        _data = {key: [] for key in keys}
        self.bad_channel = []
        drops = self.parameters.data_drop
        for channel in self.parameters.selected_columns:
            try:
                if int(self.parameters.data_drop[1]) > 0:
                    _sig = self.parameters.df_data[channel].iloc[int(drops[0]):int(drops[1])]
                else:
                    _sig = self.parameters.df_data[channel].iloc[int(drops[0]):]
                avg = np.mean(_sig)
                _sig_ac = _sig - avg
                _err_code, _sig_ac = self.filter_signals(_sig_ac)
                if _err_code != ErrorCode.ERR_NO_ERROR:
                    return _err_code, _data

                noise = np.std(_sig_ac)

                self.logger.debug(f"{avg}, {noise}")
                timex = np.linspace(0, len(_sig_ac) / self.parameters.sample_rate, len(_sig_ac))
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
                self.target_channels = copy.deepcopy(_data["channel"])
            except Exception as ex:
                self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
                self.logger.error(f"this channel have problem: {channel}")
                self.bad_channel.append(channel)
                continue
        return ErrorCode.ERR_NO_ERROR, _data

    def scale_fft_axis(self):
        try:
            if self.parameters.fft_scale is not None:
                if "x" in self.parameters.fft_scale and self.parameters.fft_scale["x"] is not None:
                    _end = self.parameters.fft_scale["x"]["end"]
                    _end = self.parameters.sample_rate / 2 if _end == -1 else _end
                    plt.xlim(self.parameters.fft_scale["x"]["start"], _end)
                if "y" in self.parameters.fft_scale and self.parameters.fft_scale["y"] is not None:
                    plt.ylim(self.parameters.fft_scale["y"]["start"], self.parameters.fft_scale["y"]["end"])
            else:
                self.logger.debug("fft scale is None, do nothing!")
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")

    def do_fft(self, _sig):
        try:
            if len(_sig) == 0:
                self.logger.error(f"signal is empty!!")
                return ErrorCode.ERR_BAD_DATA, [], [], []
            else:
                fft_size = 2 ** int(np.ceil(np.log2(len(_sig))))
                fft_freq = np.fft.rfftfreq(fft_size, d=1 / self.parameters.sample_rate)
                fft_amplitude = np.abs(np.fft.rfft(_sig, fft_size))
                fft_dbv = 20 * np.log10(fft_amplitude / 1)  # Convert to dBV
            return ErrorCode.ERR_BAD_ARGS, fft_freq, fft_amplitude, fft_dbv
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_UNKNOWN, [], [], []

    def filter_signals(self, _sig: pd.DataFrame) -> (int, pd.DataFrame):
        new_sig = copy.deepcopy(_sig)
        _err_code, new_sig = self.do_high_pass_filter(new_sig)
        if _err_code != ErrorCode.ERR_NO_ERROR:
            return _err_code, _sig
        _err_code, new_sig = self.do_low_pass_filter(new_sig)
        if _err_code != ErrorCode.ERR_NO_ERROR:
            return _err_code, _sig
        _err_code, new_sig = self.do_notch_filter(new_sig)
        if _err_code != ErrorCode.ERR_NO_ERROR:
            return _err_code, _sig

        return _err_code, new_sig

    def do_notch_filter(self, _sig):
        try:
            if self.parameters.notch_filter is None or not len(self.parameters.notch_filter):
                self.logger.info(f"notch filer parameter is empty, do nothing")
                return
            self.logger.info(f"do_notch_filter")
            _new_sig = _sig
            for idx, f in self.parameters.notch_filter.items():
                self.logger.debug(f"notch parameters: {idx}, {f}")
                if f is not None and f != {"freq": 0, "qvalue": 0}:
                    self.logger.info(f"notch parameters: {f}")
                    try:
                        b1, a1 = signal.iirnotch(w0=float(f['freq']), Q=float(f['qvalue']),
                                                 fs=self.parameters.sample_rate)
                    except Exception as ex:
                        self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
                        return ErrorCode.ERR_BAD_ARGS, _sig
                    _new_sig = signal.lfilter(b1, a1, _new_sig)
            return ErrorCode.ERR_NO_ERROR, _new_sig
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_UNKNOWN, _sig

    def do_high_pass_filter(self, sig_list, axis=-1):
        try:
            self.logger.info(f"do_high_pass_filter ...")
            if self.parameters.high_pass_filter is None or self.parameters.high_pass_filter["type"] == "":
                self.logger.info(f"bad high pass filter parameters, do nothing!")
                return ErrorCode.ERR_NO_ERROR, sig_list
            order = int(self.parameters.high_pass_filter["order"])
            freq1 = float(self.parameters.high_pass_filter["freq"])
            sig = np.asarray(sig_list, dtype=np.float32)
            sig = sig - sig[0]
            nyq = 0.5 * self.parameters.sample_rate  # Nyquist frequency
            high = freq1 / nyq
            b, a = butter(order, high, btype='high')
            # apply filter
            if self.parameters.high_pass_filter["type"] == 'lfilter':
                sig_filt = lfilter(b, a, sig, axis=axis)
            elif self.parameters.high_pass_filter["type"] == 'filtfilt':
                sig_filt = filtfilt(b, a, sig, axis=axis)
            else:
                self.logger.error(f"filter type is invalid, do nothing")
                return ErrorCode.ERR_BAD_ARGS, sig_list

            return ErrorCode.ERR_NO_ERROR, sig_filt
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_UNKNOWN, sig_list

    def do_low_pass_filter(self, sig_list, axis=-1):
        try:
            self.logger.info(f"do_low_pass_filter ...")
            if self.parameters.low_pass_filter is None or self.parameters.low_pass_filter["type"] == "":
                self.logger.info(f"bad low pass filter parameters, do nothing!")
                return ErrorCode.ERR_NO_ERROR, sig_list
            order = int(self.parameters.low_pass_filter["order"])
            freq1 = int(self.parameters.low_pass_filter["freq"])
            sig = np.asarray(sig_list, dtype=np.float32)
            sig = sig - sig[0]
            nyq = 0.5 * self.parameters.sample_rate  # Nyquist frequency
            high = freq1 / nyq
            b, a = butter(order, high, btype='low')
            # apply filter
            if self.parameters.low_pass_filter["type"] == 'lfilter':
                sig_filt = lfilter(b, a, sig, axis=axis)
            elif self.parameters.low_pass_filter["type"] == 'filtfilt':
                sig_filt = filtfilt(b, a, sig, axis=axis)
            else:
                self.logger.error(f"filter type is invalid, do nothing")
                return ErrorCode.ERR_BAD_ARGS, sig_list

            return ErrorCode.ERR_NO_ERROR, sig_filt
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_UNKNOWN, sig_list

    def on_legend_click(self, event):
        if event.button != 3:  #  1: left key, 2: middle key, 3: right key
            # self.logger.info("not right key, do nothing ...")
            return
        if event.inaxes not in self.main_lines:  # axis is not in tracker
            return
        x = event.xdata
        y = event.ydata
        ax = event.inaxes
        self.logger.info(f"click on: {x}, {y}")

        _line = self.main_lines[ax][0]
        x_length = len(_line.get_data()[0])
        for line in self.main_lines[ax]:
            x_data, y_data = list(line.get_data())
            if x_length < len(x_data):
                x_length = len(x_data)
                _line = line
        # find most close x point
        x_data, y_data = list(_line.get_data())
        idx = np.argmin(np.abs(x_data - x))
        # find the most close y point
        y_distance = np.abs(y - y_data[idx])
        for line in self.main_lines[ax]:
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
        x_format = ".4f"
        y_format = ".4f"
        text = ax.annotate(f'({x_data[idx]:{x_format}}, {y_data[idx]:{y_format}})',
                           xy=(x_data[idx], y_data[idx]))
        self.markers.append((_line, idx, marker, text))
        self.fig.canvas.draw_idle()
        self.logger.info(f"add a new mark on:{x_data[idx]},{y_data[idx]}")
        return

    def draw_checkbutton(self, _plt, _lines, _colors):
        _h = 0.021 * len(self.parameters.selected_columns)
        # _w = len(max(self.parameters.selected_columns, key=len))
        # 0.62*_w/self.fig.dpi
        rax = _plt.axes((0.91, 0.88 - _h, 0.08, _h))
        self.check_btn = list()
        self.check_btn.append(CheckButtons(
            ax=rax,
            labels=self.parameters.selected_columns,
            actives=[True for _ in range(len(self.parameters.selected_columns))],
            label_props={'color': _colors},
            frame_props={'edgecolor': _colors},
            check_props={'facecolor': _colors},
        )
        )

        def callback(label):
            for line in _lines[label]:
                line.set_visible(not line.get_visible())
                line.figure.canvas.draw_idle()
            # if self.figure_canvas is not None:
            #     self.figure_canvas.canvas.draw_idle()
        self.check_btn[0].on_clicked(callback)

    def draw_checkbutton_2(self, _plt, _lines, _colors):
        try:
            nrows = self.legend_rows

            def callback(label):
                for line in _lines[label]:
                    line.set_visible(not line.get_visible())
                    line.figure.canvas.draw_idle()
                # if self.figure_canvas is not None:
                #     self.figure_canvas.canvas.draw_idle()

            ncols = math.ceil(len(self.parameters.selected_columns)/nrows)
            self.logger.debug(f"mode rows = {len(self.parameters.selected_columns)%nrows}")
            _w = 0.08
            self.check_btn = list()
            for i in range(ncols):
                _h = 0.021 * nrows if i < ncols-1 or (len(self.parameters.selected_columns)%nrows) == 0 \
                    else 0.021 * (len(self.parameters.selected_columns)%nrows)
                self.logger.debug(f"legend height for {i}: {_h}")
                # _w = len(max(self.parameters.selected_columns, key=len))
                # 0.62*_w/self.fig.dpi
                rax = _plt.axes((1.01-ncols*0.1+i*_w, 0.88 - _h, _w, _h))
                self.check_btn.append(CheckButtons(
                    ax=rax,
                    labels=self.parameters.selected_columns[i*nrows:i*nrows+nrows],
                    actives=[True for _ in range(len(self.parameters.selected_columns[i*nrows:i*nrows+nrows]))],
                    label_props={'color': _colors[i*nrows:i*nrows+nrows]},
                    frame_props={'edgecolor': _colors[i*nrows:i*nrows+nrows]},
                    check_props={'facecolor': _colors[i*nrows:i*nrows+nrows]},
                )
                )
                self.check_btn[i].on_clicked(callback)
            return ErrorCode.ERR_NO_ERROR
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_UNKNOWN

    def _draw_table(self, ax, _table_data):
        try:
            self.logger.info(f"_draw_table..")
            ax.axis('off')
            table = Table(ax, bbox=[0, 0, 1, 1])
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
            ax.add_table(table)
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")

    def do_plot_list(self, data):
        try:
            self.logger.info(f"do_plot_list for {self.parameters.sensor}..")
            # matplotlib.rc_file_defaults()
            matplotlib.rcdefaults()
            plt.clf()
            plt.close("all")
            _nrows = len(self.parameters.selected_columns) + 1
            self.fig = plt.figure(self.parameters.plot_name, figsize=(20, 10))
            self.fig.suptitle(self.parameters.plot_name, fontsize=16)
            self.figsize = self.fig.get_size_inches()
            # if self.figure_canvas is not None and self.parameters.show:
            #     self.figure_canvas.create_canvas(self.fig)
            self.fig.subplots(_nrows, 2)
            self.fig.canvas.mpl_connect('button_press_event', self.on_legend_click)
            # plt.subplots(_nrows, 2, figsize=(20, 20))
            plt.rcParams['axes.prop_cycle'] = plt.cycler('color', plt.cm.tab20(np.linspace(0, 1, 20)))
            plt.subplots_adjust(hspace=0.6, left=0.06, right=0.95, top=0.94, bottom=0.03)
            colors = ["#00cd00", "#0000ff"]
            # plt.figtext(.3, .9, 'Aggressor:{}'.format(aggressor_name), fontsize=20, ha='center')
            # plt.figtext(.7, .9, 'Victim:IMU', fontsize=20, ha='center')
            for i in range(0, _nrows-1):
                try:
                    if self.parameters.selected_columns[i] in self.bad_channel:
                        self.logger.error(f"skip bad channel: {self.parameters.selected_columns[i]}")
                        continue
                    # Time domain
                    ax = plt.subplot(_nrows, 2, i * 2 + 1)
                    plt.text(-0.05, 1.15, self.parameters.selected_columns[i], fontsize=10, transform=plt.gca().transAxes)
                    _line, = plt.plot(data["time"][i], data["sig"][i], color=colors[0], linewidth=0.5, alpha=0.7)
                    if ax in self.main_lines:
                        self.main_lines[ax].append(_line)
                    else:
                        self.main_lines.update({ax: [_line]})
                    plt.xlabel('Time [s]', fontsize=10)
                    plt.xticks(fontsize=8)
                    plt.yticks(fontsize=8)

                    # Frequency domain
                    ax = plt.subplot(_nrows, 2, i * 2 + 2)
                    plt.text(-0.05, 1.15, f"{self.parameters.selected_columns[i]}[unit/sqrt(Hz)]",
                             fontsize=10, transform=plt.gca().transAxes)
                    FFT = 2.0 / len(data["sum_vector"][i]) * abs(scipy.fft.fft(data["sum_vector"][i]))
                    _freqs = scipy.fftpack.fftfreq(len(data["time"][i]), data["time"][i][1] - data["time"][i][0])
                    _line, = plt.plot(_freqs[1:int(len(_freqs) / 2)], (FFT[1:int(len(_freqs) / 2)]), color=colors[1], linewidth=0.5, alpha=0.7)
                    if ax in self.main_lines:
                        self.main_lines[ax].append(_line)
                    else:
                        self.main_lines.update({ax: [_line]})
                    # Peak
                    peak_index = np.argmax(FFT[1:int(len(_freqs) / 2)])
                    _line, = plt.plot(_freqs[1:int(len(_freqs) / 2)][peak_index],
                             FFT[1:int(len(_freqs) / 2)][peak_index], 'o', color="#ff0000")
                    plt.axvline(_freqs[1:int(len(_freqs) / 2)][peak_index], color="#ff0000", linestyle='--')
                    self.scale_fft_axis()

                    plt.xlabel('Frequency [Hz]')
                    plt.xticks(fontsize=8)
                    plt.yticks(fontsize=8)
                except Exception as ex:
                    self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
                    self.logger.error(f"this channel have problem:{self.parameters.selected_columns[i]}")
                    plt.axis("off")
                    continue

            # statistics table
            table_ax = plt.subplot(_nrows, 2, (_nrows-1) * 2 + 1)

            # plt.rcParams.update({'font.size': 10})
            table_data = np.array(
                [["Signal"] + self.parameters.selected_columns,
                 ["Average"] + ["{:.8f}".format(val) for val in data["avg"]],
                 ["Noise"] + ["{:.8f}".format(val) for val in data["noise"]]
                 ]).T
            self._draw_table(table_ax, table_data)

            plt.subplot(_nrows, 2, (_nrows-1) * 2 + 2)
            plt.axis("off")

            self.fig.canvas.mpl_connect('resize_event', self.update_text_size)
            _postfix = time.strftime("%Y%m%d_%H%M%S", time.localtime())
            _png_file = os.path.join(self.logger.log_path, f"{self.parameters.plot_name}_{_postfix}.png")
            df = pd.DataFrame(table_data)
            df.to_csv(os.path.join(self.logger.log_path, f"{self.parameters.plot_name}_{_postfix}.csv"), index=False)
            plt.savefig(_png_file)
            # if self.parameters.show and self.figure_canvas is not None and len(self.parameters.selected_columns):
            #     self.figure_canvas.show_plot()
            return ErrorCode.ERR_NO_ERROR
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


class MalibuDataVisualization(DataVisualization):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


# Malibu2, Bali, Tycho
class BaliDataVisualization(DataVisualization):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def visualize_emg_data(self):
        try:
            self.logger.info(f"Malibu2_emg_data: plot {self.parameters.sensor} data")

            # ToDo:: need to review which columns needed
            if not len(self.parameters.selected_columns):
                tmp = self.parameters.df_data.columns.dropna().tolist()
                self.parameters.selected_columns = [val for val in tmp if val.lower() not in ["timestamp"]]
            _err_code, self.target_data = self.calculate_emg_data()
            if _err_code != ErrorCode.ERR_NO_ERROR:
                return _err_code

            # 1. initialize
            if self.initialize_figure(2, 2) != ErrorCode.ERR_NO_ERROR:
                return ErrorCode.ERR_BAD_UNKNOWN

            # 2. time domain
            if self.draw_time_domain_chart({"rows": 2, "cols": 2, "index": 1},
                                           "Signal(V)", True) != ErrorCode.ERR_NO_ERROR:
                return ErrorCode.ERR_BAD_UNKNOWN

            # 3. statistics table
            _err_code, table_data = self.draw_statistics_table({"rows": 2, "cols": 2, "index": 3})
            self.logger.debug(f"table_data1:\n{table_data}")
            if _err_code != ErrorCode.ERR_NO_ERROR:
                return ErrorCode.ERR_BAD_UNKNOWN

            # 4. frequency domain
            if self.draw_freq_domain_chart({"rows": 2, "cols": 2, "index": 2},
                                           "Amplitude(dBV)") != ErrorCode.ERR_NO_ERROR:
                return ErrorCode.ERR_BAD_UNKNOWN

            # 5. harmonic table
            _err_code, table_data1 = self.draw_harmonics_table({"rows": 2, "cols": 2, "index": 4})
            self.logger.debug(f"table_data1:\n{table_data1}")
            if _err_code != ErrorCode.ERR_NO_ERROR:
                return ErrorCode.ERR_BAD_UNKNOWN

            # 6. draw legend
            if self.draw_checkbutton_2(plt, self.all_lines, list(self.line_colors.values())) != ErrorCode.ERR_NO_ERROR:
                return ErrorCode.ERR_BAD_UNKNOWN
            # 7. save data and picture
            if self.save_statistic_and_picture(table_data, table_data1) != ErrorCode.ERR_NO_ERROR:
                return ErrorCode.ERR_BAD_UNKNOWN

            self.logger.info(f"finish: {self.parameters.sensor}")
            return ErrorCode.ERR_NO_ERROR
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_UNKNOWN

    def convert_emg_adc_data(self) -> pd.DataFrame:
        self.parameters.df_data = self.parameters.df_data.div(4096)
        self.parameters.df_data = self.parameters.df_data.div(self.parameters.gain)
        return self.parameters.df_data

    def visualize_ppg_data(self):
        try:
            self.logger.info(f"process {self.parameters.sensor} data")
            # ToDo:: need to review which columns needed
            if not len(self.parameters.selected_columns):
                tmp = self.parameters.df_data.columns.dropna().tolist()
                self.parameters.selected_columns = [val for val in tmp if "timestamp" not in val.lower()]
            self.convert_emg_adc_data()
            _err_code, self.target_data = self.calculate_ppg_data()
            if _err_code != ErrorCode.ERR_NO_ERROR:
                return _err_code
            # 1. init figure
            if self.initialize_figure(2, 2) != ErrorCode.ERR_NO_ERROR:
                return ErrorCode.ERR_BAD_UNKNOWN

            # 2. Time domain
            if self.draw_time_domain_chart({"rows": 2, "cols": 2, "index": 1},
                                           "Raw Cnt", True) != ErrorCode.ERR_NO_ERROR:
                return ErrorCode.ERR_BAD_UNKNOWN

            # 3. Freq domain
            ax = plt.subplot(2, 2, 2)
            for i in range(0, len(self.target_channels)):
                try:
                    plt.rcParams.update({'font.size': 10})
                    FFT = 2.0 / len(self.target_data["sum_vector"][i]) * abs(scipy.fft.fft(self.target_data["sum_vector"][i]))
                    timex = self.target_data["time"][i]
                    freqs = scipy.fftpack.fftfreq(len(timex), timex[1] - timex[0])

                    print(f"freq length:{len(freqs)}")
                    _line, = plt.plot(freqs[1:int(len(freqs) / 2)], (FFT[1:int(len(freqs) / 2)]),
                                      color=self.line_colors[self.target_channels[i]],
                                      linewidth=0.5, alpha=0.7)
                    self.all_lines[self.target_channels[i]].append(_line)
                    if ax in self.main_lines:
                        self.main_lines[ax].append(_line)
                    else:
                        self.main_lines.update({ax: [_line]})
                    # Peak
                    peak_index = np.argmax(FFT[1:int(len(freqs) / 2)])
                    _line, = plt.plot(freqs[1:int(len(freqs) / 2)][peak_index],
                                      FFT[1:int(len(freqs) / 2)][peak_index], 'o', color="#ff0000")
                    self.all_lines[self.target_channels[i]].append(_line)
                    _line = plt.axvline(freqs[1:int(len(freqs) / 2)][peak_index], color="#ff0000", linestyle='--')
                    self.all_lines[self.target_channels[i]].append(_line)
                except Exception as ex:
                    self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
                    continue
            # plt.ylabel('FFT[cnt/sqrt(Hz)]', fontsize=10)
            plt.text(-0.05, 1.05, f"FFT[cnt/sqrt(Hz)]",
                     fontsize=10, transform=plt.gca().transAxes)
            plt.xlabel('Frequency [Hz]', fontsize=10)
            self.scale_fft_axis()

            # if self.draw_freq_domain_chart({"rows": 2, "cols": 2, "index": 2},
            #                                "FFT[cnt/sqrt(Hz)]") != ErrorCode.ERR_NO_ERROR:
            #     return ErrorCode.ERR_BAD_UNKNOWN
            # 4. statistics table
            table_ax = plt.subplot(2, 2, 3)
            # plt.rcParams.update({'font.size': 10})
            table_data = np.array(
                [["Signal"] + self.target_channels,
                 ["Average"] + ["{:.8f}".format(val) for val in self.target_data["avg"]],
                 ["Noise"] + ["{:.8f}".format(val) for val in self.target_data["noise"]],
                 ["SNR"] + ["{:.8f}".format(val) for val in self.target_data["snr"]]
                 ]).T
            self._draw_table(table_ax, table_data)
            # df = pd.DataFrame(table_data)
            # 5. blank
            plt.subplot(2, 2, 4)
            plt.axis('off')
            self.draw_checkbutton(plt, self.all_lines, list(self.line_colors.values()))
            # self.fig.canvas.mpl_connect('resize_event', self.update_text_size)

            self.save_statistic_and_picture(table_data)

            self.logger.info(f"finish: {self.parameters.sensor}")
            return ErrorCode.ERR_NO_ERROR
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_UNKNOWN


class GEN2DataVisualization(DataVisualization):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def visualize_emg_data(self):
        try:
            self.logger.info(f"Malibu2_emg_data: plot {self.parameters.sensor} data")

            # ToDo:: need to review which columns needed
            if not len(self.parameters.selected_columns):
                tmp = self.parameters.df_data.columns.dropna().tolist()
                self.parameters.selected_columns = [val for val in tmp if val.lower() not in ["timestamp"]]
            _err_code, self.target_data = self.calculate_emg_data()
            if _err_code != ErrorCode.ERR_NO_ERROR:
                return _err_code

            # 1. initialize
            if self.initialize_figure(2, 2) != ErrorCode.ERR_NO_ERROR:
                return ErrorCode.ERR_BAD_UNKNOWN

            # 2. time domain
            if self.draw_time_domain_chart({"rows": 2, "cols": 2, "index": 1},
                                           "Signal (mV)", True) != ErrorCode.ERR_NO_ERROR:
                return ErrorCode.ERR_BAD_UNKNOWN

            # 3. statistics table
            _err_code, table_data = self.draw_statistics_table({"rows": 2, "cols": 2, "index": 3})
            self.logger.debug(f"table_data1:\n{table_data}")
            if _err_code != ErrorCode.ERR_NO_ERROR:
                return ErrorCode.ERR_BAD_UNKNOWN

            # 4. frequency domain
            if self.draw_freq_domain_chart({"rows": 2, "cols": 2, "index": 2},
                                           "PSD (V²/Hz)", "psd") != ErrorCode.ERR_NO_ERROR:
                return ErrorCode.ERR_BAD_UNKNOWN

            # 5. harmonic table
            _err_code, table_data1 = self.draw_harmonics_table({"rows": 2, "cols": 2, "index": 4}, "psd")
            self.logger.debug(f"table_data1:\n{table_data1}")
            if _err_code != ErrorCode.ERR_NO_ERROR:
                return ErrorCode.ERR_BAD_UNKNOWN

            # 6. draw legend
            if self.draw_checkbutton_2(plt, self.all_lines, list(self.line_colors.values())) != ErrorCode.ERR_NO_ERROR:
                return ErrorCode.ERR_BAD_UNKNOWN
            # 7. save data and picture
            if self.save_statistic_and_picture(table_data, table_data1) != ErrorCode.ERR_NO_ERROR:
                return ErrorCode.ERR_BAD_UNKNOWN

            self.logger.info(f"finish: {self.parameters.sensor}")
            return ErrorCode.ERR_NO_ERROR
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_UNKNOWN

    def calculate_emg_data(self):
        self.bad_channel = []
        keys = ["channel", "time", "sig", "total_rms", "avg_p2p", "cycle", "cycle_time", "max", "min", "bias",
                "target_sig", "target_freq", "target_rms", "target_sig_peak", "target_freq_peak"]
        _data = {key: [] for key in keys}

        # covert adc code to voltage
        self.convert_emg_adc_data()

        drops = self.parameters.data_drop
        for channel in self.parameters.selected_columns:
            if int(drops[1]) > 0:
                voltage = self.parameters.df_data[channel].iloc[int(drops[0]):int(drops[1])]
            else:
                voltage = self.parameters.df_data[channel].iloc[int(drops[0]):]
            dc_bias = np.mean(voltage)
            # Remove DC bias from waveform
            ac_signal = voltage - dc_bias
            _err_code, ac_signal = self.filter_signals(ac_signal)
            if _err_code != ErrorCode.ERR_NO_ERROR:
                return _err_code, _data
            # Create time axis
            _time = np.arange(len(voltage)) / self.parameters.sample_rate
            # Calculate FFT of AC signal
            if len(ac_signal) == 0:
                self.logger.error(f"bad channel data: {channel}")
                self.bad_channel.append(channel)
                continue

            target_freq, target_sig = signal.welch(ac_signal, fs=self.parameters.sample_rate, nperseg=len(ac_signal))
            target_rms = np.sqrt(sum(target_sig[1:int(self.parameters.sample_rate / 2) + 1] * (target_freq[1] - target_freq[0])))
            peak_index = np.argmax(target_sig)
            target_sig_peak = target_sig[peak_index]
            target_freq_peak = target_freq[peak_index]

            self.logger.info(f"peak:{target_freq_peak},{target_sig_peak}")
            # Find cycle time and max/min values in each cycle
            cycle_time = 1 / target_freq_peak
            num_cycles = int(len(ac_signal) / (cycle_time * self.parameters.sample_rate))
            max_vals = np.zeros(num_cycles)
            min_vals = np.zeros(num_cycles)
            for i in range(num_cycles):
                cycle_start = int(i * cycle_time * self.parameters.sample_rate)
                cycle_end = int((i + 1) * cycle_time * self.parameters.sample_rate)
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
            _data["time"].append(_time)
            _data["sig"].append(ac_signal)
            _data["total_rms"].append(rms_val)
            _data["avg_p2p"].append(avg_peak_to_peak_val)
            _data["cycle"].append(num_cycles)
            _data["cycle_time"].append(cycle_time)
            _data["max"].append(max_vals)
            _data["min"].append(min_vals)
            _data["bias"].append(dc_bias)
            _data["target_sig"].append(target_sig)
            _data["target_freq"].append(target_freq)
            _data["target_rms"].append(target_rms)
            _data["target_freq_peak"].append(target_freq_peak)
            _data["target_sig_peak"].append(target_sig_peak)
        self.target_channels = copy.deepcopy(_data["channel"])
        return ErrorCode.ERR_NO_ERROR, _data

    def convert_emg_adc_data(self) -> pd.DataFrame:
        self.parameters.df_data = (self.parameters.df_data.div(4095)).mul(0.8)
        self.parameters.df_data = self.parameters.df_data.div(self.parameters.gain)
        return self.parameters.df_data

    def on_legend_click(self, event):
        if event.button != 3:  #  1: left key, 2: middle key, 3: right key
            # self.logger.info("not right key, do nothing ...")
            return
        if event.inaxes not in self.main_lines:  # axis is not in tracker
            return
        x = event.xdata
        y = event.ydata
        ax = event.inaxes
        self.logger.info(f"click on: {x}, {y}")

        _line = self.main_lines[ax][0]
        x_length = len(_line.get_data()[0])
        for line in self.main_lines[ax]:
            x_data, y_data = list(line.get_data())
            if x_length < len(x_data):
                x_length = len(x_data)
                _line = line
        # find most close x point
        x_data, y_data = list(_line.get_data())
        idx = np.argmin(np.abs(x_data - x))
        # find the most close y point
        y_distance = np.abs(y - y_data[idx])
        for line in self.main_lines[ax]:
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
        x_format = ".4f"
        y_format = ".2e"
        text = ax.annotate(f'({x_data[idx]:{x_format}}, {y_data[idx]:{y_format}})',
                           xy=(x_data[idx], y_data[idx]))
        self.markers.append((_line, idx, marker, text))
        self.fig.canvas.draw_idle()
        self.logger.info(f"add a new mark on:{x_data[idx]},{y_data[idx]}")
        return

    def draw_time_domain_chart(self, layout: dict, y_text: str = "", overlap: bool = False) -> ErrorCode:
        try:
            self.logger.debug("draw time domain chart ...")
            ax = plt.subplot(layout["rows"], layout["cols"], layout["index"])
            plt.rcParams.update({'font.size': self.txt_fontsize})
            # ax = axes[0][0]
            self.all_lines = {key: [] for key in self.target_channels}
            self.line_colors = {}
            if not overlap:
                _shift = np.amax(self.target_data["sig"]) - np.amin(self.target_data["sig"])
            else:
                _shift = 0
            # print(_shift)
            for i in range(0, len(self.target_channels)):
                plt.rcParams.update({'font.size': self.txt_fontsize})
                if self.parameters.sensor.lower()[:3] == "emg":
                    _line, = plt.plot(self.target_data["time"][i], (self.target_data["sig"][i] + i * _shift)*1000,
                                      linewidth=0.5, alpha=0.7)
                else:
                    _line, = plt.plot(self.target_data["time"][i], self.target_data["sig"][i] + i * _shift,
                                      linewidth=0.5, alpha=0.7)
                if overlap:
                    self.all_lines[self.target_channels[i]].append(_line)
                self.line_colors[self.target_channels[i]] = _line.get_color()
                if ax in self.main_lines:
                    self.main_lines[ax].append(_line)
                else:
                    self.main_lines.update({ax: [_line]})

            plt.text(-0.05, 1.05, y_text, fontsize=self.txt_fontsize, transform=plt.gca().transAxes)
            plt.xlabel('Time (S)', fontsize=self.txt_fontsize)
            if not overlap:
                plt.yticks([_shift * i for i in np.arange(0, len(self.target_channels))])
                ax.set_yticklabels(self.target_channels)
            return ErrorCode.ERR_NO_ERROR
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_UNKNOWN

    def draw_statistics_table(self, layout: dict) -> (ErrorCode, np.array):
        try:
            self.logger.debug("draw statistics table chart ...")
            table_ax = plt.subplot(layout["rows"], layout["cols"], layout["index"])
            # plt.rcParams.update({'font.size': 10})
            table_data = np.array(
                [["Signal"] + self.target_channels, ["RMS Level(µV)"] +
                 ["{:.8f}".format(val * 10 ** 6) for val in self.target_data["total_rms"]],
                 ["PSD RMS(µV)"] + ["{:.8f}".format(val * 10 ** 6) for val in self.target_data["target_rms"]],
                 ["Avg. Peak-to-Peak(mV)"] + ["{:.8f}".format(val * 1000) for val in self.target_data["avg_p2p"]],
                 ["DC bias(mV)"] + ["{:.8f}".format(val * 1000) for val in self.target_data["bias"]]]).T
            self.logger.debug(f"table_data:\n{table_data}")
            self._draw_table(table_ax, table_data)
            return ErrorCode.ERR_NO_ERROR, table_data
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_UNKNOWN, None


class SummaryDataVisualization:
    def __init__(self, **kwargs):
        self.logger = kwargs["logger"] if "logger" in kwargs and kwargs["logger"] else logging.getLogger()
        self.params = None

        self.figsize = list()
        self.fig = None
        self.channels = list()
        self.markers = list()
        self.main_lines = dict()
        self.postfix = None

        # ToDo:: review which columns should be ignored
        self.ignore_columns = ["sn", "start", "end", "timestamp", "serial number", "result"]

        cmaps = plt.colormaps['tab20']
        cmaps_c = plt.colormaps['tab20b']
        self.colors = [cmaps(i % 19) for i in range(20)] + [cmaps_c(i % 19) for i in range(20)]

    def visualize_data(self, params: VisualizeParameters) -> ErrorCode:
        self.params = params

        if self.fig is not None:
            for ax in self.fig.axes:
                ax.cla()
                plt.clf()
                plt.close("all")
        self.fig = None
        self.figsize = list()
        self.channels = copy.deepcopy(self.params.selected_columns)
        self.markers = list()
        self.main_lines = dict()
        if self.params.summary_scale is not None and len(self.params.summary_scale) == 0:
            self.params.summary_scale = None
        if self.params.plot_name is None or not len(self.params.plot_name.strip()):
            self.params.plot_name = self.params.sensor
        if self.params.plot_name is None or not len(self.params.plot_name.strip()):
            self.params.plot_name = "DEF"
        if not len(self.params.sensor.strip()):
            self.params.sensor = 'DEF'
        if self.params.plot_name is None or not len(self.params.plot_name.strip()):
            self.params.plot_name = self.params.sensor

        if self.params.data_file is not None:
            try:
                self.params.df_data = pd.read_csv(self.params.data_file)
                self.params.df_data = self.params.df_data.iloc[:, 3:]
            except Exception as ex:
                self.logger.error(f"Exception: {str(ex)}")
                return ErrorCode.ERR_BAD_FILE
        if self.params.df_data is None:
            return ErrorCode.ERR_BAD_DATA

        if len(self.channels):
            self.channels = [val for val in self.channels if val.lower() not in self.ignore_columns]
            base_cols = [val for val in self.channels if 'baseline' in val.lower()]
            non_base_cols = [val for val in self.channels if 'baseline' not in val.lower()]
            base_cols.sort()
            non_base_cols.sort()
            self.channels = base_cols + non_base_cols

        return self.visualize_summary_data()

    def cdf_plot(self, filename=None):
        try:
            import numpy as np
            plt.clf()
            plt.close("all")

            if not len(self.channels):
                tmp = self.params.df_data.columns.dropna().tolist()
                self.channels = [val for val in tmp if val.lower() not in self.ignore_columns]
            num_of_columns = len(self.channels)
            max_length = np.max(np.vectorize(len)(self.channels))
            self.logger.debug(f"max_length: {max_length}")
            num = 27
            ncol = np.ceil(num_of_columns / num)
            fig = plt.figure(f"{self.params.plot_name}")
            labelcolor = list()
            for i, ch in enumerate(self.channels):
                ch_data = self.params.df_data[ch].dropna()
                plt.plot(np.sort(ch_data), np.linspace(0, 1, len(ch_data), endpoint=True), label=ch,
                         color=self.colors[i % len(self.colors)], linewidth=1)
                if (self.params.summary_scale is not None
                        and (ch_data.min() < self.params.summary_scale[0] or ch_data.max() > self.params.summary_scale[1])):
                    labelcolor.append("red")
                else:
                    labelcolor.append("black")

            plt.xlabel('Value')
            plt.ylabel('Cumulative Probability')
            plt.title(f'{self.params.plot_name} CDF Plot')
            if self.params.summary_scale is not None:
                plt.xlim(self.params.summary_scale)
            plt.gca().xaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))

            legend = plt.legend(ncol=ncol, loc='upper left',
                                labelcolor=labelcolor,
                                bbox_to_anchor=(1.05, 1), fontsize=8)
            plt.gca().add_artist(legend)

            width = legend.get_window_extent().width + 28
            w = 8+width/fig.dpi + 40/fig.dpi
            fig.set_size_inches(w, 6)
            right_ratio = 8/w
            left_ratio = 80/fig.dpi/w
            plt.subplots_adjust(left=left_ratio, right=right_ratio)
            # legend.set_bbox_to_anchor(bbox=(1.05, 1), transform=plt.gca().transAxes)
            # if filename:
            #     sub_png_file = filename + '_CDF.png'
            # else:
            # time_stamp = datetime.datetime.now()
            # postfix = time_stamp.strftime("%Y%m%d_%H%M%S")
            # sub_png_file = "_".join([self.params.plot_name, f'CDF_{self.postfix}.png'])
            sub_png_file = os.path.join(self.logger.log_path, f"{self.params.plot_name}_CDF_{self.postfix}.png")
            self.logger.debug(f"file name:{sub_png_file}")
            plt.savefig(sub_png_file)

            # self.figsize = fig.get_size_inches()
            # if self.figure_canvas is not None and self.show:
            #     self.figure_canvas.create_canvas(fig)
            #
            # if self.show and self.figure_canvas is not None:
            #     self.figure_canvas.show_plot()

            return True
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return False

    def visualize_summary_data(self, filename=None):
        try:
            self.postfix = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            ret = self.cdf_plot(filename)
            if not ret:
                return ErrorCode.ERR_BAD_UNKNOWN
            if not len(self.channels):
                tmp = self.params.df_data.columns.dropna().tolist()
                self.channels = [val for val in tmp if val.lower() not in self.ignore_columns]
            num_of_columns = len(self.channels)

            # for i, ch in enumerate(self.channels):
            x = 3*len(self.channels)
            plt.clf()
            plt.close("all")
            self.fig = plt.figure(f"{self.params.plot_name}", figsize=(x, 12))
            self.figsize = self.fig.get_size_inches()
            # if self.figure_canvas is not None and self.show:
            #     self.figure_canvas.create_canvas(self.fig)
            self.fig.suptitle(self.params.plot_name, fontsize=16)
            gs = GridSpec(8, num_of_columns, figure=self.fig)

            ax_main = self.fig.add_subplot(gs[0:3, :])
            # ch_data = [data.iloc[:, j].dropna() for j in range(group_data_index[i], data.shape[1], group_size)]
            ch_data = [self.params.df_data[ch].dropna() for ch in self.channels]
            bp = ax_main.boxplot(ch_data, patch_artist=True)
            if self.params.summary_scale is not None:
                ax_main.set_ylim(self.params.summary_scale)
            # means = [np.mean(d) for d in ch_data]
            for i, patch in enumerate(bp['boxes']):
                if self.params.summary_scale is not None and (ch_data[i].min() < self.params.summary_scale[0] or ch_data[i].max() > self.params.summary_scale[1]):
                    patch.set_facecolor('red')
                elif i == 0:
                    patch.set_facecolor('#2faf00') # green

            # ax_main.set_ylim([0.8, 1.3])
            ax_main.set_xticklabels([re.sub(r"^.*_data_", "", val, flags=re.IGNORECASE) for val in self.channels])
            base_mean = self.params.df_data.loc[:, self.channels[0]].mean()
            # base_mean = means[0]
            ax_main.axhline(base_mean, color='g', linestyle='-.')
            # ax_main.axhline(1.2, color='b', linestyle='-.')

            for j in range(num_of_columns):
                ax_hist = self.fig.add_subplot(gs[3:6, j])
                if self.params.summary_scale is not None and (ch_data[j].min() < self.params.summary_scale[0] or ch_data[j].max() > self.params.summary_scale[1]):
                    _color = "red"
                elif j != 0:
                    _color = "#1f77b4"
                else:
                    _color = "#2faf00" # green
                ax_hist.hist(ch_data[j], orientation='horizontal', color=_color)
                if _color != "red":
                    ax_hist.set_ylim(self.params.summary_scale)
                # plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, loc: f"{x:.3e}"))
            csv_data = dict()
            csv_data.update({"": ["100% (maximum)", "75%", "50% (median)", "25%", "0% (minimum)",
                                  "Mean", "Std Dev", "Std Error Mean", "Upper 95% Mean", "Lower 95% Mean", "N", "Outlier"]})
            for k in range(num_of_columns):
                ax_label = self.fig.add_subplot(gs[6:8, k])
                col_data = ch_data[k]

                col_min = col_data.min()
                col_max = col_data.max()
                col_mean = col_data.mean()
                col_std_dev = col_data.std()
                std_err_mean = stats.sem(col_data)

                percentiles = col_data.quantile([0.25, 0.5, 0.75])
                percentile_25 = percentiles[0.25]
                percentile_50 = percentiles[0.5]
                percentile_75 = percentiles[0.75]

                confidence_level = 0.95
                degrees_freedom = col_data.shape[0] - 1
                confidence_interval = stats.t.interval(confidence_level, degrees_freedom, col_mean, std_err_mean)
                lower_95_mean = confidence_interval[0]
                upper_95_mean = confidence_interval[1]

                lower_whisker = percentile_25 - 1.5 * (percentile_75 - percentile_25)
                upper_whisker = percentile_75 + 1.5 * (percentile_75 - percentile_25)
                outliers = col_data[(col_data < lower_whisker) | (col_data > upper_whisker)]
                outlier_count = len(outliers)
                # print outlier SNs in log
                if 'SN' in self.params.df_data and outlier_count:
                    self.logger.warning(f"outliers:")
                    for i, v in zip(outliers.index, outliers):
                        self.logger.warning(f"index {i}, {self.params.df_data['SN'][i]}, {self.channels[k]}, {v}")
                elif outlier_count:
                    self.logger.warning(f"outliers:")
                    for i, v in zip(outliers.index, outliers):
                        self.logger.warning(f"index {i}, {self.channels[k]}, {v}")
                text_list = [
                    f"100% (maximum): {col_max:.3e}",
                    f" 75%          : {percentile_75:.3e}",
                    f" 50% (median) : {percentile_50:.3e}",
                    f" 25%          : {percentile_25:.3e}",
                    f"  0% (minimum): {col_min:.3e}",
                    f"",
                    f"Mean          : {col_mean:.3e}",
                    f"Std Dev       : {col_std_dev:.3e}",
                    f"Std Error Mean: {std_err_mean:.3e}",
                    f"Upper 95% Mean: {upper_95_mean:.3e}",
                    f"Lower 95% Mean: {lower_95_mean:.3e}",
                    f"N             : {col_data.shape[0]}",
                    f"Outlier       : {outlier_count}"
                ]

                csv_data.update({self.channels[k]: [col_max, percentile_75,
                                                    percentile_50, percentile_25,
                                                    col_min, col_mean, col_std_dev,
                                                    std_err_mean, upper_95_mean,
                                                    lower_95_mean, col_data.shape[0], outlier_count]})

                ax_label.text(0.02, 0.98, "\n".join(text_list), ha='left', va='top', fontname='monospace')
                ax_label.axis('off')
                # r_colors = ['lightgrey', '#eee9e9']
                r_colors = ['#e8e8e8', '#fffafa']
                rect = patches.Rectangle((0, 0.16), 0.97, 1, transform=ax_label.transAxes, color=r_colors[k % 2])
                ax_label.add_patch(rect)
            # if filename:
            #     sub_png_file = filename + '.png'
            # else:
            # time_stamp = datetime.datetime.now()
            # postfix = time_stamp.strftime("%Y%m%d_%H%M%S")
            # sub_png_file = f"{self.params.plot_name}_distribution_{self.postfix}.png"

            pd_data = pd.DataFrame(csv_data)
            # pd_data.to_csv(f"{self.params.plot_name}_statistics_{self.postfix}.csv", index=False)

            sub_png_file = os.path.join(self.logger.log_path, f"{self.params.plot_name}_distribution_{self.postfix}.png")

            pd_data.to_csv(os.path.join(self.logger.log_path, f"{self.params.plot_name}_{self.postfix}.csv"), index=False)

            plt.tight_layout(rect=[0, 0, 1, 1])
            plt.savefig(sub_png_file)
            self.logger.info(f"Saved to file {sub_png_file}")
            self.fig.canvas.mpl_connect('resize_event', self.update_text_size)
            # plt.show()
            # if self.show and self.figure_canvas is not None:
            #     self.figure_canvas.show_plot()
            return ErrorCode.ERR_NO_ERROR
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


def DataVisualize(params: VisualizeParameters, logger=None):
    if params.data_type == "Summary Data":
        return SummaryDataVisualization(logger=logger)
    else:
        if params.project == "gen2":
            return GEN2DataVisualization(logger=logger)
        elif params.project == "bali" or params.project == "tycho":
            return BaliDataVisualization(logger=logger)
        else:
            return MalibuDataVisualization(logger=logger)


if __name__ == '__main__':
    import sys
    from my_logger import *

    logger = MyLogger(level='debug', save=True)
    dv = DataVisualize(logger=logger)
    param = VisualizeParameters()
    param.data_file = "/Users/duleo/03_Github/cld_data_visualize/mag.csv"   # sys.argv[1]
    param.sensor = "mag" # sys.argv[2].lower()

    dv.visualize_data(param)
