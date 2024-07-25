# -*- coding: UTF-8 -*-
# from datetime import datetime
import unicodedata
import time
import sys
import os
# import platform
# import subprocess
import numpy as np
# from threading import Thread
import ttkbootstrap as ttk
# import windnd
from ttkbootstrap.style import Bootstyle
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.dialogs.dialogs import MessageDialog
import logging


class MyTtkFrame(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        try:
            self.logger = kwargs["logger"] if "logger" in kwargs else logging
            self.localdebug = False
            self.toast = None
            # self.ru = ReportUtility(self.logger, self.localdebug)
        except Exception as e:
            print(f"Excetpion: {str(e)}:{str(e.__traceback__.tb_lineno)}")

    def resource_path(self, _path):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        self.logger.debug(f"base path:{base_path}")
        return os.path.join(base_path, _path)

    def message_box(self, typ, txt, d=3000, delay=True):
        if delay:
            self.master.after(10, self._message_box, typ, txt, d)
        else:
            self._message_box(typ, txt, d)

    def _message_box(self, typ, txt, d=3000):
        self.master.update_idletasks()
        d1 = self.master.winfo_width()
        h = self.master.winfo_height()
        x = self.winfo_rootx()
        y = self.winfo_rooty()
        # self.logger.textLogger.debug(f"toast...{x}, {y}, {d1}, {h}...")
        self.toast = ToastNotification(
            title=typ,
            icon="",
            message=txt,
            duration=d,
            bootstyle="primary",
            position=(x + d1 // 2, y + h // 2, 'n')
        )
        self.toast.show_toast()
        self.master.update_idletasks()
        return self.toast

    def close_message_box(self):
        # this function should be used in a thread
        timeout_cnt = 0
        while self.toast is None and timeout_cnt < 100:
            time.sleep(0.1)
            timeout_cnt += 1
        if self.toast is not None:
            self.toast.hide_toast()
            self.toast = None

    def message_diag(self, txt):
        # self.logger.debug("Pause here...")
        # self.master.update_idletasks()
        x = self.master.winfo_rootx()
        y = self.master.winfo_rooty()
        d = self.master.winfo_width()
        h = self.master.winfo_height()
        x0 = (d - x) // 2
        y0 = (h - y) // 2
        # self.logger.debug(f"diag...{x}, {y}, {d}, {h}.{x0}, {y0}..")
        md = MessageDialog(txt, buttons=['Yes'])
        md.show(
            position=(x0, y0)
        )

    @staticmethod
    def valid_numeric(data):
        try:
            float(data)
            return True
        except ValueError:
            pass
        try:
            unicodedata.numeric(data)
            return True
        except (TypeError, ValueError):
            pass
            return False

    @staticmethod
    def my_linspace(start, stop, num):
        return [round(i, 9) for i in np.linspace(start, stop, num)]

    @staticmethod
    def my_arange(start, stop, step):
        return [round(i, 9) for i in np.arange(start, stop, step)]


class MyTips(MyTtkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        # self.widget = widget
        self.text = kwargs["text"]
        # self.tooltip = None
        self.msg = False

    def show(self, event):
        # print(f"show:{self.text}, event:{event}")
        # self.tooltip = ttk.Label(self.widget.master, text=self.text)
        # self.tooltip.place(x=event.x, y=event.y)
        self.message_box("Info", self.text)
        self.msg = True

    def hide(self, event):
        # print(f"hide:{self.text}")
        if self.msg:
            self.close_message_box()
            self.msg = False
        # if self.tooltip:
        #     self.tooltip.destroy()
        #     self.tooltip = None


class FileFrm(MyTtkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        if "logger" in kwargs:
            self.logger = kwargs['logger']
        frm = ttk.Frame(self)
        frm.pack(fill=X, expand=True, pady=5)
        _txt = kwargs["text"] if "text" in kwargs else "Undefined"
        self._func = kwargs["command"] if "command" in kwargs else None
        self._drop_func = kwargs["drop"] if "drop" in kwargs else None
        _root = kwargs["root"] if "root" in kwargs else self
        _lb = ttk.Label(frm, text=_txt)
        _lb.pack(side=LEFT, padx=5)
        self.entry = ttk.Entry(frm, bootstyle='primary')
        self.entry.pack(side=LEFT, expand=True, fill=X, padx=5)
        self.entry.insert(0, "drap file to the window or click browser button")
        self.entry.config(foreground='gray')
        if self._drop_func is not None:
            # windnd.hook_dropfiles(_root, func=self.drop)
            _root.dnd_bind('<<Drop>>', self.drop)
        file_btn = ttk.Button(frm, text="Browser", command=self._on_button)
        file_btn.pack(side=LEFT, padx=5)

        self.filepath = None

    def _on_button(self):
        self.entry.delete(0, END)
        self.entry.config(foreground='')
        if self._func() is not None:
            self._func()
        pass

    def drop(self, event):
        files = event.data.strip().split()
        self.logger.info(f"files:<{files}>")
        self.logger.info(f"file[0]:<{files[0]}>")
        # msg = '\n'.join((item for item in files))
        # self.logger.info(f"get data:[{msg}]")
        self.filepath = os.path.normpath(files[0].strip())
        self.entry.insert(0, self.filepath)
        self.entry.config(foreground='')
        self._drop_func()

    def set(self, value):
        self.entry.delete(0, END)
        self.entry.insert(0, value)
        pass

    def get(self):
        return self.entry.get()

    def get_filepath(self):
        return self.filepath


class ComboboxWithLabel(MyTtkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.logger = kwargs['logger'] if "logger" in kwargs else logging
        _txt = kwargs['text'] if "text" in kwargs else "Undefined"
        _func = kwargs['command'] if "command" in kwargs else self._on_selected
        _values = kwargs['values'] if "values" in kwargs else []
        _width = kwargs['width'] if "width" in kwargs else [10, 10]
        _default = kwargs['default'] if "default" in kwargs else 0
        _side = kwargs['side'] if "side" in kwargs else ttk.LEFT

        frm = ttk.Frame(self)
        frm.pack(fill=ttk.X, pady=5)
        self._lb = ttk.Label(frm, text=f"{_txt:<10}", width=_width[0])
        self._lb.pack(side=ttk.LEFT, padx=5)
        self._comb = ttk.Combobox(frm, bootstyle='primary', values=_values, width=_width[1])
        self._comb.set(_default)
        self._comb.bind("<<ComboboxSelected>>", _func)
        self._comb.pack(side=ttk.LEFT, padx=5)

    def _on_selected(self, event):
        pass

    def get(self):
        # self.logger.debug(f"get return:{self._comb.get()}")
        return self._comb.get()

    def set(self, val):
        self._comb.set(val)

    def configure(self, *args, **kwargs):
        if "state" in kwargs:
            self._comb.configure(state=kwargs["state"])
        if "bootstyle" in kwargs:
            self._comb.configure(bootstyle=kwargs["bootstyle"])
            self._lb.configure(bootstyle=kwargs["bootstyle"])


class EntryWithLabel(MyTtkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.logger = kwargs['logger'] if "logger" in kwargs else logging
        _txt = kwargs['text'] if "text" in kwargs else "Undefined"
        _func = kwargs['command'] if "command" in kwargs else self._on_selected
        _value = kwargs['value'] if "value" in kwargs else ""
        _width = kwargs['width'] if "width" in kwargs else [10, 10]
        _default = kwargs['default'] if "default" in kwargs else 0
        _tips = kwargs["tips"] if "tips" in kwargs else ""
        frm = ttk.Frame(self)
        frm.pack(fill=ttk.X, pady=5)
        self._lb = ttk.Label(frm, text=f"{_txt:<10}", width=_width[0])
        self._lb.pack(side=ttk.LEFT, padx=5)
        self._entry = ttk.Entry(frm, bootstyle='primary', width=_width[1])
        self._entry.pack(side=ttk.LEFT, padx=5)
        self._entry.insert(0, _default)
        if len(_tips):
            self.logger.debug(f"tips: {_tips}")
            self.tips = MyTips(text=_tips)
            self._entry.bind("<FocusIn>", self.tips.show)
            self._entry.bind("<FocusOut>", self.tips.hide)

    def _on_selected(self):
        pass

    def get(self):
        return self._entry.get()

    def set(self, val):
        self._entry.delete(0, END)
        self._entry.insert(0, val)

    def configure(self, *args, **kwargs):
        if "state" in kwargs:
            self._entry.configure(state=kwargs["state"])
        if "bootstyle" in kwargs:
            self._entry.configure(bootstyle=kwargs["bootstyle"])
            self._lb.configure(bootstyle=kwargs["bootstyle"])


class ParameterFrm(MyTtkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        try:
            if "logger" in kwargs:
                self.logger = kwargs['logger']
            frm = ttk.Frame(self)
            frm.pack(fill=ttk.X, pady=5)
            self.obj = {}
            self.entry = {}
            self.combbox = {}
            if "_combobox" in kwargs:
                for val in kwargs["_combobox"]:
                    _txt, _values, _func, _width, _default = val
                    self.combbox[_txt] = ComboboxWithLabel(frm, text=_txt, values=_values,
                                                           command=_func, width=_width, default=_default)
                    self.obj[_txt] = self.combbox[_txt]
            if "_entry" in kwargs:
                for val in kwargs["_entry"]:
                    _txt, _width, _default, _tips = val
                    self.entry[_txt] = EntryWithLabel(frm, text=_txt, width=_width, default=_default, tips=_tips)
                    self.obj[_txt] = self.entry[_txt]
            if "columns" in kwargs:
                _columns = kwargs['columns']
                row_inx = col_inx = 0
                for key in self.obj:
                    self.obj[key].grid(row=row_inx, column=col_inx, padx=5, pady=5, sticky=EW)
                    row_inx = row_inx + 1 if col_inx == _columns - 1 else row_inx
                    col_inx = 0 if col_inx == _columns - 1 else col_inx + 1
            else:
                for key in self.obj:
                    self.obj[key].pack(side=ttk.LEFT, padx=5)

        except Exception as exp:
            print(f"Excetpion: {str(exp)}:{str(exp.__traceback__.tb_lineno)}")

    def get(self, name):
        return self.obj[name].get()

    def set(self, name, val):
        self.obj[name].set(val)

    def state_config(self, s):
        _s = ["disabled", "enable"]
        _st = ['secondary', 'primary']
        for n in self.obj:
            self.obj[n].configure(state=_s[s], bootstyle=_st[s])


class FilterFrm(MyTtkFrame):
    def __init__(self, *args, **kwargs):
        try:
            super().__init__(*args)
            self.logger = kwargs['logger'] if "logger" in kwargs else logging

            frm = ttk.Frame(self)
            frm.pack(fill=ttk.X)
            self.obj = {}
            self.filter_var = {}
            self.filter_ckb = {}

            if "parameters" in kwargs:
                for key in kwargs["parameters"]:
                    _param = {}
                    frm = ttk.Frame(self)
                    frm.pack(fill=ttk.X)
                    self.filter_var[key] = ttk.BooleanVar()
                    self.filter_ckb[key] = ttk.Checkbutton(frm, text=f"{key:<30}", variable=self.filter_var[key],
                                                           command=self._on_check)
                    self.filter_ckb[key].pack(side=ttk.LEFT, padx=5)
                    for _type, _txt, _width, _default, _tips_or_values in kwargs["parameters"][key]:
                        if _type == "combobox":
                            _param[_txt] = ComboboxWithLabel(frm, text=_txt, values=_tips_or_values,
                                                             width=_width, default=_default, side=ttk.RIGHT)
                            _param[_txt].pack(side=ttk.LEFT, padx=5)
                            pass
                        elif _type == "entry":
                            _param[_txt] = EntryWithLabel(frm, text=_txt, width=_width,
                                                          default=_default, tips=_tips_or_values, side=ttk.RIGHT)
                            _param[_txt].pack(side=ttk.LEFT, padx=5)
                            pass
                        else:
                            pass
                    self.obj[key] = _param
        except Exception as exp:
            print(f"Excetpion: {str(exp)}:{str(exp.__traceback__.tb_lineno)}")

    def _on_check(self):
        _s = ["disabled", "enable"]
        _st = ['secondary', 'primary']

        for name in self.filter_var:
            s = int(self.filter_var[name].get())
            self.logger.info(f"filter check: {name}, {s}")
            for _obj in self.obj[name]:
                self.obj[name][_obj].configure(state=_s[s], bootstyle=_st[s])

    def get(self, name):
        checked = self.filter_var[name].get()
        self.logger.debug(f"get {name}: {checked}")
        return checked

    def set(self, name, val):
        self.filter_var[name].set(val)
        self._parameters_state_update(name)

    def get_parameters(self, name):
        param = {}
        for key in self.obj[name]:
            param[key] = self.obj[name][key].get()
        return param

    def set_parameters(self, name, val):
        for key in val:
            self.obj[name][key].set(val[key])

    def _parameters_state_update(self, key):
        _s = ["disabled", "enable"]
        _st = ['secondary', 'primary']
        s1 = int(self.filter_var[key].get())
        for _obj in self.obj[key]:
            self.obj[key][_obj].configure(state=_s[s1], bootstyle=_st[s1])

    def state_config(self, s):
        _s = ["disabled", "enable"]
        _st = ['secondary', 'primary']
        for key in self.filter_ckb:
            self.filter_ckb[key].configure(state=_s[s])
            self._parameters_state_update(key)


class __FilterFrm(MyTtkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.logger = kwargs['logger'] if "logger" in kwargs else logging
        frm = ttk.Frame(self)
        frm.pack(fill=ttk.X, pady=5)
        self.filters_var = {}
        self.filters_ckb = {}
        if "filters" in kwargs and "func" in kwargs and "columns" in kwargs:
            row_inx = col_inx = 0
            _columns = kwargs["columns"]
            for _filter, _func in zip(kwargs["filters"], kwargs["func"]):
                self.filters_var[_filter] = ttk.IntVar()
                self.filters_ckb[_filter] = ttk.Checkbutton(frm, text=_filter,
                                                            command=_func,
                                                            variable=self.filters_var[_filter], onvalue=1, offvalue=0)
                # self.filters_ckb[_filter].pack(side=ttk.LEFT, padx=5)
                self.filters_ckb[_filter].grid(row=row_inx, column=col_inx, padx=5, pady=5, sticky=EW)
                row_inx = row_inx + 1 if col_inx == _columns - 1 else row_inx
                col_inx = 0 if col_inx == _columns - 1 else col_inx + 1

    def get(self, _filter):
        val = self.filters_var[_filter].get()
        self.logger.debug(f"{_filter} get: {val}")
        return val

    def set(self, _filter, val):
        self.filters_var[_filter].set(val)

    def state_config(self, _filter):
        pass


class ChannelFrm(MyTtkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        if "logger" in kwargs:
            self.logger = kwargs['logger']
        _count = kwargs["count"] if "count" in kwargs else 40

        frm = ttk.Frame(self)
        frm.pack(fill=ttk.X, pady=5)
        self.channels = [val for val in range(_count)]
        self.available_channels = []

        if "command" in kwargs:
            self.command = kwargs["command"]
        else:
            self.command = self._on_check
        self.channel_var = {}
        self.channel_ckb = {}
        self.text_var = {}
        # row_inx = col_inx = 0
        for ch in self.channels:
            self.channel_var[ch] = ttk.BooleanVar()
            # self.channel_var[count].set(True)
            self.channel_ckb[ch] = ttk.Checkbutton(frm, text=ch,
                                                      command=self.command,
                                                      variable=self.channel_var[ch])
            # self.channel_ckb[ch].grid(row=row_inx, column=col_inx, padx=5, pady=5)
            # col_inx = 0 if col_inx == 4 else col_inx+1
            # row_inx = row_inx+1 if col_inx == 4 else row_inx
        self.channel_ckb[0].configure(command=self._on_all_check)

    def show_channels(self, channel_list, columns):
        self.available_channels = channel_list
        for ch in self.channels:
            self.channel_var[ch].set(False)
            self.channel_ckb[ch].grid_forget()

        if not len(channel_list):
            return

        self.channel_var[0].set(True)
        self.channel_ckb[0].configure(text="ALL")
        self.channel_ckb[0].grid(row=0, column=0, padx=5, pady=5, sticky=EW)
        row_inx = count = 1
        col_inx = 0
        for ch in channel_list:
            if count < len(self.channels):
                self.channel_var[count].set(True)
                self.channel_ckb[count].configure(text=ch)
                self.channel_ckb[count].grid(row=row_inx, column=col_inx, padx=5, pady=5, sticky=EW)
                row_inx = row_inx + 1 if col_inx == columns-1 else row_inx
                col_inx = 0 if col_inx == columns-1 else col_inx+1
                count += 1
            else:
                break

    def get_channels(self):
        _list = []
        for ch in range(len(self.channels)):
            if ch == 0:
                continue
            if self.channel_var[ch].get():
                # self.logger.info(f"{ch}")
                if self.channel_ckb[ch].cget("text") != "ALL":
                    _list.append(self.channel_ckb[ch].cget("text"))
        return _list

    def _on_check(self):
        pass

    def _on_all_check(self):
        self.logger.info(f"all checked {self.channel_var[0].get()}")
        for ch in range(len(self.available_channels)+1):
            if ch == 0:
                continue
            self.channel_var[ch].set(self.channel_var[0].get())

