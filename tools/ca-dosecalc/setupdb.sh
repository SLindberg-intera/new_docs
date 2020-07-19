#! /bin/bash
#--------
#   Create and populate a postgres database
#     'db' is the name of the database
#     stdout gets dumped to 'rep'
# 
#   assumes user is a [postgres] superuser and can
#   create/destroy databases and install extensions
echo "START setupdb"
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
db=$1 
d=$(date)
echo "$d: START setup database"
dropdb $db 
createdb $db
res=$(psql $db -qAt -f $DIR/setup.sql)
echo "Created Postgres Database with PostGIS extensions"
#psql $db -f $DIR/setup.sql > $rep
#    Sequences (used as primary keys) 
res=$(psql -d $db -qtA -f $DIR/Sequences/model_mdl_id_seq.sql)
res=$(psql -d $db -qtA -f $DIR/Sequences/concentration_bucket_bkt_id_seq.sql)
res=$(psql $db -qtA -f $DIR/Sequences/grid_grid_id_seq.sql)
res=$(psql $db -qtA -f $DIR/Sequences/map_shape_shp_id_seq.sql)
res=$(psql $db -qtA -f $DIR/Sequences/map_shapes_properties_prp_id_seq.sql)
res=$(psql $db -qtA -f $DIR/Sequences/map_image_img_id_seq.sql)
res=$(psql $db -qtA -f $DIR/Sequences/shapefiles_shp_file_id_seq.sql)
res=$(psql $db -qtA -f $DIR/Sequences/soil_type_soil_id_seq.sql)
res=$(psql $db -qtA -f $DIR/Sequences/stg_hds_rid_seq.sql)
res=$(psql $db -qtA -f $DIR/Sequences/stg_ucn_rid_seq.sql)
res=$(psql $db -qtA -f $DIR/Sequences/stomp2gw_graphs_rid_seq.sql)
res=$(psql $db -qtA -f $DIR/Sequences/stomp2gw_rid_seq.sql)
res=$(psql $db -qtA -f $DIR/Sequences/units_unit_id_seq.sql)
d=$(date)
echo "$d: Created Sequences" 

#    Tables
psql $db -qtA -f $DIR/Tables/models.sql
psql $db -qtA -f $DIR/Tables/copc.sql
psql $db -qtA -f $DIR/Tables/pathways.sql
psql $db -qtA -f $DIR/Tables/buckets.sql
psql $db -qtA -f $DIR/Tables/units.sql
psql $db -qtA -f $DIR/Tables/cells.sql
psql $db -qtA -f $DIR/Tables/soil_types.sql
psql $db -qtA -f $DIR/Tables/dose_factors.sql
psql $db -qtA -f $DIR/Tables/cell_heads.sql
psql $db -qtA -f $DIR/Tables/cell_soils.sql
psql $db -qtA -f $DIR/Tables/concentrations.sql
psql $db -qtA -f $DIR/Tables/shapefiles.sql
psql $db -qtA -f $DIR/Tables/model_shapefiles.sql
psql $db -qtA -f $DIR/Tables/map_shapes.sql
psql $db -qtA -f $DIR/Tables/map_shapes_attributes.sql
psql $db -qtA -f $DIR/Tables/map_images.sql
psql $db -qtA -f $DIR/Tables/stg_cells.sql
psql $db -qtA -f $DIR/Tables/stg_hds.sql
psql $db -qtA -f $DIR/Tables/stg_soils.sql
psql $db -qtA -f $DIR/Tables/stg_ucn.sql
psql $db -qtA -f $DIR/Tables/stomp2gw_graphs.sql
psql $db -qtA -f $DIR/Tables/stomp2gw_lookup.sql

#    Functions
echo "END  setupdb"
psql $db -qtA -f $DIR/Functions/icf_ucn_read.sql
psql $db -qtA -f $DIR/Functions/icf_ucn_read2.sql
psql $db -qtA -f $DIR/Functions/icf_util_copy_model.sql
psql $db -qtA -f $DIR/Functions/icf_util_get_srid.sql
psql $db -qtA -f $DIR/Functions/icf_write_file.sql
psql $db -qtA -f $DIR/Functions/'icf_util_map_shapes_attributes_load(integer).sql'
psql $db -qtA -f $DIR/Functions/icf_util_map_shapes_attributes_load.sql
psql $db -qtA -f $DIR/Functions/'icf_util_map_shapes_load(integer).sql'
psql $db -qtA -f $DIR/Functions/icf_util_map_shapes_load.sql
psql $db -qtA -f $DIR/Functions/icf_util_shp_to_mview.sql
psql $db -qtA -f $DIR/Functions/icf_ucn_get.sql
psql $db -qtA -f $DIR/Functions/icf_ucn_load.sql

# POSTGIS 
#psql -d $db -qtA -f $DIR/epsg_102749.sql

psql -d $db -qtA -c "vacuum analyze;"
d=$(date)
echo "$d: END loading datase"
