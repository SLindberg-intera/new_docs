#!/bin/bash

# A shell script to load a shapefile into the ICF database
# Written by: 
#    Josh Kidder, ~ june 2019
# Adopted for CA: 
#    K. Smith July 2020
# -------------------------------------------------------
# Set help/usage message
usage="
$(basename "$0") [-h] [-p] -d database -f file -m model

A shell script to load a shapefile into the ICF database
This script requires the shp2pgsql tool to run, see here
for installing

where :
     -h  show this help message
     -p  persist the staging table in the database
     -f  the name of the shapefile to load (must end in .shp)
     -d  the name of the target database
     -m  the model name to associate the shapefile to
"

# Check if machine has the shp2pgsql tool installed
shpxsts=$(shp2pgsql | grep RELEASE)
if [[ $shpxsts != "RELEASE"* ]]; then
  printf "missing shp2pgsql" >&2
  echo "$usage" >&2
  exit 1
fi

if [[ -z "$PGPASSFILE" ]]; then
  PGPASSFILE=$(pwd)/.pgpass
fi

# Get command line arguments
tkeep=1
while getopts 'hpf:d:s:m:' opt; do
  case "${opt}" in
    h)  echo "$usage" >&2
        exit;;
    p)  tkeep=0;;
    f)  fname=$OPTARG;;
    m)  model=$OPTARG;;
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

echo "Staging shapefile ....."

# Get name and path from filename argument
# Replace \ folder delims with /
if [[ $fname == *"\\"* ]]; then
  fname=$(echo "$fname" | sed 's/\\/\//g')
fi
# Check for full path or just filename
if [[ $fname == *"/"* ]]; then
  # Get full path and name of file
  fpath=$(realpath "$fname" | rev | cut -d/ -f2- | rev)
  fname=$(realpath "$fname" | rev | cut -d/ -f1 | rev)
else
  # Find file and then get full path and name of file
  # Check count of files found with name and error if not one
  fcnt=$(find / -type f -name "$fname" 2>&1 | grep -v "Permission denied" | wc -l)
  if [[ $fcnt == 1 ]]; then
    fname=$(find / -type f -name "$fname" 2>&1 | grep -v "Permission denied" | rev | cut -d/ -f1 | rev)
    fpath=$(find / -type f -name "$fname" 2>&1 | grep -v "Permission denied" | rev | cut -d/ -f2- | rev)
  else
    printf "\nERROR: "$fcnt" files found, provide full url of file!\n" >&2
    exit 1
  fi
fi


# Check for the shapefile's projection file
srid=0
fprj=$(echo "$fname" | sed 's/.shp/.prj/')
fcnt=$(find / -type f -name "$fpath"/*.prj 2>&1 | grep -v "Permission denied" | wc -l)
if [[ $fcnt == 1 ]]; then
  prj=$(head -c 100 "$fpath"/"$fprj")
  echo "Prj $prj"
  srid=$(psql -d "$dbase" -qtA -c "select srid from spatial_ref_sys where srtext like '$prj%';")
fi


# Get model id for model
mdlid=-1
#mdlid=$(psql -d "$dbase" -qtA -c "select mdl_id from public.models where mdl_nm||'-ver'||mdl_ver||'.'||mdl_sub_ver = '"$model"';")
mdlid=$(psql -d "$dbase" -qtA -c "select mdl_id from public.models where mdl_nm='$model'";)
if [[ $mdlid == -1 ]]; then
  echo "ERROR - model not found!"
  exit 1
fi

echo "mdlid ----  $mdlid"
# Import shapefile
tname=$(echo "stg_shp_"$fname | sed '$s/\.shp//')
srid=32149
shp2pgsql -s "$srid" -c "$fpath"/"$fname" public."$tname"_geom | psql -q -d "$dbase"

#shp2pgsql -s "$srid" -G -c "$fpath"/"$fname" public."$tname"_geog | psql -q -d "$dbase"

# Combine staging tables and rename
psql -d "$dbase" -c "alter table public."$tname"_geom add column geog geography;"
#psql -d "$dbase" -c "update public."$tname"_geom d set geog = s.geog from public."$tname"_geog s where d.gid = s.gid;"
#psql -d "$dbase" -c "drop table public."$tname"_geog;"
psql -d "$dbase" -c "alter table public."$tname"_geom rename to "$tname";"


# Create a record in the shapefiles table
echo "Importing shapefile ..."
sfid=-1
sfid=$(psql -d "$dbase" -qtA -c "insert into public.shapefiles (shp_file_nm, shp_file_url, shp_srid) values ('"$fname"', '"$fpath"/"$fname"', $srid) returning shp_file_id;")
#echo "$sfid"
if [[ $sfid == -1 ]]; then
  echo "Error creating shapefiles record!"
  exit 1
fi

# Insert shapefile features into the map_shapes table
rval=-1
rval=$(psql -d "$dbase" -qtA -c "select public.icf_util_map_shapes_load ('"$fname"');")
#echo "$rval"
if [[ "$rval" != "0" ]]; then
  echo "Error inserting into map_shapes!"
  exit 1
fi

# Process shapefile attributes
rval=-1
rval=$(psql -d "$dbase" -qtA -c "select public.icf_util_map_shapes_attributes_load ('"$fname"');")
#echo "$rval"
if [[ "$rval" != "0" ]]; then
  echo "Error inserting into map_shapes_attributes!"
  exit 1
fi

# Create materialized view for shapefile attributes
rval=-1
rval=$(psql -d "$dbase" -qtA -c "select * from public.icf_util_shp_to_mview('"$fname"');")
#echo "$rval"
if [[ $rval != "0" ]]; then
  echo "Error creating materialized view!"
  exit 1
fi

##  update the cells staging table
rval=$(psql -d "$dbase" -qtA -c "truncate stg_cells;")
rval=$(psql -d "$dbase" -qtA -c "insert into stg_cells(new_mdl_id, "col", "row", geom, del_x, del_y) (select $mdlid, A.j as "col", A.i as "row", geom, delx as "del_x", dely as "del_y" from $tname A);")


# Refresh database indexes
rval=-1
rval=$(psql -d "$dbase" -qtA -c "reindex table map_shapes;")
#echo "$rval"
if [[ "$rval" == -1 ]]; then
  echo "Could not refresh map_shapes indexes!"
fi

# Drop or Persist shapefile table
echo "Cleaning up ..........."
if [[ "$tkeep" == 1 ]]; then
  cln=$(psql -d "$dbase" -c "drop table public."$tname" cascade;")
fi

echo "Finished .............."

