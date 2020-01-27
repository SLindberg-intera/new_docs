'''
Author:         Neil Powers
Date:           May 2019
Company:        Intera Inc.
Usage:          preprocess Vadose Zone flux/mass (merge overlapping cells, shift
                mass as cells go dry according to flow derived from MT3D Head file),
'''
import logging
import pandas as pd
import numpy as np
import os.path
class mass_obj:
    def __init__(self, dir,log,misc_p):
        self.input_dir = dir
        self.logger = logging.getLogger(log)
        self.misc_path = misc_p
        self.cell_map_header = ['i-j','total_mass','file']
        self.cell_map_index = 'i-j'
        self.cell_map = pd.DataFrame(columns=self.cell_map_header)
        self.cell_map = self.cell_map.set_index(self.cell_map_index)
        self.cells = self.build_cell_concentration()
        self.write_cell_map()
    def pad_start_years(self,start_y):
        stop_year = int(self.cells.index[0])
        start_year = start_y
        for year in range(start_year, stop_year, 1):
            self.cells = self.cells.append(pd.Series(name=year))
        self.cells = self.cells.sort_index()
    def pad_end_years(self,end_y):
        stop_year = end_y + 1
        #print(self.cells.index[self.cells.index.size - 10:self.cells.index.size - 1])
        start_year = int(self.cells.index[self.cells.index.size - 1]) + 1
        for year in range(start_year, stop_year,1):
            self.cells = self.cells.append(pd.Series(name=year))
        self.cells = self.cells.sort_index()
    #---------------------------------------------------------------------------
    # Convert all values to unit/day, and add days column 0 to last year by
    # 365.25
    def convert_to_daily(self,start_y, end_y):

        self.logger.debug("start_year: {0}".format(start_y))
        self.logger.debug("end_year  : {0}".format(end_y))
        self.logger.debug("length bef: {0}".format(self.cells.index.size))
        # check that data has the starting years already
        if not start_y in self.cells.index:
            self.pad_start_years(start_y)
        # check that data has the ending years already
        if not end_y in self.cells.index:
            self.pad_end_years(end_y)

        #print("index after adding missing years: {0}".format(self.cells.index))

        self.cells = self.cells.loc[start_y:end_y]

        self.logger.debug("length aft: {0}".format(self.cells.index.size))

        #if self.cells.columns.size >= 1:
        #    self.logger.debug("example1 bef: {0}".format(self.cells.loc[start_y,self.cells.columns[1]]))
        #    self.logger.debug("example2 bef: {0}".format(self.cells.loc[end_y,self.cells.columns[1]]))

        self.cells = self.cells /365.25

        #if self.cells.columns.size >= 1:
        #    self.logger.debug("example1 aft: {0}".format(self.cells.loc[start_y,self.cells.columns[1]]))
        #    self.logger.debug("example2 aft: {0}".format(self.cells.loc[end_y,self.cells.columns[1]]))
        row_count = self.cells.index.size
        self.cells['days'] = np.arange(0.0,float(row_count)*365.25, 365.25)
        #self.cells['days'] = np.arange(0.0,(float(end_y-start_y)*365.25)+366, 365.25)
        self.logger.debug("days       : \n {0}".format(self.cells['days']))

        #self.cells = self.cells.replace(r'\s+', np.nan, regex=True)
        self.cells = self.cells.fillna(0)
    #---------------------------------------------------------------------------
    # build dataframe map of which cells belong to which file/model and the total_mass
    # for each cell.
    def build_cell_map(self,filename,col,total_mass):
        file = "{0} ({1})".format(filename,total_mass)
        if col in self.cell_map.index.values:
            self.cell_map.loc[col,"file"].append(file)
            self.cell_map.loc[col,"total_mass"] += total_mass
        else:
            temp = pd.DataFrame([[col,total_mass,[file]]],columns=self.cell_map_header)
            temp = temp.set_index(self.cell_map_index)
            self.cell_map = self.cell_map.append(temp,sort=False)
    #---------------------------------------------------------------------------
    #
    def write_cell_map(self):
        self.cell_map.to_csv(os.path.join(self.misc_path,r'cell_map.csv'),header = True)
    #-------------------------------------------------------------------------------
    # build_cell_concentration
    def build_cell_concentration(self):
        self.logger.info("build cell Concentrations")
        files = []
        identifier = 0
        t_mass = {}
        cells = pd.DataFrame(columns=['time'])
        cells = cells.set_index('time')

        for filename in os.listdir(self.input_dir):
            size = 0
            if filename.endswith(".csv"):
                self.logger.info("loading file:  {}".format(filename))
                dir_file = self.input_dir+filename
                self.logger.info("   processing File: {0}".format(dir_file))
                head_row = -1
                with open(dir_file,"r") as d:
                    datafile = d.read()
                    for line in datafile.splitlines():
                        head_row += 1
                        if line[0] != "#":
                            tmp = line.strip().split(",") ##line.strip().replace("  "," ")
                            if tmp[0].lower() == "time" or tmp[0].lower() == "year":
                                break

                df = pd.read_csv(dir_file,index_col=0,header=head_row, skiprows=[head_row+1])
                df.rename(str.lower, axis='columns')
                columns = df.columns
                for col in columns:
                    temp = col.strip()
                    if col == "year":
                        self.logger.info("     -renaming column year to time")
                        df.rename(index=str,columns={"year":"time"})
                    elif "-" not in col:
                        self.logger.info("     -droping column {0} as its not cell flux".format(col))
                        df.drop([col],axis=1, inplace=True)
                    elif "modflow_" in col:
                        temp = col.replace("modflow_","")
                        self.logger.info("     -renaming column {0} to {1}".format(col,temp))
                        df.rename(index=str,columns={col:temp},inplace=True)
                        self.build_cell_map(filename,col,df[temp].sum())
                    elif "-" in col:
                        self.build_cell_map(filename,col,df[col].sum())

                cells = pd.concat([cells,df],axis=1,sort=False)

                #cells = cells.merge(df, left_index=True,right_index=True, how='outer')

        #change all NaN to 0
        cells = cells.fillna(0)
        # convert all cells from string to float
        cells = cells.astype('float64')
        # change negative numbers to 0
        cells[cells < 0] = 0
        #Sum together any duplicate columns
        cells = cells.groupby(lambda x:x, axis=1).sum()
        return cells
    #-----------------------------------------------------------------------
    #
    def find_proportion(self,data,ind):
        if data[ind] != None:
            # x/i=100/k
            k = 0
            for rec in data:
                if rec != None:
                    k += rec[2]
            y = 1
            i = data[ind][2]
            return ((y*i)/k)
        else:
            return 0
    #-----------------------------------------------------------------------
    # Creates column with proportional data from original cell then adds cell_loss
    # to the cells dataframe
    def create_proportional_data(self,face,data,prcnt):
        new_i_j = '{0}-{1}'.format(face[0],face[1])
        self.logger.info("      -shifting {0}% to cell {1}".format(prcnt,new_i_j))
        tmp_cell = data.copy()
        tmp_cell = tmp_cell.rename(new_i_j)
        self.logger.info("      -renaming cell to new name: {0}".format(tmp_cell.name))
        tmp_cell = tmp_cell * prcnt
        #self.cells = pd.concat([self.cells,tmp_cell],axis=1)
        return tmp_cell
    #-----------------------------------------------------------------------
    # log where mass came from and where it went
    def add_sum_to_log(self, df,f_ij,t_ij,data):
        if t_ij not in df.index:
            df = df.append(pd.Series(name=t_ij))
            # convert all cells from string to float
            df = df.astype('float64')
        if f_ij not in df.columns:
            df[f_ij] = pd.Series(name=f_ij, index=df.index)
            # convert all cells from string to float
            df = df.astype('float64')
        #change all NaN to 0
        df = df.fillna(0.0)
        #if np.isnan(df.at[t_ij,f_ij]):
        #    df.at[t_ij,f_ij] = float64(0)
        df.at[t_ij,f_ij] +=  data.sum(axis = 0, skipna = True)
        return df
    #-----------------------------------------------------------------------
    #
    def process_dry_cells(self,dry_cells,intrmdt_flag):
        more_dry_cells = True
        move_log = pd.DataFrame(columns=["i-j"])
        move_log = move_log.set_index("i-j")

        iteration = 0
        self.logger.info("Processing Flux from Cells that have have gone dry:")
        while more_dry_cells == True:
            proportional_data = pd.DataFrame(columns=['time'])
            proportional_data = proportional_data.set_index('time')
            iteration +=1
            more_dry_cells = False
            self.logger.info("  Iteration {0}".format(iteration))
            for index, cell in dry_cells.iterrows():
                #format i and j into same format as header 'i-j'
                i_j = '{0}-{1}'.format(index[0],index[1])
                if i_j in self.cells.columns:
                    self.logger.info("    Processing {0}".format(i_j))
                    #find index of the last time step that is <= the last saturated time step
                    time_step = cell[0]
                    #Find the index of the last time step before cell goes dry
                    self.logger.info("      Time_step:  {0}".format(time_step))
                    t_rows = self.cells.loc[:,'days'] > time_step
                    if t_rows[t_rows].index.size > 0:
                        first_dry_ind = min(t_rows[t_rows].index)
                        self.logger.info ("      index of first dry time step: {0}, {1}".format(first_dry_ind,self.cells.loc[first_dry_ind,"days"]))
                        #make copy of the rows to be distributed
                        cell_loss = self.cells.loc[first_dry_ind:,i_j].copy()
                        self.logger.info("      {0} size: {1}".format(cell_loss.name,cell_loss.size))
                        #check if data to be moved has any flux > 0  otherwise ignore
                        if (cell_loss > 0).any():
                            self.logger.info("      Cell {0}: dry after time step {1} ".format(i_j,cell[0]))
                            faces = cell[1]
                            more_dry_cells = True
                            #clear copied data from column
                            self.cells.loc[first_dry_ind:,i_j] = 0
                            self.logger.debug("Debug, sliced cell data: {0}".format(cell_loss))
                            #find and create proportional data
                            prcnt = self.find_proportion(faces,0)
                            if prcnt > 0:
                                temp = self.create_proportional_data(faces[0],cell_loss,prcnt)
                                proportional_data = pd.concat([proportional_data,temp],axis=1)
                                move_log = self.add_sum_to_log(move_log,i_j,'{0}-{1}'.format(faces[0][0],faces[0][1]),temp)
                            prcnt = self.find_proportion(faces,1)
                            if prcnt > 0:
                                temp = self.create_proportional_data(faces[1],cell_loss,prcnt)
                                proportional_data = pd.concat([proportional_data,temp],axis=1)
                                move_log = self.add_sum_to_log(move_log,i_j,'{0}-{1}'.format(faces[1][0],faces[1][1]),temp)
                            prcnt = self.find_proportion(faces,2)
                            if prcnt > 0:
                                temp = self.create_proportional_data(faces[2],cell_loss,prcnt)
                                proportional_data = pd.concat([proportional_data,temp],axis=1)
                                move_log = self.add_sum_to_log(move_log,i_j,'{0}-{1}'.format(faces[2][0],faces[2][1]),temp)
                            prcnt = self.find_proportion(faces,3)
                            if prcnt > 0:
                                temp = self.create_proportional_data(faces[3],cell_loss,prcnt)
                                proportional_data = pd.concat([proportional_data,temp],axis=1)
                                move_log = self.add_sum_to_log(move_log,i_j,'{0}-{1}'.format(faces[3][0],faces[3][1]),temp)

            self.cells = pd.concat([self.cells,proportional_data],axis=1)
            #change all NaN to 0
            self.cells=self.cells.fillna(0)
            #Sum together the duplicate columns that were just added
            # to the existing columns
            if intrmdt_flag:
                self.cells.to_csv(os.path.join(self.misc_path,r'dry_cell_flux_shift_itteration_{0}.csv'.format(iteration)),header = True)
            self.cells = self.cells.groupby(lambda x:x, axis=1).sum()
        #order index and columns of move_log
        move_log.sort_index(axis=0,inplace=True)
        move_log.sort_index(axis=1,inplace=True)
        move_log.to_csv(os.path.join(self.misc_path,r'flux_mass_shift_mapping.csv'.format(iteration)),header = True)
