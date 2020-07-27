-- SEQUENCE: public.concentration_bucket_bkt_id_seq

-- DROP SEQUENCE public.concentration_bucket_bkt_id_seq;

CREATE SEQUENCE public.concentration_bucket_bkt_id_seq
    INCREMENT 1
    START 2336
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 1;

ALTER SEQUENCE public.concentration_bucket_bkt_id_seq
    OWNER TO postgres;