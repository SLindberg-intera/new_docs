import logging
import pandas as pd
import numpy as np
import os.path
#from pylib.hssmbuilder.time_series_reduction import data_reduction
from multiprocessing import get_context as context
from multiprocessing import cpu_count
from decimal import *
import datetime as dt
import pylib.gwreducer.reduce_groundwater_timeseries as rgt
from pylib.timeseries.timeseries import TimeSeries
import pylib.timeseries.timeseries_math as tsmath
import pylib.hssmbuilder.plots as plt
import scipy.signal as sig
#---------------------------------------------------------------------------
#
def setup_logger(name, log_file, formatter, level=logging.INFO):
    """Function setup as many loggers as you want"""
    # set a format which is simpler for console use

    handler = logging.FileHandler(log_file, mode='w')
    handler.setFormatter(formatter)

    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(logging.WARNING)
    streamHandler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False
    logger.addHandler(handler)
    logger.addHandler(streamHandler)
    return logger
#-------------------------------------------------------------------------------
def build_pkg(file):
    #try:
        file.set_min_step(Decimal(10*365.25),True)
        #file.set_max_step(Decimal(500*365.25),True)
        file.set_max_step(Decimal(50*365.25),True)
        max_steps=0
        new_data = []
        output =""
        if file.time:
            time_arr = file.data
        else:
            cur_date  = dt.date.today()
            time = dt.datetime.utcnow()
            lvl = logging.INFO
            formatter = logging.Formatter('%(asctime)-9s: %(levelname)-8s: %(message)s','%H:%M:%S')
            log_file = os.path.join(file.log_path,"build_i{0}-j{1}_log_{2}.txt".format(file.iSource,file.jSource,cur_date.strftime("%Y%m%d")))
            cell_logger = setup_logger(file.col,log_file,formatter,lvl)

            file.set_logger(cell_logger)
            file.check_has_data()
            #file.consolidate_entries()
            segs = []
            error = 0
            o_ts = TimeSeries(file.days,file.vals,None,None)
            r_ts = TimeSeries(file.days,file.vals,None,None)
            if file.has_data == False:
                msg_str = ("Skipping Cell i{0}-j{1}: flux never exceeds {2}".format(file.iSource,file.jSource,file.flux_floor))
                file.logger.info(msg_str)
                print(msg_str)
            else:
                non_zero_ind = np.where(file.vals > file.flux_floor)[0]
                if non_zero_ind.size < file.min_reduction_steps:
                    #add first zero after data decreases to zero
                    if non_zero_ind[-1]+1 < file.vals.size-1 and non_zero_ind[-1]+1 not in non_zero_ind:
                        non_zero_ind = np.append(non_zero_ind,non_zero_ind[-1]+1)
                    #add last zero before flux increases above zero
                    if non_zero_ind[0]-1 > 0 and non_zero_ind[0]-1 not in non_zero_ind:
                        non_zero_ind = np.append(non_zero_ind,non_zero_ind[0]-1)
                    if 0 not in non_zero_ind:
                        non_zero_ind = np.append(non_zero_ind,[0])
                    if (file.vals.size -1) not in non_zero_ind:
                        non_zero_ind = np.append(non_zero_ind,[(file.vals.size -1)])
                    non_zero_ind = np.sort(non_zero_ind)
                    days = file.days[non_zero_ind]
                    vals = file.vals[non_zero_ind]
                    segs, error = file.build_hssm_data(days,vals)
                    num_peaks, _ = sig.find_peaks(vals,width=3,rel_height=1)
                    if num_peaks.size == 0:
                        num_peaks, _ = sig.find_peaks(vals,width=2,rel_height=1)
                        if num_peaks.size == 0:
                            num_peaks, _ = sig.find_peaks(vals,width=1,rel_height=1)
                    num_peaks = num_peaks.size
                elif len(file.data) > file.min_reduction_steps and file.reduce_data:
                    #segs = file.calc_segments()

                    #start = np.where(file.vals > 0)[0][0]-1
                    #end = np.where(file.vals > 0)[0][-1]+1
                    days, vals,error,num_peaks = rgt.reduce_dataset(file.days, file.vals,
                                            file.flux_floor, file.max_tm_error)

                    segs, _ = file.build_hssm_data(days,vals)
                    r_ts = TimeSeries(days,vals,None,None)
                else:
                    num_peaks=None
                    segs, error = file.build_hssm_data(file.days,file.vals)

                file.logger.info("final data reduction produced {0} steps".format(len(segs)))
                r_ts = tsmath.interpolated(r_ts,o_ts)
                #if len(segs) > max_steps:
                #    max_steps = len(segs) + 1
                output_str = "{0} {1}\n".format(file.HSSFileName,file.inHSSFile)
                output_str += "{0} {1} {2} {3} {4}\n".format(file.kSource,file.iSource, file.jSource,
                                            file.SourceName,file.iHSSComp)
                new_data = [file.HSSFileName,segs,output_str,error,"{}-{}".format(file.iSource,file.jSource),num_peaks,r_ts,o_ts]

                i = 0
                dat_output = ""
                cell_logger.info("Building dat file: {0}".format(file.HSSFileName))

                count = 0

                #output data for cell
                consolidate = False
                c_data = 0
                #pc_data = 0
                c_count = 0
                first = True
                prev_data = []
                for rec in segs:
                    count += 1
                    dat_output += "{0} 0 {1}\n".format(hssm_obj.format_e(rec[0]),hssm_obj.format_e(rec[1]))


                with open("{0}".format(file.outputFileName),"w") as outfile:
                    outfile.write(dat_output)
                cell_logger.info("finished dat file: {0}".format(file.outputFileName))
                #if count > max_steps:
                #    max_steps = count +1

                print('processed {0}-{1} in ({2}-{3}) {4}'.format(file.iSource,file.jSource, dt.datetime.utcnow(),time,dt.datetime.utcnow()- time))
        return new_data
    #except Exception as e:
        #logger.critical('Unexpected Error: %s',e,exc_info=True)
    #    raise
    #    pass

