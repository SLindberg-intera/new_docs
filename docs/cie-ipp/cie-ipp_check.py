"""
Author:         Jacob B Fullerton
Date:           March 16, 2020
Company:        Intera Inc.
Usage:          Intended for internal use at Intera Inc. to evaluate that the functional requirements of the inventory
                preprocessing script are met
Functional Req's to verify from ca-ipp:
                1.  Final output includes all solid waste release sites and inventory
                2.  Final output includes all rerouted waste site and stream
                3.  Final output includes all SAC sites and water volumes where not present in SIMV2 AND present in
                    VZEHSIT
                4.  Final output includes all SIMV2 sites and inventory except where:
                    a.  No date was provided with waste inventory
                    b.  SIMV2 was replaced with solid waste release data
                    c.  SIMV2 was replaced with rerouted information
                    d.  SIMV2 sites are not present in VZEHSIT
Pseudo Code:    The code in general works in the following manner:
                1.  Read primary sources used by cie-ipp.pl script:
                    a.  VZEHSIT
                    b.  RADINV (SIMV2)
                    c.  LIQINV (SAC)
                    d.  CHEMINV (chemical inventory)
                    e.  REROUTED Sites/Inventory
                2.  Build dictionary from primary sources
                3.  Read final output from cie-ipp.pl and verify that it contains the right records
"""
import os
import argparse
import pandas as pd
import logging
import math
from copy import deepcopy


# ----------------------------------------------------------------------------------------------------------------------
# Utility functions


def file_path(mystr):
    if os.path.isfile(mystr):
        return mystr
    else:
        raise FileNotFoundError("File path provided does not exist: {}".format(mystr))


def dir_path(mystr):
    if os.path.isdir(mystr):
        return mystr
    else:
        raise IsADirectoryError("Path provided is not a directory: {}".format(mystr))


def is_RCASWR_idx(idx_name, rcaswr_dir):
    file = os.path.join(rcaswr_dir, idx_name)
    if os.path.isfile(file):
        return
    else:
        raise FileNotFoundError("The file name/path does not exist: {}".format(file))


def get_unique_vals(df, col):
    for val in df[col].unique():
        yield val


def configure_logger(path, verbosity):
    if verbosity.upper() == 'ALL':
        verbosity = 0
    logging.basicConfig(
        filename=path,
        level=verbosity,
        filemode='w',
        format='%(message)s'
    )


def round_sigfigs(num, sig_figs):
    """Round to specified number of sigfigs. Credit to @"Ben Hoyt" on www.code.activestate.com
    >>> round_sigfigs(0, sig_figs=4)
    0
    >>> int(round_sigfigs(12345, sig_figs=2))
    12000
    >>> int(round_sigfigs(-12345, sig_figs=2))
    -12000
    >>> int(round_sigfigs(1, sig_figs=2))
    1
    >>> '{0:.3}'.format(round_sigfigs(3.1415, sig_figs=2))
    '3.1'
    >>> '{0:.3}'.format(round_sigfigs(-3.1415, sig_figs=2))
    '-3.1'
    >>> '{0:.5}'.format(round_sigfigs(0.00098765, sig_figs=2))
    '0.00099'
    >>> '{0:.6}'.format(round_sigfigs(0.00098765, sig_figs=3))
    '0.000988'
    """
    if num != 0:
        return round(num, -int(math.floor(math.log10(abs(num))) - (sig_figs - 1)))
    else:
        return 0  # Can't take the log of 0


def is_integer(mystr):
    try:
        int(mystr)
        return True
    except:
        return False


def normalize_col_names(old_col, water_col=None, chm_col=False):
    """
    :param old_col:     Old column name to change
    :param water_col:   If water column, the old column name will match the string provided
    :param chm_col:     If reformatting a chemical column
    :return:
    """
    # For radionuclide waste columns
    if water_col is None and chm_col is False:
        new_copc = old_col.replace(' (decay only)', '').upper()
        new_col = '{}(ci/year)'.format(new_copc)
    # For chemical waste columns
    elif chm_col:
        new_copc = old_col.replace('-Total', '').replace(' [kg]', '').upper()
        new_col = '{}(kg/year)'.format(new_copc)
    else:
        new_copc = 'WATER'
        new_col = '{}(m^3/year)'.format(new_copc)
    return new_copc, new_col


def clean_df(df, drop_cols):
    """
    Removes the unwanted columns, and "NAN" records.
    This will NOT take into account whether all of your records are kept. If a "NAN"  cell is present in the row,
    the function will exclude the row and return the new dataframe. This will also summarize/sum by year (no duplicate
    years will be kept, unique years and corresponding values only). If two years with different values are present,
    the function will return a single year with an sum of the different values of the same year.
    :param df:          Dataframe to be cleaned
    :param drop_cols:   "List" data type containing strings representing column names
    :return:
    """
    try:
        for col in drop_cols:
            df = df.drop(labels=col, axis=1)
        df = df.dropna()
        df = df.reset_index(drop=True)
    except TypeError:
        raise TypeError("This function expects a dataframe with an iterable")
        exit()
    # Groupby years, then return as dataframe
    df = pd.DataFrame(df.groupby(by='year', as_index=False).sum())
    return df


