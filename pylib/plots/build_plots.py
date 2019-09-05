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



#globals
m_200e = {}
#{'afarms':'A Farms','atrenches':'A Trenches','b3abponds':'B-3A/B Ponds',
#          'b3cpond':'B-3C Pond','b3pond':'B-3 Pond','b63':'B-63',
#          'bccribs':'BC Cribs & Trenches','bfarms':'B Farms','bplant':'B Plant',
#          'c-9_pond':'C-9 Pond','mpond':'M Pond','purex':'Purex'}
m_200w = {}
#{'lwcrib':'LW Crib','pfp':'PFP','redox':'Redox','rsp':'Redox Swamp/Pond',
#          'sfarms':'S Farms','salds':'SALDS','tfarms':'T Farms','tplant':'T Plant',
#          'u10':'U-10 West','ufarm':'U Farm','uplant':'U Plant'}
m_pa = {}
#{'wmac_past_leaks':'WMA C Past Leaks','wmac':'WMA C','erdf':'ERDF','idf':'IDF','usecology':'US Ecology'}
colors = {}
#{'afarms':'lime','atrenches':'red','b3abponds':'peru','b3cpond':'steelblue','b3pond':'teal',
#          'b63':'deeppink','bccribs':'deepskyblue','bfarms':'royalblue','bplant':'maroon','c-9_pond':'black',
#          'mpond':'orangered','purex':'fuchsia','lwcrib':'royalblue','pfp':'grey','redox':'navy',
#          'rsp':'maroon','sfarms':'orange','salds':'brown','tfarms':'Peru','tplant':'red',
#          'u10':'deeppink','ufarm':'aqua','uplant':'green','wmac_past_leaks':'red','wmac':'orange','erdf':'purple','idf':'blue','usecology':'green'}
copcs_chems = []
#['cn','cr','no3','u']
copcs_rads = []
#['h-3','i-129','sr-90','tc-99']
copcs = {}
#{'cn':'CN','cr':'CR','no3':'NO3','u':'Total U','h-3':'H-3',
#         'i-129':'I-129','sr-90':'SR-90','tc-99':'TC-99'}

#constants
FORMATTER = mtick.FormatStrFormatter('%.1e')
thisdir = os.path.abspath(os.path.dirname(__file__))
CONFIG_FILE = os.path.join(thisdir, "config.json")

def build_model(args):
    file = args.input.rstrip()
    out_dir = args.output.rstrip()
    head_row = 0
    with open(file,"r") as d:
        datafile = d.read()
        for line in datafile.splitlines():
            head_row += 1
            if line[0] != "#":
                tmp = line.strip().split(",") ##line.strip().replace("  "," ")
                if tmp[0].lower() == "time" or tmp[0].lower() == "year":
                    break
    df = pd.read_csv(file,index_col=0,header=head_row-1, skiprows=[head_row+1])
    df.rename(str.lower, axis='columns')
    columns = df.columns

    for col in columns:
        temp = col.strip()
        if col == "year":
            df.rename(index=str,columns={"year":"time"})
        elif "-" not in col and 'time' != col:
            df.drop([col],axis=1, inplace=True)
        elif "modflow_" in col:
            temp = col.replace("modflow_","")
            df.rename(index=str,columns={col:temp})
    model_name = get_model(file)
    copc,unit =get_copc(file)
    if not np.isreal(df.index[0]):
        df = df.iloc[1:]
    df.fillna(0)
    df = df.astype('float64')
    df.to_csv(os.path.join(out_dir,r'{}_{}_all_cells_units_{}.csv'.format(model_name,copc,unit)), header=True)
    return df, model_name, copc,unit

