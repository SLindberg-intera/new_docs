-- Table: public.units

-- DROP TABLE public.units;

CREATE TABLE public.units
(
    unit_id integer NOT NULL DEFAULT nextval('units_unit_id_seq'::regclass),
    unit_in citext COLLATE pg_catalog."default" NOT NULL,
    unit_out citext COLLATE pg_catalog."default" NOT NULL,
    conversion_factor numeric NOT NULL,
    CONSTRAINT pk_units PRIMARY KEY (unit_id),
    CONSTRAINT unq_units UNIQUE (unit_in, unit_out)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.units
    OWNER to postgres;
COMMENT ON TABLE public.units
    IS 'A table to store measurement units.';

COMMENT ON COLUMN public.units.unit_id
    IS 'Sequence generated identifier of the Units table.';

COMMENT ON COLUMN public.units.unit_in
    IS 'The input unit, typically the measurement unit.';

COMMENT ON COLUMN public.units.unit_out
    IS 'The output unit, typically the reporting unit.';

COMMENT ON COLUMN public.units.conversion_factor
    IS 'The conversion factor between the input and output units.';