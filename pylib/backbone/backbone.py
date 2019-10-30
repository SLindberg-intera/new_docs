"""
utilities to help traverse the ICF blockchain with Python


"""
import sys
import json
import os
import versions
import itertools


""" constants used below """
HASH = 'Hash' # key in the blockchain file's JSON object
INHERITANCE = 'Inheritance' # key in the blockchain's JSON object
FINGER_FILENAME = "fingerprint.txt" # the name of the fingerprint files
ICF_BLOCK_FILENAME = "icfblock.block" # the name of the blockchain files
META_DIR = 'meta'  # name of the "meta" directory
DATA_DIR = 'data' # name of the "data" directory

def version_path_to_blockfile(version_path):
    """ given a path to a work product version directory, return
    the path to the icf blockfile """
    return os.path.join(version_path, META_DIR, ICF_BLOCK_FILENAME)

def get_dirs(start_path):
    """ get a list of the directories in a path"""
    return list(a[0] for a in os.walk(start_path))

class Connection:
    """
        a connection between two objects.  Useful in building
        a force diagram in D3

        this relates a source to a target

    """
    def __init__(self, source, target, value=1):
        self.source = source
        self.target = target
        self.value = value

    def __str__(self):
        return "Connection(source={}, target={}, value={})".format(
                self.source, self.target, self.value)
    
    def as_dict():
        return {
          "source":self.source, 
          "target":self.target, "value":self.value}


class Block:
    """ represents a "block" in the blockchain 
    
    
        corresponds to the contents of an ICF_BLOCK_FILENAME file


        the path is the path to the physical ICF blockchain file
    """
    def __init__(self, path, hashkey, inheritance=[]):
        self.path = path
        self.hashkey = hashkey 
        self.inheritance = inheritance 

    @classmethod
    def from_path(cls, filepath):
        """ read a block from the blockchain"""
        with open(filepath, 'r') as f:
            d = json.load(f)
            p = []
            rootpath = os.path.dirname(filepath)
            for path in d[INHERITANCE]:
                path = os.path.abspath(
                        version_path_to_blockfile(
                            os.path.join(rootpath, path) 
                            ))
                p.append(cls.from_path(path))

            return cls(os.path.abspath(filepath), d[HASH], p)

    def __itr_nodes(self,):
        """returns an iterator over nodes
        
        note nodes is not unique because there may be
        multiple references to a node in the chain.

        use self.nodes()  to get a unique list of nodes instead
        """
        yield self.path
        for node in self.inheritance:
            yield from node.__itr_nodes()

    @property        
    def nodes(self):
        """ obtain a list of all the [unique] nodes in the blockchain """
        return list(set(self.__itr_nodes()))

    def __itr_connections(self, ):
        """ returns an iterator over connections"""
        for node in self.inheritance:
            yield Connection(source=self.path, target=node.path)
            yield from node.__itr_connections()

    @property        
    def connections(self):
        """ obtain a list of all the connections in the blockchain """
        return list(self.__itr_connections())

    def __str__(self):
        if(len(self.inheritance)>0):
            return "[{}:{}]".format(self.path,
                    " ".join(map(str, self.inheritance)))
        return "[{}]".format(self.path)    


def get_fingerprint(filepath, sep="\t"):
    """
        read the fingerprint from a valid fingerprint file

    """
    with open(filepath, 'r') as f:
        lines = f.readlines()
    fingerline = lines[1]
    if "Total" not in fingerline:
        raise ValueError("Invalid fingerprint file")
    return fingerline.split(sep)[1]    

def get_version(meta_folder_path):
    """ given a path to a meta folder, get the version number """
    vstr = os.path.split(meta_folder_path)
    return versions.parse_version_str(vstr[-1])

class WorkProducts:
    """
        represents all the work products in an ICF data structure

        path is the directory where these are stored
    """
    def __init__(self, path):
        self.path = path

    @property
    def all(self):
        l = lambda x: WorkProduct(x)
        paths = [os.path.abspath(os.path.join(self.path, i))
                for i in os.listdir(self.path)]
        return list(map(l, paths)) 

    def __iter__(self):
        yield from self.all


