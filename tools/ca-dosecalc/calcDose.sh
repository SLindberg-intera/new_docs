#!/bin/bash
NLay=7
gridShapefile='/home/ca/dosecalc/source/MFGRID/v8.3/data/grid_274_geo.shp'
soilFile='/home/ca/dosecalc/source/SOILIND/v1.0/data/mfgrid_soil_indices.csv'
ucnFile='/home/ca/dosecalc/source/testConc/u235/P2RGWM.ucn'
copc='U235'
unitsin='pCi/m^3'
unitsout='pCi/L'
conversion='1'
startyear='1944'
modeldate='2020-07-13'
outputFormat='9.99999999EEEE'

doseFiles='/home/ca/dosecalc/dev/fakeDoseFactorData/'
pathways=$doseFiles'pathways.csv'
copcFile=$doseFiles'tempcopc.csv'
dosefactsFile=$doseFiles'tempdose.csv'
outputFile=$doseFiles'output/'$copc'.csv'


# this constitutes a model run
mdl=$copc
dbase='dosecalc'$copc
toolsdir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
$toolsdir/setupdb.sh $dbase
$toolsdir/add_model.sh $dbase $startyear $modeldate $mdl
$toolsdir/load_units.sh $dbase $conversion $unitsin $unitsout
$toolsdir/shapefile_loader.sh -d $dbase -f $gridShapefile -m $mdl
$toolsdir/populate_cells.sh -m $mdl -l $NLay -d $dbase
$toolsdir/load_soils.sh -f $soilFile -d "$dbase" -m $mdl
$toolsdir/pop_dose_factors.sh $dbase $pathways $copcFile $dosefactsFile
$toolsdir/pop_concentration.sh -f $ucnFile -c $copc -m $mdl -d $dbase -u $unitsin 
$toolsdir/pop_views.sh $dbase
$toolsdir/output_dose.sh $dbase $copc $outputFormat $outputFile

