-- Table: public.map_shapes

-- DROP TABLE public.map_shapes;

CREATE TABLE public.map_shapes
(
    shp_id bigint NOT NULL DEFAULT nextval('map_shape_shp_id_seq'::regclass),
    shp_length numeric,
    shp_area numeric,
    geom geometry NOT NULL,
    geog geography,
    shp_file_id smallint,
    gid integer,
    CONSTRAINT pk_map_shapes PRIMARY KEY (shp_id),
    CONSTRAINT fk_shapefiles_map_shapes FOREIGN KEY (shp_file_id)
        REFERENCES public.shapefiles (shp_file_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.map_shapes
    OWNER to postgres;
COMMENT ON TABLE public.map_shapes
    IS 'A table to store shapefiles related to a model.';

COMMENT ON COLUMN public.map_shapes.shp_id
    IS 'Sequence generated identifier of the Map Shape table.';

COMMENT ON COLUMN public.map_shapes.shp_length
    IS 'The length of the shapefile, if available.';

COMMENT ON COLUMN public.map_shapes.shp_area
    IS 'The area of the shapefile, if available.';

COMMENT ON COLUMN public.map_shapes.geom
    IS 'The PostGIS Geometry representation of the shapefile.';

COMMENT ON COLUMN public.map_shapes.geog
    IS 'The PostGIS Geography representation of the shapefile.';

-- Index: gisidx_map_shapes_geom

-- DROP INDEX public.gisidx_map_shapes_geom;

CREATE INDEX gisidx_map_shapes_geom
    ON public.map_shapes USING gist
    (geom)
    TABLESPACE pg_default;


-- Index: idx_map_shapes

-- DROP INDEX public.idx_map_shapes;

CREATE INDEX idx_map_shapes
    ON public.map_shapes USING btree
    (shp_file_id ASC NULLS LAST)
    TABLESPACE pg_default;