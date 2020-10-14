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


""" These keys are used in the input file """
SOURCE_FILE_KEY = "Source File"
ZERO_BELOW_KEY = "Zero Below"
WASTE_SITES_KEY = 'Waste Sites'
ERROR = "ERROR"
COLOR = "COLOR"
SYMBOL = "SYMBOL"
SMOOTH_KEY = "SMOOTHING"
BUTTER_INDEX_KEY = "BUTTERWORTH_FACTOR"
CUTOFF_FREQUENCY = "CUTOFF_FREQUENCY"