# ----------------------------------------------------------------------------------------------------------------------
# User Input (Parser)


parser = argparse.ArgumentParser()
parser.add_argument('--VZEHSIT',
                    dest='vzehsit',
                    type=file_path,
                    required=True,
                    help='Provide the path to the VZEHSIT work product from the ICF'
                    )
parser.add_argument('--VZINV',
                    dest='vzinv',
                    type=file_path,
                    help='Provide the path to the VZINV work product from the ICF'
                    )
parser.add_argument('--CHEMINV',
                    dest='cheminv',
                    type=file_path,
                    help='Provide the path to the CHEMINV work product from the ICF'
                    )
parser.add_argument('--CLEANINV',
                    dest='cleaninv',
                    type=file_path,
                    help='Provide the path to the CLEANINV work product from the ICF'
                    )
parser.add_argument('--RCASWR_dir',
                    dest='rcaswr_dir',
                    type=dir_path,
                    help='Provide the path to the RCASWR work product data directory from the ICF'
                    )
parser.add_argument('--RCASWR_idx',
                    dest='rcaswr_idx',
                    type=str,
                    help='Provide only the filename of the RCASWR index file from the ICF (do not include path)'
                    )
parser.add_argument('--REROUTE',
                    dest='reroute',
                    nargs='+',
                    type=file_path,
                    help='Provide each rerouting work product file (and path) from the ICF, separated by spaces'
                    )
parser.add_argument('-i', '--ipp_output',
                    dest='ipp_output',
                    type=file_path,
                    help='Provide the file and associated path (can be relative) to the cie-ipp.pl output file being\n'
                         'verified. This should be a CSV file.'
                   )
parser.add_argument('--COPCs',
                    dest='copcs',
                    nargs='+',
                    type=str,
                    default=[
                        'H-3',
                        'I-129',
                        'Sr-90',
                        'Tc-99',
                        'U',
                        'Cr',
                        'NO3',
                        'CN'
                    ],
                    help='This flag allows you to define which constituents/analytes to include in the check. Call\n'
                         'the flag in the commandline for as many COPCs that need to be checked.'
                    )
parser.add_argument('--exclude_solids',
                    dest='exclude_solids',
                    type=bool,
                    default=True,
                    help='This flag allows you to specify whether to include solids. Liquids will always be included,\n'
                         'and any "entrained solids" will be treated as liquids. Default is [True], meaning that \n'
                         'solids will not be included (solid sources that are not "entrained solids").'
                    )
parser.add_argument('-o', '--output',
                    dest='output',
                    type=dir_path,
                    default=os.getcwd(),
                    help='Directory in which to store files'
                    )
parser.add_argument('--verbosity',
                    dest='verbosity',
                    choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "ALL"],
                    default="ALL",
                    help='Set the verbosity to produce more/less output in the log file.\n'
                         '"ALL" is equivalent to "NOTSET" when setting the logger and will print all messages.'
                    )
args = parser.parse_args()


# ----------------------------------------------------------------------------------------------------------------------
# Primary functions


def csv_parser(path, skip_lines, use_cols=None, col_names=None, codec='utf-8'):
    """
    :param codec:           Encoding to be used when parsing CSV file
    :param path:            Path to CSV file being parsed
    :param skip_lines:      Number of lines to skip at the top of the file, may be integer or list
    :param use_cols:        Columns to be used from the file being parsed
    :param col_names:       Column names to be used in output dataframe
    :return:
    """
    if use_cols is None and col_names is None:
        df = pd.read_csv(path, engine='c', skiprows=skip_lines, encoding=codec)
    elif use_cols is None:
        df = pd.read_csv(path, engine='c', skiprows=skip_lines, names=col_names, encoding=codec)
    elif col_names is None:
        df = pd.read_csv(path, engine='c', skiprows=skip_lines, usecols=use_cols, encoding=codec)
    else:
        df = pd.read_csv(path, engine='c', skiprows=skip_lines, usecols=use_cols, names=col_names, encoding=codec)
    # Make sure to clean up all trailing spaces for all columns
    for col in df.columns:
        try:
            df[col] = df[col].str.strip()
        except:
            continue
    return df


