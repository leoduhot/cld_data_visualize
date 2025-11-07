# -*- coding: UTF-8 -*-
# import sys
import os.path

import numpy as np
import pandas as pd
import logging
from enum import IntEnum
import json
import re
import csv


class OpCode(IntEnum):
    extract = 0,
    convert = 1,
    unknown = 2,


class ErrorCode(IntEnum):
    ERR_NO_ERROR = 0,
    ERR_BAD_FILE = -1,
    ERR_BAD_DATA = -2,
    ERR_BAD_TYPE = -3,
    ERR_BAD_ARGS = -4,
    ERR_BAD_PROJECT = -5,
    ERR_BAD_UNKNOWN = -255,


ErrorMsg = {
    f"{ErrorCode.ERR_BAD_FILE}": "ErrorCode.ERR_BAD_FILE",
    f"{ErrorCode.ERR_BAD_DATA}": "ErrorCode.ERR_BAD_DATA",
    f"{ErrorCode.ERR_BAD_TYPE}": "ErrorCode.ERR_BAD_DATA",
    f"{ErrorCode.ERR_BAD_ARGS}": "ErrorCode.ERR_BAD_ARGS",
    f"{ErrorCode.ERR_BAD_PROJECT}": "ErrorCode.ERR_BAD_PROJECT",
    f"{ErrorCode.ERR_BAD_UNKNOWN}": "ErrorCode.ERR_BAD_UNKNOWN",
}


