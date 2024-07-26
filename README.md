# colada_sensor_data_visualization

## Compile

* Windows:
	> pyinstaller -F --hidden-import scipy.special._special_ufuncs --hidden-import scipy._lib.array_api_compat.numpy.fft main.py ui_main.py my_logger.py ui_utility.py data_visualization_utility.py data_parser.py --add-data="D:\Programs\Python\Python311\Lib\site-packages\tkinterdnd2\tkdnd:." --add-data=resource:resource -i .\resource\icon.ico -n v0.1.001

* Mac
	> pyinstaller -F main.py ui_main.py my_logger.py ui_utility.py data_visualization_utility.py data_parser.py --add-data=resource:resource -i ./resource/icon.ico -n v0.1.001
	
