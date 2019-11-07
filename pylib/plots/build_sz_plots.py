#-------------------------------------------------------------------------------
# build_sz_plots
# penta_plot below format
#    ____
#    _  _
#    _  _
# quad_plot belwo format
#    _  _
#    _  _
# bi_plot below format
#    ____
#    ____
# set_plot formats and loads data for individual graphs
# build_max_data builds crosstab of max data by plot name
import sys,os
sys.path.append(
        os.path.join(os.path.dirname(__file__), '..','..'))

#from pathlib import Path
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator, FuncFormatter)
from matplotlib.pyplot import cm
import argparse
import datetime as dt
import pandas as pd
import numpy as np
import math
#import constants
from pylib.config.config import read_config
from pylib.autoparse.autoparse import config_parser
#constants
FORMATTER = mtick.FormatStrFormatter('%.1e')
thisdir = os.path.abspath(os.path.dirname(__file__))
CONFIG_FILE = os.path.join(thisdir, "config_sz.json")

class plot_obj:
    def __init__(self, **kwargs):
        self.set_plot_names(kwargs.get('plot_names',[]))
        self.set_line_style(kwargs.get('line_style',[]))
        self.set_line_color(kwargs.get('line_color',[]))
        self.set_plot_order(kwargs.get('plot_order',[]))
        self.set_data_def(kwargs.get('data_def',{}))
        self.set_index(kwargs.get('index','plot_id'))
        self.set_title(kwargs.get('title',''))
        self.set_path(kwargs.get('path','output'))
        self.set_file_name(kwargs.get('file_name','graph'))
        self.set_data(kwargs.get('data',pd.DataFrame()))
        self.set_start_year(kwargs.get('start_year',2000))
        self.set_end_year(kwargs.get('end_year',12000))
    #-----------------------------
    # Define line styles
    def set_line_style(self,styles):
        self.line_style = np.array(styles)
        if len(self.line_style) == 0:
            self.line_style = ['-', '--', '-.', ':']
    def set_line_color(self,colors):
        self.line_color = np.array(colors)
        if len(self.line_color) == 0:
            self.line_color = ["#9A321E", "#0072B2", "#E69F00","#4CE7C8", "#CC79A7",
                      "#6432C8","#D81B60"]
    def set_data_def(self,data_def):
        self.data_def = data_def
    def set_index(self,ind):
        self.index = ind
    def set_plot_names(self,names):
        self.plot_names = names
    def set_title(self,title):
        self.title = title
    def set_path(self, path):
        self.path = path
    def set_file_name(self,file_name):
        self.file_name = file_name
    def set_data(self,data):
        self.data = data
        if not self.data.empty:
            if self.plot_order.size == 0:
                self.set_plot_order(np.array(data.index.unique(level=index)))
    def set_plot_order(self,order):
        self.plot_order = np.array(order)
    def set_start_year(self,start):
        self.start_year = start
    def set_end_year(self,end):
        self.end_year = end
    #-------------------------------------------------------------------------------
    # path: string, output directory
    # file_name: string, name of the file to be created.
    # data: pandas dataframe,
    #       keys:  index, year
    #       columns: index_name,  data to be plotted against key(year)
    #
    def penta_plot(self):
        matplotlib.rcParams['axes.formatter.useoffset'] = False
        f, ax = plt.subplots(3, 2,sharey='all', sharex='all', figsize=(4, 6))
        f.set_size_inches(11, 12) #(11,10.5)
        #modify graph 1 to cover 2 columns in first row
        gs = ax[0, 0].get_gridspec()
        # remove the underlying axes
        ax[0, 1].remove()
        ax[0, 0].remove()
        axbig = f.add_subplot(gs[0, 0:],sharex=ax[1,0],sharey=ax[1,0])
        y_min = 1
        y_max = 10
        i = 0
        for plot_id in self.plot_order:
            subset = self.data.iloc[self.data.index.get_level_values(self.index) == plot_id]
            plot_name = self.get_plot_name(plot_id)
            subset = subset.reset_index(level=self.index, drop=True)
            legend = False
            top = 1.8
            if i == 0:
                top = 1.05
                axis = axbig
                legend =True
            elif i == 1:
                axis = ax[1,0]
            elif i == 2:
                axis = ax[1,1]
            elif i == 3:
                top = 1.5
                axis = ax[2,0]
            elif i == 4:
                top = 1.5
                axis = ax[2,1]
            i += 1
            if subset.empty == False:
                self.set_plot(axis,plot_name,subset,legend=legend, top_factor=top)
                axis.set_xlim(xmin=self.start_year,xmax=self.end_year)

                min_val, max_val = axis.get_ylim()
                if float(min_val) < y_min:
                    y_min = min_val
                if float(max_val) < y_max
                    y_max = max_val

            else:
                axis.remove()

        f.suptitle(self.title,fontsize=16)
        plt.set_ylim(ymin=y_min,y_max)

        plt.rc('xtick',labelsize=14)
        plt.rc('ytick',labelsize=14)
        plt.tight_layout()
        plt.savefig(os.path.join(self.path, self.file_name),bbox_inches='tight',dpi=1200)
        plt.close('all')