#
# this class is base on Malibu project, other project should inherit from this class
#
class RawSensorDataParser:
    def __init__(self, **kwargs):
        self.logger = kwargs["logger"] if 'logger' in kwargs and kwargs['logger'] is not None else logging.getLogger()
        self.sensor = None
        self.project = None
        self.source_file = None
        self.target_file = None
        self.data = None

        self.sensor_data_func = {
            "emg": [self.extract_emg_data, self.convert_emg_data],
            "ppg": [self.extract_ppg_data, self.convert_ppg_data],
            "alt": [self.extract_alt_data, self.convert_alt_data],
            "imu": [self.extract_imu_data, self.convert_imu_data],
            "mag": [self.extract_mag_data, self.convert_mag_data],
            "bti": [self.extract_bti_data, self.convert_bti_data],
            "als": [self.extract_als_data, self.convert_als_data],
        }
        self.ref_key_names = {
            "emg":  ["CH03", "CH05", "CH07", "CH08", "CH10", "CH12", "CH13", "CH15"],
            "ppg":  ["measurement", "timestamp", "pd_1", "pd_2", "pd_3", "pd_4"],
            "imu":  ["Timestamp", "X-Axis", "Y-Axis", "Z-Axis", "Temperature"],
            "alt":  ["Pressure", "Temperature", "Timestamp"],
            "mag":  ["Compass X", "Compass Y", "Compass Z", "Temperature", "Timestamp"],
            "bti":  ["Force", "Temperature", "Timestamp", "Sensor"],
            "als":  ["Time", "Raw"]
        }
        self.sensor_pattern = {
            "emg": ["sending cmd: ad469x dump_last_stream emg_adc0@0"],
            "ppg": [r'\{(?:[^{}]*?"data": \[)', "FT> {", "ppg print_samples"],
            "imu": [r'\{(?:[^{}]*?"data": \[)', "FT> {", "imu get_samples"],
            "alt": [r'\{(?:[^{}]*?"data": \[)', "FT> {", "press get_samples"],
            "mag": [r'\{(?:[^{}]*?"data": \[)', "FT> {", "mag print_samples"],
            "bti": [r'\{(?:[^{}]*?"data": \[)', "FT> {", "bti print_samples"],
            "als": ["Reading samples", "millilux, timestamp"],
            "def": [r'\{(?:[^{}]*?"data": \[)', "FT> {"],
        }

    '''
        _source_file: raw data file pull path, in text format
        _data: input data, in DataFrame format
        _sensor: sensor name
        _project: project name
        _target_file: full file path to save the converted data, in csv format
    '''
    def extract_sensor_data(self, _source_file: str = None, _data: pd.DataFrame = None, _sensor: str = None,
                            _project: str = None, _target_file: str = None) -> (ErrorCode, pd.DataFrame | None):
        try:
            self.sensor = _sensor.lower()[0:3]   # get first 3 char, in case als100, als10, imu_120, ...
            if self.sensor not in self.sensor_data_func:
                return ErrorCode.ERR_BAD_ARGS, None
            self.project = _project
            # self.source_file = _source_file
            # self.target_file = _target_file
            # get data from file fist, if not available, get from _data
            self.data = None
            if _source_file is not None and os.path.exists(_source_file):
                _fh = open(_source_file, 'r', errors='ignore')
                self.data = _fh.read()
            if self.data is None:
                self.data = _data
            err_code, _df = self.sensor_data_func[self.sensor][OpCode.extract]()
            if _target_file is not None and err_code == ErrorCode.ERR_NO_ERROR:
                _df.to_csv(_target_file, index=False)
            # self.target_file = None
            # self.source_file = None
            return err_code, _df
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            self.source_file = None
            return ErrorCode.ERR_BAD_DATA, None

    '''
        _source_file: raw data file pull path, in csv format
        _data: input data, in DataFrame format
        _sensor: sensor name
        _project: project name
        _target_file: full file path to save the converted data, in csv format
    '''
    def convert_sensor_data(self, _source_file=None, _data: pd.DataFrame = None, _sensor: str = None,
                            _project: str = None, _target_file: str = None) -> (ErrorCode, pd.DataFrame | None):
        try:
            self.sensor = _sensor.lower()[0:3]   # get first 3 char, in case als100, als10, imu_120, ...
            if self.sensor not in self.sensor_data_func:
                return ErrorCode.ERR_BAD_ARGS, None
            self.project = _project
            self.source_file = _source_file
            # self.target_file = _target_file
            # get data from file fist, if not available, get from _data
            self.data = None
            if _source_file is not None and os.path.exists(_source_file):
                _fh = open(_source_file, 'r', errors='ignore')
                self.data = _fh.read()
            if self.data is None:
                self.data = _data
            err_code, _df = self.sensor_data_func[self.sensor][OpCode.convert]()
            if _target_file is not None and err_code == ErrorCode.ERR_NO_ERROR:
                _df.to_csv(_target_file, index=False)
            # self.target_file = None
            return err_code, _df
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            # self.target_file = None
            return ErrorCode.ERR_BAD_DATA, None

    # extract data from command raw output
    def extract_emg_data(self):
        try:
            _data_lines = self.data.splitlines()
            values = list()
            for line in _data_lines:
                if re.match(r'^(\d\.\d{6}\t){8}$', line):
                    _row = [float(val) for val in line.strip().split()]
                    values.append(_row)

            col = self.ref_key_names["emg"]

            _df = pd.DataFrame(np.array(values), columns=col)
            self.logger.debug(f"{__name__}: {len(_df)}")
            return ErrorCode.ERR_NO_ERROR, _df
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_DATA, None

    def extract_ppg_data(self):
        try:
            _err, _json_data = self.extract_json_data(self.data, self.sensor_pattern[self.sensor])
            if _err != ErrorCode.ERR_NO_ERROR:
                return ErrorCode.ERR_BAD_DATA, None

            mes_samples = {}
            values = {}
            for obj in _json_data:
                err_code, _mes = self.read_value(obj["samples"], "measurement")
                if err_code == ErrorCode.ERR_NO_ERROR:
                    if str(_mes) in mes_samples:
                        mes_samples[str(_mes)].append(obj["samples"])
                    else:
                        mes_samples[str(_mes)] = [obj["samples"]]
            _expected = self.ref_key_names["ppg"][1:]
            for _key in mes_samples:
                _err, _values = self.extract_df_values(mes_samples[_key], self.ref_key_names["ppg"], _expected)
                if _err == ErrorCode.ERR_NO_ERROR:
                    values[_key] = _values

            _keys = list(values.keys())
            values_all = values[_keys[0]]
            col = []
            for _key in _keys:
                if _key != _keys[0]:
                    values_all = [x + y for x, y in zip(values_all, values[_key])]
                col = col+["MES"+_key+"_"+val for val in _expected]
            _df = pd.DataFrame(np.array(values_all), columns=col)
            self.logger.debug(f"{__name__}: {len(_df)}")
            return ErrorCode.ERR_NO_ERROR, _df
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_DATA, None

    def extract_alt_data(self):
        try:
            _err, _json_data = self.extract_json_data(self.data, self.sensor_pattern[self.sensor])
            if _err != ErrorCode.ERR_NO_ERROR:
                return ErrorCode.ERR_BAD_DATA, None
            return self.convert_json_to_df(_json_data, self.sensor)
            # samples = [obj["samples"] for obj in _json_data]
            # _err, values = self.extract_df_values(samples, self.ref_key_names[self.sensor], self.ref_key_names[self.sensor])
            # if _err == ErrorCode.ERR_NO_ERROR:
            #     _df = pd.DataFrame(np.array(values), columns=self.ref_key_names[self.sensor])
            #     self.logger.debug(f"{__name__}: {self.sensor}: {len(_df)}")
            #     return ErrorCode.ERR_NO_ERROR, _df
            # else:
            #     return _err, None
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_DATA, None

    def extract_mag_data(self):
        try:
            _err, _json_data = self.extract_json_data(self.data, self.sensor_pattern[self.sensor])
            if _err != ErrorCode.ERR_NO_ERROR:
                return ErrorCode.ERR_BAD_DATA, None
            return self.convert_json_to_df(_json_data, self.sensor)
            # samples = [obj["samples"] for obj in _json_data]
            # _err, values = self.extract_df_values(samples, self.ref_key_names[self.sensor], self.ref_key_names[self.sensor])
            # if _err == ErrorCode.ERR_NO_ERROR:
            #     _df = pd.DataFrame(np.array(values), columns=self.ref_key_names[self.sensor])
            #     self.logger.debug(f"{__name__}: {self.sensor}: {len(_df)}")
            #     return ErrorCode.ERR_NO_ERROR, _df
            # else:
            #     return _err, None
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_DATA, None

    def extract_imu_data(self):
        try:
            _err, _json_data = self.extract_json_data(self.data, self.sensor_pattern[self.sensor])
            if _err != ErrorCode.ERR_NO_ERROR:
                return ErrorCode.ERR_BAD_DATA, None

            samples_gyro = []
            samples_acc = []
            samples_temper = []
            for obj in _json_data:
                if obj["desc"] == "IMU gyro data":
                    samples_gyro.append(obj["samples"])
                elif obj["desc"] == "IMU accelerometer data":
                    samples_acc.append(obj["samples"])
                elif obj["desc"] == "IMU temperature data":
                    samples_temper.append(obj["samples"])
            _gyro_expected = self.ref_key_names["imu"][0:4]
            _err1, values_gyro = self.extract_df_values(samples_gyro, self.ref_key_names["imu"], _gyro_expected)
            _acc_expected = self.ref_key_names["imu"][1:4]
            _err2, values_acc = self.extract_df_values(samples_acc, self.ref_key_names["imu"], _acc_expected)
            _temper_expected = self.ref_key_names["imu"][4:]
            _err3, values_temper = self.extract_df_values(samples_temper, self.ref_key_names["imu"], _temper_expected)
            if _err1 == ErrorCode.ERR_NO_ERROR and _err2 == ErrorCode.ERR_NO_ERROR and _err3 == ErrorCode.ERR_NO_ERROR:
                values_all = [x + y + z for x, y, z in zip(values_gyro, values_acc, values_temper)]
                col = ([_gyro_expected[0]] + ["gyro_" + x for x in _gyro_expected[1:]] +
                       ["acc_" + x for x in _acc_expected] + _temper_expected)
                _df = pd.DataFrame(np.array(values_all), columns=col)
                self.logger.debug(f"{__name__}: {len(_df)}")
                return ErrorCode.ERR_NO_ERROR, _df
            else:
                return ErrorCode.ERR_BAD_DATA, None
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_DATA, None

    def extract_bti_data(self):
        try:
            _err, _json_data = self.extract_json_data(self.data, self.sensor_pattern[self.sensor])
            if _err != ErrorCode.ERR_NO_ERROR:
                return ErrorCode.ERR_BAD_DATA, None

            samples_sensor0 = []
            samples_sensor1 = []
            for obj in _json_data:
                err_code, _mes = self.read_value(obj["samples"], "Sensor")
                if err_code == ErrorCode.ERR_NO_ERROR and _mes == 0:
                    samples_sensor0.append(obj["samples"])
                elif err_code == ErrorCode.ERR_NO_ERROR and _mes == 1:
                    samples_sensor1.append(obj["samples"])
                else:
                    continue
            _expected = self.ref_key_names["bti"][:-1]
            # print(f"{samples_sensor0}")
            _err0, values_0 = self.extract_df_values(samples_sensor0, self.ref_key_names["bti"], _expected)
            _err1, values_1 = self.extract_df_values(samples_sensor1, self.ref_key_names["bti"], _expected)
            if _err0 == ErrorCode.ERR_NO_ERROR and _err1 == ErrorCode.ERR_NO_ERROR:
                values_all = [x + y for x, y in zip(values_0, values_1)]
                col = (["sensor0_"+val for val in _expected] + ["sensor1_" + val for val in _expected])
                # print(f"columns name:{col}")
                _df = pd.DataFrame(np.array(values_all), columns=col)
                self.logger.debug(f"{__name__}: {len(_df)}")
                return ErrorCode.ERR_NO_ERROR, _df
            else:
                return ErrorCode.ERR_BAD_DATA, None
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_DATA, None

    def extract_als_data(self):
        try:
            _err, _json_data = self.extract_json_data(self.data, self.sensor_pattern[self.sensor])
            if _err != ErrorCode.ERR_NO_ERROR:
                return ErrorCode.ERR_BAD_DATA, None
            return self.convert_json_to_df(_json_data, self.sensor)
            # samples = [obj["samples"] for obj in _json_data]
            # _err, values = self.extract_df_values(samples, self.ref_key_names[self.sensor], self.ref_key_names[self.sensor])
            # if _err == ErrorCode.ERR_NO_ERROR:
            #     _df = pd.DataFrame(np.array(values), columns=self.ref_key_names[self.sensor])
            #     self.logger.debug(f"{__name__}: {self.sensor}: {len(_df)}")
            #     return ErrorCode.ERR_NO_ERROR, _df
            # else:
            #     return _err, None
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_DATA, None

    # convert adc code to target value, and save to csv file
    def convert_emg_data(self):
        return ErrorCode.ERR_NO_ERROR, self.data

    def convert_ppg_data(self):
        return ErrorCode.ERR_NO_ERROR, self.data

    def convert_imu_data(self):
        return ErrorCode.ERR_NO_ERROR, self.data

    def convert_alt_data(self):
        return ErrorCode.ERR_NO_ERROR, self.data

    def convert_mag_data(self):
        return ErrorCode.ERR_NO_ERROR, self.data

    def convert_bti_data(self):
        return ErrorCode.ERR_NO_ERROR, self.data

    def convert_als_data(self):
        return ErrorCode.ERR_NO_ERROR, self.data

    def extract_json_data(self, _data, _reg=None):
        try:
            is_json = False
            json_obj = list()
            json_decoded = list()
            start_index = 0
            if _reg is not None:
                for reg in _reg:
                    matches = re.search(reg, _data, re.MULTILINE)
                    if matches:
                        self.logger.info(f"find {matches}")
                        start_index = matches.end()
                        break
            _data_lines = _data[start_index:].splitlines()
            for line in _data_lines:
                if line.startswith("      {"):
                    is_json = True
                    json_obj = list()
                elif is_json and line.startswith("      },"):  # ignore "}," if previous "{" is not found
                    is_json = False
                    json_obj.append("      }")
                    _json_data = json.loads("\n".join(json_obj))
                    json_decoded.append(_json_data)
                if is_json:
                    json_obj.append(line)
            return ErrorCode.ERR_NO_ERROR, json_decoded
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_DATA, None

    def convert_json_to_df(self, _json_data, sensor=None):
        try:
            samples = [obj["samples"] for obj in _json_data]
            _err, values = self.extract_df_values(samples, self.ref_key_names[sensor], self.ref_key_names[sensor])
            if _err == ErrorCode.ERR_NO_ERROR:
                _df = pd.DataFrame(np.array(values), columns=self.ref_key_names[sensor])
                self.logger.debug(f"{__name__}: {sensor}: {len(_df)}")
                return ErrorCode.ERR_NO_ERROR, _df
            else:
                return _err, None
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_DATA, None

    def extract_df_values(self, _samples, _ref_names, _expect_columns):
        try:
            values_all = list()
            for sample in _samples:
                # print(sample)
                is_valid = True
                for item in sample:
                    # print(f"item:{item}")
                    if item["name"] not in _ref_names:
                        is_valid = False
                        break
                    else:
                        continue
                if is_valid:
                    values_row = [item["value"] for item in sample if item["name"] in _expect_columns]
                    values_all.append(values_row)
            self.logger.debug(f"{__name__}: {len(values_all)}")
            return ErrorCode.ERR_NO_ERROR, values_all
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_DATA, []

    def read_value(self, _sample, _name):
        try:
            for item in _sample:
                if item["name"] == _name:
                    self.logger.debug(f"value of [{_name}] is {item['value']}")
                    return ErrorCode.ERR_NO_ERROR, item["value"]
                else:
                    continue
            return ErrorCode.ERR_BAD_DATA, ErrorCode.ERR_BAD_UNKNOWN
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_DATA, ErrorCode.ERR_BAD_UNKNOWN


