"""
Author:         Jacob B Fullerton
Date:           November 6, 2020
Company:        INTERA Inc.
Usage:          This code is meant to read a STOMP grid card, then generate an XYZ file of cell centroids

Pseudo Code:    The code in general works in the following manner:
                1.  Read STOMP input file
                2.  Build list of centroid coordinates
                3.  Export final output to file
"""

import argparse
from pathlib import Path
import pandas as pd


# ----------------------------------------------------------------------------------------------------------------------
# Utility functions


def file_path(mystr):
    if Path(mystr).is_file():
        return mystr
    else:
        raise FileNotFoundError("File path provided does not exist: {}".format(mystr))


def dir_path(mystr):
    if Path(mystr).is_dir():
        return mystr
    else:
        raise IsADirectoryError("Path provided is not a directory: {}".format(mystr))


def is_int(mystr):
    try:
        int(mystr)
        return True
    except ValueError:
        return False


def clean_and_split(mystr, split_char=','):
    mystr = mystr.replace('\r', '').replace('\n', '')
    if split_char != '':
        mystr = mystr.split(split_char)
    return mystr


# ----------------------------------------------------------------------------------------------------------------------
# User Input (Parser)


parser = argparse.ArgumentParser()
parser.add_argument('-i', '--STOMP_input',
                    dest='stomp_input',
                    type=file_path,
                    required=True,
                    help='The cards of interest include the "~Rock/Soil Zonation Card" and the \n'
                         '"~Mechanical Properties Card". It is expected that the "~Rock/Soil Zonation Card" be\n'
                         'written such that the zonation card is saved externally from the input file and is \n'
                         '"Zonation File Formatted" with indices matching the model input file ("0" being inactive).\n'
                         'The zonation card and STOMP input file should be in the same relative folder structure as\n'
                         'when the STOMP model is executed (relative to each other) so this script can find and parse\n'
                         'the zonation card.'
                    )
parser.add_argument('-c', '--Centroids_w_Concs',
                    dest='centroids_w_concs',
                    type=file_path,
                    required=True,
                    help='Provide the path to the STOMP centroid xyz file with concentration column(s). Expects a\n'
                         'minimum of 4 columns: I,J,K,[analyte-soil-concentration].\n'
                         'Make sure to specify the [analyte-soil-concentration] column with the "COPC_columns" flag.'
                    )
parser.add_argument('-o', '--output_directory',
                    dest='output_directory',
                    type=dir_path,
                    help='Provide the path to the output directory for saving the output file.'
                    )
parser.add_argument('-f', '--output_file_name',
                    dest='output_file_name',
                    type=str,
                    default='STOMP_centroids.csv',
                    help='The name of the output file, default is [STOMP_centroids.csv].'
                    )
parser.add_argument('--COPC_columns',
                    dest='COPC_columns',
                    nargs='+',
                    type=str.upper,
                    required=True,
                    help='This script only processes one COPC. However, it can accept multiple columns of the same\n'
                         'COPC, but what this will do is take the maximum of the columns given for each point.'
                    )
parser.add_argument('--threshold',
                    dest='threshold',
                    type=float,
                    default=5000,
                    help='This value corresponds with the smallest-acceptable value for being included in the initial\n'
                         'conditions card. The default is [5000], which means values "<" less-than [5000] will not\n'
                         'be included.'
                    )
parser.add_argument('--conversion_factor',
                    dest='factor',
                    type=float,
                    default=1e-6,
                    help='This is the conversion factor for getting the output into the desired units. The default is\n'
                         '[1e-6]. This conversion works with particle density in [g/cm^3] and soil conc in [µg/kg].'
                    )
parser.add_argument('--scale_factor',
                    dest='display_units',
                    type=float,
                    default=21780741,
                    help='Using this option will produce 2 files: 1 that represents the sampled mass/activity and\n'
                         'another that scales the sampled mass/activity to match a desired value. If the sampled \n'
                         'total mass/activity were equal to 1, but the desired end total should be 9, then typing\n'
                         'a "9" in this option would multiply each cell by the appropriate scaling factor such that \n'
                         'resultant total of the scaled output is equal to the desired end value. The default is\n'
                         '[21780741].'
                    )
