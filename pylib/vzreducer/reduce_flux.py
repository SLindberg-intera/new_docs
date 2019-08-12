import numpy as np
import scipy.signal as sig
import pylib.timeseries.timeseries_math as tsmath
import pylib.datareduction.recursive_contour as redcon  
from pylib.datareduction.reduction_result import ReductionResult

from pylib.timeseries.timeseries import TimeSeries

import math

SMOOTH = "SMOOTH"
RAW = "RAW"

def reduce_timeseries(timeseries, threshold_area, threshold_peak, mass,
        solve_type=RAW, simple_peaks=False):
    x = timeseries.times
    y = timeseries.values

    #zero_flux = np.argwhere(y==0)
    #if np.all(y[zero_flux[1][0]:]==0):
    #    timeseries.times =timeseries.times[:zero_flux[1][0]]
    #    timeseries.values = timeseries.values[:zero_flux[1][0]]
    #    x = timeseries.times
    #    y = timeseries.values
    #    x_zeros = x[zero_flux[1][0]+1:]
    #    y_zeros = y[zero_flux[1][0]+1:]

    #x = timeseries.times
    #y = timeseries.values

    peaks, _ = sig.find_peaks(y)

    peaks = x[peaks]
    pneg, _ = sig.find_peaks(-y)
    pneg = x[pneg]

    required = {x[0], x[-1]}

    required_slope = x[np.divide(np.abs(np.diff(y,prepend=0)),y,
            where=(y>0.05*np.max(y)))>0.2]



    required_slope_lower = [i-1 for i in required_slope if i != x[0]]
    required_slope_upper = [i+1 for i in required_slope if i != x[-1]]
    required_slope = sorted([*{*[*required_slope, *required_slope_upper, *required_slope_lower]}])

    deriv_y = tsmath.diff(timeseries)
    required_first_deriv_up =  np.argwhere( (abs(deriv_y.values[0:-1]/deriv_y.values[1:] ) != float("Inf")) & (abs(deriv_y.values[0:-1]/deriv_y.values[1:] ) >1.1 )).tolist()
    required_first_deriv_down = np.argwhere( (abs(deriv_y.values[0:-1]/deriv_y.values[1:] ) != float("Inf"))  &(abs(deriv_y.values[0:-1]/deriv_y.values[1:] ) != 0) & (abs(deriv_y.values[0:-1]/deriv_y.values[1:] ) < 0.9)).tolist()
    deriv_3 = x[[item for sublist in required_first_deriv_up for item in sublist if item <1000 and y[item]> 0.005*np.max(y)]]
    deriv_4 = x[[item for sublist in required_first_deriv_down for item in sublist if item <1000 and y[item]> 0.005* np.max(y)]]
    deriv_1 = x[[item + 1 for sublist in required_first_deriv_down for item in sublist if item < 1000 ]]
    deriv_2= x[[item + 1 for sublist in required_first_deriv_up for item in sublist if item < 1000 ]]
    deriv_5 = x[[item-1 for sublist in required_first_deriv_down for item in sublist if item<1000 and item!=0]]
    deriv_6 = x[[item-1 for sublist in required_first_deriv_up for item in sublist if item<1000 and item!=0]]
    required_first_deriv =[*deriv_1,*deriv_2,*deriv_3,*deriv_4,*deriv_5,*deriv_6]
    #required_first_deriv =x[[52,53,54,55,56]]
    #required_hard_coded = x[[i for i in range(1000,10000,3500)]]
    if simple_peaks:
        peaks = [x[np.argmax(timeseries.values)]]
        pneg = []
        # this is never used....above is required_slope (singular and not plural...)
        # threw off reduction for T31 and T34 (C-14 for sure) if required slope is cleared though...
        required_slopes = []


    if solve_type == SMOOTH:
        ts_smooth = tsmath.smooth(timeseries)
        y = ts_smooth.values

    #zero_flux = np.argwhere(y == 0)
    #if np.all(y[zero_flux[1][0]:] == 0):
    #    x = x[:zero_flux[1][0]]
    #    y = y[:zero_flux[1][0]]

    r = redcon.reducer((x,y), 
            threshold_area=threshold_area,
            threshold_peak=threshold_peak,
    )

    try:
        flat_reduced_x = set(redcon.flatten_reduced(r))
    except Exception:
        input("exception thrown at flat_reduced_x")
        input(flat_reduced_x)
        print(Exception)
    #required = {x[0],x[-1]}

    try:
        #xout = sorted(list(flat_reduced_x.union(required)\
        #        .union(peaks).union(pneg).union(required_slope)
        #       ))
        xout = sorted(set([*flat_reduced_x,*required,*peaks,*pneg,*required_slope,*required_first_deriv]))
        #xout = sorted(set([*flat_reduced_x, *required, *peaks, *pneg, *required_slope, *required_hard_coded]))
        #xout = sorted(set([*flat_reduced_x, *required, *peaks, *pneg, *required_slope]))
    except Exception:
        input(flat_reduced_x)
        input("exception thrown at xout")

        input(r)


        print(Exception)
    reduced_flux = timeseries.subset(xout)
    reduced_mass = tsmath.integrate(reduced_flux)

    return reduced_flux, reduced_mass

