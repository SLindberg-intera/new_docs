#!/bin/bash

# -------------------------------------------------------
# Set help/usage message
usage="
$(basename "$0") [-h] -d database -m model

where :
     -h  show this help message
     -d  the name of the target database
     -m  the model name 
"
# Get command line arguments
tkeep=1
while getopts 'h:f:d:m:' opt; do
  case "${opt}" in
    h)  echo "$usage" >&2
        exit;;
    m)  model=$OPTARG;;
    f)  fpath=$OPTARG;;
    d)  dbase=$OPTARG;;
    :)  printf "missing argument for -%s\n" "$OPTARG" >&2
        echo "$usage" >&2
        exit 1;;
    \?) printf "illegal option: -%s\n" "$OPTARG" >&2
        echo "$usage" >&2
        exit 1;;
  esac
done
shift $((OPTIND - 1))

# Get model id for model
mdlid=-1
#mdlid=$(psql -d "$dbase" -qtA -c "select mdl_id from public.models where mdl_nm||'-ver'||mdl_ver||'.'||mdl_sub_ver = '"$model"';")
mdlid=$(psql -d "$dbase" -qtA -c "select mdl_id from public.models where mdl_nm='$model'";)
if [[ $mdlid == -1 ]]; then
  echo "ERROR - model not found!"
  exit 1
fi

# drop staging table
res=$(psql -d "$dbase" -qtA -c "drop table if exists public.stg_soils;")

# create staging table
res=$(psql -d "$dbase" -qtA -c "create table stg_soils ("ID" character varying(80), "ROW" integer,"COL" integer, "SOIL_CATEGORY" character varying(90),"SOIL_INDEX" integer);")

# load data into staging
res=$(psql -d "$dbase" -qtA -c "copy stg_soils from '$fpath' csv header delimiter ',';")

# populate the soil_types table
res=$(psql -d "$dbase" -qtA -c "delete from soil_types where mdl_id=$mdlid;")
res=$(psql -d "$dbase" -qtA -c "insert into soil_types (soil_desc, soil_nm, mdl_id, soil_id) (select distinct soil_category as soil_desc, left(soil_category, 30) as soil_nm, $mdlid as mdl_id, soil_index as soil_id from stg_soils);")

# populate cell_soils
res=$(psql -d "$dbase" -qtA -c "insert into cell_soils (cell_id, soil_id) (select cell_id, soil_id from stg_soils S, soil_types T, cells C where C.row=S.row and C.col=S.col and T.mdl_id=$mdlid and C.mdl_id=$mdlid and T.soil_id=S.soil_index);")

# drop staging table
res=$(psql -d "$dbase" -qtA -c "drop table stg_soils;")
