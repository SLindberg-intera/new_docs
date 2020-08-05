"""
    maxDose.py

    This stand-alone tool that will calculate the
    maximum dose by processing the output of the DoseCalculator

    for each timeinterval in Intervals
        For each domain (defined as a set of rows/columns):
            At each time, t: 
                For each pathway and for the total (sum over pathways):
                    Max dose
                    Location (layer/row/col) of the max dose
                    time (date) of the max dose
            Regardless of t:
                For each pathway and for the total (sum over pathways):
                    Max dose
                    Location (layer/row/col) of max dose
                    time (date) of the max dose

    This reads an input control file that defines the
        Domains and the Intervals

    requires the third-party pandas library



    this is intended to be used on the command line.  The first argument
    is the path to the control file:

    maxDose.py input.json
"""

import os
import pandas as pd
import json
import sys

def row_col_to_id(row, col):
    """ map (row, col) to a single number """
    return int(row)+int(col)*1000

class Cell:
    """ container class; represent a row/col pair"""
    def __init__(self, row, col):
        self.row = row
        self.col = col

    def __repr__(self):
        return "Cell(row={}, col={})".format(self.row, self.col)

    @property
    def id(self):
        """ return a single value that can be used to ID a cell """
        return row_col_to_id(self.row, self.col)

class YearRange:
    """ container class; represent a start and end year"""
    def __init__(self, start_year, end_year):
        self.start_year = start_year
        self.end_year = end_year
    def __repr__(self):
        return "YearRange(start_year={}, end_year={})".format(
           self.start_year, self.end_year)

def date_string_to_year(date_str):
    """ turn '2020-01-01' to the integer 2020 """
    return int(date_str.split("-")[0])

def extract_for_year_range(df, year_range):
    """
        take a dataframe and return a subset for the year_range
            dates are from start_year to end_year, inclusive
    """
    years = df.model_date.apply(date_string_to_year).values
     
    out = df.iloc[
        (years >=year_range.start_year)&(years<=year_range.end_year)]
    return out

def extract_for_cells(df, cells):
    """ given a Cells instance and a pandas dataframe, 

    return a dataframe that only includes the cells
    """
    ids = [i.id for i in cells]
    truth = df.apply(
           lambda x: row_col_to_id(x.cell_row, x.cell_column), axis=1)
    truth = truth.isin(ids)
    return df.loc[truth]

class DoseFile:
    """ pandas dataframe representation of a dose file """
    def __init__(self, filepath, df=None):
        if(filepath is not None):
            self.df = pd.read_csv(filepath) 
            return

        if(df is not None):
            self.df = df

    @classmethod
    def from_df(cls, df):
        """ returns an instance given a pandas dataframe"""
        return cls(filepath=None, df=df)

    def reduce(self, year_range, cells=None, inplace=True):
        """ cut portion not containing year_range and cells
        
            if inplace=False, does not update 
        """
        reduced = extract_for_year_range(self.df, year_range)
        if cells is None:
            print("Cells is none, no mask applied")
            pass
        else:    
            reduced = extract_for_cells(reduced, cells)
        if(inplace==True):
            self.df = reduced
            return self

        return self.from_df(reduced)

    def max_by_pathway_by_time(self):
        """ for each pathway, for each timestep,
            find the max dose anywhere in space

            returns a pandas dataframe
        """
        outdf = self.df.sort_values(by='dose',
                ascending=False).groupby(['pathway','model_date']).first()
        return outdf.reset_index()

    def max_by_pathway(self):
        """
            for each pathway, find the max dose anywhere and at any time

            returns a pandas dataframe
        """
        outdf = self.df.sort_values(by=['dose', 'elapsed_tm'],
                ascending=[False, True])
        outdf = outdf.groupby(['pathway'], sort=False).first()
        #outdf = outdf.idxmax()
        #print("Dose output:\n", outdf['dose'])
        print("RESULT:\n", outdf)
       
        return outdf.reset_index()


def to_csv(df, fname):
    """ writes a pandas dataframe to a csv file. """
    df.to_csv(fname)
    return 

def make_filename(prefix, copc, domain, dateRange, suffix=".csv"):
    return "{}_{}_{}_yr{}-{}{}".format(prefix, 
            copc, domain, dateRange.start_year, dateRange.end_year, suffix)


