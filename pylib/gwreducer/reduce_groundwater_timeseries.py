"""
    use data reduction method on groundwater timeseries

"""
import numpy as np
from pylib.timeseries.timeseries import TimeSeries
from pylib.gwreducer import reduce_flux as red_flux
from pylib.datareduction.reduction_result import ReductionResult
##test
from pylib.datareduction import rdp as rdp
#from pylib.gwreducer import rdp as rdp
import pylib.timeseries.timeseries_math as tsmath
##
SMOOTH = 'SMOOTH'
RAW = 'RAW'
import scipy.signal as sig
#-------------------------------------------------------------------------------
# iterate through reduction algorithms
def reduct_iter(timeseries,flux_floor,ythresh,out_error,out_error_last,OUT_ERROR_THRESHOLD,UPPER_N,LOWER_N,last_result,MAX_ITERATIONS, algo="iter"):
    out_error_last = out_error
    prev_point_count = 0
    good_result=last_result
    mass = timeseries.integrate()
    epsilon = ythresh
    mult_by = .5
    #upper_epsilon = ythresh
    #lower_epsilon = flux_floor
    for ix in range(MAX_ITERATIONS):
        #execute Ramer–Douglas–Peucker_algorithm
        temp = rdp.rdp(np.stack((timeseries.times,timeseries.values), axis=-1), epsilon=epsilon,algo=algo)
        #find the relative error
        reduced_flux = TimeSeries(temp[:, 0],temp[:, 1],None,None)
        reduced_mass = tsmath.integrate(reduced_flux)
        res = ReductionResult(
                flux=timeseries,
                mass=mass,
                reduced_flux=reduced_flux,
                reduced_mass=reduced_mass)

        out_error = abs(res.relative_total_mass_error)
        # if relative error below error threshold record result
        if out_error < OUT_ERROR_THRESHOLD:
            #if num of points greater than the lower point bound then we are done
            # exit loop
            if res.reduced_flux.times.size >= LOWER_N:
                last_result = res
                break
            #if num of points is smaller than the lower point bound but has more
            # points than previously found tries then keep this as a potential
            # good data set.
            elif res.reduced_flux.times.size > prev_point_count:
                prev_point_count = res.reduced_flux.times.size
                good_result = res
        #reduce epsilon to increase number of points found
        if epsilon * mult_by > flux_floor:
            epsilon = epsilon * mult_by
        else:
            #previous reduction was not good, try reducing epsilon slower
            mult_by = mult_by * .5
            epsilon = ythresh
            if epsilon * mult_by > flux_floor:
                epsilon = epsilon * mult_by
            else:
                break
        #test upper lower bounds for epsilon
        #find the best epsilon by defining upper and lower bounds.
        #  if the number of points exceeds the Upper bound of points then set it
        #    as a lower bound
        #  if
        #if res.reduced_flux.times.size > UPPER_N:
        #    lower_epsilon = epsilon
        #    epsilon = (epsilon + upper_epsilon)*.5
        #    if lower_epsilon > epsilon:
        #        epsilon = ((upper_epsilon-lower_epsilon)*.5)+lower_epsilon
        #else:
        #    upper_epsilon = epsilon
        #    epsilon = (epsilon + lower_epsilon)*.5
        #    if upper_epsilon > epsilon:
        #        epsilon = ((upper_epsilon-lower_epsilon)*.5)+lower_epsilon
        #end test
#        out_error_last = out_error
        last_result = res
    if prev_point_count > 0:
        if last_result.reduced_flux.times.size > UPPER_N or out_error_last > OUT_ERROR_THRESHOLD:
            if good_result.reduced_flux.times.size < UPPER_N:
                last_result = good_result
    #if rdp == "iter":
        #if the timeseries has an error > Threshold or was not reduced by atleast 50% then try Kevins
        # algorithm
    #    if out_error > OUT_ERROR_THRESHOLD or len(res.reduced_flux) > timeseries.times.size/2:
    #        res,ix2 = reduct_iter(timeseries,area,ythresh,out_error,out_error_last,OUT_ERROR_THRESHOLD,UPPER_N,LOWER_N,last_result,MAX_ITERATIONS, "rec")
    #        out_error2 = abs(res.relative_total_mass_error)
    #        if (out_error2 < OUT_ERROR_THRESHOLD or out_error2 < out_error) and reduced_flux.size < last_result.size:
    #            last_result = res
    #            ix += ix2
    #if ix>=MAX_ITERATIONS - 1:
    #    print("MAX ITERATIONS")
    return last_result,ix
