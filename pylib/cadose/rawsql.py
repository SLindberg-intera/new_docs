
pathways = [""" drop table if exists public.pathways""",
   """CREATE TABLE public.pathways(
     mdl_id integer NOT NULL,
     pathway_nm character varying(32) COLLATE pg_catalog."default" NOT NULL,
     pathway_desc character varying(255) COLLATE pg_catalog."default",
     CONSTRAINT pk_pathways PRIMARY KEY (mdl_id, pathway_nm))
    WITH ( OIDS = FALSE ) TABLESPACE pg_default;""",
    """ALTER TABLE public.pathways OWNER to postgres""",
    """COMMENT ON TABLE public.pathways
         IS 'A table to store the models allowed dose pathway names.'""",
    """COMMENT ON COLUMN public.pathways.mdl_id
     IS 'A reference to the model identifier.'""",
    """ COMMENT ON COLUMN public.pathways.pathway_nm
     IS 'The unique pathway name.'""",
    """ COMMENT ON COLUMN public.pathways.pathway_desc
     IS 'A description of the pathway.'""",
     "select * from public.pathways"
]

copc = [
 "drop table if exists public.copc",
 """CREATE TABLE public.copc (
    contam_nm character varying(32) COLLATE pg_catalog."default" NOT NULL,
    contam_long_nm character varying(255) COLLATE pg_catalog."default",
    contam_desc character varying(255) COLLATE pg_catalog."default",
    mcl numeric NOT NULL DEFAULT 0,
    unit_id integer NOT NULL,
    min_thresh numeric DEFAULT 0.0,
    contam_type text COLLATE pg_catalog."default",
    CONSTRAINT pk_copc PRIMARY KEY (contam_nm),
    CONSTRAINT unq_copc UNIQUE (mdl_id, contam_nm, contam_long_nm),
    CONSTRAINT fk_model_copc FOREIGN KEY (mdl_id)
                                                            REFERENCES public.models (mdl_id) MATCH SIMPLE
                                                                    ON UPDATE NO ACTION
                                                                            ON DELETE CASCADE
                                                                            )
WITH (
            OIDS = FALSE
            )
TABLESPACE pg_default;

ALTER TABLE public.copc
    OWNER to postgres;
    COMMENT ON TABLE public.copc
        IS 'A table to store the models contaminants of potential concern.';

        COMMENT ON COLUMN public.copc.mdl_id
            IS 'A reference to the model identifier.';

            COMMENT ON COLUMN public.copc.contam_nm
                IS 'The short name of the contaminant of potiential concern.';

                COMMENT ON COLUMN public.copc.contam_long_nm
                    IS 'The full name of the contaminant of potiential concern.';

                    COMMENT ON COLUMN public.copc.contam_desc
                        IS 'A description of the contaminant of potiential concern.';

                        COMMENT ON COLUMN public.copc.mcl
                            IS 'The mininum concentration for inclusion in the dose calculation.';

                            COMMENT ON COLUMN public.copc.unit_id
                                IS 'The measurement unit of the analyte.';
                                -- Index: fkidx_cells_mdl_id

                                -- DROP INDEX public.fkidx_cells_mdl_id;

                                CREATE INDEX fkidx_cells_mdl_id
                                    ON public.copc USING btree
                                        (mdl_id ASC NULLS LAST)
                                            TABLESPACE pg_default;
