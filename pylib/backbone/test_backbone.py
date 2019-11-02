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
import itertools
import shutil
import blockchain

try:
    sys.path.append("pylib\\fingerprint")
    import fingerprint
except Exception as e:
    raise e

"""********** TEST HELPERS *******************
This section 
    sets up a structure where there are two work products
    (one version each)

    work product 2 references work product 1
    work product 1 references nothing

    work product 1 exits in both TEST and PROD environments

    these files are created on disk along with fingerprints
    and a block chain

"""
HOME_DIR = os.path.join("ignore", "temp", "ICF")
START_DIR = os.path.join(HOME_DIR, "Test")
START_DIR_PROD = os.path.join(HOME_DIR, "Prod")

KEY = 'Work Product 1'
KEY2 = 'Work Product 2'
version = 'v1.2.3'
version2 = 'v0a'
KEY3 = 'Work Product 3'
version3 = 'v1'

keydir = os.path.join(START_DIR, KEY)
keypdir = os.path.join(START_DIR_PROD, KEY)
key2dir = os.path.join(START_DIR, KEY2)
key3dir = os.path.join(START_DIR, KEY3)
versiondir = os.path.join(keydir, version)
version2dir = os.path.join(key2dir, version2)
versionpdir = os.path.join(keypdir, version)
version3dir = os.path.join(key3dir, version3)


datadir = os.path.join(versiondir, 'data')
data2dir = os.path.join(version2dir, 'data')
datafile = os.path.join(datadir, 'test_file.txt')
data2file = os.path.join(data2dir, 'test_file.txt')
metadir = os.path.join(versiondir, 'meta')
meta2dir = os.path.join(version2dir, 'meta')
meta3dir = os.path.join(version3dir, 'meta')
data3dir = os.path.join(version3dir, 'data')
data3file = os.path.join(data3dir, 'test3.txt')
commit_file = os.path.join("ignore", 'temp', 'icf-input.csv')

FILE_CONTENTS = 'HELLO WORLD\n'
""" The above represents a dummy data file associated with a work product.

    don't change the above line; it will change the fingerprint
    that is referenced in the tests
"""
FILE3_CONTENTS = 'HELLO FILE 3\n'

def create_data(filename):
    with open(filename, 'w') as f:
        f.write(FILE_CONTENTS)

def create_path(pathname):
    try:
        os.makedirs(pathname)
    except FileExistsError as e:
        if os.path.isdir(pathname):
            return
        raise e 

def remove_path(pathname):
    try:
        os.rmdir(pathname)
    except Exception as e:
        raise e

def make_blockfile(fingerprint, inheritance, outfile):
    d = {"Hash":fingerprint, "Inheritance":inheritance}
    with open(outfile, 'w') as f:
        f.write(json.dumps(d))

FINGERPRINT = backbone.FINGER_FILENAME 
INHERITANCE1 = []
INHERITANCE2 = [os.path.join("..","..", "..", 
    KEY, version, "meta","icfblock.block")]
BLOCK1 = os.path.join(metadir, backbone.ICF_BLOCK_FILENAME)
BLOCK2 = os.path.join(meta2dir, backbone.ICF_BLOCK_FILENAME)

def fingerprint_file(finger_file_in, finger_file_out):
    filename = FINGERPRINT
    s = fingerprint.extract_fingerprints(finger_file_in)
    outfile = os.path.join(finger_file_out, filename)
    fingerprint.to_file(outfile, s)

def make_commit_input_file(testfile):
    """ example file for building the blockchain"""
    with open(testfile, 'w') as f:
        f.write("#comment\n")
        f.write("\n")
        f.write("work product,version\n")
        f.write(",".join([KEY3, version3])+'\n')
        f.write(",".join([KEY2, version2])+'\n')
        f.write(",".join([KEY, version])+'\n')

def create_test_data():
    make_commit_input_file(commit_file)
    create_path(START_DIR)
    create_path(START_DIR_PROD)
    create_path(datadir)
    create_path(data2dir)
    create_path(metadir)
    create_path(meta2dir)
    create_path(meta3dir)
    create_data(datafile)
    create_data(data2file)
    create_path(data3dir)
    create_data(data3file)
    fingerprint_file(datadir, metadir)
    fingerprint_file(data2dir, meta2dir)
    fingerprint_file(data3dir, meta3dir)
    fingerprint = backbone.get_fingerprint(
            os.path.join(metadir, FINGERPRINT))

    fingerprint2 = backbone.get_fingerprint(
            os.path.join(meta2dir, FINGERPRINT))
    
    make_blockfile(fingerprint, INHERITANCE1, BLOCK1)
    make_blockfile(fingerprint2, INHERITANCE2, BLOCK2)
    try:
        shutil.copytree(versiondir, versionpdir)
    except FileExistsError:
        pass

