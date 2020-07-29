-- FUNCTION: public.icf_util_map_shapes_attributes_load(text)

-- DROP FUNCTION public.icf_util_map_shapes_attributes_load(text);

CREATE OR REPLACE FUNCTION public.icf_util_map_shapes_attributes_load(
	_shapefile text)
    RETURNS integer
    LANGUAGE 'plpgsql'

    COST 100
    VOLATILE 
AS $BODY$
declare
	ssql  text;
begin
	select 'insert into public.map_shapes_attributes (shp_id, prp_key, prp_value) select * from ('||
		string_agg('select distinct shp_id, '''||column_name||''' prp_key, '||
			case data_type 
				when 'date' then 'to_json('||quote_ident(column_name)||'::timestamp)#>>''{}'' prp_value' 
				when 'character varying' then quote_ident(column_name)||'::text prp_value' 
				else quote_ident(column_name)||'::text prp_value' 
			end||
			' from public.map_shapes ms join public.'||table_name||' sm using (gid) where (shp_file_id) = ('||shp_file_id||')', ' union all ' order by column_name
		)||') X where prp_value notnull order by shp_id, prp_key;' 
	into ssql
	from information_schema.columns 
	join shapefiles s on (replace(table_name,'stg_shp_','') = lower(replace(s.shp_file_nm,'.shp','')))
	where (s.shp_file_nm) = (_shapefile) and column_name not in ('gid','geom','geog');
	
	execute ssql;

	return 0;
exception
	when null_value_not_allowed then
		return 0;
	when others then
		raise info '%',ssql;
		raise info '% - %',SQLSTATE,SQLERRM;
		return 1;
end
$BODY$;

ALTER FUNCTION public.icf_util_map_shapes_attributes_load(text)
    OWNER TO ca;
