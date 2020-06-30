-- Table: public.cell_heads

-- DROP TABLE public.cell_heads;

CREATE TABLE public.cell_heads
(
    cell_id integer NOT NULL,
    stress_period integer NOT NULL,
    time_step numeric NOT NULL,
    head numeric,
    CONSTRAINT pk_cell_heads PRIMARY KEY (cell_id, stress_period, time_step),
    CONSTRAINT fk_grid_grid_head FOREIGN KEY (cell_id)
        REFERENCES public.cells (cell_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.cell_heads
    OWNER to postgres;

COMMENT ON COLUMN public.cell_heads.cell_id
    IS 'A reference to the grid identifier.';

COMMENT ON COLUMN public.cell_heads.stress_period
    IS 'The stress period of the model.';

COMMENT ON COLUMN public.cell_heads.time_step
    IS 'The time step of the model.';

COMMENT ON COLUMN public.cell_heads.head
    IS 'The head value of the grid cell at the specified time.';