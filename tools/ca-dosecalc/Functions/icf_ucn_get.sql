-- FUNCTION: public.icf_ucn_get(character varying, integer, character varying, integer)

-- DROP FUNCTION public.icf_ucn_get(character varying, integer, character varying, integer);

CREATE OR REPLACE FUNCTION public.icf_ucn_get(
	fname character varying,
	mdlidin integer,
	copcin character varying,
	layerin integer)
    RETURNS integer
    LANGUAGE 'plpgsql'

    COST 100
    VOLATILE 
AS $BODY$
DECLARE
	stgchk     integer;
	thresh     numeric;
	recinsert  integer;
BEGIN
	SELECT min_thresh
	INTO thresh
	FROM public.models
	JOIN public.copc USING (mdl_id)
	WHERE mdl_id = mdlidin
		AND contam_nm = copcin;

	IF thresh ISNULL THEN
		RAISE INFO '%', 'Model or COPC not found';
		RETURN -1;
	END IF;
	
	SELECT COUNT(*) 
	INTO stgchk
	FROM public.stg_ucn
	WHERE (mdl_id, contam, layer) = (mdlidin, copcin, layerin);

	IF stgchk > 0 THEN
		RAISE INFO '%', 'Duplicate staging records found, empty the public.stg_ucn before trying again.';
		RETURN -2;
	END IF;

	INSERT INTO public.stg_ucn (mdl_id, contam, col, "row", layer, stress_period, time_step, elapsed_time, concentration)
	SELECT DISTINCT mdlidin, copcin, mcolumn, mrow, mlayer, stress_period, time_step, etime, concentration
	FROM (
		SELECT mcolumn, mrow, mlayer, stress_period, time_step, round(elapsed_time) etime, concentration, 
			RANK() OVER (PARTITION BY mcolumn, mrow, mlayer, stress_period ORDER BY stress_period, time_step DESC) pos
		FROM public.icf_ucn_read2(fname, layerin, thresh)
	) X
	WHERE pos = 1 
	ORDER BY 1, 2, 3, 4, 5, 8;

	GET DIAGNOSTICS recinsert = ROW_COUNT;
	
	RETURN recinsert;
END;
$BODY$;

ALTER FUNCTION public.icf_ucn_get(character varying, integer, character varying, integer)
    OWNER TO ca;
