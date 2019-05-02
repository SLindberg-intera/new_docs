"""
   configure the runner


   - reads the config file
      - creates the command line arguments
"""
import constants
import sys, os

sys.path.append(
        os.path.join(os.path.dirname(__file__), '..','..'))


from pylib.config.config import read_config
from pylib.autoparse.autoparse import config_parser 

config = read_config(constants.CONFIG_FILE)
parse_args = lambda : config_parser(config)

