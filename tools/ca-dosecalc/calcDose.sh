#!/bin/bash

# Set help/usage message
usage="
$(basename "$0") [-h] copc NLay gridShapefile ucnFile soilFile dosefactsFile copcFile pathwaysFile unitsin unitsout conversion startyear outputFormat modelDate outputFile

Program that computes the dose for every node in a UCN file

where :
   -h  show this help message
   1. copc  the target copc in copcFile that corresponds to the ucnFile
   2. NLay  the number of layers in the UCN file
   3. gridShapefile   path to the shapefile containing the MODFLOW grid
   4. ucnFile    path to the UCN (concentrations) file
   5. soilFile   path to csv that relates soil types to row, col    
   6. dosefactsFile   path to the csv containing the dose factors
   7. copcFile  path to a csv defining the copcs
   8. pathwaysFile  path to csv containing the pathways
   9. unitsin   typically 'piCi/m^3'; units of the concentration in ucnFile
   10. unitsout  typically 'piCi/L'; units needed to multiply the dose factor
   11. conversion   defined as: unitsout = conversion * unitsin
   12. startyear   the beginning year of the first timestep in the model
   13. outputFormat  defines the precision of the output.  '9.99999999
   14. modeldate   (not used) today's date in format 'yyyy-mm-dd'

   15. outputFile   path to file to write results

"

NLay=$2
gridShapefile=$3
soilFile=$5
ucnFile=$4
copc=$1
unitsin=$9
unitsout=${10}
conversion=${11}
startyear=${12}
modeldate=${14}
outputFormat=${13}
pathwaysFile=$8
copcFile=$7
dosefactsFile=$6
outputFile=${15}


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
$toolsdir/pop_dose_factors.sh $dbase $pathwaysFile $copcFile $dosefactsFile
$toolsdir/pop_concentration.sh -f $ucnFile -c $copc -m $mdl -d $dbase -u $unitsin 
$toolsdir/pop_views.sh $dbase
$toolsdir/output_dose.sh $dbase $copc $outputFormat $outputFile

