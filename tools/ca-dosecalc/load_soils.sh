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
while getopts 'h:d:m:' opt; do
  case "${opt}" in
    h)  echo "$usage" >&2
        exit;;
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

