"""
    This module creates directories and files in the process
    of testing.  It should remove all of them but take care not
    to run this script in a directory that is under version 
    control so that the temporary files aren't added to the repository

"""

import unittest
import backbone
import os
import sys
import json

try:
    sys.path.append("pylib\\fingerprint")
    import fingerprint
except Exception as e:
    raise e

"""********** TEST HELPERS *******************"""
START_DIR = os.path.join("ignore", "temp")

KEY = 'HSDB'
KEY2 = 'HSDB2'
version = 'v1.2.3'
version2 = 'v0a'

keydir = os.path.join(START_DIR, KEY)
key2dir = os.path.join(START_DIR, KEY2)
versiondir = os.path.join(keydir, version)
version2dir = os.path.join(key2dir, version2)
datadir = os.path.join(versiondir, 'data')
data2dir = os.path.join(version2dir, 'data')
datafile = os.path.join(datadir, 'test_file.txt')
data2file = os.path.join(data2dir, 'test_file.txt')
metadir = os.path.join(versiondir, 'meta')
meta2dir = os.path.join(version2dir, 'meta')

FILE_CONTENTS = 'HELLO WORLD\n'
""" The above represents a dummy data file.

    don't change the above line; it will change the fingerprint
    that is referenced in the tests
"""


def create_data(filename):
    with open(filename, 'w') as f:
        f.write(FILE_CONTENTS)

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

def make_blockfile(fingerprint, inheritance, outfile):
    d = {"Hash":fingerprint, "Inheritance":inheritance}
    with open(outfile, 'w') as f:
        f.write(json.dumps(d))

FINGERPRINT = "fingerprint.txt"
INHERITANCE1 = []
INHERITANCE2 = [os.path.join("..","..", "..", KEY, version)]
BLOCK1 = os.path.join(metadir, backbone.ICF_BLOCK_FILENAME)
BLOCK2 = os.path.join(meta2dir, backbone.ICF_BLOCK_FILENAME)

def fingerprint_file(finger_file_in, finger_file_out):
    filename = FINGERPRINT
    s = fingerprint.extract_fingerprints(finger_file_in)
    outfile = os.path.join(finger_file_out, filename)
    fingerprint.to_file(outfile, s)

def create_test_data():
    create_path(START_DIR)
    create_path(datadir)
    create_path(data2dir)
    create_path(metadir)
    create_path(meta2dir)
    create_data(datafile)
    create_data(data2file)
    fingerprint_file(datadir, metadir)
    fingerprint_file(data2dir, meta2dir)
    fingerprint = backbone.get_fingerprint(
            os.path.join(metadir, FINGERPRINT))
    fingerprint2 = backbone.get_fingerprint(
            os.path.join(meta2dir, FINGERPRINT))
    
    make_blockfile(fingerprint, INHERITANCE1, BLOCK1)
    make_blockfile(fingerprint2, INHERITANCE2, BLOCK2)

def destroy_test_data():
    os.remove(datafile)
    os.remove(data2file)
    os.remove(os.path.join(metadir, FINGERPRINT))
    os.remove(os.path.join(meta2dir, FINGERPRINT))
    os.remove(BLOCK1)
    os.remove(BLOCK2)
    remove_path(datadir)
    remove_path(data2dir)
    remove_path(metadir)
    remove_path(meta2dir)
    remove_path(versiondir)
    remove_path(version2dir)
    remove_path(keydir)
    remove_path(key2dir)
    remove_path(START_DIR)


"""***********  Actual Tests **************"""

class TestWorkProductVersion(unittest.TestCase):
    def setUp(self):
        create_test_data()
        self.wp1 = backbone.WorkProductVersion(versiondir)
        self.wp2 = backbone.WorkProductVersion(version2dir)
    
    def tearDown(self):
        #destroy_test_data()
        pass

    def test_setUp(self):
        self.assertTrue(os.path.isdir(metadir))
        self.assertTrue(os.path.isdir(datadir))

    def test_fingerprint(self):
        f = backbone.get_fingerprint(os.path.join(metadir, FINGERPRINT))
        self.assertTrue("56c2988" in f)

    def test_get_version(self):
        v1 = backbone.get_version(versiondir)
        v2 = backbone.get_version(version2dir)
        self.assertTrue(v1>v2)

    def test_version_number(self):
        v = backbone.get_version(versiondir)
        v2 = self.wp1.version_number
        self.assertEqual(v, v2)

    def test_version_str(self):
        v = self.wp1.version_str
        self.assertEqual(v, version)
        v2 = self.wp2.version_str
        self.assertEqual(v2, version2)

    def test_fingerprint(self):
        f1 = self.wp1.fingerprint
        f2 = self.wp2.fingerprint
        self.assertEqual(f1, f2)

    def test_block(self):
        """ can we get the related Block object and is it 
        connected correctly """
        block = self.wp1.block
        self.assertEqual(len(block.nodes), 1)
        self.assertEqual(len(block.connections), 0)
        block2 = self.wp2.block
        self.assertEqual(len(block2.nodes), 2)
        self.assertEqual(len(block2.connections), 1)
        

if __name__=="__main__":
    unittest.main()
