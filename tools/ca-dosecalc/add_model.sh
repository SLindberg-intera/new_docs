dbase=$1
startyear=$2
modeldate=$3
modelname=$4

psql $dbase -qtA -c "insert into models (mdl_id, mdl_nm, mdl_ver, mdl_sub_ver, mdl_desc, mdl_exec_tm, mdl_start_yr, mdl_srid) values (1, '$modelname', 1, 1, '$modelname', '$modeldate', '$startyear', 4326);"
d=$(date)
echo "$d: Created model '$modelname' with start year '$startyear'."
