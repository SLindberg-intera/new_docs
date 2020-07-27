-- FUNCTION: public.icf_util_copy_model(smallint, character varying, text, smallint, smallint, character varying, timestamp without time zone, integer)

-- DROP FUNCTION public.icf_util_copy_model(smallint, character varying, text, smallint, smallint, character varying, timestamp without time zone, integer);

CREATE OR REPLACE FUNCTION public.icf_util_copy_model(
	p_copymodleid smallint,
	p_modelname character varying DEFAULT NULL::character varying,
	p_modelscenario text DEFAULT NULL::text,
	p_modelversion smallint DEFAULT NULL::smallint,
	p_modelsubversion smallint DEFAULT NULL::smallint,
	p_modeldesc character varying DEFAULT NULL::character varying,
	p_modelexectime timestamp without time zone DEFAULT NULL::timestamp without time zone,
	p_modelstartyear integer DEFAULT NULL::integer)
    RETURNS integer
    LANGUAGE 'plpgsql'

    COST 100
    VOLATILE 
AS $BODY$
declare 
	new_mdl_id smallint;
	v_mdlnm varchar;
	v_mdlsc text;
	v_mdlvr smallint;
	v_mdlsv smallint;
	v_mdldc varchar;
	v_mdlxt timestamp;
	v_mdlsy integer;
	v_mdlos integer;
	v_mdlsr integer;
begin
	select nextval('model_mdl_id_seq'::regclass) into new_mdl_id;

	select coalesce(p_modelname, mdl_nm), coalesce(p_modelscenario, mdl_scenario), coalesce(p_modelversion, mdl_ver), coalesce(p_modelsubversion, mdl_sub_ver), 
		coalesce(p_modeldesc, mdl_desc), coalesce(p_modelexectime, mdl_exec_tm), coalesce(p_modelstartyear, mdl_start_yr), mdl_lrc_offset, mdl_srid
	into 	v_mdlnm, v_mdlsc, v_mdlvr, v_mdlsv, v_mdldc, v_mdlxt, v_mdlsy, v_mdlos, v_mdlsr
	from public.models
	where mdl_id = p_copymodelid;

	insert into public.models (mdl_id, mdl_nm, mdl_scenario, mdl_ver, mdl_sub_ver, mdl_desc, mdl_exec_tm, mdl_start_yr, mdl_lrc_offset, mdl_srid)
	values (new_mdl_id, v_mdlnm, v_mdlsc, v_mdlvr, v_mdlsv, v_mdldc, v_mdlxt, v_mdlsy, v_mdlos, v_mdlsr);

	insert into public.copc (mdl_id, contam_nm, contam_long_nm, contam_desc, contam_type, unit_id, mcl, min_thresh) 
	select distinct new_mdl_id, contam_nm, contam_long_nm, contam_desc, contam_type, unit_id, mcl, min_thresh
	from public.copc
	where mdl_id = p_copymodelid
	order by 1, 2;

	insert into public.buckets (mdl_id, contam_nm, bkt_type, bkt_min, bkt_max, hex_color_code)
	with bckts as (
		select new_mdl_id, *, row_number() over (partition by mdl_id, contam_nm, bkt_type order by bkt_min) grp_id
		from public.buckets
		where mdl_id = p_copymodelid and bkt_type = 'MCL'
	), grps as (
		select distinct grp_id
		from bckts
		group by grp_id
		order by grp_id
	), copcs as (
		select new_mdl_id, mdl_id, contam_nm, mcl, grp_id, mcl * unnest(array[0.5,1,2,4,8,10]) bkt_min, mcl * unnest(array[1,2,4,8,10,'NaN'::float]) bkt_max
		from public.copc, grps
		where mdl_id = new_mdl_id
	)
	select distinct copcs.new_mdl_id, copcs.contam_nm, bckts.bkt_type, copcs.bkt_min, copcs.bkt_max, bckts.hex_color_code
	from copcs
	join bckts using (mdl_id, contam_nm, grp_id)
	order by copcs.new_mdl_id, copcs.contam_nm, bckts.bkt_type, copcs.bkt_min;

	insert into public.cells (mdl_id, row, col, lay, node, geom, del_x, del_y, del_z, node_src) 
	select new_mdl_id, row, col, lay, node, geom, del_x, del_y, del_z, node_src 
	from cells 
	where mdl_id = p_copymodleid
	order by 1, 2, 3, 4;

	insert into public.pathways (mdl_id, pathway_nm)
	select new_mdl_id, pathway_nm
	from public.pathways
	where mdl_id = p_copymodleid
	order by mdl_id, pathway_nm;

	insert into public.soil_types (mdl_id, soil_nm, soil_density, soil_moisture, dose_nm)
	select new_mdl_id, soil_nm, soil_density, soil_moisture, dose_nm
	from public.soil_types
	where mdl_id = p_copymodleid
	order by 1, 2;

	insert into public.model_shapefiles
	select distinct shp_file_id, new_mdl_id 
	from public.model_shapefiles
	where mdl_id = p_copymodleid
	order by 1;

	insert into public.cell_soils
	with mysoils as (
		select os.soil_id, ns.soil_id new_soil_id, ns.mdl_id
		from (select * from soil_types where mdl_id = p_copymodleid) os
		join (select * from soil_types where mdl_id = new_mdl_id) ns using (soil_nm)
	), mycells as (
		select oc.cell_id, nc.cell_id new_cell_id, nc.mdl_id
		from (select * from public.cells where mdl_id = p_copymodleid) oc
		join (select * from public.cells where mdl_id = new_mdl_id) nc using (node)
	)	
	select new_cell_id, new_soil_id
	from public.cell_soils 
	join mysoils s using (soil_id)
	join mycells c using (cell_id)
	order by 1, 2;

	insert into public.dose_factors (soil_id, pathway_mdl_id, pathway_nm, contam_mdl_id, contam_nm, dose_factor)
	with maps as (
		select os.mdl_id, os.soil_id, os.pathway_nm, os.contam_nm, ns.mdl_id new_mdl_id, ns.soil_id new_soil_id, ns.pathway_nm new_path, ns.contam_nm new_copc
		from (select mdl_id, soil_id, soil_nm, pathway_nm, contam_nm from soil_types s join pathways p using (mdl_id) join copc a using (mdl_id) where mdl_id = p_copymodleid) os
		join (select mdl_id, soil_id, soil_nm, pathway_nm, contam_nm from soil_types s join pathways p using (mdl_id) join copc a using (mdl_id) where mdl_id = new_mdl_id) ns using (pathway_nm, contam_nm, soil_nm)
	)
	select distinct m.new_soil_id soil_id, m.new_mdl_id pathway_mdl_id, m.new_path pathway_nm, m.new_mdl_id contam_mdl_id, m.new_copc contam_nm, d.dose_factor
	from dose_factors d
	join maps m using (soil_id, pathway_nm, contam_nm)
	where d.contam_mdl_id = p_copymodleid
	order by 1, 2, 3, 4, 5;

	return new_mdl_id;
exception
	when others then
		raise info '%',sqlerrm;
		return -1;
end;
$BODY$;

ALTER FUNCTION public.icf_util_copy_model(smallint, character varying, text, smallint, smallint, character varying, timestamp without time zone, integer)
    OWNER TO postgres;
