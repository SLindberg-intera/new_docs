"""
    Relies on TimeSeries
"""


from pylib.vzreducer.timeseries import TimeSeries
import numpy as np

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

