-- Table: public.concentrations

-- DROP TABLE public.concentrations;

CREATE unlogged TABLE public.concentrations
(
    cell_id integer NOT NULL,
    mdl_id integer NOT NULL,
    contam_nm character varying(32) COLLATE pg_catalog."default" NOT NULL,
    elapsed_tm integer NOT NULL,
    concentration numeric,
    stress_period integer NOT NULL,
    time_step integer,
    CONSTRAINT fk_dose_copc FOREIGN KEY (contam_nm, mdl_id)
        REFERENCES public.copc (contam_nm, mdl_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE,
    CONSTRAINT fk_dose_grid FOREIGN KEY (cell_id)
        REFERENCES public.cells (cell_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.concentrations
    OWNER to postgres;

COMMENT ON COLUMN public.concentrations.cell_id
    IS 'A reference to the grid identifier.';

COMMENT ON COLUMN public.concentrations.mdl_id
    IS 'A reference to the copc identifier.';

COMMENT ON COLUMN public.concentrations.contam_nm
    IS 'A reference to the copc identifier.';

COMMENT ON COLUMN public.concentrations.elapsed_tm
    IS 'The stress period of the model.';

COMMENT ON COLUMN public.concentrations.concentration
    IS 'The concentration of the copc.';

-- Index: idx_concentrations

-- DROP INDEX public.idx_concentrations;

CREATE INDEX idx_concentrations
    ON public.concentrations USING btree
    (cell_id ASC NULLS LAST, mdl_id ASC NULLS LAST, contam_nm COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
