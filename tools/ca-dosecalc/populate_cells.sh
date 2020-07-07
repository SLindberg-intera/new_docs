#!/bin/bash

# -------------------------------------------------------
# Set help/usage message
usage="
$(basename "$0") [-h] -l maxlay -d database -m model



where :
     -h  show this help message
     -l  the number of layers (eg 3 means there are lay=1,2,3 layers)
     -d  the name of the target database
     -m  the model name 
"
# Get command line arguments
tkeep=1
while getopts 'h:l:d:m:' opt; do
  case "${opt}" in
    h)  echo "$usage" >&2
        exit;;
    l)  layend=$OPTARG;;
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

# Get model id for model
mdlid=-1
#mdlid=$(psql -d "$dbase" -qtA -c "select mdl_id from public.models where mdl_nm||'-ver'||mdl_ver||'.'||mdl_sub_ver = '"$model"';")
mdlid=$(psql -d "$dbase" -qtA -c "select mdl_id from public.models where mdl_nm='$model'";)
if [[ $mdlid == -1 ]]; then
  echo "ERROR - model not found!"
  exit 1
fi

# delete records with model id (we are going to refresh) 
rval=$(psql -d "$dbase" -qtA -c "delete from cells where mdl_id=$mdlid;")

# for each item in layers, populate cells
for layid in $(eval echo {1..$layend})
do
rval=$(psql -d "$dbase" -qtA -c "insert into cells (lay, mdl_id, row, col, geom, del_x, del_y) (select $layid, new_mdl_id as mdl_id, "row", "col", geom, del_x, del_y from stg_cells where new_mdl_id=$mdlid);")
echo "updated cells: added layer $layid"
done

