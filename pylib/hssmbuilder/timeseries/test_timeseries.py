import sys
import os
sys.path.append(
    os.path.join(os.path.dirname(__file__), '..','..')
)
import pylib.vzreducer.constants as c
import unittest
import numpy as np
from pylib.timeseries import timeseries as ts
from pylib.vzreducer import plots
import matplotlib.pyplot as plt

class TestTimeSeries(unittest.TestCase):
    def setUp(self):
        self.x = np.arange(0, np.pi/2, np.pi/10000.)
        self.y = np.sin(self.x)
        self.r = (np.random.rand(len(self.x))-0.5)/13
        self.noisy = self.y+self.r

        self.t = ts.TimeSeries(self.x, self.noisy, "dummy", "dummy")

    def test_integrate(self):
        mass = self.t.integrate()
        self.assertTrue(1-mass.values[-1]<1e-4)

    def test_get_peaks(self):
        peaks,_ = self.t.get_peaks()
        self.assertTrue(peaks)


    #def test_run(self):
    #    filtered = self.t.smooth()
    #    self.assertTrue(len(filtered.times)==len(self.x))

  #  def test_residual_plot(self):
   #     residual = self.t.get_residual()
    #    try:
     #       os.remove("temp.png")
      #  except FileNotFoundError:
       #     pass
        #plots.residual_plot(residual, 'temp.png', show=True)
        ##elf.assertTrue(os.path.exists("temp.png"))
        #os.remove("temp.png")

        
if __name__=="__main__":
    unittest.main()
