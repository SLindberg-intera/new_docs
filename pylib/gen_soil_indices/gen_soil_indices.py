'''
Author:         Jacob B Fullerton
Date:           October 5, 2018
Company:        Intera Inc.
Project:        This script was funded in support of the "Composite Analysis (CA), Vadose Zone Facet"
Usage:          Intended for internal use at Intera Inc. to extract soil indices and write a CSV of soils for P2R grid
'''
import pandas as pd
import os
import argparse
import geopandas as gp

# ----------------------------------------------------------------------------------------------------------------------
# Utility functions

def dir_path(mystr):
    if os.path.isdir(mystr):
        mystr = os.path.abspath(mystr)
        return mystr
    else:
        raise IsADirectoryError("Path provided is not a directory: {}".format(mystr))


def is_file(mystr):
    if os.path.isfile(mystr):
        mystr = os.path.abspath(mystr)
        return mystr
    else:
        try:
            file = open(mystr, 'a+')
            del file
            os.remove(mystr)
            return mystr
        except:
            raise FileNotFoundError("Cannot find or create the file at the given location: {}".format(mystr))


def is_shp(mystr):
    if is_file(mystr):
        try:
            try:
                gdf = gp.read_file(mystr)
                return gdf
            except:
                gdf = gp.read_file(mystr, encoding="utf-8")
                return gdf
        except:
            raise TypeError("The file provided is not a shapefile or may have an unrecognized encoding")

# ----------------------------------------------------------------------------------------------------------------------
# User Input (Parser)


parser = argparse.ArgumentParser()
parser.add_argument('-o', '--output_folder',
                    dest='outfolder',
                    type=dir_path,
                    required=True,
                    help='This is the output folder where the script output file will be saved.'
                    )
parser.add_argument('-f', '--output_filename',
                    dest='output_filename',
                    type=str,
                    default='mfgrid_soil_indices.csv',
                    help='This is the output file name. Default is: [mfgrid_soil_indices.csv]'
                    )
parser.add_argument('-s', '--soils_w_MFgrid',
                    dest='soils_w_MFgrid',
                    type=is_shp,
                    required=True,
                    help='This file is a spatial representation of the intersection between soils and\n'
                         'MODFLOW grid to use.'
                    )
parser.add_argument('--soils_column',
                    dest='soils_column',
                    type=str,
                    default='SOIL_NAME',
                    help='The column name for the soil names stored as an attribute in the geospatial dataset provided.'
                    )
parser.add_argument('--verbose_output',
                    dest='verbose_output',
                    type=bool,
                    default=False,
                    help='Toggle this to True if you want all of the output data columns (before filtering to unique\n'
                         'cell assignments).'
                    )
args = parser.parse_args()


# ----------------------------------------------------------------------------------------------------------------------
# Primary classes and functions


class SoilGroups:
    raw_soil_indices = {
        'burbank loamy sand': 1,
        'dunesand': 2,
        'ephrata sandy loam': 3,
        'esquatzel silt loam': 4,
        'hezel sand': 5,
        'kiona silt loam': 6,
        'koehler sand': 7,
        'pasco silt loam': 8,
        'quincy sand': 9,
        'riverwash': 10,
        'scooteney stoney silt loam': 11,
        'warden silt loam': 12
    }
    grouped_soil_indices = {
        1: {
            'raw_indices': [9, 10],
            'group_name': 'Rupert Sand'
        },
        2: {
            'raw_indices': [5, 7],
            'group_name': 'Hezel/Koehler Sand'
        },
        3: {
            'raw_indices': [2],
            'group_name': 'Dunesand'
        },
        4: {
            'raw_indices': [1],
            'group_name': 'Burbank Loamy Sand'
        },
        5: {
            'raw_indices': [3],
            'group_name': 'Ephrata Sandy Loam'
        },
        6: {
            'raw_indices': [4, 6, 8, 11, 12],
            'group_name': 'Esquatzel/Pasco/Kiona/Warden Silt Loam'
        }
    }


