"""
    provides "fingerprints" (hashes) of target files

"""

import hashlib
import os

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
    if is_file(target):
        yield [target, fingerprint_file(target)]
    hasher = get_hasher()
    for dirpath, dirnames, filenames in os.walk(target):
        for filename in filenames:
            p = os.path.join(dirpath, filename)
            finger_print = fingerprint_file(p)
            hasher.update(finger_print.encode())
            yield [p, fingerprint_file(p)]
    yield ["Total", hasher.hexdigest()]

def to_file(filename, extract_fingerprints_itr):
    with open(filename, 'w') as f:
        for title, fprint in extract_fingerprints_itr:
            f.write("\t".join([title, fprint]))
            f.write("\n")

if __name__=="__main__":
    import sys
    start = sys.argv[1]
    outfile = sys.argv[2]

    s = extract_fingerprints(start)
    to_file(outfile, s)
    