def destroy_test_data():
    return
    os.remove(datafile)
    os.remove(data2file)
    os.remove(data3file)
    os.remove(os.path.join(metadir, FINGERPRINT))
    os.remove(os.path.join(meta2dir, FINGERPRINT))
    os.remove(os.path.join(meta3dir, FINGERPRINT))
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
    remove_path(data3dir)
    remove_path(meta3dir)
    remove_path(version3dir)
    shutil.rmtree(START_DIR_PROD)
    shutil.rmtree(START_DIR)


"""***********  Actual Tests **************"""

class TestWorkProductVersion(unittest.TestCase):
    def setUp(self):
        create_test_data()
        self.wp1 = backbone.WorkProductVersion(versiondir)
        self.wp2 = backbone.WorkProductVersion(version2dir)
    
    def test_QA_status(self):
        self.assertEqual(self.wp2.qa_status, backbone.TEST)
        self.assertEqual(self.wp1.qa_status, backbone.PROD) 

    def tearDown(self):
        destroy_test_data()
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
        
    def test_from_block(self):
        block = self.wp1.block
        wp3 = backbone.WorkProductVersion.from_block(block)
        self.assertEqual(wp3, self.wp1)
        self.assertNotEqual(wp3, self.wp2)

    def test_work_product_name(self):
        wp1 = self.wp1.work_product_name
        wp2 = self.wp2.work_product_name
        self.assertEqual(wp1, KEY)
        self.assertEqual(wp2, KEY2)

    def test_summary(self):
        summary = self.wp2.get_summary()
        self.assertTrue( KEY in summary)
        self.assertTrue( KEY2 in summary)
        self.assertTrue(self.wp2.path in summary)
        self.assertTrue(self.wp1.path in summary)

        summary = self.wp1.get_summary()
        self.assertTrue(self.wp1.path in summary)
        self.assertFalse(self.wp2.path in summary)

    def test_explain_version(self):
        e1 = backbone.WorkProductVersion.explain_version(versiondir)
        e2 = backbone.WorkProductVersion.explain_version(version2dir)
        self.assertTrue("Summary of" in e1)

    def test_get_children_paths(self):
        """
        wp1 should have 1 child (wp2)
        wp2 should have no children
        """
        self.assertTrue(len(self.wp2._get_children_paths())==0)
        self.assertTrue(len(self.wp1._get_children_paths())==1)
        self.assertTrue(
                self.wp1._get_children_paths()[0]  
                    ==os.path.abspath(self.wp2.path)
        )

    def test_children(self):
        """ same as _get_children_paths except class instances """
        p = self.wp1.children
        self.assertTrue(p[0]==self.wp2)
        p2 = self.wp2.children
        self.assertTrue(p2==[])
    
    def test_parents(self):
        """
        wp1 should have no parents
        wp2 should have one parent (wp1)
        """
        p2 = self.wp2.parents
        p1 = self.wp1.parents
        self.assertTrue(len(p1)==0)
        self.assertTrue(len(p2)==1)
        self.assertTrue(p2[0]==self.wp1)

    def test_WorkProduct(self):
        wps = backbone.WorkProducts(self.wp1.all_work_products_path)
        versions = [wp.most_recent_version for wp in wps]
        self.assertTrue(v in [self.wp1, self.wp2] for v in versions)
   
class TestBlockchain(unittest.TestCase):
    def setUp(self):
        create_test_data()
        self.wp1 = backbone.WorkProductVersion(versiondir)
        self.wp2 = backbone.WorkProductVersion(version2dir)
        self.input_file = commit_file

    def test_get_ancestors_from_file(self):
        """
            file should be read successfully and output
            should be of form [work product, version]

        """
        p, raw = blockchain.get_ancestors_from_file(self.input_file)
        self.assertEqual(raw[0][0], KEY)
        self.assertEqual(raw[1][0], KEY2)
        self.assertEqual(raw[0][1], version)
        self.assertEqual(raw[1][1], version2)

    def test_as_path(self):
        p, raw = blockchain.get_ancestors_from_file(self.input_file)
        paths = [blockchain.as_path(*item, START_DIR) for item in raw]

    def test_make_block(self):
        """
            when there are ancestors, inheritance should reflect
            that and there should be a hash that is not equal to the
            input hash, because of the addition of the inheritance
        """
        p, raw = blockchain.get_ancestors_from_file(self.input_file)
        paths = blockchain.ancestors_to_relative_blockchain_paths(raw)
        contents = blockchain.make_block(
                os.path.abspath(version3dir), raw, '')
        self.assertEqual(len(contents['Inheritance']), 2)
        self.assertTrue(KEY in contents['Inheritance'][0])
        self.assertTrue(KEY2 in contents['Inheritance'][1])
        self.assertNotEqual(contents['Hash'], '')

    def test_make_block_no_ancestors(self):
        """
            when there are no ancestors, there should
            be no inheritance and hash should equal
            the input hash

        """
        contents = blockchain.make_block(
                os.path.abspath(version3dir), [], 'test')
        self.assertEqual(contents['Inheritance'], [])
        self.assertEqual(contents['Hash'], 'test')

    def tearDown(self):
        destroy_test_data()


if __name__=="__main__":
    unittest.main()
