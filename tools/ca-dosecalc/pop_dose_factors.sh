# Populates the dose_factors table
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
res=$(psql -d "$dbase" -qtA -c "create unlogged table stg_dosefacts ("'"'"SOIL_INDEX"'"'" int, "'"'"SOIL_CATEGORY"'"'" varchar(100), "'"'"COPC"'"'" varchar(100), "'"'"Pathway"'"'" varchar(100), "'"'"Dose Factor"'"'" float8);")
res=$(psql -d "$dbase" -qtA -c "copy stg_dosefacts ("'"'"SOIL_INDEX"'"'" , "'"'"SOIL_CATEGORY"'"'" , "'"'"COPC"'"'" , "'"'"Pathway"'"'" , "'"'"Dose Factor"'"'") from '$fname' with CSV HEADER;")

res=$(psql -d "$dbase" -qtA -c "insert into dose_factors (soil_id, contam_nm, contam_mdl_id, pathway_nm, dose_factor) select "'"'"SOIL_INDEX"'"'" AS soil_id, "'"'"COPC"'"'" as contam_nm, 1 as contam_mdl_id, "'"'"Pathway"'"'" as pathway_nm, "'"'"Dose Factor"'"'" as dose_factor from stg_dosefacts where stg_dosefacts."'"'"Dose Factor"'"'">1e-12;")

#soil_id, contam_mdl_id, pathway_nm, contam_nm, dose_factor, pathway_mdl_id

d=$(date)
echo "$d: Loaded pathways from '$2'"
echo "$d: Loaded copcs from '$3'"
echo "$d: Loaded dose factors from '$4'"
