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

SMOOTH = "SMOOTH"  #MOVED TO INPUT file 08.09.2019
RAW = "RAW"        #MOVED TO INPUT file 08.09.2019
flux_floor = 1e-15
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
    copc = timeseries.copc
    site = timeseries.site
    if timeseries.are_all_zero():
        logging.info("Skipped {} {} - all zero".format(
            copc, site))
        return False
    else:
        years = timeseries.times
        values = timeseries.values
        #  anything less than Flux floor is considered to be zero
        #  we are removing anything under flux floor to help remove jidder

        non_zero_ind = np.where(values > flux_floor)[0]
        # add last zero before flux increases above zero
        if non_zero_ind[-1] + 1 < values.size - 1 and non_zero_ind[-1] + 1 not in non_zero_ind:
            ind = non_zero_ind[-1] + 1
            non_zero_ind = np.append(non_zero_ind, [ind])
            low_val = values[ind]
            # if low_val is not 0 then find then next zero
            if low_val != 0:
                for i in range(ind, values.size):
                    if values[i] == 0:
                        ind = i
                        break
                    elif values[i] < low_val:
                        low_val = values[i]
                        ind = i
                if ind not in non_zero_ind:
                    non_zero_ind = np.append(non_zero_ind, [ind])
        # add last zero before flux increases above zero
        if non_zero_ind[0] - 1 > 0 and non_zero_ind[0] - 1 not in non_zero_ind:
            ind = non_zero_ind[0] - 1
            non_zero_ind = np.append(non_zero_ind, [ind])
            low_val = values[ind]
            # if low_val is not 0 then find the previous zero
            if low_val != 0:
                for i in range(ind, 0, -1):
                    if values[i] == 0:
                        ind = i
                        break
                    elif values[i] < low_val:
                        low_val = values[i]
                        ind = i
                if ind not in non_zero_ind:
                    non_zero_ind = np.append(non_zero_ind, [ind])
        if non_zero_ind[0] - 1 > 0:
            non_zero_ind = np.append(non_zero_ind, non_zero_ind[0] - 1)
        # add first zero after data decreases to zero
        if non_zero_ind[-1] + 1 < values.size - 1:
            non_zero_ind = np.append(non_zero_ind, non_zero_ind[-1] + 1)
        if 0 not in non_zero_ind:
            non_zero_ind = np.append(non_zero_ind, [0])
        if (values.size - 1) not in non_zero_ind:
            non_zero_ind = np.append(non_zero_ind, [(values.size - 1)])
        #    zero = np.where(values > 0)[0][0]-1
        #    if zero > 0 and zero not in non_zero_ind:
        #        non_zero_ind = np.append(non_zero_ind,[zero])
        #    zero = np.where(values > 0)[0][0]+1
        #    if zero > 0 and not zero in non_zero_ind:
        #        non_zero_ind = np.append(non_zero_ind,[zero])
        #    floor = np.where(values > flux_floor)[0][0]-1
        #    if floor < years.size-1 and floor not in non_zero_ind:
        #        non_zero_ind = np.append(non_zero_ind,[floor])
        #    floor = np.where(values > flux_floor)[0][0]+1
        #    if floor < years.size-1 and floor not in non_zero_ind:
        #        non_zero_ind = np.append(non_zero_ind,[floor])

        non_zero_ind = np.sort(non_zero_ind)
        years_mod = years[non_zero_ind]
        values_mod = values[non_zero_ind]
        if years_mod.size < 3:
            years_mod = years
            values_mod = values
            values_mod = 0
        #    elif years_mod.size < 200:
        #        o_ts = TimeSeries(years,values,None,None)
        #        r_ts = TimeSeries(years_mod,values_mod,None,None)
        #        rr = ReductionResult(
        #                flux=o_ts,
        #                mass=o_ts.integrate(),
        #                reduced_flux=r_ts,
        #                reduced_mass=r_ts.integrate())
        #        peaks, _ = sig.find_peaks(rr.reduced_flux.values,width=3,rel_height=1)
        #        return rr.reduced_flux.times, rr.reduced_flux.values,-rr.total_mass_error,peaks.size
        elif (TimeSeries(years, values, None, None).integrate().values[-1]) < 1e12:  # equivalent of 1 ci
            years_mod = years
            values_mod = values

        # normalize Values
        maxval = np.max(values_mod)
        values_mod = values_mod / maxval
        o_timeseries = TimeSeries(years, values / maxval, None, None)
        o_mass = o_timeseries.integrate()
        timeseries = TimeSeries(years_mod, values_mod, None, None)

    #normalize fluxes
    #    max_val = np.max(timeseries.values)
    #    timeseries.values = timeseries.values/max_val
    mx = np.argmax(timeseries.values)
    # unused variable...SLL
    points = [0, mx, len(timeseries)]
    x = timeseries.times
    # unused variable...SLL
    mass = timeseries.integrate()

    area = 100*np.std(timeseries.values)*(x[-1]-x[0])
    # unused variable (already commented out)...SLL
    #mass.values[-1]
    ythresh = 100*np.std(timeseries.values)
    out_error = 1
    # tracked but unused variable?...SLL
    out_error_last = out_error

    # SLL--constants to move to vz-reducer-input.json file
    OUT_ERROR_THRESHOLD = float(input_data[c.OUT_ERROR_THRESHOLD_KEY]) #1e-2
    UPPER_N =  int(input_data[c.UPPER_N_KEY]) #50
    LOWER_N = int(input_data[c.LOWER_N_KEY]) #15

    last_result = None

    # SLL--constant to move to vz-reducer-input.json file(I had bumped it up to 100 in testing)
    MAX_ITERATIONS = int(input_data[c.MAX_ITERATIONS_KEY])  #80

    solve_type = input_data[c.SOLVE_TYPE_KEY]   #SMOOTH
    simple_peaks = False

    for ix in range(MAX_ITERATIONS):

        res = red_flux.reduce_flux(timeseries, area, ythresh, 
                solve_type=solve_type,
                simple_peaks=simple_peaks
                )
        out_error = abs(res.relative_total_mass_error)
        if out_error < OUT_ERROR_THRESHOLD and len(res.reduced_flux)>=LOWER_N:
            last_result = res
            out_error_last = res.relative_total_mass_error
            break
        if len(res.reduced_flux) > 2*UPPER_N:
            simple_peaks = True
            solve_type = RAW
        ythresh = 0.5*ythresh
        area = 0.5*area
        if abs(out_error_last) > out_error or abs(out_error_last)==1: #trying adding logic that only if error is reduced replace the last result...
            out_error_last = res.relative_total_mass_error

            last_result = res
            logging.info("Best fit consistent with current iteration")
        else:
            logging.info("Best fit occurred prior to current iteration")

    if ix>=MAX_ITERATIONS - 1:
        logging.info("MAX ITERATIONS")


    #delta_mass = last_result.total_mass_error

    #last_result = red_flux.rebalance(last_result)
    #plot_file = summary_plot(last_result, output_folder)
    #last_result.to_csv(output_folder)
    #used_ythresh = ythresh
    #used_area = area
    #n_iterations = ix
    #summary_info(last_result, summary_file,
    #        delta_mass, used_ythresh, used_area, n_iterations, out_error_last)
    #log_info(last_result)


