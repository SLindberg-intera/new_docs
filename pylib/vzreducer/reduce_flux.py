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
    peaks, _ = sig.find_peaks(y)

    peaks = x[peaks]
    pneg, _ = sig.find_peaks(-y)
    pneg = x[pneg]
    required_slope = x[np.divide(np.abs(np.diff(y,prepend=0)),y,
            where=(y>0.05*np.max(y)))>0.20]

    zero_flux = np.argwhere(np.diff(y,prepend=0)==0)

    required_slope_lower = [i-1 for i in required_slope if i != x[0]]
    required_slope_upper = [i+1 for i in required_slope if i != x[-1]]
    required_slope = sorted([*{*[*required_slope, *required_slope_upper, *required_slope_lower]}])

    deriv_y = tsmath.diff(timeseries)
    required_first_deriv =  np.argwhere(np.diff(deriv_y.values,prepend=0) > 0.001).tolist()
    #required_first_deriv = x[[item for sublist in required_first_deriv for item in sublist]]
    required_first_deriv =x[[53,54,55,56,57]]
    if simple_peaks:
        peaks = [x[np.argmax(timeseries.values)]]
        pneg = []
        # this is never used....above is required_slope (singular and not plural...)
        # threw off reduction for T31 and T34 (C-14 for sure) if required slope is cleared though...
        required_slopes = []


    if solve_type == SMOOTH:
        ts_smooth = tsmath.smooth(timeseries)
        y = ts_smooth.values


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
    required = {x[0],x[-1]}

    try:
        #xout = sorted(list(flat_reduced_x.union(required)\
        #        .union(peaks).union(pneg).union(required_slope)
        #       ))
        xout = sorted(set([*flat_reduced_x,*required,*peaks,*pneg,*required_slope,*required_first_deriv]))
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
    
