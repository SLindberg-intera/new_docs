import logging
import os
try:
#this config file is not in sync with the code--the config.py file located in runner\ is the one with the config and
    from pylib.config import config, parse_args
except ModuleNotFoundError:
    from config import config, parse_args
import pylib.vzreducer.constants as c
from pylib.vzreducer.parse_input_file import parse_input_file
from pylib.vzreducer.read_solid_waste_release import SolidWasteReleaseData
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
        logging.info("Reduction will be performed for the following user-defined waste sites : {}".format(', '.join(set(input_data[c.WASTE_SITES_KEY])&set(solid_waste_release.sites))))
        return sorted(list((set(input_data[c.WASTE_SITES_KEY])&set(solid_waste_release.sites))))
    logging.info("Reduction will be executed for all waste sites included in the solid waste inventory")
    return sorted(solid_waste_release.sites)

def get_copc_list(input_data, solid_waste_release):
    """ get copcs to reduce """
    if len(input_data[c.COPCS_KEY])>0:
        logging.info("Reduction will be performed for the following user-defined COPCs : {}".format(', '.join(input_data[c.COPCS_KEY])))
        return input_data[c.COPCS_KEY]
    logging.info("Reduction will be executed for all COPCs included in the solid waste inventory")
    return sorted(solid_waste_release.copcs)


def reduce_for_copc_site(solid_waste_release, copc, site,
        summary_file, output_folder,input_data):
    """
        extract a TimeSeries instance from solid_waste_release
        corresponding to the target copc/site and then reduce it
        
        returns True if succeded in reducing; false otherwise
    
    """
    timeseries = solid_waste_release.extract(copc, site)
    worked = reduce_dataset(
            timeseries, summary_file, output_folder, input_data
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
                #SLL--inserted input_data as an argument for reduction constants moved to input file
                worked = reduce_for_copc_site(
                        solid_waste_release, copc, site,
                        summary_file, output_folder, input_data)
                if not worked:
                    continue
            except TypeError as e:
#SLL: switched the order of the following two lines so that the error will be logged if an exception is thrown...
                logging.error("failed at {} {}".format(copc, site))
                raise Exception(e)


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
    logging.info(input_data)
    output_folder = get_output_folder(args)
    summary_filename = "summary.csv"
    summary_header = ','.join(input_data['SUMMARY_HEADER']) +'\n'
    summary_file = reset_summary_file(output_folder, summary_filename,summary_header)

    #replaced the area keys with source files key in case the areas change?
    #for filekey in [c._200E_KEY, c._200W_KEY]:
    for filekey in  input_data[c.SOURCE_FILES_KEY]:
        reduce_input_data(filekey, input_data, summary_file,
                output_folder)

    logging.info("END execution")


if __name__ == "__main__":
    main()

