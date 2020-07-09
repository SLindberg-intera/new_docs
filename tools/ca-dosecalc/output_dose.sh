
dbase='testcapython'
copc='Tc99'
mdlid=1
dFormat='9.99999999999999EEEE'

fout='/home/ca/dosecalc/dev/fakeDoseFactorData/output/'$copc'-'$mdlid'.csv'

d=$(date)
echo "$d: START Export of dose data for '$copc' to '$fout' "
res=$(psql -d "$dbase" -qtA -c "copy (select copc, model_date::date, soil, pathway, cell_row, cell_column, cell_layer, to_char(concentration, '$dFormat') as concentration, dose_factor, to_char(dose, '$dFormat') as dose from mv_dose where mdl_id=$mdlid and copc='$copc' ) to '$fout' delimiter ',' csv header;")
d=$(date)
echo "$d: END"
