# colada_sensor_data_visualization

## UI
* 1. view and edit UI by: pyside6-designer mainWin.ui
* 2. save UI changes by: pyside6-uic mainWin.ui > mainWin_ui.py

## Compile

* Windows:
	> pyinstaller -F --hidden-import scipy.special._special_ufuncs --hidden-import scipy._lib.array_api_compat.numpy.fft main.py --add-data=resource:resource -i .\resource\icon.ico -n v0.4.000

* Mac
	> pyinstaller -F main.py --add-data=resource:resource -i ./resource/icon.ico -n v0.4.000
	
