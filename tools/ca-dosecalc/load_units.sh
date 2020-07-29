dbase=$1
conversion=$2
unitin=$3
unitout=$4

rval=$(psql -d "$dbase" -qtA -c "insert into units (unit_in, unit_out, conversion_factor) values ('$unitin', '$unitout', $conversion);")
d=$(date)
echo "$d: unit: '$unitout = $conversion * $unitin"