#-------------------------------------------------------------------------------
#
def remove_begin_end_zero_flux(days,vals,flux_floor,min_reduction_steps):
    non_zero_ind = np.where(vals > 0)[0]
    pre_data = 0
    post_data = 0
    if (non_zero_ind[-1] - non_zero_ind[0]) > min_reduction_steps:
        non_zero_ind = np.where(vals > flux_floor)[0]
    if non_zero_ind[0] > 0:
        pre_data = non_zero_ind[0] - 1
    if non_zero_ind[-1] < len(days)-1:
        post_data = non_zero_ind[-1] + 1
    non_zero_ind = np.array([days[0],pre_data,days[non_zero_ind[0]],days[non_zero_ind[-1]],post_data,days[0]])
    return non_zero_ind
def set_flux_below_floor(vals,flux_floor):
    vals[vals < flux_floor] = 0
    return vals
#-------------------------------------------------------------------------------
#
def remove_zero_flux(days,vals,flux_floor,min_reduction_steps):
    last_ind = vals.size-1
    #check if allowing any steps greater than 0 is still below min_reduction_steps
    non_zero_ind = np.where(vals > 0)[0]
    if non_zero_ind.size > min_reduction_steps:
        non_zero_ind = np.where(vals > flux_floor)[0]
    #add first zero after data decreases to zero
    if non_zero_ind.size == 0:
        return np.where(vals <= flux_floor)[0]
    if non_zero_ind[-1]+1 < last_ind and non_zero_ind[-1]+1 not in non_zero_ind:
        ind = non_zero_ind[-1]+1
        non_zero_ind = np.append(non_zero_ind,[ind])
        low_val = vals[ind]
        #zero_ind = ind
        #if low_val is not 0 then find then next zero
        if vals[ind] != 0:
            for i in range(ind,vals.size):
                if vals[i] == 0:
                    ind = i
                    break
                elif vals[i] < low_val:
                    low_val = vals[i]
                    ind = i
            if ind not in non_zero_ind:
                non_zero_ind = np.append(non_zero_ind,[ind])
    #add last zero before flux increases above zero
    if non_zero_ind[0]-1 > 0 and non_zero_ind[0]-1 not in non_zero_ind:
        ind = non_zero_ind[0]-1
        non_zero_ind = np.append(non_zero_ind,[ind])
        low_val = vals[ind]
        #if low_val is not 0 then find the previous zero
        if low_val != 0:
            for i in range(ind, 0,-1):
                if vals[i] == 0:
                    ind = i
                    break
                elif vals[i] < low_val:
                    low_val = vals[i]
                    ind = i
        if ind not in non_zero_ind:
            non_zero_ind = np.append(non_zero_ind,[ind])
    if 0 not in non_zero_ind:
        non_zero_ind = np.append(non_zero_ind,[0])
    if (vals.size -1) not in non_zero_ind:
        non_zero_ind = np.append(non_zero_ind,[(vals.size -1)])
    non_zero_ind = np.sort(non_zero_ind)
    return non_zero_ind
