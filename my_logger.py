# -*- coding: UTF-8 -*-
import logging
# from datetime import datetime
# import configparser
# import os

_INITIALIZED_ = False


class MyLogger:
    def __init__(self, is_to_file, log_name, log_level):
        # global _INITIALIZED_
        # if not _INITIALIZED_:
        if self.get_log_level(log_level) == logging.DEBUG:
            formatter = logging.Formatter("%(asctime)s %(filename)s %(lineno)s %(levelname)s: %(message)s")
        else:
            formatter = logging.Formatter("%(asctime)s %(lineno)s %(levelname)s: %(message)s")
        # formatter.datefmt = "%Y-%m-%d %H:%M:%S%z"
        sh = logging.StreamHandler()
        sh.setLevel(self.get_log_level(log_level))
        sh.setFormatter(formatter)
        rl = logging.getLogger()
        rl.setLevel(self.get_log_level(logging.DEBUG))
        rl.addHandler(sh)
        if is_to_file:
            fh = logging.FileHandler(filename=log_name, mode="w")
            fh.setLevel(self.get_log_level(log_level))
            fh.setFormatter(formatter)
            rl.addHandler(fh)
            # _INITIALIZED_ = True

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

    def debug(self, msg, *args, **kwargs):
        logging.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        logging.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        logging.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        logging.error(msg, *args, **kwargs)

    @staticmethod
    def critical(self, msg, *args, **kwargs):
        logging.critical(msg, *args, **kwargs)
