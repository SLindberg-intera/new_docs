"""
   Creates a command line parser by reading a configuration dictionary


   Allowed arguments are passed in through a configuration dictionary, which
   specifies parameters passed to argparse


"""

import argparse
from . import constants as c

def config_parser(config_dict):
    """
        traverse config_dict and map its contents to python's ArgParser

        config_dict must have a key of c.ARGPARSE_SECTION_KEY that contains
           a dictonary that will be mapped to argparse
           
           each record in config_dict[c.ARGPARSE_SECTION_KEY][c.ARGUMENTS_KEY] must:
              have a structure that can be mapped to argparse.Parser.add_argument()

        see the test cases for an example
    """
    try:
        parse = config_dict[c.ARGPARSE_SECTION_KEY]
    except KeyError:
        raise ValueError("Could not find command {} in parser configuration".format(
            c.ARGPARSE_SECTION_KEY))
    args = parse.pop(c.ARGUMENTS_KEY, None)

    parser = argparse.ArgumentParser(**parse)
    if args is None:
        return {}
    for item in args:
        arg = item.pop(c.ARG)
        if arg is not None:
            parser.add_argument(arg, **item)
    try:
        args = parser.parse_args()
    except SystemExit as e:
        raise e
        raise ValueError("error with arg {}".format(args))
    return args
