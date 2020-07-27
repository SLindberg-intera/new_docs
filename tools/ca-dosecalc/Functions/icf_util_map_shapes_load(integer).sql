-- FUNCTION: public.icf_util_map_shapes_load(text, integer)

-- DROP FUNCTION public.icf_util_map_shapes_load(text, integer);

CREATE OR REPLACE FUNCTION public.icf_util_map_shapes_load(
	_shapefile text,
	_mdlid integer)
    RETURNS integer
    LANGUAGE 'plpgsql'

    COST 100
    VOLATILE 
AS $BODY$
declare
	carea varchar;
	cleng varchar;
	tgeom varchar;
	mdlid integer;
	spfid integer;
	ssql  text;
begin
	select mdl_id, shp_file_id, 'stg_shp_'||replace(_shapefile,'.shp','') into mdlid, spfid, tgeom from shapefiles where (mdl_id, shp_file_nm) = (_mdlid, _shapefile);
	select coalesce(string_agg(column_name,''), 'st_area(geom)') into carea from information_schema.columns where table_name ilike '%'||replace(_shapefile,'.shp','') and (column_name like '%area%' or column_name = 'shape_star');
	select coalesce(string_agg(column_name,''), 'st_length(geom)') into cleng from information_schema.columns where table_name ilike '%'||replace(_shapefile,'.shp','') and (column_name like '%len%' or column_name = 'shape_stle');

	ssql = 'insert into public.map_shapes (mdl_id, shp_file_id, gid, shp_length, shp_area, geom, geog, shp_srid)
	select '||mdlid||', '||spfid||', gid, '||cleng||', '||carea||', geom, geog, st_srid(geom)
	from '||tgeom||';';
	
	execute ssql;

	return 0;
exception
	when others then
		raise info '%',SQLERRM;
		return 1;
end
$BODY$;

ALTER FUNCTION public.icf_util_map_shapes_load(text, integer)
    OWNER TO ca;
