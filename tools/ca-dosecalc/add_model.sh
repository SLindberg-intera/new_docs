startyear=$1
modeldate=$2
modelname=$3

psql testcapython -qtA -c "insert into models (mdl_id, mdl_nm, mdl_ver, mdl_sub_ver, mdl_desc, mdl_exec_tm, mdl_start_yr, mdl_srid) values (1, '$modelname', 1, 1, '$modelname', '$modeldate', '$startyear', 4326);"
d=$(date)
echo "$d: Created model '$modelname' with start year '$startyear'."