#-------------------------------------------------------------------------------
# path: string, output directory
# file_name: string, name of the file to be created.
# title1: string, first line of the plot title
# title2 : string, second line of the plot title
# title3: string, third line of the plot title
# type: string, ('Concentration', Pathway ('inhalation, direct contact, etc'))
# data: pandas dataframe,
#       keys:  index, year
#       columns: index_name,  data to be plotted against key(year)
#
#def quad_plot(path,file_name,title1,title2,title3,index,index_name,data,units):#copc,mdl,scenario,type,data,units):
    #path = args.output.rstrip()
#    matplotlib.rcParams['axes.formatter.useoffset'] = False
#    shp = data.index.unique(level=index)
#    f, ax = plt.subplots(2, 2,sharey='all', sharex='all', figsize=(4, 6))
    #f, ax = plt.subplots(2, 2)
#    f.set_size_inches(11, 9)
    #[([tk.set_visible(True) for tk in ax2.get_yticklabels()], [tk.set_visible(True) for tk in ax2.get_yticklabels()]) for ax2 in ax.flatten()]
#    row = 0
#    col = 0
#    top_row = True
    #max_v = data.max(numeric_only=True).max()
    #min_v = data.min(numeric_only=True).min()
    #graph 1
#    for i in range(0,shp.size):
#        if i == 1:
#            row = 0
#            col = 1
#        elif i == 2:
#            top_row = False
#            row = 1
#            col = 0
#        elif i == 3:
#            top_row = False
#            row = 1
#            col = 1
#        subset = data.iloc[data.index.get_level_values(index) == shp[i]]
#        if subset.size > 0:
#            shp_name = subset[index_name].values[0]
#            shp_name = shp_name.rstrip('.shp').replace('_',' ')
#            subset = subset.reset_index(level=index, drop=True)
#            subset = subset.drop([index_name], axis=1)
#            ax[row,col] = self.set_plot(ax[row,col],shp_name,subset,top_row,units,legend)

#        else:
            #ax[row,col].set_visible(False)
#            ax[row,col].axis('off')

    #ax[1,0].get_shared_y_axes().join(ax[0,0], ax[0,1], ax[1,0], ax[1,1])

#    f.suptitle("{}\n{}\n{}".format(title1,title2,title3),fontsize=16)
    #plt.ylim(min_v,max_v)
