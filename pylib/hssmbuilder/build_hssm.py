'''
Author:         Neil Powers
Date:           Apr 2019
Company:        Intera Inc.
Usage:          process MT3D Head and associated files to get cell saturation,
                preprocess Vadose Zone flux/mass (merge overlapping cells, shift
                mass as cells go dry according to flow derived from MT3D Head file),
                perform data reduction, and build HSSM package.
'''
#import numpy as np
from pathlib import Path
import sys, os
import argparse
import datetime as dt
import numpy as np
import pandas as pd
import os.path
import logging
import json

sys.path.append(
        os.path.join(os.path.dirname(__file__), '..','..'))
#custom libraries
from pylib.hssmbuilder.hssm_pkg import hssm_obj
from pylib.hssmbuilder.build_saturation import sat_obj
from pylib.hssmbuilder.preprocess_mass import mass_obj


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# set up Log handler
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
#def is_float(s):
#    try:
#        float(s)
#        return True
#    except ValueError:
#        return False
#-------------------------------------------------------------------------------
#Load paramater file
def load_parameters(file):
    with open(file, "r") as dat:
        params = json.load(dat)
        if "isPickled" not in params.keys():

            if "satFile" in params.keys():
                params["isPickled"] = False
            else:
                params["isPickled"] = True
            print("Warning: field 'isPickled' not found. defaulting to {}".format(params["isPickled"]))
        if "input" not in params.keys() or not os.path.isdir(params["input"]):
            print("ERROR:  field 'input' is missing or is not a valid directory")
            ValueError('Invalid input directory')
        if "output" not in params.keys():
            parms["output"] = "output/"
            print("Warning: field 'output' not found. defaulting to {}".format(parms["output"]))
        if "sat_lvl" not in params.keys():
            params["sat_lvl"] = .75
            print("Warning: field 'sat_lvl' not found. defaulting to {}".format(params["sat_lvl"]))
        if "tolerance" not in params.keys():
            params["tolerance"] = 1e-2
            print("Warning: field 'tolerance' not found. defaulting to {}".format(params["tolerance"]))
        if "mass_shift" not in params.keys():
            params["mass_shift"] = False
            print("Warning: field 'mass_shift' not found. defaulting to {}".format(params["mass_shift"]))
        if "data_reduction" not in params.keys():
            params["data_reduction"] = True
            print("Warning: field 'data_reduction' not found. defaulting to {}".format(params["data_reduction"]))
        if "flux_floor" not in params.keys():
            params["flux_floor"] = 1E-15
            print("Warning: field 'flux_floor' not found. defaulting to {}".format(params["flux_floor"]))
        if "max_tm_error" not in params.keys():
            params["max_tm_error"] = 2.25E7
            print("Warning: field 'max_tm_error' not found. defaulting to {}".format(params["max_tm_error"]))
        if "units" not in params.keys():
            params["units"] = "pCi"
            print("Warning: field 'units' not found. defaulting to {}".format(params["units"]))

    return params


