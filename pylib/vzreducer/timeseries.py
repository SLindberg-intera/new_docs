""" represents a timeseries """
import scipy.signal as signal
import numpy as np

def smooth(timeseries):
    """ smooth the data set """
    x = timeseries.times
    y = timeseries.values
    
    N = 4
    f_c = .1
    B, A = signal.butter(N, f_c, output='ba')
    smoothed = signal.filtfilt(B, A, y)

    return smoothed


class TimeSeries:
    """ Represents a particular site/copc's timeseries 
    
        times is array-like
        values is array-like (indexted the same as times)
        copc is a string
        site is a string
    
    """
    def __init__(self, times, values, copc, site):
        self.site = site
        self.copc = copc
        self.times = times
        self.values = values

    def smooth(self):
        """ return a new instanced with smoothed data """ 
        smoothed_values = smooth(self)
        return TimeSeries(self.times, smoothed_values, 
                self.copc, self.site)


class Residual:
    """  Represents a signal with an estimate
            of its error
    """
    def __init__(self, timeseries):
        self.raw = timeseries
        self.smoothed = timeseries.smooth()
        self.errors = self.estimate_error_series()
        self.error_mean = np.mean(np.abs(self.errors.values))
        self.error_std = np.std(np.abs(self.errors.values))
    
    def estimate_error_series(self):
        """
            estimate the error by subtracting the
            smoothed signal from the raw signal
        """
        v = self.raw.values - self.smoothed.values
        copc = self.raw.copc
        site = self.raw.site
        return TimeSeries(self.raw.times,  v, copc, site)


