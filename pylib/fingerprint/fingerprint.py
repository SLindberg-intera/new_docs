"""
    provides "fingerprints" (hashes) of target files

"""

import hashlib
import os
import argparse
import datetime
import sys

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

def fingerprint_lines(filename, start_line, end_line=None):
    """ gets hash for section start_line to (not including) end_line
    
        if end_line is None, just reutrns the hash of start_line
    """
    if end_line is None:
        end_line = start_line+1

    with open(filename, 'rb') as f:
        lines = f.readlines()
    data = b''.join(lines[start_line: end_line]) 
    hasher = get_hasher()
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
        return
    hasher = get_hasher()
    if not is_dir(target):
        raise FileNotFoundError("Could not find '{}'".format(target))
    for dirpath, dirnames, filenames in os.walk(target):
        for filename in filenames:
            p = os.path.join(dirpath, filename)
            finger_print = fingerprint_file(p)
            hasher.update(finger_print.encode())
            count+=1
            yield [p, fingerprint_file(p)]
            
    yield ["Total for {} files".format(count), hasher.hexdigest()]

SEP = "\t"
def to_file(filename, extract_fingerprints_itr):
    all_items = list(extract_fingerprints_itr)
    with open(filename, 'w') as f:
        f.write("Fingerprint generated at {}\n".format(
            datetime.datetime.now()))
        f.write(SEP.join(all_items[-1]))
        f.write("\n")
        f.write("\n")
        for line in all_items[0:-1]:
            f.write(SEP.join(line))
            f.write("\n")

def setupArgParse():
    pa = argparse.ArgumentParser()
    pa.add_argument("target", 
            type=str,
            help="The target file or directory you would like to fingerprint")
    pa.add_argument("-o", "--output",
            type=str,
            help="The name of the output fingerprint file.  The default is 'fingerprint.txt'",
            default="fingerprint.txt"
            )

    return pa

if __name__=="__main__":
    pa = setupArgParse()
    args = pa.parse_args()
    start = args.target
    outfile = args.output

    s = extract_fingerprints(start)
    to_file(outfile, s)
    

