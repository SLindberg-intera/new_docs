import sys, os
sys.path.append(
        os.path.join(os.path.dirname(__file__), '..','..'))
import logging
import numpy as np
import pandas as pd
import os.path
#from pylib.hssmbuilder.time_series_reduction import data_reduction

from multiprocessing import get_context as context
from multiprocessing import cpu_count
from decimal import *
import datetime as dt
import scipy.signal as sig
#custom libraries
import pylib.hssmbuilder.gwreducer.reduce_groundwater_timeseries as rgt
from pylib.hssmbuilder.timeseries.timeseries import TimeSeries
import pylib.hssmbuilder.timeseries.timeseries_math as tsmath
from pylib.hssmbuilder.datareduction.reduction_result import ReductionResult
import pylib.hssmbuilder.plots as plt

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
#
def build_pkg(file):
    #try:
        new_data = []
        if file.time:
            time_arr = file.data
        else:
            cur_date  = dt.date.today()
            time = dt.datetime.utcnow()
            lvl = logging.INFO
            formatter = logging.Formatter('%(asctime)-9s: %(levelname)-8s: %(message)s','%H:%M:%S')
            log_file = os.path.join(file.log_path,"build_i{0}-j{1}-k{3}_log_{2}.txt".format(file.iSource,file.jSource,cur_date.strftime("%Y%m%d"),file.kSource))
            cell_logger = setup_logger(log_file,log_file,formatter,lvl)

            file.set_logger(cell_logger)
            file.check_has_data()
            segs = []
            error = 0
            days = file.days
            vals = file.vals
            o_ts = TimeSeries(file.days,file.vals,None,None)
            o_mass = o_ts.integrate().values[-1]
            r_ts = TimeSeries(days,vals,None,None)
            num_peaks = None
            #non_zero_ind = np.where(file.vals > (file.flux_floor * 365.25))[0]
            if file.has_data == False:# or non_zero_ind.size < file.min_reduction_steps:
                msg_str = ("Skipping Cell i{0}-j{1}; k{4}: total mass={5}; flux never exceeds {2} {3}/day".format(file.iSource,file.jSource,file.flux_floor, file.units,file.kSource,file.vals.sum()*365.25))
                file.logger.info(msg_str)
                print(msg_str)
                new_data = ["i{}j{}k{}".format(file.iSource,file.jSource,file.kSource),o_ts]
            else:
                #check if allowing any steps greater than flux_floor yearly is below min_reduction_steps
                #non_zero_ind = file.remove_zero_flux()
                #non_zero_ind = rgt.remove_zero_flux(file.days,file.vals,file.flux_floor,file.min_reduction_steps)
                non_zero_ind, min_zero_years = rgt.remove_begin_end_zero_flux(file.days,file.vals,file.flux_floor,file.min_reduction_steps)

                ix = 0
                r_ts = TimeSeries(file.days[non_zero_ind],file.vals[non_zero_ind],None,None)
                r_mass = r_ts.integrate().values[-1]
                #check if allowing only steps greater than flux floor (converted to year vs dayly) reduces steps to below min_reduction_steps

                if abs(o_mass - r_mass) < (file.flux_floor) and non_zero_ind.size < file.min_reduction_steps and non_zero_ind.size > 1 and file.reduce_data:
                    days = file.days[non_zero_ind]
                    vals = file.vals[non_zero_ind]

    #                    segs, error = file.build_hssm_data(days,vals)
    #                    num_peaks, _ = sig.find_peaks(vals,width=3,rel_height=1)
    #                    if num_peaks.size == 0:
    #                        num_peaks, _ = sig.find_peaks(vals,width=2,rel_height=1)
    #                        if num_peaks.size == 0:
    #                            num_peaks, _ = sig.find_peaks(vals,width=1,rel_height=1)
    #                    num_peaks = num_peaks.size
    #                    r_ts = TimeSeries(days,vals,None,None)
                #if (flux never rises above flux_floor and there are more than min_reduction_steps) or o_mass == 0 skip.
                #  This is due to splitting cells into layers you may have less than 200 years in a single layer, and removing
                #  the layer can have adverse consequences to the overall cell error if removed.
                #elif file.has_data == False:
                #    msg_str = ("Skipping Cell i{0}-j{1}; k{4}: total mass={5}; flux never exceeds {2} {3}/day".format(file.iSource,file.jSource,file.flux_floor, file.units,file.kSource,file.vals.sum()*365.25))
                #    file.logger.info(msg_str)
                #    print(msg_str)
                #    return ["i{}j{}k{}".format(file.iSource,file.jSource,file.kSource),o_ts]
                elif len(file.data) > file.min_reduction_steps and file.reduce_data:
                    days, vals,error,num_peaks,ix = rgt.reduce_dataset(file.days, file.vals, file.flux_floor, file.max_tm_error, file.min_reduction_steps)
                    #if file.days[min_zero_years[0]] not in days or file.days[min_zero_years[1]] not in days or file.days[min_zero_years[2]] not in days or file.days[min_zero_years[3]] not in days:
                        #print(file.HSSFileName)
                        #print(file.days[min_zero_years])
                    #segs, _ = file.build_hssm_data(days,vals)
                    #r_ts = TimeSeries(days,vals,None,None)
    #                else:
    #                    num_peaks=None
    #                    segs, error = file.build_hssm_data(file.days,file.vals)
                segs, error = file.build_hssm_data(days,vals)
                if num_peaks == None:
                    num_peaks, _ = sig.find_peaks(vals,width=3,rel_height=1)
                    if num_peaks.size == 0:
                        num_peaks, _ = sig.find_peaks(vals,width=2,rel_height=1)
                        if num_peaks.size == 0:
                            num_peaks, _ = sig.find_peaks(vals,width=1,rel_height=1)
                    num_peaks = num_peaks.size

                r_ts = TimeSeries(days,vals,None,None)
                file.logger.info("final data reduction produced {0} steps".format(len(segs)))

                r_ts = tsmath.interpolated(r_ts,o_ts)

                output_str = "{0} {1}\n".format(file.HSSFileName,file.inHSSFile)
                output_str += "{0} {1} {2} {3} {4}\n".format(file.kSource,file.iSource, file.jSource,
                                            file.SourceName,file.iHSSComp)
                new_data = [file.HSSFileName,segs,output_str,error,"{}-{}".format(file.iSource,file.jSource),num_peaks,r_ts,o_ts,file.kSource]

                i = 0
                dat_output = ""
                cell_logger.info("Building dat file: {0}".format(file.outputFileName))

                count = 0

                #output data for cell
                consolidate = False
                c_data = 0
                #pc_data = 0
                c_count = 0
                first = True
                prev_data = []
                cell_logger.info("timeseries:")
                for rec in segs:
                    count += 1
                    cell_logger.info("{0} 0 {1}".format(rec[0],rec[1]))
                    dat_output += "{0} 0 {1}\n".format(hssm_obj.format_e(rec[0]),hssm_obj.format_e(rec[1]))


                with open("{0}".format(file.outputFileName),"w") as outfile:
                    outfile.write(dat_output)
                cell_logger.info("finished dat file: {0}".format(file.outputFileName))
                #if count > max_steps:
                #    max_steps = count +1

                print('processed {0}-{1};k{4} in ({2} iterations) {3} time'.format(file.iSource,file.jSource, ix,dt.datetime.utcnow()- time,file.kSource))
            return new_data
    #except Exception as e:
        #logger.critical('Unexpected Error: %s',e,exc_info=True)
    #    raise
    #    pass