def stomp_format_parser(path, skip_pattern='241'):
    # Load whole file into memory as dictionary whose levels consist of:
    #   site-name
    #   --->dataframe (with columns for: [year, volume(m^3)]
    with open(path, 'r') as file:
        # Skip the header line
        line = next(file).split(',')
        new_lex = {}
        # Count the number of sites
        site_counter = 0
        # Collect duplicate sites for logging
        dup_sites = []
        # Collect sites without data for logging
        no_data_sites = []
        # Collect sites to be skipped
        skip_sites = []
        for line in file:
            # Remove line endings in case of mixed input
            line = line.replace('\n', '').replace('\r', '').replace('"', '')
            line = line.upper().split(',')
            # Obtain the site and number of conditions and iterate over each condition
            try:
                site, num_conds = line[0], int(line[1])
            except:
                # Catch the case where line[0] is tritium "H3"
                if 'H3' in line[0]:
                    continue
                else:
                    logging.critical("##Failed to parse SAC work product")
                    exit()
            site_counter += 1
            data_series = []
            while num_conds > 0:
                # Conditions need to be evaluated by using the first position of the list, if it's numeric it's a cond.
                line = next(file).replace('\n', '').replace('\r', '')
                line = line.split(',')
                if is_integer(line[0]):
                    num_conds -= 1
                else:
                    continue
                if 'm^3' in line[3] and is_integer(line[0]):
                    year, volume = int(line[0]), float(line[5])
                    data_series.append([year, volume])
            # Add the new site and associated water volumes if there's data present, else continue
            if site not in new_lex and len(data_series) > 0:
                if skip_pattern in site:
                    skip_sites.append(site)
                    continue
                df = pd.DataFrame(data_series, columns=['year', 'WATER(m^3/year)'])
                new_lex[site] = {'WATER': df}
            # Track all duplicate and no data sites in logger
            elif site in new_lex:
                dup_sites.append(site)
            if len(data_series) == 0:
                no_data_sites.append(site)
        logging.info("##Total number of sites in SAC: {}".format(site_counter))
        logging.info("##Number of sites with data from SAC: {}".format(len(new_lex)))
        if len(dup_sites) > 0:
            logging.debug("##SAC Inventory has duplicate entries for the following sites ({}):".format(len(dup_sites)))
            for site in sorted(dup_sites):
                logging.debug(site)
        if len(no_data_sites) > 0:
            logging.info("##SAC Inventory Sites with no Data ({}):".format(len(no_data_sites)))
            for site in sorted(no_data_sites):
                logging.info(site)
        if len(skip_sites) > 0:
            logging.info("##SAC Inventory Sites to be excluded ({}):".format(len(skip_sites)))
            for site in sorted(skip_sites):
                logging.info(site)
    return new_lex


def combine_lex(lex1, lex2):
    """
    This will combine site records from lex2 into lex1 if (*IF*) lex1[site].keys() == 0 (i.e. has not received other
    information from another primary source)
    :param lex1:        Dictionary to combine information into, should start out as a dictionary with sites and no
                        other nested keys (i.e. len(lex1[site].keys()) = 0 should yield True)
    :param lex2:        Dictionary of site records from a primary source to be combined into lex1
    :return:            Combined dictionary, dictionary of sites and streams used from primary source
    """
    used_lex = {}
    for site in lex1:
        # This conditional statement prevents the function from adding information to a site record where another
        # primary source has already provided information. An example is if the rerouted sites source has information
        # for a site, then a subsequent source like SIMv2 should not be allowed to provide any new information for the
        # same site.
        if len(lex1[site].keys()) > 0:
            continue
        # If there is information from the source being added for the site in question...
        if site in lex2:
            used_lex[site] = []
            for copc in lex2[site]:
                used_lex[site].append(copc)
                lex1[site][copc] = lex2[site][copc]
    return lex1, used_lex


