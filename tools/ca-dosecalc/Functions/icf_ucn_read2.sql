-- FUNCTION: public.icf_ucn_read2(character varying, integer, numeric)

-- DROP FUNCTION public.icf_ucn_read2(character varying, integer, numeric);

CREATE OR REPLACE FUNCTION public.icf_ucn_read2(
	fname character varying,
	layerin integer,
	thresh numeric)
    RETURNS TABLE(mlayer integer, mrow integer, mcolumn integer, stress_period integer, time_step integer, elapsed_time numeric, concentration numeric) 
    LANGUAGE 'plpython3u'

    COST 100
    VOLATILE 
    ROWS 1000000
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
			df = pd.DataFrame({'mlayer':l.flatten(),'mrow':r.flatten(),'mcolumn':c.flatten(),'stress_period':sp[t.flatten(),1],'time_step':sp[t.flatten(),0],'elapsed_time':ts[t.flatten()],'concentration':dat.flatten()}, columns=['mlayer','mrow','mcolumn','stress_period','time_step','elapsed_time','concentration']).to_records(index=False)
	else:
			dat = uo.get_alldata(mflay=layerin)
			t, r, c = np.indices(dat.shape)
			l = np.repeat(layerin,np.prod(dat.shape))
			df = pd.DataFrame({'mlayer':l,'mrow':r.flatten(),'mcolumn':c.flatten(),'stress_period':sp[t.flatten(),1],'time_step':sp[t.flatten(),0],'elapsed_time':ts[t.flatten()],'concentration':dat.flatten()}, columns=['mlayer','mrow','mcolumn','stress_period','time_step','elapsed_time','concentration']).to_records(index=False)
	return df[df['concentration']>=thresh]
$BODY$;

ALTER FUNCTION public.icf_ucn_read2(character varying, integer, numeric)
    OWNER TO ca;
