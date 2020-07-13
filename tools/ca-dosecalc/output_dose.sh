dbase=$1
copc=$2
dFormat=$3
fout=$4

mdlid=1
d=$(date)
echo "$d: START Export of dose data for '$copc' to '$fout' "
res=$(psql -d "$dbase" -qtA -c "copy (select model_date::date, soil, pathway, cell_row, cell_column, cell_layer, to_char(concentration, '$dFormat') as concentration, dose_factor, to_char(dose, '$dFormat') as dose from mv_dose where mdl_id=$mdlid and copc='$copc' ) to '$fout' delimiter ',' csv header;")
d=$(date)
echo "$d: END Export of dose data."
