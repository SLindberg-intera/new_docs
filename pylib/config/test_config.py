import unittest
import config
import json
import os

TEST_CONFIG_PATH = os.path.join(os.path.abspath(
    os.path.dirname(__file__)), "test", "test_config.json")

class TestConfig(unittest.TestCase):
    def test_read_config(self):
        c = config.read_config(TEST_CONFIG_PATH)
        self.assertEqual(c["Test Key"], "test value")

if __name__ == "__main__":
    unittest.main()