class WorkProductVersion:
    """
        Represents a particular version of a work product.

        This corresponds to an commited ICF work product.

        self.path  should be the path to the version directory
            i.e

            /workproduct/
                /v1.2/ <--- this is "path" in constructor 
                    /data
                        [data files go here]
                    /meta
                        [meta files go here, blockchain and fingerprint]
                        

    """
    def __init__(self, path):
        self.path = path

    def __eq__(self, other):
        if (other.fingerprint==self.fingerprint):
            if(other.version_number==self.version_number):
                return True
        return False    

    @property
    def other_versions_path(self):
        """ return path folder containing other versions of this
        work product version
        """
        return os.path.abspath(os.path.join(self.path, ".."))

    @property
    def all_work_products_path(self):
        """return path of folder containing ICF data structure
           (the "work products" directory)
        """
        return os.path.abspath(os.path.join(self.other_versions_path, ".."))

    @property
    def meta_path(self):
        return os.path.join(self.path, META_DIR)
    
    @property
    def data_path(self):
        return os.path.join(self.PATH, DATA_DIR)

    @property
    def fingerprint_path(self):
        return os.path.join(self.meta_path, FINGER_FILENAME)

    @property
    def work_product_path(self):
        wpp, version = os.path.split(self.path)
        return wpp

    @property
    def block_path(self):
        return os.path.join(self.meta_path, ICF_BLOCK_FILENAME)

    @property
    def version_number(self):
        return get_version(self.path)

    @property
    def version_str(self):
        return os.path.split(self.path)[-1]

    @property
    def fingerprint(self):
        return get_fingerprint(self.fingerprint_path)

    @property
    def block(self):
        """ obtain a Block instance from this version """
        return Block.from_path(self.block_path)

    @property
    def work_product_name(self):
        return os.path.split(self.work_product_path)[1]

    @classmethod
    def from_block(cls, block):
        blockpath, blockfile = os.path.split(os.path.abspath(block.path))
        version_path, metadir = os.path.split(blockpath)
        return cls(version_path)

    def get_summary(self, sep=" "):
        block = self.block
        s = []
        for node in block.nodes:
            parent = WorkProductVersion.from_block(Block.from_path(node))
            s.append(sep.join([
                parent.work_product_name, parent.version_str, parent.path
                ]
            ))
        return "\n".join(s)


    @classmethod
    def explain_version(cls, path):
        c = cls(path)
        outstr = "Summary of '{}':\n{}".format(path, c.get_summary('\t'))
        return outstr

    def _get_children_paths(self):
        """
            traverse the directory structure and identify other
            work product versions which reference this one in
            their inheritance.
        """
        all_products_path = self.all_work_products_path
        block_path = self.block.path
        work_products = WorkProducts(all_products_path)
        versions = [[i.path for i in work_product.versions
                    if (block_path in i.block.nodes)]
                for work_product in work_products]

        # remove "this" from the children and make a flat list 
        return list(set(itertools.chain(*
                [i for i in versions if os.path.abspath(self.path)
            not in i]
                )))
    @property
    def children(self):
        return [WorkProductVersion(i) for i in self._get_children_paths()]

    @property
    def parents(self):
        items = [WorkProductVersion.from_block(Block.from_path(i))
                for i in self.block.nodes]
        # remove 'self' from the list of parents
        return [i for i in items if i !=self]


class WorkProduct:
    """
        Represents an ICF Work Product.  This is a class of work
        performed as part of the CA or CIE;

        Actual ICF work products correspond to WorkProductVersion
        instances.  This class represents the collection of work
        product verions


    """
    def __init__(self, path):
        if os.path.isdir(path):
            self.path = path
            return
        raise ValueError("'{}' is not a valid path".format(path))

    def __str__(self, ):
        return os.path.split(self.path)[1]

    @property
    def versions(self, ):
        return [WorkProductVersion(
                os.path.abspath(os.path.join(self.path, version)))
                for version in os.listdir(self.path)]

    @property
    def most_recent_version(self, ):
        vlist = [(v.version_number, v) for v in self.versions]
        out = sorted(vlist, key=lambda x: x[0])
        try:
            return out[0][1]
        except IndexError:
            return None

