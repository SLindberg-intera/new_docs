import unittest
import os
import sys
from . import autoparse
from . import constants as c


try:
    from pylib.config.config import read_config
except ModuleNotFoundError as e:
    thisdir = os.path.dirname(__file__)
    homepath = os.path.abspath( os.path.join(thisdir, '..'))
    sys.path.append(homepath)
    from config.config import read_config 

CONFIG_FILE = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "test", "test_config.json"))
config = read_config(CONFIG_FILE)

class TestArg(unittest.TestCase):
    def test_valid_config(self):
        args = autoparse.config_parser(config)
        self.assertEqual(args.testarg, "default value")

    def test_invalid_config(self):
        with self.assertRaises(ValueError):
            autoparse.config_parser({})

    def test_null_config(self):
        d = {c.ARGPARSE_SECTION_KEY:{}}
        args = autoparse.config_parser(d)
        self.assertEqual(args, {})


if __name__=='__main__':
    unittest.main()