def reduce_dataset(years, values,flux_floor=0,max_tm_error=0):
    """ takes  times and values and then reduces it

    returns reduced_times and reduced_values

    if all elements are zero, it returns False

    flux_floor > flux == 0
    max_tm_error > total mass error
    """

    #  anything less than Flux floor is considered to be zero
    #  we are removing anything under flux floor to help remove jidder
    #non_zero_ind = np.where(values > flux_floor)[0]
    #non_zero_start_ind = non_zero_ind[0]
    #non_zero_end_ind = non_zero_ind[-1]
    #non_zero_start_day = years[non_zero_start_ind]
    #non_zero_end_day = years[non_zero_end_ind]
    #add last zero before flux increases above zero
    #if non_zero_end_ind+1 < values.size-1 and non_zero_end_ind+1 not in non_zero_ind:
    #    ind = non_zero_ind[-1]+1
    #    non_zero_ind = np.append(non_zero_ind,[ind])
    #    low_val = values[ind]
    #    #if low_val is not 0 then find then next zero
    #    if low_val != 0:
    #        for i in range(ind,values.size):
    #            if values[i] == 0:
    #                ind = i
    #                break
    #            elif values[i] < low_val:
    #                low_val = values[i]
    #                ind = i
    #        if ind not in non_zero_ind:
    #            non_zero_ind = np.append(non_zero_ind,[ind])
    #    non_zero_ind = np.sort(non_zero_ind)
    #add last zero before flux increases above zero
    #if non_zero_start_ind-1 > 0 and non_zero_start_ind-1 not in non_zero_ind:
    #    ind = non_zero_start_ind-1
    #    non_zero_ind = np.append(non_zero_ind,[ind])
    #    low_val = values[ind]
    #    #if low_val is not 0 then find the previous zero
    #    if low_val >= flux_floor:
    #        for i in range(ind, 0,-1):
    #            if values[i] == 0:
    #                ind = i
    #                break
    #            elif values[i] < low_val:
    #                low_val = values[i]
    #                ind = i
    #        if ind not in non_zero_ind:
    #            non_zero_ind = np.append(non_zero_ind,[ind])
    #    non_zero_ind = np.sort(non_zero_ind)
    #if non_zero_start_ind-1 > 0:
    #    non_zero_ind = np.append(non_zero_ind,non_zero_start_ind-1)
    #    non_zero_ind = np.sort(non_zero_ind)

    #add first zero after data decreases to zero
    #if non_zero_end_ind+1 < values.size-1:
    #    non_zero_ind = np.append(non_zero_ind,non_zero_end_ind+1)
    #    non_zero_ind = np.sort(non_zero_ind)
    #non_zero_ind = np.sort(non_zero_ind)
    #if 0 not in non_zero_ind:
    #    non_zero_ind = np.append(non_zero_ind,[0])
    #    non_zero_ind = np.sort(non_zero_ind)
    #if (values.size -1) not in non_zero_ind:
    #    non_zero_ind = np.append(non_zero_ind,[(values.size -1)])
    #non_zero_ind = np.sort(non_zero_ind)

    #test
    #non_zero_ind = remove_zero_flux(years,values,flux_floor,500)
    remove_begin_end_zero_flux(days,vals,flux_floor,min_reduction_steps)
    #end test
    years_mod = years[non_zero_ind]
    values_mod = values[non_zero_ind]
    #test
    values_mod = set_flux_below_floor(values_mod,flux_floor)
    #end_test
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
    #if total mass is less than the max to mass error then use all data
    elif (TimeSeries(years,values,None,None).integrate().values[-1]) < max_tm_error:#1e12:#equivalent of 1 ci
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
    #area = 100*np.mean(timeseries.values)*(x[-1]-x[0])
    ythresh = 100*np.mean(timeseries.values)
    out_error = 1
    out_error_last = out_error
    OUT_ERROR_THRESHOLD = 1e-2
    #UPPER_N = 100
    UPPER_N = 200
    LOWER_N = 50
    last_result = None
    MAX_ITERATIONS = 80

    solve_type = SMOOTH
    simple_peaks = False
    last_result,ix = reduct_iter(timeseries,flux_floor,ythresh,out_error,out_error_last,OUT_ERROR_THRESHOLD,UPPER_N,LOWER_N,last_result,MAX_ITERATIONS)
    #Add the point prior to first (flux > 0), add point after last of (flux >0)
    last_result = add_zero_markers(o_timeseries,last_result.reduced_flux,flux_floor)

    #for ix in range(MAX_ITERATIONS):
        #res = red_flux.reduce_flux(timeseries, area, ythresh,
        #        solve_type=solve_type,
        #        simple_peaks=simple_peaks
        #        )
        #test
    #    temp = rdp.rdp(np.stack((timeseries.times,timeseries.values), axis=-1), epsilon=ythresh)

    #    reduced_flux = TimeSeries(temp[:, 0],temp[:, 1],None,None)
    #    reduced_mass = tsmath.integrate(reduced_flux)
    #    res = ReductionResult(
    #            flux=timeseries,
    #            mass=mass,
    #            reduced_flux=reduced_flux,
    #            reduced_mass=reduced_mass)
        #end test
    #    out_error = abs(res.relative_total_mass_error)

    #    if len(res.reduced_flux) > 2*UPPER_N:
    #        simple_peaks = True
    #        solve_type = RAW
    #    elif out_error < OUT_ERROR_THRESHOLD and len(res.reduced_flux)>=LOWER_N:
    #        last_result = res
    #        break

        #if simple_peaks and len(res.reduced_flux) > 2*UPPER_N:
        #    print("data reduction getting to many points")
        #    last_result = res
        #    break
    #    ythresh = 0.5*ythresh
    #    area = 0.5*area
    #    out_error_last = out_error
    #    last_result = res
    #if ix>=MAX_ITERATIONS - 1:
    #    print("MAX ITERATIONS")

    #Commented out 20190619, logging not defined when called directly
    #    logging.info("MAX ITERATIONS")




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
    pneg = np.where(pneg)

    peaks = peaks[0]
    pneg = pneg[0]
    iter = 0
    while abs(last_result.total_mass_error*maxval) > flux_floor*365.25 and iter < 100:
        rr = red_flux.rebalance_valleys(rr,peaks,pneg)
        #keep the lowest total_mass_error
        if abs(rr.total_mass_error) < abs(last_result.total_mass_error):
            last_result = rr
        iter += 1

    out_times = last_result.reduced_flux.times
    out_values = last_result.reduced_flux.values
    #return the reduced data, undo normalize of the values (*maxval)
    return out_times, out_values*maxval,-(last_result.total_mass_error * maxval),peaks.size,ix
