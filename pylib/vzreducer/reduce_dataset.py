import logging
import os
import numpy as np
import matplotlib.pyplot as plt
import pylib.vzreducer.constants as c
import pylib.vzreducer.reduce_flux as red_flux
import pylib.vzreducer.plots as p
from pylib.vzreducer.summary_file import summary_info
#neils code imports...
from pylib.timeseries.timeseries import TimeSeries
from pylib.datareduction.reduction_result import ReductionResult
import scipy.signal as sig
import datetime

from pylib.pygit.git import get_version

#check other branch for code change here....
SMOOTH = "SMOOTH"  #MOVED TO INPUT file 08.09.2019
RAW = "RAW"        #MOVED TO INPUT file 08.09.2019





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


def summary_plot(reduction_result, output_folder):
    """ make a plot of hte reduction result and place it in output_folder"""
    copc = reduction_result.mass.copc
    site = reduction_result.mass.site
    f, ax1, ax2 = p.reduced_timeseries_plot(reduction_result)
    plt.savefig(os.path.join(output_folder, 
            "{}-{}.png".format(copc, site)))
    plt.close(f)


def reduce_dataset(timeseries, summary_file, output_folder, input_data):
    """ take a TimeSeries object and reduce it.

    write a summary into summary_folder

    """
    #grab user-defined constant values from input JSON file
    flux_floor = float(input_data[c.FLUX_FLOOR_KEY])  # 1e-15
    peak_height = float(input_data[c.PEAK_HEIGHT_KEY]) #1e-10 (for 08.20.2019 reduction for review)

    copc = timeseries.copc
    site = timeseries.site
    if timeseries.are_all_zero():
        logging.info("Skipped {} {} - all zero".format(
            copc, site))
        return False
    else:
        #set o_timeseries = unreduced (original) timeseries--not normalized
        o_timeseries = timeseries
        o_mass = o_timeseries.integrate()




    #find timestep of max flux
    mx = np.argmax(timeseries.values)

    # unused variable...commented out--SLL
    # points = list of indexes for the first timestep, max timestep, last timestep
    #points = [0, mx, len(timeseries)]

    x = timeseries.times

    # unused variable?...SLL
    #mass = timeseries.integrate()

    area = 100*np.std(timeseries.values)*(x[-1]-x[0])
    # unused variable (already commented out)...SLL
    #mass.values[-1]
    ythresh = 100*np.std(timeseries.values)
    out_error = 1
    # tracked but unused variable?...commented out--SLL
    #out_error_last = out_error

    # SLL--constants to move to vz-reducer-input.json file--original assigned values in comments
    OUT_ERROR_THRESHOLD = float(input_data[c.OUT_ERROR_THRESHOLD_KEY]) #1e-2
    UPPER_N =  int(input_data[c.UPPER_N_KEY]) #50
    LOWER_N = int(input_data[c.LOWER_N_KEY]) #15


    last_result = None

    # SLL--constant to move to JSON input file--original assigned values in comments
    #the maximum number of reduction iterations
    MAX_ITERATIONS = int(input_data[c.MAX_ITERATIONS_KEY])  #80
    #the maximum number of iterations for mass error redistribution
    MAX_ERR_ITERATIONS = int(input_data[c.MAX_ERR_ITERATIONS_KEY])

    solve_type = input_data[c.SOLVE_TYPE_KEY]   #SMOOTH
    simple_peaks = False

    for ix in range(MAX_ITERATIONS):

        res = red_flux.reduce_flux(timeseries, area, ythresh, peak_height,
                solve_type=solve_type,
                simple_peaks=simple_peaks
                )
        out_error = abs(res.relative_total_mass_error)
        if out_error < OUT_ERROR_THRESHOLD and len(res.reduced_flux)>=LOWER_N:
            last_result = res
            out_error_last = out_error

            break
        if len(res.reduced_flux) > 2*UPPER_N:
            simple_peaks = True
            solve_type = RAW

        ythresh = 0.5*ythresh
        area = 0.5*area


    if ix>=MAX_ITERATIONS - 1:
        logging.info("MAX ITERATIONS exceeded")

#this is the original code--commented out to incorporate the GW reducer's functionality to distribute error to valleys
    delta_mass = last_result.total_mass_error

    #last_result = red_flux.rebalance(last_result)
    #plot_file = summary_plot(last_result, output_folder)
    #last_result.to_csv(output_folder)
    used_ythresh = ythresh
    #used_area = area
    #n_iterations = ix
    #summary_info(last_result, summary_file,
    #        delta_mass, used_ythresh, used_area, n_iterations, out_error_last)
    #log_info(last_result)


#Add the point prior to first (flux > 0), add point after last of (flux >0)
    last_result = add_zero_markers(o_timeseries,last_result.reduced_flux,flux_floor)


    rr = last_result
    #find peaks for data rebalance and reporting
    peaks, _ = sig.find_peaks(rr.reduced_flux.values)
#SSL commenting out the following; going with just the peaks and not depending on the peak width for now....
    #peaks, _ = sig.find_peaks(rr.reduced_flux.values,width=3,rel_height=1)
    #if peaks.size == 0 :
    #    peaks, _ = sig.find_peaks(rr.reduced_flux.values,width=2,rel_height=1)
    #    if peaks.size == 0:
    #        peaks, _ = sig.find_peaks(rr.reduced_flux.values,width=1,rel_height=1)
    pneg, _ = sig.find_peaks((-rr.reduced_flux.values))
