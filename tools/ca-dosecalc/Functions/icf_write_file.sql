-- FUNCTION: public.icf_write_file(bytea, text)

-- DROP FUNCTION public.icf_write_file(bytea, text);

CREATE OR REPLACE FUNCTION public.icf_write_file(
	param_bytes bytea,
	param_filepath text)
    RETURNS text
    LANGUAGE 'plpython3u'

    COST 100
    VOLATILE 
AS $BODY$
	f = open(param_filepath, 'wb+')
	f.write(param_bytes)
	f.close()
	return param_filepath
$BODY$;

ALTER FUNCTION public.icf_write_file(bytea, text)
    OWNER TO ca;
