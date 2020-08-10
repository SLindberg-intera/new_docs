import flopy as fp
import numpy as np
import sys

input_ucn = sys.argv[1]
thresh = float(sys.argv[2])
output_filename = sys.argv[3]

fname = 'inputs/u236/P2RGWM.ucn'
ucn = fp.utils.binaryfile.UcnFile(input_ucn, precision='double')
times = np.array( ucn.get_times())
""" 
	flopy uses zero-indexing
	we use 1-indexing
"""

allvalues =  ucn.get_alldata() 
cond = allvalues>=thresh
tids, layers, rows, cols = np.where(cond)
conc = allvalues[tids, layers,rows,cols]
# make a big'ol string
out = zip(times[tids], layers+1, rows+1, cols+1, conc)
# write the resultstring to a csvfile
out2 = "\n".join(map(lambda x: ",".join(map(str, x)), out))
with open(output_filename, "w") as f:
    f.write(out2)

