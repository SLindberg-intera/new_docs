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
SOURCE_FILES_KEY = "Source Files"
_200E_KEY = "200 E"
_200W_KEY = "200 W"
ZERO_BELOW_KEY = "Zero Below"
WASTE_SITES_KEY = 'Waste Sites'
COPCS_KEY = "COPCs"