def soil_index(soil):
    """
    This expects the full soil name and returns the corresponding soil index value.
    :param soil:    A string representation of the soil name
    :return:        An integer of the index associated with the soil name
    """
    try:
        soil = soil.lower()
    except:
        soil = None
    if soil in SoilGroups.raw_soil_indices:
        raw_index = SoilGroups.raw_soil_indices[soil]
    else:
        return 0
    # Obtain final/grouped index
    for key in SoilGroups.grouped_soil_indices:
        if raw_index in SoilGroups.grouped_soil_indices[key]['raw_indices']:
            return key

def group_name(group_index):
    """
    Maps the group index with the appropriate group name
    :param group_index:     An integer representing the soil group index
    :return:                A string representing the soil group name
    """
    for key in SoilGroups.grouped_soil_indices:
        if key == group_index:
            return SoilGroups.grouped_soil_indices[key]['group_name']
    return 'No Group Assigned'


def gen_indices(gdf, soil_col):
    """
    Accepts a geodataframe and returns a geodataframe with new columns representing the soil indices and name,
    respectively.
    :param gdf:         GeoPandas geodataframe with a column
    :param soil_col:    The column where the soil names are stored in the geodataframe
    :return:            A GeoPandas geodataframe with a new column called "SOIL_INDEX" and "SOIL_CATEGORY'
    """
    gdf['SOIL_INDEX'] = gdf[soil_col].apply(soil_index)
    gdf['SOIL_CATEGORY'] = gdf['SOIL_INDEX'].apply(group_name)
    return gdf


def select_soils(gdf, id_col, sort_col):
    """
    Will pick the soil that takes up the most of a given MODFLOW cell, reducing the list down so each MODFLOW cell has
    only one entry in the gdf
    :param gdf:         GeoPandas geodataframe for all MODFLOW cell intersections with the soils dataset
    :param id_col:      MODFLOW cell ID column (to make unique by removing/filtering excess rows based on sort_col)
    :param sort_col:    Area column (numeric values only in the column) to use for filtering
    :return:            GeoPandas geodataframe (after filtering/reduction)
    """
    filtered_gdf = gdf.sort_values(sort_col, ascending=True).copy(deep=True)
    filtered_gdf = filtered_gdf.drop_duplicates(id_col, keep='last')
    return filtered_gdf


# ----------------------------------------------------------------------------------------------------------------------
# Main Program
if __name__ == '__main__':
    soil_grid_gdf = gen_indices(args.soils_w_MFgrid, args.soils_column)
    # Rename the following columns: 'row' -> 'ROW(I)', 'column' -> 'COL(J)' and create an ID column combining the two
    soil_grid_gdf.rename({'row': 'ROW(I)', 'column': 'COL(J)'}, axis='columns', inplace=True)
    soil_grid_gdf['ID'] = soil_grid_gdf['ROW(I)'].astype(str) + '_' + soil_grid_gdf['COL(J)'].astype(str)
    # Update the 'area' column by calculating the actual area of each polygon in the geodataframe
    soil_grid_gdf['area'] = soil_grid_gdf['geometry'].area
    # If the user wants the whole file, write out the file, including 'verbose' at the end of the file name
    if args.verbose_output is not False:
        file_name = "{0}_{2}.{1}".format(*args.output_filename.split("."), 'verbose')
        output_file_path = os.path.join(args.outfolder, file_name)
        soil_grid_gdf.to_csv(output_file_path, index=False)
    # Select the soil type for each cell using the maximum overlap (e.g. 40% dunesand, 60% rupert sand -> cell = rupert)
    soil_grid_gdf = select_soils(soil_grid_gdf, id_col='ID', sort_col='area')
    # Write the final product to a file, only including the columns of interest
    output_file_path = os.path.join(args.outfolder, args.output_filename)
    soil_grid_gdf.sort_values(by=['ROW(I)', 'COL(J)'], ascending=True, inplace=True)
    soil_grid_gdf[['ID', 'ROW(I)', 'COL(J)', 'SOIL_CATEGORY', 'SOIL_INDEX']].to_csv(output_file_path, index=False)
