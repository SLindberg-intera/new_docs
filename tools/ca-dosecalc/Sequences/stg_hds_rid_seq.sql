-- SEQUENCE: public.stg_hds_rid_seq

-- DROP SEQUENCE public.stg_hds_rid_seq;

CREATE SEQUENCE public.stg_hds_rid_seq
    INCREMENT 1
    START 7
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 1;

ALTER SEQUENCE public.stg_hds_rid_seq
    OWNER TO postgres;