#    plt.rc('xtick',labelsize=12)
#    plt.rc('ytick',labelsize=12)
#    plt.tight_layout()
#    plt.savefig(os.path.join(path, file_name),bbox_inches='tight',dpi=1200)
#    plt.close('all')
#-------------------------------------------------------------------------------
#
    def bi_plot(self):
        matplotlib.rcParams['axes.formatter.useoffset'] = False

        f, (ax1, ax2) = plt.subplots(2,1,sharex='all', sharey='none', figsize=(4, 6))
        f.set_size_inches(11, 8.5)
        #graph = data.index.unique(level=self.index)
        #graph 1

        plot_id = self.plot_order[0]
        plot_name = self.get_plot_name(plot_id)
        subset = self.data.iloc[self.data.index.get_level_values(self.index) == plot_id]
        subset = subset.reset_index(level=self.index, drop=True)
        top = 1.05
        self.set_plot(ax1,plot_name,subset,legend=True, top_factor=top)
        ax1.set_xlim(xmin=self.start_year,xmax=self.end_year)
        y_min = 1
        min_val, max_val = ax1.get_ylim()
        if float(min_val) < y_min:
            y_min = min_val
        ax1.set_ylim(ymin=y_min)

        #graph 2
        plot_id = self.plot_order[1]
        plot_name = self.get_plot_name(plot_id)
        subset = self.data.iloc[self.data.index.get_level_values(self.index) == plot_id]
        subset = subset.reset_index(level=self.index, drop=True)

        top = 1.75
        self.set_plot(ax2,plot_name,subset,legend=True, top_factor=top,
                 y_scale='linear')
        ax2.set_xlim(xmin=self.start_year,xmax=self.end_year)
        ax2.set_ylim(ymin=0,ymax=100)
        f.suptitle(self.title,fontsize=16)

        plt.rc('xtick',labelsize=12)
        plt.rc('ytick',labelsize=12)
        plt.tight_layout()
        plt.savefig(os.path.join(self.path, self.file_name),bbox_inches='tight',dpi=1200)
        plt.close('all')
    #-------------------------------------------------------------------------------
    #
    def single_plot(path,file_name,data,**kwargs):
        matplotlib.rcParams['axes.formatter.useoffset'] = False

        f, ax = plt.subplots()
        f.set_size_inches(15,7)

        subset = self.data.reset_index(level=self.index, drop=True)
        #Restrict the size of the legend to less than 120 characters per line
        cols = subset.columns.values
        l_cols = find_num_legend_columns(cols)

        t_factor = get_legend_top_factor()
        self.set_plot(ax,'',subset,top_factor=t_factor
                ,legend_cols=l_cols,legend_anchor=(0., -.2, 1., .102))
        ax.set_xlim(xmin=self.start_year,xmax=self.end_year)
        y_min = 10
        min_val, max_val = ax.get_ylim()
        if float(min_val) < y_min:
            y_min = min_val
        ax.set_ylim(ymin=y_min)

        f.suptitle(self.title,fontsize=16)

        plt.rc('xtick',labelsize=12)
        plt.rc('ytick',labelsize=12)
        plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)
        plt.savefig(os.path.join(path, file_name),bbox_inches='tight',dpi=1200)
        plt.close('all')

#-------------------------------------------------------------------------------
#
#def single_line_bar_graph(path,file_name,data,**kwargs):
    #get data or defaults
#    title = kwargs.get('title','')
#    title_lines = kwargs.get('title_lines',1)
#    units = kwargs.get('units','')
#    index = np.array(kwargs.get('index','graphs'))
#    plot_names = np.array(kwargs.get('plot_names',[]))
#    plot_order = np.array(kwargs.get('plot_order',data.index.unique(level=index)))
#    start_year = kwargs.get('start_year',data.index.unique(level='year').min())
#    end_year = kwargs.get('end_year',data.index.unique(level='year').max())
#    plot_names = np.array(kwargs.get('plot_names',[]))
#    line_style = np.array(kwargs.get('line_style',[]))
#    line_color = np.array(kwargs.get('line_color',[]))
#    data_def = kwargs.get('data_def',{})
#    matplotlib.rcParams['axes.formatter.useoffset'] = False

#    f, ax = plt.subplots()
#    f.set_size_inches(15,7)

#    ax.set_xlim(xmin=start_year,xmax=end_year)

    #years = range(start_year,end_year,10)
#    years = data.index.get_level_values('year')
#    barWidth =8
    #subset = data.iloc[data.index.get_level_values("year") in years]
    #subset = data.iloc[data.index.isin(years,level="year")]
#    subset = data.reset_index(level=index, drop=True)
#    l_cols = find_num_legend_columns(subset.columns.values)

#    bar1=np.array(subset['H3'].values)
#    bar2=np.array(subset['Tc99'].values)
#    bar3=np.array(subset['I129'].values)

    #bar4=np.array(subset['Sr90'].values)
#    subset = subset.drop(["H3","Sr90","Tc99","I129"],axis=1)

    #bar1 starts at bottom of plot

#    ax.bar(years, bar1,barWidth, label='H3',color='#7f6d5f', edgecolor='white')
    # bar2 on top of bar1
