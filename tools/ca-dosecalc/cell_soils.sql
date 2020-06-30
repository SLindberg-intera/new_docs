-- Table: public.cell_soils

-- DROP TABLE public.cell_soils;

CREATE TABLE public.cell_soils
(
    cell_id integer NOT NULL,
    soil_id integer NOT NULL,
    CONSTRAINT pk_cell_soils PRIMARY KEY (cell_id, soil_id),
    CONSTRAINT fk_grid_soil_type_grid FOREIGN KEY (cell_id)
        REFERENCES public.cells (cell_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE,
    CONSTRAINT fk_grid_soil_type_soil FOREIGN KEY (soil_id)
        REFERENCES public.soil_types (soil_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.cell_soils
    OWNER to postgres;

COMMENT ON COLUMN public.cell_soils.cell_id
    IS 'A reference to the grid identifier.';

COMMENT ON COLUMN public.cell_soils.soil_id
    IS 'A reference to the soil type identifier.';
-- Index: fkidx_cell_soils_cells

-- DROP INDEX public.fkidx_cell_soils_cells;

CREATE INDEX fkidx_cell_soils_cells
    ON public.cell_soils USING btree
    (cell_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: fkidx_cell_soils_soils

-- DROP INDEX public.fkidx_cell_soils_soils;

CREATE INDEX fkidx_cell_soils_soils
    ON public.cell_soils USING btree
    (soil_id ASC NULLS LAST)
    TABLESPACE pg_default;