#-------------------------------------------------------------------------------
#
class hss_file():#data_reduction):
    def __init__(self, ofn,fn, k, i, j, sn, c,tol,sy,log_p,min_steps,flux_floor,
                max_tm_error,units,dr=True):

        #data_reduction.__init__(self,i,j)
        self.version = 0.1
        self.start_year = sy
        #self.segments = []
        self.HSSFileName = fn
        self.outputFileName = ofn
        self.inHSSFile = ""
        self.kSource = k
        self.iSource = i
        self.jSource = j
        self.SourceName = sn
        self.iHSSComp = "COPC"
        self.col = c
        self.min_reduction_steps = min_steps
        #self.tolerance = tol
        self.has_data = False
        self.log_path = log_p
        self.flux_floor = flux_floor
        self.max_tm_error = max_tm_error
        self.units = units
        self.reduce_data = dr
        self.time = []
        self.flux = []
    def set_min_step(self, ms, day_unit):
        self.min_step = Decimal(ms)
        self.day_unit = day_unit
    def set_max_step(self, ms, day_unit):
        self.max_step = Decimal(ms)
        self.day_unit = day_unit
    def set_logger(self,log):
        self.logger = log
    #---------------------------------------------------------------------------
    #
    def build_hssm_data(self,days,vals):
        r_t_mass = TimeSeries(days, vals, None, None).integrate()
        t_mass = TimeSeries(self.days,self.vals,None,None).integrate()
        segs = []
        error = (t_mass.values[-1] -r_t_mass.values[-1])
        for i in range(len(days)):
            segs.append([Decimal(days[i]),Decimal(vals[i]),r_t_mass.values[i]])
        plt.summary_plot(self.days,self.vals,days, vals,self.iSource,self.jSource, self.log_path,self.units,self.start_year)
        if error != 0:
            self.logger.info("{0}-{1} tmass_error:{2}".format(self.iSource,self.jSource,error))
        return segs,error
    #---------------------------------------------------------------------------
    # convert columns to list of arrays
    def build_array(self,days,vals):
        new_arr = []
        self.vals = vals
        self.days = days
        for i in range(len(days)):
            new_arr.append([Decimal(days[i]),Decimal(vals[i])])
        self.data = new_arr

    #---------------------------------------------------------------------------
    #obsolete
    def consolidate_entries(self):
        d_len = len(self.data)
        new_data = []
        self.has_data = False
        for i in range(d_len):
            # check if flux ever exceeds 0
            if self.data[i][1] > self.flux_floor:
                self.has_data = True
            #always keep first year
            if i == 0:
                new_data.append(self.data[i])
            #always keep last year
            elif i == d_len-1:
                new_data.append(self.data[i])
            #cur year conc != next conc then keep.
            # this will consolidate concentrations that already
            # the same accross consecutive years into the last
            # year.
            elif self.data[i][1] != self.data[i+1][1]:
                new_data.append(self.data[i])
        self.data = []
        self.data = new_data
    #---------------------------------------------------------------------------
    #
    def check_has_data(self):
        d_len = len(self.data)
        new_data = []
        self.has_data = False
        if np.any(self.vals > self.flux_floor):
            self.has_data = True

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# build package object
class hssm_obj:
    def __init__(self, sat, cel,params,log,log_p,misc_p,min_steps=200):

        self.saturation = sat
        self.cells = cel
        self.head = self.cells.loc[:, self.cells.columns != 'days'].columns.values
        if "output" in params.keys():
            self.path = params["output"]
        else:
            self.path = "output/"
        self.tolerance = params["tolerance"]
        self.start_year = params["start_year"]
        self.end_year = params["end_year"]
        self.log_path = log_p
        self.misc_path = misc_p
        self.reduced_data = []
        self.logger = logging.getLogger(log)
        self.flux_floor = params["flux_floor"]
        self.max_tm_error =params["max_tm_error"]
        self.min_reduction_steps = min_steps
        self.units = params["units"]
        self.data_reduction = params["data_reduction"]
        if "HSSpath" in params.keys():
            self.HSSpath = params["HSSpath"]
        else:
            self.HSSpath = "./hss/"
    #---------------------------------------------------------------------------
    #
    def build_data(self):
        data = []
        days = self.cells.loc[:,'days'].values
        list = []

        for i in range(self.head.size):

            str_ind = self.head[i].find('-')
            try:
                i_ind = int(self.head[i][0:str_ind])
                j_ind = int(self.head[i][str_ind+1:])
                try:
                    k = int(self.saturation.loc[(i_ind,j_ind),'k'])
                except:
                    k = 0
                    self.logger.info("{} Error: could not find saturation layer".format(self.head[i]))
                    print("{} Error: could not find saturation layer".format(self.head[i]))
                #print('{0}-{1}:{2} ({3})'.format(i_ind, j_ind,k,self.saturation.loc[(i_ind-1,j_ind-1),'k']))
                list.append('{0}-{1}'.format(i_ind, j_ind))
            except:
                #self.logger.critical("Invalid header format {0}".format(self.head[i]))
                raise
            out_fileName = "{0}i{1}j{2}_hss.dat".format(self.path,i_ind,j_ind)
            HSSFileName = "{0}i{1}j{2}_hss.dat".format(self.HSSpath,i_ind,j_ind)
            rec = hss_file(out_fileName,HSSFileName,k,i_ind,j_ind,1,self.head[i],
                            self.tolerance,self.start_year,self.log_path,
                            self.min_reduction_steps,self.flux_floor,
                            self.max_tm_error,self.units,self.data_reduction)
            values = self.cells.loc[:,self.head[i]].values
            rec.build_array(days,values)

            data.append(rec)

        return data

    #-------------------------------------------------------------------------------
    @staticmethod
    def format_e(n):
        if n == 0.0:
            a = n
        else:
            try:
                a = '%.10E' % n
                a = a.split('E')[0].rstrip('0').rstrip('.') + 'E' + a.split('E')[1]
            except:
                print (n)
                raise
        return a #a.split('E')[0].rstrip('0').rstrip('.') + 'E' + a.split('E')[1]

    #-------------------------------------------------------------------------------
    # write data
    def write_data(self):

        time_arr = []
        new_data = []
        max_lines = []
        data = self.build_data()
        procs = cpu_count()
        if procs > 3:
            procs = 3
        #with context("spawn").Pool(processes=procs) as pool:
        with context("spawn").Pool(processes=1) as pool:
            self.reduced_data = pool.map(build_pkg,data )

        file_str = ""
        num_files = 0
        max_steps = 0
        for x in self.reduced_data:
            if len(x) > 1:
                file_str += x[2]
                num_files += 1
                if len(x[1]) >= max_steps:
                    max_steps = len((x[1]))+5
        self.logger.info("Building dat file: mt3d.hss")
        output = "{0} {1} {2} NoRunHSSM\n".format(num_files, 1,max_steps)
        output += "{0} {1} {2}\n".format(1, 1, 1)
        output += "{0}\n{1}".format(num_files,file_str)
        with open("{0}mt3d.hss".format(self.path),"w") as outfile:
            outfile.write(output)

        #self.misc_files()
        self.misc_file_generation()
        self.misc_files()
        self.error_check()
    #---------------------------------------------------------------------------
    #
    def error_check(self):
        start = 0
        #if first position does not have data look for first data set that does
        if len(self.reduced_data[0]) < 8:
            for i in range(0,len(self.reduced_data)):
                if len(self.reduced_data[i]) >= 8:
                    start = i
                    break
        #check to make sure data was found
        if len(self.reduced_data[start]) >= 8:
            #o_ts = TimeSeries(self.reduced_data[start][7].times,np.zeros(self.reduced_data[start][7].times.size),None,None)
            cols = list(self.cells.columns)
            cols.remove('days')
            o_ts = TimeSeries(self.cells['days'].values,self.cells[cols].sum(axis=1).values,None,None)

            r_ts = TimeSeries(o_ts.times,np.zeros(o_ts.times.size),None,None)
            check_cells = pd.DataFrame()
            for data in self.reduced_data:
                if len(data) >= 8:
                    #o_ts.values += data[7].values
                    #interp_fn = tsmath.interpolate(data[6])
                    #interp_values = interp_fn(o_ts.times)
                    #r_ts.values += interp_values
                    r_ts.values += tsmath.interpolated(data[6],o_ts).values
                    #check mass differences for cell
                    r_t_mass = data[6].integrate()
                    t_mass = data[7].integrate()
                    d_mass_ts = tsmath.delta(t_mass,r_t_mass)
                    p_mass_ts = TimeSeries(d_mass_ts.times,d_mass_ts.values /t_mass.values,None,None)

                    d_flux_ts = tsmath.delta(data[7],data[6])
                    p_flux_ts = TimeSeries(d_flux_ts.times,d_flux_ts.values /data[7].values,None,None)

                    error_mass_ind = np.where(p_mass_ts.values > .1)[0]
                    error_flux_ind = np.where(p_flux_ts.values > .1)[0]
                    if len(error_mass_ind) > 0:
                        t_data = pd.DataFrame(d_mass_ts.times[error_mass_ind],columns=["{} day".format(data[0])])
                        check_cells = pd.concat([check_cells,t_data],axis=1,sort=False)
                        t_data = pd.DataFrame(d_mass_ts.values[error_mass_ind],columns=["mass difference (pCi)"])
                        check_cells = pd.concat([check_cells,t_data],axis=1,sort=False)
                        t_data = pd.DataFrame(p_mass_ts.values[error_mass_ind],columns=["% mass difference".format(data[0])])
                        check_cells = pd.concat([check_cells,t_data],axis=1,sort=False)
                    if len(error_flux_ind) > 0:
                        t_data = pd.DataFrame(d_flux_ts.times[error_flux_ind],columns=["{} day".format(data[0])])
                        check_cells = pd.concat([check_cells,t_data],axis=1,sort=False)
                        t_data = pd.DataFrame(d_flux_ts.values[error_flux_ind],columns=["flux difference (pCi/day)".format(data[0])])
                        check_cells = pd.concat([check_cells,t_data],axis=1,sort=False)
                        t_data = pd.DataFrame(p_flux_ts.values[error_flux_ind],columns=["% flux difference".format(data[0])])
                        check_cells = pd.concat([check_cells,t_data],axis=1,sort=False)

            #write file with mass error issues
            fileName = os.path.join(self.misc_path,'cell_mass_error_year.csv')
            check_cells.to_csv(fileName, header=True)
            #finish processing total mass differences
            o_mass_ts = o_ts.integrate()
            r_mass_ts = r_ts.integrate()
            d_ts = tsmath.delta(o_ts,r_ts)
            d_mass_ts = tsmath.delta(o_mass_ts,r_mass_ts)

            output = "year,day,original rate ({0}/day),reduced rate ({0}/day),original mass ({0}),reduced mass ({0}), rate error, mass error\n".format(self.units)
            for i in range(0,o_ts.times.size):
                day = o_ts.times[i]
                year = (day/365.25)+self.start_year
                d_flux = o_ts.values[i]-r_ts.values[i]
                p_flux = d_flux / o_ts.values[i]
                d_mass = o_mass_ts.values[i]-r_mass_ts.values[i]
                p_mass = d_mass / o_mass_ts.values[i]
                output += "{},{},{},{},{},{},{} ({}%),{} ({}%)\n".format(year,day,
                            o_ts.values[i],r_ts.values[i],o_mass_ts.values[i],
                            r_mass_ts.values[i],d_flux,p_flux,d_mass,p_mass)
            fileName = os.path.join(self.misc_path,'net_error_by_year.csv')
            with open(fileName,"w") as outfile:
                outfile.write(output)
            plt.summary_plot(o_ts.times,o_ts.values,r_ts.times,r_ts.values,0,0, self.log_path,self.units,self.start_year,True)
    #---------------------------------------------------------------------------
    #
    def misc_files(self):
        cols = ['cell','#pts','total_mass_error','%error','peaks_found']
        cells = pd.DataFrame(columns=cols)
        days = self.cells.loc[:,'days'].values
        for x in self.reduced_data:
            if len(x) > 0:
                values = self.cells.loc[:,x[4]].values
                ts = TimeSeries(days,values,None,None)
                total_mass = ts.integrate().values[-1]
                p_error = x[3]/total_mass

                temp = pd.DataFrame(np.array([[x[0],len(x[1]),x[3],p_error,x[5]]]),columns=cols)
                cells = cells.append(temp)

        fileName = os.path.join(self.misc_path,'cell_error.csv')
        cells.to_csv(fileName, header=True)

    #---------------------------------------------------------------------------
    #
    def misc_file_generation(self):
        #--Build consolidated output file
        yearly_output = ""
        output = ""
        cols = ""
        first = True
        total_cum = 0
        keys = self.cells.index.values
        keys.sort()

        for i in range(len(keys)):
            total_flux = self.cells.loc[keys[i], self.cells.columns != 'days'].sum()
            #days = self.cells.loc[keys[i],'days'].values
            days = self.cells.loc[keys[i],'days']
            # if prev rec is set then calculate cumulative mass
            if i > 0:
                total_cum += total_flux *  (keys[i] - keys[i-1])
            # else this is the first rec so no calculation needed.
            else:
                total_cum = total_flux
            #convert to ci (1E-12) from pCi, for second cumulative column
            total_cum_ci = total_cum * .000000000001
            output += "{0},{1},{2},{3}".format(days,total_flux,total_cum,total_cum_ci)
            yearly_output += "{0},{1},{2}\n".format(keys[i] /365.25 + self.start_year,(total_flux * 365.25)*.000000000001,total_cum_ci)
            for x in self.reduced_data:
                if (len(x) > 0):

                    if (len(x[1]) > i):
                        cur_rec = x[1][i]
                        #logger.debug(cur_rec)
                        if first:
                            cols += ",day,{0},cumulative".format(x[0])
                        #if len(output) < 1:
                        #    output += "{0},{1},{2}".format(cur_rec[0],cur_rec[1],cur_rec[2])
                        #else:
                        output += ",{0},{1},{2}".format(cur_rec[0],cur_rec[1],cur_rec[2])

                    else:
                        output += ",,,"

            if len(cols) > 3:
                output += "\n"
                first = False
        output = "days,total flux(pCi), total cumulative(pCi),total cumulative(ci){0}\n{1}".format(cols,output)
        yearly_output = "years,total flux(Ci), total cumulative(Ci)\n{0}".format(yearly_output)
        fileName = os.path.join(self.misc_path,'full_data_set.csv')
        with open(fileName,"w") as outfile:
            outfile.write(output)
        fileName = os.path.join(self.misc_path,'cumulative_data_set_by_year.csv')
        with open(fileName,"w") as outfile:
            outfile.write(yearly_output)
