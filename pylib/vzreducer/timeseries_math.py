"""
    operations on TimeSeries
"""

import scipy.signal as signal
from scipy.integrate import cumtrapz as cumtrapz, trapz
from pylib.vzreducer.config import config
import pylib.vzreducer.constants as c
from scipy.interpolate import interp1d
import numpy as np

def smooth(timeseries):
    """ smooth the data set """
    x = timeseries.times
    y = timeseries.values
    
    N = config[c.SMOOTH_KEY][c.BUTTER_INDEX_KEY]
    f_c = config[c.SMOOTH_KEY][c.CUTOFF_FREQUENCY]
    B, A = signal.butter(N, f_c, output='ba')
    smoothed = signal.filtfilt(B, A, y)

    return timeseries.from_values(smoothed)


def equal_times(timeseries1, timeseries2):
    """
        True if times are equivalent
    """
    return np.all(timeseries1.times == timeseries2.times)


def interpolate(timeseries):
    """ create a linear interpolation of the timeseries
    
        returns a function f(times)->interpolated_values

    """
    x = timeseries.times
    y = timeseries.values
    return interp1d(x, y, assume_sorted=True)


def integrate(timeseries):
    """ integrate as a cumulative trap"""
    y_int = cumtrapz(timeseries.values, timeseries.times, initial=0)
    return timeseries.from_values(y_int)


def diff(timeseries):
    """ simple first order derviative"""
    y_diff = np.gradient(timeseries.values, timeseries.times)
    return timeseries.from_values(y_diff)


def delta(timeseries1, timeseries2):
    """
        return a timeseries that is ts1.values - ts2.values

        if the times are not the same, iterpolate ts2 at ts1's times
        and then subtract

    """
    if equal_times(timeseries1, timeseries2):
        return timeseries1.from_values(
                values=(timeseries1.values-timeseries2.values))

    interp_fn = interpolate(timeseries2)
    interp_values = interp_fn(timeseries1.times)
    aligned_timeseries = timeseries1.from_values(
            values=interp_values)
    return delta(timeseries1, aligned_timeseries)


