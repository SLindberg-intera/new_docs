-- FUNCTION: public.icf_util_map_shapes_load(text)

-- DROP FUNCTION public.icf_util_map_shapes_load(text);

CREATE OR REPLACE FUNCTION public.icf_util_map_shapes_load(
	_shapefile text)
    RETURNS integer
    LANGUAGE 'plpgsql'

    COST 100
    VOLATILE 
AS $BODY$
declare
	carea varchar;
	cleng varchar;
	tgeom varchar;
	spfid integer;
	ssql  text;
begin
	select shp_file_id, 'stg_shp_'||replace(_shapefile,'.shp','') into spfid, tgeom from shapefiles where (shp_file_nm) = (_shapefile);
	select coalesce(string_agg(column_name,''), 'st_area(geom)') into carea from information_schema.columns where table_name ilike '%'||replace(_shapefile,'.shp','') and (column_name like '%area%' or column_name = 'shape_star') and (column_name not like '%size%') and (column_name not like '%_st%');
	select coalesce(string_agg(column_name,''), 'st_length(geom)') into cleng from information_schema.columns where table_name ilike '%'||replace(_shapefile,'.shp','') and (column_name like '%len%' or column_name = 'shape_stle') and (column_name not like '%size%') and (column_name not like '%_st%');

	ssql = 'insert into public.map_shapes (shp_file_id, gid, shp_length, shp_area, geom, geog)
	select '||spfid||', gid, '||cleng||', '||carea||', geom, geog
	from '||tgeom||';';
	
	execute ssql;

	return 0;
exception
	when others then
		raise info '%',SQLERRM;
		return 1;
end
$BODY$;

ALTER FUNCTION public.icf_util_map_shapes_load(text)
    OWNER TO ca;
