"""
History:
20220315: initialize

"""
# -*- coding: UTF-8 -*-

import logging
from datetime import datetime
import csv
import os
import sys


class MyLogger:
    def __init__(self, **kwargs):
        is_to_file = kwargs['save'] if 'save' in kwargs else False
        log_level = kwargs['level'] if 'level' in kwargs else "info"
        log_name = kwargs['name'] if 'name' in kwargs else f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self.logger = logging.getLogger("emulator")
        self.logger.setLevel(self.get_log_level(log_level))
        formatter = logging.Formatter("%(asctime)s %(filename)s %(lineno)s %(levelname)s %(message)s")
        log_strm_handler = logging.StreamHandler()
        log_strm_handler.setLevel(self.get_log_level(log_level))
        log_strm_handler.setFormatter(formatter)
        self.logger.addHandler(log_strm_handler)
        if is_to_file:
            log_file_handler = logging.FileHandler(filename=log_name, mode="w")
            log_file_handler.setLevel(self.get_log_level(log_level))
            log_file_handler.setFormatter(formatter)
            self.logger.addHandler(log_file_handler)

        self.debug = self.logger.debug
        self.info = self.logger.info
        self.warning = self.logger.warning
        self.error = self.logger.error
        self.critical = self.logger.critical
        self.base_path = os.path.abspath(".")
        self.log_path = os.path.dirname(log_name)

        self.data_files = dict()
        self.file_writers = dict()
        self.resource_path = self.get_resource_path("resource")

    @staticmethod
    def get_log_level(level):
        d = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL
        }
        if level in d:
            return d[level]
        else:
            return logging.DEBUG

    def save_data_to_csv(self, filename=None, **kwargs):
        with open(os.path.join(self.log_path, filename+".csv"), 'a', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            if filename not in self.data_files:  # only write the column name first time file created
                self.data_files[filename] = file
                if len(kwargs):
                    writer.writerow([key for key in kwargs])
            if len(kwargs):
                _path = os.path.join(self.log_path, filename + ".csv")
                self.logger.debug(f"save to: {_path}")
                self.logger.debug(f"{[kwargs[key] for key in kwargs]}")
                writer.writerow([kwargs[key] for key in kwargs])

        # if filename not in self.data_files:
        #     self.data_files[filename] = open(os.path.join(self.log_path, filename+".csv"),
        #                                      'a', encoding='utf-8', newline='')
        #     self.file_writers[filename] = csv.writer(self.data_files[filename])
        #     self.file_writers[filename].writerow([key for key in kwargs])
        # if len(kwargs):
        #     _path = os.path.join(self.log_path, filename+".csv")
        #     self.logger.debug(f"save to: {_path}")
        #     self.logger.debug(f"{[kwargs[key] for key in kwargs]}")
        #     self.file_writers[filename].writerow([kwargs[key] for key in kwargs])

    def get_resource_path(self, folder):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        self.logger.debug(f"base path: {base_path}")
        return os.path.join(base_path, folder)