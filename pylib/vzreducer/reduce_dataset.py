from pylib.vzreducer.summary_report import SummaryReportRecord
import logging
from pylib.vzreducer.reduce_timeseries import ReducedTimeSeries
from plots import reduced_timeseries_plot 
import os
import matplotlib.pyplot as plt
import pylib.vzreducer.constants as c


REQUIRED_RELATIVE_ERROR = 1e-6 #4
MAX_ITERATIONS = 20
MAX_OUTPUT_POINTS = 70

def reduce_dataset(timeseries, summary_file, output_folder, input_data):
    copc = timeseries.copc
    site = timeseries.site
    if timeseries.are_all_zero():
        logging.info("Skipped {} {} - all zero".format(
            copc, site))
        return False    
    relative_error = 1
    area = None
    threshold_peak = None
    ix = 0
    n_points = len(timeseries)
    while (relative_error > REQUIRED_RELATIVE_ERROR or n_points>MAX_OUTPUT_POINTS) and ix < MAX_ITERATIONS:
        reduced_timeseries = ReducedTimeSeries.from_timeseries(
            timeseries, area=area, threshold_peak=threshold_peak)
        relative_error = abs(reduced_timeseries.relative_mass_error)
        # tighten for next step
        #threshold_peak = 0.5*reduced_timeseries.threshold_peak
        area = 0.51*reduced_timeseries.area
        n_points = len(reduced_timeseries)
        if n_points < 10:
            area = 0.3*area
            relative_error = 1
            ix+=1
            continue
        if n_points>200:
            """ we were probably way too constrained"""
            area = 1e2*area
            #threshold_peak = 1.7*threshold_peak
        ix+=1
        
    if ix==MAX_ITERATIONS:
        print("max iterations")

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
            f.write(srr.to_line(input_data[c.SUMMARY_TEMPLATE_KEY]))
    except Exception as e:
        print("error: {}".format(str(e)))
