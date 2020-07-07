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
db=$1 rep=$2
dropdb $db
createdb $db
psql $db -f $DIR/setup.sql >> $rep
echo "Created Postgres Database with PostGIS extensions"
#psql $db -f $DIR/setup.sql > $rep
#    Sequences (used as primary keys) 
psql $db -f $DIR/Sequences/model_mdl_id_seq.sql >> $rep
psql $db -f $DIR/Sequences/concentration_bucket_bkt_id_seq.sql >> $rep
psql $db -f $DIR/Sequences/grid_grid_id_seq.sql >> $rep
psql $db -f $DIR/Sequences/map_shape_shp_id_seq.sql >> $rep
psql $db -f $DIR/Sequences/map_shapes_properties_prp_id_seq.sql >> $rep
psql $db -f $DIR/Sequences/map_image_img_id_seq.sql >> $rep
psql $db -f $DIR/Sequences/shapefiles_shp_file_id_seq.sql >> $rep
psql $db -f $DIR/Sequences/soil_type_soil_id_seq.sql >> $rep
psql $db -f $DIR/Sequences/stg_hds_rid_seq.sql >> $rep
psql $db -f $DIR/Sequences/stg_ucn_rid_seq.sql >> $rep
psql $db -f $DIR/Sequences/stomp2gw_graphs_rid_seq.sql >> $rep
psql $db -f $DIR/Sequences/stomp2gw_rid_seq.sql >> $rep
psql $db -f $DIR/Sequences/units_unit_id_seq.sql >> $rep
echo "Created Sequences" 

#    Tables
psql $db -f $DIR/Tables/models.sql >> $rep
psql $db -f $DIR/Tables/copc.sql >> $rep
psql $db -f $DIR/Tables/pathways.sql >> $rep
psql $db -f $DIR/Tables/buckets.sql >> $rep
psql $db -f $DIR/Tables/units.sql >> $rep
psql $db -f $DIR/Tables/cells.sql >> $rep
psql $db -f $DIR/Tables/soil_types.sql >> $rep
psql $db -f $DIR/Tables/dose_factors.sql >> $rep
psql $db -f $DIR/Tables/cell_heads.sql >> $rep
psql $db -f $DIR/Tables/cell_soils.sql >> $rep
psql $db -f $DIR/Tables/concentrations.sql >> $rep
psql $db -f $DIR/Tables/shapefiles.sql >> $rep
psql $db -f $DIR/Tables/model_shapefiles.sql >> $rep
psql $db -f $DIR/Tables/map_shapes.sql >> $rep
psql $db -f $DIR/Tables/map_shapes_attributes.sql >> $rep
psql $db -f $DIR/Tables/map_images.sql >> $rep
psql $db -f $DIR/Tables/stg_cells.sql >> $rep
psql $db -f $DIR/Tables/stg_hds.sql >> $rep
psql $db -f $DIR/Tables/stg_soils.sql >> $rep
psql $db -f $DIR/Tables/stg_ucn.sql >> $rep
psql $db -f $DIR/Tables/stomp2gw_graphs.sql >> $rep
psql $db -f $DIR/Tables/stomp2gw_lookup.sql >> $rep

#    Functions
echo "END  setupdb"
psql $db -f $DIR/Functions/icf_ucn_read.sql >> $rep
psql $db -f $DIR/Functions/icf_ucn_read2.sql >> $rep
psql $db -f $DIR/Functions/icf_util_copy_model.sql >> $rep
psql $db -f $DIR/Functions/icf_util_get_srid.sql >> $rep
psql $db -f $DIR/Functions/icf_write_file.sql >> $rep
psql $db -f $DIR/Functions/'icf_util_map_shapes_attributes_load(integer).sql' >> $rep
psql $db -f $DIR/Functions/icf_util_map_shapes_attributes_load.sql >> $rep
psql $db -f $DIR/Functions/'icf_util_map_shapes_load(integer).sql' >> $rep
psql $db -f $DIR/Functions/icf_util_map_shapes_load.sql >> $rep
psql $db -f $DIR/Functions/icf_util_shp_to_mview.sql >> $rep
psql $db -f $DIR/Functions/icf_ucn_get.sql >> $rep
psql $db -f $DIR/Functions/icf_ucn_load.sql >> $rep

# POSTGIS 
psql $db -f $DIR/epsg_102749.sql >> $rep
