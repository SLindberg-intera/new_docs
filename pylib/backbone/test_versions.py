import unittest
import versions 

class TestVersionStr(unittest.TestCase):
    """
        test the version parser against
        various string combos
    """
    def setUp(self):
        self.f = versions.parse_version_str

    def test_valid_simple(self):
        v1 = self.f("v123")
        v2 = self.f("v124")
        v3 = self.f("v1")
        v4 = self.f("v0")
        self.assertTrue(v2>v1)
        self.assertTrue(v3<v1)
        self.assertTrue(v4<v3)

    def test_valid_decimal(self):
        v1 = self.f("v1.2.3.4", depth_level=4)
        v2 = self.f("v1.2.3.5", depth_level=4)
        v3 = self.f("v2.0.0.0", depth_level=4)
        self.assertTrue(v1<v2)
        self.assertTrue(v2<v3)

    def test_valid_alpha(self):
        v1 = self.f("v1.2.3a")
        v2 = self.f("v1.2.3b")
        v3 = self.f("v2")
        v4 = self.f("v3a.0.0")
        v5 = self.f("v3b.0.0")
        v6 = self.f("v0.0.0")
        self.assertTrue(v1<v2)
        self.assertTrue(v2<v3)
        self.assertTrue(v5>v4)
        self.assertTrue(v5>v3)
        self.assertTrue(v6<v1)
        
    def test_valid_sep(self):
        v1 = self.f("v1_3_3", sep="_")
        v2 = self.f("v2", sep="_")
        v3 = self.f("v1_3a_3", sep="_")
        self.assertTrue(v2>v1)
        self.assertTrue(v3>v1)
        self.assertTrue(v2>v3)

    def test_valid_prefix(self):
        v1 = self.f("p1a2a3", sep="a", prefix="p")
        v2 = self.f("p1a2a4", sep="a", prefix="p")
        self.assertTrue(v2>v1)

if __name__=="__main__":
    unittest.main()