parser.add_argument('--solute_name',
                    dest='solute_name',
                    type=str,
                    default='NO3',
                    help='This is the name of the solute that will be used when writing the initial conditions card.'
                    )
parser.add_argument('--out_format',
                    dest='out_format',
                    type=str,
                    default='{:.5e}',
                    help='This is how you can modify the output format of the initial conditions values. Default is:\n'
                         '{:.5e}'
                    )
parser.add_argument('--display_units',
                    dest='display_units',
                    type=str,
                    default='kg/m^3',
                    help='This is to define the units of the final output (relevant to the Tecplot file only).\n'
                         'The default is [kg/m^3].'
                    )
args = parser.parse_args()


# ----------------------------------------------------------------------------------------------------------------------
# Primary functions


def parse_csv(path, header='infer', usecols=None):
    """
    Wrapper for the "read_csv()" method of Pandas
    :param path:    The file path to read (CSV format expected)
    :param header:  The header row to use (set to None if no header provided)
    :param usecols: Columns to use when parsing
    :return:
    """
    if usecols is None:
        df = pd.read_csv(filepath_or_buffer=path, header=header, engine='c')
    else:
        # Make all of the "usecols" uppercase as applicable
        for val in usecols:
            if isinstance(val, str):
                usecols[usecols.index(val)] = val.upper()
        df = pd.read_csv(
            filepath_or_buffer=path,
            header=header,
            engine='c',
            usecols=lambda x: x.upper() in usecols
        )
    # Make all of the column headers uppercase
    df.columns = map(str.upper, df.columns)
    return df


class STOMP_obj:
    def __init__(self, input_file):
        self.input_file = input_file
        self.soil_lex, self.zonation_path, self.cell_dims = parse_input(input_file)
        self.volumes = self.get_volumes()
        self.I_len = len(self.cell_dims['x-dir']) - 1
        self.J_len = len(self.cell_dims['y-dir']) - 1
        self.K_len = len(self.cell_dims['z-dir']) - 1

    def get_volumes(self):
        """
        Takes the self.cell_dims (cell dimensions, edge-to-edge) and calculates the cell volumes
        :return:
        """
        x_dims = []
        y_dims = []
        z_dims = []
        cell_vols = {'I': [], 'J': [], 'K': [], 'VOLUME': []}
        for val1, val2 in zip(self.cell_dims['x-dir'], self.cell_dims['x-dir'][:-1]):
            x_dims.append(val2 - val1)
        for val1, val2 in zip(self.cell_dims['y-dir'], self.cell_dims['y-dir'][:-1]):
            y_dims.append(val2 - val1)
        for val1, val2 in zip(self.cell_dims['z-dir'], self.cell_dims['z-dir'][:-1]):
            z_dims.append(val2 - val1)
        for i in range(len(x_dims)):
            for j in range(len(y_dims)):
                for k in range(len(z_dims)):
                    cell_vols['I'].append(i + 1)
                    cell_vols['J'].append(i + 1)
                    cell_vols['K'].append(i + 1)
                    cell_vols['VOLUME'].append(x_dims[i] * y_dims[j] * z_dims[k])
        return cell_vols


