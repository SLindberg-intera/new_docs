"""

This tool depends on two other modules:

  pylib\fingerprint
  pylib\backbone

"""
import sys, os
import json

from constants import ICF_HOME

try:
    from ..fingerprint import fingerprint
    from ..backbone import blockchain as blockchain
    from ..backbone import backbone

except (ImportError, ValueError):
    reporoot = os.path.abspath(
        os.path.join(os.path.abspath(__file__), '..','..'))
    if reporoot not in sys.path:
        sys.path.append(reporoot)

    from fingerprint import fingerprint
    from backbone import backbone
    from backbone import blockchain 

def parse_input_file(fname):
    """ read the contents from the input file
    """
    return blockchain.get_ancestors_from_file(fname)

def path_to_data_folder(work_product, version, rootdir=ICF_HOME):
    """
        get a path to the data folder
    """
    path = os.path.join(rootdir, work_product, version, backbone.DATA_DIR)
    if (os.path.exists(path)):
        return path
    raise ValueError("Data Path '{}' does not exist".format(path))

def path_to_version_folder(work_product, version, rootdir=ICF_HOME):
    """
        retun oath to the meta folder
    """
    path = os.path.abspath(os.path.join(rootdir, work_product, version))
    if (os.path.exists(path)):
        return path
    raise ValueError("Work Product Path '{}' does not exist".format(path))

def generate_fingerprint_file(work_product, version, outfile):
    """ 

    """
    path = path_to_data_folder(work_product, version)
    s = fingerprint.extract_fingerprints(path)
    fingerprint.to_file(outfile, s)

def extract_total_fingerprint(fingerprint_file):
    """

    """
    with open(fingerprint_file, 'r') as f:
        lines = f.readlines()
        return lines[1].split("\t")[1].strip()


def write_block(block_dict, to_file):
    with open(to_file, 'w') as f:
        f.write(json.dumps(block_dict))

if __name__=="__main__":
    print("Running")
    fname = sys.argv[1]
    outpath = sys.argv[2]
    outfinger = os.path.join(outpath, backbone.FINGER_FILENAME)
    outblock = os.path.join(outpath, backbone.ICF_BLOCK_FILENAME)
    
    print("Parsing input file {}".format(fname))
    target, parents = parse_input_file(fname)

    generate_fingerprint_file(*target, outfinger)
    fingerprint = extract_total_fingerprint(outfinger)
    version_path = path_to_version_folder(*target)
    block = blockchain.make_block(version_path, parents, fingerprint)
    write_block(block, outblock)
