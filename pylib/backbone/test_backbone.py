"""
    This module creates directories and files in the process
    of testing.  It should remove all of them but take care not
    to run this script in a directory that is under version 
    control so that the temporary files aren't added to the repository

"""

import unittest
import backbone

import os

START_DIR = os.path.join("ignore", "temp")

KEY = 'HSDB'
version = 'v1.2.3'

keydir = os.path.join(START_DIR, KEY)
versiondir = os.path.join(keydir, version)
datadir = os.path.join(versiondir, 'data')
datafile = os.path.join(datadir, 'test_file.txt')
metadir = os.path.join(versiondir, 'meta')


def create_data():
    with open(datafile, 'w') as f:
        f.write("hello world")

def create_path(pathname):
    try:
        os.makedirs(pathname)
    except FileExistsError:
        pass

def remove_path(pathname):
    try:
        os.rmdir(pathname)
    except Exception as e:
        raise e


class TestBackbone(unittest.TestCase):
    def setUp(self):
        create_path(START_DIR)
        create_path(datadir)
        create_path(metadir)
        create_data()
    
    def tearDown(self):
        os.remove(datafile)
        remove_path(datadir)
        remove_path(metadir)
        remove_path(versiondir)
        remove_path(keydir)
        remove_path(START_DIR)

    def test_setUp(self):
        self.assertTrue(os.path.isdir(metadir))
        self.assertTrue(os.path.isdir(datadir))

    

if __name__=="__main__":
    unittest.main()
