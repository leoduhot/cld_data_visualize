# -*- coding: UTF-8 -*-
import logging
# from datetime import datetime
# import configparser
# import os

_INITIALIZED_ = False


class MyLogger:
    def __init__(self, is_to_file, log_name, log_level):
        global _INITIALIZED_
        if not _INITIALIZED_:
            if self.get_log_level(log_level) == logging.DEBUG:
                formatter = logging.Formatter("%(asctime)s %(filename)s %(lineno)s %(levelname)s: %(message)s")
            else:
                formatter = logging.Formatter("%(asctime)s %(lineno)s %(levelname)s: %(message)s")
            # formatter.datefmt = "%Y-%m-%d %H:%M:%S%z"
            sh = logging.StreamHandler()
            sh.setLevel(self.get_log_level(log_level))
            sh.setFormatter(formatter)
            self.logger = logging.getLogger()
            self.logger.setLevel(self.get_log_level(logging.DEBUG))
            self.logger.addHandler(sh)
            if is_to_file:
                fh = logging.FileHandler(filename=log_name, mode="w")
                fh.setLevel(self.get_log_level(log_level))
                fh.setFormatter(formatter)
                self.logger.addHandler(fh)
                _INITIALIZED_ = True

            self.debug = self.logger.debug
            self.info = self.logger.info
            self.warning = self.logger.warning
            self.error = self.logger.error
            self.critical = self.logger.critical

    @staticmethod
    def get_log_level(level):
        d = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL,
        }
        if level in d:
            return d[level.lower()]
        else:
            return logging.DEBUG
