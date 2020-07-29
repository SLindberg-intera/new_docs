-- FUNCTION: public.icf_ucn_read(character varying, character varying, character varying, integer)

-- DROP FUNCTION public.icf_ucn_read(character varying, character varying, character varying, integer);

CREATE OR REPLACE FUNCTION public.icf_ucn_read(
	fname character varying,
	modelin character varying,
	copcin character varying,
	layerin integer)
    RETURNS TABLE(model character varying, contam character varying, mlayer integer, mrow integer, mcolumn integer, time_step integer, stress_period integer, elapsed_time numeric, concentration numeric) 
    LANGUAGE 'plpython3u'

    COST 100
    VOLATILE 
    ROWS 1000
AS $BODY$
	import os
	import numpy as np
	import pandas as pd
	import flopy.utils.binaryfile as bf
	uo = bf.UcnFile(fname, precision='double')
	sp = np.array(uo.get_kstpkper())
	ts = np.array(uo.get_times())
	if layerin == -1:
			dat = uo.get_alldata()
			t, l, r, c = np.indices(dat.shape)
			m = np.repeat(modelin,np.prod(dat.shape))
			a = np.repeat(copcin,np.prod(dat.shape))
			df = pd.DataFrame({'model':m,'contam':a,'mlayer':l.flatten(),'mrow':r.flatten(),'mcolumn':c.flatten(),'time_step':sp[t.flatten(),0],'stress_period':sp[t.flatten(),1],'elapsed_time':ts[t.flatten()],'concentration':dat.flatten()}, columns=['model','contam','mlayer','mrow','mcolumn','time_step','stress_period','elapsed_time','concentration']).to_records(index=False)
	else:
			dat = uo.get_alldata(mflay=layerin)
			t, r, c = np.indices(dat.shape)
			m = np.repeat(modelin,np.prod(dat.shape))
			a = np.repeat(copcin,np.prod(dat.shape))
			l = np.repeat(layerin,np.prod(dat.shape))
			df = pd.DataFrame({'model':m,'contam':a,'mlayer':l,'mrow':r.flatten(),'mcolumn':c.flatten(),'time_step':sp[t.flatten(),0],'stress_period':sp[t.flatten(),1],'elapsed_time':ts[t.flatten()],'concentration':dat.flatten()}, columns=['model','contam','mlayer','mrow','mcolumn','time_step','stress_period','elapsed_time','concentration']).to_records(index=False)
	return df[df['concentration']>=1E-6]
$BODY$;

ALTER FUNCTION public.icf_ucn_read(character varying, character varying, character varying, integer)
    OWNER TO ca;
