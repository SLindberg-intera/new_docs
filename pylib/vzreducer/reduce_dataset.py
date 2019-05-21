import logging
import os
import matplotlib.pyplot as plt
import pylib.vzreducer.constants as c
import pylib.vzreducer.reduce_flux as red_flux
import pylib.vzreducer.plots as p
import numpy as np

def log_info(reduction_result):
    msg = "{} {} reduced: {} E_m:{:.2g}%"
    rr = reduction_result
    s = msg.format(
            rr.mass.copc,
            rr.mass.site,
            rr.num_reduced_points,
            rr.relative_total_mass_error*100
    )
    logging.info(s)

SMOOTH = "SMOOTH"
RAW = "RAW"

def reduce_dataset(timeseries, summary_file, output_folder, input_data):
    copc = timeseries.copc
    site = timeseries.site
    if timeseries.are_all_zero():
        logging.info("Skipped {} {} - all zero".format(
            copc, site))
        return False    
    mx = np.argmax(timeseries.values)
    points = [0, mx, len(timeseries)]
    x = timeseries.times

    area = 100*np.std(timeseries.values)*(x[-1]-x[0])
    ythresh = 100*np.std(timeseries.values)
    out_error = 1
    out_error_last = out_error
    OUT_ERROR_THRESHOLD = 1e-2
    UPPER_N = 50
    LOWER_N = 10
    last_result = None 
    MAX_ITERATIONS = 80

    solve_type = SMOOTH

    for ix in range(MAX_ITERATIONS):

        res = red_flux.reduce_flux(timeseries, area, ythresh, 
                solve_type=solve_type)
        #result.append(res) 
        out_error = abs(res.relative_total_mass_error)
        if abs(out_error_last - out_error) < 1e-3:
            pass #break
        if out_error < OUT_ERROR_THRESHOLD and len(res.reduced_flux)>=LOWER_N:
            last_result = res
            break
        if len(res.reduced_flux) > 2*UPPER_N:
            solve_type = RAW
        ythresh = 0.5*ythresh
        area = 0.5*area
        out_error_last = out_error
        last_result = res

    if ix>=MAX_ITERATIONS - 1:
        logging.info("MAX ITERATIONS")

    log_info(last_result)
    if out_error*100 > 1:
        f, ax1, ax2 = p.reduced_timeseries_plot(last_result)
        plt.savefig(os.path.join(output_folder, 
            "{}-{}.png".format(copc, site)))
        plt.close(f)
