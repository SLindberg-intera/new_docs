import os
import datetime
import hashlib

try:
    from backbone import backbone
except ImportError:
    import backbone

def compute_hash(instr):
    f = hashlib.sha256()
    f.update(instr.encode())
    return f.hexdigest()

def itr_inheritance(version_path, inheritance_list):
    """
        for each element of an inheritance list,
        construct the corresponding work product
    """
    for parent_product, parent_version in inheritance_list:
        path = os.path.join(version_path, "..", "..")
        parentpath = os.path.join(path, parent_product, parent_version)
        try:
            # can we create a block?
            parent = backbone.WorkProductVersion(parentpath).block
        except Exception as e:    
            raise ValueError(
                    "Invalid Blockchain.  "
                    "Could not resolve block at '{}'".format(parentpath))
        yield {
                'path':os.path.join("..", "..", "..",parent_product,
                    parent_version, 
                    backbone.META_DIR, backbone.ICF_BLOCK_FILENAME),
                'hashkey': parent.hashkey
                }

def make_block(version_path, inheritance_list, fingerprint):
    """ make a block in the blockchain 
    
        must supply a fingerprint
    """
    ancestors = list(itr_inheritance(version_path, inheritance_list))
    inheritance_hash_str = "".join([item['hashkey'] for item in ancestors])
    inheritance = [item["path"] for item in ancestors]
    if(inheritance_hash_str ==""):
        total_hash_str = fingerprint
    else:
        hash_str = "".join([fingerprint, inheritance_hash_str])
        total_hash_str = compute_hash(hash_str)

    return {
            backbone.HASH: total_hash_str,
            backbone.INHERITANCE: inheritance,
            backbone.TIMESTAMP: str(datetime.datetime.now())
            }

def as_path(work_product, version, path_to_icf_test=""):
    """ create a path of the form used inthe icf blockchain"""
    return os.path.join(path_to_icf_test, work_product, version)


def get_ancestors_from_file(infile, sep=","):
    """
        infile is a path to a blockchain input file (used
        by the QA officer to create the blockchain)

        The file is assumed to be of the form of
           # these are comments.  Anything beyond first two
           #  columns are ignored

           # blank lines are ignored
           work Product, version,  # this is a header
           
           # for the target/Daughter work product:
           WorkProduct,version 
           # for each ancestor of WorkProduct/Version
           WorkProduct,version

        returns a tuple:
        ([work product, ver] <-- #0 the daughter work product
         [ [work product, ver] <-- #1 a list
                of each ancestor, ordered by work product ]
         )
         
    """
    def itr_inheritance():
        with open(infile, 'r') as f:
            data = f.readlines()
        for ix, line in enumerate(data):
            if line.strip().startswith("#"):
                continue
            if line.strip() == '':
                continue
            if line.strip().lower().startswith("work product,"):
                continue

            yield list(map(lambda x: x.strip(), line.split(sep)[0:2]))
    items = list(itr_inheritance())
    try:
        return (items[0], sorted(items[1:]))
    except IndexError:
        return (items[0], [])

def ancestors_to_relative_blockchain_paths(ancestors):
    """
        for every ancestor in a chain, construct
        the (relative) path that will go in the blockhain
    """
    return [as_path(*ancestor, os.path.join("..",".."))
        for ancestor in ancestors]

