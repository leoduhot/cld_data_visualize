# Author : Eric Si
# E-mail : eric.si@oculus.com
# Version: 0.5.0
# Date   : 2024-06-09

import os, sys
import argparse
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.gridspec import GridSpec
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import re
import logging
from data_visualization_utility import ErrorCode
import datetime
# import tkinter as tk


class SummaryDataParser:
    def __init__(self, *args, **kwargs):
        self.logger = kwargs["logger"] if "logger" in kwargs else logging.getLogger()
        self.root = kwargs["root"] if "root" in kwargs else None
        self.channels = []
        self.sensor = "others"
        self.data_file = None
        self.markers = []
        self.fig = None
        self.channel_lines = {}
        self.df_data = None

        self.main_funcs = {
            'alt': self.plot_emg_histogram,
            'bti': self.plot_emg_histogram,
            'mag': self.plot_emg_histogram,
            'emg': self.plot_emg_histogram,
            'imu': self.plot_emg_histogram,
            'ppg': self.plot_emg_histogram,
            'als1hz': self.plot_emg_histogram,
            'als10hz': self.plot_emg_histogram
        }

    def summary_data_visualize(self, *args, **kwargs):
        self.logger.info(f"start summary_data_visualize ...")
        self.channels = kwargs["channels"] if "channels" in kwargs else []
        self.sensor = kwargs["sensor"] if "sensor" in kwargs else "others"
        self.data_file = kwargs["file"] if "file" in kwargs else None
        self.markers = []
        self.fig = None
        self.channel_lines = {}

        if self.data_file is not None:
            try:
                self.df_data = pd.read_csv(self.data_file)
                self.df_data = self.df_data.iloc[:, 3:]
            except Exception as ex:
                self.logger.error(f"Exception: {str(ex)}")
                return ErrorCode.ERR_BAD_FILE
        else:
            self.df_data = kwargs["data"] if "data" in kwargs else None

        return self.main_funcs[self.sensor.lower()]()

    def extract_aggressors(self, victim, data):
        pass

    def extract_channels(self, victim, data):
        pass

    def extract_data_type(self, victim, data):
        pass

    def plot_emg_histogram(self, filename=None):
        try:
            num_of_columns = len(self.channels)

            # for i, ch in enumerate(self.channels):
            x = 3*len(self.channels)
            fig = plt.figure(f"{self.sensor}", figsize=(x, 12))
            fig.suptitle(self.sensor, fontsize=16)
            gs = GridSpec(8, num_of_columns, figure=fig)

            ax_main = fig.add_subplot(gs[0:3, :])
            # ch_data = [data.iloc[:, j].dropna() for j in range(group_data_index[i], data.shape[1], group_size)]
            ch_data = [self.df_data[ch].dropna() for ch in self.channels]
            ax_main.boxplot(ch_data, patch_artist=True)
            # ax_main.set_ylim([0.8, 1.3])
            ax_main.set_xticklabels([re.sub(r"^.*_data_", "", val, flags=re.IGNORECASE) for val in self.channels])
            base_mean = self.df_data.loc[:, self.channels[0]].mean()
            ax_main.axhline(base_mean, color='g', linestyle='-.')
            # ax_main.axhline(1.2, color='b', linestyle='-.')

            for j in range(num_of_columns):
                ax_hist = fig.add_subplot(gs[3:6, j])
                ax_hist.hist(ch_data[j], orientation='horizontal')
                # plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, loc: f"{x:.3e}"))

            for k in range(num_of_columns):
                ax_label = fig.add_subplot(gs[6:8, k])
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
                if 'SN' in self.df_data and outlier_count:
                    self.logger.warning(f"outliers:")
                    for i, v in zip(outliers.index, outliers):
                        self.logger.warning(f"index {i}, {self.df_data['SN'][i]}, {self.channels[k]}, {v}")
                elif outlier_count:
                    self.logger.warning(f"outliers:")
                    for i, v in zip(outliers.index, outliers):
                        self.logger.warning(f"index {i}, {self.channels[k]}, {v}")
                #     sn_list = [f"{self.df_data['SN'][i]}: {v}" for i, v in zip(outliers.index, outliers)]
                # else:
                #     sn_list = list()
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
                ] # + sn_list

                ax_label.text(0.0, 0.98, "\n".join(text_list), ha='left', va='top', fontname='monospace')
                ax_label.axis('off')
                # r_colors = ['lightgrey', '#eee9e9']
                r_colors = ['#e8e8e8', '#fffafa']
                rect = patches.Rectangle((0, 0), 1, 0.98, transform=ax_label.transAxes, color=r_colors[k % 2])
                ax_label.add_patch(rect)
            if filename:
                sub_png_file = filename + '.png'
            else:
                time_stamp = datetime.datetime.now()
                postfix = time_stamp.strftime("%Y%m%d_%H%M%S")
                sub_png_file = f"{self.sensor}_{postfix}.png"
            plt.tight_layout(rect=[0, 0, 1, 1])
            plt.savefig(sub_png_file)
            self.logger.info(f"Saved to file {sub_png_file}")
            plt.show()
            # # 创建一个Toplevel窗口
            # plot_window = tk.Toplevel(self.root)
            # plot_window.title(self.sensor)
            #
            # # 将图形添加到Toplevel窗口中
            # canvas = FigureCanvasTkAgg(fig, master=plot_window)
            # canvas.draw()
            # canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
            #
            # # 添加导航工具栏
            # toolbar = NavigationToolbar2Tk(canvas, plot_window)
            # canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
            return ErrorCode.ERR_NO_ERROR
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_UNKNOWN

if __name__ == "__main__":
    sdp = SummaryDataParser()
    df_data = pd.read_csv(sys.argv[1], index_col=False)
    sensor = sys.argv[2]
    print(df_data.columns)
    channels=input("select channels:")
    channels = channels.split(";")
    print("channels:",channels)
    sdp.summary_data_visualize(data=df_data, sensor=sensor, channels=channels)
