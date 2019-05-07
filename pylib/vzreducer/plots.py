import matplotlib.pyplot as plt

def make_title(residual):
    return "{} {}".format(residual.raw.copc, residual.raw.site)

def residual_plot(residual, tofile):
    x = residual.raw.times
    raw = residual.raw.values

    smoothed = residual.smoothed.values

    errs = residual.errors.values

    f, (ax1, ax2) = plt.subplots(2,1, sharex=True, squeeze=True)

    ax1.plot(x, smoothed, 'k')
    ax1.plot(x, raw, 'b.')
    ax1.set_ylabel("Signal")
    ax2.plot(x, errs, 'r.')
    ax2.plot(x, 0*errs+residual.error_mean, 'k')
    ax2.plot(x, 0*errs-residual.error_mean, 'k')
    ax2.set_ylabel("Est. Error")
    ax1.set_title(make_title(residual))
    ax2.set_title("Avg. Error: {:.4g}".format(residual.error_mean))
    f.savefig(tofile)
