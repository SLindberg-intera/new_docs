from config import config, parse_args 
import logging
import constants as c
import os
from parse_input_file import parse_input_file
from pylib.vzreducer.reduce_timeseries import ReducedTimeSeries
from pylib.vzreducer.read_solid_waste_release import SolidWasteReleaseData
from plots import residual_plot, mass_plot, recursive_plot, reduced_timeseries_plot 
import matplotlib.pyplot as plt
from pylib.vzreducer.reduce_dataset import reduce_dataset
from pylib.vzreducer.summary_file import reset_summary_file 

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


def get_site_list(input_data, solid_waste_release):
    """ get sites to reduce"""
    if len(input_data[c.WASTE_SITES_KEY])>0:
        return input_data[c.WASTE_SITES_KEY]
    return sorted(solid_waste_release.sites)

def get_copc_list(input_data, solid_waste_release):
    """ get copcs to reduce """
    if len(input_data[c.COPCS_KEY])>0:
        return input_data[c.COPCS_KEY]
    return sorted(solid_waste_release.copcs)


def reduce_for_copc_site(solid_waste_release, copc, site,
        summary_file, output_folder):
    """
        extract a TimeSeries instance from solid_waste_release
        corresponding to the target copc/site and then reduce it
        
        returns True if succeded in reducing; false otherwise
    
    """
    timeseries = solid_waste_release.extract(copc, site)
    worked = reduce_dataset(
            timeseries, summary_file, output_folder
            )
    return worked


def reduce_input_data(filekey, input_data, summary_file, output_folder):
    """
        Reduce all the data in the input_data object  for the
        given filekey

    """

    logging.info("START reducing {}".format(filekey))
    solid_waste_release = SolidWasteReleaseData(
            input_data[c.SOURCE_FILES_KEY][filekey],
            input_data[c.ZERO_BELOW_KEY]
    )
    copc_list = get_copc_list(input_data, solid_waste_release)
    site_list = get_site_list(input_data, solid_waste_release)

    for copc in copc_list:
        for site in site_list:
            try:
                worked = reduce_for_copc_site(
                        solid_waste_release, copc, site,
                        summary_file, output_folder)
                if not worked:
                    continue
            except TypeError as e:
                raise Exception(e)
                logging.error("failed at {} {}".format(copc, site))
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
    for filekey in [c._200E_KEY, c._200W_KEY]:
        reduce_input_data(filekey, input_data, summary_file,
                output_folder)

    logging.info("END execution")


if __name__ == "__main__":
    main()

