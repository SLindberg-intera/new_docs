import logging
import os
try:
    from pylib.config import config, parse_args 
except ModuleNotFoundError:
    from config import config, parse_args
import pylib.gwreducer.constants as c
from pylib.gwreducer.parse_input_file import parse_input_file
from pylib.gwreducer.read_gw import GWData
from pylib.gwreducer.reduce_dataset import reduce_dataset
from pylib.gwreducer.summary_file import reset_summary_file 

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



def reduce_for_row_col(gw_data, row, col,
        summary_file, output_folder):
    """
        extract a TimeSeries instance from a GWData
        corresponding to the target row/col and then reduce it
        
        returns True if succeded in reducing; false otherwise
    
    """
    timeseries = gw_data.extract(row, col)
    worked = reduce_dataset(
            timeseries, summary_file, output_folder
            )
    return worked


def reduce_input_data(input_data, summary_file, output_folder):
    """
        Reduce all the data in the input_data object  for the
        given filekey

    """
    filekey = input_data["Source File"]
    logging.info("START reducing {}".format(filekey))
    gw_data = GWData(filekey)

    for rowcol in gw_data.get_rowcols:
        row, col = rowcol.split('-')
        try:
            worked = reduce_for_row_col(
                    gw_data, row, col,
                    summary_file, output_folder)
            #if not worked:
            #    continue
        except TypeError as e:
            raise Exception(e)
            logging.error("failed at {} {}".format(row, col))
def main():
    """ 
        parse the input arguments, configure the logger
        obtain the input data
        reduce the input data
        and write the results

    """

    args = parse_args()
    configure_logger(args)
    logging.info("START execution")
    input_file = get_inputfile(args)
    input_data = parse_input_file(input_file)
    output_folder = get_output_folder(args)
    summary_filename = "summary.csv"
    summary_file = reset_summary_file(output_folder, summary_filename)
    reduce_input_data(input_data, summary_file,
                output_folder)

    logging.info("END execution")


if __name__ == "__main__":
    main()

