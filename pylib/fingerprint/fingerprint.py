"""
    provides "fingerprints" (hashes) of target files

"""

import hashlib
import os
import argparse

BLOCKSIZE = 2**20

def get_hasher():
    return hashlib.sha256()

def fingerprint_file(filename):
    with open(filename, 'rb') as f:
        hasher = get_hasher()
        while True:
            data = f.read(BLOCKSIZE)
            if not data:
                break
            hasher.update(data)
        return hasher.hexdigest()    

def is_file(target):
    return os.path.isfile(target)

def is_dir(target):
    return os.path.isdir(target)

def extract_fingerprints(target):
    count = 0
    if is_file(target):
        yield [target, fingerprint_file(target)]
    hasher = get_hasher()
    for dirpath, dirnames, filenames in os.walk(target):
        for filename in filenames:
            p = os.path.join(dirpath, filename)
            finger_print = fingerprint_file(p)
            hasher.update(finger_print.encode())
            count+=1
            yield [p, fingerprint_file(p)]
    yield ["Total for {} files".format(count), hasher.hexdigest()]

def to_file(filename, extract_fingerprints_itr):
    with open(filename, 'w') as f:
        for title, fprint in extract_fingerprints_itr:
            f.write("\t".join([title, fprint]))
            f.write("\n")

def setupArgParse():
    pa = argparse.ArgumentParser()
    pa.add_argument("target", 
            type=str,
            help="The target file or directory you would like to fingerprint")
    pa.add_argument("output",
            default="fingerprint.txt",
            type=str,
            help="The name of the output fingerprint file.  The default is 'fingerprint.txt'")


    return pa

if __name__=="__main__":
    import sys
    pa = setupArgParse()
    args = pa.parse_args()
    start = args.target
    outfile = args.output

    s = extract_fingerprints(start)
    to_file(outfile, s)
    

