from config import config, parse_args 
import logging
import constants as c
import os

def configure_logger(args):
    """
        set the logger for this utility
    """
    logging.basicConfig(
            level=c.LOG_LEVEL_MAP[args.loglevel],
            filemode=args.logfilemode.lower(),
            filename=args.logfile,
            **config[c.LOGGER_KEY]
     )

def get_inputfile(args):
    """get input file or fail """
    if os.path.exists(args.inputFile):
        return args.inputFile
    raise IOError("Could not locate input file '{}'.".format(args.inputFile))

def get_output_folder(args):
    """ get output directory or fail"""
    if os.path.exists(args.outputFolder):
        return args.outputFolder
    raise IOError("Could not locate output folder '{}'.".format(args.outputFolder))

if __name__ == "__main__":
    args = parse_args()
    configure_logger(args)
    logging.info("START execution")
    input_file = get_inputfile(args)
    output_folder = get_output_folder(args)
    logging.info("END execution")
