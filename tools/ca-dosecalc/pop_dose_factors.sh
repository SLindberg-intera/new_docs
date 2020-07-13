###  This script is not for QA
#
#   it must be rebuilt to load data from the external dose factors table
#   

dbase=$1

# pop pathways
fname=$2
res=$(psql -d "$dbase" -qtA -c "truncate pathways cascade;")
res=$(psql -d "$dbase" -qtA -c "copy pathways (mdl_id, pathway_nm, pathway_desc) from '$fname' with CSV;")

# pop copc
fname=$3
res=$(psql -d "$dbase" -qtA -c "truncate copc cascade;")
res=$(psql -d "$dbase" -qtA -c "copy copc (mdl_id, contam_nm, contam_long_nm, contam_desc, mcl, unit_id, min_thresh, contam_type) from '$fname' with CSV;")

# pop dose factors
fname=$4
res=$(psql -d "$dbase" -qtA -c "truncate dose_factors cascade;")
res=$(psql -d "$dbase" -qtA -c "copy dose_factors (soil_id, contam_mdl_id, pathway_nm, contam_nm, dose_factor, pathway_mdl_id) from '$fname' with CSV;")

d=$(date)
echo "$d: Loaded pathways from '$2'"
echo "$d: Loaded copcs from '$3'"
echo "$d: Loaded dose factors from '$4'"
