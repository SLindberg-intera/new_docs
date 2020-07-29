#
#   Example usage script 
#

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
pathwaysFile=$doseFiles'pathways.csv'
copcFile=$doseFiles'tempcopc.csv'
dosefactsFile=$doseFiles'tempdose.csv'
outputFile=$doseFiles'output/'$copc'.csv'


toolsDir='/home/ca/dosecalc/CA-CIE-Tools'
cmd="$toolsDir'/tools/ca-dosecalc/calcDose.sh' $copc $NLay $gridShapefile $ucnFile $soilFile $dosefactsFile $copcFile $pathwaysFile $unitsin $unitsout $conversion $startyear $outputFormat $modeldate $outputFile"



echo "$cmd"

