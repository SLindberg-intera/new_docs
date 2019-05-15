"""
represents a reduction operation

"""

class Reduction:
    """ 
        A container for parameters related to reducing data

    """
    def __init__(self, diff_threshold, area_threshold):
        
        self.diff_threshold=diff_threshold
        self.area_threshold=area_threshold

    def reduce(self, timeseries):
        """
            Takes a TimeSeries object and then reduces it
        """

        pass
