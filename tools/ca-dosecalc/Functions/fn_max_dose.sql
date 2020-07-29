-- FUNCTION: public.fn_max_dose(character varying, integer, character varying, character varying)

-- DROP FUNCTION public.fn_max_dose(character varying, integer, character varying, character varying);

CREATE OR REPLACE FUNCTION public.fn_max_dose(
	model_in character varying,
	sp_in integer,
	copc_in character varying,
	pathway_in character varying)
    RETURNS TABLE(id integer, geom geometry, conc double precision, dose double precision) 
    LANGUAGE 'plpgsql'

    COST 100
    VOLATILE 
    ROWS 1000
AS $BODY$
BEGIN
	RETURN QUERY
	WITH md AS (
		SELECT model.mdl_id, to_date(model.mdl_start_yr::text,'YYYY')::timestamp
		FROM public.model
		WHERE (mdl_nm||'-ver'||mdl_ver||'.'||COALESCE(mdl_sub_ver,'0')) = model_in
	)
	SELECT DISTINCT node, geom, max_concentration, max_dose
	FROM md 
	JOIN public.max_dose USING (mdl_id)
	JOIN public.cell USING (row, col)
	WHERE copc = copc_in
		AND pathway = pathwayin
		AND (model_date - mdl_start_yr)::int = sp_in
	ORDER BY row, col, model_date;
END;
$BODY$;

ALTER FUNCTION public.fn_max_dose(character varying, integer, character varying, character varying)
    OWNER TO ca;
