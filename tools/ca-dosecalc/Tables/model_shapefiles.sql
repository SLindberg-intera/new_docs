-- Table: public.model_shapefiles

-- DROP TABLE public.model_shapefiles;

CREATE TABLE public.model_shapefiles
(
    shp_file_id integer NOT NULL,
    mdl_id integer NOT NULL,
    CONSTRAINT pk_model_shapefiles PRIMARY KEY (shp_file_id, mdl_id),
    CONSTRAINT fk_models_model_shapefiles FOREIGN KEY (mdl_id)
        REFERENCES public.models (mdl_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_shapefiles_model_shapefiles FOREIGN KEY (shp_file_id)
        REFERENCES public.shapefiles (shp_file_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.model_shapefiles
    OWNER to ca;