class InvObj:
    def __init__(self, user_args):
        self.inv_args = deepcopy(user_args)         # User arguments passed from namespace as namespace
        if hasattr(self.inv_args, "copcs"):         # Make all copc's uppercase for consistency
            self.inv_args.copcs = [c.upper() for c in self.inv_args.copcs] + ['WATER']
        self.vz_sites = self.parse_vzehsit()        # Parse list of accepted waste sites as generator
        self.inv_lex = self.init_lex()              # Initialize final inventory dictionary
        self.chm_cols = {                           # Chemical columns (general match for input files, no uppercase)
            'Cr',
            'NO3',
            'U',
            'CN'
        }
        if self.inv_args.rcaswr_dir is not None or self.inv_args.rcaswr_idx is not None:
            self.swr_lex = self.parse_swr()         # Solid waste release dictionary
        if self.inv_args.reroute is not None:
            self.red_lex = self.parse_red()         # Rerouted waste releases dictionary
        if self.inv_args.cleaninv is not None:
            self.sac_lex = self.parse_sac()         # SAC liquid-only inventory
        if self.inv_args.cheminv is not None:
            self.chm_lex = self.parse_chm()         # Chemical Inventory
        if self.inv_args.vzinv is not None:
            self.sim_lex = self.parse_sim()         # SIMV2 RAD inventory
        self.inv_lex = self.build_inv()             # Populate final inventory dictionary
        self.inv_lex = self.clean_inv()             # Clean up any sites that don't have any waste streams/water sources

    def parse_vzehsit(self):
        path = self.inv_args.vzehsit
        with open(path, 'r') as file:
            next(file)
            for line in file:
                # Read only the first column of each line for the waste site names
                site = line.upper().split(',')[0]
                if site != '':
                    yield site.upper()

    def init_lex(self):
        # Iterates over the list of waste sites parsed from VZEHSIT to generate a master dictionary
        new_lex = {}
        site_counter = 0
        sites_used = 0
        dup_sites = []
        for site in self.vz_sites:
            if site not in new_lex:
                new_lex[site] = {}
                sites_used += 1
            else:
                dup_sites.append(site)
            site_counter += 1
        logging.info("##Parsed VZEHSIT:\n"
                     "##Total number of sites in VZEHSIT: {0}\n"
                     "##Total number of sites used (excluding duplicates): {1}".format(site_counter, sites_used)
                     )
        if len(dup_sites) > 0:
            logging.debug("##Sites with duplicate entries in VZEHSIT:")
            for site in set(dup_sites):
                logging.debug('{}'.format(site))
        return new_lex

    def parse_swr(self):
        # Pulls all files but the index file and parses them into corresponding entries in the master dictionary
        swr_dir = self.inv_args.rcaswr_dir
        new_lex = {}
        not_vzehsit = []
        site_counter = 0
        for swr_file in next(os.walk(swr_dir))[2]:
            if swr_file != self.inv_args.rcaswr_idx:
                # All files except for the index file are delimited by '_', so splitting yields a list of:
                #   [waste site, waste stream]
                site_name, copc = swr_file.upper().replace('.CSV', '').split('_')
                if site_name not in self.inv_lex:
                    not_vzehsit.append(site_name)
                path = os.path.join(swr_dir, swr_file)
                site_df = csv_parser(path, 4)
                # Rename the columns to be consistent with the rest of the check
                site_df['year'] = site_df["Reduced Year"]
                site_df['{}(ci/year)'.format(copc)] = site_df["Reduced Activity Release Rate (Ci/year)"]
                site_df = clean_df(site_df, ["Reduced Year", "Reduced Activity Release Rate (Ci/year)"])
                if len(site_df) == 0:
                    continue
                if site_name not in new_lex:
                    site_counter += 1
                    new_lex[site_name] = {copc: site_df}
                else:
                    new_lex[site_name][copc] = site_df
        if len(not_vzehsit) > 0:
            logging.debug("##Solid Waste Release sites NOT in VZEHSIT")
            for site in not_vzehsit:
                logging.debug("{}".format(site))
        else:
            logging.info("##Total number of Solid Waste Release Sites: {}".format(site_counter))
            logging.info("##All Solid Waste Release Sites are present in VZEHSIT")
        return new_lex

    def parse_red(self):
        new_lex = {}
        # Waste site column to use for building dictionary
        site_col = "CIE site name"
        year_col = 'Discharge/decay-corrected year'
        water_col = 'Volume [m3]'
        # Ignore the following columns when evaluating for copc's
        non_copcs = [
            'Inventory Module',
            'SIMV2 site name',
            site_col,
            'Source Type',
            year_col,
            'year',
        ]
        # Keep track of any sites that aren't part of VZEHSIT to pass to logger
        not_vzehsit = []
        for red_file in self.inv_args.reroute:
            df = csv_parser(red_file, skip_lines=[1])
            # Split by waste site and stream and store in dictionary
            df['year'] = df[year_col]
            for copc in df.columns:
                if copc in non_copcs:
                    continue
                else:
                    for site in get_unique_vals(df, site_col):
                        if site not in self.inv_lex:
                            not_vzehsit.append(site)
                        site_df = df.loc[df[site_col] == site, ['year', copc]].copy(deep=True)
                        if copc == water_col:
                            new_copc, new_col = normalize_col_names(copc, water_col=water_col)
                        elif copc in self.chm_cols:
                            new_copc, new_col = normalize_col_names(copc, chm_col=True)
                        else:
                            new_copc, new_col = normalize_col_names(copc)
                        site_df[new_col] = site_df[copc]
                        site_df = clean_df(site_df, [copc])
                        # Verify that there are records in the new dataframe, continue if empty dataframe
                        if len(site_df) == 0:
                            continue
                        if site in new_lex:
                            new_lex[site][new_copc] = site_df
                        else:
                            new_lex[site] = {
                                new_copc: site_df
                            }
        if len(not_vzehsit) > 0:
            logging.debug("##Rerouted sites NOT in VZEHSIT:")
            for site in not_vzehsit:
                logging.debug("{}".format(site))
        logging.info("##Rerouted Waste Sites:")
        logging.info("{:<40}{:<40}".format("Waste Site:", "[Listing of routed waste streams]"))
        for site in new_lex:
            copc_list = list(new_lex[site].keys())
            write_str = "{:<40}" + len(copc_list) * "{:10}"
            site += ':'
            logging.info(write_str.format(site, *copc_list))
        return new_lex

    def parse_sac(self):
        # This file is written in STOMP format, needs to be parsed differently from the other tabular files
        sac_path = self.inv_args.cleaninv
        sac_lex = stomp_format_parser(sac_path)
        # Only need to store sites with yearly data that have entries in VZEHSIT
        new_lex = {site: sac_lex[site] for site in self.inv_lex if site in sac_lex}
        unused_sac_sites = set(sac_lex.keys()) - set(new_lex.keys())
        logging.info("##Total number of sites included from SAC: {}".format(len(new_lex)))
        logging.info("##Sites with data in SAC not present in VZEHSIT ({}):".format(len(unused_sac_sites)))
        for site in sorted(unused_sac_sites):
            logging.info(site)
        return new_lex

    def parse_chm(self):
        # Take the CHEMINV work product file, parse as Pandas dataframe, then convert to
        chm_path = self.inv_args.cheminv
        site_col = 'CIE Site Name'
        year_col = 'Year'
        water_col = 'Volume Mean [m3]'
        copc_cols = [
            'U-Total [kg]',
            'Cr [kg]',
            'NO3 [kg]',
            'CN [kg]',
            water_col
        ]
        df = csv_parser(chm_path, skip_lines=[], codec='utf-8')
        not_vzehsit = []
        new_lex = {}
        site_counter = 0
        for copc in df.columns:
            if copc in copc_cols:
                for site in get_unique_vals(df, site_col):
                    if site.upper() not in self.inv_lex:
                        not_vzehsit.append(site.upper())
                    site_df = df.loc[df[site_col] == site, [year_col, copc]].copy(deep=True)
                    site_df.rename(columns={year_col: 'year'}, inplace=True)
                    # Normalize the column names
                    if copc == water_col:
                        new_copc, new_col = normalize_col_names(copc, water_col=water_col)
                    else:
                        new_copc, new_col = normalize_col_names(copc, chm_col=True)
                    site_df[new_col] = site_df[copc]
                    site_df = clean_df(site_df, [copc])
                    # Normalize the site name to only have upper case
                    site = site.upper()
                    if len(site_df) == 0:
                        continue
                    elif site_df[new_col].sum() == 0:
                        continue
                    if site in new_lex:
                        new_lex[site][new_copc] = site_df
                    else:
                        site_counter += 1
                        new_lex[site] = {
                            new_copc: site_df
                        }
        if len(not_vzehsit) > 0:
            logging.debug("##CHEMINV sites NOT in VZEHSIT:")
            for site in not_vzehsit:
                logging.debug("{}".format(site))
        else:
            logging.info("##Total number of CHEMINV Sites: {}".format(site_counter))
            logging.info("##All CHEMINV Sites are present in VZEHSIT")
        return new_lex

    def parse_sim(self):
        new_lex = {}
        # Columns that will be used repeatedly
        site_col = "CA site name"
        year_col = 'Discharge/decay-corrected year'
        water_col = 'Volume [m3]'
        waste_mod = 'Inventory Module'
        waste_type = 'Source Type'
        # Ignore the following columns when evaluating for copc's
        non_copcs = [
            waste_mod,
            'SIMV2 site name',
            'CA site name',
            waste_type,
            year_col
        ]
        # Keep track of any sites that aren't part of VZEHSIT to pass to logger
        not_vzehsit = []
        site_counter = 0
        path = self.inv_args.vzinv
        df = csv_parser(path, skip_lines=3, codec='iso-8859-1')
        # Convert all waste stream types (solid vs liquid) to liquid if inventory module is "Entrained Solids"
        df.loc[df[waste_mod] == 'SIM-v2 entrained solids', waste_type] = 'Liquid'
        # Exclude inventory records that are waste_type = 'solid' if in solid waste release
        # Only necessary if solid waste release sites are included in the analysis/check
        if hasattr(self, "swr_lex"):
            df = df.loc[~((df[site_col].isin(self.swr_lex)) & (df[waste_type] == 'Solids')), :]
        if self.inv_args.exclude_solids:
            df = df.loc[df[waste_type] == 'Liquid', :]
        # Split by waste site and stream and store in dictionary
        for copc in df.columns:
            if copc in non_copcs:
                continue
            else:
                for site in get_unique_vals(df, site_col):
                    if site.upper() not in self.inv_lex:
                        not_vzehsit.append(site.upper())
                        continue
                    # Filter by waste site, waste stream, exclude waste_type = solid if site in solid waste release list
                    site_df = df.loc[df[site_col] == site, [year_col, copc]].copy(deep=True)
                    site_df['year'] = site_df[year_col]
                    if copc == water_col:
                        new_copc, new_col = normalize_col_names(copc, water_col=water_col)
                    else:
                        new_copc, new_col = normalize_col_names(copc)
                    site_df[new_col] = site_df[copc]
                    site_df = clean_df(site_df, [year_col, copc])
                    # Normalize the site name to only have upper case
                    site = site.upper()
                    # Verify that there are records in the new dataframe, continue if empty dataframe
                    if len(site_df) == 0:
                        continue
                    if site in new_lex:
                        new_lex[site][new_copc] = site_df
                    else:
                        new_lex[site] = {
                            new_copc: site_df
                        }
                        site_counter += 1
        logging.info("##Total number of SIMV2 Waste Sites: {}".format(site_counter))
        logging.info("##Sites not in VZEHSIT ({}):".format(len(set(not_vzehsit))))
        for site in sorted(set(not_vzehsit)):
            logging.info(site)
        return new_lex

    def build_inv(self):
        # This method will combine all of primary source information into the final inventory dictionary for comparison
        # against the ca-ipp output file (comparison done in another function, not included in this class)
        # The order is essential for this given the functional requirements listed at the header of this file. The order
        # for adding the parsed information is as follows:
        #   1.  Rerouted Inventory  (red_lex)
        #   2.  Solid Waste Release (swr_lex)
        #   3.  SIMV2 Inventory     (sim_inv)
        #   4.  Chemical Inventory  (chm_lex)
        #   4.  SAC Water Inventory (sac_lex)
        final_lex = self.inv_lex
        if hasattr(self, "red_lex"):
            logging.info('##Merging Rerouted Sites into final dictionary')
            final_lex, used_lex = combine_lex(final_lex, self.red_lex)
            self.clean_lex(used_lex, 'red_lex')
        if hasattr(self, "swr_lex"):
            logging.info('##Merging SWR into final dictionary')
            final_lex, used_lex = combine_lex(final_lex, self.swr_lex)
            self.clean_lex(used_lex, 'swr_lex')
        if hasattr(self, "sim_lex"):
            logging.info('##Merging SIMV2 into final dictionary')
            # If SWR is included in analysis, make sure SIMV2 dictionary doesn't override the values
            if hasattr(self, "swr_lex"):
                final_lex, used_lex = combine_lex(final_lex, self.sim_lex)
                self.clean_lex(used_lex, 'sim_lex')
            # If no SWR, merge SIMV2 like normal
            else:
                final_lex, used_lex = combine_lex(final_lex, self.sim_lex)
                self.clean_lex(used_lex, 'sim_lex')
        if hasattr(self, "chm_lex"):
            logging.info('##Merging Chemical Inventory into final dictionary')
            final_lex, used_lex = combine_lex(final_lex, self.chm_lex)
            self.clean_lex(used_lex, 'chm_lex')
        if hasattr(self, "sac_lex"):
            logging.info('##Merging SAC into final dictionary')
            final_lex, used_lex = combine_lex(final_lex, self.sac_lex)
            self.clean_lex(used_lex, 'sac_lex')
        logging.info('##All primary source data have been merged into a hashed dictionary, proceeding to check.')
        return final_lex

    def clean_inv(self):
        # Remove any dictionary keys that don't have waste streams/water sources
        final_lex = {}
        copc_list = []
        for site in self.inv_lex.keys():
            for copc in self.inv_lex[site].keys():
                if copc in self.inv_args.copcs:
                    copc_list.append(copc)
                    if site in final_lex:
                        final_lex[site][copc] = self.inv_lex[site][copc]
                    else:
                        final_lex[site] = {
                            copc: self.inv_lex[site][copc]
                        }
        # final_lex = {site: self.inv_lex[site] for site in self.inv_lex if len(self.inv_lex[site].keys()) > 0}
        # Log the final waste streams to be included in the analysis
        copc_list = sorted(list(set(copc_list)))
        logging.info("##Waste streams to be considered for this check:")
        write_str = len(copc_list) * "{:<10}"
        logging.info(write_str.format(*copc_list))
        # Log the waste sites that have no inventory for evaluation after excluding the extraneous information
        unused_sites = set(self.inv_lex.keys()) - set(final_lex.keys())
        if len(unused_sites) > 0:
            logging.info("##The following sites had no inventory or water volume (after excluding extraneous sources):")
            for site in sorted(unused_sites):
                logging.info(site)
        else:
            logging.info("##All sites in VZEHSIT have at least one waste stream/water volume time series.")
        return final_lex

    def clean_lex(self, keep_lex, attr_str=''):
        """
        This method removes excess sites that did not make it into the final inventory object from the primary source
        dictionaries. As an example: if site 123-x-4 is present in the red_lex (rerouted sites source) and in sac_lex
        (for the SAC source), we'd want to keep 123-x-4 in red_lex, and remove it from sac_lex.
        :param keep_lex:        Dictionary of sites/streams to keep: keep_lex[site]
        :param attr_str:        The string of the attribute to set/modify
        :return:
        """
        try:
            assert hasattr(self, attr_str)
        except AssertionError:
            logging.exception("The method was not provided a valid attribute string {}".format(attr_str))
            raise AssertionError
        new_lex = {}
        for site in keep_lex.keys():
            new_lex[site] = {}
            for copc in keep_lex[site]:
                new_lex[site][copc] = getattr(self, attr_str)[site][copc]
        setattr(self, attr_str, new_lex)
        return


