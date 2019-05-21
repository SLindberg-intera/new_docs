"""
    DEPRECIATED?

    helper for taking a TimeSeries object
    and then reducing the number of data points

"""

import numpy as np
import pylib.vzreducer.recursive_contour as recursive_contour
import pylib.vzreducer.timeseries as ts 
from scipy.interpolate import interp1d


class ErrorReport:
    """ Abstracts error information about a 
        data reduction operation
    """
    def __init__(self, 
            timeseries,
            integrated_timeseries, 
            reduced_timeseries,
            integrated_reduced_timeseries,
            residual 
            ):
        self.timeseries = timeseries 
        self.integrated_timeseries = integrated_timeseries 
        self.integrated_reduced_timeseries = integrated_reduced_timeseries

        self.reduced_mass = self.make_interpolation(
                integrated_timeseries,
                integrated_reduced_timeseries)
        self.residual = residual
        self.mass_error = self.calc_mass_error(integrated_timeseries)
        self.last_raw_mass = integrated_timeseries.values[-1]
        
        self.model_mass_error = residual.mass_error
        self.number_reduced_points = len(
                timeseries)-len(reduced_timeseries)

    @property
    def last_mass_error(self):
        try:
            return self._last_mass_error
        except AttributeError:
            self._last_mass_error = self.mass_error.values[-1]
        return self.last_mass_error    

    @property
    def average_rms_mass_error(self):
        try:
            return self._average_rms_mass_error
        except AttributeError:
            self._average_rms_mass_error = np.mean(
                    np.abs(self.mass_error.values))
        return self.average_rms_mass_error

    @property
    def total_rms_mass_error(self):
        try:
            return 
        except AttributeError:
            self._total_rms_mass_error = np.sum(
                    np.abs(self.mass_error.values))
        return self.total_rms_mass_error

    def calc_mass_error(self, integrated_timeseries):
        y = self.reduced_mass.values - integrated_timeseries.values
        return ts.TimeSeries(
                times = integrated_timeseries.times,
                values = y,
                copc=integrated_timeseries.copc,
                site=integrated_timeseries.site
                )

    def make_interpolation(self, raw, reduced):
        """ linearly interpolate the reduced data set
        at all the points on the raw data set """
        self.mass_error_f = interp1d(reduced.times, reduced.values)

        return ts.TimeSeries(
                times=raw.times,
                values=self.mass_error_f(raw.times),
                copc=raw.copc,
                site=raw.site)

class ReducedTimeSeries(ts.TimeSeries):
    def __init__(self, error_report, timeseries, area=None, threshold_peak=None):
        self.error_report = error_report
        super().__init__(
                times=timeseries.times,
                values=timeseries.values,
                copc=timeseries.copc,
                site=timeseries.site)
        self.area = area
        self.threshold_peak = threshold_peak

    def get_residual(self):
        return self.error_report.residual

    @property
    def number_reduced_points(self):
        return self.error_report.number_reduced_points

    @property
    def last_mass_error(self):
        return self.error_report.last_mass_error

    @property
    def total_rms_mass_error(self):
        return self.error_report.total_rms_mass_error
    
    @property
    def total_mass(self):
        return self.error_report.integrated_timeseries.values[-1]

    @property
    def model_mass_error(self):
        """ an estimate of the mass error expected from the model itself
            due to model noise"""
        return self.error_report.model_mass_error
    
    @property
    def mass_error_factor(self):
        """
            the mass error expressed as a fraction of the model error
        """
        return self.last_mass_error/self.model_mass_error

    @property
    def relative_mass_error(self):
        """
            mass_error/last_mass
        """
        return self.last_mass_error/self.total_mass


    @classmethod
    def from_timeseries(cls, timeseries, area=None, threshold_peak=None):
        """
            timeseries is a instance of TimeSeries
        """
        integrated = timeseries.integrate()
        residual = timeseries.get_residual()
        mass_error = residual.mass_error
        if area is None:
            #area = 1e5*mass_error 
            area = abs(np.max(integrated.values))

        if threshold_peak is None:
            threshold_peak = .2501
        #100000*residual.error_mean
        r = recursive_contour.reducer(
                (timeseries.times, timeseries.values), area, 
                threshold_peak=threshold_peak)
        red = recursive_contour.flatten_reduced(r)
        ix = np.argmax(timeseries.values)
        res = sorted(list(set(red).union([
            timeseries.times[ix],
            timeseries.times[0],
            timeseries.times[-1]
            ])
        )) # timeseteps of the output 
        yout = [timeseries.values[np.where(
            integrated.times==i)[0]][0] for i in res]
        
        reduced_timeseries = ts.TimeSeries(
                times=res, values=yout, copc=timeseries.copc,
                site=timeseries.site)

        error_report = ErrorReport(
                timeseries,
                integrated,
                reduced_timeseries,
                reduced_timeseries.integrate(),
                residual=residual
                )
        return cls(error_report, reduced_timeseries, area, threshold_peak) 
