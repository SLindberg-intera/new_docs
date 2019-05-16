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

def integrate(signal):
    x, y = signal
    return trapz(y, x)

def diff(signal):
    x, y = signal
    return x, np.gradient(y,x)

def partition(signal, xpeak):
    x, y = signal
    ix = np.where(x==xpeak)[0][0]
    if ix == 0:
        return None
    A = (x[0:ix], y[0:ix])
    B = (x[ix:], y[ix:])
    return [A, B]

def reducer(signal, threshold_area, threshold_peak, branch0=0):
    x, y = signal
    if len(x)<=2:
        return [x[-1]]
    dx = x[-1]-x[1]
    line = make_line(signal)
    flat_segment = subtract(signal, line)
    area = np.max(y)/integrate(flat_segment) #/(dx*np.max(y))
    y_seg = flat_segment[1]

    if np.all(
         (y_seg)/np.max(y)<threshold_peak) and area < threshold_area:
        return [x[-1]]
    peak, xpeak, ypeak = get_first_peak(flat_segment)
    segments = partition(signal, xpeak)
    if segments is None:
        return [x[0], x[-1]]
    return [reducer(segment, threshold_area, threshold_peak,
        branch0*10+branch) 
            for branch, segment in enumerate(segments)
            ]

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
    ix = np.argmax(y)
    return ix, x[ix], y[ix]
    peak_indicies, _ = find_peaks(y)
    # also need to find valleys
    #valleys = (y-np.max(y))
    #valley_indicies, _ = find_peaks(valleys)
    #plt.plot(x, y)
    #plt.plot(x, valleys)
    #plt.show()
    p = peak_indicies

    #p = set(peak_indicies).union(set(valley_indicies))
    #p = sorted(list(p))
    try:
        return p[0], x[p[0]], y[p[0]]
    except IndexError:
        return 0, x[0], y[0]


def make_signal():
    start = 0.01
    end = 2*np.pi
    x = np.arange(start, end, 0.0001)
    y = np.zeros(len(x))
    y[234:237] = 200
    y[237:10600] = 53
    #y = 5*np.sin(8*x)*np.sin(x)/x-x+5
    return x, y


if __name__ == "__main__":

    signal = make_signal()
    line = make_line(signal)
    x, y = signal
    area = 1e-8
    ytol = .1
    
    
    rawf = cumtrapz(y, x, initial=0)
    res_integrated = sorted(np.concatenate(
            (list(set(flatten_reduced(reducer(
        (x, rawf), area, ytol)))),
        [x[0], x[-1]])))
    res = list(set(flatten_reduced(reducer(signal, area, ytol))))

    res = np.concatenate(([x[0]], sorted(res), [x[-1]]))
    yout = [y[np.where(x==i)[0]][0] for i in res]
    youtint = [y[np.where(x==i)[0]][0] for i in res_integrated]

    num_out = len(yout)
    num_in = len(y)
    factor = num_in/num_out

    f, (a1, a2) = plt.subplots(2,1, sharex=True, squeeze=True)
    a1.plot(x, y, 'b.')
    a1.plot(res, yout, 'yo-')
    print("Reduced by {:.1f}: {} -> {}".format(factor, num_in, num_out))
    rawint = cumtrapz(yout, res, initial=0)
    print(rawf[-1]-rawint[-1]) 
    a2.plot(res, cumtrapz(yout, res, initial=0))
    a2.plot(x, cumtrapz(y, x, initial=0))
    #a1.plot(res_integrated, youtint, 'r.-')

    plt.show()
