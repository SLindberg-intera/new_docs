import json
import os, sys
import pandas as pd
from functools import reduce

def parse_control_file(fpath):
    """ returns the control file as a dict """
    with open(fpath, 'r') as f:
        return json.loads(f.read())

def open_df(fpath):
    return pd.read_csv(fpath)

class DoseFile:
    """ data class; 

        represents a path to a dose file

    """
    allowed_columns = ['pathway', 'elapsed_tm', 
	'cell_layer','cell_row','cell_column', 'dose']
    index_cols = ['pathway', 
	'elapsed_tm','cell_layer','cell_row','cell_column']

    def __init__(self, copc, fpath):
        self.copc=copc
        self.fpath=fpath

    def __repr__(self):
        return "DoseFile(copc='{0}', fpath='{1}')".format(
		self.copc, self.fpath)

    @property
    def df(self):
        """ pandas dataframe of the contents of self.fpath """
        try:
            return self._df
        except AttributeError:
            self._df = open_df(self.fpath)[self.allowed_columns]
            
            cols = [i for i in self._df.columns]
            cols[-1] = self.copc
            self._df.columns = cols
            self._df.set_index(self.index_cols, inplace=True,
		verify_integrity=True
		)

        return self.df


class ControlFile:
    """ Represents the input control file """
    DOSEFILES = 'doseFiles'
    OUTPUTFILE = 'outputFile'

    def __init__(self, fpath):
        self.data = parse_control_file(fpath)

    def __getitem__(self, key):
        try:
            return self.data[key]
        except KeyError as e:
            msg = "error parsing the control file: can't find '{}'".format(
		key)
            raise KeyError(msg)

    @property
    def output_file(self):
        return self[self.OUTPUTFILE]

    @property
    def doseFiles(self):
        return list(map(lambda x: DoseFile(**x), self[self.DOSEFILES]))


class DoseFiles:
    def __init__(self, dosefileslist):
        self._dosefiles = dosefileslist

    def merge(self):
        """ conbine all the dataframes into a single
             by joining on their axes """
        fn = lambda a, b: pd.concat([a, b], axis=1)
        total = reduce(fn, [i.df for i in self._dosefiles])
        keys = [i.copc for i in self._dosefiles]
        total['Sum'] = total[keys].sum(axis=1)
        return total

    @property
    def total(self):
        try:
            return self._total 
        except AttributeError:
            self._total = self.merge()
        return self._total


def main(input_control_file):
    try:
        inputs = ControlFile(input_control_file)
    except Exception as e:
        raise IOError("Could not process the control file")
        return

    dfs = DoseFiles(inputs.doseFiles) 
    with open(inputs.output_file, "w") as f:
        dfs.total.to_csv(f)


if __name__ == "__main__":
    try:
        control_file = sys.argv[1]

    except IndexError as e:
        raise IOError("Required argument missing: Path to control file")
        sys.exit(1)

    if(os.path.exists(control_file)):
        try:
            main(control_file)

        except Exception as e:
            print("Failed for {}".format(control_file))
            raise e
    else:
        msg = "Path to the input control file {} does not exist"
        raise IOError(msg.format(control_file))