class MalibuSensorDataParser(RawSensorDataParser):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class BaliSensorDataParser(RawSensorDataParser):
    def extract_emg_data(self):
        try:
            if self.data is None:
                self.logger.error("data is None!")
                return ErrorCode.ERR_BAD_DATA, None

            start_idx = self.data.find("{")
            end_idx = self.data.rfind("}")
            ch_num = 20
            self.logger.debug(f"{start_idx}, {end_idx}")
            js_obj = json.loads(self.data[start_idx: end_idx + 1])
            arr = np.array(js_obj["output"]["adc_data"])
            self.logger.debug(f"arr length {len(arr)}")
            output_arr = np.reshape(arr, (-1, ch_num*2))
            base_timestamp = 0
            # Decompress timestamps
            for i in range(len(output_arr)):
                output_arr[i][1] = output_arr[i][1] + base_timestamp
                base_timestamp = output_arr[i][1]
                for j in range(1, ch_num):
                    output_arr[i][2 * j + 1] = output_arr[i][2 * j + 1] + base_timestamp
            # Decompress channel data
            for i in range(1, len(output_arr)):
                for j in range(0, ch_num):
                    output_arr[i][2 * j] = output_arr[i][2 * j] + output_arr[i - 1][2 * j]

            df = pd.DataFrame(output_arr)
            df.columns = ["ch0", "ts0", "ch1", "ts1", "ch2", "ts2", "ch3", "ts3", "ch4", "ts4", "ch5", "ts5", "ch6",
                          "ts6", "ch7", "ts7", "ch8", "ts8", "ch9", "ts9", "ch10", "ts10", "ch11", "ts11",
                          "ch12", "ts12", "ch13", "ts13", "ch14", "ts14", "ch15", "ts15", "ch16", "ts16", "ch17",
                          "ts17", "ch18", "ts18", "ch19", "ts19"]
            self.logger.debug(f"{__name__}: {len(df)}")
            return ErrorCode.ERR_NO_ERROR, df
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_DATA, None

    def extract_mag_data(self):
        return self.extract_other_sensors_data("mag")

    def extract_alt_data(self):
        return self.extract_other_sensors_data("alt")

    def extract_ppg_data(self):
        try:
            if self.data is None:
                self.logger.error("Data is None or sensor is not supported!")
                return ErrorCode.ERR_BAD_DATA, None

            start_idx = self.data.find("{")
            end_idx = self.data.rfind("}")
            self.logger.debug(f"{start_idx}, {end_idx}")
            js_obj = json.loads(self.data[start_idx: end_idx + 1])
            output_arr = [[],]

            if "ppg_data" not in js_obj["output"]:
                return ErrorCode.ERR_BAD_DATA, None
            arr = list(np.array(js_obj["output"]["ppg_data"]))
            arr = np.reshape(arr, (-1, 4))
            self.logger.debug(f"arr length {len(arr)}")
            self.logger.debug(f"arr \n{arr}")
            _base = arr[0]
            for i in range(1, len(arr)):
                for j in range(4):
                    arr[i][j] = arr[0][j] + arr[i][j]

            # output_arr = np.column_stack(output_arr)
            output_arr = np.array(arr).T
            output_arr = np.column_stack(output_arr)
            self.logger.debug(f"output_arr {output_arr}")
            # print(f"output_arr:\n {output_arr}")
            df = pd.DataFrame(output_arr)
            df.columns = ["ppg_data-0", "ppg_data-1", "ppg_data-2", "ppg_data-3"]
            return ErrorCode.ERR_NO_ERROR, df
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_DATA, None

    def extract_imu_data(self):
        try:
            json_keys = ["accel(micro-g)", "gyro(micro-dps)", "temp(micro-degrees)", "timestamp"]
            final_column_name = ["accel(micro-g)-X", "accel(micro-g)-Y", "accel(micro-g)-Z",
                                 "gyro(micro-dps)-X", "gyro(micro-dps)-Y", "gyro(micro-dps)-Z",
                                 "temp(micro-degrees)", "timestamp"]
            if self.data is None:
                self.logger.error("Data is None or sensor is not supported!")
                return ErrorCode.ERR_BAD_DATA, None

            start_idx = self.data.find("{")
            end_idx = self.data.rfind("}")
            self.logger.debug(f"{start_idx}, {end_idx}")
            js_obj = json.loads(self.data[start_idx: end_idx + 1])
            output_arr = []
            for key in json_keys:
                if key not in js_obj["output"]:
                    continue
                arr = list(np.array(js_obj["output"][key]))
                if key == "accel(micro-g)" or key == "gyro(micro-dps)":
                    arr = np.array(np.reshape(arr, (-1, 3))).T
                    for i in range(3):
                        output_arr.append(arr[i])
                    self.logger.debug(f"arr:\n {arr}")
                else:
                    output_arr.append(arr)
                    self.logger.debug(f"arr:\n {arr}")
                self.logger.debug(f"arr length {len(arr)}")
            output_arr = np.column_stack(output_arr)
            self.logger.debug(f"output_arr {output_arr}")
            # print(f"output_arr:\n {output_arr}")
            df = pd.DataFrame(output_arr)
            df.columns = final_column_name
            return ErrorCode.ERR_NO_ERROR, df
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_DATA, None

    def extract_other_sensors_data(self, _sensor):
        try:
            sensor_param = {
                "alt": ["press_data(Pa)", "temp_data"],
                "ppg": ["ppg_data"],
                "mag": ["mag_x(micro gauss)", "mag_y(micro gauss)", "mag_z(micro gauss)", "temp(celsius)", "timestamps"],
            }
            if self.data is None or _sensor not in sensor_param:
                self.logger.error("Data is None or sensor is not supported!")
                return ErrorCode.ERR_BAD_DATA, None

            start_idx = self.data.find("{")
            end_idx = self.data.rfind("}")
            self.logger.debug(f"{start_idx}, {end_idx}")
            js_obj = json.loads(self.data[start_idx: end_idx + 1])
            output_arr = []
            for key in sensor_param[_sensor]:
                if key not in js_obj["output"]:
                    continue
                arr = list(np.array(js_obj["output"][key]))
                self.logger.debug(f"arr length {len(arr)}")
                output_arr.append(arr)
            output_arr = np.column_stack(output_arr)
            self.logger.debug(f"output_arr {output_arr}")
            # print(f"output_arr:\n {output_arr}")
            df = pd.DataFrame(output_arr)
            df.columns = sensor_param[_sensor]
            return ErrorCode.ERR_NO_ERROR, df
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_DATA, None

    def convert_emg_data(self):
        df_data = pd.DataFrame(self.data[1:], columns=self.data[0])
        df_data = (df_data.sub(4096)).div(4096)
        return df_data


