-- SEQUENCE: public.soil_type_soil_id_seq

-- DROP SEQUENCE public.soil_type_soil_id_seq;

CREATE SEQUENCE public.soil_type_soil_id_seq
    INCREMENT 1
    START 102
    MINVALUE 1
    MAXVALUE 32767
    CACHE 1;

ALTER SEQUENCE public.soil_type_soil_id_seq
    OWNER TO postgres;