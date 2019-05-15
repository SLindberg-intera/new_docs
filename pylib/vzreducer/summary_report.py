import os
import pylib.vzreducer.constants as c
from pylib.vzreducer.config import config

class SummaryReportRecord:
    """ 
        Helps write reduced data to a file
    """
    def __init__(self, copc,
            site, total_mass_error='',
            average_mass_error='',
            target_file='',
            plot_file='',
            starting_number='',
            reduced_number='',
            reduced_threshold='',
            area_threshold='',
            total_mass='',
            model_mass_error='',
            relative_mass_error='',
            mass_error_factor=''):
        self.copc = copc
        self.site = site
        self.total_mass_error = total_mass_error
        self.average_mass_error = average_mass_error
        self.target_file = target_file
        self.plot_file = plot_file
        self.starting_number = starting_number
        self.reduced_number = reduced_number
        self.reduced_threshold = reduced_threshold
        self.area_threshold = area_threshold
        self.model_mass_error = model_mass_error
        self.total_mass = total_mass
        self.mass_error_factor = mass_error_factor
        self.relative_mass_error = relative_mass_error

    @classmethod
    def from_reduced_timeseries(cls, reduced_timeseries):
        """
            timeseries is instance of ReducedTimeSeries;
        """
        rt = reduced_timeseries
        return cls(
                copc=rt.copc,
                site=rt.site,
                reduced_number=len(rt),
                total_mass_error=rt.last_mass_error,
                model_mass_error=rt.model_mass_error,
                total_mass=rt.total_mass,
                relative_mass_error=rt.relative_mass_error,
                mass_error_factor=rt.mass_error_factor
                )

    def to_line(self, template):
        """
            write the results to a string
        """
        return template.format(
                site=self.site,
                copc=self.copc,
                reduced_number=self.reduced_number,
                total_mass_error=self.total_mass_error,
                model_mass_error=self.model_mass_error,
                total_mass=self.total_mass,
                mass_error_factor=self.mass_error_factor,
                relative_mass_error=self.relative_mass_error,
                average_mass_error=self.average_mass_error
        )