def parse_ipp_output(path, copc_list, vzehsit):
    ipp_out_lex = {}
    header_lines = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12]
    # Column names of cie-ipp.pl output to be used throughout parsing
    year_col = 'Discharge/decay-corrected year'
    water_col = 'Volume [m3]'
    site_col = 'CA site name'
    non_copcs = [
        'Inventory Module',
        'SIMV2 site name',
        site_col,
        'Source Type',
        'year'
    ]
    # Parse only those columns of interest as specified by the user and necessary ID columns
    usecols = non_copcs[:-1] + [year_col] + copc_list + [water_col]
    df = csv_parser(path, skip_lines=header_lines, use_cols=usecols)
    # Verify whether all copc columns were included from cie-ipp.pl output, also identify chems vs rads
    ipp_out_text = open(path, 'r')
    i = 0
    while i in header_lines:        # Not concerned about skipping the last of these lines, as we want the units line
        next(ipp_out_text)
        i += 1
    col_row = next(ipp_out_text)[::-1].replace(',', '', 1)[::-1].replace('\n', '').replace('\r', '').split(',')
    unit_row = next(ipp_out_text)[::-1].replace(',', '', 1)[::-1].replace('\n', '').replace('\r', '').split(',')
    # Compare col_row against the columns
    excluded_copcs = list(set(copc_list).difference(set(col_row)))
    if len(excluded_copcs) > 0:
        write_str = len(copc_list) * "{:10}"
        logging.warning("The following COPCs were not included in the analysis, though they are in the IPP output:")
        logging.warning(write_str.format(*excluded_copcs))
    # Identify chems vs rads
    rad_indices = [index for index, value in enumerate(unit_row) if value.lower() == 'ci']
    chem_indices = [index for index, value in enumerate(unit_row) if value.lower() == 'kg']
    rad_list = [col_row[i] for i in rad_indices]
    chem_list = [col_row[i] for i in chem_indices]
    # Make sure to only pull those rads/chemicals specified by the user
    rad_list = list(set(rad_list).intersection(set(copc_list)))
    chem_list = list(set(chem_list).intersection(set(copc_list)))
    # Drop the old year column and replace with "year"
    df.rename(columns={year_col: 'year'}, inplace=True)
    col_names = df.columns
    # Track all sites that are not in VZEHSIT
    sites_not_vzehsit = []
    # Break out each of the waste sites and waste streams into a dictionary of the same format as was done with InvObj
    for copc in col_names:
        if copc in non_copcs:
            continue
        else:
            if copc == water_col:
                new_copc, new_col = normalize_col_names(copc, water_col=water_col)
            elif copc in chem_list:
                new_copc, new_col = normalize_col_names(copc, chm_col=True)
            else:
                new_copc, new_col = normalize_col_names(copc)
            df[new_col] = df[copc]
            for site in get_unique_vals(df, site_col):
                if site.upper() not in vzehsit:
                    # If the site is not in VZEHSIT, then collect it and continue to next site (don't parse non-VZEHSIT)
                    sites_not_vzehsit.append(site.upper())
                    continue
                site_df = df.loc[df[site_col] == site, ['year', new_col]].copy(deep=True)
                site_df = clean_df(site_df, [])
                # Verify that the dataframe has data (continue if empty dataframe)
                if len(site_df) == 0:
                    continue
                # Make sure that the site-naming convention stays upper-case to be consistent with check
                site = site.upper()
                if site not in ipp_out_lex:
                    ipp_out_lex[site] = {
                        new_copc: site_df
                    }
                else:
                    ipp_out_lex[site][new_copc] = site_df
    if len(sites_not_vzehsit) > 0:
        logging.critical(
            "##QA-FAIL(Waste Site Parse Check): The cie-ipp.pl output has {} site(s) that are not in VZEHSIT:".format(len(sites_not_vzehsit))
        )
        for site in sites_not_vzehsit:
            logging.critical(site)
    else:
        logging.info("#\n#\n##QA-PASS (Waste Site Parse Check): The cie-ipp.pl output only has sites listed in the VZEHSIT.\n#\n#")
    return ipp_out_lex


