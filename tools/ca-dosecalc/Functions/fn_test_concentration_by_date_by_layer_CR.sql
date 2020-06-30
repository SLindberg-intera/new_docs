-- FUNCTION: public."fn_test_concentration_by_date_by_layer_CR"(integer, integer)

-- DROP FUNCTION public."fn_test_concentration_by_date_by_layer_CR"(integer, integer);

CREATE OR REPLACE FUNCTION public."fn_test_concentration_by_date_by_layer_CR"(
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
with pairs AS (
	with Layers AS (
		SELECT cell_layer lay
		FROM mv_concentrations
		GROUP BY cell_layer
	), Years AS (
		SELECT model_date
		FROM mv_concentrations
		GROUP BY model_date
	), mv AS (
		SELECT cell_layer lay, model_date, concentration, cell_row, cell_column
		FROM mv_concentrations
		WHERE cell_row = in_cell_row AND cell_column = in_cell_column
	)
	SELECT model_date, lay, COALESCE(concentration, 0) concentration
	FROM Layers
	LEFT JOIN Years ON (true)
	LEFT JOIN mv USING (lay, model_date)
), info AS (
	SELECT json_build_object(
		'Date', t1.model_date::date,
		'Concentrations', json_agg(t1.obj)
	) feature
	FROM (
		SELECT json_build_object(
			'Layer', lay::text,
			'Value', CAST(concentration AS FLOAT)
		) obj,
		model_date model_date
		FROM pairs
	) t1
	GROUP BY t1.model_date
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

ALTER FUNCTION public."fn_test_concentration_by_date_by_layer_CR"(integer, integer)
    OWNER TO ca;