def parse_input(path):
    """
    This will read the STOMP input file for the "~Rock/Soil Zonation Card" and the "~Mechanical Properties Card". It is
    expected that the "~Rock/Soil Zonation Card" be written such that the zonation card is saved externally from the
    input file and is "Zonation File Formatted" with indices matching the model input file ("0" being inactive).
    :param path:
    :return:
    """
    cards = ['~ROCK/SOIL ZONATION CARD', '~MECHANICAL PROPERTIES CARD', '~GRID CARD']
    soils = {"Inactive": {"index": 0, "bulk_density": 0}}
    counter = 1
    i = 0
    with open(path, 'r') as stomp_file:
        while i < 2:
            line = clean_and_split(next(stomp_file), split_char='')
            if line.upper() == cards[0]:
                line = next(stomp_file)
                while 'ZONATION FILE FORMATTED' not in line.upper():
                    line = next(stomp_file)
                line = clean_and_split(line)
                try:
                    zone_file = file_path(line[1])
                except FileNotFoundError:
                    try:
                        zone_file = file_path(Path(Path(path).parent, line[1]))
                    except FileNotFoundError:
                        raise FileNotFoundError(
                            "The zonation file indicated in the STOMP input file cannot be located.")
                line = clean_and_split(next(stomp_file))
                while ('#' not in ''.join(line)) and ('~' not in ''.join(line)) and (line != ['']):
                    soil = line[0]
                    if soil not in soils:
                        soils[soil] = {'index': counter}
                    else:
                        soils[soil]['index'] = counter
                    counter += 1
                    line = clean_and_split(next(stomp_file))
                i += 1
            elif line.upper() == cards[1]:
                line = next(stomp_file)
                while '#' in line:
                    line = clean_and_split(next(stomp_file))
                while ('#' not in ''.join(line)) and ('~' not in ''.join(line)) and (line != ['']):
                    soil, part_density, porosity = line[0], float(line[1]), float(line[3])
                    bulk_density = (1 - porosity) * part_density
                    if soil not in soils:
                        soils[soils] = {'bulk_density': bulk_density}
                    else:
                        soils[soil]['bulk_density'] = bulk_density
                    line = clean_and_split(next(stomp_file))
                i += 1
            elif line.upper() == cards[2]:
                while True:
                    line = line.replace('\r', '').replace('\n', '').split(',')
                    if is_int(line[0]):
                        # Want to skip the line that tells STOMP how many cells to expect ("greedy parsing")
                        line = next(stomp_file)
                        break
                    else:
                        line = next(stomp_file)
                        continue
                # This should now be the first line of the STOMP grid file dictating the "i-dir" centroid locations
                i_list = parse_grid_line(line)
                line = next(stomp_file)
                j_list = parse_grid_line(line)
                line = next(stomp_file)
                k_list = parse_grid_line(line)
    # Package the spacings into a dictionary
    spacings = {
        'x-dir': i_list,
        'y-dir': j_list,
        'z-dir': k_list
    }
    # Turn the soils dictionary inside-out
    new_soils = {}
    for soil in soils:
        idx = soils[soil]['index']
        bulk_density = soils[soil]['bulk_density']
        new_soils[idx] = bulk_density
    return new_soils, zone_file, spacings


def parse_grid_line(line_str):
    """
    Expects a STOMP grid card line dictating a cartesian coordinate system. An example of such a line might be:
        572800,m,39@10,m,56@5,m,43@10,m,
    The expected return value will be a list of values, generated by expanding the STOMP grid card line.
    :param line_str:
    :return:
    """
    line = line_str.replace('\r', '').replace('\n', '').split(',')
    val = float(line[0])
    edges = [val]
    spacings = [tuple(map(float, val.split('@'))) for val in line if '@' in val]
    for disc in spacings:
        for i in range(int(disc[0])):
            val = val + disc[1]
            edges.append(val)
    return edges


