-- FUNCTION: public.icf_util_get_srid(character varying)

-- DROP FUNCTION public.icf_util_get_srid(character varying);

CREATE OR REPLACE FUNCTION public.icf_util_get_srid(
	proj4in character varying)
    RETURNS integer
    LANGUAGE 'sql'

    COST 100
    VOLATILE 
AS $BODY$
	SELECT DISTINCT srid
	FROM (
		SELECT TRIM(STRING_AGG(p4, '|' ORDER BY TRIM(SPLIT_PART(p4,'=',1)))) p4text
		FROM (
			SELECT UNNEST(STRING_TO_ARRAY(proj4in, '+', '')) p4
		) X
		WHERE p4 NOTNULL
			AND CASE WHEN SPLIT_PART(p4,'=',1) LIKE '%\_%' ESCAPE'\' THEN RIGHT(TRIM(SPLIT_PART(p4,'=',1)),1) = '0' ELSE TRUE END
			AND TRIM(SPLIT_PART(p4,'=',1)) NOT IN ('ellps','towgs84')
	) B
	JOIN (
		SELECT srid, TRIM(STRING_AGG(p4, '|' ORDER BY TRIM(SPLIT_PART(p4,'=',1)))) p4text
		FROM (
			SELECT srid, UNNEST(STRING_TO_ARRAY(proj4text, '+', '')) p4
			from spatial_ref_sys
		) X
		WHERE p4 NOTNULL
			AND CASE WHEN SPLIT_PART(p4,'=',1) LIKE '%\_%' ESCAPE '\' THEN RIGHT(TRIM(SPLIT_PART(p4,'=',1)),1) = '0' ELSE TRUE END
			AND TRIM(SPLIT_PART(p4,'=',1)) NOT IN ('ellps','towgs84')
		GROUP BY srid
	) D USING (p4text)
	LIMIT 1;
$BODY$;

ALTER FUNCTION public.icf_util_get_srid(character varying)
    OWNER TO ca;
