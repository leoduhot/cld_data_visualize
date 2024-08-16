# -*- coding: UTF-8 -*-
# import sys
import numpy as np
import pandas as pd
import logging
from enum import IntEnum
import json


class ErrorCode(IntEnum):
    ERR_NO_ERROR = 0,
    ERR_BAD_FILE = -1,
    ERR_BAD_DATA = -2,
    ERR_BAD_TYPE = -3,
    ERR_BAD_ARGS = -4,
    ERR_BAD_UNKNOWN = -255,


class RawDataParser:
    ref_key_names = {
        "emg":  ["CH3", "CH5"],
        "ppg":  ["measurement", "timestamp", "pd_1", "pd_2", "pd_3", "pd_4"],
        "imu":  ["Timestamp", "X-Axis", "Y-Axis", "Z-Axis"],
        "alt":  ["Pressure", "Temperature", "Timestamp"],
        "mag":  ["Compass X", "Compass Y", "Compass Z", "Temperature", "Timestamp"],
        "bti":  ["Force", "Temperature", "Timestamp", "Sensor"],
    }
    sensor_pattern = {
        "emg": "sending cmd: ad469x dump_last_stream emg_adc0@0",
        "ppg": "ppg print_samples",
        "imu": "imu get_samples",
        "alt": "press get_samples",
        "mag": "mag print_samples",
        "bti": "bti print_samples",
    }

    def __init__(self, *args, **kwargs):
        self.logger = kwargs["logger"] if 'logger' in kwargs else logging.getLogger()
        self.sensor = None

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

    def extract_sensor_data(self, _file, _sensor):
        try:
            _fh = open(_file, 'r')
            _fd = _fh.read()
            if _sensor == "emg":
                return self.extract_emg_data(_fd)
            else:
                _err, _json_data = self.extract_json_data(_fd, self.sensor_pattern[_sensor])
                if _err == ErrorCode.ERR_NO_ERROR:
                    _err, _df_data = self.convert_json_to_df(_json_data, _sensor)
                    if _err == ErrorCode.ERR_NO_ERROR:
                        # print(_df_data)
                        return _err, _df_data
                    else:
                        self.logger.error("convert json data failed!")
                else:
                    self.logger.error("get json data failed!")
            return ErrorCode.ERR_BAD_DATA, None
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_FILE, None

    def extract_emg_data(self, _data):
        try:
            _data_lines = _data.splitlines()
            _reg_index = _data_lines.index(self.sensor_pattern['emg'])
            self.logger.info(f"find [{self.sensor_pattern['emg']}] in {_reg_index}")
            values = list()
            col_line = _data_lines[_reg_index+1].strip().replace("(V)", "")
            col_line = col_line.replace(":", "")
            col = [val.strip().upper() for val in col_line.strip().split()]
            self.logger.info(f"col:{col}")
            for line in _data_lines[_reg_index+2:]:
                if "CMD_CMPT" != line[0:8]:
                    _row = [float(val) for val in line.strip().split()]
                    values.append(_row)
                else:
                    break
            _df = pd.DataFrame(np.array(values), columns=col)
            self.logger.debug(f"{__name__}: {len(_df)}")
            return ErrorCode.ERR_NO_ERROR, _df
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_DATA, None

    def extract_json_data(self, _data, _reg):
        try:
            is_json = False
            json_obj = list()
            json_decoded = list()
            _data_lines = _data.splitlines()
            _reg_index = _data_lines.index(_reg)
            self.logger.info(f"find [{_reg}] in {_reg_index}")
            for line in _data_lines[_reg_index:]:
                if line.startswith("      {"):
                    is_json = True
                    json_obj = list()
                elif line.startswith("      },"):
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

    # _ref_names, to check if the sample data is valid or not
    # _expect_columns, to specific the expected data
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

    def convert_json_to_df(self, _json_data, sensor=None):
        try:
            if sensor == "imu":
                return self.convert_imu_json_to_df(_json_data)
            elif sensor == "bti":
                return self.convert_bti_json_to_df(_json_data)
            elif sensor == "ppg":
                return self.convert_ppg_json_to_df(_json_data)
            else:
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

    def convert_imu_json_to_df(self, _json_data):
        try:
            samples_gyro = []
            samples_acc = []
            for obj in _json_data:
                if obj["desc"] == "IMU gyro data":
                    samples_gyro.append(obj["samples"])
                elif obj["desc"] == "IMU accelerometer data":
                    samples_acc.append(obj["samples"])
            _gyro_expected = self.ref_key_names["imu"]
            _err1, values_gyro = self.extract_df_values(samples_gyro, self.ref_key_names["imu"], _gyro_expected)
            _acc_expected = self.ref_key_names["imu"][1:]
            _err2, values_acc = self.extract_df_values(samples_acc, self.ref_key_names["imu"], _acc_expected)
            if _err1 == ErrorCode.ERR_NO_ERROR and _err2 == ErrorCode.ERR_NO_ERROR:
                values_all = [x + y for x, y in zip(values_gyro, values_acc)]
                col = ([_gyro_expected[0]] + ["gyro_" + x for x in _gyro_expected[1:]] +
                       ["acc_" + x for x in _acc_expected])
                _df = pd.DataFrame(np.array(values_all), columns=col)
                self.logger.debug(f"{__name__}: {len(_df)}")
                return ErrorCode.ERR_NO_ERROR, _df
            else:
                return ErrorCode.ERR_BAD_DATA, None
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_DATA, None

    def convert_bti_json_to_df(self, _json_data):
        try:
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
            print(f"{samples_sensor0}")
            _err0, values_0 = self.extract_df_values(samples_sensor0, self.ref_key_names["bti"], _expected)
            _err1, values_1 = self.extract_df_values(samples_sensor1, self.ref_key_names["bti"], _expected)
            if _err0 == ErrorCode.ERR_NO_ERROR and _err1 == ErrorCode.ERR_NO_ERROR:
                values_all = [x + y for x, y in zip(values_0, values_1)]
                col = (["sensor0_"+val for val in _expected] + ["sensor1_" + val for val in _expected])
                print(f"columns name:{col}")
                _df = pd.DataFrame(np.array(values_all), columns=col)
                self.logger.debug(f"{__name__}: {len(_df)}")
                return ErrorCode.ERR_NO_ERROR, _df
            else:
                return ErrorCode.ERR_BAD_DATA, None
        except Exception as ex:
            self.logger.error(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            return ErrorCode.ERR_BAD_DATA, None

    def convert_ppg_json_to_df(self, _json_data):
        try:
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


# example
# if __name__ == '__main__':
#     rdp = RawDataParser()
#     s = sys.argv[2].strip()
#
#     err, df_data = rdp.extract_sensor_data(sys.argv[1], s)
#     if err == ErrorCode.ERR_NO_ERROR:
#         print(df_data.to_string())
#     else:
#         print("convert json data failed!")