def parse_zone_file(path, i_max, j_max, k_max):
    """
    This expects a path to a "Zonation File Formatted" file (per STOMP input). Should only contain indices for the soil
    types indexed in order from left-to-right, top-to-bottom by IJK indexing (1,1,1   2,1,1  ...  1,2,1   2,2,1  ...).
    :param path:    Valid file path
    :param i_max:   The maximum index for the I-dir
    :param j_max:   The maximum index for the J-dir
    :param k_max:   The maximum index for the K-dir
    :return:
    """
    zone_file = open(path, 'r')
    zone_text = zone_file.read()
    zone_file.close()
    zone_indices = {'I': [], 'J': [], 'K': [], 'MAT_IDX': []}
    # Process entire file to be a single chain of indices
    zones_list = zone_text.replace('\r', '\n').replace('\n\n', '\n').replace('\n', '').split()
    if '' in zones_list:
        # Remove empty indices and set datatype to integers for all values
        zones_list = [int(val) for val in zones_list if val != '']
    else:
        zones_list = list(map(int, zones_list))
    # Build dictionary with corresponding indices
    i = 1
    j = 1
    k = 1
    for val in zones_list:
        zone_indices['I'].append(i)
        zone_indices['J'].append(j)
        zone_indices['K'].append(k)
        zone_indices['MAT_IDX'].append(val)
        i += 1
        if i > i_max:
            i = 1
            j += 1
        if j > j_max:
            j = 1
            k += 1
        if k > k_max + 1:
            raise ValueError("The file provided has more zonation indices than there are cells in the model. Verify\n"
                             "that the right model files are being referenced in the STOMP input file.")
    return zone_indices


def soil_to_vol_conc(df, mat_lex, unit_factor):
    """
    Convert from soil to volumetric concentration values using the bulk density and any conversion factor needed to
    maintain the proper units.
    :param df:          Pandas dataframe with the following columns: I, J, K, MAT_IDX
    :param mat_lex:     Dictionary for matching material indices with the proper bulk density value
    :param unit_factor: The conversion factor to apply when adjusting for unit conversions
    :return:
    """
    # Convert from soil to volumetric concentration values: 1) Assign bulk density 2) Multiply bulk density by soil conc
    # 3) Filter out zeros and keep only relevant columns
    df['BULK_DENSITY'] = df['MAT_IDX'].map(mat_lex)
    df['FACTOR'] = unit_factor
    df['INIT_COND'] = df['SOIL_CONC'] * df['BULK_DENSITY'] * df['FACTOR']
    df = df.loc[df['INIT_COND'] > 0, ['I', 'J', 'K', 'INIT_COND']].copy(deep=True)
    df.reset_index(drop=True, inplace=True)
    return df


def write_init_conds(df, number_format, out_file):
    """
    Takes the information pertinent for the STOMP initial conditions card and writes it to a file (STOMP-formatted).
    :param df:              Pandas dataframe with the following columns: I, J, K, INIT_COND
    :param number_format:   The format to use when preparing the numbers
    :param out_file:        The file path to write to
    :return:
    """
    # Prepare the card text, STOMP expects the following index pattern: i-start, i-end, j-start, j-end, k-start, k-end
    df['CARD_TEXT'] = 'Overwrite Solute Volumetric Concentration,NO3,' + \
                      df['INIT_COND'].map(number_format.format) + \
                      ',1/m^3,,,,,,,' + \
                      df['I'].astype('str') + \
                      ',' + \
                      df['I'].astype('str') + \
                      ',' + \
                      df['J'].astype('str') + \
                      ',' + \
                      df['J'].astype('str') + \
                      ',' + \
                      df['K'].astype('str') + \
                      ',' + \
                      df['K'].astype('str') + \
                      ','
    df.to_csv(
        path_or_buf=out_file,
        columns=['CARD_TEXT'],
        header=False,
        index=False
    )
    # Reload the file, remove the double quotes, add the appropriate card header, save and close!
    with open(out_file, 'r') as read_file:
        final_text = read_file.read()
    final_text = final_text.replace('"', '').replace('\r', '\n').replace('\n\n', '\n')
    with open(out_file, 'w') as write_file:
        write_file.write('#------------------------------------------------------------------\n')
        write_file.write('~Initial Conditions Card\n')
        write_file.write('#------------------------------------------------------------------\n')
        write_file.write('Gas Pressure, Aqueous Pressure,\n')
        write_file.write('{},\n'.format(len(df)))
        write_file.write('#------------------------------------------------------------------\n')
        write_file.write(final_text)
        write_file.write('#------------------------------------------------------------------\n')
    return out_file