#-------------------------------------------------------------------------------
# Individual cell object
class hss_file():#data_reduction):
    def __init__(self, ofn,fn, k, i, j, sn, c,tol,sy,log_p,min_steps,flux_floor,
                max_tm_error,units,graph_name,copc,dr=True):

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
        self.copc = copc
        self.graph_name = graph_name
    def set_min_step(self, ms, day_unit):
        self.min_step = Decimal(ms)
        self.day_unit = day_unit
    def set_max_step(self, ms, day_unit):
        self.max_step = Decimal(ms)
        self.day_unit = day_unit
    def set_logger(self,log):
        self.logger = log
        self.logger.info("Initiated Data reduction for cell {0}-{1}".format(self.iSource,self.jSource))

    #---------------------------------------------------------------------------
    # build timeseries format for HSSM package .dat file and create summaryplot
    # for the cell
    def build_hssm_data(self,days,vals):
        r_t_mass = TimeSeries(days, vals, None, None).integrate()
        t_mass = TimeSeries(self.days,self.vals,None,None).integrate()
        segs = []
        error = (t_mass.values[-1] -r_t_mass.values[-1])
        for i in range(len(days)):
            segs.append([Decimal(days[i]),Decimal(vals[i]),r_t_mass.values[i]])
        jk = "{}(k{})".format(self.jSource,self.kSource)
        #plt.summary_plot(self.days,self.vals,days, vals,self.iSource,self.jSource, self.log_path,self.units,self.start_year,self.graph_name,self.copc)
        plt.summary_plot(self.days,self.vals,days, vals,self.iSource,jk, self.log_path,self.units,self.start_year,self.graph_name,self.copc)
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
    # convert columns to list of arrays, used for spliting original data between
    # layers.  days/values will be only a portion of the data, so need to filled
    # in days and values between start and end day that are not covered by Days
    # with zeros for vals
    def build_array_fill_empty(self,start_day,end_day,days,vals):
        new_arr = []
        new_vals = []
        self.days = np.arange(start_day, end_day+.1,365.25)
        for day in self.days:
            val = 0
            if day in days:
                val = vals[days.index(day)]
            new_arr.append([Decimal(day),Decimal(val)])
            new_vals.append(val)
        if len(new_vals) != len(self.days):
            print("number of Values: {} != number of days: {}".format(len(new_vals),len(self.days)))
            raise
        else:
            self.vals = np.array(new_vals)
        self.data = new_arr
    #---------------------------------------------------------------------------
    #obsolete
    #def consolidate_entries(self):
    #    d_len = len(self.data)
    #    new_data = []
    #    self.has_data = False
    #    for i in range(d_len):
            # check if flux ever exceeds 0
    #        if self.data[i][1] > self.flux_floor:
    #            self.has_data = True
            #always keep first year
    #        if i == 0:
    #            new_data.append(self.data[i])
            #always keep last year
    #        elif i == d_len-1:
    #            new_data.append(self.data[i])
            #cur year conc != next conc then keep.
            # this will consolidate concentrations that already
            # the same accross consecutive years into the last
            # year.
    #        elif self.data[i][1] != self.data[i+1][1]:
    #            new_data.append(self.data[i])

    #    self.data = []
    #    self.data = new_data

    #---------------------------------------------------------------------------
    # check the cell has mass, and total mass is above flux floor
    def check_has_data(self):
        d_len = len(self.data)
        new_data = []
        self.has_data = False
        #check if has any flux
        if np.any(self.vals > 0):#self.flux_floor):
            #check if the total mass gets above the yearly flux floor.
            #  --current flux floor is figured in days so you multiply it
            #    by 365.25 to get the yearly flux floor.
            o_ts = TimeSeries(self.days,self.vals,None,None)
            o_mass = o_ts.integrate().values[-1]
            if o_mass > self.flux_floor * 365.25:
                self.has_data = True
    #-------------------------------------------------------------------------------
    #
    #def remove_begin_end_zero_flux(days,vals,flux_floor,min_reduction_steps):
    #    non_zero_ind = np.where(vals > 0)[0]
    #    pre_data = 0
    #    post_data = 0
    #    if (non_zero_ind[-1] - non_zero_ind[0]) > min_reduction_steps:
    #        non_zero_ind = np.where(vals > flux_floor)[0]
    #    if non_zero_ind.size == 0:
    #        return np.where(vals <= flux_floor)[0]
    #    if non_zero_ind[0] > 0:
    #        pre_data = non_zero_ind[0] - 1
    #    if non_zero_ind[-1] < len(days)-1:
    #        post_data = non_zero_ind[-1] + 1
    #    non_zero_ind = cp.concatenate((np.array([0,pre_data]),non_zero_ind,np.array([post_data,days.size -1])))
    #    return non_zero_ind
    #---------------------------------------------------------------------------
    # remove all points below flux_floor (data that is below the flux floor
    # causes issues in data reduction as its so small typicall)
    def remove_zero_flux(self):
        last_ind = self.vals.size-1
        #check if allowing any steps greater than 0 is still below min_reduction_steps
        non_zero_ind = np.where(self.vals > 0)[0]
        if non_zero_ind.size > self.min_reduction_steps:
            non_zero_ind = np.where(self.vals > self.flux_floor)[0]
        #add first zero after data decreases to zero
        if non_zero_ind.size == 0:
            return np.where(self.vals <= self.flux_floor)[0]
        if non_zero_ind[-1]+1 < last_ind and non_zero_ind[-1]+1 not in non_zero_ind:
            ind = non_zero_ind[-1]+1
            non_zero_ind = np.append(non_zero_ind,[ind])
            low_val = self.vals[ind]
            #zero_ind = ind
            #if low_val is not 0 then find then next zero
            if self.vals[ind] != 0:
                for i in range(ind,self.vals.size):
                    if self.vals[i] == 0:
                        ind = i
                        break
                    elif self.vals[i] < low_val:
                        low_val = self.vals[i]
                        ind = i
                if ind not in non_zero_ind:
                    non_zero_ind = np.append(non_zero_ind,[ind])
        #add last zero before flux increases above zero
        if non_zero_ind[0]-1 > 0 and non_zero_ind[0]-1 not in non_zero_ind:
            ind = non_zero_ind[0]-1
            non_zero_ind = np.append(non_zero_ind,[ind])
            low_val = self.vals[ind]
            #if low_val is not 0 then find the previous zero
            if low_val != 0:
                for i in range(ind, 0,-1):
                    if self.vals[i] == 0:
                        ind = i
                        break
                    elif self.vals[i] < low_val:
                        low_val = self.vals[i]
                        ind = i
            if ind not in non_zero_ind:
                non_zero_ind = np.append(non_zero_ind,[ind])
        if 0 not in non_zero_ind:
            non_zero_ind = np.append(non_zero_ind,[0])
        if (self.vals.size -1) not in non_zero_ind:
            non_zero_ind = np.append(non_zero_ind,[(self.vals.size -1)])
        non_zero_ind = np.sort(non_zero_ind)
        return non_zero_ind