def compare_ipp_output(check_obj, ipp_out):
    """
    :param check_obj:       This is the InvObj object, or in other words, the expected result set
    :param lex2:            This is the dictionary representation of the cie-ipp.pl output to compare
    :return:
    """
    lex1 = check_obj.inv_lex
    check_list = []
    if hasattr(check_obj, "sac_lex"):
        site_list = check_obj.sac_lex.keys()
        check_lex = {site: check_obj.inv_lex[site] for site in site_list}
        check_list.append([check_lex, "SAC Check"])
    if hasattr(check_obj, "red_lex"):
        site_list = check_obj.red_lex.keys()
        check_lex = {site: check_obj.inv_lex[site] for site in site_list}
        check_list.append([check_lex, "Rerouted Sites Check"])
    if hasattr(check_obj, "swr_lex"):
        site_list = check_obj.swr_lex.keys()
        check_lex = {site: check_obj.inv_lex[site] for site in site_list}
        check_list.append([check_lex, "Solid Waste Release Check"])
    if hasattr(check_obj, "chm_lex"):
        site_list = check_obj.chm_lex.keys()
        check_lex = {site: check_obj.inv_lex[site] for site in site_list}
        check_list.append([check_lex, "Chemical Inventory Check"])
    if hasattr(check_obj, "sim_lex"):
        site_list = check_obj.sim_lex.keys()
        check_lex = {site: check_obj.inv_lex[site] for site in site_list}
        check_list.append([check_lex, "SIMV2 Check"])
    # Comprehensive check
    check_list.append([check_obj.inv_lex, "Comprehensive Check"])
    # Verify that the same waste sites have been used
    unused_sites = set(lex1.keys()) - set(ipp_out.keys())
    # Known exceptions to site list [["missing site", "known exception"]]
    site_exceptions = {
        'T31': '200-W-254',
        'T34': '200-W-254',
    }
    missed_sites = [site for site in unused_sites if
                        site not in site_exceptions.keys()]
    site_exceptions = {site_exceptions[site] for site in unused_sites if
                        site in site_exceptions.keys() and site_exceptions[site] in ipp_out.keys()
                       }
    if len(site_exceptions) > 0:
        logging.info('##The following sites are known exceptions:')
        write_str = '{:<20}{:<20}'
        logging.info(write_str.format('Missing Site', 'Mapped Site'))
        for site in site_exceptions:
            logging.info(write_str.format(site, site_exceptions[site]))
    if len(missed_sites) > 0:
        logging.warning("##Output from cie-ipp.pl does not contain the following sites:")
        for site in sorted(unused_sites):
            logging.warning(site)
    for check in check_list:
        lex, src = check
        result = compare_lex(lex, ipp_out)
        log_results(result, src)
    # Reverse the comprehensive check to make sure nothing was missed by the check (i.e. more info in cie-ipp.pl output)
    result = compare_lex(ipp_out, check_obj.inv_lex)
    log_results(result, "Comprehensive Check in Reverse")
    return


