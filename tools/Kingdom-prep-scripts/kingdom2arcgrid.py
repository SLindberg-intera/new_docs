""" this script converts Kindgom point files of surfaces (geologic
    structure contour tops) to ascii raster file that Leapfrog can load.
    The Kingdom point files are x,y,z with a constant dx and dy 
    and are sent to us by Sarah from CHPRC.

The Leapfrom ASCII raster (grid) file format is (example):
ncols        8500
nrows        120
xllcenter    568255.000000000000
yllcenter    132005.000000000000
cellsize     50.000000000000
NODATA_value  -99999

    MWilliams, Intera 12-12-2016

    Updated by MDWilliams. Intera, 1-25-2017
    Fixed bug - data is written out starting with the UL row and moving down

    Updated and rebamed by MDWilliams, Intera 1/28/2020
    New name is Kingdom2arcgrid.py
    changed xllcorner adn yllcorner to xllcenter and yllcenter

"""
import sys
import numpy as np

nodata = -99999
fnodata = float(nodata)

# two command line arguments: input-kingdom-file output-leapfrog-grid
print(sys.argv[1])
print(sys.argv[2])


# load csv file from kingdom
with open(sys.argv[1],"r") as fi:
	kingall = fi.read()

kinglines=kingall.split("\n")  # separate out lines into array
klen=len(kinglines)

# Points from Kingdom can come in irregular order or inconsistent rows
# and columns.  Scan file first to build max rectangular domain
xd = dict()
yd = dict()

for pline in kinglines[0:klen-1]:
	sxyz = pline.split(",")
	fx = float(sxyz[0])
	fy = float(sxyz[1])
	fz = float(sxyz[2])
	xd[fx] = 1
	yd[fy] = 1

# sort keys
nx=0
xl=[fnodata] * len(xd)
for fx in sorted(xd):
	xd[fx]=nx
	xl[nx]=fx
	nx+=1

ny=0
yl=[fnodata] * len(yd)
for fy in sorted(yd):
	yd[fy]=ny
	yl[ny]=fy
	ny+=1

print("nx,ny=",nx,ny)
zsize = nx*ny
z = []
for i in range(zsize):
	z.append(fnodata)
print("zlen=",len(z))
for pline in kinglines[0:klen-1]:
	sxyz = pline.split(",")
	fx = float(sxyz[0])
	fy = float(sxyz[1])
	fz = float(sxyz[2])
	i = xd[fx]
	j = yd[fy]
	zptr = (nx*j) + i
#	print("zptr=",zptr,i,j)
	z[zptr] = fz

# write out ASCII raster file for leapfrog
with open(sys.argv[2],"w") as fo:
	fo.write("ncols        %d\n" % nx)
	fo.write("nrows        %d\n" % ny)
	fo.write("xllcenter    %f\n" % xl[0])
	fo.write("yllcenter    %f\n" % yl[0])
	fo.write("cellsize     %f\n" % (xl[1]-xl[0]))
	fo.write("NODATA_value ");
	fo.write("%d\n" % nodata)
	# Patch - reversed order (jmax first) - mdw 1/25/2017
	# for j in range(ny):
	for j in reversed(range(ny)):
		for i in range(nx):
			zptr = (nx*j) + i
			if z[zptr] == fnodata:
				fo.write("%d " % nodata)
			else:
				fo.write("%f " % z[zptr])
		fo.write("\n")
		
