-- View: public.mv_dose

-- DROP MATERIALIZED VIEW public.mv_dose;

CREATE MATERIALIZED VIEW public.mv_dose
TABLESPACE pg_default
AS
 SELECT DISTINCT cc.model_name,
    cc.model_version,
    cc.copc,
    sl.soil_nm AS soil,
    df.pathway_nm AS pathway,
    cc.model_date,
    cc.cell_row,
    cc.cell_column,
    cc.cell_layer,
    cc.concentration,
    df.dose_factor,
    cc.concentration::double precision * df.dose_factor AS dose,
    cc.units,
    cc.geom,
    cc.mdl_id,
    cc.cell_id,
    sl.soil_id,
    cc.unit_id
   FROM dose_factors df
     JOIN soil_types sl ON sl.mdl_id = df.contam_mdl_id AND sl.soil_id = df.soil_id
     JOIN cell_soils cs ON cs.soil_id = sl.soil_id
     JOIN mv_concentrations cc ON cc.mdl_id = sl.mdl_id AND cc.copc::text = df.contam_nm::text AND cc.cell_id = cs.cell_id AND cs.soil_id = sl.soil_id
WITH DATA;
