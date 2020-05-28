'''
Author:         Neil Powers
Date:           Apr 2019
Company:        Intera Inc.
Usage:          open MT3D head file, layer ref files, and build a single file
                with saturations for each time period/layer/cell
'''
import numpy as np
import argparse
import datetime as dt
from decimal import *
import flopy.utils.binaryfile as bf
import pandas as pd
import os.path
from pathlib import Path
import math
import logging
class sat_obj:
    #---------------------------------------------------------------------------
    # pkl = (bool) use existing pickled file
    # pkl_f = name of the pickled file to use or create
    #   bf = binary hds file
    # if pkl is false then below is mandatory:
    #   tr = Top reference file for first layer
    #   br = array of bottom depth layer ref files
    #   i = number of rows in grid
    #   j = number of columns in grid
    #   k = number of lyaers in grid
    #   msl = minimum Saturation for a layers

    def __init__(self, pkl, pkl_d, sat_f, flow_f, bin_f, top_r, bot_r,i_cond, i, j, k, msl,log):
        start_time = dt.datetime.now()
        cur_time = dt.datetime.now()
        self.logger = logging.getLogger(log)
        self.hds_file = bin_f
        self.pkl_dir = pkl_d
        self.init_cond = i_cond
        self.sat_f = sat_f
        self.flow_f = flow_f
        self.top_ref = top_r
        self.bot_ref = bot_r
        self.cols_i = int(i) #vertical
        self.cols_j = int(j) #horizontal
        self.cols_k = int(k) # down
        self.min_sat_lvl = msl
        self.sat_cols =  ['i','j','k','time_step','last_time_step','hds','top_depth','bot_depth','saturation']
        self.types = {'i' : int,'j': int,'k': int,'time_step': float,'hds':float,'top_depth':float,'bot_depth':float,'saturation':float}
        self.flow_cols = ['i','j','time_step','faces']
        self.f_types = {'i' : int,'j': int,'time_step': float}
        self.index = ['i','j']
        self.index_year = ['i','j','time_step']
        self.check_output_dir(self.pkl_dir)
        cur_time = dt.datetime.now()
        self.logger.info("reading HDS file: {0} start_time: {1}".format(self.hds_file,cur_time))
        self.binary_obj = self.read_hds_file()
        self.logger.info("Finished reading HDS file: end_time: {0}; elapsed:{1}".format(cur_time, dt.datetime.now()-cur_time))
        cur_time = dt.datetime.now()
        self.logger.info("Finding time steps, start_time: {0}".format(cur_time))
        self.sp_times = self.get_sp_times()
        self.logger.info("Finished finding time steps: end_time: {0}; elapsed:{1}".format(cur_time, dt.datetime.now()-cur_time))
        cur_time = dt.datetime.now()
        self.logger.info("Reading layer depths: {0},{1} start_time: {2}".format(self.top_ref,self.bot_ref,cur_time))
        self.layer_depths = self.get_layers()
        self.logger.info("Finished reading layer depths: end_time: {0}; elapsed:{1}".format(cur_time, dt.datetime.now()-cur_time))
        if pkl:
            cur_time = dt.datetime.now()

            if self.check_file_exists(self.pkl_dir,self.sat_f):
                self.logger.info("Read in saturation pkl file: {0} start_time: {1}".format(self.sat_f,cur_time))
                self.sat_obj = self.read_pickle(self.sat_f)
            else:
                self.logger.info("building Saturation pkl file: start_time: {0}".format(cur_time))
                self.sat_obj = self.build_end_year_saturation()
                self.pickle_data(self.sat_f,self.sat_obj)
                self.create_meta_data(self.sat_f)
            self.logger.info("Finished loading saturation data: end_time: {0}; elapsed:{1}".format(cur_time, dt.datetime.now()-cur_time))
            cur_time = dt.datetime.now()
            if self.check_file_exists(self.pkl_dir,self.flow_f):
                self.logger.info("Reading Flow pkl file: {0} start_time: {1}".format(self.flow_f,cur_time))
                self.flow_obj = self.read_pickle(self.flow_f)
            else:
                self.logger.info("building Flow pkl File: {0} start_time: {1}".format(self.flow_f,cur_time))
                self.flow_obj = self.build_flow()
                self.pickle_data(self.flow_f,self.flow_obj)
            self.logger.info("Finished loading flow data: end_time: {0}; elapsed:{1}".format(cur_time, dt.datetime.now()-cur_time))
        else:

            cur_time = dt.datetime.now()
            self.logger.info("Build saturation data, start_time: {0}".format(cur_time))
            self.sat_obj = self.build_end_year_saturation()
            self.logger.info("Finished build saturation data: end_time: {0}; elapsed:{1}".format(cur_time, dt.datetime.now()-cur_time))
            cur_time = dt.datetime.now()
            self.logger.info("Pickling data: start_time: {0}".format(cur_time))
            self.pickle_data(self.sat_f,self.sat_obj)
            self.create_meta_data(self.sat_f)
            self.logger.info("Finished pickling: end_time: {0}; elapsed:{1}".format(cur_time, dt.datetime.now()-cur_time))
            #---
            # to do build flow
            self.logger.info("Build flow data: start_time:{0}".format(cur_time))
            self.flow_obj = self.build_flow()
            self.logger.info("Finished build flow data: end_time: {0}; elapsed:{1}".format(cur_time, dt.datetime.now()-cur_time))
            #cur_time = dt.datetime.now()
            #logger.info("Pickle data: start_time:".format(cur_time))
            self.pickle_data(self.flow_f,self.flow_obj)
            self.logger.info("Finished pickling: end_time: {0}; elapsed:{1}".format(cur_time, dt.datetime.now()-cur_time))
    #---------------------------------------------------------------------------
    #
    def check_output_dir(self,dir):
        if not os.path.isdir(dir):
            try:
                os.mkdir(dir)
            except OSError:
                self.logger.info ("Creation of the directory '%s' failed" % dir)
                raise
            else:
                self.logger.info("Successfully created the directory %s " % dir)

    #---------------------------------------------------------------------------
    # Layer files are 10 columns accross so if there is more than 10 j columns for
    #each i then it will wrap to the next line.
    #To find all the rows belonging to a single i:
    #   divide the total j columns by 10, and add 1 if there is a remainder to
    #   find how many rows there are for each i

    def parse_ref_line(self,file):
        def get_j_ref_rows():
            return int(math.ceil(self.cols_j/10))
        ref_array = []
        i = 0
        row = 0
        l_per_rec = get_j_ref_rows()
        t_line = ""

        for line in file:
            t_line = t_line + line.strip() + " "
            i = i+1
            #when line / l_per_rec has a remainder of 0 then you have reached
            #the end of a row in the grid. add it to the array as a single rows
            # the row represents i, the columns being added represent j
            if i % l_per_rec == 0:
                t_line = t_line.replace("-9.9900000e+002"," -9.9900000e+002").replace("  "," ").strip()
                ref_array.append(t_line.split(" "))
                t_line = ""
                row = row + 1
        return ref_array
    #---------------------------------------------------------------------------
    # open top ref file and get depth for each cell
    def get_surface(self, file_name):
        top = []
        #with open(Path(file_name), "r") as file:
        with open(file_name, "r") as file:
            # Layer files are 10 columns accross so if there is more than 10 j columns for
            #each i then it will wrap to the next line.
            top = self.parse_ref_line(file)
        return top
    #---------------------------------------------------------------------------
    # as there are multiple bottom layers you will need to lop through each files
    # and add file to the array in order from layer 1 to layer x.
    def get_layers(self):
        #make sure layer_files are in ascending order
        self.bot_ref.sort()
        # Layer files are 10 columns accross so if there is more than 10 j columns for
        #each i then it will wrap to the next line.

        bot = []
        bot.append(self.get_surface(self.top_ref))
        for file in self.bot_ref:
            #bot.append([])
            with open(file, "r") as file:
                bot.append(self.parse_ref_line(file))
        return bot
    #---------------------------------------------------------------------------
    # get time steps
    def get_sp_times(self):
        sp_times = self.binary_obj.get_times()
        return sp_times
    #---------------------------------------------------------------------------
    # find time steps that are less than 1 day difference
    #def find_bad_SPs(self):
    #    sp_diffs = [val2 - val1 for val1, val2 in zip(self.sp_times, self.sp_times[1:])]
    #    sp_diffs = [self.sp_times[0], *sp_diffs]
    #    bad_indices = [index for index in range(len(sp_diffs)) if sp_diffs[index] < 1]
    #    return bad_indices
    #---------------------------------------------------------------------------
    #saturation calculation:
    #(simulated head – bottom elevation) / (top elevation – bottom elevation)
    def calc_sat(self,h,t,b):
        x = (h-b)
        y = (t-b)
        #check for divide by zero issues
        if y > 0:
            lvl = (h-(b))/(t-(b))
            return lvl
        else:
            return 0
    #---------------------------------------------------------------------------
    #check cell to see if it has any active layers.
    #inactive layers have a depth of zero
    def check_cell_has_depth(self,i,j):
        for k in range(self.cols_k):
            k_ind = k+1
            t_depth = float(self.layer_depths[k][i][j])
            b_depth = float(self.layer_depths[k_ind][i][j])
            if b_depth > 0 and ( t_depth - b_depth ) > 0 :
                return True
                break
        self.logger.info("i-j({0}-{1}): Cell is inactive".format(i+1,j+1))
        return False
    #---------------------------------------------------------------------------
    # as there are multiple bottom layers you will need to lop through each files
    # and add file to the array in order from layer 1 to layer x.
    def build_initial_conditions(self):
        #make sure layer_files are in ascending order
        self.init_cond.sort()
        # Layer files are 10 columns accross so if there is more than 10 j columns for
        #each i then it will wrap to the next line.

        hds = []
        for file in self.init_cond:
            #bot.append([])
            with open(file, "r") as file:
                hds.append(self.parse_ref_line(file))

        return hds
    #---------------------------------------------------------------------------
    # build a saturation object that has the time period for each layer that is
    # above minumum saturation layer
    def build_saturation_by_year(self,pkl, yearly_sat_file):
        cur_time = dt.datetime.now()
        self.logger.info("Build saturation data, start_time: {0}".format(cur_time))
        data_loaded = False
        cell_sat = pd.DataFrame(columns=self.sat_cols)
        cell_sat = cell_sat.astype(self.types)
        cell_sat = cell_sat.set_index(self.index_year)
        calc = "({0} - {1})/({2}-{1})={3}"
        init_cond = self.build_initial_conditions()
        #load from pkl file if directed
        if pkl:
            if self.check_file_exists(self.pkl_dir,yearly_sat_file):
                cur_time = dt.datetime.now()
                self.logger.info("Reading yearly saturation pkl file: {0} start_time: {1}".format(yearly_sat_file,cur_time))
                cell_sat = self.read_pickle(yearly_sat_file)
                self.logger.info("finished Reading yearly saturation pkl file: {0}".format(cur_time))
                data_loaded = True
        #check to see if data was loaded (pkl file not found then rebuild file)
        if data_loaded == False:
            start_time = dt.datetime.now()
            for i in range (self.cols_i):
                i_ind = i+1
                #if i == 35:
                #    cell_sat.to_csv(os.path.join(r'output_tc-99/misc',r'yearly_saturation_under35.csv'), header=True)
                #self.logger.debug("{0}: finished row i-{1}".format(dt.datetime.now(),i_ind))
                for j in range (self.cols_j):
                    j_ind = j+1
                    # starting from the last time step
                    last_t_step = False
                    cell_has_depth = False

                    #Check if cell actally has layers or if its an inactive cell
                    if self.check_cell_has_depth(i,j):
                        current_layer = -1
                        #find initial saturation of cells from initial conditions
                        for k in range(self.cols_k):
                            k_ind = k+1

                            hds = float(init_cond[k][i][j])
                            t_depth = float(self.layer_depths[k][i][j])
                            b_depth = float(self.layer_depths[k_ind][i][j])

                            lvl = self.calc_sat(hds,t_depth,b_depth)
                            calc_txt = calc.format(hds,b_depth,t_depth,lvl)

                            if lvl > self.min_sat_lvl:
                                current_layer = k_ind
                                temp = pd.DataFrame([[i_ind,j_ind,current_layer,0,last_t_step,hds,t_depth,b_depth,lvl]],columns=self.sat_cols)
                                temp = temp.set_index(self.index_year)
                                cell_sat = cell_sat.append(temp,sort=False)
                                self.logger.info("K,i-j,day({0},{1}-{2},{3}): (Initial layer){4} ".format(k_ind,i_ind,j_ind,0,calc_txt))
                                break
                        t_step_prev = self.sp_times[0]
                        prev_calc = ""
                        max_step = len(self.sp_times)
                        for x in range(max_step):
                            t_step = self.sp_times[x]
                            if x == max_step-1:
                                last_t_step = True
                            head = self.binary_obj.get_data(totim=t_step)
                            #Find the first layer with a saturation > min_sat_lvl
                            for k in range(self.cols_k):
                                k_ind = k+1
                                # Calculate cell Saturation
                                # k=bottom of previous layer
                                # k_ind = bottom of current layer

                                hds = float(head[k][i][j])
                                t_depth = float(self.layer_depths[k][i][j])
                                b_depth = float(self.layer_depths[k_ind][i][j])

                                lvl = self.calc_sat(hds,t_depth,b_depth)
                                calc_txt = calc.format(hds,b_depth,t_depth,lvl)
                                if lvl > self.min_sat_lvl:
                                    if current_layer == -1:
                                        #set initial layer
                                        current_layer = k_ind
                                        self.logger.info("K,i-j,day({0},{1}-{2},{3}): (Initial layer){4} ".format(k_ind,i_ind,j_ind,t_step,calc_txt))
                                        temp = pd.DataFrame([[i_ind,j_ind,current_layer,t_step,last_t_step,hds,t_depth,b_depth,lvl]],columns=self.sat_cols)
                                        temp = temp.set_index(self.index_year)
                                        cell_sat = cell_sat.append(temp,sort=False)
                                        #last_calc = last_calc.set_index(self.index_year)
                                        #cell_sat = cell_sat.append(last_calc,sort=False)

                                        #self.logger.info("K,i-j,day({0},{1}-{2},{3}): {4} ".format(k+1,i+1,j+1,t_step,calc_txt))
                                    elif current_layer != k_ind:# or last_t_step:
                                        #if saturation layer changes add the
                                        #previous year as the last year for the
                                        #old layer and thenset current_layer
                                        current_layer = k_ind
                                        temp = pd.DataFrame([[i_ind,j_ind,current_layer,t_step,last_t_step,hds,t_depth,b_depth,lvl]],columns=self.sat_cols)
                                        temp = temp.set_index(self.index_year)
                                        cell_sat = cell_sat.append(temp,sort=False)
                                        #if last_t_step:
                                        #    last_calc = pd.DataFrame([[i_ind,j_ind,current_layer,t_step,last_t_step,hds,t_depth,b_depth,lvl]],columns=self.sat_cols)
                                        #    self.logger.info("K,i-j,day({0},{1}-{2},{3}): {4} ".format(k+1,i+1,j+1,t_step,calc_txt))
                                        #else:
                                        self.logger.info("K,i-j,day({0},{1}-{2},{3}): {4} ".format(k_ind,i_ind,j_ind,t_step,calc_txt))

                                        #last_calc = last_calc.set_index(self.index_year)
                                        #cell_sat = cell_sat.append(last_calc,sort=False)


                                    #last_calc = pd.DataFrame([[i_ind,j_ind,current_layer,t_step_prev,last_t_step,hds,t_depth,b_depth,lvl]],columns=self.sat_cols)
                                    break

                            #t_step_prev = t_step
                            #prev_calc = calc_txt
            #tabbed line in once so saves the file if its being generated
            #and not when being loaded.
            self.pickle_data(yearly_sat_file,cell_sat)
        self.year_sat = cell_sat
        self.logger.info("Finished build saturation data: end_time: {0}; elapsed:{1}".format(cur_time, dt.datetime.now()-cur_time))
    #---------------------------------------------------------------------------
    #
    def build_end_year_saturation(self):
        #self.sp_times
        #self.bad_sp_list

        cell_sat = pd.DataFrame(columns=self.sat_cols)
        cell_sat = cell_sat.astype(self.types)
        cell_sat = cell_sat.set_index(self.index)

        t_depth = float(0.0)
        b_depth = float(0.0)
        hds     = float(0.0)
        lvl     = float(0.0)
        i_ind = int(0)
        j_ind = int(0)
        k_ind = int(0)
        t_step = 0
        calc = "({0} - {1})/({2}-{1})={3}"
        #loop through i and j
        start_time = dt.datetime.now()
        for i in range (self.cols_i):
            i_ind = i+1

            self.logger.info("{0}: finished row i-{1}".format(dt.datetime.now(),i_ind))
            for j in range (self.cols_j):
                j_ind = j+1
                # starting from the last time step
                last_t_step = True
                #cell_has_depth = False
                #Check if cell actally has layers or if its an inactive cell
                #for k in range(self.cols_k):
                #    k_ind = k+1
                #    t_depth = float(self.layer_depths[k][i][j])
                #    b_depth = float(self.layer_depths[k_ind][i][j])
                #    if b_depth > 0 and ( t_depth - b_depth ) > 0 :
                #        cell_has_depth = True
                #        break
                if self.check_cell_has_depth(i,j):
                    for x in reversed(range(len(self.sp_times))):
                        t_step = self.sp_times[x-1]
                        head = self.binary_obj.get_data(totim=t_step)
                        #Find the first layer with a saturation > min_sat_lvl
                        for k in range(self.cols_k):
                            k_ind = k+1
                            # Calculate cell Saturation
                            hds = float(head[k][i][j])
                            t_depth = float(self.layer_depths[k][i][j])
                            b_depth = float(self.layer_depths[k_ind][i][j])

                            lvl = self.calc_sat(hds,t_depth,b_depth)
                            calc_txt = calc.format(hds,b_depth,t_depth,lvl)
                            if lvl > self.min_sat_lvl:
                                self.logger.info("K,i-j({0},{1}-{2}): {3} ".format(k+1,i+1,j+1,calc_txt))
                                #logger.info(("K,i-j({0},{1}-{2}): {3} ".format(k+1,i+1,j+1,calc_txt)))
                                if lvl > 1:
                                    lvl = 1
                                k_ind = k+1
                                break
                        if lvl > self.min_sat_lvl:
                            break
                        else:
                            last_t_step = False
                    if lvl > self.min_sat_lvl:
                        temp = pd.DataFrame([[i_ind,j_ind,k_ind,t_step,last_t_step,hds,t_depth,b_depth,lvl]],columns=self.sat_cols)
                        temp = temp.set_index(self.index)
                        cell_sat = cell_sat.append(temp,sort=False)
                        #logger.info (cell_sat.loc[i_ind,j_ind])

            self.logger.info("{0}: finished row elapsed time: {1}".format(dt.datetime.now(),dt.datetime.now()-start_time))
            start_time = dt.datetime.now()
            cur_time = dt.datetime.now()
            self.logger.info("Pickling data: start_time: {0}".format(cur_time))
            self.pickle_data(self.sat_f,cell_sat)
            self.create_meta_data(self.sat_f)
            self.logger.info("Finished pickling: end_time: {0}; elapsed:{1}".format(cur_time, dt.datetime.now()-cur_time))
        return cell_sat
    #---------------------------------------------------------------------------
    # If I,J exists and time step is greater than original time step and hds is
    # lower than original hds then return cell data
    def get_recieving_cell(self, i,j,hds,step):
        try:
            temp = self.sat_obj.loc[i,j]
            if temp['time_step'] > step and hds > temp['hds']:
                self.logger.info ("    {0}-{1}: hds = {2}; last_time_step = {3}".format(i,j,temp['hds'],int(temp['time_step']/365.25)+2018))
                return [i,j,temp['hds'],temp['time_step']]
        except:
            pass
    #---------------------------------------------------------------------------
    # If I,J exists and time step is greater than original time step and hds is
    # lower than original hds then return cell data
    def get_cell(self, i,j):
        try:
            temp = self.sat_obj.loc[i,j]
            return [i,j,temp['hds'],temp['time_step']]
        except:
            pass
        #return []
    #---------------------------------------------------------------------------
    # if cell is a sink then find the lowest surroinding cell and add it as a
    # direction flow --equivalent of filling sink to be equal to lowest neighbor
    def fix_sink(self, i,j,faces):
        temp = []
        min_hds = 10000
        temp.append(self.get_cell(i+1,j))
        temp.append(self.get_cell(i-1,j))
        temp.append(self.get_cell(i,j+1))
        temp.append(self.get_cell(i,j-1))
        for t in temp:
            self.logger.info("  -{0}".format(t))
            if t != None and t[2] < min_hds:
                self.logger.info("     -New Min hds = {0}".format(t[2]))
                min_hds = t[2]

        for ind in range(4):
            t_i = i
            t_j = j
            if temp[ind] != None and temp[ind][2] == min_hds:
                self.logger.info("  -sink filled to lvl of cell {0}-{1}".format(temp[ind][0],temp[ind][1]))
                faces[ind] = temp[ind]
        return faces
    #---------------------------------------------------------------------------
    # get hds for north,south, east, west faces.  then return the indexes of the
    # faces that have a lower hds than the current (center) cell.
    def get_flow(self,index, time):
        i = index[0]
        j = index[1]

        #    faces array( North, South, East, West)
        faces = []
        temp = self.sat_obj.loc[i,j]
        c_hds = temp['hds']
        self.logger.info("Cell flow for {0}-{1}: (hds = {2}; Last_time_step = {3} ({4}))".format(i,j, temp['hds'],temp['time_step'],int(temp['time_step']/365.25)+2018))
        faces.append(self.get_recieving_cell(i+1,j,temp['hds'],temp['time_step'])) #north
        faces.append(self.get_recieving_cell(i-1,j,temp['hds'],temp['time_step'])) #South
        faces.append(self.get_recieving_cell(i,j+1,temp['hds'],temp['time_step'])) #east
        faces.append(self.get_recieving_cell(i,j-1,temp['hds'],temp['time_step'])) #west
        if faces.count(None) == len(faces):
            self.logger.info("fixing sink at {0}-{1}".format(i,j))
            faces = self.fix_sink(i,j,faces)
        return faces

    #---------------------------------------------------------------------------
    # loop through all i,j addresses and define flow for addresses that are not
    # in the last time step.
    #['i','j','k','time_step','last_time_step','hds','top_depth','bot_depth','saturation']
    def build_flow(self):
        cell_flow = pd.DataFrame(columns=self.flow_cols)
        cell_flow = cell_flow.astype(self.f_types)
        cell_flow = cell_flow.set_index(self.index)
        count = 0
        for index, row in self.sat_obj.iterrows():

            if row['last_time_step'] == False:
                count += 1
                indexes = self.get_flow(index,row['time_step'])
                temp = pd.DataFrame([[index[0],index[1],row['time_step'],indexes]],columns=self.flow_cols)
                temp = temp.set_index(self.index)
                cell_flow = cell_flow.append(temp,sort=False)
        self.logger.info("total number of cells that go dry before final time step: {0}".format(count))
        return cell_flow
    #---------------------------------------------------------------------------
    #Create intermediate file for future use, so you dont have reprocess the HDS
    # and ref files.
    def pickle_data(self, fileName, data):
        file = os.path.join(self.pkl_dir, fileName)
        data.to_pickle(file)

    def create_meta_data(self,fileName):
        format_str = ['{' + str(place) + ':>15}' for place in range(len(self.sat_cols))]
        column_line = ''.join(format_str).format(*self.sat_cols)
        with open(os.path.join(self.pkl_dir, fileName.replace('.pkl', '_meta.txt')), 'w+') as file:
            file.write('The pickled saturation dataframe is organized with the following columns:\n')
            file.write(column_line)
            file.write('\n\n')
            file.write('-------------------------------------------------------------------------\n')
            format_str = ['{' + str(place) + ':>15}' for place in range(len(self.flow_cols))]
            column_line = ''.join(format_str).format(*self.flow_cols)
            file.write('The pickled flow dataframe is organized with the following columns:\n')
            file.write(column_line)
            file.write('\n\n')
            file.write('-------------------------------------------------------------------------\n')
            file.write('The inputs used to generate this dataframe from the binary were as follows:\n')
            file.write('Input binary file: {0}\n'.format(self.hds_file))
            file.write('Top Depth ref file: {0}\n'.format(self.top_ref))
            file.write('bottom depth ref files: {0}\n'.format(self.bot_ref))
            #file.write('Output file location: {0}\n'.format(self.outdir))
            #file.write('Output file name given: {0}\n'.format(filename))
            file.write('\n\nThe elapsed time for each stress period reported in the dataframe:\n')
            file.write('SP_No, Days\n')
            for sp in range(len(self.sp_times)):
                file.write('{0}, {1}'.format(sp,self.sp_times[sp]))
    #---------------------------------------------------------------------------
    # read in mt3d head file
    def read_hds_file(self):
        return bf.HeadFile(self.hds_file, precision='double')
    #---------------------------------------------------------------------------
    # read in existing pickled file
    def read_pickle(self, p_file):
        return pd.read_pickle(os.path.join(self.pkl_dir, p_file))
    #---------------------------------------------------------------------------
    #check if file exists in given directory
    def check_file_exists(self, dir,file):
        return os.path.isfile(os.path.join(dir,file))
    #------------------------ End of class:sat_obj------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#Load paramater file
