-- Table: public.shapefiles

-- DROP TABLE public.shapefiles;

CREATE TABLE public.shapefiles
(
    shp_file_id smallint NOT NULL DEFAULT nextval('shapefiles_shp_file_id_seq'::regclass),
    shp_file_nm text COLLATE pg_catalog."default" NOT NULL,
    shp_file_url text COLLATE pg_catalog."default",
    shp_srid integer NOT NULL,
    CONSTRAINT pk_shapefiles PRIMARY KEY (shp_file_id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.shapefiles
    OWNER to ca;