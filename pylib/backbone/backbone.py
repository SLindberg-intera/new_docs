"""
utility to help traverse the ICF blockchain with Python

"""
import sys
import json
import os
import versions


HASH = 'Hash'
INHERITANCE = 'Inheritance'
DEVELOPMENT = 'Development'
DEVELOPMENT_PATH = os.path.join("S:\\", "PSC","!HANFORD","ICF", "TEST")

def get_dirs(start_path):
    """ get a list of the directories in a path"""
    return list(a[0] for a in os.walk(start_path))

class Connection:
    """
        a connection between two nodes.  Useful in building
        a force diagram in D3
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
    """ represents a block in the blockchain """
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
            for path in d[INHERITANCE]:
                p.append(cls.from_path(path))

            return cls(filepath, d[HASH], p)

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


class WorkProductVersion:
    """
        Represents a particular version of a work product.

        This corresponds to an commited ICF work product.

    """
    def __init__(self, path):
        self.path = path

    @property
    def version_number(self):
        pass

    @property
    def block(self):
        """ obtain a Block instance from this version """
        return Block.from_path(
                os.path.join(self.path, "meta", "icfblock.block") 
                )
    

class WorkProduct:
    """
        Represents an ICF Work Product.  This is a class of work
        performed as part of the CA or CIE;

        Actual ICF work products correspond to WorkProductVersion
        instances.  This class represents the collection of work
        product verions

        
        sketching this out for now;
        problably should move to another module


    """
    def __init__(self, key, root=DEVELOPMENT_PATH):
        self.key = key

    @property
    def versions(self, ):
        raise NotImplemented()

    @property
    def most_recent_version(self, ):
        raise NotImplemented()

    @property
    def path(self):
        return os.path.join(DEVELOPMENT_PATH, self.key)


if __name__ == "__main__":
    try:
        blockpath = sys.argv[1]
        block = Block.from_path(blockpath)
        print("Nodes", block.nodes)
        print("Connections", ", ".join(map(str, block.connections)))
    except IndexError:
        pass
