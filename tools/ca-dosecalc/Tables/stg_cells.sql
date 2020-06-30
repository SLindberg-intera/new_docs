-- Table: public.stg_cells

-- DROP TABLE public.stg_cells;

CREATE TABLE public.stg_cells
(
    new_mdl_id integer,
    new_cell_id bigint,
    old_mdl_id integer,
    old_cell_id bigint,
    "row" integer,
    col integer,
    lay integer,
    node integer,
    geom geometry,
    del_x numeric,
    del_y numeric,
    del_z numeric,
    node_src character varying(255) COLLATE pg_catalog."default"
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.stg_cells
    OWNER to ca;