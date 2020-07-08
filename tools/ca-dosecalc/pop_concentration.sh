# these should be parameters to this script
fname='/home/ca/dosecalc/source/testConc/tc99/P2RGWM.ucn'
copcnm='Tc99'
minthresh='1e-6'
model='test'
mcl=1
contamtype='rad'
dbase='testcapython'
unit='pCi/m^3'

d=$(date)
echo "starting at $d"

# obtain the model id for the given model name
mdlid=$(psql -d "$dbase" -qtA -c "select mdl_id from public.models where mdl_nm='$model';")

# obtain the unit id for the units
unitid=$(psql -d "$dbase" -qtA -c "select unit_id from public.units where unit_in='$unit';")

# obtain the layer indicies
layersArr=$(psql -d "$dbase" -qtA -c "select array_agg(lay) from (select distinct lay from cells where mdl_id=$mdlid) a;")
layers=$(echo "$layersArr" | sed 's/,/ /g' | sed 's/{//g' | sed 's/}//g')

# remove elements in the copc table (cascades to concentrations)
rval=$(psql -d "$dbase" -qtA -c "delete from copc where contam_nm='$copcnm' and mdl_id=$mdlid;")

# add the COPC
rval=$(psql -d "$dbase" -qtA -c "insert into copc (mdl_id, contam_nm, mcl, unit_id, min_thresh, contam_type)  values ($mdlid, '$copcnm', $mcl, $unitid, $minthresh, '$contamtype');")

# remove elements in the ucn staging table
rval=$(psql -d "$dbase" -qtA -c "truncate stg_ucn;")

for lay in $layers
do
  # load UCN file into ucn staging table one layer at a time
  rval=$(psql -d "$dbase" -qtA -c "select icf_ucn_get('$fname', $mdlid, '$copcnm', $lay);")
  echo "moved layer $lay of $fname into staging."
done

# load all ucn data into the concentrations table
rval=$(psql -d "$dbase" -qtA -c "select icf_ucn_load();")

d=$(date)
echo "end at $d; Loaded concentration table for $fname"

