-- SEQUENCE: public.stomp2gw_rid_seq

-- DROP SEQUENCE public.stomp2gw_rid_seq;

CREATE SEQUENCE public.stomp2gw_rid_seq
    INCREMENT 1
    START 589008
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

ALTER SEQUENCE public.stomp2gw_rid_seq
    OWNER TO postgres;