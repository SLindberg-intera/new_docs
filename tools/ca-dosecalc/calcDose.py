"""
   This is a wrapper.

   it simply calls calcDose.sh and passes any arguments to it

"""

import sys, os

if __name__=="__main__":
    fpath = ".".join([__file__.split(".py")[0], "sh"])
    argv = " ".join(sys.argv[1:])
    os.system(" ".join([fpath, argv]))
    
    
