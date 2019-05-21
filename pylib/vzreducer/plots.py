import matplotlib.pyplot as plt
from matplotlib.ticker import EngFormatter
import pylib.vzreducer.constants as c
from pylib.vzreducer.config import config
import numpy as np
from scipy import interpolate

from pylib.vzreducer.reduce_timeseries import ReducedTimeSeries

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

def reduced_timeseries_plot(reduction_result):
    f, (ax1, ax2) = plt.subplots(2,1, sharex=True)
    flux = reduction_result.flux
    mass = reduction_result.mass
    r_flux = reduction_result.reduced_flux
    r_mass = reduction_result.reduced_mass

    ax1.plot(flux.times, flux.values, 'b.-')
    ax1.plot(r_flux.times, r_flux.values, 'r.')
    ax2.plot(mass.times, mass.values, 'b.-')
    ax2.plot(r_mass.times, r_mass.values, 'r.')

    ax1.yaxis.set_major_formatter(FORMATTER)
    ax2.yaxis.set_major_formatter(FORMATTER)

    ax1.set_title(
            "{}  {}".format(
            flux.site, flux.copc)
            )
    ax1.set_ylabel("Flux (Ci/yr)")
    ax2.set_ylabel("Mass (Ci)")

    return  f, ax1, ax2



