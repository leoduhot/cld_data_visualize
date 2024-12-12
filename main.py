# -*- coding: UTF-8 -*-
from ui_main import *
import platform

tver = "v0.3.002"
tag = "2024/12/12 10:30 +0800"

if __name__ == '__main__':
    log_path = os.path.join(os.path.abspath("."), 'log')
    if not os.path.exists(log_path):
        try:
            os.makedirs(log_path, True)
            os.chmod(log_path, 0o755)
        except Exception as ex:
            print(f"{str(ex)}\nin {__file__}:{str(ex.__traceback__.tb_lineno)}")
            sys.exit(-1)
    try:
        dt = datetime.now()
        filename = dt.strftime("%Y%m%d_%H%M%S")
        _logger = MyLogger(True, os.path.join(log_path, f"log_{filename}.log"), "info")
        _logger.info(f"\n{tver}\n{tag}\nstart...")
        if platform.system().lower() == "darwin" and platform.machine().lower().startswith("arm"):
            wm = ttk.Window(
                title=f'Sensor Data Visualization {tver} ({tag})',
                themename="litera",
            )
        else:
            wm = MyDnDWindow(
                title=f'Sensor Data Visualization {tver} ({tag})',
                themename="litera",
            )
            wm.drop_target_register(DND_FILES)
        wm.geometry(f"{int(wm.winfo_screenwidth()*0.4)}x{int(wm.winfo_screenheight()*0.6)}"
                    f"+{int(wm.winfo_screenwidth()*0.3)}+{int(wm.winfo_screenheight()*0.2)}")

        t = SensorDataVisualizationUI(wm, logger=_logger)
        wm.mainloop()
    except Exception as ex:
        print(f"Excetpion: {str(ex)}:{str(ex.__traceback__.tb_lineno)}")
        sys.exit(-1)
