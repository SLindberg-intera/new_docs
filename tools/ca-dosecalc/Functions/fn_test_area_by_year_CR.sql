-- FUNCTION: public."fn_test_area_by_year_CR"()

-- DROP FUNCTION public."fn_test_area_by_year_CR"();

CREATE OR REPLACE FUNCTION public."fn_test_area_by_year_CR"(
	)
    RETURNS TABLE(model_date date, global_area double precision, outside_inner_area double precision, outside_outer_area double precision) 
    LANGUAGE 'plpgsql'

    COST 100
    VOLATILE 
    ROWS 1000
AS $BODY$
BEGIN
RETURN QUERY

WITH years AS (
	SELECT mv.model_date
	FROM mv_concentrations mv
	GROUP BY mv.model_date
), global_area AS (
	SELECT mv.model_date, st_area(st_union(mv.geom)) area
	FROM mv_concentrations mv
	GROUP BY mv.model_date
), inner_area AS (
	WITH area AS (
		SELECT st_transform(t2.geom, 4326) geom
		FROM mvshp_ehremgca t1
		JOIN map_shapes t2 USING(shp_id)
		WHERE t1.name LIKE 'INNER'
	)
	SELECT mv.model_date, st_area(st_transform(st_union(mv.geom), 4326)) area
	FROM mv_concentrations mv, area
	WHERE NOT st_within(mv.geom, area.geom)
	GROUP BY mv.model_date
), outer_area AS (
	WITH area AS (
		SELECT st_transform(st_union(t2.geom), 4326) geom
		FROM mvshp_ehremgca t1
		JOIN map_shapes t2 USING(shp_id)
		WHERE t1.name LIKE 'INNER' OR t1.name LIKE 'OUTER'
	)
	SELECT mv.model_date, st_area(st_transform(st_union(mv.geom), 4326)) area
	FROM mv_concentrations mv, area
	WHERE NOT st_within(mv.geom, area.geom)
	GROUP BY mv.model_date
)
SELECT years.model_date::date, global_area.area global_area, inner_area.area outside_inner_area, outer_area.area outside_outer_area
FROM years
LEFT JOIN global_area USING(model_date)
LEFT JOIN inner_area USING(model_date)
LEFT JOIN outer_area USING(model_date);

END
$BODY$;

ALTER FUNCTION public."fn_test_area_by_year_CR"()
    OWNER TO ca;
