-- Table: public.pathways

-- DROP TABLE public.pathways;

CREATE TABLE public.pathways
(
    mdl_id integer NOT NULL,
    pathway_nm character varying(32) COLLATE pg_catalog."default" NOT NULL,
    pathway_desc character varying(255) COLLATE pg_catalog."default",
    CONSTRAINT pk_pathways PRIMARY KEY (mdl_id, pathway_nm),
    CONSTRAINT fk_model_pathways FOREIGN KEY (mdl_id)
        REFERENCES public.models (mdl_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.pathways
    OWNER to postgres;
COMMENT ON TABLE public.pathways
    IS 'A table to store the models allowed dose pathway names.';

COMMENT ON COLUMN public.pathways.mdl_id
    IS 'A reference to the model identifier.';

COMMENT ON COLUMN public.pathways.pathway_nm
    IS 'The unique pathway name.';

COMMENT ON COLUMN public.pathways.pathway_desc
    IS 'A description of the pathway.';