class TychoSensorDataParser(RawSensorDataParser):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def extract_emg_data(self):
        try:
            start_idx = self.data.find("{")
            end_idx = self.data.rfind("}")
            ch_num = 20
            self.logger.debug(f"{start_idx}, {end_idx}")
            js_obj = json.loads(self.data[start_idx: end_idx + 1])
            arr = np.array(js_obj["output"]["adc_data"])
            self.logger.debug(f"arr length {len(arr)}")
            output_arr = np.reshape(arr, (-1, ch_num*2))
            base_timestamp = 0
            # Decompress timestamps
            for i in range(len(output_arr)):
                output_arr[i][1] = output_arr[i][1] + base_timestamp
                base_timestamp = output_arr[i][1]
                for j in range(1, ch_num):
                    output_arr[i][2 * j + 1] = output_arr[i][2 * j + 1] + base_timestamp
            # Decompress channel data
            for i in range(1, len(output_arr)):
                for j in range(0, ch_num):
                    output_arr[i][2 * j] = output_arr[i][2 * j] + output_arr[i - 1][2 * j]

            df = pd.DataFrame(output_arr)
            df.columns = ["ch1", "ts1", "ch3", "ts3", "ch4", "ts4", "ch6", "ts6", "ch7", "ts7", "ch9", "ts9", "ch10",
                          "ts10", "ch11", "ts11", "ch12", "ts12", "ch13", "ts13", "ch14", "ts14", "ch15", "ts15",
                          "ch16", "ts16", "ch17", "ts17", "ch18", "ts18", "ch19", "ts19", "ch20", "ts20", "ch21",
                          "ts21", "ch22", "ts22", "ch24", "ts24"]
            # df = (df.sub(4096)).div(4096)
            self.logger.debug(f"{__name__}: {len(df)}")
            return ErrorCode.ERR_NO_ERROR, df
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_DATA, None