def rebalance(reduction_result):
    """
        return a new ReductionResult 
        flux, mass such that the total mass difference is 0
    """
    rr = reduction_result
    deltaM = rr.total_mass_error
    vals = rr.reduced_flux.values
    times = rr.reduced_flux.times
    # equal application
    dt = times[-1]-times[0]
    vals += deltaM/dt 

    adjusted = rr.reduced_flux.from_values(
            values =vals)
    reduced_mass = tsmath.integrate(adjusted)
    return ReductionResult(
            flux=rr.flux,
            mass=rr.mass,
            reduced_flux=adjusted,
            reduced_mass=reduced_mass)


def reduce_flux(flux, threshold_area, threshold_peak, solve_type,
        simple_peaks):
    mass = tsmath.integrate(flux)
    # note: don't think that mass is ever used in the called function reduce_timeseries ....
    reduced_flux, reduced_mass = reduce_timeseries(
            flux, threshold_area, threshold_peak,
            mass, solve_type, simple_peaks)
    
    result = ReductionResult(
            flux=flux,
            mass=mass,
            reduced_flux=reduced_flux,
            reduced_mass=reduced_mass)
    return result
    
#-------------------------------------------------------------------------------
#calculate mass between two points, then find the point that contains half the mass
def find_inflection(x,y,s_ind,e_ind):
    #Calculate mass
    ts1 = TimeSeries(x[s_ind:e_ind],y[s_ind:e_ind],None,None)
    mass = ts1.integrate().values[-1]
    half_mass = mass/2
    #build loop criteria process from peak to valley
    #if value at s_ind is < than value at e_ind then e_ind is the peak.
    # therefore process in reverse
    loop = range(e_ind,s_ind,-1)
    reverse = True
    #start_ind = s_ind
    #last_ind = e_ind
    #if value at s_ind is > than value at e_ind then s_ind is the peak.
    #therefor process in sequence
    if y[s_ind] > y[e_ind]:
        loop = range(s_ind,e_ind)
        reverse = False
    #starting at peak find the total mass between valley and i. stop when <= half_mass
    for i in loop:
        #s_ind is the peak
        start = s_ind
        end = i
        #s_ind is the valley
        if reverse == False:
            start = i
            end = e_ind
        #calculate mass
        ts2 = TimeSeries(x[start:end],y[start:end],None,None)
        mass = ts2.integrate().values[-1]
        #check if mass <= half mass
        if mass <= half_mass:
            return i
    #should never get to here.
    if reverse:
        return e_ind
    else:
        return s_ind