def log_results(compare_result, fr):
    """
    Takes a list of strings and logs them to the logfile
    :param compare_result:      List of strings
    :param fr:                  The functional requirement being tested
    :return:
    """
    if len(compare_result) > 0:
        logging.critical("#\n#\n##QA-FAIL ({}): the following differences were found:".format(fr))
        for diff in sorted(compare_result):
            logging.critical("{:<20}{:<20}".format(diff, compare_result[diff]))
        logging.critical("#\n#\n")
    else:
        logging.info("#\n#\n##QA-PASS ({})\n#\n#".format(fr))
    return


def compare_lex(lex1, lex2):
    """
    :param lex1:    Primary dictionary to check with
    :param lex2:    cie-ipp.pl output to verify
    :return:
    """
    mismatched_sites = {}
    for site in lex1:
        # Record missing sites
        if site not in lex2:
            mismatched_sites[site] = "Waste Site Missing"
        else:
            for stream in lex1[site]:
                # Record missing waste streams/water volumes
                if stream not in lex2[site]:
                    mismatched_sites[site] = "Waste Stream Missing: {}".format(stream)
                else:
                    # Test that each waste stream is equal to one another
                    df1 = lex1[site][stream]
                    df2 = lex2[site][stream]
                    result = compare_dfs(df1, df2)
                    if result:
                        for diff in result:
                            try:
                                mismatched_sites[site] = "Waste Stream Difference (Column  Difference): " \
                                                     "{:<20}{:<20}".format(*diff)
                            except IndexError:
                                mismatched_sites[site] = diff
    return mismatched_sites


