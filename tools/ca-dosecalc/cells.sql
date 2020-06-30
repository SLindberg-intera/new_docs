-- Table: public.cells

-- DROP TABLE public.cells;

CREATE TABLE public.cells
(
    cell_id bigint NOT NULL DEFAULT nextval('grid_grid_id_seq'::regclass),
    mdl_id integer NOT NULL,
    "row" integer,
    col integer,
    lay integer,
    node integer,
    geom geometry,
    del_x numeric,
    del_y numeric,
    del_z numeric,
    node_src character varying(255) COLLATE pg_catalog."default",
    CONSTRAINT pk_cells PRIMARY KEY (cell_id),
    CONSTRAINT unq_cells UNIQUE (mdl_id, lay, "row", col),
    CONSTRAINT fk_model_grid FOREIGN KEY (mdl_id)
        REFERENCES public.models (mdl_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.cells
    OWNER to postgres;
COMMENT ON TABLE public.cells
    IS 'A table to store the model grid.';

COMMENT ON COLUMN public.cells.cell_id
    IS 'Sequence generated identifier for the Grid table. This is the 3D unique identifier.';

COMMENT ON COLUMN public.cells.mdl_id
    IS 'A reference to the model identifier.';

COMMENT ON COLUMN public.cells."row"
    IS 'The row, or y value, of the grid.';

COMMENT ON COLUMN public.cells.col
    IS 'The column, or x value, of the grid.';

COMMENT ON COLUMN public.cells.lay
    IS 'The layer, or z value, of the grid.';

COMMENT ON COLUMN public.cells.node
    IS 'The node identifier from the P2R Grid shapefile. This is the 2D unique identifier.';

COMMENT ON COLUMN public.cells.del_x
    IS 'The width of the grid cell.';

COMMENT ON COLUMN public.cells.del_y
    IS 'The length of the grid cell.';

COMMENT ON COLUMN public.cells.del_z
    IS 'The height of the grid cell.';
-- Index: gisidx_cells_geom

-- DROP INDEX public.gisidx_cells_geom;

CREATE INDEX gisidx_cells_geom
    ON public.cells USING gist
    (geom)
    TABLESPACE pg_default;
-- Index: idx_cells_mdl_id

-- DROP INDEX public.idx_cells_mdl_id;

CREATE INDEX idx_cells_mdl_id
    ON public.cells USING btree
    (mdl_id ASC NULLS LAST)
    TABLESPACE pg_default;