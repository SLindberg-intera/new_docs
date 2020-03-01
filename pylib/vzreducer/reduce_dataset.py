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
import pylib.timeseries.timeseries_math as tsmath
from pylib.datareduction.reduction_result import ReductionResult
import scipy.signal as sig
import datetime

from pylib.pygit.git import get_version



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
    """ make a plot of the reduction result and place it in output_folder"""
    copc = reduction_result.mass.copc
    site = reduction_result.mass.site
    f, ax1, ax2 = p.reduced_timeseries_plot(reduction_result)
    plt.savefig(os.path.join(output_folder,
            "{}-{}.png".format(copc, site)),bbox_inches = 'tight', dpi = 1200)
    plt.close(f)


def reduce_dataset(timeseries, summary_file, output_folder, input_data):
    """ take a TimeSeries object and reduce it.

    write a summary into summary_folder

    """
    copc = timeseries.copc
    site = timeseries.site
    if timeseries.are_all_zero():
        logging.info("Skipped {} {} - all zero".format(
            copc, site))
        return False

    #for site/copc with nonzero fluxes, save unreduced timeseries to o_timeseries (original) for error correction (below)
    o_timeseries = timeseries

    # grab user-defined constant values from input JSON file
    close_gaps = input_data[c.GAP_CLOSED].lower()
    if input_data[c.GAP_DELTA]:
        gap_delta = int(input_data[c.GAP_DELTA])
    else:
        gap_delta = 0
    if input_data[c.GAP_STEPS]:
        gap_steps = int(input_data[c.GAP_STEPS])
    else:
        gap_steps = 0

    diff_mass = input_data[c.DIFF_MASS].lower()

