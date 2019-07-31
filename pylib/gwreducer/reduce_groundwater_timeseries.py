"""
    use data reduction method on groundwater timeseries

"""
import numpy as np
from pylib.timeseries.timeseries import TimeSeries
from pylib.gwreducer import reduce_flux as red_flux
from pylib.datareduction.reduction_result import ReductionResult
SMOOTH = 'SMOOTH'
RAW = 'RAW'
import scipy.signal as sig
def reduce_dataset(years, values,flux_floor=0,max_tm_error=0):
    """ takes  times and values and then reduces it

    returns reduced_times and reduced_values

    if all elements are zero, it returns False

    flux_floor > flux == 0
    max_tm_error > total mass error
    """

    #  anything less than Flux floor is considered to be zero
    #  we are removing anything under flux floor to help remove jidder

    non_zero_ind = np.where(values > flux_floor)[0]
    #add last zero before flux increases above zero
    if non_zero_ind[-1]+1 < values.size-1 and non_zero_ind[-1]+1 not in non_zero_ind:
        ind = non_zero_ind[-1]+1
        non_zero_ind = np.append(non_zero_ind,[ind])
        low_val = values[ind]
        #if low_val is not 0 then find then next zero
        if low_val != 0:
            for i in range(ind,values.size):
                if values[i] == 0:
                    ind = i
                    break
                elif values[i] < low_val:
                    low_val = values[i]
                    ind = i
            if ind not in non_zero_ind:
                non_zero_ind = np.append(non_zero_ind,[ind])
    #add last zero before flux increases above zero
    if non_zero_ind[0]-1 > 0 and non_zero_ind[0]-1 not in non_zero_ind:
        ind = non_zero_ind[0]-1
        non_zero_ind = np.append(non_zero_ind,[ind])
        low_val = values[ind]
        #if low_val is not 0 then find the previous zero
        if low_val != 0:
            for i in range(ind, 0,-1):
                if values[i] == 0:
                    ind = i
                    break
                elif values[i] < low_val:
                    low_val = values[i]
                    ind = i
            if ind not in non_zero_ind:
                non_zero_ind = np.append(non_zero_ind,[ind])
    if non_zero_ind[0]-1 > 0:
        non_zero_ind = np.append(non_zero_ind,non_zero_ind[0]-1)
    #add first zero after data decreases to zero
    if non_zero_ind[-1]+1 < values.size-1:
        non_zero_ind = np.append(non_zero_ind,non_zero_ind[-1]+1)
    if 0 not in non_zero_ind:
        non_zero_ind = np.append(non_zero_ind,[0])
    if (values.size -1) not in non_zero_ind:
        non_zero_ind = np.append(non_zero_ind,[(values.size -1)])
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
    if years_mod.size <3:
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
    elif (TimeSeries(years,values,None,None).integrate().values[-1]) < 1e12:#equivalent of 1 ci
        years_mod = years
        values_mod = values


    #normalize Values
    maxval = np.max(values_mod)
    values_mod = values_mod/maxval
    o_timeseries = TimeSeries(years,values/maxval,None,None)
    o_mass = o_timeseries.integrate()
    timeseries = TimeSeries(years_mod, values_mod, None, None)
    #Commented out 20190619, logging not defined when called directly
    if timeseries.are_all_zero():
    #    logging.info("Skipped - all zero")
        return years, values,0,0

    mx = np.argmax(timeseries.values)
    points = [0, mx, len(timeseries)]
    x = timeseries.times

    mass = timeseries.integrate()
    area = 100*np.mean(timeseries.values)*(x[-1]-x[0])
    ythresh = 100*np.mean(timeseries.values)
    out_error = 1
    out_error_last = out_error
    OUT_ERROR_THRESHOLD = 1e-2
    UPPER_N = 100
    LOWER_N = 50
    last_result = None
    MAX_ITERATIONS = 80

    solve_type = SMOOTH
    simple_peaks = False

    for ix in range(MAX_ITERATIONS):
        res = red_flux.reduce_flux(timeseries, area, ythresh,
                solve_type=solve_type,
                simple_peaks=simple_peaks
                )

        out_error = abs(res.relative_total_mass_error)

        if len(res.reduced_flux) > 2*UPPER_N:
            simple_peaks = True
            solve_type = RAW
        elif out_error < OUT_ERROR_THRESHOLD and len(res.reduced_flux)>=LOWER_N:
            last_result = res
            break

        #if simple_peaks and len(res.reduced_flux) > 2*UPPER_N:
        #    print("data reduction getting to many points")
        #    last_result = res
        #    break
        ythresh = 0.5*ythresh
        area = 0.5*area
        out_error_last = out_error
        last_result = res

    if ix>=MAX_ITERATIONS - 1:
        print("MAX ITERATIONS")
    #Commented out 20190619, logging not defined when called directly
    #    logging.info("MAX ITERATIONS")

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
