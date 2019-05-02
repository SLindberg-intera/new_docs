import unittest
from . import info

class TestInfo(unittest.TestCase):
    def setUp(self):
        self.info = info.Info()

    def test_machine(self):
        self.assertTrue(
                len(self.info.machine)>0)
    def test_uname(self):
        self.assertTrue(
                len(self.info.uname)>0)
        
    def test_platform(self):
        self.assertTrue(len(self.info.platform)>0)

    def test_computer(self):
        self.assertTrue(len(self.info.computer)>0)

    def test_start(self):
        self.assertTrue(len(self.info.start)>0)

    def test_now(self):
        self.assertTrue(len(self.info.now)>0)

if __name__ =="__main__":
    unittest.main()
