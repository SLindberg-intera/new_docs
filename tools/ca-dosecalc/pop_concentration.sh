#    -------------
# Loads concentration data from a target .ucn file 
#
# these should be parameters to this script
#    -f='/home/ca/dosecalc/source/testConc/tc99/P2RGWM.ucn'
#    -c='Tc99'
#    -t='1e-6'
#    -m='test'
#    -d='testcapython'
#    -u='pCi/m^3'
# --------------------------

# Set help/usage message
usage="
$(basename "$0") [-h] -d database -m model -f ucnfile -c copc -u unit -t threshold

where :
     -h  show this help message
     -d  the name of the target database
     -m  the model name 
     -f  the full path to the .UCN file to load
     -c  the name of hte copc ('Tc99')
     -u  the unit (usually pCi/m^3 )
     -t  the threshold of 'Zero'
"
# Get command line arguments
tkeep=1
while getopts 'h:f:d:m:c:u:t:' opt; do
  case "${opt}" in
    h)  echo "$usage" >&2
        exit;;
    m)  model=$OPTARG;;
    f)  fname=$OPTARG;;
    d)  dbase=$OPTARG;;
    c)  copcnm=$OPTARG;;
    t)  minthresh=$OPTARG;;
    u)  unit=$OPTARG;;
    :)  printf "missing argument for -%s\n" "$OPTARG" >&2
        echo "$usage" >&2
        exit 1;;
    \?) printf "illegal option: -%s\n" "$OPTARG" >&2
        echo "$usage" >&2
        exit 1;;
  esac
done
shift $((OPTIND - 1))


contamtype='rad' # placeholder; unused in dose calc 
mcl=-1  # placeholder; unused in dose calc 

echo "Loading $copcm from $fname into $dbase:"
d=$(date)
echo "$d: START"

# obtain the model id for the given model name
mdlid=$(psql -d "$dbase" -qtA -c "select mdl_id from public.models where mdl_nm='$model';")

# obtain the unit id for the units
unitid=$(psql -d "$dbase" -qtA -c "select unit_id from public.units where unit_in='$unit';")

# obtain the layer indicies
layersArr=$(psql -d "$dbase" -qtA -c "select array_agg(lay) from (select distinct lay from cells where mdl_id=$mdlid) a;")
layers=$(echo "$layersArr" | sed 's/,/ /g' | sed 's/{//g' | sed 's/}//g')

# remove elements in the copc table (cascades to concentrations)
#rval=$(psql -d "$dbase" -qtA -c "delete from copc where contam_nm='$copcnm' and mdl_id=$mdlid;")

# add the COPC
#rval=$(psql -d "$dbase" -qtA -c "insert into copc (mdl_id, contam_nm, mcl, unit_id, min_thresh, contam_type)  values ($mdlid, '$copcnm', $mcl, $unitid, $minthresh, '$contamtype');")

# remove elements in the ucn staging table
rval=$(psql -d "$dbase" -qtA -c "truncate stg_ucn;")

for lay in $layers
do
  # load UCN file into ucn staging table one layer at a time
  rval=$(psql -d "$dbase" -qtA -c "select icf_ucn_get('$fname', $mdlid, '$copcnm', $lay);")
  d=$(date)
  echo "$d: moved layer $lay into staging."
done

# load all ucn data into the concentrations table
rval=$(psql -d "$dbase" -qtA -c "select icf_ucn_load();")

d=$(date)
echo "$d: END; Loaded concentration table for $fname into $dbase."