#-------------------------------------------------------------------------------
#- define start and end points for valley segments
def get_inflection_points(flux,peaks,pneg,p_area):
    x = flux.times
    y = flux.values

    # add ending point of data.
    last_val = y.size-1
    # ignore trailing zeros
    if y[last_val] == 0:
        last_val = np.where(y > 0)[0][-1]+1

    #add first and last points from flux to the peaks if they dont already exist
    peaks = np.unique(np.concatenate((np.array([0,last_val]),peaks)))
    peaks.sort(kind='mergesort')

    inflection_pts = []
    #set starting point
    start_val = 0
    #ignore leading zeros
    if y[start_val] == 0:
        start_val = np.where(y > 0)[0][0]-1
    s_ind = start_val

    if peaks.size == 2:
        start_ind = s_ind
        end_ind = last_val #
        if y[start_ind] > y[end_ind]:
            start_ind = find_inflection(x,y,start_ind,end_ind)
        else:
            end_ind = find_inflection(x,y,start_ind,end_ind)
        inflection_pts.append([start_ind,end_ind])
    else:
        for index in range(1,peaks.size):
            e_ind = peaks[index]
            if e_ind > s_ind and (e_ind - s_ind) > 0 and e_ind <= last_val: #skip time step 0 as that will always be a starting point
                #find the deepest part of the valley
                v_ind = np.where((pneg > s_ind) & (pneg < e_ind))
                v_ind = v_ind[0]
                if v_ind.size == 1:
                    v_ind = v_ind[0]
                elif v_ind.size > 1:
                    print("*****ERROR in rebalance_valleys function.  found multiple valleys between begin and peak*****")
                else:
                    #if there is no valley point set v_ind to s_ind
                    v_ind = s_ind

                #default values half way point between start and valley, valley and end
                start_ind = math.floor((v_ind - s_ind)*p_area) + s_ind
                end_ind = math.floor((e_ind - v_ind)*p_area) + v_ind
                #if valley exists find inflection point between between start and valley.
                if v_ind > s_ind:
                    start_ind = find_inflection(x,y,s_ind,v_ind)
                #find inflection point between valley and end
                end_ind = find_inflection(x,y,v_ind,e_ind)
                #if this is the first segment find inflection point between first_val and peak
                if s_ind == start_val:
                    end_ind = find_inflection(x,y,s_ind,e_ind)
                    start_ind = s_ind
                #if this is the last segment find the inflectin point between peak and last val
                elif e_ind == last_val:
                    start_ind = find_inflection(x,y,s_ind,e_ind)
                    end_ind = e_ind
                #append inflection point set
                inflection_pts.append([start_ind,end_ind])
            #set s_ind to current end point.
            s_ind = e_ind
    return inflection_pts
#-------------------------------------------------------------------------------
#adjusts fluxes to reduce total mass error.
def adjust_flux(data,error):
    total_mass = float(0.0)
    #sum cumulative mass of all segments
    for seg in data:
        if len(seg) > 0:
            ts = TimeSeries(seg.times,seg.values,None,None)
            temp_series = ts.integrate()
            total_mass += temp_series.values[-1]
    adjusted = {}

    #total_error_perc = float(0.0)
    #mass_used = float(0.0)

    #figure precentage to adjust each point by
#    flux_diff = (total_mass+error)/total_mass
    for seg in data:
        #if segment has atleast 3 points (mid points are adjusted)
        if seg.times.size > 2:
            x = seg.times#[1:-1]
            y = seg.values#[1:-1]
            #ts = TimeSeries(x,y,None,None)
            mass = seg.integrate().values[-1]
            #get Percent mass current segment is of the total mass
            p_mass =  mass/ total_mass
            #get find equivalent percentage of total_error
            e_mass = error * p_mass
            #divide reduced total error by time (not including begin and end points (they never change))
            flux_diff = e_mass / mass
            if abs(flux_diff) > .1:
                if flux_diff >0:
                    flux_diff = .1
                else:
                    flux_diff = -.1

            adjusted[x[0]] = y[0]
            #for each value (except first and last values) adjust value by percent (flux_diff)
            for i in range(1,x.size-1):

                new_val = y[i]+(y[i] * flux_diff)
                #should not happen but just in case negative numbers not allowed
                #if new_val < 0:
                #    new_val = float(0.0)
                adjusted[x[i]] = new_val

    return adjusted
