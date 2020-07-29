-- FUNCTION: public.icf_ucn_load()

-- DROP FUNCTION public.icf_ucn_load();

CREATE OR REPLACE FUNCTION public.icf_ucn_load(
	)
    RETURNS integer
    LANGUAGE 'plpgsql'

    COST 100
    VOLATILE 
AS $BODY$
DECLARE
	curlay integer;
BEGIN
	FOR curlay IN (SELECT DISTINCT layer FROM public.stg_ucn GROUP BY layer ORDER BY layer) LOOP
		INSERT INTO public.concentrations (mdl_id, contam_nm, cell_id, time_step, stress_period, elapsed_tm, concentration)
		SELECT DISTINCT gd.mdl_id, cc.contam_nm, gd.cell_id, su.time_step, su.stress_period, su.elapsed_time, su.concentration
		FROM public.models md 
		JOIN public.copc cc USING (mdl_id) 
		JOIN public.stg_ucn su ON (lower(su.contam) = lower(cc.contam_nm)
		                      AND (su.mdl_id = md.mdl_id))
		JOIN public.cells gd   ON (md.mdl_id = gd.mdl_id 
													AND (su.layer + md.mdl_lrc_offset) = gd.lay 
													AND (su."row" + md.mdl_lrc_offset) = gd."row" 
													AND (su.col + md.mdl_lrc_offset) = gd.col 
															)
		WHERE su.layer = curlay
		ORDER BY gd.mdl_id, cc.contam_nm, gd.cell_id, su.time_step, su.stress_period, su.elapsed_time;
	END LOOP;
	RETURN 0;
EXCEPTION
	WHEN OTHERS THEN
		RAISE INFO '%',SQLERRM;
		RETURN -1;
END
$BODY$;

ALTER FUNCTION public.icf_ucn_load()
    OWNER TO ca;