#-------------------------------------------------------------------------------
# main process
def main():
    ####
    # Setup Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("ref", type=str, help="file that contains meta data for run.")

    pd.set_option('display.precision', 28)

    #try:
    args = parser.parse_args()
    datfile = args.ref.rstrip()
    if not os.path.isfile(datfile):
        if not os.path.isfile(datfile):
            print('Invalid inputs: {0} '.format(datfile))
            print('                File not found, exiting script.')
            return ValueError('Invalid file')

    params = load_parameters(datfile)

    log_dir = os.path.join(params['output'], 'log')
    misc_dir = os.path.join(params['output'], 'misc')
    step_dir = os.path.join(params['output'], 'step_format')
    if os.path.isdir(params["output"]):
        print('Invalid output directory: {0} '.format(params["output"]))
        print('                Directory Already Exists!')
        return ValueError('Output Directory already exists')
    try:
        os.mkdir(params["output"])
        os.mkdir(log_dir)
        os.mkdir(misc_dir)
        if ("stepwise" in params.keys() and params['stepwise']):
            os.mkdir(step_dir)
    except OSError:
        print("Creation of the directory %s failed" % params["output"])
    else:
        print("Successfully created the directory %s " % params["output"])

    log = os.path.join(log_dir,"build_hss_log_{0}.txt".format(cur_date.strftime("%Y%m%d")))
    formatter = logging.Formatter('%(asctime)-9s: %(levelname)-8s: %(message)s','%H:%M:%S')
    lvl = logging.INFO
    logger = setup_logger('logger', log, formatter, lvl)

    logger.info("inputs:")
    logger.info("   use pickle files: {0}".format(params["isPickled"]))
    logger.info("   pickle file Directory: {0}".format(params["pickleDir"]))
    logger.info("     saturation file name: {0}".format(params["satFile"]))
    logger.info("     flow file name: {0}".format(params["flowFile"]))
    logger.info("   cell input directory: {0}".format(params["input"]))
    logger.info("   modflow head: {0}".format(params["hds"]))
    logger.info("   modflow top: {0}".format(params["top_ref"]))
    logger.info("   modflow bottom: {0}".format(params["bot_ref"]))
    logger.info("   output dir:{0}".format(params["output"]))
    logger.info("   target saturation:{0}".format(params["sat_lvl"]))
    logger.info("   max I: {0}, max J:{1}".format(params["max_i"], params["max_j"]))
    logger.info("   year range: {0} - {1}".format(params["start_year"],params["end_year"]))
    logger.info("----------------------------------------------------")

    setup_logger('sat_obj', os.path.join(log_dir,'build_sat_data_log_{0}.log'.format(cur_date.strftime("%Y%m%d"))), formatter, lvl)
    setup_logger('mass_obj', os.path.join(log_dir,'build_mass_data_log_{0}.log'.format(cur_date.strftime("%Y%m%d"))), formatter, lvl)
    setup_logger('hssm_obj', os.path.join(log_dir,'build_hssm_build_log_{0}.log'.format(cur_date.strftime("%Y%m%d"))), formatter, lvl)
    #load saturation data
    sat = sat_obj(params["isPickled"],params["pickleDir"],params["satFile"],
            params["flowFile"],params['hds'],params['top_ref'],params['bot_ref'],
            params["hds_init_conditions"],params['max_i'],params['max_j'],params['max_k'],
            params["sat_lvl"],'sat_obj')


    sat.sat_obj.to_csv(os.path.join(misc_dir,r'saturation.csv'), header=True)
    #load mass/flux data
    mass = mass_obj(params["input"],'mass_obj',misc_dir)
    mass.cells.to_csv(os.path.join(misc_dir,r'01_all_cells_after_cell_merge.csv'), header=True)
    sat.flow_obj.to_csv(os.path.join(misc_dir,r'dry_cells.csv'), header=True)
    #convert flux to daily from yearly and add column for time in days
    mass.convert_to_daily(params["start_year"],params["end_year"])
    mass.cells.to_csv(os.path.join(misc_dir,r'02_all_cell_by_day.csv'), header=True)
    #Shift mass out of dry cells and move to saturated all_cells
    if params['mass_shift']:
        mass.process_dry_cells(sat.flow_obj, True)
        mass.cells.to_csv(os.path.join(misc_dir,r'03_all_cell_by_day_dry_cell_shifted.csv'), header=True)
    #create object to process data into HSSM package.
    if params["find_sat_layer_by_year"]:
        sat.build_saturation_by_year(params["isPickled"],params["yearlySatFile"])
        sat.year_sat.to_csv(os.path.join(misc_dir,r'yearly_saturation.csv'), header=True)
        hssm = hssm_obj(sat.year_sat,mass.cells,params,'hssm_obj',log_dir,misc_dir)
    else:
        hssm = hssm_obj(sat.sat_obj,mass.cells,params,'hssm_obj',log_dir,misc_dir)
    #clean memory space up a bit.
    sat = None
    mass = None
    #Create HSSM packages
    hssm.write_data(params["find_sat_layer_by_year"])
    logger.info("\n\n Application Completed Normally.")
    logger.info("----------------------------------------------------")
    logger.info("----------------------------------------------------")
    #except Exception as e:
    #    print('Unexpected Error: {0}'.format(e))
#-------------------------------------------------------------------------------
# Start main process
if __name__ == "__main__":
    #-------------------------------------------------------------------------------
    # build globals
    cur_date  = dt.date.today()
    time = dt.datetime.utcnow()
    testout = main()