#    ax.bar(years, bar2,barWidth, label='Tc99',bottom=bar1, color='#E69F00', edgecolor='white' )
    # bar3 on top of bar2
#    ax.bar(years, bar3,barWidth, label='I129',bottom=bar1 + bar2, color='#0072B2', edgecolor='white')
    #ax.bar(years, bar4,barWidth, label='Sr90',bottom=bar1+ bar2+bar3, color='#9A321E', edgecolor='white')

#    set_plot(ax,'',subset,top_factor=(.5+(title_lines*.22))
#                    ,legend_cols=l_cols,legend_anchor=(0., -.2, 1., .102)
#                    ,line_style=line_style, line_color=line_color,data_def=data_def)



    #ax.set_yscale('log')
#    f.suptitle(title,fontsize=16)
#    plt.rc('xtick',labelsize=12)
#    plt.rc('ytick',labelsize=12)
#    plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)
#    plt.savefig(os.path.join(path, file_name),bbox_inches='tight',dpi=1200)
#    plt.close('all')

    #-------------------------------------------------------------------------------
    # define individual plot
    def set_plot(self,ax, name, data, **kwargs):
        legend = kwargs.get('legend',True)
        top_factor = kwargs.get('top_factor',.5)
        legend_cols = kwargs.get('legend_cols',6)
        legend = kwargs.get('legend',True)
        legend_anchor = kwargs.get('legend_anchor',(.5,-.2))

        y_scale = kwargs.get('y_scale','log')
        subset, units = self.get_units(data)
        cols = subset.columns.values


        ls_i = 0
        i = 0
        remove = True
        for col in cols:
            time = subset.index.values
            ls = self.line_style[0]
            cr = self.line_color[i]

            if bool(self.data_def) and col in self.data_def.keys():
                ls = self.line_style[self.data_def[col][1]]
                cr = self.line_color[self.data_def[col][0]]
            else:
                i += 1
                if i > 6:
                    i=0
                    ls = self.line_style[ls_i]
                    ls_i += 1
            if data[col].sum() > 0:
                remove = False
                ax.plot(time, subset[col].values,color=cr,linestyle=ls, label=col, linewidth=1.5)
        if remove:
            ax.remove()
        else:

            ax.set_ylabel("{0: ^25}".format(units),fontsize=12)
            #ax.set_ylabel(units,fontsize=12)
            ax.yaxis.set_tick_params(which='both', labelleft=True)
            ax.yaxis.set_major_formatter(FORMATTER)
            ax.set_yscale(y_scale)
            ax.tick_params(labelsize=12)
            ax.set_xlabel("Calendar Year",fontsize=12)
            ax.xaxis.set_tick_params(which='both', labelbottom=True)
            ax.xaxis.set_minor_locator(AutoMinorLocator())
            box = ax.get_position()
            ax.set_position([box.x0, box.y0 + box.height * top_factor,
                                 box.width, box.height * .05])
            if legend:
                # Put a legend below current axis
                ax.legend(loc='upper center', fontsize=10, bbox_to_anchor=legend_anchor,
                      fancybox=True, shadow=True, ncol=legend_cols)

            ax.set_title(name,fontsize=14)
        return ax
    #-------------------------------------------------------------------------------
    #
    def get_plot_name(self,plot_id):
        plot_name = ''
        if plot_id < len(self.plot_names):
            plot_name = self.plot_names[plot_id]
        return plot_name
    #---------------------------------------------------------------------------
    #
    def get_legend_top_factor(self):
        num_lines = self.title.count("\n")
        return (.5+(num_lines*.22))
    #-------------------------------------------------------------------------------
    #-
    def find_num_legend_columns(self,cols):
        l_cols = 7
        l_len = 0
        i = 0
        #cols = data.columns.values
        for ind in range(len(cols)):
            l_len += len(cols[ind])
            i +=1
            if l_len > 120 and l_cols > i:
                l_cols = math.ceil(i / 2)
                i = 0
                l_len = 0
        return l_cols
    def get_units(self,data):

        unit = data['unit'].values[0]
        units = unit
        if 'pci' in unit.lower():
            units = "Concentration ({})".format(unit)
        elif 'mrem'in unit.lower():
            units = "Dose ({})".format(unit)

        return data.drop(["unit"],axis=1), units
