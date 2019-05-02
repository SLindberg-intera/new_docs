"""
   configure the runner

   - reads the config file
   - defines the command line arguments that are possible

   
   config is a dictionary containing the configuration parameters

   parse_args is a function handle; 
      when called, the command line arguments are parsed and returned
      as a namespace
   
"""
import constants
import sys, os

sys.path.append(
        os.path.join(os.path.dirname(__file__), '..','..'))

from pylib.config.config import read_config
from pylib.autoparse.autoparse import config_parser 

config = read_config(constants.CONFIG_FILE)
parse_args = lambda : config_parser(config)