class CeresSensorDataParser(RawSensorDataParser):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def extract_emg_data(self):
        try:
            if self.data is None:
                self.logger.error("Data is None!")
                return ErrorCode.ERR_BAD_DATA, None
            start_idx = self.data.find("{")
            end_idx = self.data.rfind("}")
            ch_num = 8
            self.logger.debug(f"{start_idx}, {end_idx}")
            js_obj = json.loads(self.data[start_idx: end_idx + 1])
            arr = np.array(js_obj["output"]["adc_data"])
            self.logger.debug(f"arr length {len(arr)}")
            output_arr = np.reshape(arr, (-1, ch_num*2))
            base_timestamp = 0
            # Decompress timestamps
            for i in range(len(output_arr)):
                output_arr[i][1] = output_arr[i][1] + base_timestamp
                base_timestamp = output_arr[i][1]
                for j in range(1, ch_num):
                    output_arr[i][2 * j + 1] = output_arr[i][2 * j + 1] + base_timestamp
            # Decompress channel data
            for i in range(1, len(output_arr)):
                for j in range(0, ch_num):
                    output_arr[i][2 * j] = output_arr[i][2 * j] + output_arr[i - 1][2 * j]

            df = pd.DataFrame(output_arr)
            df.columns = ["ch1", "ts1", "ch2", "ts2", "ch3", "ts3", "ch5", "ts5", "ch6", "ts6", "ch7", "ts7",
                          "ch11", "ts11", "ch13", "ts13"]
            df = (df.div(65536)).mul(5)
            self.logger.debug(f"{__name__}: {len(df)}")
            return ErrorCode.ERR_NO_ERROR, df
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_DATA, None

    def convert_emg_data(self):
        try:
            max_len = max(len(row) for row in self.data)
            raw_data = np.array([row + [''] * (max_len - len(row)) for row in self.data]).T
            df = pd.DataFrame(raw_data[1:], columns=raw_data[0])
            new_columns = list()
            valid_columns = list()
            station_name = ""
            for item in df.columns:
                if len(df[item].values[0]) == 0:
                    station_name = item
                    new_columns.append(item)
                else:
                    new_columns.append(f"{station_name}_{item}")
                    valid_columns.append(f"{station_name}_{item}")
            df.columns = new_columns
            df = df[valid_columns]
            for name in df.columns:
                if "EMG" in name:
                    df[name] = (df[name].replace('', np.nan).astype(float).div(65536)).mul(5)
                else:
                    df[name] = df[name].replace('', np.nan).astype(float)
            return ErrorCode.ERR_NO_ERROR, df
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_FILE, None


