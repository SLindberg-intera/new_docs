import scipy.interpolate as interp
from scipy.integrate import trapz, cumtrapz
from scipy.signal import find_peaks
import numpy as np
import matplotlib.pyplot as plt



def make_line(signal):
    x, y = signal
    line_x = [x[0], x[-1]]
    line_y = [y[0], y[-1]]
    try:
        line = interp.interp1d(line_x, line_y)
        return x, line(x)

    except Exception as e:
        input("exception occurred in make_line line 12 {}".format(e))
        return Exception
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
    
    area = integrate(flat_segment)
    y_seg = flat_segment[1]

    xout = [x[-1]]

    if np.all(
         np.abs(y_seg)<threshold_peak) and area < threshold_area:
        return xout
    peak, xpeak, ypeak = get_first_peak(flat_segment)
    segments = partition(signal, xpeak)
    if segments is None:
        return xout
    try:
        return [reducer(segment, threshold_area, threshold_peak,
            branch0*10+branch)
                for branch, segment in enumerate(segments)
                ]
    except Exception:
        input("exception at return[reducer...]")
        return(Exception)
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
    #ix = np.argmax(y)
    #return ix, x[ix], y[ix]

    peak_indicies, _ = find_peaks(y)
    #SLL--this code was unreachable--commented out lines 75 and 76 above and modified following lines 82-85
    # also need to find valleys
    #valleys = (y-np.max(y))
    valley_indicies, _ = find_peaks(-y)
    p = peak_indicies

    p = set(peak_indicies).union(set(valley_indicies))
    p = sorted(list(p))
    try:
        return p[0], x[p[0]], y[p[0]]
    except IndexError:
        return 0, x[0], y[0]


def make_signal():
    start = 0.01
    end = 2*np.pi
    x = np.arange(start, end, 0.0001)
    y = np.zeros(len(x))
    maxy = 20000
    y[232] = maxy/2
    y[233] = maxy/3
    y[234:237] = maxy
    y[237:10600] = maxy/10

    y[800:900] = maxy/20
    y = 5*np.sin(8*x)*np.sin(x)/x-x+5
    #y=1*np.random.rand(len(y))+y
    return x, y


if __name__ == "__main__":

    signal = make_signal()
    line = make_line(signal)
    x, y = signal
    area = np.std(y)*(x[-1]-x[0])
    #np.max(y)
    ytol = np.std(y)/10.
    #np.max(y)
    
    
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
