"""
    use data reduction method on groundwater timeseries

"""
import numpy as np
from pylib.timeseries.timeseries import TimeSeries
from pylib.gwreducer import reduce_flux as red_flux

SMOOTH = 'SMOOTH'
RAW = 'RAW'

def reduce_dataset(years, values):
    """ takes  times and values and then reduces it

    returns reduced_times and reduced_values
    
    if all elements are zero, it returns False

    """
    maxval = np.max(values)
    values = values/maxval
    timeseries = TimeSeries(years, values, None, None)
    if timeseries.are_all_zero():
        logging.info("Skipped - all zero")
        return False    
    
    mx = np.argmax(timeseries.values)
    points = [0, mx, len(timeseries)]
    x = timeseries.times

    mass = timeseries.integrate()
    area = 100*np.mean(timeseries.values)*(x[-1]-x[0])
    ythresh = 100*np.mean(timeseries.values)
    out_error = 1
    out_error_last = out_error
    OUT_ERROR_THRESHOLD = 1e-2
    UPPER_N = 50
    LOWER_N = 15
    last_result = None 
    MAX_ITERATIONS = 80

    solve_type = SMOOTH
    simple_peaks = False

    for ix in range(MAX_ITERATIONS):
        res = red_flux.reduce_flux(timeseries, area, ythresh, 
                solve_type=solve_type,
                simple_peaks=simple_peaks
                )
        out_error = abs(res.relative_total_mass_error)
        if out_error < OUT_ERROR_THRESHOLD and len(res.reduced_flux)>=LOWER_N:
            last_result = res
            break
        if len(res.reduced_flux) > 2*UPPER_N:
            simple_peaks = True
            solve_type = RAW
        ythresh = 0.5*ythresh
        area = 0.5*area
        out_error_last = out_error
        last_result = res

    if ix>=MAX_ITERATIONS - 1:
        logging.info("MAX ITERATIONS")

    last_result = red_flux.rebalance(last_result)
    out_times = last_result.reduced_flux.times
    out_values = last_result.reduced_flux.values
    return out_times, out_values*maxval

