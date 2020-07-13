-- View: public.mv_concentrations

-- DROP MATERIALIZED VIEW public.mv_concentrations;

CREATE MATERIALIZED VIEW public.mv_concentrations
TABLESPACE pg_default
AS
 SELECT DISTINCT a.model_name,
    a.model_version,
    c.contam_nm AS copc,
    to_date(a.mdl_start_yr::text, 'YYYY'::text)::timestamp without time zone + ((c.elapsed_tm || ' days'::text)::interval) AS model_date,
    g."row" AS cell_row,
    g.col AS cell_column,
    g.lay AS cell_layer,
    c.concentration * a.cf AS concentration,
    a.unit_out AS units,
    c.mdl_id,
    c.cell_id,
    a.unit_id,
    st_transform(g.geom, a.mdl_srid) AS geom
   FROM mv_analytes a
     JOIN cells g ON a.mdl_id = g.mdl_id
     JOIN concentrations c ON c.mdl_id = a.mdl_id AND c.cell_id = g.cell_id AND c.contam_nm::text = a.analyte::text AND c.concentration >= a.min_thresh
  ORDER BY a.model_name, a.model_version, c.contam_nm, (to_date(a.mdl_start_yr::text, 'YYYY'::text)::timestamp without time zone + ((c.elapsed_tm || ' days'::text)::interval)), g."row", g.col, g.lay
WITH DATA;


CREATE INDEX idx_mv_concentrations
    ON public.mv_concentrations USING btree
    (mdl_id, copc COLLATE pg_catalog."default", cell_id)
    TABLESPACE pg_default;
