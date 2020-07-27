-- FUNCTION: public."fn_test_stats_by_year_outside_outer_CR"()

-- DROP FUNCTION public."fn_test_stats_by_year_outside_outer_CR"();

CREATE OR REPLACE FUNCTION public."fn_test_stats_by_year_outside_outer_CR"(
	)
    RETURNS TABLE(model_date date, max_concentration numeric, min_concentration numeric, avg_concentration numeric, std_dev_of_concentration numeric, ninetieth_percentile double precision, seventy_fifth_percentile double precision, fiftieth_percentile_percentile double precision, twenty_fiftieth_percentile double precision, count bigint) 
    LANGUAGE 'plpgsql'

    COST 100
    VOLATILE 
    ROWS 1000
AS $BODY$
BEGIN
RETURN QUERY

WITH years AS (
	SELECT mv.model_date::date
	FROM mv_concentrations mv
	GROUP BY mv.model_date
), boundry AS (
	WITH area AS (
		SELECT st_transform(st_union(t2.geom), 4326) geom
		FROM mvshp_ehremgca t1
		JOIN map_shapes t2 USING(shp_id)
		WHERE t1.name LIKE 'INNER' OR t1.name LIKE 'OUTER'
	)
	SELECT mv.* 
	FROM mv_concentrations mv, area
	WHERE NOT st_within(mv.geom, area.geom)
), mv_stats AS (
	SELECT mv.model_date::date, MAX(concentration) max_concentration, MIN(concentration) min_concentration,
		AVG(concentration) avg_concentration, stddev(concentration) std_dev_of_concentration,
		percentile_cont(.90) WITHIN GROUP(ORDER BY concentration) ninetieth_percentile,
		percentile_cont(.75) WITHIN GROUP(ORDER BY concentration) seventy_fifth_percentile,
		percentile_cont(.50) WITHIN GROUP(ORDER BY concentration) fiftieth_percentile_percentile,
		percentile_cont(.25) WITHIN GROUP(ORDER BY concentration) twenty_fiftieth_percentile,
		COUNT(*) count
	FROM boundry mv
	GROUP BY mv.model_date
)
SELECT years.model_date, mv_stats.max_concentration, mv_stats.min_concentration, mv_stats.avg_concentration,
	mv_stats.std_dev_of_concentration, mv_stats.ninetieth_percentile, mv_stats.seventy_fifth_percentile,
	mv_stats.fiftieth_percentile_percentile, mv_stats.twenty_fiftieth_percentile, mv_stats.count
FROM years
LEFT JOIN mv_stats USING(model_date)
ORDER BY years.model_date;

END
$BODY$;

ALTER FUNCTION public."fn_test_stats_by_year_outside_outer_CR"()
    OWNER TO ca;