class GEN2SensorDataParser(RawSensorDataParser):
    def extract_emg_data(self):
        try:
            if self.data is None:
                self.logger.error("Data is None!")
                return ErrorCode.ERR_BAD_DATA, None
            start_idx = self.data.find("{")
            end_idx = self.data.rfind("}")
            ch_num = 20
            self.logger.debug(f"{start_idx}, {end_idx}")
            js_obj = json.loads(self.data[start_idx: end_idx + 1])
            arr = np.array(js_obj["output"]["adc_data"])
            self.logger.debug(f"arr length {len(arr)}")
            output_arr = np.reshape(arr, (-1, ch_num*2))
            base_timestamp = 0
            # Decompress timestamps
            for i in range(len(output_arr)):
                output_arr[i][1] = output_arr[i][1] + base_timestamp
                base_timestamp = output_arr[i][1]
                for j in range(1, ch_num):
                    output_arr[i][2 * j + 1] = output_arr[i][2 * j + 1] + base_timestamp
            # Decompress channel data
            for i in range(1, len(output_arr)):
                for j in range(0, ch_num):
                    output_arr[i][2 * j] = output_arr[i][2 * j] + output_arr[i - 1][2 * j]

            df = pd.DataFrame(output_arr)
            df.columns = ["ch0", "ts0", "ch1", "ts1", "ch2", "ts2", "ch3", "ts3", "ch4", "ts4", "ch5", "ts5", "ch6",
                          "ts6", "ch7", "ts7", "ch8", "ts8", "ch9", "ts9", "ch10", "ts10", "ch11", "ts11",
                          "ch12", "ts12", "ch13", "ts13", "ch14", "ts14", "ch15", "ts15", "ch16", "ts16", "ch17",
                          "ts17", "ch18", "ts18", "ch19", "ts19"]
            self.logger.debug(f"{__name__}: {len(df)}")
            return ErrorCode.ERR_NO_ERROR, df
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_DATA, None


def RawDataParser(project="malibu", **kwarge):
    parser = {
        "malibu": MalibuSensorDataParser,
        "ceres": CeresSensorDataParser,
        "bali": BaliSensorDataParser,
        "tycho": TychoSensorDataParser,
        "gen2": GEN2SensorDataParser,
    }
    if project in parser:
        return parser[project](**kwarge)
    else:
        return MalibuSensorDataParser(**kwarge)


# example
if __name__ == '__main__':
    import sys
    rdp = RawDataParser(project="bali")
    # err, df_data = rdp.convert_ceres_test_data(sys.argv[1])
    # if err == ErrorCode.ERR_NO_ERROR:
    #     df_data.to_csv("test.csv", index=False)
    s = sys.argv[2].strip()

    err, df_data = rdp.extract_sensor_data(_source_file=sys.argv[1], _sensor=s, _project="03")
    if err == ErrorCode.ERR_NO_ERROR:
        print(df_data.to_string())
        df_data.to_csv(f"{s}.csv", index=False)
    else:
        print("convert json data failed!")
