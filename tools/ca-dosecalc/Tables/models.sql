-- Table: public.models

-- DROP TABLE public.models;

CREATE TABLE public.models
(
    mdl_id smallint NOT NULL DEFAULT nextval('model_mdl_id_seq'::regclass),
    mdl_nm character varying(255) COLLATE pg_catalog."default" NOT NULL,
    mdl_ver smallint NOT NULL DEFAULT 0,
    mdl_sub_ver smallint,
    mdl_desc character varying(255) COLLATE pg_catalog."default",
    mdl_exec_tm timestamp without time zone,
    mdl_lrc_offset integer DEFAULT 0,
    mdl_start_yr smallint,
    mdl_srid integer,
    mdl_scenario text COLLATE pg_catalog."default" DEFAULT 'Main'::text,
    CONSTRAINT pk_models PRIMARY KEY (mdl_id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.models
    OWNER to postgres;
COMMENT ON TABLE public.models
    IS 'The table to store the model.';

COMMENT ON COLUMN public.models.mdl_id
    IS 'Sequence generated identifier of the Model table.';

COMMENT ON COLUMN public.models.mdl_nm
    IS 'The name of the model.';

COMMENT ON COLUMN public.models.mdl_ver
    IS 'The version of the model.';

COMMENT ON COLUMN public.models.mdl_sub_ver
    IS 'The sub-version of the model.';

COMMENT ON COLUMN public.models.mdl_desc
    IS 'A description of the model.';

COMMENT ON COLUMN public.models.mdl_exec_tm
    IS 'The execution or run time of the model.';

COMMENT ON COLUMN public.models.mdl_lrc_offset
    IS 'An offset to handle any differences in index starting values.';

COMMENT ON COLUMN public.models.mdl_scenario
    IS 'The modeling scenario for the model.';

-- Index: idx_models

-- DROP INDEX public.idx_models;

CREATE UNIQUE INDEX idx_models
    ON public.models USING btree
    (mdl_nm COLLATE pg_catalog."default" ASC NULLS LAST, mdl_ver ASC NULLS LAST, mdl_sub_ver ASC NULLS LAST, mdl_scenario COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;