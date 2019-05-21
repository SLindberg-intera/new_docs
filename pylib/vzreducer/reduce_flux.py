import pylib.vzreducer.timeseries_math as tsmath
import pylib.vzreducer.recursive_contour as redcon  
from pylib.vzreducer.reduction_result import ReductionResult
import numpy as np

SMOOTH = "SMOOTH"
RAW = "RAW"

def reduce_timeseries(timeseries, threshold_area, threshold_peak,
        solve_type=RAW):
    x = timeseries.times
    y = timeseries.values
    if solve_type == SMOOTH:
        ts_smooth = tsmath.smooth(timeseries)
        y = ts_smooth.values
    r = redcon.reducer((x,y), 
            threshold_area=threshold_area,
            threshold_peak=threshold_peak,
    )

    flat_reduced_x = set(redcon.flatten_reduced(r))
    peaks = [timeseries.times[np.argmax(timeseries.values)]]
    required = {x[0], x[-1]}
    xout = sorted(list(flat_reduced_x.union(required).union(set(peaks))))

    return timeseries.subset(xout)

def reduce_flux(flux, threshold_area, threshold_peak, solve_type):
    mass = tsmath.integrate(flux)
    reduced_flux = reduce_timeseries(flux, threshold_area, threshold_peak,
            solve_type)
    reduced_mass = tsmath.integrate(reduced_flux)
    
    result = ReductionResult(
            flux=flux,
            mass=mass,
            reduced_flux=reduced_flux,
            reduced_mass=reduced_mass)
    return result
    
