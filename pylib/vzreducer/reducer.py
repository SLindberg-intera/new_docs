from config import config, parse_args 
import logging
import constants as c
import os
from parse_input_file import parse_input_file
from read_solid_waste_release import SolidWasteReleaseData
from pylib.vzreducer.reduce_timeseries import ReducedTimeSeries
from plots import residual_plot, mass_plot, recursive_plot, reduced_timeseries_plot 
import matplotlib.pyplot as plt
from pylib.vzreducer.summary_report import SummaryReportRecord

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
        copc_list = solid_waste_release.copcs
    if len(input_data[c.WASTE_SITES_KEY])>0:
        site_list = input_data[c.WASTE_SITES_KEY]
    else:    
        site_list = solid_waste_release.sites

    summary_file = os.path.join(output_folder, "summary.csv")
    with open(summary_file, "w") as f:
        f.write("test line\n")
    for copc in copc_list:
        for site in site_list:
            try:
                timeseries = solid_waste_release.extract(copc, site)
                if timeseries.are_all_zero():
                    logging.info("Skipped {} {} - all zero".format(
                        copc, site))
                    continue
                reduced_timeseries = ReducedTimeSeries.from_timeseries(
                        timeseries)
                f, axes = reduced_timeseries_plot(reduced_timeseries)
                f.savefig(
                        os.path.join(output_folder,
                        "{} {}.png".format(copc, site))
                )
                logging.info("reduced {} {} to {}".format(
                    copc, site, len(reduced_timeseries)))
                plt.close(f)
                try:
                    srr = SummaryReportRecord.from_reduced_timeseries(
                            reduced_timeseries)
                    with open(summary_file, "a") as f:
                        f.write("{}\n".format(copc))
                        f.write(srr.to_line(input_data[c.SUMMARY_TEMPLATE_KEY]))
                except Exception as e:
                    print("error: {}".format(str(e)))


            except TypeError:
                logging.error("failed at {} {}".format(copc, site))
    logging.info("END execution")

