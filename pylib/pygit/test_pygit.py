import unittest
from . import git

class TestFn_run_command(unittest.TestCase):
    def test_runs_ok(self):
        res = git.run_command("status")
        self.assertTrue(res.startswith("On branch"))

    def test_runs_junk(self):
        with self.assertRaises(ValueError):
            res = git.run_command("garbage fail")

class TestFn_get_version(unittest.TestCase):
    def test_executes(self):
        res = git.get_version()
        self.assertTrue(len(res)>0)

class TestFn_is_clean_master_branch(unittest.TestCase):
    def test_execute(self):
        res = git.is_clean_master_branch()
        self.assertTrue(type(res)==bool)

if __name__ == "__main__":
    unittest.test()

