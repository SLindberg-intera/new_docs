import numpy as np
import pylib.timeseries.timeseries_math as tsmath
from pylib.datareduction.reduction_result import ReductionResult
from pylib.datareduction.rdp import rdp

from pylib.timeseries.timeseries import TimeSeries

import math


def reduce_timeseries(timeseries, epsilon, close_gaps, gap_delta, gap_steps):
    x = timeseries.times
    y = timeseries.values

    #reduced dataset includes significant slope deltas (where the (y2-y1)/y2 > 0.2) and y > 0.05*max y
    required_slope = x[np.divide(np.abs(np.diff(y,prepend=0)),y,
        where=(y>0.05*np.max(y)))>0.2]


    #grab timesteps on either side of "required slope" timestep and add to the required slope list
    required_slope_lower = [i-1 for i in required_slope if i != x[0]]
    required_slope_upper = [i+1 for i in required_slope if i != x[-1]]
    required_slope = sorted([*{*[*required_slope, *required_slope_upper, *required_slope_lower]}])

    #normalize the fluxes for the RDP reduction algorithm
    y_normalized = y/np.max(y)
    list_xy = list(zip(x,y_normalized))


    rdp_list = rdp(list_xy, epsilon)
    #parse the returned reduced dataset into timesteps and normalized fluxes (normalized fluxes don't need to be
    #converted back because not used for reduced fluxes [handled by timeseries.subset()]
    rdp_x = [int(pair[0]) for pair in rdp_list]
    rdp_y = [pair[1] for pair in rdp_list]

    #for some datasets which large gaps between timesteps, reduction error is improved by adding add'l timesteps
    #user-defined in JSON config file whether applied or not
    x_gaps = []
    if close_gaps.lower() == "true":
        if np.where(np.diff(rdp_x) > gap_delta):
           for index in (np.where(np.diff(rdp_x) > gap_delta))[0]:
                #check to see if slope between timesteps > 0 and if so fill in gaps with timesteps
                if abs(np.diff(rdp_y)[index])>0:
                    x_gaps += [timestep for timestep in range(rdp_x[index], rdp_x[index+1], int((np.diff(rdp_x)[index])/[(gap_steps+1)]))]

    xout = sorted(set([*required_slope, *rdp_x, *x_gaps]))

    reduced_flux = timeseries.subset(xout)
    reduced_mass = tsmath.integrate(reduced_flux)

    return reduced_flux, reduced_mass


def reduce_flux(flux, epsilon, close_gaps, gap_delta, gap_steps):
    mass = tsmath.integrate(flux)
    reduced_flux, reduced_mass = reduce_timeseries(flux, epsilon, close_gaps, gap_delta, gap_steps)

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
    #this grabs the last leading zero before flux > 0
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
            years = seg.times#[1:-1]
            fluxes = seg.values#[1:-1]
            #ts = TimeSeries(x,y,None,None)
            mass = seg.integrate().values[-1]
            #get Percent mass current segment is of the total mass
            p_mass = mass/total_mass
            #get find equivalent percentage of total_error
            e_mass = error * p_mass
            #divide reduced total error by time (not including begin and end points (they never change))
            flux_diff = e_mass / (years[-1]-years[0]) #mass

            if abs(flux_diff)>0.1:
                flux_diff=abs(flux_diff)/flux_diff*0.1
                 #if flux_diff >0:
                 #   flux_diff = .1
                 #else:
                 #  flux_diff = -.1

            adjusted[years[0]] = fluxes[0]
            max_flux = max(fluxes)


            #for each value (except first and last values) adjust value by percent (flux_diff)
            for i in range(1,years.size-1):
                new_val = fluxes[i] + flux_diff #(fluxes[i] * flux_diff)
                if new_val > max_flux:
                    new_val = fluxes[i] + ((max_flux - fluxes[i]) * .1)

                #new_val = y[i]+(y[i] * flux_diff)
                #should not happen but just in case negative numbers not allowed

                if new_val < 0:
                    new_val = float(0.0)
                adjusted[years[i]] = new_val

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
