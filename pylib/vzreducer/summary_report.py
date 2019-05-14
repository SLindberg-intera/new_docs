import os
import pylib.vzreducer.constants as c
from pylib.vzreducer.config import config

class SummaryReportRecord:
    """ 
        Helps write reduced data to a file
    """
    def __init__(self, copc,
            site, total_error,
            average_mass_error,
            target_file,
            plot_file,
            starting_number,
            reduced_number,
            reduced_threshold,
            area_threshold):
        self.copc = copc
        self.site = site
        self.total_mass_error = total_error
        self.average_mass_error = average_mass_error
        self.target_file = target_file
        self.plot_file = plot_file
        self.starting_number = starting_number
        self.reduced_number = reduced_number
        self.reduced_threshold = reduced_threshold
        self.area_threshold = area_threshold
    
    @classmethod
    def from_reduced_timeseries(cls, reduced_timeseries):
        """
            timeseries is instance of ReducedTimeSeries;
        """
        rt = reduced_timeseries
        return cls(
                copc=rt.copc,
                site=rt.site
                )

    def to_line(self, template):
        """
            write the results to a string
        """
        return template.format(
                site=self.site,
                copc=self.copc,
                average_mass_error=self.average_mass_error
        )
