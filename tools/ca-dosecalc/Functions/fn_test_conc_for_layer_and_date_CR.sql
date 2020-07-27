-- FUNCTION: public."fn_test_conc_for_layer_and_date_CR"(integer, integer)

-- DROP FUNCTION public."fn_test_conc_for_layer_and_date_CR"(integer, integer);

CREATE OR REPLACE FUNCTION public."fn_test_conc_for_layer_and_date_CR"(
	in_cell_row integer,
	in_cell_column integer)
    RETURNS json
    LANGUAGE 'plpgsql'

    COST 100
    VOLATILE 
AS $BODY$
declare out_json json;
begin
-- BODY OF FUNCTION
WITH info AS (
	SELECT json_build_object(
		'Layer', t1.cell_layer::text,
		'Concentrations', json_agg(t1.obj)
	) feature
	FROM (
		SELECT json_build_object(
			'Date', mv.model_date::date,
			'Value', mv.concentration
		) obj,
		mv.cell_layer cell_layer
		FROM mv_concentrations mv
		WHERE mv.cell_row = in_cell_row AND mv.cell_column = in_cell_column
	) t1
	GROUP BY t1.cell_layer
)
SELECT json_build_object (
	'Row', in_cell_row,
	'Column', in_cell_column,
	'Info', json_agg(info.feature)
)
INTO out_json
FROM info;

RETURN out_json;
END
$BODY$;

ALTER FUNCTION public."fn_test_conc_for_layer_and_date_CR"(integer, integer)
    OWNER TO ca;