def compare_dfs(df1, df2):
    diff_cols = list(set(df1.columns).difference(set(df2.columns)))
    if len(diff_cols) > 0:
        return [diff_cols, "Column names that don't match"]
    else:
        for col in df1.columns:
            series1 = df1[col]
            series2 = df2[col]
            series_check = compare_series(series1, series2)
            if not series_check:
                diff_cols.append([col, "Series data do not match"])
    if len(diff_cols) > 0:
        return diff_cols
    else:
        return False


def compare_series(ser1, ser2, sig_fig=6):
    # Make sure that precision is matched by rounding to 6 significant digits (the expected output format of cie-ipp.pl)
    # To avoid floating point error issues, first round to 8 sig figs, then to 6 sig figs. Example of this being a
    # problem is 426.03049999996 rounded to 6th sig fig gives 426.03 rather than 426.031
    sigfig_list = [sig_fig + 4, sig_fig]
    for digits in sigfig_list:
        ser1 = ser1.apply(lambda x: round_sigfigs(x, digits))
        ser2 = ser2.apply(lambda x: round_sigfigs(x, digits))
    try:
        result = (ser1 == ser2).unique().tolist() == [True]
    except ValueError:
        return False
    if result:
        return True
    else:
        return False


# ----------------------------------------------------------------------------------------------------------------------
# Main Program
if __name__ == '__main__':
    configure_logger(os.path.join(args.output, "ipp_check.log"), args.verbosity)
    if args.rcaswr_idx is not None and args.rcaswr_dir is not None:
        is_RCASWR_idx(args.rcaswr_idx, args.rcaswr_dir)
    else:
        logging.debug("No Solid Waste Releases to be considered in this check.")
    inv_check = InvObj(args)
    # Pass the path to the ipp_output file, whether chemicals should be included, and the list of VZEHSIT sites
    vz_sites = list(inv_check.parse_vzehsit())
    ipp_out = parse_ipp_output(args.ipp_output, args.copcs, vz_sites)
    compare_ipp_output(inv_check, ipp_out)
