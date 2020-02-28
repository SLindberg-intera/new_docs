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
SUMMARY_FILE_NAME = "SUMMARY_FILE_NAME"
SUMMARY_MODE = "SUMMARY_MODE"
COPCS_KEY = "COPCs"
WASTE_SITES_KEY = 'Waste Sites'
#end of original constants/input file values

#start of constants added to migrate from hard-coded values
#These keys are for the error acceptance criteria
MASS_THRESHOLD = "Mass Threshold"
#for sites with total mass/activity greater than mass threshold
LOWER_OUT_ERROR_THRESHOLD_KEY = "Output Lower Error Threshold"

#for sites with total mass/activity less than or equal to mass threshold
UPPER_OUT_ERROR_THRESHOLD_KEY = "Output Upper Error Threshold"

#minimum and maximum numbers of data points
LOWER_N_KEY = "Lower Reduced Datapoint Limit"
UPPER_N_KEY = "Upper Reduced Datapoint Limit"

#the maximum number of iterations for data reduction
MAX_ITERATIONS_KEY = "Maximum Iterations"

#the maximum number of iterations when distributing the difference in mass
MAX_ERR_ITERATIONS_KEY = "Maximum Error Iterations"


FLUX_FLOOR_KEY = "Flux Floor"
EPSILON = "Epsilon"
GAP_CLOSED = "Close Gaps"
GAP_DELTA = "Gap Delta"
""" End of keys used in the input JSON file """


PLOTS_KEY = "PLOTS"
ERROR_TITLE = "ERROR_TITLE"
AVERAGE_ERROR_LABEL = "AVERAGE_ERROR_LABEL"


ERROR = "ERROR"
COLOR = "COLOR"
SYMBOL = "SYMBOL"
""" End of keys used in the config JSON file """