class Domain:
    """ container for a model domain/boundary """
    def __init__(self, name, fpath):
        self.name=name
        self.fpath = fpath
        try:
            self._cells = self.load_file()
        except Exception as e:
            self._cells = None
    
    def __repr__(self):
        return "Domain(name={}, fpath={})".format(
            self.name, self.fpath)

    def load_file(self):
        """  load cells from the target file 

        file is assumed to be a header row and then
        each line containing a comma-separated ROW,COL tuple
        """
        
        with open(self.fpath, 'r') as f:
            cells = [Cell(*line.strip().split(",")) 
               for line in f.readlines()[1:]]
        return cells 

    @property
    def cells(self):
        return self._cells

def process_dose(fpath, copc, domain, year_range, outputDir):
    """
        given a path to a dose file
        a copc (used as a label)
        a Domain
        and a YearRange 

        do all the dose processing (find the max by 
           pathway, time, etc.)

        outputs the result to outputDir   

    """
    dose = DoseFile(fpath)
    cells = domain.cells 

    domain = domain.name
    copc = copc
    reduced = dose.reduce(year_range, cells, inplace=False)

    dfmaxts = reduced.max_by_pathway_by_time()

    outname = os.path.join(outputDir, "max_for_pathway_for_time")
    n = make_filename(outname, copc, domain, year_range)
    to_csv(dfmaxts, n)

    dfmax = reduced.max_by_pathway()
    outname = os.path.join(outputDir, "max_for_pathway")
    n = make_filename(outname, copc, domain, year_range)
    to_csv(dfmax, n)

def parse_control_file(fpath):
    """ returns the control file as a dict """
    with open(fpath, 'r') as f:
        return json.loads(f.read())

class ControlFile:
    """ Represents the input control file

    expects a json file of the form:
    
    {
        "copc":"U235",   <---  copc name
        "dosepath":"data/U235.csv",   <--- path to dose file
        "domains":[ <--- a list of domain objects
            {"name":"inner", "fpath":""},  <--- name and path to domain
            {"name":"outer", "fpath":""},
            {"name":"ca99", "fpath":""}
        ],
        "outputdir":"output",
        "dateranges":[ <--- a list of YearRange objects
            {"start_year":2070, "end_year":3070},  
            {"start_year":3070, "end_year":12070}
        ]
    }
    
    """
    COPC = 'copc'
    DATERANGES = 'dateranges'
    START_YEAR = 'start_year'
    END_YEAR = 'end_year'
    DOMAINS = 'domains'
    DOSEPATH = 'dosepath'
    FPATH = 'fpath'
    NAME = 'name'
    OUTPUTDIR = 'outputdir'

    def __init__(self, fpath):
        self.data = parse_control_file(fpath)

    def __getitem__(self, key):
        try:
            return self.data[key]
        except KeyError:
            msg = "Error parsing the control file: can't find '{}'"
            raise KeyError(msg.format(key))

    @property
    def copc(self):
        return self[self.COPC]

    @property
    def date_ranges(self):
        rawranges = self[self.DATERANGES]
        ranges = [
            YearRange(start_year=item[self.START_YEAR], 
                end_year=item[self.END_YEAR])
          for item in rawranges]
        return ranges

    @property
    def dose_path(self):
        return self[self.DOSEPATH]

    @property
    def outputDir(self):
        return self[self.OUTPUTDIR]

    @property
    def domains(self):
        ds = self[self.DOMAINS]
        domains = [
           Domain(name=item[self.NAME], fpath=item[self.FPATH])
           for item in ds]
        return domains


def main(input_control_file_path):
    """

        main execution: given a input control file,
            - parse the control file
            - for each Domain:
                - for each DateRange:
                  - process the dose data
    """
    try:
        inputs = ControlFile(input_control_file_path)
    except Exception as e:
        raise IOError("Could not process the control file")
        return
    
    dose_path = inputs.dose_path
    copc = inputs.copc
    date_ranges = inputs.date_ranges
    domains = inputs.domains
    outputDir = inputs.outputDir
    
    for domain in domains:
        for date_range in date_ranges:
            print(domain, date_range)
            process_dose(dose_path, copc, domain, date_range, outputDir)


if __name__=="__main__":
    try:
        control_file = sys.argv[1]
    except IndexError as e:
        raise IOError("Required argument missing: Path to control file") 
        sys.exit(1)

    if(os.path.exists(control_file)):
        main(control_file)
    else:
        raise IOError("Path to the input control file does not exist")

