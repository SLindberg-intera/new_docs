import pylib.vzreducer.timeseries_math as tsmath
import pylib.vzreducer.recursive_contour as redcon  
from pylib.vzreducer.reduction_result import ReductionResult
import numpy as np

def reduce_timeseries(timeseries, threshold_area, threshold_peak):
    x = timeseries.times
    y = timeseries.values
    r = redcon.reducer((x,y), 
            threshold_area=threshold_area,
            threshold_peak=threshold_peak,
    )

    flat_reduced_x = set(redcon.flatten_reduced(r))
    required = {x[0], x[-1]}
    xout = sorted(list(flat_reduced_x.union(required)))

    return timeseries.subset(xout)

def reduce_flux(flux, threshold_area, threshold_peak):
    mass = tsmath.integrate(flux)
    reduced_mass = reduce_timeseries(mass, threshold_area, threshold_peak)
    reduced_flux_direct = reduce_timeseries(
            flux, threshold_area, threshold_peak)

    x = sorted(list(set(np.concatenate((reduced_mass.times, reduced_flux_direct.times)
        ))))

    
    reduced_flux = flux.subset(x)
    reduced_mass = tsmath.integrate(reduced_flux)
    
    #reduced_flux = tsmath.diff(reduced_mass)

    result = ReductionResult(
            flux=flux,
            mass=mass,
            reduced_flux=reduced_flux,
            reduced_mass=reduced_mass)
    return result
    
