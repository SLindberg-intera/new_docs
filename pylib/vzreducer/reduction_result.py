import pylib.vzreducer.timeseries_math as tsmath
import numpy as np


class ReductionResult:
    """
        container for four TimeSeries:
            flux (the raw flux curve)
            mass (the integrated raw flux curve)
            reduced_flux (the reduced flux curve)
            reduced_mass (the reduced mass curve)

    """
    def __init__(self, flux, mass, reduced_flux, reduced_mass):
        self.flux = flux
        self.mass = mass
        self.reduced_flux = reduced_flux
        self.reduced_mass = reduced_mass

    def as_str(self):
        return "n: {} E_m: {} E_f: {}".format(
                self.num_reduced_points,
                self.relative_total_mass_error,
                self.relative_average_flux_error)

    @property
    def num_reduced_points(self):
        return len(self.reduced_mass)

    @property
    def num_points(self):
        return len(self.flux)

    @property
    def reduction_ratio(self):
        return self.num_reduced_points/self.num_points

    @property
    def diff_mass(self):
        try:
            return self._diff_mass
        except AttributeError:
            self._diff_mass = tsmath.delta(self.mass, self.reduced_mass)
        return self.diff_mass    

    @property
    def diff_flux(self):
        try:
            return self._diff_flux
        except AttributeError:
            self._diff_flux = tsmath.delta(self.flux, self.reduced_flux)
        return self.diff_flux
    
    @property
    def total_mass_error(self):
        return self.diff_mass.values[-1]

    @property
    def average_mass_error(self):
        return np.mean(np.abs(self.diff_mass.values))

    @property
    def relative_total_mass_error(self):
        err = self.total_mass_error
        mss = self.mass.values[-1]
        return err/mss

    @property
    def relative_average_mass_error(self):
        err = self.average_mass_error
        mss = self.mass.values[-1]
        return err/mss

    @property
    def average_flux_error(self):
        return np.mean(np.abs(self.diff_flux.values))

    @property
    def max_flux_error(self):
        return np.max(np.abs(self.diff_flux.values))

    @property
    def relative_max_flux_error(self):
        return self.max_flux_error/self.max_flux

    @property
    def max_flux(self):
        return np.max(np.abs(self.flux.values))

    @property
    def relative_average_flux_error(self):
        err = self.average_flux_error
        flx = self.max_flux
        return err/flx

