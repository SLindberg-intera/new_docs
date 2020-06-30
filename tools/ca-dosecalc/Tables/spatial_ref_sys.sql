-- Table: public.spatial_ref_sys

-- DROP TABLE public.spatial_ref_sys;

CREATE TABLE public.spatial_ref_sys
(
    srid integer NOT NULL,
    auth_name character varying(256) COLLATE pg_catalog."default",
    auth_srid integer,
    srtext character varying(2048) COLLATE pg_catalog."default",
    proj4text character varying(2048) COLLATE pg_catalog."default",
    CONSTRAINT spatial_ref_sys_pkey PRIMARY KEY (srid),
    CONSTRAINT spatial_ref_sys_srid_check CHECK (srid > 0 AND srid <= 998999)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.spatial_ref_sys
    OWNER to ca;

GRANT ALL ON TABLE public.spatial_ref_sys TO ca;

GRANT SELECT ON TABLE public.spatial_ref_sys TO PUBLIC;