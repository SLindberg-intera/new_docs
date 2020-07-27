-- FUNCTION: public.fn_test_concentration_layer(date)

-- DROP FUNCTION public.fn_test_concentration_layer(date);

CREATE OR REPLACE FUNCTION public.fn_test_concentration_layer(
	in_model_date date)
    RETURNS json
    LANGUAGE 'plpgsql'

    COST 100
    VOLATILE 
AS $BODY$
declare out_json json;
begin
with A as (
	select concentration, 
		cell_lrc, 
		geom, 
		case
			when concentration/1000 between 1 and 10 then 0 
			when concentration/1000 between 10.000001 and 100 then 1 
			when concentration/1000 between 100.0000001 and 500 then 2 
			else 3
		end as rangeType
	from concentration
	where concentration/1000 > 1 and model_date::date = in_model_date
)

select json_build_object(
	'type', 'FeatureCollection',
	'features', jsonb_agg(feature)
) into out_json
from ( select json_build_object(
	'type', 'Feature',
	'geometry', ST_asGeoJSON(
			st_transform(ST_Union(geom), 4326), 6
	)::jsonb,
	'properties', json_build_object(
		'max concentration (pCi/L)', max(concentration/1000),
		'fill', case
					when rangeType = 0 then '#89a9dd'
					when rangeType = 1 then '#4b6ca3'
					when rangeType = 2 then '#d1b245'
					else '#e8d9a4'
				end,
		'stroke-width', 0,
		'stroke-opacity', 0,
		'fill-opacity', 1
	)
) as feature from A group by rangeType order by rangeType) V;

return out_json;
end
$BODY$;

ALTER FUNCTION public.fn_test_concentration_layer(date)
    OWNER TO ca;
