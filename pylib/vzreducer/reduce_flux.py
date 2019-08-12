import numpy as np
import scipy.signal as sig
import pylib.timeseries.timeseries_math as tsmath
import pylib.datareduction.recursive_contour as redcon  
from pylib.datareduction.reduction_result import ReductionResult

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
    required_hard_coded = x[[i for i in range(1000,10000,3500)]]
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
    
