-- View: public.mv_analytes

-- DROP MATERIALIZED VIEW public.mv_analytes;

CREATE MATERIALIZED VIEW public.mv_analytes
TABLESPACE pg_default
AS
 SELECT m.mdl_nm AS model_name,
    (m.mdl_ver || '.'::text) || COALESCE(m.mdl_sub_ver, '0'::smallint) AS model_version,
    m.mdl_start_yr,
    c.contam_nm AS analyte,
    c.contam_long_nm AS analyte_long,
    c.min_thresh,
    c.mcl,
    u.unit_in,
    u.unit_out,
    u.conversion_factor AS cf,
    c.mdl_id,
    u.unit_id,
    m.mdl_srid
   FROM copc c
     JOIN units u USING (unit_id)
     JOIN models m USING (mdl_id)
  ORDER BY m.mdl_nm, ((m.mdl_ver || '.'::text) || COALESCE(m.mdl_sub_ver, '0'::smallint)), c.contam_nm, u.unit_in, u.unit_out
WITH DATA;
