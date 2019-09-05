#plot one model for all cells per graph
#py ../build_plots.py data_tc-99/bccribs-tc-99-bot_yearly_steps.csv plots --single true
#plot all models in directory per graph
#py ../build_plots.py data_tc-99 plots
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
#import constants
from pylib.config.config import read_config
from pylib.autoparse.autoparse import config_parser


#constants
FORMATTER = mtick.FormatStrFormatter('%.1e')
thisdir = os.path.abspath(os.path.dirname(__file__))
CONFIG_FILE = os.path.join(thisdir, "config.json")

def build_model(args):
    file = args.input.rstrip()
    out_dir = args.output.rstrip()
    head_row = 0

    ind_cols = ['copc','mdl_id','shp_file_id','year']
    print (file)
    df = pd.read_csv(file,index_col=ind_cols,header=head_row)
    df.rename(str.lower, axis='columns')
    return df
#-------------------------------------------------------------------------------
# path: string, output directory
# copc: string, copc
# mdl : string, model name (average, maximum,etc)
# data: pandas dataframe,
#       keys:  shp_file_id, year
#       columns: shp_file_nm, shp_file_id, max, p95, p90, p75, p50
#
def plot_model(path,copc,mdl,data):
    #path = args.output.rstrip()
    matplotlib.rcParams['axes.formatter.useoffset'] = False
    shp = data.index.unique(level='shp_file_id')
    fig = plt.figure()
    f, ax = plt.subplots(2,2)

    #graph 1
    subset = data.iloc[data.index.get_level_values('shp_file_id') == shp[0]]
    subset = subset.reset_index(level='shp_file_id', drop=True)
    shp_name = subset['shp_file_nm'].values[0]
    shp_name = shp_name.rstrip('.shp').replace('_',' ')
    ax[0,0] = set_plot(ax[0,0],shp_name,subset,False)

    #graph2
    subset = data.iloc[data.index.get_level_values('shp_file_id') == shp[1]]
    subset = subset.reset_index(level='shp_file_id', drop=True)
    shp_name = subset['shp_file_nm'].values[0]
    shp_name = shp_name.rstrip('.shp').replace('_',' ')
    ax[0,1] = set_plot(ax[0,1],shp_name,subset,False)

    #graph3
    subset = data.iloc[data.index.get_level_values('shp_file_id') == shp[2]]
    subset = subset.reset_index(level='shp_file_id', drop=True)
    shp_name = subset['shp_file_nm'].values[0]
    shp_name = shp_name.rstrip('.shp').replace('_',' ')
    ax[1,0] = set_plot(ax[1,0],shp_name,subset,True)

    #graph4
    subset = data.iloc[data.index.get_level_values('shp_file_id') == shp[3]]
    subset = subset.reset_index(level='shp_file_id', drop=True)
    shp_name = subset['shp_file_nm'].values[0]
    shp_name = shp_name.rstrip('.shp').replace('_',' ')
    ax[1,1] = set_plot(ax[1,1],shp_name,subset,True)



    f.suptitle("{} ({})".format(copc,mdl),fontsize=14)
    plt.rc('xtick',labelsize=8)
    plt.rc('ytick',labelsize=8)
    plt.tight_layout()
    plt.savefig(os.path.join(path, "{}_{}".format(mdl,copc)),bbox_inches='tight',dpi=1200)

def set_plot(ax,name,data,top):
    cols = ['max','p95','p90','p75','p50']
    top_factor = .25
    if top:
        top_factor = .35
    #linestyles = ['-', '--', '-.', ':']
    #models = {1:'',2:'',3:'Average',4:'Maximum',5:'Average CTET 41',6:'Average CTET 630',7:'Maximum CTET 41',8:'Maximum CTET 630'}
    #mdl = data.index.unique(level='mdl_id')
    #ind = 0
    #for mdl_ind in mdl:
    #line = linestyles[ind]
    #    ind += 1
    #    subset = data.iloc[data.index.get_level_values('mdl_id') == mdl_ind]
    #    subset = subset.reset_index(level=['mdl_id'], drop=True)
    time = data.index.values
    for col in cols:
        #ax.plot(data.index.values.astype('int'), values, color=c, label=cell, linewidth=.75)
        #label = "{} {}".format(col,models[mdl_ind])
        #ax.plot(time, subset[col].values,linestyle=line, label=label, linewidth=.75)
        ax.plot(time, data[col].values, label=col, linewidth=.75)
    ax.FontSize = 9
    ax.set_ylabel("Rate (pCi/L)")
    ax.set_xlabel("Calendar Year")

    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * top_factor,
                     box.width, box.height * .9])

    # Put a legend below current axis
    ax.legend(loc='upper center', fontsize=4, bbox_to_anchor=(0.5, -0.25),
              fancybox=True, shadow=True, ncol=5)

    ax.yaxis.set_major_formatter(FORMATTER)
    ax.set_yscale('log')
    #ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.set_title(name)
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
    models = {1:'',2:'',3:'Average',4:'Maximum',5:'Average CTET 41',6:'Average CTET 630',7:'Maximum CTET 41',8:'Maximum CTET 630'}
    data = build_model(args)
    #index['shp_file_id','copc','mdl_id','year']

    copcs = data.index.unique(level='copc')
    mdl = data.index.unique(level='mdl_id')
    for mdl_ind in mdl:
        for copc in copcs:
            subset = data.iloc[data.index.get_level_values('mdl_id') == mdl_ind]
            subset = subset.iloc[subset.index.get_level_values('copc') == copc]
            if subset.size > 0:
                subset = subset.reset_index(level=['copc','mdl_id'], drop=True)
                plot_model(args.output.rstrip(),copc,models[mdl_ind],subset)


#-------------------------------------------------------------------------------
# Start main process
if __name__ == "__main__":
    #-------------------------------------------------------------------------------
    # build globals
    cur_date  = dt.date.today()
    time = dt.datetime.utcnow()

    testout = main()
