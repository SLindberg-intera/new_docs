-- FUNCTION: public.fn_arcgis_concentration_coverage(character varying, character varying, character varying)

-- DROP FUNCTION public.fn_arcgis_concentration_coverage(character varying, character varying, character varying);

CREATE OR REPLACE FUNCTION public.fn_arcgis_concentration_coverage(
	model_in character varying,
	version_in character varying,
	copc_in character varying)
    RETURNS TABLE(oid bigint, model_date date, cell_row integer, cell_column integer, concentration numeric, geom geometry) 
    LANGUAGE 'plpgsql'

    COST 100
    VOLATILE 
    ROWS 1000
AS $BODY$

BEGIN
	RETURN QUERY

select row_number() over(order by C.model_date::date, C.cell_row, C.cell_column) as oid,
	C.model_date::date, C.cell_row, C.cell_column,
	max(C.concentration) as concentration, st_union(C.geom) as geom from mv_concentrations C where
	C.model_name = model_in and
	C.model_version = version_in and
	C.copc = copc_in
	group by C.model_date::date, C.cell_row, C.cell_column
	order by C.model_date::date, C.cell_row, C.cell_column;
	END;
$BODY$;

ALTER FUNCTION public.fn_arcgis_concentration_coverage(character varying, character varying, character varying)
    OWNER TO ca;
