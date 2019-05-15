""" represents a timeseries """
import scipy.signal as signal
from scipy.integrate import cumtrapz as cumtrapz, trapz
import numpy as np
from pylib.vzreducer.config import config
import pylib.vzreducer.constants as c

def smooth(timeseries):
    """ smooth the data set """
    x = timeseries.times
    y = timeseries.values
    
    N = config[c.SMOOTH_KEY][c.BUTTER_INDEX_KEY]
    f_c = config[c.SMOOTH_KEY][c.CUTOFF_FREQUENCY]
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

    def __len__(self):
        return len(self.times)

    def are_all_zero(self):
        return np.all(self.values==0)

    def smooth(self):
        """ return a new instanced with smoothed data """ 
        smoothed_values = smooth(self)
        return TimeSeries(self.times, smoothed_values, 
                self.copc, self.site)

    def get_residual(self):
        """ Return an instance of Residual from self """
        return Residual(self)

    def integrate(self):
        """ integrate as a cumulative trap"""
        y_int = cumtrapz(self.values, self.times, initial=0)
        return TimeSeries(self.times, y_int, self.copc, self.site)

    def diff(self):
        y_diff = np.gradient(self.values, self.times)
        return TimeSeries(self.times, y_diff, self.copc, self.site)

    def rectified_acceleration(self, diff=None, 
            acc=None, integ=None, prob=None):
        """
            calculate the acceleration of the signal
            and take the absolute value

            then normalize it.

            This acts as a probability distribution of where the signal
            is likely to be non-linear.
        """
        if diff is None:
            diff = self.diff()
        if acc is None:    
            acc = diff.diff()
        if integ is None:
            integ = self.integrate()
        if prob is None:    
            p_acc =  np.abs(acc.values)/np.max(acc.values)
            p_diff = np.abs(diff.values)/np.max(diff.values)
            p_sig = np.abs(self.values)/np.max(self.values)
            p_mass = np.abs(-(np.max(integ.values)-integ.values))
            p_mass = p_mass/np.max(p_mass)
            y = (p_mass+p_sig+p_acc+p_diff)
            rect = [1 if item>0.1 else item for item in y]
            #rect = y
        else:
            rect = prob
        norm = np.sum(rect)
        return TimeSeries(self.times, rect/norm, self.copc, self.site)

    def get_peaks(self):
        peaks, _ = signal.find_peaks(self.values)
        peaks_neg, _ = signal.find_peaks(-self.values)
        peaks = np.concatenate((self.times[peaks], self.times[peaks_neg]))
        return np.concatenate((peaks, peaks_neg))
            

    def sample(self, N=30, required=[], interval=None, probs=None):
        """ sample from the signal where the probability is high """
        if probs is None:
            rect = self.rectified_acceleration().values
        else:
            rect = probs/np.sum(probs)
        res = np.random.choice(self.times, N, p=rect, replace=False)

        if interval is not None:
            res = np.concatenate((res, self.times[::interval],
                 [self.times[0], self.times[-1]],
                 required
                ))

        sorted(list(set(res)))
        return res

    def subset(self, timesteps):
        """ return a TimeSeries with the specific timesteps """
        times = self.times
        values = self.values
        condition = [i in timesteps for i in self.times]
        out = values[condition]
        return TimeSeries(times[condition], out, self.copc, self.site)


class Residual:
    """  Represents a signal with an estimate
            of its error
    """
    def __init__(self, timeseries):
        self.raw = timeseries
        self.smoothed = timeseries.smooth()
        self.errors = self.estimate_error_series()
        self.error_mean = np.mean(np.abs(self.errors.values))/(
                np.sqrt(len(self.errors.times))
                )
        self.error_std = np.std(np.abs(self.errors.values))
        self.mass_error = self._mass_error()

    def _mass_error(self):
        """ effectively integrating the error in the flux
        to get an estimate of the accumlative error in the mass
        at the last timestep
        
        """
        return self.error_mean*(self.raw.times[-1]-self.raw.times[0])

    def estimate_error_series(self):
        """
            estimate the error by subtracting the
            smoothed signal from the raw signal
        """
        v = self.raw.values - self.smoothed.values
        copc = self.raw.copc
        site = self.raw.site
        return TimeSeries(self.raw.times,  v, copc, site)

    def region_large_error(self):
        """ return a TimeSeries that only has the points
        that have an ERROR > average error (not signal)

        These are points where the smoothing was poor
        """
        condition = np.abs(self.errors.values) > self.error_mean
        xnew = self.raw.times[condition]
        ynew = self.raw.values[condition]
        return TimeSeries(xnew, ynew, self.raw.copc, self.raw.site)

    def region_above_error(self):
        """ return a TimeSeries that only has values that
        are (strictly) greater than the estimated noise floor """
        condition = np.abs(self.raw.values) > self.error_mean
        xnew = self.raw.times[condition]
        ynew = self.raw.values[condition]
        return TimeSeries(xnew, ynew, self.raw.copc, self.raw.site)

    def region_below_error(self):
        """ return a TimeSeries that only has values that
        are less than or equal to the estimated noise floor """
        condition = np.abs(self.raw.values) <= self.error_mean
        xnew = self.raw.times[condition]
        ynew = self.raw.values[condition]
        return TimeSeries(xnew, ynew, self.raw.copc, self.raw.site)

