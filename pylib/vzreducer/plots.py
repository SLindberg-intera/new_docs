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


def reduced_timeseries_plot(timeseries):
    error_report = timeseries.error_report
    
    f, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True, squeeze=True)
    raw_x = error_report.timeseries.times
    raw_y = error_report.timeseries.values
    red_x = timeseries.times
    red_y = timeseries.values
    
    # the flux data
    ax1.plot(raw_x, raw_y, 'b.')
    ax1.plot(red_x, red_y, 'r.')

    mass_x = error_report.integrated_timeseries.times
    mass_y = error_report.integrated_timeseries.values
    red_mass_x = error_report.integrated_reduced_timeseries.times
    red_mass_y = error_report.integrated_reduced_timeseries.values

    # the mass data
    ax2.plot(mass_x, mass_y, 'b.-')
    ax2.plot(red_mass_x, red_mass_y, '.')

    # the residual
    resid_x = error_report.mass_error.times
    resid_y = error_report.mass_error.values
    ax3.plot(resid_x, resid_y, 'b.')

    ax1.yaxis.set_major_formatter(FORMATTER)
    ax2.yaxis.set_major_formatter(FORMATTER)
    ax3.yaxis.set_major_formatter(FORMATTER)

    ax1.set_title(
            "{}  {}".format(
            timeseries.site, timeseries.copc)
            )
    ax1.set_ylabel("Flux (Ci/yr)")
    ax2.set_ylabel("Mass (Ci)")
    ax3.set_ylabel("Error Mass (Ci)")

    return f, (ax1, ax2, ax3)

def recursive_plot(timeseries, masseries):
    """
        DEPRECIATED : This was development code
    """
    integrated = timeseries.integrate()
    residual = timeseries.get_residual()
    mass_error = residual.mass_error
    area = mass_error 
    threshold_peak = 200*residual.error_mean
    to_recurse = timeseries 
    r = recursive_contour.reducer(
            (to_recurse.times, to_recurse.values), area, 
            threshold_peak=threshold_peak)
    red = recursive_contour.flatten_reduced(r)
    ix = np.argmax(timeseries.values)
    res = sorted(list(set(red).union([timeseries.times[ix]])))
    yout = [timeseries.values[np.where(
        integrated.times==i)[0]][0] for i in res]
    f, (ax1, ax2) = plt.subplots(2, 1, sharex=True, squeeze=True)
    ax1.plot(timeseries.times, timeseries.values, '.')
    ax2.plot(integrated.times, integrated.values, 'b.-')
    ax1.plot(res, yout, '.r')
    temp = timeseries
    temp.times = res
    temp.values = yout
    reduced_integrated = temp.integrate()
    ax2.plot(reduced_integrated.times, reduced_integrated.values, 'c.-')
    plt.show()
    print(len(reduced_integrated.times))
    v = reduced_integrated.values[-1] - integrated.values[-1]
    print("Error:{}  estimated signal error:{}".format(v, mass_error))


def mass_plot(timeseries, masseries):
    integrated = timeseries.integrate()
    residual = timeseries.get_residual()
    mass_error = residual.mass_error
    acc = timeseries.rectified_acceleration(integ=integrated)
    f, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True, squeeze=True)
    ax1.plot(timeseries.times, timeseries.values, get_symbol(c.RAW))
    ax2.plot(masseries.times, masseries.values)
    ax1.yaxis.set_major_formatter(FORMATTER)
    ax2.yaxis.set_major_formatter(FORMATTER)
    cnt = 0
    Sout = 300
    Savg = 300
    ErrSig = 300
    peaks = timeseries.get_peaks()
    new_prob = acc.values
    max_mass = np.max(integrated.values)
    required = []
    while (cnt < 500):
        req_points = np.concatenate((required, peaks))
        t_choices = timeseries.sample(N=30,
                interval=1000, required=req_points, probs=new_prob)
        t_subset = timeseries.subset(t_choices)
        t_int0 = integrated.subset(t_choices)
        t_int = t_subset.integrate()
        t_tot = (np.abs(t_int.values-t_int0.values))
        t_s = np.sum(t_tot)/len(t_int.values)
        t_s_relative = t_s/max_mass
        m_out_error = np.abs(t_int.values[-1]-t_int0.values[-1])
        m_out_relative_error=m_out_error/max_mass

        grand_errs_fn = interpolate.interp1d(t_int.times, t_tot)
        interp_sig_fn = interpolate.interp1d(
                t_subset.times, t_subset.values)
        interp_sig = interp_sig_fn(timeseries.times)

        timeseries_err =  (
              np.abs(interp_sig-timeseries.values))
        timeseries_err_tot = np.sum(timeseries_err)

        if m_out_error < Sout and t_s < Savg and timeseries_err_tot < ErrSig:
            ratio = m_out_error/mass_error
            ratio2 = t_s/mass_error
            relative_error_model = mass_error/max_mass

            print("ix:{} Eavg:{:.2g} Eavgrel:{:.2g} Emodel:{:.2g} Erelmodel:{:.2g} Elast:{:.2g} average_err ratio:{:.2g} last mass ratio:{:.2g} last rel err:{:.2g}".format(
                cnt, t_s, t_s_relative, mass_error, 
                relative_error_model, m_out_error, 
                ratio2, ratio, 
                m_out_relative_error
            ))
            Sout = m_out_error
            subset = t_subset
            Savg = t_s
            ErrSig = timeseries_err_tot
            gef = grand_errs_fn(timeseries.times)
            ms = timeseries_err/np.max(timeseries_err)
            ms = -(ms -np.max(ms))
            ix = np.where(ms<0.2)[0]
            new_prob = acc.values+0.1*ms/np.sum(ms)
            #new_prob[ix] = 1
            if ratio < 1 and ratio2 < 1:
                print("terminated at {}".format(cnt))
                break
        cnt+=1    

    ax1.plot(subset.times, subset.values, 'r.')
    mass2 = subset.integrate()
    ax2.plot(mass2.times, mass2.values)
    ax3.plot(timeseries.times, ms)

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
