"""
utility to help traverse the ICF blockchain with Python

"""
import sys
import json


HASH = 'Hash'
INHERITANCE = 'Inheritance'

class Block:
    """ represents a block in the blockchain """
    def __init__(self, hashkey, inheritance=[]):
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

            return cls(d[HASH], p)

    def itr_nodes(self,):
        """returns an iterator over nodes"""
        yield self.hashkey
        for node in self.inheritance:
            yield node.hashkey

    def itr_connections(self, ):
        """ returns an iterator over connections"""
        for node in self.inheritance:
            yield self.hashkey, node.hashkey
            yield from node.itr_connections()

    def __str__(self):
        if(len(self.inheritance)>0):
            return "[{}:{}]".format(self.hashkey,
                    " ".join(map(str, self.inheritance)))
        return "[{}]".format(self.hashkey)    

if __name__ == "__main__":
    blockpath = sys.argv[1]
    block = Block.from_path(blockpath)
    #print(list(block.itr_nodes()))
    print(list(block.itr_connections()))
