dbase=$1

d=$(date)
echo "$d: START computing dose"
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"'/Views'
res=$(psql $dbase -f $DIR/mv_analytes.sql)
res=$(psql $dbase -f $DIR/mv_concentrations.sql)
res=$(psql $dbase -c "vacuum analyze;")
res=$(psql $dbase -f $DIR/mv_dose.sql)
d=$(date)
echo "$d: END computing dose"

