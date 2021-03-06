import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
from matplotlib.ticker import EngFormatter
import pylib.vzreducer.constants as c
from pylib.vzreducer.config import config
import numpy as np
from scipy import interpolate

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
    """  makes a pretty plot of the reduction result """
    f, (ax1, ax2) = plt.subplots(2,1, sharex=True)
    f.figsize = [8,4.8]
    flux = reduction_result.flux
    mass = reduction_result.mass

    r_flux = reduction_result.reduced_flux
    #r_flux = reduction_result.reduced_flux.interpolate_at_timeseries(flux)
    r_mass = reduction_result.reduced_mass
    #r_mass = r_flux.integrate()
    #reduction_result.reduced_mass

    dflux = flux - r_flux
    dmass = mass - r_mass

    y_formatter = tkr.ScalarFormatter()
    y_formatter.set_scientific(True)
    #ax1.ticklabel_format(axis = 'y', style='sci', scilimits=(0,0))
    #ax1.yaxis.set_major_formatter(y_formatter)
    ax1.yaxis.set_major_formatter(tkr.FormatStrFormatter('%.2e'))
    ax2.yaxis.set_major_formatter(tkr.FormatStrFormatter('%.2e'))

    ax1.plot(flux.times[:], flux.values[:], 'b', label="input")
    ax1.plot(r_flux.times[:], r_flux.values[:], 'r.', label="reduced ({} data pairs)".format(len(r_flux.values)))
    ax2.plot(mass.times[:], mass.values[:], 'b')
    ax2.plot(r_mass.times[:], r_mass.values[:], 'r.')

    ax1.plot(dflux.times[:], dflux.values[:], 'k', label="diff [original-reduced]")
    ax2.plot(dmass.times[:], dmass.values[:], 'k')

    #ax1.plot(flux.times[0:500], flux.values[0:500], 'b', label="input")
    #ax1.plot(r_flux.times[0:22], r_flux.values[0:22], 'r.', label="reduced {}".format(len(r_flux.values)))
    #ax2.plot(mass.times[0:500], mass.values[0:500], 'b')
    #ax2.plot(r_mass.times[0:22], r_mass.values[0:22], 'r.')

    #ax1.plot(dflux.times[0:500], dflux.values[0:500], 'k', label="diff [original-reduced]")
    #ax2.plot(dmass.times[0:500], dmass.values[0:500], 'k')

    #ax1.yaxis.set_major_formatter(FORMATTER)
    #ax2.yaxis.set_major_formatter(FORMATTER)
    ax1.legend()

    ax1.set_title(
            "{}  {}".format(
            flux.site, flux.copc)
            )
    ax1.set_ylabel("Flux (Ci/yr)")
    #ax1.set_xlabel("Time (years)")
    ax2.set_ylabel("Mass (Ci)")
    ax2.set_xlabel("Time (years)")

    return  f, ax1, ax2



