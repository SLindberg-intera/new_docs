-- Table: public.stg_hds

-- DROP TABLE public.stg_hds;

CREATE TABLE public.stg_hds
(
    rid bigint NOT NULL DEFAULT nextval('stg_hds_rid_seq'::regclass),
    model_nm character varying(255) COLLATE pg_catalog."default",
    layer integer,
    "row" integer,
    col integer,
    stress_period integer,
    elapsed_time real,
    value double precision
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.stg_hds
    OWNER to postgres;
COMMENT ON TABLE public.stg_hds
    IS 'A table to stage the concentration values of an individual contaminant of possible concern.';