def write_tecplot_file(df, out_file, number_format, display_units):
    """
    Takes the pandas dataframe, expecting the xyz coordinates and the volumetric concentrations (4 columns)
    :param df:              Must have the following columns: X, Y, Z, INIT_COND
    :param out_file:        The path to save the file to
    :param number_format:   The number format to use when writing the volumetric concentration values
    :param display_units:   The units to use for the concentration values
    :return:
    """
    # Sort the cells to be compatible with Tecplot formatting, sorting so that you increment X > Y > Z
    df.sort_values(by=['Z', 'Y', 'X'], ascending=True, inplace=True)
    # Get the index maxima
    i_max = df['I'].max(axis=0)
    j_max = df['J'].max(axis=0)
    k_max = df['K'].max(axis=0)
    # Write the header and the data to a string in memory
    write_str = 'VARIABLES = "X (m)" "Y (m)" "Z (m)" "Volumetric Concentration {}"\n'.format(display_units)
    write_str += 'ZONE T= "1" I={:>6}, J={:>6}, K={:>6} DATAPACKING=POINT\n'.format(i_max, j_max, k_max)
    write_str += df.to_string(
        columns=['X', 'Y', 'Z', 'INIT_COND'],
        formatters={'INIT_COND': number_format.format},
        justify='left',
        header=False,
        index=False
    )
    with open(out_file, 'w+') as write_file:
        write_file.write(write_str)
    return


# ----------------------------------------------------------------------------------------------------------------------
# Main Program
if __name__ == '__main__':
    # Build the dataframe of the concentrations
    init_conds = parse_csv(
        args.centroids_w_concs,
    )
    # Unify the concentration columns into one by taking the maximum of the "COPC_columns"
    init_conds['SOIL_CONC'] = init_conds[args.COPC_columns].max(axis=1)
    # Set values to zero if they are less than the specified threshold
    init_conds.loc[init_conds['SOIL_CONC'] < args.threshold, 'SOIL_CONC'] = 0
    init_conds.drop(columns=args.COPC_columns, inplace=True)
    # Sort the dataframe by the indices: I > J > K (levels)
    init_conds.sort_values(by=['I', 'J', 'K'], axis=0, ascending=True, inplace=True)
    init_conds.reset_index(drop=True, inplace=True)
    # Parse needed information from the STOMP card
    stomp_info = STOMP_obj(args.stomp_input)
    # Assign the material indices to each node
    try:
        init_conds['MAT_IDX'] = parse_zone_file(stomp_info.zonation_path, stomp_info.I_len, stomp_info.J_len, stomp_info.K_len)
    except ValueError:
        raise ValueError("Although the zone file was parsed correctly, the number of records didn't match up with\n"
                         "the number of centroids provided with the concentrations file. Verify that the right STOMP\n"
                         "model input file was used with the right soil concentrations file.")
    final_df = soil_to_vol_conc(init_conds, stomp_info.soil_lex, args.factor)
    # Write the initial conditions to file
    init_conds_file = write_init_conds(final_df, args.out_format, Path(args.output_directory, args.output_file_name))
    # Write out the detailed table for debugging purposes
    detail_file = Path(args.output_directory, '{}_detail.csv'.format(init_conds_file.stem))
    init_conds.to_csv(
        path_or_buf=detail_file,
        columns=['I', 'J', 'K', 'SOIL_CONC', 'MAT_IDX', 'BULK_DENSITY', 'FACTOR', 'INIT_COND'],
        index=False
    )
    # Write out the Tecplot files for visualizing the initial conditions recently generated.
    tec_file = Path(args.output_directory, '{}_tecplot.dat'.format(init_conds_file.stem))
    write_tecplot_file(init_conds, tec_file, args.out_format, args.display_units)
