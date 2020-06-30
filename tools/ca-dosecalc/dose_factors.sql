-- Table: public.dose_factors

-- DROP TABLE public.dose_factors;

CREATE TABLE public.dose_factors
(
    soil_id integer NOT NULL,
    contam_mdl_id integer NOT NULL,
    pathway_nm character varying(32) COLLATE pg_catalog."default" NOT NULL,
    contam_nm character varying(32) COLLATE pg_catalog."default" NOT NULL,
    dose_factor double precision NOT NULL,
    pathway_mdl_id integer,
    CONSTRAINT pk_dose_factors PRIMARY KEY (soil_id, contam_mdl_id, pathway_nm, contam_nm),
    CONSTRAINT fk_dose_factor_copc FOREIGN KEY (contam_mdl_id, contam_nm)
        REFERENCES public.copc (mdl_id, contam_nm) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_dose_factor_pathway FOREIGN KEY (contam_mdl_id, pathway_nm)
        REFERENCES public.pathways (mdl_id, pathway_nm) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_dose_factor_soil_type FOREIGN KEY (soil_id)
        REFERENCES public.soil_types (soil_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.dose_factors
    OWNER to postgres;

COMMENT ON COLUMN public.dose_factors.soil_id
    IS 'A reference to the soil type identifier.';

COMMENT ON COLUMN public.dose_factors.contam_mdl_id
    IS 'A reference to the copc identifier.';

COMMENT ON COLUMN public.dose_factors.pathway_nm
    IS 'A reference to the pathway identifier.';

COMMENT ON COLUMN public.dose_factors.contam_nm
    IS 'A reference to the copc identifier.';

COMMENT ON COLUMN public.dose_factors.dose_factor
    IS 'The factor to apply to the copc concentration when calculating the contaminant dose.';