#Add the point prior to first (flux > 0), add point after last of (flux >0)
    last_result = add_zero_markers(o_timeseries,last_result.reduced_flux,flux_floor)


    rr = last_result
    #find peaks for data rebalance and reporting
    peaks, _ = sig.find_peaks(rr.reduced_flux.values,width=3,rel_height=1)
    if peaks.size == 0 :
        peaks, _ = sig.find_peaks(rr.reduced_flux.values,width=2,rel_height=1)
        if peaks.size == 0:
            peaks, _ = sig.find_peaks(rr.reduced_flux.values,width=1,rel_height=1)
    pneg, _ = sig.find_peaks(-rr.reduced_flux.values,width=3,rel_height=1)
    if pneg.size == 0:
        pneg, _ = sig.find_peaks(-rr.reduced_flux.values,width=2,rel_height=1)
        if pneg.size == 0:
            pneg, _ = sig.find_peaks(-rr.reduced_flux.values,width=1,rel_height=1)

    peaks = rr.reduced_flux.times[peaks]
    pneg = rr.reduced_flux.times[pneg]

    peaks = np.isin(o_timeseries.times,peaks)
    pneg = np.isin(o_timeseries.times,pneg)
    peaks = np.where(peaks)
    pneg = np.where(peaks)

    peaks = peaks[0]
    pneg = pneg[0]
    iter = 0
    while abs(last_result.total_mass_error*maxval) != 0 and iter < 100:
        rr = red_flux.rebalance_valleys(rr,peaks,pneg)
        #keep the lowest total_mass_error
        if abs(rr.total_mass_error) < abs(last_result.total_mass_error):
            last_result = rr
        iter += 1

    out_times = last_result.reduced_flux.times
    out_values = last_result.reduced_flux.values
    #return the reduced data, undo normalize of the values (*maxval)
    return out_times, out_values*maxval,-(last_result.total_mass_error * maxval),peaks.size
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