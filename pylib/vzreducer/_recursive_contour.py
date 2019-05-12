import scipy.interpolate as interp
from scipy.integrate import trapz, cumtrapz
from scipy.signal import find_peaks
import numpy as np
import matplotlib.pyplot as plt


def make_line(signal):
    x, y = signal
    line_x = [x[0], x[-1]]
    line_y = [y[0], y[-1]]
    line = interp.interp1d(line_x, line_y)
    return x, line(x)

def subtract(signal, line):
    x, y = signal
    return x, np.abs(y-line[1])

def normalize(signal):
    x, y = signal
    return x, y
    ay = np.abs(y)
    ay = y
    my = np.max(y)
    if my < 1e-16:
        return x, ay
    n = ay/np.max(y)
    return x, n

def integrate(signal):
    x, y = signal
    return trapz(y, x)

def partition(signal, ix):
    x, y = signal
    A = (x[:ix], y[:ix])
    B = (x[ix:], y[ix:])
    return A, B

def reducer(signal, threshold_area):
    x, y = signal
    line = make_line(signal)
    flat_segment = normalize(subtract(signal, line))
    area = integrate(flat_segment)
    try:
        peak, xpeak = get_first_peak(flat_segment)
    except ValueError:
        return x[0]
    if area < threshold_area:
        return xpeak
    segments = partition(signal, peak)
    return [reducer(segment, threshold_area) for segment in segments]

def flatten_reduced(reduced):
    for seg in reduced:
        try:
            yield from flatten_reduced(seg)
        except TypeError:
            yield seg

def get_first_peak(signal):
    x, y = signal
    if len(x)<=2:
        raise ValueError("Not enough Points")

    ix = np.argmax(np.abs(y))
    #plt.plot(x, y)
    #plt.plot([x[ix]], [y[ix]], 'ro')
    #plt.show()
    return ix, x[ix]

    peak_indicies, _ = find_peaks(y)
    max_peak_ix = np.argmax(y[peak_indicies])
    p = np.where(x[peak_indicies]==max_peak_ix)[0]
    return p, x[p]
    return peak_indicies[0], x[peak_indicies[0]]

def make_signal():
    start = 0.01
    end = 2*np.pi
    x = np.arange(start, end, 0.001)
    y = 5*np.sin(3*x)*np.sin(x)/x-x+5
    return x, y


if __name__ == "__main__":

    signal = make_signal()
    line = make_line(signal)
    x, y = signal
    sx, sy = normalize(subtract(signal, line))
    area = 1.4
    res = list(set(flatten_reduced(reducer(signal, area))))
    res = np.concatenate(([x[0]], sorted(res), [x[-1]]))
    yout = [y[np.where(x==i)[0]][0] for i in res]

    num_out = len(yout)
    num_in = len(y)
    factor = num_in/num_out

    f, (a1, a2) = plt.subplots(2,1, sharex=True, squeeze=True)
    a1.plot(x, y, 'b.')
    a1.plot(res, yout, 'yo-')
    print("Reduced by {:.1f}: {} -> {}".format(factor, num_in, num_out))
    a2.plot(res, cumtrapz(yout, res, initial=0))
    a2.plot(x, cumtrapz(y, x, initial=0))

    plt.show()
