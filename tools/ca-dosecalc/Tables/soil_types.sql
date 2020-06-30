-- Table: public.soil_types

-- DROP TABLE public.soil_types;

CREATE TABLE public.soil_types
(
    soil_id smallint NOT NULL DEFAULT nextval('soil_type_soil_id_seq'::regclass),
    mdl_id integer NOT NULL,
    soil_nm character varying(32) COLLATE pg_catalog."default" NOT NULL,
    soil_desc character varying(255) COLLATE pg_catalog."default",
    soil_density numeric,
    soil_moisture numeric,
    dose_nm character varying(32) COLLATE pg_catalog."default",
    CONSTRAINT pk_soil_types PRIMARY KEY (soil_id),
    CONSTRAINT unq_soil_types UNIQUE (mdl_id, soil_nm),
    CONSTRAINT fk_model_soil_type FOREIGN KEY (mdl_id)
        REFERENCES public.models (mdl_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.soil_types
    OWNER to postgres;
COMMENT ON TABLE public.soil_types
    IS 'The table to store the model soil types.';

COMMENT ON COLUMN public.soil_types.soil_id
    IS 'Sequence generated identifier for the Soil Type table.';

COMMENT ON COLUMN public.soil_types.mdl_id
    IS 'A reference to the model identifier.';

COMMENT ON COLUMN public.soil_types.soil_nm
    IS 'The name of the soil.';

COMMENT ON COLUMN public.soil_types.soil_desc
    IS 'A description of the soil.';

COMMENT ON COLUMN public.soil_types.soil_density
    IS 'This is the Dry Bulk Density of the soil measured in g/cm³.';

COMMENT ON COLUMN public.soil_types.soil_moisture
    IS 'This is the percent of moisture in the soil.';

COMMENT ON COLUMN public.soil_types.dose_nm
    IS 'An alternate name of the soil, used in the Dose.';