#-------------------------------------------------------------------------------
#
def build_segments(rr,peaks,pneg,inflection_area):
    inf_pts = get_inflection_points(rr.flux,peaks,pneg,inflection_area)
    #segments,t_mass = build_segments(inf_pts,rr,peaks,pneg)

    x = rr.flux.times
    y = rr.flux.values
    r_x = rr.reduced_flux.times
    r_y = rr.reduced_flux.values
    segments = []
    segs_total_mass = 0

    for years in inf_pts:
        s_year = x[years[0]]
        e_year = x[years[1]]
        if (e_year-s_year) > 4:
            if not np.any(r_x == x[years[0]]):
                r_x,r_y = insert_point(r_x,r_y,x[years[0]],y[years[0]])
            if not np.any(r_x == x[years[0]+1]):
                r_x,r_y = insert_point(r_x,r_y,x[years[0]+1],y[years[0]+1])
            if not np.any(r_x == x[years[1]]):
                r_x,r_y = insert_point(r_x,r_y,x[years[1]],y[years[1]])
            if not np.any(r_x == x[years[1]-1]):
                r_x,r_y = insert_point(r_x,r_y,x[years[1]-1],y[years[1]-1])
            r_seg = np.where((r_x >= s_year) & (r_x <= e_year))
            seg_x = r_x[r_seg]
            seg_y = r_y[r_seg]

            timeseries = TimeSeries(seg_x,seg_y,None,None)
            segs_total_mass += timeseries.integrate().values[-1]
        #timeseries = TimeSeries(r_x[r_seg],r_y[r_seg],None,None)
        #timeseries = TimeSeries(r_x[r_start:r_end],r_y[r_start:r_end],None,None)
        segments.append(timeseries)
    return segments, segs_total_mass
#-------------------------------------------------------------------------------
# rebalance reduced time series by adjusting valleys to be deeper/shallower without
# affecting the peaks
def rebalance_valleys(reduction_result,peaks,pneg):
    rr = reduction_result

    error = rr.total_mass_error
    x = rr.flux.times
    y = rr.flux.values
    r_x = rr.reduced_flux.times
    r_y = rr.reduced_flux.values

    segments,t_mass = build_segments(rr,peaks,pneg,.5)


    #if abs(error) > t_mass:
    #    print("*Warning: total_mass_error ({}) exceeds valley mass ({}) for error adjustment; increasting inflection points from 50% to 75% of valley area".format(error,t_mass))
    #    segments,t_mass = build_segments(rr,peaks,pneg,.75)
    if abs(error) > t_mass:
        print("*Warning: total_mass_error ({}) exceeds valley mass ({}) for error adjustment; unable to correct mass_error".format(error,t_mass))
        return rr
    adj_dict = adjust_flux(segments,error)

    for i in range(r_x.size):
        year = r_x[i]
        if year in adj_dict.keys():
            r_y[i] = adj_dict[year]

    adjusted = TimeSeries(r_x,r_y,None,None)

    reduced_mass = tsmath.integrate(adjusted)
    rr = ReductionResult(
        flux=rr.flux,
        mass=rr.mass,
        reduced_flux=adjusted,
        reduced_mass=reduced_mass)
    return rr
#-------------------------------------------------------------------------------
#deprecated
#def rebalance(reduction_result):
    """
        return a new ReductionResult
        flux, mass such that the total mass difference is 0
    """
#    rr = reduction_result
#    #minvalue = np.min(rr.reduced_flux.values)*.0001
#    deltaM = rr.total_mass_error
#    vals = rr.reduced_flux.values
#    times = rr.reduced_flux.times3    # equal application
#    dt = times[-1]-times[0]
#    vals += deltaM/dt
#
#    adjusted = rr.reduced_flux.from_values(
#            values =vals)
#    reduced_mass = tsmath.integrate(adjusted)
#    rr = ReductionResult(
#        flux=rr.flux,
#        mass=rr.mass,
#        reduced_flux=adjusted,
#        reduced_mass=reduced_mass)
#    return rr

#-------------------------------------------------------------------------------

def insert_point(times, values,time,value):
    times = np.append(times,time)
    times.sort(kind='mergesort')
    ind = np.where(times == time)[0][0]
    values2 = np.insert(values,ind,value)

    return times, values2