#---------------------END CLASS-------------------------------------------------
#-------------------------------------------------------------------------------
# transform data into crosstab data of max concentration for each shape for by_graphs
#def build_max_data(data,index,index_names):
#    shp = data.index.unique(level=index)
#    max = pd.DataFrame(columns=['year'])
#    max = max.set_index('year')
#    max_g = pd.DataFrame(columns=['year'])
#    max_g = max_g.set_index('year')
#    for i in range(0,shp.size):
#        subset = data.iloc[data.index.get_level_values(index) == shp[i]]
#        name = index_names[shp[i]]
#        subset = subset.reset_index(level=index, drop=True)
#        subset.rename(columns = {'max':name}, inplace = True)
#        if name == 'Max':
#            max_g = pd.concat([max_g,subset[name]],axis=1,sort=False)
#        else:
#            max = pd.concat([max,subset[name]],axis=1,sort=False)
#    max = max.assign(graphs=lambda x: 'Max concentrations')
#    max_g = max_g.assign(graphs=lambda x: 'Max')
#    max = max.set_index(['graphs'], append=True)
#    max_g = max_g.set_index(['graphs'], append=True)
#    max = pd.concat([max,max_g],axis=1, sort=False,ignore_index=False)
#    return max
def build_model(args,config):
    file = args.input.rstrip()
    #out_dir = args.output.rstrip()
    head_row = 0
    cols = config["columns"]
    key_cols = config["key_cols"]
    df = pd.read_csv(file,index_col=key_cols,header=head_row,usecols=cols)
    df.rename(str.lower, axis='columns')

    return df
#-------------------------------------------------------------------------------
# main process
def main():
    ####
    # Setup Arguments
    config = read_config(CONFIG_FILE)
    arg_parcer = lambda : config_parser(config)
    args = arg_parcer()
    if args.alt_config != "":
        if not os.path.isfile(args.alt_config):
            if not os.path.isfile(args.alt_config):
                print('Invalid inputs: {0} '.format(args.alt_config))
                print('                File not found, exiting script.')
                return ValueError('Invalid file')

        config = read_config(args.alt_config.rstrip())
    models = config["models"]
    scenarios = config["scenarios"]
    mdl_keys = config["models_used"]
    index =config["graph_index"]
    index_name = config["graph_names"]
    data = build_model(args,config)

    copcs = data.index.unique(level='copc')
    mdl = data.index.unique(level='mdl_id')
    for copc in copcs:
        for mdl_ind in mdl:
            if mdl_ind in mdl_keys:

                subset = data.iloc[data.index.get_level_values('mdl_id') == mdl_ind]
                subset = subset.iloc[subset.index.get_level_values('copc') == copc]

                if subset.size and copc=='Tc99':
                    unit = subset['unit_out'].values[0]
                    subset = subset.reset_index(level=['copc','mdl_id'], drop=True)
                    subset.drop(["unit_out"],axis=1, inplace=True)
                    title1 = scenarios[mdl_ind]
                    title2 = "{} ({})".format(copc,models[mdl_ind])
                    title3 = "Concentration"
                    file_name = "{}_{}_{}".format(scenarios[mdl_ind],models[mdl_ind],copc)
                    #quad_plot(args.output.rstrip(),file_name,title1,title2,title3,index,index_name,subset,unit)
                    penta_plot(args.output.rstrip(),file_name,title1,title2,title3,index,index_name,subset,unit)
                    if "max" in subset.columns.values:
                        file_name = "{}_{}_{}_global".format(scenarios[mdl_ind],models[mdl_ind],copc)
                        title1 = ""
                        title2 = "{} ({})".format(copc,models[mdl_ind])
                        title3 = "Concentration"
                        bi_plot(args.output.rstrip(),file_name,title1,title2,title3,'graphs','graphs',build_max_data(subset,index,index_name),unit)

#-------------------------------------------------------------------------------
# Start main process
if __name__ == "__main__":
    #---------------------------------------------------------------------------
    # build globals
    cur_date  = dt.date.today()
    time = dt.datetime.utcnow()

    testout = main()
