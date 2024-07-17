# colada_sensor_data_visualization

## Compile

* Windows:
	> pyinstaller -F --hidden-import scipy.special._special_ufuncs --hidden-import scipy._lib.array_api_compat.numpy.fft main.py my_logger.py ui_utility.py data_visualization_utility.py -n cld_sensor_data_visualize_v0.1.001

* Mac
	> pyinstaller -F main.py my_logger.py ui_utility.py data_visualization_utility.py -n cld_sensor_data_visualie_v0.1.001