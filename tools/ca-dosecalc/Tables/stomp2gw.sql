-- Table: public.stomp2gw

-- DROP TABLE public.stomp2gw;

CREATE TABLE public.stomp2gw
(
    rid integer NOT NULL DEFAULT nextval('stomp2gw_rid_seq'::regclass),
    copc text COLLATE pg_catalog."default" NOT NULL,
    unit text COLLATE pg_catalog."default" NOT NULL,
    "time" integer NOT NULL,
    run_date date,
    action_case text COLLATE pg_catalog."default",
    domain_name text COLLATE pg_catalog."default" NOT NULL,
    value numeric,
    CONSTRAINT pk_stomp2gw PRIMARY KEY (rid)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.stomp2gw
    OWNER to postgres;