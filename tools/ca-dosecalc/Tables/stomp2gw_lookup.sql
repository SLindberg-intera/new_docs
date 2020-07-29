-- Table: public.stomp2gw_lookup

-- DROP TABLE public.stomp2gw_lookup;

CREATE TABLE public.stomp2gw_lookup
(
    prp_value text COLLATE pg_catalog."default",
    id smallint NOT NULL,
    domain_name text COLLATE pg_catalog."default",
    CONSTRAINT stomp2gw_lookup_pkey PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.stomp2gw_lookup
    OWNER to ca;