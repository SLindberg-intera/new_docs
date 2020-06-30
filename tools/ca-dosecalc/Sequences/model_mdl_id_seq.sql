-- SEQUENCE: public.model_mdl_id_seq

-- DROP SEQUENCE public.model_mdl_id_seq;

CREATE SEQUENCE public.model_mdl_id_seq
    INCREMENT 1
    START 16
    MINVALUE 1
    MAXVALUE 32767
    CACHE 1;

ALTER SEQUENCE public.model_mdl_id_seq
    OWNER TO postgres;