#-------------------------------------------------------------------------------
#
def add_zero_markers(o_ts,r_ts,flux_floor):
    new_ts = r_ts
    r_times = r_ts.times
    r_values = r_ts.values
    num_steps = o_ts.times.size
    if(o_ts.values[0] <= 0):
        zero_ind = np.where(o_ts.values > 0)[0][0]-1
        if not np.any(r_times == o_ts.times[zero_ind]):
            r_times,r_values = insert_point(r_times,r_values,o_ts.times[zero_ind],o_ts.values[zero_ind])
            #new_ts = TimeSeries(r_times,r_values,None,None)
    if o_ts.times[0] != r_times[0]:
        r_times,r_values = insert_point(r_times,r_values,o_ts.times[0],o_ts.values[0])
        #new_ts = TimeSeries(r_times,r_values,None,None)
    zero_ind = 0
    if(o_ts.values[-1] <= 0):
        zero_ind = np.where(o_ts.values > 0)[0][-1]+1
        if zero_ind < num_steps and not np.any(r_times == o_ts.times[zero_ind]):
            r_times,r_values = insert_point(r_times,r_values,o_ts.times[zero_ind],o_ts.values[zero_ind])
            #new_ts = TimeSeries(r_times,r_values,None,None)
    if o_ts.times[-1] != r_times[-1]:
        r_times,r_values = insert_point(r_times,r_values,o_ts.times[-1],o_ts.values[-1])
        #new_ts = TimeSeries(r_times,r_values,None,None)
    new_ts = TimeSeries(r_times,r_values,None,None)

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
