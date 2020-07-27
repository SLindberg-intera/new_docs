-- FUNCTION: public."fn_test_concentration_layer_CR"(date)

-- DROP FUNCTION public."fn_test_concentration_layer_CR"(date);

CREATE OR REPLACE FUNCTION public."fn_test_concentration_layer_CR"(
	in_model_date date)
    RETURNS json
    LANGUAGE 'plpgsql'

    COST 100
    VOLATILE 
AS $BODY$
declare out_json json;
begin
WITH wrap AS (
	WITH mv AS (
		SELECT DISTINCT ON(t1.cell_row, t1.cell_column, t1.model_date) t1.cell_row, t1.cell_column, t1.model_date, t1.concentration, t1.cell_layer, t1.copc, t1.geom
		FROM mv_concentrations t1
		LEFT JOIN mv_concentrations t2
		ON t2.concentration > t1.concentration AND t1.cell_row = t2.cell_row AND t1.cell_column = t2.cell_column AND t1.model_date = t2.model_date
		WHERE t2.concentration IS NULL
	), area AS (
		SELECT st_union(t2.geom) geom
		FROM mvshp_ehremgca t1
		JOIN map_shapes t2 USING(shp_id)
	)
	SELECT st_transform(mv.geom, 4326) geom, mv.cell_row, mv.cell_column, mv.cell_layer, mv.model_date, mv.concentration conc
	FROM mv, area
	WHERE NOT ST_WITHIN(mv.geom, area.geom) AND mv.model_date::date = in_model_date
), A AS (
	SELECT conc, cell_row, cell_column, cell_layer, model_date, geom, 
	CASE
		WHEN conc BETWEEN 1 AND 10 THEN 0 
		WHEN conc BETWEEN 10.000001 AND 100 THEN 1 
		WHEN conc BETWEEN 100.0000001 AND 500 THEN 2 
		ELSE 3
	END AS rangeType
	FROM wrap
	WHERE conc > 1
)
SELECT json_build_object (
	'type', 'FeatureCollection',
	'features', jsonb_agg(feature)
) 
INTO out_json
FROM (
	SELECT json_build_object (
	'type', 'Feature', 'geometry', 
	ST_asGeoJSON (geom, 6)::jsonb, 
	'properties', json_build_object (
			'max concentration (pCi/L)', conc/1000,
			'cell row', cell_row, 
			'cell column', cell_column, 
			'cell layer', cell_layer,
			'fill', 
			CASE
				WHEN rangeType = 0 THEN '#89a9dd'
				WHEN rangeType = 1 THEN '#4b6ca3'
				WHEN rangeType = 2 THEN '#d1b245'
				ELSE '#e8d9a4'
			END,
			'stroke-width', 0,
			'stroke-opacity', 0,
			'fill-opacity', 1
		)
	) AS feature 
	FROM A 
	GROUP BY rangeType, conc, geom, cell_row, cell_column, cell_layer
	ORDER BY rangeType
) V;

RETURN out_json;
END
$BODY$;

ALTER FUNCTION public."fn_test_concentration_layer_CR"(date)
    OWNER TO ca;
