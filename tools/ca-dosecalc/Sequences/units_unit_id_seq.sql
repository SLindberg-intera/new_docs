-- SEQUENCE: public.units_unit_id_seq

-- DROP SEQUENCE public.units_unit_id_seq;

CREATE SEQUENCE public.units_unit_id_seq
    INCREMENT 1
    START 3
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

ALTER SEQUENCE public.units_unit_id_seq
    OWNER TO postgres;