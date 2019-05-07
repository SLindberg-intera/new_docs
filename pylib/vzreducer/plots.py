import matplotlib.pyplot as plt
from matplotlib.ticker import EngFormatter
import pylib.vzreducer.constants as c
from pylib.vzreducer.config import config
import numpy as np

def make_title(residual):
    return "{} {}".format(residual.raw.copc, residual.raw.site)


PLOT = config[c.PLOTS_KEY] # shortcut to the PLOT dict in the config file
BLACK = 'k'

def get_symbol(source_key):
    """ construct a matplotlib plot symbol

    source_key must be the key of the PLOT dict in the config file
    """
    color = PLOT[source_key][c.COLOR]
    symbol = PLOT[source_key][c.SYMBOL]
    return color+symbol


FORMATTER = EngFormatter(places=0, sep="\N{THIN SPACE}")

def mass_plot(timeseries, masseries):
    f, (ax1, ax2) = plt.subplots(2, 1, sharex=True, squeeze=True)
    ax1.plot(timeseries.times, timeseries.values, get_symbol(c.RAW))
    ax2.plot(masseries.times, masseries.values)

    ax1.yaxis.set_major_formatter(FORMATTER)
    ax2.yaxis.set_major_formatter(FORMATTER)
    plt.show()

def residual_plot(residual, tofile, show=False):
    """
        Constructs a plot with two graphs:

        Top plot: the signal and the smoothed values for that signal
        Bottomplot : the estimated error for the signal


        the result is saved to a file "tofile" or displayed
        to the screen if show=True

    """

    x = residual.raw.times
    raw = residual.raw.values
    

    smoothed = residual.smoothed.values

    errs = residual.errors.values
    regs = residual.region_large_error()

    f, (ax1, ax2) = plt.subplots(2, 1, sharex=True, squeeze=True)

    ax1.plot(x, raw, get_symbol(c.RAW))

    ax1.plot(x, smoothed, get_symbol(c.SMOOTHED))
    ax1.plot(regs.times, regs.values, get_symbol(c.ERROR))

    ax1.set_ylabel(PLOT[c.SIGNAL_TITLE])
    ax2.plot(x, np.abs(errs), get_symbol(c.ERROR))
    ax2.plot(x, 0*errs+residual.error_mean, BLACK)
    #ax2.plot(x, 0*errs-residual.error_mean, BLACK)
    ax2.set_yscale('log')
    
    ax2.set_ylabel(PLOT[c.ERROR_TITLE])
    ax1.set_title(make_title(residual))
    ax2.set_title(PLOT[c.AVERAGE_ERROR_LABEL].format(
        residual.error_mean, residual.mass_error))

    ax1.yaxis.set_major_formatter(FORMATTER)
    ax2.yaxis.set_major_formatter(FORMATTER)
    if show:
        plt.show()
    else:    
        f.savefig(tofile)
