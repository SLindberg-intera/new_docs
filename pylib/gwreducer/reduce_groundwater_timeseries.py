"""
    use data reduction method on groundwater timeseries

"""
import numpy as np
from pylib.timeseries.timeseries import TimeSeries
from pylib.gwreducer import gwreduce_flux as red_flux
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

    mass = timeseries.integrate()
    good_result=ReductionResult(
                flux=timeseries,
                mass=mass,
                reduced_flux=timeseries,
                reduced_mass=mass)
    last_result = ReductionResult(
                flux=timeseries,
                mass=mass,
                reduced_flux=timeseries,
                reduced_mass=mass)
    epsilon = ythresh
    mult_by = .5

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

        last_result = res
    if prev_point_count > 0:
        if last_result.reduced_flux.times.size > UPPER_N or out_error_last > OUT_ERROR_THRESHOLD:
            if good_result.reduced_flux.times.size < UPPER_N:
                last_result = good_result

    return last_result,ix
#-------------------------------------------------------------------------------
#
def remove_begin_end_zero_flux(days,vals,flux_floor,min_reduction_steps):
    non_zero_ind = np.where(vals > 0)[0]
    old_non_zero_ind = np.array([])
    temp = np.array([])
    pre_data = days[1]
    post_data = days[-2]
    if (non_zero_ind.size) > min_reduction_steps:
        old_non_zero_ind = non_zero_ind
        temp = np.where(vals > flux_floor)[0]
    if temp.size > 0:
        non_zero_ind = temp
    if non_zero_ind[0] > 1:
        pre_data = days[non_zero_ind[0] - 1]
    if non_zero_ind[-1] < len(days)-2:
        post_data = days[non_zero_ind[-1] + 1]
    #get add first year, year of last 0 before mass, first 0 after flux, last year
    zero_ind = np.concatenate((np.array([0]),np.where(np.logical_or(days ==pre_data, days==post_data))[0],np.array([days.size -1])))
    if old_non_zero_ind.size > 0:
        pre = old_non_zero_ind[0] if old_non_zero_ind[0] > 1 else 1
        post = old_non_zero_ind[-1] if old_non_zero_ind[0] < len(days)-2 else len(days)-2
        zero_ind = np.concatenate((zero_ind,np.array([pre,post])))
        zero_ind = np.unique(zero_ind)
        zero_ind.sort()
    #get add first year, year of last 0 before mass,all years with mas, first 0 after flux, last year
    non_zero_ind = np.concatenate((np.array([0]),np.where(np.logical_and(days >=pre_data, days<=post_data))[0],np.array([days.size -1])))

    return non_zero_ind,zero_ind
#-------------------------------------------------------------------------------
# take an array of indexes from unreduced data and add them back into the reduced data set.
# array should contain first and last indexes, other points are point before mass,
# before flux floor mass, after mass, after flux floor
def retain_min_years(r_ts,o_ts,o_mass,min_years_ind):

    years = o_ts.times[min_years_ind]
    if r_ts.times[0] != years[0]:
        r_ts.times = np.insert(r_ts.times,0,years[0])
        r_ts.values = np.insert(r_ts.values,0,o_ts.values[min_years_ind[0]])
    if len(years) > 2:
        for ind in range(1,len(years-2)):
            if not np.any(r_ts.times == years[ind]):
                pos = np.where(r_ts.times > years[ind])[0][0]
                if pos < 0:
                    pos = np.where(r_ts.times < years[ind])[0][-1]
                r_ts.times = np.insert(r_ts.times,pos,years[ind])
                r_ts.values = np.insert(r_ts.values,pos,o_ts.values[min_years_ind[ind]])

    if r_ts.times[-1] != years[-1]:
        ind = r_ts.times.size-1
        r_ts.times = np.insert(r_ts.times,ind,years[-1])
        r_ts.values = np.insert(r_ts.values,ind,o_ts.values[min_years_ind[-1]])
    reduced_mass = tsmath.integrate(r_ts)
    return ReductionResult(
            flux=o_ts,
            mass=o_mass,
            reduced_flux=r_ts,
            reduced_mass=reduced_mass)
#-------------------------------------------------------------------------------
# if flux is below flux floor then it is considered noise and effectively 0 so
#  set it to 0.  this fixes some issues with extremely small numbers.
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
def reduce_dataset(years, values,flux_floor=0,max_tm_error=0,min_reduction_steps=200):
    """ takes  times and values and then reduces it

    returns reduced_times and reduced_values

    if all elements are zero, it returns False

    flux_floor > flux == 0
    max_tm_error > total mass error
    """
    non_zero_ind, min_retained_zero_years = remove_begin_end_zero_flux(years,values,flux_floor,min_reduction_steps)

    years_mod = years[non_zero_ind]
    values_mod = values[non_zero_ind]

    if years_mod.size <3:
        years_mod = years
        values_mod = values
        values_mod = 0
    else:
        #makes ure you have not removed more than 1% of the mass when removing 0 or flux floor rates
        o_mass = TimeSeries(years,values,None,None).integrate().values[-1]
        r_mass = TimeSeries(years_mod, values_mod, None, None).integrate().values[-1]
        if abs((o_mass-r_mass)/o_mass)*100 > 1:
            years_mod = years
            values_mod = values
            timeseries = TimeSeries(years_mod, values_mod, None, None)
            mass = timeseries.integrate()

    #normalize Values
    maxval = np.max(values_mod)
    values_mod = values_mod/maxval
    o_timeseries = TimeSeries(years,values/maxval,None,None)
    o_mass = o_timeseries.integrate()
    timeseries = TimeSeries(years_mod, values_mod, None, None)
    mass = timeseries.integrate()

    mx = np.argmax(timeseries.values)
    points = [0, mx, len(timeseries)]
    x = timeseries.times

    ythresh = 100*np.mean(timeseries.values)
    out_error = 1
    out_error_last = out_error
    OUT_ERROR_THRESHOLD = 1e-2

    UPPER_N = 200
    LOWER_N = 50
    last_result = None
    MAX_ITERATIONS = 80

    solve_type = SMOOTH
    simple_peaks = False
    last_result,ix = reduct_iter(timeseries,flux_floor,ythresh,out_error,out_error_last,OUT_ERROR_THRESHOLD,UPPER_N,LOWER_N,last_result,MAX_ITERATIONS)
    last_result = retain_min_years(last_result.reduced_flux,o_timeseries,o_mass,min_retained_zero_years)
    #if there are less points than the min_reduction_steps then use the remaining
    #points to rebalance the segments with the largest mass errors.
    play_points = min_reduction_steps - last_result.num_reduced_points
    bef = last_result.reduced_flux.times.size
    if play_points > 0:
        last_result = red_flux.rebalance_extra_points(last_result,play_points)

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
    while iter < 100 and (abs(last_result.total_mass_error*maxval) > max_tm_error or abs(last_result.total_mass_error/last_result.mass.values[-1])*100 > .001) :
        rr = red_flux.rebalance_valleys(rr,peaks,pneg)
        #keep the lowest total_mass_error
        if abs(rr.total_mass_error) < abs(last_result.total_mass_error):
            last_result = rr
        else:
            break
        iter += 1

    out_times = last_result.reduced_flux.times
    out_values = last_result.reduced_flux.values
    #return the reduced data, undo normalize of the values (*maxval)
    return out_times, out_values*maxval,-(last_result.total_mass_error * maxval),peaks.size,iter
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
