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
    input_data = parse_input_file(input_file)
    output_folder = get_output_folder(args)

    solid_waste_release = SolidWasteReleaseData(
            input_data[c.SOURCE_FILES_KEY][c._200E_KEY],
            input_data[c.ZERO_BELOW_KEY]
    )
    if len(input_data[c.COPCS_KEY])>0:
        copc_list = input_data[c.COPCS_KEY]
    else:    
        copc_list = sorted(solid_waste_release.copcs)
    if len(input_data[c.WASTE_SITES_KEY])>0:
        site_list = input_data[c.WASTE_SITES_KEY]
    else:    
        site_list = sorted(solid_waste_release.sites)

    summary_file = os.path.join(output_folder, "summary.csv")
    with open(summary_file, "w") as f:
        f.write("test line\n")
    for copc in copc_list:
        for site in site_list:
            try:
                timeseries = solid_waste_release.extract(copc, site)
                worked = reduce_dataset(
                        timeseries, summary_file, output_folder,
                        input_data
                        )
                if not worked:
                    continue
                
            except TypeError as e:
                raise Exception(e)
                logging.error("failed at {} {}".format(copc, site))
    logging.info("END execution")

