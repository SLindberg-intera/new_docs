import os, sys


try:
    from pylib.runner.constants import LOGGER_KEY, LOG_LEVEL_MAP
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(__file__), '..','..')
    )
    from pylib.runner.constants import LOGGER_KEY, LOG_LEVEL_MAP

CONFIG_FILE = os.path.abspath(
	os.path.join(
		os.path.dirname(__file__), 'config.json')
)


""" These keys are used in the input JSON file """
SOURCE_FILES_KEY = "Source Files"
_200E_KEY = "200 E"
_200W_KEY = "200 W"

ZERO_BELOW_KEY = "Zero Below"

SUMMARY_TEMPLATE_KEY = "SUMMARY_TEMPLATE"

COPCS_KEY = "COPCs"
WASTE_SITES_KEY = 'Waste Sites'
#end of original constants/input file values

#start of constants added to migrate from hard-coded values
OUT_ERROR_THRESHOLD_KEY = "Output Error Threshold"

LOWER_N_KEY = "Lower Reduced Datapoint Limit"
UPPER_N_KEY = "Upper Reduced Datapoint Limit"

MIN_ITERATIONS_KEY = "Minimum Iterations"
MAX_ITERATIONS_KEY = "Maximum Iterations"

MAX_ERR_ITERATIONS_KEY = "Maximum Error Iterations"
PEAK_HEIGHT_KEY = "Peak Height"
#DELTA_SLOPE_TOL_KEY = "Delta Slope Tolerance"
#FLUX_FLOOR_KEY = "Flux Floor"
SOLVE_TYPE_KEY = "Solve Type"
""" End of keys used in the input JSON file """

""" These keys are used in the config JSON file [for plotting/graphing?]--move to input JSON? """
SMOOTH_KEY = "SMOOTHING"
BUTTER_INDEX_KEY = "BUTTERWORTH_FACTOR"
CUTOFF_FREQUENCY = "CUTOFF_FREQUENCY"

PLOTS_KEY = "PLOTS"
ERROR_TITLE = "ERROR_TITLE"
SIGNAL_TITLE = "SIGNAL_TITLE"
AVERAGE_ERROR_LABEL = "AVERAGE_ERROR_LABEL"

RAW = "RAW"
SMOOTHED = "SMOOTHED"
ERROR = "ERROR"
COLOR = "COLOR"
SYMBOL = "SYMBOL"
""" End of keys used in the config JSON file """



