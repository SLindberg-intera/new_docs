import numpy as np
import scipy.signal as sig
from scipy.interpolate import UnivariateSpline as uvs
import math
import pylib.hssmbuilder.timeseries.timeseries_math as tsmath
import pylib.hssmbuilder.datareduction.recursive_contour as redcon
from pylib.hssmbuilder.datareduction.reduction_result import ReductionResult
from pylib.hssmbuilder.timeseries.timeseries import TimeSeries
SMOOTH = "SMOOTH"
RAW = "RAW"


def reduce_timeseries(timeseries, threshold_area, threshold_peak, mass,
        solve_type=RAW, simple_peaks=False):
    x = timeseries.times
    y = timeseries.values
    peaks, _ = sig.find_peaks(y)
    peaks = x[peaks]
    pneg, _ = sig.find_peaks(-y)
    pneg = x[pneg]
    peak_width = 1
    while peaks.size >10:
        peak_width += 1
        peaks, _ = sig.find_peaks(y,width=peak_width,rel_height=1)
        peaks = x[peaks]
        pneg, _ = sig.find_peaks(-y,width=peak_width,rel_height=1)
        pneg = x[pneg]

    required_slope = x[np.divide(np.abs(np.diff(y,prepend=0)),y,
            where=(y>0.05*np.max(y)))>0.20]

    required_slope = [i-1 for i in required_slope]

    if simple_peaks:
        peaks = np.array([x[np.argmax(timeseries.values)]])
        pneg = []
        required_slope = np.array([])

    if solve_type == SMOOTH:
        ts_smooth = tsmath.smooth(timeseries)
        y = ts_smooth.values
    r = redcon.reducer((x,y),
            threshold_area=threshold_area,
            threshold_peak=threshold_peak,
    )

    flat_reduced_x = set(redcon.flatten_reduced(r))

    required = {x[0],x[-1]}

    xout = sorted(list(flat_reduced_x.union(required)\
            .union(peaks).union(pneg).union(required_slope)
           ))
    reduced_flux = timeseries.subset(xout)
    reduced_mass = tsmath.integrate(reduced_flux)

    return reduced_flux, reduced_mass
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
                min_val = min(y[s_ind:e_ind])
                v_ind = np.where(pneg==min_val)
                #v_ind = np.where((pneg > s_ind) & (pneg < e_ind))
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
            p_error = error / total_mass
            flux_diff = p_mass * p_error
            #get find equivalent percentage of total_error
            #e_mass = error * p_mass
            #divide reduced total error by total mass of segment
            #flux_diff = e_mass / mass
            # if dif is greater than 10% reduce it to 10%
            if abs(flux_diff) > .1:
                flux_diff=abs(flux_diff)/flux_diff*0.1
            #    if flux_diff >0:
            #        flux_diff = .1
            #    else:
            #        flux_diff = -.1

            #if abs(flux_diff) < 0.001:
            #    flux_diff = abs(flux_diff)/flux_diff *0.001

            adjusted[x[0]] = y[0]
            max_flux = max(y)

            #for each value (except first and last values) adjust value by percent (flux_diff)
            for i in range(1,x.size-1):

                new_val = y[i]+(y[i] * flux_diff)
                if new_val > max_flux:
                    new_val = y[i] + ((max_flux - y[i]) * .1)
                #should not happen but just in case negative numbers not allowed
                if new_val < 0:
                    new_val = float(0.0)
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
def rebalance(reduction_result):
    """
        return a new ReductionResult
        flux, mass such that the total mass difference is 0
    """
    rr = reduction_result
    #minvalue = np.min(rr.reduced_flux.values)*.0001
    deltaM = rr.total_mass_error
    vals = rr.reduced_flux.values
    times = rr.reduced_flux.times
    # equal application
    dt = times[-1]-times[0]
    vals += deltaM/dt

    adjusted = rr.reduced_flux.from_values(
            values =vals)
    reduced_mass = tsmath.integrate(adjusted)
    rr = ReductionResult(
        flux=rr.flux,
        mass=rr.mass,
        reduced_flux=adjusted,
        reduced_mass=reduced_mass)
    return rr