def build_data(args):
    dir = args.input.rstrip()
    out_dir = args.output.rstrip()

    files = []
    identifier = 0
    #data = pd.DataFrame(columns=['time'])
    #data = data.set_index('time')
    data = {}
    pa_data = pd.DataFrame(columns=['time'])
    pa_data = pa_data.set_index('time')
    models = {}#pd.DataFrame(columns=['time'])
    pa_mdoels = {}
    #models = models.set_index('time')

    for filename in os.listdir(dir):
        size = 0
        if filename.endswith(".csv"):
            dir_file = os.path.join(dir,filename)
            head_row = -1
            with open(dir_file,"r") as d:
                datafile = d.read()
                for line in datafile.splitlines():
                    head_row += 1
                    if line[0] != "#":
                        tmp = line.strip().split(",") ##line.strip().replace("  "," ")
                        if tmp[0].lower() == "time" or tmp[0].lower() == "year":
                            break
            df = pd.read_csv(dir_file,index_col=0,header=head_row, skiprows=[head_row+2])
            df.rename(str.lower, axis='columns')
            columns = df.columns
            for col in columns:
                temp = col.strip()
                if col == "year":
                    df.rename(index=str,columns={"year":"time"})
                elif "-" not in col and 'time' != col:
                    df.drop([col],axis=1, inplace=True)
                elif "modflow_" in col:
                    temp = col.replace("modflow_","")
                    df.rename(index=str,columns={col:temp})

            if not np.isreal(df.index[0]):
                df = df.iloc[1:]
            df.fillna(0)
            df = df.astype('float64')
            df.index = df.index.astype('int')
            model_name = get_model(filename)
            copc, unit =get_copc(filename)
            if copc in data.keys():
                t_data = data[copc]
            else:
                t_data = pd.DataFrame(columns=['time'])
                t_data = t_data.set_index('time')
            if model_name != None and copc != None:
                print('processing file: {} ({}, {})'.format(filename,model_name, copc))
                cols = list(df.columns)
                sf = df[cols].sum(axis=1)
                df = pd.DataFrame({"time":sf.index, model_name:sf.values})
                df = df.set_index('time')

                data[copc] = pd.concat([t_data,df],axis=1,sort=False)
                if model_name in models.keys():
                    if copc in models[model_name].keys():
                        df = pd.concat([models[model_name][copc]['rate'],df],axis=1,sort=False)
                        df.fillna(0)
                        # convert all cells from string to float
                        df = df.astype('float64')
                        # change negative numbers to 0
                        df[df < 0] = 0
                        #Sum together any duplicate columns
                        df = df.groupby(lambda x:x, axis=1).sum()
                        models[model_name][copc]['rate'] = df
                    else:
                        models[model_name][copc] = {'rate':df}
                else:
                    models[model_name] = {copc:{'rate':df}}
                models[model_name][copc]['cum'] = models[model_name][copc]['rate'].cumsum()
            else:
                print("skipping {}, model: {}, copc: {}".format(filename,model_name,copc))
                #change all NaN to 0
    for copc in data.keys():
        t_data = data[copc]
        t_data.fillna(0)
        # convert all cells from string to float
        t_data = t_data.astype('float64')
        # change negative numbers to 0
        t_data[t_data < 0] = 0

        #Sum together any duplicate columns
        t_data = t_data.groupby(lambda x:x, axis=1).sum()
        t_data.to_csv(os.path.join(out_dir,r'all_models_{}_units_{}.csv'.format(copc,unit)), header=True)
    return models

def get_model(file):
    for mdl in m_200e.keys():
        if mdl in file.lower():
            return mdl
    for mdl in m_200w.keys():
        if mdl in file.lower():
            return mdl
    for mdl in m_pa.keys():
        if mdl in file.lower():
            #if wmac check to make sure its not wmac past leaks
            if mdl.lower != 'wmac':
                return mdl
            elif 'leak' not in file.lower():
                return mdl
def get_copc(file):
    str1 = '-{}-'
    str2 = '_{}_'
    for copc in copcs_rads:
        if str1.format(copc) in file.lower() or str2.format(copc) in file.lower():
            return copc,'pci'
    for copc in copcs_chems:
        if str1.format(copc) in file.lower() or str2.format(copc) in file.lower():
            return copc,'ug'
    return None,None

