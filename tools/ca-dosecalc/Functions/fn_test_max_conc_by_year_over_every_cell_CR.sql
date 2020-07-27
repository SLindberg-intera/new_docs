-- FUNCTION: public."fn_test_max_conc_by_year_over_every_cell_CR"()

-- DROP FUNCTION public."fn_test_max_conc_by_year_over_every_cell_CR"();

CREATE OR REPLACE FUNCTION public."fn_test_max_conc_by_year_over_every_cell_CR"(
	)
    RETURNS TABLE(model_name character varying, model_version text, copc character varying, model_date date, node integer, cell_row integer, cell_column integer, cell_layer integer, concentration numeric, units citext, mdl_id integer, cell_id integer, unit_id integer, geom geometry) 
    LANGUAGE 'plpgsql'

    COST 100
    VOLATILE 
    ROWS 1000
AS $BODY$
BEGIN
RETURN QUERY
WITH mv_max AS (
	SELECT mv.model_date, MAX(mv.concentration) concentration
	FROM mv_concentrations mv
	GROUP BY mv.model_date
)
SELECT mv.model_name, mv.model_version, mv.copc, mv.model_date::date,
	mv.node, mv.cell_row, mv.cell_column, mv.cell_layer, mv.concentration,
	mv.units, mv.mdl_id, mv.cell_id, mv.unit_id, mv.geom
FROM mv_concentrations mv
JOIN mv_max USING(model_date, concentration);

END
$BODY$;

ALTER FUNCTION public."fn_test_max_conc_by_year_over_every_cell_CR"()
    OWNER TO ca;