#Placeholder code if flux_floor is needed in the future
    #if input_data[c.FLUX_FLOOR_KEY] is not "":
    #    flux_floor = float(input_data[c.FLUX_FLOOR_KEY])

    #else:
    #    flux_floor = ""
    #    logging.info("no flux floor value is being applied")

    upper_n = int(input_data[c.UPPER_N_KEY])
    lower_n = int(input_data[c.LOWER_N_KEY])

    #the maximum number of reduction iterations
    max_iters = int(input_data[c.MAX_ITERATIONS_KEY])

    #the maximum number of iterations for mass error redistribution
    max_err_iters = int(input_data[c.MAX_ERR_ITERATIONS_KEY])

    epsilon = float(input_data[c.EPSILON])

    res = red_flux.reduce_flux(timeseries, epsilon, close_gaps, gap_delta, gap_steps)
    out_error = abs(res.relative_total_mass_error)
    #last_result = res
    out_error_last = out_error
    last_timesteps = 0

    if res.mass.values[-1] > float(input_data[c.MASS_THRESHOLD]):
        out_error_threshold = float(input_data[c.LOWER_OUT_ERROR_THRESHOLD_KEY])
    else:
        out_error_threshold = float(input_data[c.UPPER_OUT_ERROR_THRESHOLD_KEY])

    for ix in range(max_iters):
        timesteps = len(res.reduced_flux)
        out_error = abs(res.relative_total_mass_error)

        #if the timesteps are within the acceptable range and error < error threshold --> done
        if timesteps <= upper_n and timesteps >= lower_n and out_error <= out_error_threshold:
            last_result = res
            used_epsilon = epsilon
            break

        elif timesteps < lower_n:
            epsilon = epsilon / 2

        elif timesteps <= upper_n and timesteps >= lower_n and out_error > out_error_threshold and out_error < out_error_last:
            epsilon = epsilon / 2

        elif timesteps <= upper_n and timesteps >= lower_n and out_error > out_error_threshold and last_timesteps <= timesteps:
            epsilon = epsilon / 2

        #after exceeding max points then iterate between upper_n and last epsilon where timesteps < upper_n
        elif timesteps > upper_n and last_timesteps < timesteps:
            epsilon = epsilon * 1.75

        elif timesteps <= last_timesteps:
            epsilon = epsilon / 1.5

        #keep the result as the last result only if timesteps are < max and if error is lower than previous result
        if timesteps <= upper_n and out_error <= out_error_last:
            last_result = res
            last_timesteps = timesteps
            out_error_last = out_error
            used_epsilon = epsilon

        res = red_flux.reduce_flux(timeseries, epsilon, close_gaps, gap_delta, gap_steps)

    if ix>= max_iters - 1:
        logging.info("MAX ITERATIONS exceeded")

    n_iterations = ix+1

    if diff_mass == "true":
        #check error in cummulative mass differences of reduced and original dataset after reduction
        mass = last_result.mass
        r_mass = last_result.reduced_mass
        dmass = mass - r_mass
        diff_iter = 0
        corrected = False
        while abs(max(dmass.values))/mass.values[-1] > out_error_threshold and diff_iter <max_err_iters:# or abs(min(dmass.values))/mass.values[-1] > out_error_threshold:
            year_err = dmass.times[np.where(dmass.values == max(dmass.values))].tolist()[0]
            year2 = r_mass.times[np.where(r_mass.times > year_err)][0]
            year1 = r_mass.times[np.where(r_mass.times < year_err)][-1]
            interval  = int((year2-year1)/2)
            diff_iter+=1
            if interval >= 2:
                years = [year+interval for year in range(year1, year2, interval)][0:-1]
                revised_years = sorted(set([*r_mass.times.tolist(), *years]))
                r_flux = timeseries.subset(revised_years)
                r_mass = tsmath.integrate(r_flux)
                dmass=mass-r_mass
                corrected = True
            else:
                break

        if corrected:
            last_result = ReductionResult(
            flux=last_result.flux,
            mass=last_result.mass,
            reduced_flux=r_flux,
            reduced_mass=r_mass)

    out_error_last = abs(last_result.relative_total_mass_error)
    delta_mass = last_result.total_mass_error

     # for tracking reduction of error through the iterations....
    max_err = last_result.total_mass_error
    min_err = last_result.total_mass_error
    iter = 0
    rr = last_result

    if abs(last_result.relative_total_mass_error)>out_error_threshold:
    #find peaks for data rebalance and reporting
        #Note: departure from HSS algorithm--no peak width consideration for solid waste result reduction
        peaks, _ = sig.find_peaks(rr.reduced_flux.values)
        pneg, _ = sig.find_peaks((-rr.reduced_flux.values))

        peaks = rr.reduced_flux.times[peaks]
        pneg = rr.reduced_flux.times[pneg]

        peaks = np.isin(o_timeseries.times,peaks)
        pneg = np.isin(o_timeseries.times,pneg)
        peaks = np.where(peaks)
        pneg = np.where(pneg)

        peaks = peaks[0]
        pneg = pneg[0]




    while abs(last_result.relative_total_mass_error) > out_error_threshold and iter < max_err_iters:
        rr = red_flux.rebalance_valleys(rr,peaks,pneg)
        #keep the lowest total_mass_error
        if abs(rr.total_mass_error) < abs(last_result.total_mass_error):
            last_result = rr
            min_err = rr.total_mass_error
        else:
            max_err = rr.total_mass_error
        iter += 1

    logging.info("min error: {}; max error: {}--after rebalance iterations {}".format(min_err,max_err,iter))
    #last_result.flux.values = last_result.flux.values
    #last_result.reduced_flux.values = last_result.reduced_flux.values


#end of Neil's code...

    plot_file = summary_plot(last_result, output_folder)
    filename = last_result.to_csv(output_folder)

    # eventually update a module with insert_header information functionality but keeping it here for now...
    header_info = 'Site Name: {}\n Date Created: {}\n Script Version: {} \nCOPC: {} \n'.format(rr.mass.site, datetime.datetime.now().strftime('%Y/%m/%d'),get_version(), rr.mass.copc )


    with open(filename,'r+') as f:
        old = f.read()
        f.seek(0)
        f.write(header_info +old)



    summary_template = input_data["SUMMARY_TEMPLATE"] + '\n'
    summary_info(last_result, filename, summary_file, summary_template,
            delta_mass, used_epsilon, n_iterations, out_error_last)
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