import unittest
import numpy as np
from . import timeseries as ts
import matplotlib.pyplot as plt

class TestTimeSeries(unittest.TestCase):
    def setUp(self):
        self.x = np.arange(0, 2*np.pi, np.pi/200.)
        self.y = np.sin(self.x)
        self.r = (np.random.rand(len(self.x))-0.5)/13
        self.noisy = self.y+self.r

        self.t = ts.TimeSeries(self.x, self.noisy, "dummy", "dummy")

    def test_run(self):
        filtered = self.t.smooth()
        #plt.plot(self.t.times, self.t.values)
        #plt.plot(filtered.times, filtered.values, 'r')
        #plt.show()
        self.assertTrue(len(filtered.times)==len(self.x))

    def test_residual(self):
        residual = ts.Residual(self.t)
        plt.plot(residual.errors.times, residual.errors.values)
        plt.plot(
                residual.errors.times, 
                residual.errors.values*0+residual.error_mean)
        plt.show()
        


if __name__=="__main__":
    unittest.main()