def reduce_flux(flux, threshold_area, threshold_peak, solve_type,
        simple_peaks):
    mass = tsmath.integrate(flux)
    reduced_flux, reduced_mass = reduce_timeseries(
            flux, threshold_area, threshold_peak,
            mass, solve_type, simple_peaks)

    result = ReductionResult(
            flux=flux,
            mass=mass,
            reduced_flux=reduced_flux,
            reduced_mass=reduced_mass)
    return result
def insert_point(times, values,time,value):
    times = np.append(times,time)
    times.sort(kind='mergesort')
    ind = np.where(times == time)[0][0]
    values2 = np.insert(values,ind,value)

    return times, values2
#-------------------------------------------------------------------------------
# add extra points in areas of greatest error until you run out of points or
#  you reach less than .01% relative error.
def rebalance_extra_points(reduction_result,num_points=10):
    #----------------------
    #
    def find_mean_dif_day():
        diff = rr.diff_mass
        #m_diff = max(abs(diff.values))
        m_diff = np.mean(abs(diff.values))
        if m_diff > 0:
            #ind = np.flatnonzero(abs(diff.values) == m_diff)[0]
            ind = np.flatnonzero(abs(diff.values) >= m_diff)[0]
            return diff.times[ind]
        return -1
    #--------------------
    #
    def check_zero_fluxes():
        points = num_points
        times = rr.reduced_flux.times
        vals = rr.reduced_flux.values
        zero_inds = np.flatnonzero(rr.flux.values == 0)
        series = []
        result = [series]
        expect = None
        step = 1
        #loop through indexes and find consecutive zeros
        for v in zero_inds:
            if (v == expect) or (expect is None):
                series.append(v)
            else:
                run = [v]
                result.append(series)
            expect = v + step
        #

        for r in result:
            #leave a few points for adding in strategice points.
            if points <= 10:
                break
            if len(r) > 5:
                times,vals = insert_point(times, vals,rr.flux.times[r[0]],rr.flux.values[r[0]])
                times,vals = insert_point(times, vals,rr.flux.times[r[-1]],rr.flux.values[r[-1]])
                points -= 2
        return points,times,vals

    rr = reduction_result
    points,times,vals = check_zero_fluxes()
    adjusted = TimeSeries(times,vals,None,None)
    reduced_mass = tsmath.integrate(adjusted)
    rr = ReductionResult(
        flux=rr.flux,
        mass=rr.mass,
        reduced_flux=adjusted,
        reduced_mass=reduced_mass)
    #loop through and add mid points at strategic places.
    for x in range(points):
        diff_day = find_mean_dif_day()
        #if diff_day == -1, then max_diff was 0, which means there is nothing to
        # correct.
        if diff_day == -1:
            return rr
        times = rr.reduced_flux.times
        vals = rr.reduced_flux.values
        start_ind = np.flatnonzero(times < diff_day)[-1]
        end_ind = np.flatnonzero(times >= diff_day)[0]
        mid_day = 0
        #zero_inds = np.flatnonzero(vals[start_ind:end_ind] == 0)
        #if zero_inds.size > 0:
        #    mid_point = zero_inds[-1]
        #    mid_day = times[mid_point]
        #else:
        start_day = times[start_ind]
        end_day = times[end_ind]
        mid_day = ((end_day-start_day )/2)+start_day
        mid_point =  np.flatnonzero(rr.flux.times >= mid_day)[0]
        if not mid_day in times:
            times,vals = insert_point(times, vals,rr.flux.times[mid_point],rr.flux.values[mid_point])
        adjusted = TimeSeries(times,vals,None,None)
        reduced_mass = tsmath.integrate(adjusted)
        rr = ReductionResult(
            flux=rr.flux,
            mass=rr.mass,
            reduced_flux=adjusted,
            reduced_mass=reduced_mass)

        if abs(rr.total_mass_error/rr.mass.values[-1])*100 < .001:
            break
    return rr
