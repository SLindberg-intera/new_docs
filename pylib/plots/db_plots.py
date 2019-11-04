import psycopg2 as psy
import sys,os
sys.path.append(
        os.path.join(os.path.dirname(__file__), '..','..'))
#import argparse
import pandas as pd
import numpy as np
#import constants
from pylib.config.config import read_config
from pylib.autoparse.autoparse import config_parser
#import class
from build_sz_plots import plot_obj
#-------------------------------------------------------------------------------
# query database
def query_db(config, args):

    conn = psy.connect(host=args.host.rstrip(),database=args.db.rstrip(),
                        user=args.user.rstrip(), password=args.password.rstrip())
    df = pd.read_sql(config["plot_sql"], conn)
    df = df.set_index(config["key_cols"])
    df = df.sort_index()
    return df
#-------------------------------------------------------------------------------
# build plots
def build_plots(data,config,args):
    keys1 = data.index.unique(level='data_key1')
    keys2 = data.index.unique(level='data_key2')
    models = config["models"]
    scenarios = config["scenarios"]
    plot_names = config["plot_names"]
    plot_size = config["plot_size"]
    file_mod = config["file_mod"]
    #plot_order = config["plot_order"]
    #data_def = config.get("data_def", {})
    #l_color = config.get("line_color", [])
    #l_style = config.get("line_style", [])
    exclude_cols = config.get("exclude_cols", [])
    f_data = data
    for col in exclude_cols:
        if col in f_data.columns.values:
            f_data = f_data.drop([col], axis=1)
    plots = plot_obj(scenarios = config["scenarios"], plot_order = config["plot_order"], plot_names = plot_names,
                     data_def = config.get("data_def", {}), line_color = config.get("line_color", []), line_style = config.get("line_style", []),
                     start_year=config['start_year'],end_year=config['end_year'],index='plot_id',path=args.output.rstrip())
    i = 0
    for key1 in keys1:
        for key2 in keys2:
            subset = f_data.iloc[f_data.index.get_level_values('data_key2') == key2]
            subset = subset.iloc[subset.index.get_level_values('data_key1') == key1]
            if subset.size > 0 and (len(config['restrict_keys']) == 0 or key1 in config['restrict_keys']):

                subset = subset.reset_index(level=['data_key1','data_key2'], drop=True)


                t1 = config["title_line_1"].format(key1)
                t2 = ""
                t3 = ""
                if len(config["title_line_2"]) > 0:
                    t2 = config["title_line_2"].format(plot_names[key1])
                if len(config["title_line_3"]) > 0:
                    t3 = config['title_line_3']
                plots.set_file_name( "{}_{}_{}_{}_{}".format(scenarios[key2],models[key2],key1,file_mod,i))
                plots.set_data(subset)
                i+=1
                title = "{}\n{}\n  \n{}".format(t1,t2,t3)

                if plot_size == 5:
                    plots.set_title = title
                    plots.penta_plot()
                elif plot_size == 2:
                    plots.set_title = title
                    plots.bi_plot()
                elif plot_size == 1:
                    title = "{}\n{}\n".format(t1,t2)
                    plots.set_title = title
                    plots.single_plot()
                #elif plot_size == 0:
                #    title = "{}\n{}\n".format(t1,t2)
                #    plots.single_line_bar_graph(args.output.rstrip(), file_name,subset,
                #                    start_year=config['start_year'], end_year=config['end_year'],
                #                    title=title, index='plot_id',
                #                    plot_names=plot_names, plot_order=plot_order,
                #                    title_lines=2,line_color=l_color,line_style=l_style,
                #                    data_def = data_def)
    build_csv(args.output.rstrip(),"{}.csv".format(file_mod),data,config)
#-------------------------------------------------------------------------------
# build csv
def build_csv(dir,name,data,config):
    #keys1 = data.index.unique(level='data_key1')
    keys = data.index.unique(level='data_key2')
    scenarios = config["scenarios"]
    models = config["models"]
    data['model'] = ''
    data['scenario'] = ''
    data['plot_name'] = ''
    for key in keys:
        #data.loc[data.index.get_level_values("data_key2") == key] = models[key]
        data.loc[data.index.get_level_values("data_key2") == key,'model'] = models[key]
        data.loc[data.index.get_level_values("data_key2") == key,'scenario'] = scenarios[key]
    plot_names = config["plot_names"]
    plots = config["plot_names"]
    keys = data.index.unique(level='plot_id')
    for key in keys:
        data.loc[data.index.get_level_values('plot_id') == key,'plot_name'] = plots[key]
    data.to_csv(os.path.join(dir,name), header=True)

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
    data = query_db(config,args)
    build_plots(data,config,args)

#-------------------------------------------------------------------------------
# Start main process
if __name__ == "__main__":
    #---------------------------------------------------------------------------
    # build globals
    #cur_date  = dt.date.today()
    #time = dt.datetime.utcnow()
    thisdir = os.path.abspath(os.path.dirname(__file__))
    CONFIG_FILE = os.path.join(thisdir, "config_db.json")
    testout = main()