#---------------------------------new object_-----------------------------------
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
        self.flux_floor = params["flux_floor"]/365.25
        self.max_tm_error =params["max_tm_error"]
        self.min_reduction_steps = min_steps
        self.units = params["units"]
        self.data_reduction = params["data_reduction"]
        self.graph_name = params["graph_name"]
        self.copc = params["copc"]
        if "HSSpath" in params.keys():
            self.HSSpath = params["HSSpath"]
        else:
            self.HSSpath = "./hss/"

    #---------------------------------------------------------------------------
    #break a dataframe of cells down into individual cell objects (this is used to
    # multiprocess)
    def build_data(self):
        data = []
        days = self.cells.loc[:,'days'].values
        #list = []

        for i in range(self.head.size):
            #get I and J indexes from head
            str_ind = self.head[i].find('-')
            k = 0
            k_df = pd.DataFrame()
            try:
                i_ind = int(self.head[i][0:str_ind])
                j_ind = int(self.head[i][str_ind+1:])
                try:

                    if self.saturation.loc[(i_ind,j_ind),'k'].size > 1:
                        k_df = self.saturation.loc[(i_ind,j_ind),['k']].sort_values(by=['time_step'])
                    else:
                        k = int(self.saturation.loc[(i_ind,j_ind),'k'])
                except Exception as e:
                    k = 0
                    self.logger.info("{} Error: could not find saturation layer".format(self.head[i]))
                    print("{} Error: could not find saturation layer".format(self.head[i]))
                    print(e)
                #print('{0}-{1}:{2} ({3})'.format(i_ind, j_ind,k,self.saturation.loc[(i_ind-1,j_ind-1),'k']))
                #list.append('{0}-{1}'.format(i_ind, j_ind))
            except:
                #self.logger.critical("Invalid header format {0}".format(self.head[i]))
                raise
            if k_df.size > 0:
                k_used = []
                for ind in range(k_df.size):
                    k = int(k_df.iloc[ind]['k'])
                    if not k in k_used:
                        k_used.append(k)
                        lay_days, lay_vals = self.build_time_val_series(k,k_df,self.head[i])
                        #start_day = k_df.index.values[ind]
                        #end_day = days[-1]+1


                        out_fileName = "{0}i{1}j{2}k{3}_hss.dat".format(self.path,i_ind,j_ind,k)
                        HSSFileName = "{0}i{1}j{2}k{3}_hss.dat".format(self.HSSpath,i_ind,j_ind,k)
                        rec = hss_file(out_fileName,HSSFileName,k,i_ind,j_ind,1,self.head[i],
                                        self.tolerance,self.start_year,self.log_path,
                                        self.min_reduction_steps,self.flux_floor,
                                        self.max_tm_error,self.units,self.graph_name,self.copc,self.data_reduction)


                        rec.build_array_fill_empty(days[0],days[-1],lay_days.tolist(), lay_vals.tolist())
                        data.append(rec)

            else:
                out_fileName = "{0}i{1}j{2}k{3}_hss.dat".format(self.path,i_ind,j_ind,k)
                HSSFileName = "{0}i{1}j{2}k{3}_hss.dat".format(self.HSSpath,i_ind,j_ind,k)
                values = self.cells.loc[:,self.head[i]].values
                rec = hss_file(out_fileName,HSSFileName,k,i_ind,j_ind,1,self.head[i],
                                self.tolerance,self.start_year,self.log_path,
                                self.min_reduction_steps,self.flux_floor,
                                self.max_tm_error,self.units,self.graph_name,self.copc,self.data_reduction)

                rec.build_array(days,values)
                data.append(rec)

        return data
    #---------------------------------------------------------------------------
    #
    def build_time_val_series(self, k, k_df,head):
        lay_days = self.cells['days'].values
        lay_vals = np.zeros(lay_days.size)

        for ind in range(k_df.size):
            k2 = int(k_df.iloc[ind]['k'])
            if k2 == k:
                start_day = k_df.index.values[ind]
                end_day = lay_days[-1]+1

                #size gives size ind is zero based. so to determine if there
                # is another record after the current ind add 2 and compare to
                # size
                if ind+2 <= k_df.size:
                    end_day = k_df.index.values[ind+1]

                temp_days = np.where((lay_days >= start_day)&(lay_days < end_day))
                lay_vals[temp_days] = self.cells.iloc[temp_days][head]
                self.logger.info("seperating layers {0}-k{1}: start day: {2}, end day: {3}".format(head,k,start_day,end_day-1))

        return lay_days, lay_vals
    #-------------------------------------------------------------------------------
    # method can be called without instantiating an object.
    # format a float as scientific string representation
    @staticmethod
    def format_e(n):
        if n == 0.0 or n == 0 or n == '--':
            a = 0.0
        else:
            try:
                a = '%.10E' % n
                #print(a)
                #print(a.split('E')[0].rstrip('0').rstrip('.'))
                #print(a.split('E')[1])
                a = a.split('E')[0].rstrip('0').rstrip('.') + 'E' + a.split('E')[1]
            except:
                print ("invalidfloat: {}".format(n))
                raise
        return a #a.split('E')[0].rstrip('0').rstrip('.') + 'E' + a.split('E')[1]

    #-------------------------------------------------------------------------------
    # process each cell object (reduce data), then create a HSSM package from the
    #  reduced cells and cell meta data
    def write_data(self):

        time_arr = []
        new_data = []
        max_lines = []
        data = self.build_data()
        procs = cpu_count()-1
        if procs > 3:
            procs = 3
        elif procs <1:
            procs = 1
        with context("spawn").Pool(processes=procs) as pool:
        #with context("spawn").Pool(processes=1) as pool:
            self.reduced_data = pool.map(build_pkg,data )

        file_str = ""
        num_files = 0
        max_steps = 0
        for x in self.reduced_data:
            if len(x) > 2:
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
        self.misc_files(self.reduced_data,'cell_error_by_layer.csv',True)
        self.consolidate_multi_layer_cells()
        self.misc_file_generation()
        self.misc_files(self.reduced_data_c,'cell_error.csv')

        #self.error_check() broken
    #---------------------------------------------------------------------------
    # Build a csv file showing the mass error by year per cell/layer when the total
    # mass error was > .1
    def error_check(self):
        start = 0

        cols = list(self.cells.columns)
        cols.remove('days')
        summed_cells = np.array([])
        check_cells = pd.DataFrame()
        for data in self.reduced_data_c:
            if len(data) > 2:
                o_ts = TimeSeries(self.cells['days'].values ,self.cells[data[4]].values ,None,None)
                r_ts = data[6]

                interp = np.array(tsmath.interpolated(r_ts,o_ts).values,dtype='float64')

                if summed_cells.size == 0:
                    summed_cells =  np.array(interp,dtype='float64')
                else:
                    summed_cells = np.sum([summed_cells,interp],axis=0)
                r_t_mass = data[6].integrate()
                t_mass = o_ts.integrate()
                d_mass_ts = tsmath.delta(t_mass,r_t_mass)
                p_mass_ts = TimeSeries(d_mass_ts.times,(d_mass_ts.values /t_mass.values)*100,None,None)
                d_flux_ts = tsmath.delta(o_ts,data[6])
                p_flux_ts = TimeSeries(d_flux_ts.times,(d_flux_ts.values /data[7].values)*100,None,None)

                error_mass_ind = np.where(p_mass_ts.values > .1)[0]
                error_flux_ind = np.where(p_flux_ts.values > .1)[0]
                if len(error_mass_ind) > 0:
                    t_data = pd.DataFrame(d_mass_ts.times[error_mass_ind],columns=["{} day".format(data[0])])
                    check_cells = pd.concat([check_cells,t_data],axis=1,sort=False)
                    t_data = pd.DataFrame(d_mass_ts.values[error_mass_ind],columns=["mass difference (pCi)"])
                    check_cells = pd.concat([check_cells,t_data],axis=1,sort=False)
                    t_data = pd.DataFrame(p_mass_ts.values[error_mass_ind],columns=[".1% or > mass difference".format(data[0])])
                    check_cells = pd.concat([check_cells,t_data],axis=1,sort=False)
                else:
                    t_data = pd.DataFrame(['--'],columns=["{} day".format(data[0])])
                    check_cells = pd.concat([check_cells,t_data],axis=1,sort=False)
                    t_data = pd.DataFrame(['--'],columns=["mass difference (pCi)"])
                    check_cells = pd.concat([check_cells,t_data],axis=1,sort=False)
                    t_data = pd.DataFrame(['--'],columns=[".1% or > mass difference".format(data[0])])
                    check_cells = pd.concat([check_cells,t_data],axis=1,sort=False)
                if len(error_flux_ind) > 0:
                    t_data = pd.DataFrame(d_flux_ts.times[error_flux_ind],columns=["{} day".format(data[0])])
                    check_cells = pd.concat([check_cells,t_data],axis=1,sort=False)
                    t_data = pd.DataFrame(d_flux_ts.values[error_flux_ind],columns=["flux difference (pCi/day)".format(data[0])])
                    check_cells = pd.concat([check_cells,t_data],axis=1,sort=False)
                    t_data = pd.DataFrame(p_flux_ts.values[error_flux_ind],columns=[".1% or > flux difference".format(data[0])])
                    check_cells = pd.concat([check_cells,t_data],axis=1,sort=False)
                else:
                    t_data = pd.DataFrame(['--'],columns=["{} day".format(data[0])])
                    check_cells = pd.concat([check_cells,t_data],axis=1,sort=False)
                    t_data = pd.DataFrame(['--'],columns=["flux difference (pCi/day)".format(data[0])])
                    check_cells = pd.concat([check_cells,t_data],axis=1,sort=False)
                    t_data = pd.DataFrame(['--'],columns=[".1% or > flux difference".format(data[0])])
                    check_cells = pd.concat([check_cells,t_data],axis=1,sort=False)
        #write file with mass error issues
        fileName = os.path.join(self.misc_path,'cell_mass_significant_error_by_year.csv')
        check_cells.to_csv(fileName, header=True)
        #finish processing total mass differences
        o_ts = TimeSeries(self.cells['days'].values,self.cells[cols].sum(axis=1).values,None,None)
        r_ts = TimeSeries(self.cells['days'].values, summed_cells, None,None)
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
            p_mass = (d_mass / o_mass_ts.values[i])*100
            output += "{},{},{},{},{},{},{} ({}%),{} ({}%)\n".format(year,day,
                        o_ts.values[i],r_ts.values[i],o_mass_ts.values[i],
                        r_mass_ts.values[i],d_flux,p_flux,d_mass,p_mass)
        fileName = os.path.join(self.misc_path,'net_error_by_year.csv')
        with open(fileName,"w") as outfile:
            outfile.write(output)
        plt.summary_plot(o_ts.times,o_ts.values,r_ts.times,r_ts.values,0,0, self.log_path,self.units,self.start_year,self.graph_name,self.copc,True)
    #---------------------------------------------------------------------------
    # generate csv file showing #pts, total_mass_err, percent mass err, # peaks found,
    #  mass lost when noise removed.  formated by cell and/or by cell/layer
    def misc_files(self,data,fileName,layers = False):
        cols = ['cell','#pts','o_total_mass({})'.format(self.units),'r_total_mass({})'.format(self.units),'total_mass_error({})'.format(self.units),'%error','peaks_found', 'mass lost due to noise','Notes']
        cells = pd.DataFrame(columns=cols)
        cells = cells.set_index('cell')
        days = self.cells.loc[:,'days'].values
        cells_interp = pd.DataFrame(days,columns=['days'])
        cells_interp = cells_interp.set_index('days')
        for x in data:
            if len(x) > 2:

                values = self.cells.loc[:,x[4]].values
                ts = TimeSeries(days,values,None,None)
                #total_mass = ts.integrate().values[-1]
                r_ts = x[6]

                #r_tmass = r_ts.integrate().values[-1]
                result = ReductionResult(
                                flux=ts,
                                mass=ts.integrate(),
                                reduced_flux=r_ts,
                                reduced_mass=r_ts.integrate())


                total_mass = result.mass.values[-1]
                r_tmass = result.reduced_mass.values[-1]
                t_mass_diff = result.total_mass_error
                p_error = ((t_mass_diff)/total_mass)*100
                v_minus_ff = (values[values < self.flux_floor].sum())*365.25
                t_dict = {'days':ts.times,'{}_orig'.format(x[4]):ts.values,'cumulative':result.mass.values}
                t_data = pd.DataFrame(t_dict)
                t_data = t_data.set_index('days')
                cells_interp = pd.concat([cells_interp,t_data],axis=1,sort=False)
                i_ts = tsmath.interpolated(r_ts,ts)
                t_dict = None
                t_dict = {'days':i_ts.times,'{}_interp'.format(x[0][x[0].index('/i')+1:]):i_ts.values,'cumulative':i_ts.integrate().values}
                t_data = pd.DataFrame(t_dict)
                t_dict = None
                t_data = t_data.set_index('days')
                cells_interp = pd.concat([cells_interp,t_data],axis=1,sort=False)

                #if data has mulitple layers per cell create a summed record for
                # each cell
                if layers:
                    all_layers = "{}summed_layers".format(x[0][x[0].index('/i')+1:x[0].index('k')])
                    temp = pd.DataFrame(np.array([[x[0][x[0].index('/i')+1:],len(x[1]),'--',r_tmass,'--','--',x[5],v_minus_ff,'']]),columns=cols)
                    temp = temp.set_index('cell')
                    cells = cells.append(temp)
                    #if record exists update it otherwise insert it.
                    if all_layers in cells.index:
                        #print(cells.loc[all_layers,['r_total_mass({})'.format(self.units)]])
                        cells.at[all_layers,'r_total_mass({})'.format(self.units)] = r_tmass + float(cells.loc[all_layers,'r_total_mass({})'.format(self.units)])
                        cells.at[all_layers,'mass lost due to noise'] = v_minus_ff + float(cells.loc[all_layers,'mass lost due to noise'])
                        diff = total_mass - float(cells.loc[all_layers,'r_total_mass({})'.format(self.units)])
                        cells.at[all_layers,'total_mass_error({})'.format(self.units)] = diff
                        cells.at[all_layers,'%error'] = (diff / total_mass)*100
                    else:
                        temp = pd.DataFrame(np.array([[all_layers,'--',total_mass,r_tmass,t_mass_diff,p_error,'--',v_minus_ff,'All layers for this cell summed together']]),columns=cols)
                        temp = temp.set_index('cell')
                        cells = cells.append(temp)
                else:
                    fn = x[0][x[0].index('/i')+1:]
                    temp = pd.DataFrame(np.array([[fn,len(x[1]),total_mass,r_tmass,t_mass_diff,p_error,x[5],v_minus_ff,'']]),columns=cols)
                    temp = temp.set_index('cell')
                    cells = cells.append(temp)
            elif len(x) > 0:
                values = x[1].values#self.cells.loc[:,x[0]].values
                ts = TimeSeries(days,values,None,None)
                total_mass = ts.integrate().values[-1]
                temp = pd.DataFrame(np.array([['{} Skipped'.format(x[0]),'--',total_mass,'--','--','--','--',total_mass,'This cell was skipped as the flux never rises above minimum flux({})'.format(self.flux_floor)]]),columns=cols)
                temp = temp.set_index('cell')
                cells = cells.append(temp)

        cells.sort_index(axis=0,inplace=True)
        #show what the mass difference is if you remove everything below the flux floor
        #t_vals = self.cells.loc[:,self.cells.columns != 'days'].astype('float64')
        #values = t_vals.sum(axis=1).values
        #ts = TimeSeries(days,values,None,None)
        #total_mass = ts.integrate().values[-1]
        #t_vals[t_vals < self.flux_floor] =  0
        #values = t_vals.sum(axis=1).values
        #nz_ts = TimeSeries(days,values,None,None)
        #nz_total_mass = nz_ts.integrate().values[-1]
        #t_mass_diff = total_mass-nz_total_mass
        #p_error = ((t_mass_diff)/nz_total_mass)*100
        #temp = pd.DataFrame(np.array([['Approximate mass removed as Noise (flux < {} {}/day)'.format(self.flux_floor,self.units),'--',total_mass,nz_total_mass,t_mass_diff,p_error,'--',t_mass_diff,'This is the removal of any fluxes considered to be noise (flux < {} {}/day) calculated before any data reduction'.format(self.flux_floor,self.units)]]),columns=cols)
        #temp = temp.set_index('cell')
        #cells = cells.append(temp)

        pathfile = os.path.join(self.misc_path,fileName)#'cell_error_by_layer.csv')
        cells.to_csv(pathfile, header=True)
        pathfile = os.path.join(self.misc_path,'interpolated_results_{}'.format(fileName.replace('_error','')))#'cell_error_by_layer.csv')
        cells_interp.to_csv(pathfile, header=True)
    #---------------------------------------------------------------------------
    #takes the reduced data which is seperated by cells and layers and consolidates
    # all of the layers for each cell so there is a single entry per cell
    def consolidate_multi_layer_cells(self):
        def sort_first_field(val):
            return val[0]
        reduced_c = []
        completed_cells = []
        #self.reduced_data.sort(key = sort_first_field, reverse = true)
        for x in self.reduced_data:
            if len(x)>2:
                cur_rec = x
                ij = cur_rec[4]

                if not ij in completed_cells and len(cur_rec[1]) > 0:
                    #segs = []
                    #segs.append(cur_rec[1])
                    #if len(cur_rec[1]) == 1:
                    #    segs = array(cur_rec[1])
                    #else :
                    segs = []#cur_rec[1]

                    completed_cells.append(ij)
                    layers = []

                    o_ts = TimeSeries(self.cells['days'].values,self.cells[ij].values,None,None)
                    #loop through to find all layers for ij
                    cell = pd.DataFrame([[o_ts.times]],columns=['days'])
                    cell = cell.set_index('days')
                    pre_data = o_ts.times[1]
                    post_data = o_ts.times[-2]
                    for y in self.reduced_data:
                        if len(y) > 2:
                            #check if the same cell
                            if y[4] == ij:
                                #days = np.array(y[1]).astype(float)[:,0]
                                #vals = np.array(y[1]).astype(float)[:,1]
                                #cum = np.array(yrec).astype(float)[:,2]
                                #non_zero_ind = np.where(vals > 0)[0]
                                #print(cell)

                                #find the last day where flux is 0 before mass starts
                                #if pre_data > days[non_zero_ind[0]-1] > o_ts.times[0]:
                                #    pre_data = days[non_zero_ind[0] - 1]
                                #find the first day where flux is 0 after mass ends
                                #if post_data < days[non_zero_ind[-1]+1] < o_ts.times[-1]:
                                #    post_data = days[non_zero_ind[-1] + 1]
                                #non_zero_ind = np.concatenate((np.where(np.logical_and(days >=pre_data+1, days<=post_data-1))[0]))
                                #temp = pd.DataFrame([days[non_zero_ind],vals[non_zero_ind],cum[non_zero_ind]],columns=['days','vals','cum'])
                                #days_tmp = np.array(days[non_zero_ind])
                                #vals_tmp = np.array(vals[non_zero_ind])
                                #temp = pd.DataFrame([[days_tmp,vals_tmp]],columns=['days','vals'])
                                #temp = temp.set_index('days')

                                #cell = pd.concat([cell,temp],axis=1,sort=False)

                                #original
                                for yrec in y[1]:

                                    found = False

                                    for xrec in segs:
                                        #if years are equal update flux and total mass
                                        if xrec[0] == yrec[0]:
                                            xrec[1] += yrec[1]
                                            xrec[2] += yrec[2]
                                            found = True
                                            break

                                    if not found:
                                        #if yrec and original value is less than flux_floor
                                        # Then keep the record.  if yrec is less and original
                                        # is greater then yrec is likely where the mass ends
                                        # for that layer. which means the next layer will have
                                        # the correct value for this day
                                        if yrec[1] == 0:
                                            ind = np.where(o_ts.times == yrec[0])[0]
                                            if o_ts.values[ind] < self.flux_floor:
                                                segs.append(yrec)
                                        else:
                                            segs.append(yrec)
                                    #end of original

                                    #if r_ts.times.size ==0:
                                    #    r_ts = y[6]
                                    #else:
                                    #    r_ts.values = np.add(r_ts.values,y[6].values)

                    segs.sort(key = sort_first_field)
                    ###u, c =
                    days = [float(i[0]) for i in segs]
                    days = np.array(segs).astype(float)[:,0]
                    vals = [float(i[1]) for i in segs]
                    vals = np.array(segs).astype(float)[:,1]
                    if 0 not in days:
                        days = np.insert(days,0, 0)
                        vals = np.insert(vals,0, 0)
                    #pre_ind = np.where(o_ts.times == pre_data)
                    #post_ind = np.where(o_ts.times == post_data)
                    #days_tmp = np.array([o_ts.times[0],o_ts.times[pre_ind],o_ts.times[post_ind],o_ts.times[-1]])
                    #vals_tmp = np.array([0,0,0,0])
                    #temp = pd.DataFrame([[days_tmp,vals_tmp]],columns=['days','vals'])
                    #temp = temp.set_index('days')
                    #cell = cell.combine_first(temp).reset_index().fillna(0)
                    #print(cell)
                    #cell = pd.concat([cell,temp],axis=1,sort=False)
                    #cell = cell.groupby(lambda x:x, axis=1).sum()
                    #print(cell)
                    #days = cell.index.values
                    #vals = cell[:,0].values
                    try:
                        r_ts = TimeSeries(np.array(days),np.array(vals),None,None)
                        r_ts = tsmath.interpolated(r_ts,o_ts)
                    except:
                        print(r_ts.times)
                        print('{} failed.  start: {}; end: {};'.format(ij,r_ts.times[0],r_ts.times[-1]))
                        print('{} failed.  start: {}; end: {};'.format(ij,o_ts.times[0],o_ts.times[-1]))
                        raise
                    cur_rec[1] = segs
                    cur_rec[6] = r_ts
                    cur_rec[7] = o_ts
                    reduced_c.append(cur_rec)
                    i = ij[:ij.rfind('-')]
                    j = "{}_all_layers".format(ij[ij.rfind('-')+1:])
                    time = []
                    value = []
                    for ind in range(len(segs)):
                        time.append(float(segs[ind][0]))
                        value.append(float(segs[ind][1]))
                    time = np.array(time)
                    value = np.array(value)
                    plt.summary_plot(self.cells['days'].values,self.cells[ij].values,time,value,i,j, self.log_path,self.units,self.start_year,self.graph_name,self.copc,False)

        self.reduced_data_c = reduced_c



    #---------------------------------------------------------------------------
    # create csv files for the full reduced data set (in reduced form), the cumulative mass summed
    #  (each cell) by year (original and reduced (after integrated back to yearly)),
    # summed flux (all cells after integrated back to yearly) by year.
    def misc_file_generation(self):
        #--Build consolidated output file
        yearly_output = ""
        output = ""
        cols = ""
        error_str = ""
        e_cols = ""
        first = True
        total_cum = 0
        #index should be in years
        keys = self.cells.index.values
        keys.sort()

        for i in range(len(keys)):
            total_flux = self.cells.loc[keys[i], self.cells.columns != 'days'].sum()
            #days column is the number of days since start_year
            days = self.cells.loc[keys[i],'days']
            # if prev rec is set then calculate cumulative mass
            if i > 0:
                total_cum += (total_flux * 365.25) #*  (keys[i] - keys[i-1])
            # else this is the first rec so no calculation needed.
            else:
                total_cum = total_flux * 365.25
            #convert to ci (1E-12) from pCi, for second cumulative column
            factor = 1
            unit = self.units
            if self.units.lower() == 'ug':
                unit = 'kg'
                factor = 1e-9
            elif self.units.lower() == 'pci':
                unit = "Ci"
                factor = 1e-12
            total_cum_ci = total_cum * factor
            output += "{0},{1},{2},{3}".format(days,total_flux,total_cum,total_cum_ci)
            #yearly_output += "{0},{1},{2}\n".format(keys[i] /365.25 + self.start_year,(total_flux * 365.25)*factor,total_cum_ci)
            yearly_output += "{0},{1},{2}\n".format(keys[i],(total_flux * 365.25)*factor,total_cum_ci)

            for x in self.reduced_data_c:
                if (len(x) > 0):

                    if (len(x[1]) > i):
                        cur_rec = x[1][i]
                        #logger.debug(cur_rec)
                        #temp = x[0][x[0].rfind('/i')+2:x[0].rfind('_h')]
                        #ij = "{0}-{1} (K:{2})".format(temp[:temp.rfind('j')],temp[temp.rfind('j')+1:temp.rfind('k')],temp[temp.rfind('k')+1:])
                        ij = x[4]
                        if first:
                            cols += ",{0} (day),rate ({1}/day),cumulative ({1})".format(ij,self.units)#x[0])
                            e_cols += "{0},original rate ({1}/year), reduced rate ({1}/year), percent error,".format(ij,self.units)
                        #if len(output) < 1:
                        #    output += "{0},{1},{2}".format(cur_rec[0],cur_rec[1],cur_rec[2])
                        #else:
                        output += ",{0},{1},{2}".format(cur_rec[0],cur_rec[1],cur_rec[2])
                        #check error on flux
                        year = (cur_rec[0]/Decimal('365.25'))+self.start_year

                        flux = Decimal(self.cells.loc[int(year),ij]*365.25)
                        r_flux = cur_rec[1] * Decimal('365.25')
                        error = (flux-r_flux)
                        if abs(error) > 0:
                            error = (error/flux)*100
                        if error > .001:
                            error_str += "{0},{1},{2},{3},".format(year,flux,r_flux,error)
                        else:
                            error_str  += "{},--,--,--,".format(year)
                    else:
                        output += ",,,"
                        error_str  += ",,,,"

            if len(cols) > 3:
                output += "\n"
                error_str += "\n"
                first = False
        output = "days,total flux({2}/day), total cumulative({2}),total cumulative({3}){0}\n{1}".format(cols,output,self.units,unit)
        error_str = "{0}\n{1}".format(e_cols,error_str)
        yearly_output = "years,total flux({1}/year), total cumulative({1})\n{0}".format(yearly_output,unit)
        fileName = os.path.join(self.misc_path,'full_data_set.csv')
        with open(fileName,"w") as outfile:
            outfile.write(output)
        fileName = os.path.join(self.misc_path,'cumulative_data_set_by_year.csv')
        with open(fileName,"w") as outfile:
            outfile.write(yearly_output)
        fileName = os.path.join(self.misc_path,'rate_error_check.csv')
        with open(fileName,"w") as outfile:
            outfile.write(error_str)
