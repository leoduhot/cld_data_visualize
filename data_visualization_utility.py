# -*- coding: UTF-8 -*-
import sys
import numpy as np
import pandas as pd
import scipy.fftpack
from scipy import signal
from scipy.signal import butter, lfilter, filtfilt
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons
matplotlib.use('TkAgg')
import math
import os
import logging
from enum import Enum, IntEnum


class ErrorCode(IntEnum):
    ERR_NO_ERROR = 0,
    ERR_BAD_FILE = -1,
    ERR_BAD_DATA = -2,
    ERR_BAD_TYPE = -3,
    ERR_BAD_ARGS = -4,
    ERR_BAD_UNKNOWN = -255,


class DataVisualization:
    def __init__(self, *args, **kwargs):
        self.logger = kwargs["logger"] if 'logger' in kwargs else logging
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

        self.process_func = {
            "emg": self.emg_data,
            "ppg": self.ppg_data,
            "imu": self.imu_data,
            "alt": self.alt_data,
            "compass": self.compass_data,
            "bti": self.bti_data,
            "others": self.others_data,
        }

    def visualize(self, *args, **kwargs):
        self.list = kwargs["channels"] if "channels" in kwargs else []
        self.sensor = kwargs["sensor"] if "sensor" in kwargs else "others"
        self.sample_rate = float(kwargs["rate"]) if "rate" in kwargs else 1
        self.data_drop = kwargs["drop"] if "drop" in kwargs else [0, -1]
        self.data_file = kwargs["file"] if "file" in kwargs else None
        self.high_pass_filter = kwargs["highpassfilter"] if "highpassfilter" in kwargs else {"type": '', "order": 0, "freq": 0}
        self.low_pass_filter = kwargs["lowpassfilter"] if "lowpassfilter" in kwargs else {"type": '', "order": 0, "freq": 0}
        self.notch_filter = kwargs["notchfilter"] if "notchfilter" in kwargs else [[0,0], [0,0], [0,0]]

        try:
            self.df_data = pd.read_csv(self.data_file)
        except Exception as ex:
            self.logger.error(f"Exception: {str(ex)}")
            return ErrorCode.ERR_BAD_FILE

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
            self.logger.debug(f"do_notch_filter")
            _new_sig = _sig
            for f in self.notch_filter:
                if f != [0, 0] and f != []:
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
            if self.high_pass_filter["type"] == "":
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
            if self.low_pass_filter["type"] == "":
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

    def do_data_conversion(self, b_snr=False):
        keys = ["avg", "sig", "noise", "time", "sum_vector", "snr"]
        _data = {key: [] for key in keys}
        self.bad_channel = []
        for channel in self.list:
            try:
                _sig = self.df_data[channel].iloc[int(self.data_drop[0]):int(self.data_drop[1])]
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

    def draw_checkbutton(self):
        pass
    def do_plot_list(self, data):
        _nrows = len(self.list) + 1
        fig = plt.figure(self.sensor, figsize=(20, 10))
        fig.subplots(_nrows, 2)
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
                plt.subplot(_nrows, 2, i * 2 + 1)
                plt.text(-0.05, 1.05, self.list[i], fontsize=10, transform=plt.gca().transAxes)
                plt.plot(data["time"][i], data["sig"][i], color=colors[0])
                plt.xlabel('Time [s]', fontsize=10)
                plt.xticks(fontsize=8)
                plt.yticks(fontsize=8)

                # Frequency domain
                plt.subplot(_nrows, 2, i * 2 + 2)
                plt.text(-0.05, 1.05, f"{self.list[i]}[unit/sqrt(Hz)]",
                         fontsize=10, transform=plt.gca().transAxes)
                FFT = 2.0 / len(data["sum_vector"][i]) * abs(scipy.fft.fft(data["sum_vector"][i]))
                _freqs = scipy.fftpack.fftfreq(len(data["time"][i]), data["time"][i][1] - data["time"][i][0])

                plt.plot(_freqs[1:int(len(_freqs) / 2)], (FFT[1:int(len(_freqs) / 2)]), color=colors[1])
                # Peak
                peak_index = np.argmax(FFT[1:int(len(_freqs) / 2)])
                plt.plot(_freqs[1:int(len(_freqs) / 2)][peak_index],
                         FFT[1:int(len(_freqs) / 2)][peak_index], 'o', color="#ff0000")
                plt.axvline(_freqs[1:int(len(_freqs) / 2)][peak_index], color="#ff0000", linestyle='--')

                # plt.xlim([0.1, fs / 2])
                plt.xlabel('frequency [Hz]')
                plt.xticks(fontsize=8)
                plt.yticks(fontsize=8)
                # plt.ylabel('{}\n[unit/sqrt(Hz)]'.format(self.list[i]), fontsize=10, rotation=0, loc="top")
            except Exception as ex:
                self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
                self.logger.error(f"this channel have problem:{self.list[i]}")
                plt.axis("off")
                continue

        # statistics table
        plt.subplot(_nrows, 2, (_nrows-1) * 2 + 1)
        plt.rcParams.update({'font.size': 10})
        table_data = np.array(
            [[""] + self.list,
             ["avg."] + ["{:.8f}".format(val) for val in data["avg"]],
             ["noise"] + ["{:.8f}".format(val) for val in data["noise"]]
             ]).T
        table = plt.table(cellText=table_data, cellLoc='center', loc='center', fontsize=[10, 10, 10])
        # table.auto_set_font_size(False)
        # table.scale(1, 2.5)
        for (row, col), cell in table.get_celld().items():
            cell.set_linewidth(0.3)
        plt.axis('off')
        plt.subplot(_nrows, 2, (_nrows-1) * 2 + 2)
        plt.axis("off")

        plt.show()
        plt.cla()
        plt.close("all")
        return ErrorCode.ERR_NO_ERROR

    def do_plot_together(self, time_data, freq_data, statistics_data):
        pass

    def emg_data_with_notch(self, *args, **kwargs):

        # Get file path and sample rate from command line arguments
        file_path = self.data_file
        sample_rate = self.sample_rate

        # Read data from file and convert to voltage
        data = pd.read_csv(file_path)
        for channel in self.list:
            voltage = data[channel]

            # Calculate DC bias
            dc_bias = np.mean(voltage)

            # Remove DC bias from waveform
            ac_signal = voltage - dc_bias

            # Create time axis
            time = np.arange(len(data)) / sample_rate

            # Calculate RMS level value
            rms_val = np.sqrt(np.mean(ac_signal ** 2))

            # Calculate FFT of AC signal before notch filter
            fft_size = 2 ** int(np.ceil(np.log2(len(ac_signal))))
            fft_freq = np.fft.rfftfreq(fft_size, d=1 / sample_rate)
            fft_amplitude = np.abs(np.fft.rfft(ac_signal, fft_size))
            fft_dbv = 20 * np.log10(fft_amplitude / 1)  # Convert to dBV

            # Find peak value of AC signal in FFT plot before notch filter
            ac_peak_index = np.argmax(fft_amplitude)
            ac_peak_freq = fft_freq[ac_peak_index]
            ac_peak_dbv = fft_dbv[ac_peak_index]
            ac_peak_coord = (ac_peak_freq, ac_peak_dbv)

            # Apply notch filters to remove dedicated frequency spurs
            notch_freq_1 = self.notch_filter[0][0] # 2430  # Specify the frequency of the first spur to be removed
            Q_1 = self.notch_filter[0][1] # 10  # Specify the quality factor of the first notch filter
            b1, a1 = signal.iirnotch(notch_freq_1, Q_1, fs=sample_rate)
            ac_signal_filtered_1 = signal.lfilter(b1, a1, ac_signal)

            notch_freq_2 = self.notch_filter[1][0] # 3130  # Specify the frequency of the second spur to be removed
            Q_2 = self.notch_filter[1][1] # 10  # Specify the quality factor of the second notch filter
            b2, a2 = signal.iirnotch(notch_freq_2, Q_2, fs=sample_rate)
            ac_signal_filtered_2 = signal.lfilter(b2, a2, ac_signal_filtered_1)

            notch_freq_3 = self.notch_filter[2][0] # 2400  # Specify the frequency of the second spur to be removed
            Q_3 = self.notch_filter[2][1] # 50  # Specify the quality factor of the second notch filter
            b3, a3 = signal.iirnotch(notch_freq_3, Q_3, fs=sample_rate)
            ac_signal_filtered_3 = signal.lfilter(b3, a3, ac_signal_filtered_2)

            # Calculate RMS level value after notch filters
            rms_val_filtered = np.sqrt(np.mean(ac_signal_filtered_3 ** 2))

            # Calculate FFT of AC signal after notch filters
            fft_amplitude_filtered = np.abs(np.fft.rfft(ac_signal_filtered_3, fft_size))
            fft_dbv_filtered = 20 * np.log10(fft_amplitude_filtered / 1)  # Convert to dBV

            # Specify the frequency range to plot
            start_freq = 50  # Starting frequency for the plot

            # Find the indices corresponding to the desired frequency range
            start_index = np.argmax(fft_freq >= start_freq)
            end_index = len(fft_freq)

            plt.figure(f"{channel}", figsize=(20, 10))
            # Plot AC signal and DC bias
            plt.subplot(4, 1, 1)
            plt.plot(time, ac_signal, label='AC Signal')
            plt.text(0.1, 1.2, 'RMS Level Value: {:.8f} V'.format(rms_val), transform=plt.gca().transAxes, fontsize=10)
            plt.text(0.1, 1, 'RMS Level Value after filter: {:.8f} V'.format(rms_val_filtered),
                     transform=plt.gca().transAxes, fontsize=10)
            plt.ylabel('Signal (V)')
            plt.xlabel('Time (S)')
            plt.legend()

            # Plot AC signal after filter
            plt.subplot(4, 1, 2)
            plt.plot(time, ac_signal_filtered_2, label='AC Signal after filter')
            # plt.text(0.1, 1.2, 'RMS Level Value: {:.8f} V'.format(rms_val), transform=plt.gca().transAxes, fontsize=10)
            # plt.text(0.1, 1, 'RMS Level Value after filter: {:.8f} V'.format(rms_val_filtered), transform=plt.gca().transAxes, fontsize=10)
            plt.ylabel('Signal (V)')
            plt.xlabel('Time (S)')
            plt.legend()

            # Plot FFT before notch filters
            plt.subplot(4, 1, 3)
            plt.plot(fft_freq[start_index:end_index], fft_dbv[start_index:end_index], label='FFT Before Notch Filter')
            plt.axvline(ac_peak_freq, color='r', linestyle='--', label='Peak Frequency: {:.2f} Hz'.format(ac_peak_freq))
            plt.xlim(start_freq, fft_freq[end_index - 1])
            plt.ylabel('Magnitude (dBV)')
            plt.xlabel('Frequency (Hz)')
            plt.legend()

            # Plot FFT after notch filters
            plt.subplot(4, 1, 4)
            plt.plot(fft_freq[start_index:end_index], fft_dbv_filtered[start_index:end_index],
                     label='FFT After Notch Filters')
            plt.xlim(start_freq, fft_freq[end_index - 1])
            plt.ylabel('Magnitude (dBV)')
            plt.xlabel('Frequency (Hz)')
            plt.legend()

            plt.tight_layout()
            plt.show()

            self.logger.info("AC RMS Level (Filtered): {:.8f} V".format(rms_val_filtered))

    def emg_data(self, *args, **kwargs):
        self.logger.info(f"process {self.sensor} data")
        title = os.path.basename(self.data_file)
        aggressor_name = title.replace(".csv", "")
        aggressor_name = aggressor_name.replace("EMG_Data_", "")

        list_time = []
        list_ac_signal = []
        list_rms_val = []
        list_avg_peak_to_peak_val = []
        list_num_cycles = []
        list_cycle_time = []
        list_max_vals = []
        list_min_vals = []
        list_fft_freq = []
        list_ac_peak_freq = []
        list_fft_dbv = []
        list_ac_peak_dbv = []
        list_dc_bias = []
        self.bad_channel = []
        # time,ac_signal,rms_val,avg_peak_to_peak_val,num_cycles,cycle_time,max_vals,min_vals,fft_freq,ac_peak_freq,fft_dbv,ac_peak_dbv
        for channel in self.list:
            voltage = self.df_data[channel].iloc[int(self.data_drop[0]):int(self.data_drop[1])]
            # Calculate DC bias
            dc_bias = np.mean(voltage)
            # Remove DC bias from waveform
            ac_signal = voltage - dc_bias
            _err_code, ac_signal = self.do_high_pass_filter(ac_signal)
            if _err_code != ErrorCode.ERR_NO_ERROR:
                return _err_code
            _err_code, ac_signal = self.do_low_pass_filter(ac_signal)
            if _err_code != ErrorCode.ERR_NO_ERROR:
                return _err_code
            _err_code, ac_signal = self.do_notch_filter(ac_signal)
            if _err_code != ErrorCode.ERR_NO_ERROR:
                return _err_code
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
            list_time.append(time)
            list_ac_signal.append(ac_signal)
            list_rms_val.append(rms_val)
            list_avg_peak_to_peak_val.append(avg_peak_to_peak_val)
            list_num_cycles.append(num_cycles)
            list_cycle_time.append(cycle_time)
            list_max_vals.append(max_vals)
            list_min_vals.append(min_vals)
            list_fft_freq.append(fft_freq)
            list_ac_peak_freq.append(ac_peak_freq)
            list_fft_dbv.append(fft_dbv)
            list_ac_peak_dbv.append(ac_peak_dbv)
            list_dc_bias.append(dc_bias)

        fig = plt.figure(f"EMG v.s. {aggressor_name}", figsize=(20, 10))
        axes = fig.subplots(2, 2)
        plt.subplot(2, 2, 1)
        plt.rcParams.update({'font.size': 10})
        ax = axes[0][0]
        channel_lines = {key: [] for key in self.list}
        channel_colors = {}
        _shift = np.amax(list_ac_signal)-np.amin(list_ac_signal)
        # print(_shift)
        for i in range(0, len(self.list)):
            if self.list[i] in self.bad_channel:
                self.logger.error(f"skip bad channel: {self.list[i]}")
                continue
            plt.rcParams.update({'font.size': 10})
            _line, = ax.plot(list_time[i], list_ac_signal[i]+i*_shift, label=f'{self.list[i]} AC Signal')
            channel_colors[self.list[i]] = _line.get_color()

        ax.text(-0.05, 1.05, f"Signal (V)", fontsize=10, transform=plt.gca().transAxes)
        ax.set_xlabel('Time (S)', fontsize=10)
        ax.set_yticks([_shift*i for i in np.arange(0,len(self.list))])
        ax.set_yticklabels(self.list)
        # ax.legend()

        plt.subplot(2, 2, 3)
        plt.rcParams.update({'font.size': 10})
        table_data = np.array([[""]+self.list, ["RMS Level(V)"]+["{:.8f}".format(val) for val in list_rms_val],
                    ["Average Peak-to-Peak"]+["{:.8f}".format(val) for val in list_avg_peak_to_peak_val],
                    ["DC bias"]+["{:.8f}".format(val) for val in list_dc_bias]]).T
        _table = plt.table(cellText=table_data, cellLoc='center', loc='center', fontsize=[10,10,10])
        for (row, col), cell in _table.get_celld().items():
            cell.set_linewidth(0.3)
        plt.axis('off')

        plt.subplot(2, 2, 2)
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
                harmonic_index = np.argmin(np.abs(list_fft_freq[i] - h * list_ac_peak_freq[i]))
                harmonic_freq = list_fft_freq[i][harmonic_index]
                harmonic_dbv = list_fft_dbv[i][harmonic_index]
                harmonic_coords.append((harmonic_freq, harmonic_dbv))
                harmonic_data[k][i] = (harmonic_freq, harmonic_dbv)

            # Plot FFT of AC signal
            _line, = plt.plot(list_fft_freq[i], list_fft_dbv[i])
            channel_lines[self.list[i]].append(_line)

            _line, = plt.plot(list_ac_peak_freq[i], list_ac_peak_dbv[i], 'o',
                              color=self.adjust_color(channel_colors[self.list[i]]))
            channel_lines[self.list[i]].append(_line)

            _line = plt.axvline(float(list_ac_peak_freq[i]), linestyle='--',
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
        plt.xlim(1, self.sample_rate/2)
        # plt.ylim(-50, 20)
        plt.subplot(2, 2, 4)
        plt.rcParams.update({'font.size': 10})
        table_data = np.array([[""]+self.list,
                               ["Peak"]+["({:.2f}, {:.2f})".format(val1, val2) for val1, val2 in
                                         zip(list_ac_peak_freq, list_ac_peak_dbv)],
                               ["Harmonic 2"]+["({:.2f}, {:.2f})".format(val1, val2) for val1, val2 in
                               harmonic_data[0]],
                               ["Harmonic 3"]+["({:.2f}, {:.2f})".format(val1, val2) for val1, val2 in
                                                 harmonic_data[1]],
                               ["Harmonic 4"] + ["({:.2f}, {:.2f})".format(val1, val2) for val1, val2 in
                                                 harmonic_data[2]],
                               ["Harmonic 5"] + ["({:.2f}, {:.2f})".format(val1, val2) for val1, val2 in
                                                 harmonic_data[3]],
                               ]).T
        _table = plt.table(cellText=table_data, cellLoc='center', loc='center', fontsize=[10,10,10])
        for (row, col), cell in _table.get_celld().items():
            cell.set_linewidth(0.3)
        plt.axis('off')

        colors = list(channel_colors.values())
        # rax = plt.axes((0.025, 0.68, 0.05, 0.2))
        rax = plt.axes((0.925, 0.68, 0.05, 0.2))
        check = CheckButtons(
            ax=rax,
            labels=self.list,
            actives=[True for _ in range(len(self.list))],
            label_props={'color': colors},
            frame_props={'edgecolor': colors},
            check_props={'facecolor': colors},
        )

        def callback(label):
            for line in channel_lines[label]:
                line.set_visible(not line.get_visible())
                line.figure.canvas.draw_idle()

        check.on_clicked(callback)

        # plt.tight_layout(rect=(0.1, 0.0, 0.9, 0.95))
        if len(self.list):
            plt.show()
        plt.cla()
        plt.close("all")
        self.logger.info(f"finish: {self.sensor}")
        return ErrorCode.ERR_NO_ERROR

    def ppg_data(self, *args, **kwargs):
        self.logger.info(f"process {self.sensor} data")
        title = os.path.basename(self.data_file)
        # path = os.path.join(file_path, title)
        aggressor_name = title.replace(".csv", "")
        aggressor_name = aggressor_name.replace("PPG_Data_", "")
        list_avg = []
        list_timex = []
        list_hp_data = []
        list_sum_vector = []
        list_hp_noise = []
        list_hp_snr = []
        list_sum_vector = []
        # writelog(aggressor_name + ":\n", logpath)
        try:
            data = pd.read_csv(self.data_file, index_col=False)
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_FILE
        self.bad_channel = []
        fs = self.sample_rate
        start = int(self.data_drop[0])
        end = int(self.data_drop[1])
        for channel in self.list:
            try:
                _sig = data[channel].iloc[start:end]
                _avg = abs(np.mean(_sig))
                _sig_ac = _sig - _avg
                _err_code, _sig_ac = self.do_high_pass_filter(_sig_ac)
                if _err_code != ErrorCode.ERR_NO_ERROR:
                    return _err_code
                _err_code, _sig_ac = self.do_low_pass_filter(_sig_ac)
                if _err_code != ErrorCode.ERR_NO_ERROR:
                    return _err_code
                _err_code, _sig_ac = self.do_high_pass_filter(_sig_ac, axis=-1)
                if _err_code != ErrorCode.ERR_NO_ERROR:
                    return _err_code
                _noise = np.std(_sig_ac)
                _snr = 20 * math.log10(_avg / _noise)

                self.logger.debug(_avg, _noise, _snr)

                timex = np.linspace(0, len(_sig_ac) / fs, len(_sig_ac))
                sum_vector = np.array(_sig_ac)
                list_avg.append(_avg)
                list_timex.append(timex)
                list_hp_data.append(_sig_ac)
                list_sum_vector.append(sum_vector)
                list_hp_noise.append(_noise)
                list_hp_snr.append(_snr)
            except Exception as ex:
                self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
                self.logger.error("this channel have problem:" + title + channel)
                self.bad_channel.append(channel)
                continue

        fig = plt.figure(f"{self.sensor} v.s. {aggressor_name}", figsize=(20, 20))
        axes = fig.subplots(2, 2)
        channel_lines = {key: [] for key in self.list}
        channel_colors = {}
        _shift = np.amax(list_hp_data) - np.amin(list_hp_data)

        plt.subplot(2, 2, 1)
        plt.rcParams.update({'font.size': 10})
        ax = axes[0][0]
        for i in range(0, len(self.list)):
            if self.list[i] in self.bad_channel:
                self.logger.error(f"skip bad channel: {self.list[i]}")
                continue
            try:
                plt.rcParams.update({'font.size': 10})
                _line, = ax.plot(list_timex[i], list_hp_data[i]+i*_shift)
                channel_colors[self.list[i]] = _line.get_color()
            except Exception as ex:
                self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
                continue
        # ax.set_ylabel('Raw Cnt', fontsize=10)
        ax.text(-0.05, 1.05, f"Raw Cnt",
                 fontsize=10, transform=plt.gca().transAxes)
        ax.set_xlabel('Time (s)', fontsize=10)
        ax.set_yticks([_shift * i for i in np.arange(0, len(self.list))])
        ax.set_yticklabels(self.list, fontsize=10)

        plt.subplot(2, 2, 3)
        plt.rcParams.update({'font.size': 10})
        table_data = np.array(
            [[""] + self.list,
             ["avg."] + ["{:.8f}".format(val) for val in list_avg],
             ["noise"] + ["{:.8f}".format(val) for val in list_hp_noise],
             ["snr"] + ["{:.8f}".format(val) for val in list_hp_snr]
             ]).T
        table = plt.table(cellText=table_data, cellLoc='center', loc='center', fontsize=[10,10,10])
        # table.auto_set_font_size(False)
        table.scale(1, 2.5)
        for (row, col), cell in table.get_celld().items():
            cell.set_linewidth(0.3)
        plt.axis('off')

        plt.subplot(2, 2, 2)
        for i in range(0, len(self.list)):
            if self.list[i] in self.bad_channel:
                self.logger.error(f"skip bad channel: {self.list[i]}")
                continue
            try:
                plt.rcParams.update({'font.size': 10})
                FFT = 2.0 / len(list_sum_vector[i]) * abs(scipy.fft.fft(list_sum_vector[i]))
                freqs = scipy.fftpack.fftfreq(len(list_timex[i]), timex[1] - timex[0])

                _line, = plt.plot(freqs[1:int(len(freqs) / 2)], (FFT[1:int(len(freqs) / 2)]), color=channel_colors[self.list[i]])
                channel_lines[self.list[i]].append(_line)
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
        plt.xlim([0.1, fs / 2])
        # plt.ylim([-0.1, 5])
        plt.xlabel('frequency [Hz]', fontsize=10)
        # plt.ylabel('FFT[cnt/sqrt(Hz)]', fontsize=10)
        plt.text(-0.05, 1.05, f"FFT[cnt/sqrt(Hz)]",
                fontsize=10, transform=plt.gca().transAxes)

        plt.subplot(2, 2, 4)
        plt.axis('off')

        colors = list(channel_colors.values())
        # rax = plt.axes((0.025, 0.68, 0.05, 0.2))
        rax = plt.axes((0.91, 0.68, 0.06, 0.2))
        check = CheckButtons(
            ax=rax,
            labels=self.list,
            actives=[True for _ in range(len(self.list))],
            label_props={'color': colors},
            frame_props={'edgecolor': colors},
            check_props={'facecolor': colors},
        )

        def callback(label):
            for line in channel_lines[label]:
                line.set_visible(not line.get_visible())
                line.figure.canvas.draw_idle()
        check.on_clicked(callback)

        plt.show()
        plt.cla()
        plt.close("all")
        self.logger.info(f"finish: {self.sensor}")
        return ErrorCode.ERR_NO_ERROR

    def imu_data(self):
        try:
            self.logger.info(f"process {self.sensor} data")
            try:
                self.df_data = pd.read_csv(self.data_file, index_col=False)
            except Exception as ex:
                self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
                return ErrorCode.ERR_BAD_FILE
            _err_code, _data = self.do_data_conversion()
            if _err_code != ErrorCode.ERR_NO_ERROR:
                return _err_code
            self.do_plot_list(_data)
            return self.do_plot_list(_data)
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


# example
if __name__ == '__main__':
    dv = DataVisualization()
    dv.visualize(file=sys.argv[1], sensor="EMG",
                  channels=["CH1","CH2","CH3","CH5","CH6","CH7","CH11","CH13"], rate=float(sys.argv[2]), drop=0)