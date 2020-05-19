import matplotlib
import matplotlib.pyplot as plt
plt.switch_backend('Agg')

#from matplotlib.ticker import EngFormatter
#from matplotlib.ticker import ScalarFormatter
import matplotlib.ticker as mtick
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)
import os.path
import numpy as np
#custom libraries
#import pylib.hssmbuilder.gwreducer.constants as c
#from pylib.hssmbuilder.gwreducer.config import config
import pylib.hssmbuilder.timeseries.timeseries_math as tsmath
from pylib.hssmbuilder.timeseries.timeseries import TimeSeries

#-------------------------------------------------------------------------------
#-create plots
#def make_title(residual):
#    return "{} {}".format(residual.raw.copc, residual.raw.site)

#BLACK = 'k

#FORMATTER = EngFormatter(places=0, sep="\N{THIN SPACE}")
#FORMATTER = ScalarFormatter(useOffset=False)
FORMATTER = mtick.FormatStrFormatter('%.1e')
def unit_conversion(ts,units,start_year):
    x = ts.times
    y = ts.values

    x = (x/365.25)+start_year
    y = y * 365.25
    new_unit = ['Ci/year','Ci']
    factor = 1
    if units.lower() == 'pci':
        factor = 1e-12
    elif units.lower() in ['kg','g','ug']:
        new_unit = ['kg/year','kg']
        if units.lower() == 'g':
            factor = 1e-3
        elif units.lower() == 'ug':
            factor = 1e-9
    new_ts = TimeSeries(x,y*factor,None,None)
    return new_ts, new_unit
def reduced_timeseries_plot(o_flux,r_flux,i,j,unit,start_year,copc,summary_plot):
    """  makes a pretty plot of the reduction result """
    f, (ax1, ax2) = plt.subplots(2,1, sharex=True)
    #o_flux, _ = unit_conversion(o_flux,units,start_year)
    #r_flux, _ = unit_conversion(r_flux,units,start_year)
    mass = o_flux.integrate()
    r_mass = r_flux.integrate()


    #dflux = o_ts - r_ts
    #dmass = mass - r_mass
    o_steps = o_flux.times.size
    r_steps = r_flux.times.size
    r_line = "r."
    g_title = "{} GW Model Surface {}-{}".format(copc,i,j)
    title = 'Activity'
    o_label = "unreduced ({} data points)".format(o_steps)
    r_label = "reduced   ({} data points)".format(r_steps)
    if unit[1].lower == 'kg':
        title = "Mass"
    if summary_plot:
        r_line = "r--"
        g_title = "{}".format(copc)
        o_label = "unreduced"
        r_label = "reduced"
    ax1.plot(o_flux.times, o_flux.values, 'b',    label=o_label)
    ax1.plot(r_flux.times, r_flux.values, r_line, label=r_label,markersize=4)
    ax2.plot(mass.times, mass.values, 'b')
    ax2.plot(r_mass.times, r_mass.values, r_line,markersize=4)

    ax1.yaxis.set_major_formatter(FORMATTER)
    ax2.yaxis.set_major_formatter(FORMATTER)
    ax1.legend()

    ax1.set_title(g_title)

    ax1.set_ylabel("Rate ({})".format(unit[0]))
    ax2.set_ylabel("Cumulative ({})".format(unit[1]))
    ax1.xaxis.set_minor_locator(AutoMinorLocator())
    ax1.set_xlabel("Calendar Year")
    ax2.set_xlabel("Calendar Year")
    ax2.xaxis.set_minor_locator(AutoMinorLocator())
    return  f, ax1, ax2

def summary_plot(o_time,o_flux,r_time,r_flux,i,j, output_folder,units,start_year,graph_name,copc,summary_plot = False):
    matplotlib.rcParams['axes.formatter.useoffset'] = False
    """ make a plot of hte reduction result and place it in output_folder"""

    o_flux = TimeSeries(o_time, o_flux, None, None)
    r_flux = TimeSeries(r_time, r_flux, None, None)
    #convert to ci/kg from current unit.
    o_flux, unit = unit_conversion(o_flux,units,start_year)
    r_flux, _ = unit_conversion(r_flux,units,start_year)

    f, ax1, ax2 = reduced_timeseries_plot(o_flux,r_flux,i,j,unit,start_year,copc,summary_plot)
    file_name = "{}_{}-{}.png".format(graph_name,i, j)
    if summary_plot:
        file_name = "{}.png".format(graph_name)

    plt.savefig(os.path.join(output_folder, file_name),bbox_inches='tight',dpi=1200)
    plt.close('all')
    plt.clf()