def plot_model(args,data,model,copc,units):
    path = args.output.rstrip()

    matplotlib.rcParams['axes.formatter.useoffset'] = False
    name = ''
    if model in m_200e.keys():
        name = m_200e[model]
    else:
        name = m_200w[model]

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    n= data.columns.size
    colors = iter(cm.rainbow(np.linspace(0,1,n)))
    unit = []
    for cell in data.columns.values:
        c = next(colors)
        unit, values = unit_conversion(units,data[cell].values)
        ax.plot(data.index.values.astype('int'), values, color=c, label=cell, linewidth=.75)

    ax.set_ylabel("Rate ({})".format(unit[0]))
    ax.set_xlabel("Calendar Year")

    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.1,
                     box.width, box.height * 0.9])

    # Put a legend below current axis
    ax.legend(loc='upper center', fontsize=6, bbox_to_anchor=(0.5, -0.05),
              fancybox=True, shadow=True, ncol=5)

    ax.yaxis.set_major_formatter(FORMATTER)
    ax.set_yscale('log')
    #ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.set_title('{} Rates by cell {}'.format(copc.lstrip('_'),name))
    plt.savefig(os.path.join(path, "{}_flux_{}".format(copc.lstrip('_'),name)),bbox_inches='tight',dpi=1200)

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    colors = iter(cm.rainbow(np.linspace(0,1,n)))
    for cell in data.columns.values:
        c = next(colors)
        unit, values = unit_conversion(units, data[cell].cumsum().values)
        ax.plot(data.index.values.astype('int'), values, color=c, label=cell, linewidth=.75)
    ax.set_ylabel("Rate ({})".format(unit[0]))
    ax.set_xlabel("Calendar Year")

    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.1,
                     box.width, box.height * 0.9])

    # Put a legend below current axis
    ax.legend(loc='upper center', fontsize=6, bbox_to_anchor=(0.5, -0.05),
              fancybox=True, shadow=True, ncol=5)

    ax.yaxis.set_major_formatter(FORMATTER)
    ax.set_yscale('log')
    #ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.set_title('{} Cumulative by cell {}'.format(copc.lstrip('_'),name))
    plt.savefig(os.path.join(path, "{}_cum_{}".format(copc.lstrip('_'),name)),bbox_inches='tight',dpi=1200)

def build_plots(args,models,zone,name,copc,units):
    path = args.output.rstrip()
    start_year = int(args.startyear)
    end_year = int(args.endyear)
    matplotlib.rcParams['axes.formatter.useoffset'] = False
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    keys = models.keys()
    found = False
    time = []
    for mdl in zone.keys():
        if mdl in keys:
            if copc in models[mdl].keys():
                df = models[mdl][copc]['rate']
                if start_year != -1 and end_year != -1:
                    df = df.loc[start_year:end_year]
                if np.any(df > 0):
                    unit, values = unit_conversion(units,df)
                    time = df.index.values.astype('int')
                    #time = range(int(models[mdl][copc]['rate'].index.values[0]),int(models[mdl][copc]['rate'].index.values[-1])+1,1)

                    lbl = zone[mdl]
                    found = True
                    ax.plot(time, values, color=colors[mdl], label=lbl, linewidth=.75)
                #maj_loc = models[mdl][copc]['rate'].index.values.size/5
    if found:
        ax.set_ylabel("Rate ({})".format(unit[0]))
        ax.set_xlabel("Calendar Year")

        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1,
                         box.width, box.height * 0.9])

        # Put a legend below current axis
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
                  fancybox=True, shadow=True, ncol=5)

        ax.set_yscale('log')
        start, end = ax.get_xlim()
        if start_year == -1:
            start_year = start-1
        if end_year == -1:
            end_year = end+1

        ax.xaxis.set_minor_locator(AutoMinorLocator())
        ax.set_xlim(start_year,end_year)
        ticks = np.arange(start_year, end_year, int(len(time)/1000)*200)
        ax.xaxis.set_ticks(ticks)

        ax.set_title('{} Rates {}'.format(copcs[copc],name))
        plt.savefig(os.path.join(path, "{}_flux_{}".format(copc.lstrip('_'),name)),dpi=1200,bbox_inches='tight')
    plt.close()

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    keys = models.keys()
    found = False
    for mdl in zone.keys():
        if mdl in keys:
            if copc in models[mdl].keys():
                df = models[mdl][copc]['cum']
                if start_year != -1 and end_year != -1:
                    df = df.loc[start_year:end_year]
                if np.any(df > 0):
                    unit, values = unit_conversion(units,df)
                    time = df.index.values.astype('int')
                #time = models[mdl][copc]['cum'].index.values.astype('int')
                #    unit, values = unit_conversion(units,models[mdl][copc]['cum'].values)
                #if np.any(values > 0):
                    lbl = zone[mdl]
                    ax.plot(time, values, color=colors[mdl], label=lbl, linewidth=.75)
                    found = True
    if found:
        ax.set_ylabel("Rate ({})".format(unit[0]))
        ax.set_xlabel("Calendar Year")
        #ax.yaxis.set_major_formatter(FORMATTER)
        ax.set_yscale('log')
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1,
                         box.width, box.height * 0.9])

        # Put a legend below current axis
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
                  fancybox=True, shadow=True, ncol=5)

        start, end = ax.get_xlim()
        if start_year == -1:
            start_year = start-1
        if end_year == -1:
            end_year = end+1

        ax.xaxis.set_minor_locator(AutoMinorLocator())
        ax.set_xlim(start_year,end_year)
        ticks = np.arange(start_year, end_year, int(len(time)/1000)*200)
        ax.xaxis.set_ticks(ticks)

        ax.set_title('{} Cumulative {}'.format(copcs[copc],name))
        plt.savefig(os.path.join(path, "{}_cum_{}".format(copc.lstrip('_'),name)),bbox_inches='tight',dpi=1200)
    else:
        plt.close()
