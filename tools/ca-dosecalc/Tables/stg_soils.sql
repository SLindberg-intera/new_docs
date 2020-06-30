-- Table: public.stg_soils

-- DROP TABLE public.stg_soils;

CREATE TABLE public.stg_soils
(
    new_soil_id bigint,
    new_mdl_id integer,
    soil_id smallint,
    mdl_id integer,
    soil_nm character varying(32) COLLATE pg_catalog."default",
    soil_desc character varying(255) COLLATE pg_catalog."default",
    soil_density numeric,
    soil_moisture numeric,
    dose_nm character varying(32) COLLATE pg_catalog."default"
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.stg_soils
    OWNER to ca;