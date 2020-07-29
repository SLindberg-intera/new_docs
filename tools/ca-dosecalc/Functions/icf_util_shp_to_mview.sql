-- FUNCTION: public.icf_util_shp_to_mview(text)

-- DROP FUNCTION public.icf_util_shp_to_mview(text);

CREATE OR REPLACE FUNCTION public.icf_util_shp_to_mview(
	_shapefile text)
    RETURNS integer
    LANGUAGE 'plpgsql'

    COST 100
    VOLATILE 
AS $BODY$
DECLARE
	ssql text;
BEGIN
	with shpf as (
		select distinct shp_file_id sfid, lower(shp_file_nm) shp_file_nm, prp_key column_name
		from shapefiles s 
		join map_shapes f using (shp_file_id)
		join map_shapes_attributes a using (shp_id)
		where shp_file_nm = _shapefile
	), foo as (
		select sfid, shp_file_nm, 
			'gid numeric, shp_id numeric, geom geometry, '||string_agg(quote_ident(c.column_name)||' '||case c.data_type when 'character varying' then 'text' when 'date' then 'text' else 'numeric' end, ', ' order by c.column_name) fields,
			'ct.gid, '||string_agg('ct.'||quote_ident(c.column_name), ', ' order by c.column_name)||', ct.shp_id, ct.geom' selects
		from information_schema.columns c
		join shpf s on (lower(regexp_replace(c.table_name,'stg_shp_|_geom','','g')) = replace(s.shp_file_nm,'.shp','') and c.column_name = s.column_name)
		group by sfid, shp_file_nm
	)
	select 'create materialized view public.mvshp_'||replace(shp_file_nm,'.shp','')||' as
select '||selects||'
from crosstab(''select gid::numeric, shp_id::numeric, geom, prp_key, prp_value from public.shapefiles join public.map_shapes using (shp_file_id) join public.map_shapes_attributes using (shp_id) where (lower(shp_file_nm)) = ('''''||shp_file_nm||''''') order by shp_id, prp_key'',
              ''select distinct prp_key from public.shapefiles join public.map_shapes using (shp_file_id) join public.map_shapes_attributes using (shp_id) where (lower(shp_file_nm)) = ('''''||shp_file_nm||''''') order by prp_key''
             ) as ct ('||foo.fields||')
order by 1;
alter materialized view public.mvshp_'||replace(shp_file_nm,'.shp','')||' owner to postgres;'
-- grant references, select on table public.mvshp_'||replace(shp_file_nm,'.shp','')||' to intera_modeler;'
	into ssql
	from foo;

	execute ssql;

	return 0;
EXCEPTION
	when null_value_not_allowed then
		return 0;
	when others then
	  raise info '%',ssql;
		raise info '% - %',SQLSTATE,SQLERRM;
		return 1;
END
$BODY$;

ALTER FUNCTION public.icf_util_shp_to_mview(text)
    OWNER TO ca;