def unit_conversion(units,data):
    new_unit = ['Ci/year','Ci']
    factor = float(1)
    if units.lower() == 'pci':
        factor = float(1e-12)
    elif units.lower() in ['kg','g','ug']:
        new_unit = ['kg/year','kg']
        if units.lower() == 'g':
            factor = float(1e-3)
        elif units.lower() == 'ug':
            factor = float(1e-9)
    return new_unit, data*factor

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

#-------------------------------------------------------------------------------
# main process
def main():
    ####
    # Setup Arguments
    #parser = argparse.ArgumentParser()
    #parser.add_argument("input", type=str, help="out directory.")
    #parser.add_argument("output", type=str, help="out directory.")
    #parser.add_argument("-startyear", type=int, default=-1, help="start year of graph")
    #parser.add_argument("-endyear", type=int, default=-1, help="end year of graph")
    #parser.add_argument("-single", type=str2bool, nargs='?', const=True, default=False, help="Model all cells for single model.")
    #parser.add_argument("-config", type=str, default=thisdir, help="alternate configuration file")
    #args = parser.parse_args()
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

    global m_200e
    m_200e = config['m_200e']
    global m_200w
    m_200w = config['m_200w']
    global m_pa
    m_pa = config['m_pa']
    global colors
    colors = config['colors']
    global copcs_chems
    copcs_chems = config['copcs_chems']
    global copcs_rads
    copcs_rads = config['copcs_rads']
    global copcs
    copcs = config['copcs']
    #input_dir = args.input.rstrip()
    #out_dir = args.output.rstrip()
    #end_year = args.endyear
    #start_year = args.startyear
    #print(input_dir)
    #print(out_dir)
    #print(start_year)
    #print(end_year)
    if args.single:
        data,model,copc,unit = build_model(args)
        data.to_csv(os.path.join(args.output.rstrip(),r'{}_{}_all_cells.csv'.format(model,copc)), header=True)
        plot_model(args,data,model,copc,unit)
    else:
        models = build_data(args)
        for copc in copcs_chems:
            build_plots(args,models,m_200e,'200 East',copc,'ug')
            build_plots(args,models,m_200w,'200 West',copc,'ug')
            build_plots(args,models,m_pa,'PAs',copc,'ug')
        for copc in copcs_rads:
            build_plots(args,models,m_200e,'200 East',copc,'pci')
            build_plots(args,models,m_200w,'200 West',copc,'pci')
            build_plots(args,models,m_pa,'PAs',copc,'pci')
#-------------------------------------------------------------------------------
# Start main process
if __name__ == "__main__":
    #-------------------------------------------------------------------------------
    # build globals
    cur_date  = dt.date.today()
    time = dt.datetime.utcnow()

    testout = main()
