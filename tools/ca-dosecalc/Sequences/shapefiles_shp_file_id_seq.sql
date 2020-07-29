-- SEQUENCE: public.shapefiles_shp_file_id_seq

-- DROP SEQUENCE public.shapefiles_shp_file_id_seq;

CREATE SEQUENCE public.shapefiles_shp_file_id_seq
    INCREMENT 1
    START 17
    MINVALUE 1
    MAXVALUE 32767
    CACHE 1;

ALTER SEQUENCE public.shapefiles_shp_file_id_seq
    OWNER TO ca;