# SSL commenting out the following; going with just the peaks and not depending on the peak width for now....
    #pneg, _ = sig.find_peaks(-rr.reduced_flux.values,width=3,rel_height=1)
    #if pneg.size == 0:
    #    pneg, _ = sig.find_peaks(-rr.reduced_flux.values,width=2,rel_height=1)
    #    if pneg.size == 0:
    #        pneg, _ = sig.find_peaks(-rr.reduced_flux.values,width=1,rel_height=1)

    peaks = rr.reduced_flux.times[peaks]
    pneg = rr.reduced_flux.times[pneg]

    peaks = np.isin(o_timeseries.times,peaks)
    pneg = np.isin(o_timeseries.times,pneg)
    peaks = np.where(peaks)
#made the following change [peaks --> pneg] to code and commented out the old stuff....check with Neil on this change...
    #pneg = np.where(peaks)
    pneg = np.where(pneg)

    peaks = peaks[0]
    pneg = pneg[0]
    iter = 0

    # for tracking reduction of error through the iterations....
    max_err = last_result.total_mass_error
    min_err = last_result.total_mass_error
    # got rid of multiplying mass error by maxval (currently not normalizing fluxes-08.2019)
    # while abs(last_result.total_mass_error * maxval) != 0 and iter < 100:
    while abs(last_result.total_mass_error) != 0 and iter < MAX_ERR_ITERATIONS: #100:
        rr = red_flux.rebalance_valleys(rr,peaks,pneg)
        #keep the lowest total_mass_error
        if abs(rr.total_mass_error) < abs(last_result.total_mass_error):
            last_result = rr
            min_err = rr.total_mass_error

        else:

            max_err = rr.total_mass_error

        iter += 1
    logging.info("min error: {}; max error: {}--after rebalance iterations {}".format(min_err,max_err,iter))
    last_result.flux.values = last_result.flux.values
    last_result.reduced_flux.values = last_result.reduced_flux.values

    #out_times = last_result.reduced_flux.times
    #out_values = last_result.reduced_flux.values
    #return the reduced data, undo normalize of the values (*maxval)
    #return out_times, out_values*maxval,-(last_result.total_mass_error * maxval),peaks.size
#end of Neil's code...
    #delta_mass = last_result.total_mass_error
    #last_result. = red_flux.rebalance(last_result)
    plot_file = summary_plot(last_result, output_folder)
    filename = last_result.to_csv(output_folder)

    # eventually update a module with insert_header information functionality but keeping it here for now...
    header_info = 'Site Name: {}\n Date Created: {}\n Script Version: {} \nCOPC: {} \n'.format(rr.mass.site, datetime.datetime.now().strftime('%Y/%m/%d'),get_version(), rr.mass.copc )


    with open(filename,'r+') as f:
        old = f.read()
        f.seek(0)
        f.write(header_info +old)
    #used_ythresh = ythresh
    used_area = area
    n_iterations = ix

    summary_template = input_data["SUMMARY_TEMPLATE"] + '\n'
    summary_info(last_result, filename, summary_file, summary_template,
            delta_mass, used_ythresh, used_area, n_iterations, out_error_last)
    log_info(last_result)
#-------------------------------------------------------------------------------
#
def add_zero_markers(o_ts,r_ts,flux_floor):
    new_ts = r_ts
    num_steps = o_ts.times.size
    if(o_ts.values[0] <= 0):
        zero_ind = np.where(o_ts.values > 0)[0][0]-1
        if not np.any(r_ts.times == o_ts.times[zero_ind]):
            r_times,r_values = insert_point(new_ts.times,new_ts.values,o_ts.times[zero_ind],o_ts.values[zero_ind])
            new_ts = TimeSeries(r_times,r_values,None,None)
    zero_ind = 0
    if(o_ts.values[-1] <= 0):
        zero_ind = np.where(o_ts.values > 0)[0][-1]+1
        if zero_ind < num_steps and not np.any(r_ts.times == o_ts.times[zero_ind]):
            r_times,r_values = insert_point(new_ts.times,new_ts.values,o_ts.times[zero_ind],o_ts.values[zero_ind])
            new_ts = TimeSeries(r_times,r_values,None,None)
#    if(o_ts.values[0] <= flux_floor):
#        zero_ind = np.where(o_ts.values > 0)[0][0]-1
#        if not np.any(r_ts.times == o_ts.times[zero_ind]):
#            r_times,r_values = insert_point(new_ts.times,new_ts.values,o_ts.times[zero_ind],o_ts.values[zero_ind])
#            new_ts = TimeSeries(r_times,r_values,None,None)
#    zero_ind = 0
#    if(o_ts.values[-1] <= flux_floor):
#        zero_ind = np.where(o_ts.values > 0)[0][-1]+1
#        if zero_ind < num_steps and not np.any(r_ts.times == o_ts.times[zero_ind]):
#            r_times,r_values = insert_point(new_ts.times,new_ts.values,o_ts.times[zero_ind],o_ts.values[zero_ind])
#            new_ts = TimeSeries(r_times,r_values,None,None)
    return ReductionResult(
                    flux=o_ts,
                    mass=o_ts.integrate(),
                    reduced_flux=new_ts,
                    reduced_mass=new_ts.integrate())
#-------------------------------------------------------------------------------
#
def insert_point(times, values,time,value):
    times = np.append(times,time)
    times.sort(kind='mergesort')
    ind = np.where(times == time)[0][0]
    values2 = np.insert(values,ind,value)

    return times, values2