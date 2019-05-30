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
    required_slope = [i-1 for i in required_slope]

    if simple_peaks:
        peaks = [x[np.argmax(timeseries.values)]]
        pneg = []
        required_slopes = []

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
    reduced_flux, reduced_mass = reduce_timeseries(
            flux, threshold_area, threshold_peak,
            mass, solve_type, simple_peaks)
    
    result = ReductionResult(
            flux=flux,
            mass=mass,
            reduced_flux=reduced_flux,
            reduced_mass=reduced_mass)
    return result
    
