-- Table: public.stg_ucn

-- DROP TABLE public.stg_ucn;

CREATE TABLE public.stg_ucn
(
    rid bigint NOT NULL DEFAULT nextval('stg_ucn_rid_seq'::regclass),
    model_nm character varying(255) COLLATE pg_catalog."default",
    contam character varying(32) COLLATE pg_catalog."default",
    layer integer,
    "row" integer,
    col integer,
    stress_period integer,
    elapsed_time real,
    concentration double precision,
    time_step integer,
    mdl_id integer
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.stg_ucn
    OWNER to postgres;
COMMENT ON TABLE public.stg_ucn
    IS 'A table to stage the concentration values of an individual contaminant of possible concern.';