def load_parameters(file):
    with open(file, "r") as dat:
        i = 0
        params = {}
        for line in dat:
            if i == 0:
                temp = line.rstrip()
                if temp.lower() == 'true':
                    params["isPickled"] = True
                else:
                    params["isPickled"] = False
            elif i == 1:
                params["pickleDir"] = line.rstrip()
            elif i == 2:
                params["satFile"] = line.rstrip()
            elif i == 3:
                params["flowFile"] = line.rstrip()
            elif i == 4:
                #params.update({"hds": Path(line.rstrip())})
                params.update({"hds": line.rstrip()})
            elif i == 5:
                params.update({"top_ref": line.rstrip()})
            elif i == 6:
                params.update({"bot_ref": line.rstrip().split(",")})
            elif i == 7:
                params.update({"input": line.rstrip()})
            elif i == 8:
                params.update({"output": line.rstrip()})
            elif i == 9:
                params.update({"sat_lvl": Decimal(line.rstrip())})
            elif i == 10:
                params.update({"max_i": int(line.rstrip())})
            elif i == 11:
                params.update({"max_j": int(line.rstrip())})
            elif i == 12:
                params.update({"max_k": int(line.rstrip())})
            elif i == 13:
                params.update({"start_year": Decimal(line.rstrip())})
            elif i == 14:
                params.update({"end_year": Decimal(line.rstrip())})
            elif i == 15:
                params.update({"tolerance": Decimal(line.rstrip())})
            i += 1
    return params
#-------------------------------------------------------------------------------
# Start main process
if __name__ == "__main__":
    ####
    # Setup Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("ref", type=str, help="file that contains meta data for run.")

    args = parser.parse_args()
    datfile = args.ref.rstrip()
    #pkl, pkl_d, bf, tr, br, i, j, k, msl
    params = load_parameters(datfile)
    print (params)
    sat = sat_obj(params["isPickled"],params["pickleDir"],params["satFile"],
            params["flowFile"],params['hds'],params['top_ref'],params['bot_ref'],
            params['max_i'],params['max_j'],params['max_k'],
            params["sat_lvl"],'')
    sat.flow_obj.to_csv(r'dry_cells.csv', header=True)
