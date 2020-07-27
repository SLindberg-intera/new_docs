-- Table: public.buckets

-- DROP TABLE public.buckets;

CREATE TABLE public.buckets
(
    bkt_id bigint NOT NULL DEFAULT nextval('concentration_bucket_bkt_id_seq'::regclass),
    mdl_id bigint NOT NULL,
    contam_nm character varying(32) COLLATE pg_catalog."default" NOT NULL,
    pathway_nm character varying(32) COLLATE pg_catalog."default",
    bkt_type character varying(3) COLLATE pg_catalog."default" NOT NULL DEFAULT 'LI'::character varying,
    bkt_min numeric NOT NULL,
    bkt_max numeric NOT NULL,
    hex_color_code character varying(7) COLLATE pg_catalog."default" NOT NULL DEFAULT '#FFFFFF'::character varying,
    CONSTRAINT pk_buckets PRIMARY KEY (bkt_id),
    CONSTRAINT fk_copc_concentration_bucket FOREIGN KEY (contam_nm, mdl_id)
        REFERENCES public.copc (contam_nm, mdl_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_model_concentration_bucket FOREIGN KEY (mdl_id)
        REFERENCES public.models (mdl_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_pathway_concentration_bucket FOREIGN KEY (mdl_id, pathway_nm)
        REFERENCES public.pathways (mdl_id, pathway_nm) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.buckets
    OWNER to postgres;
COMMENT ON TABLE public.buckets
    IS 'A table of concentration buckets, or grouping of the values, and their hex color code to represent them in a map or plot.';

COMMENT ON COLUMN public.buckets.bkt_id
    IS 'Sequence generated identifier of the Concentration Bucket table.';

COMMENT ON COLUMN public.buckets.mdl_id
    IS 'A reference to the model identifier.';

COMMENT ON COLUMN public.buckets.contam_nm
    IS 'A reference to the COPC tables contaminate name.';

COMMENT ON COLUMN public.buckets.pathway_nm
    IS 'A reference to the Pathway tables pathway name.';

COMMENT ON COLUMN public.buckets.bkt_type
    IS 'The type of values grouping bucket, possible values include LI = Linear Interpolation, QT = Quartiles, CS = Custom.';

COMMENT ON COLUMN public.buckets.bkt_min
    IS 'The exclusive minimum of the values grouping bucket.';

COMMENT ON COLUMN public.buckets.bkt_max
    IS 'The inclusive maximum of the values grouping bucket.';

COMMENT ON COLUMN public.buckets.hex_color_code
    IS 'The Hex Color Code that represents the values grouping bucket.';

-- Index: idx_buckets

-- DROP INDEX public.idx_buckets;

CREATE INDEX idx_buckets
    ON public.buckets USING btree
    (mdl_id ASC NULLS LAST, contam_nm COLLATE pg_catalog."default" ASC NULLS LAST, pathway_nm COLLATE pg_catalog."default" ASC NULLS LAST, bkt_type COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;