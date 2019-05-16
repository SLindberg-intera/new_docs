import logging
import os
import matplotlib.pyplot as plt
import pylib.vzreducer.constants as c
import pylib.vzreducer.reduce_flux as red_flux
import pylib.vzreducer.plots as p
import numpy as np

def log_info(reduction_result):
    msg = "{} {} reduced: {}  E_flx: {:.2g} E_m:{:.2g}"
    rr = reduction_result
    s = msg.format(
            rr.mass.copc,
            rr.mass.site,
            rr.num_reduced_points,
            rr.relative_max_flux_error,
            rr.relative_total_mass_error
    )
    logging.info(s)


def reduce_dataset(timeseries, summary_file, output_folder, input_data):
    copc = timeseries.copc
    site = timeseries.site
    if timeseries.are_all_zero():
        logging.info("Skipped {} {} - all zero".format(
            copc, site))
        return False    
    mx = np.argmax(timeseries.values)
    points = [0, mx, len(timeseries)]

    result = []
    for ix in range(len(points)-1):
        trunc = timeseries.slice(points[ix], points[ix+1]+1)
        if len(trunc)<=1:
            continue
    res = red_flux.reduce_flux(timeseries, .01, .001)
    #result.append(res) 
    f, ax1, ax2 = p.reduced_timeseries_plot(res)
    plt.savefig(os.path.join(output_folder, 
        "{}-{}-{}.png".format(copc, site, ix)))
    plt.close(f)
    log_info(res)

