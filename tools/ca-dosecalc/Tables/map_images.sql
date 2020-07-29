-- Table: public.map_images

-- DROP TABLE public.map_images;

CREATE TABLE public.map_images
(
    img_id bigint NOT NULL DEFAULT nextval('map_image_img_id_seq'::regclass),
    mdl_id bigint NOT NULL,
    img_nm text COLLATE pg_catalog."default" NOT NULL,
    img_loc citext COLLATE pg_catalog."default",
    img_object bytea NOT NULL,
    CONSTRAINT pk_map_images PRIMARY KEY (img_id),
    CONSTRAINT fk_model_map_image FOREIGN KEY (mdl_id)
        REFERENCES public.models (mdl_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.map_images
    OWNER to postgres;
COMMENT ON TABLE public.map_images
    IS 'A table to store images related to a model.';

COMMENT ON COLUMN public.map_images.img_id
    IS 'Sequence generated identifier of the Map Image table.';

COMMENT ON COLUMN public.map_images.mdl_id
    IS 'A reference to the model identifier.';

COMMENT ON COLUMN public.map_images.img_nm
    IS 'The user friendly name of the image.';

COMMENT ON COLUMN public.map_images.img_loc
    IS 'The url of the image.';

COMMENT ON COLUMN public.map_images.img_object
    IS 'The binary byte array representation of the image.';

-- Index: idx_map_images

-- DROP INDEX public.idx_map_images;

CREATE UNIQUE INDEX idx_map_images
    ON public.map_images USING btree
    (mdl_id ASC NULLS LAST, img_nm COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;