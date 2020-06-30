#! /bin/bash
#--------
#   Create and populate a postgres database
#     'db' is the name of the database
#     stdout gets dumped to 'rep'
# 
#   assumes user is a [postgres] superuser and can
#   create/destroy databases and install extensions
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
db=$1 rep=$2
dropdb $db
createdb $db
psql $db -f $DIR/setup.sql > $rep
psql $db -f $DIR/model_seq.sql >> $rep
#psql $db -f models.sql >> $rep
#psql $db -f copc.sql >> $rep
#psql $db -f pathways.sql >> $rep
#psql $db -f cells.sql >> $rep
#psql $db -f soils.sql >> $rep
#psql $db -f cell_soils.sql >> $rep
#psql $db -f concentrations.sql >> $rep


