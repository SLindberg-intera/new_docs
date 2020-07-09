dbase='testcapython'

echo "START loading views"
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"'/Views'
res=$(psql $dbase -f $DIR/mv_analytes.sql)
res=$(psql $dbase -f $DIR/mv_concentrations.sql)
res=$(psql $dbase -f $DIR/mv_dose.sql)

echo "END loading views"

