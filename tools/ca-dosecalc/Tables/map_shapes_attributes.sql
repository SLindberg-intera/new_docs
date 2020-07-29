-- Table: public.map_shapes_attributes

-- DROP TABLE public.map_shapes_attributes;

CREATE TABLE public.map_shapes_attributes
(
    prp_id bigint NOT NULL DEFAULT nextval('map_shapes_properties_prp_id_seq'::regclass),
    shp_id bigint NOT NULL,
    prp_key text COLLATE pg_catalog."default" NOT NULL,
    prp_value text COLLATE pg_catalog."default",
    CONSTRAINT pk_map_shapes_attributes PRIMARY KEY (prp_id),
    CONSTRAINT fk_map_shapes_properties FOREIGN KEY (shp_id)
        REFERENCES public.map_shapes (shp_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.map_shapes_attributes
    OWNER to ca;

-- Index: idx_map_shapes_attributes

-- DROP INDEX public.idx_map_shapes_attributes;

CREATE INDEX idx_map_shapes_attributes
    ON public.map_shapes_attributes USING btree
    (shp_id ASC NULLS LAST)
    TABLESPACE pg_default;