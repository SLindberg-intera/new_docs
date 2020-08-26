"""
    maxDose.py

    reimplementation that uses a postgres database backend

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
import subprocess

def create_database_cmd(dbname):
    """ returns a command that when executed creates a database dbname """
    return ["createdb", dbname]

def drop_database_cmd(dbname):
    """ returns a command that when executed drops the database dbname """
    return ["dropdb", dbname]

def run_command(cmd):
    """ for a given cmd (i.e. a command -- the output of 
          any function in this script ending in _cmd

        call the command as a linux subprocess
    """
    proc = subprocess.run(cmd) 
    #, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def create_run_sql_cmd(dbname, sql):
    """ given a databasename, and a sequel statement,
        return a command that when executed, calls the sql statement
    """
    return ["psql", '-d', dbname,'-qAt','-c', sql]


class DoseColumns:
    """
        represents column definitions that will
           be turned into columsn in the dose table
    """
    def __init__(self, datacolsdict):
        self._cols = datacolsdict

    @property
    def names(self):
        return [i['name'] for i in self._cols]

    def __iter__(self):
        for item in self._cols:
            yield item['name'], item['type'] 

    def as_table_def_str(self):
        """ return a string that can be used in a sql CREATE TABLE statement """
        return ",".join(["{} {}".format(*item) for item in self])

    def as_table_names_str(self):
        """ return a string that can be used in a sql SELECT statement """
        return ",".join(self.names)

def load_dose_table_cmd(dbname, dosepath, datacols):
    """ returns a command that when executed

      loads the dose table 

        datacols is expected to be a list of column names 
    """
    colfrags = datacols.as_table_def_str()
    colnames = datacols.as_table_names_str()

    sql = """
        create table dose(
           {colfrags}
           );
        create table maxdose(
            domain varchar(100),
            start_year INTEGER,
            end_year INTEGER,
            {colfrags}
        ); 
        create table maxdosets(
            domain varchar(100),
            start_year INTEGER,
            end_year INTEGER,
            {colfrags}
        );

        COPY dose({cols}) 
         from '{fname}' DELIMITER ',' CSV HEADER;

    """.format(colfrags=colfrags, cols=colnames, fname=dosepath)
    return create_run_sql_cmd(dbname, sql)


def export_cmd(dbname, outdir):
    """ return a command that when executed writes the results to file 

        two files are producted: 
            max_dose_timeseries: max year-by-year
            max_dose: the maximum over the interval 
    """
    
    timefile = os.path.join(outdir, 'max_dose_timeseries.csv')
    totalfile = os.path.join(outdir, 'max_dose.csv') 

    sql = """
        copy maxdose to '{}' delimiter ',' csv header;
        copy maxdosets to '{}' delimiter ',' csv header;
     """.format(totalfile, timefile)
    return create_run_sql_cmd(dbname, sql)

def load_boundary_cmd(dbname, boundary):
    """  returns a command that when executed, loads 
             the boundary into the exclusion table

        boundary should be an instance of Domain

     """

    sql = """
        truncate stginclude;

        copy stginclude(row, "column")
            from '{fname}' DELIMITER ',' CSV HEADER;

        update stginclude set boundary='{bname}';

        insert into include select boundary, row, "column" from stginclude;
            

    """.format(fname=boundary.fpath, bname=boundary.name)
    return create_run_sql_cmd(dbname, sql)
            

def create_include_table_cmd(dbname):
    """ returns a command that when executed creates
         a table to hold the cells that should be inluded

    """
    sql = """
        create table include(
            boundary varchar(200),
            row INTEGER,
            "column" INTEGER
        );
        create table stginclude(
            boundary varchar(200),
            row INTEGER, "column" INTEGER);
    """
    return create_run_sql_cmd(dbname, sql)


def copy_table_cmd(dbname, name, inputfile):
    """  returns a command that when executed

        Loads data from the inputfile into staging.  It then loads it into
        the dose table.

    """
    sql = """
        truncate dosestg;
        COPY dosestg(elapsed_tm, model_date, soil, pathway, cell_row,
            cell_column, cell_layer, concentration, dose_factor, dose)
         from '{0}' DELIMITER ',' CSV HEADER;


        INSERT INTO dose 
            select '{1}' as copc, elapsed_tm, model_date, soil, pathway, cell_row,
              cell_column, cell_layer, concentration, dose_factor, dose
            from dosestg;

    """.format(inputfile, name)
    return create_run_sql_cmd(dbname, sql)


def details_frag(copc):
    """ given a copc (string), return a text fragment that can 
         be used to extract that copc's dose 

        this is used to build the column headers in calc_sum_cmd from
          the copc names that are provided at run time in the inputControlFile
    """
    return '''details->'{copc}' as "{copc}"'''.format(copc=copc)

def details_sql(copcs):
    """ return a string that will be used to select dose 
            this is used do define column names in in calc_sum_cmd
              given the copc names specified at run time in the inputControlFile
    """
    return ", ".join([details_frag(copc) for copc in copcs])

def vacuum_cmd(dbname):
    """ return a command that when executed performs a vacuum analyze on
        the dose table """
    sql = """vacuum analyze;"""
    return create_run_sql_cmd(dbname, sql)

def create_index_cmd(dbname,):
    """ command to create index on the dose table;
             useful for efficient aggregation """
    sql = """
        create index tm_idx on dose (elapsed_tm);
        create index path_idx on dose (pathway);
        create index row_idx on dose (cell_row);
        create index lay_idx on dose (cell_layer);
        create index col_idx on dose (cell_column);
        create index icol_idx on include ("column");
        create index ir_idx on include (row);
        create index inm_idx on include (boundary);

    """
    return create_run_sql_cmd(dbname, sql)


def comment_cmd(comment):
    """ return a command that when executed yields the comment """
    return ["echo", comment]


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


class ExtractionInterval:
    """ corresponds to one time interval and domain """
    def __init__(self, year_range, domain):
        self.year_range = year_range
        self.domain = domain

    def extract_max_ts_to_file_cmd(self, dbname, copc):
        """ return a cmd that aggregates timeseries of the max over pathways """
        sql = """
             insert into maxdosets 
                select A.boundary, 
                   {start_year} as start_year,
                   {end_year} as end_year, S.* from (
                    select distinct on (year) 
                        boundary, year, cell_row, cell_column,
                         cell_layer, elapsed_tm 
                         from (
                            select *, split_part(model_date, '-', 1)::int as year
                            from dose
                           ) D, include I 
                    where D.cell_row=I.row
                        and I."column"=D.cell_column
                        and boundary = '{boundary}'
                        and year >= {start_year}
                        and year <= {end_year}
                    order by year, dose desc) A,
                        dose S where
                         S.cell_row=A.cell_row and
                         S.cell_column=A.cell_column and
                         S.cell_layer=A.cell_layer
                         and S.elapsed_tm=A.elapsed_tm
            order by boundary, start_year, elapsed_tm, elapsed_tm;
        
        """.format(boundary=self.domain.name, 
            start_year=self.year_range.start_year,
            end_year=self.year_range.end_year)

        return create_run_sql_cmd(dbname, sql)

    def extract_max_to_file_cmd(self, dbname, copc):
        """returns cmd that aggregates the max over pathways """
        sql = """
             insert into maxdose 
                select A.boundary, 
                   {start_year} as start_year,
                   {end_year} as end_year, S.* from (
                    select boundary, year, 
                    cell_row, cell_column, cell_layer, elapsed_tm 
                         from (
                            select *, split_part(model_date, '-', 1)::int as year
                            from dose
                           ) D, include I 
                    where D.cell_row=I.row
                        and I."column"=D.cell_column
                        and boundary = '{boundary}'
                        and year >= {start_year}
                        and year <= {end_year}
                    order by dose desc limit 1) A,
                        dose S where
                         S.cell_row=A.cell_row and
                         S.cell_column=A.cell_column and
                         S.cell_layer=A.cell_layer
                         and S.elapsed_tm=A.elapsed_tm
            order by pathway;

        """.format(boundary=self.domain.name, 
            start_year=self.year_range.start_year,
            end_year=self.year_range.end_year)

        return create_run_sql_cmd(dbname, sql)

    def __repr__(self):
        return "ExtractionInterval(year_range={}, domain={})".format(
            self.year_range, self.domain)

def iter_extraction_intervals(year_ranges, domains):
    """ iterates over the year ranges and domains to get 
          a stream of ExtractionInterval objects
    """
    for year_range in year_ranges:
        for domain in domains:
            yield ExtractionInterval(year_range, domain)

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
       
        return outdf.reset_index()


def make_filename(prefix, copc, domain, dateRange, suffix=".csv"):
    return "{}_{}_{}_yr{}-{}{}".format(prefix, 
            copc, domain, dateRange.start_year, dateRange.end_year, suffix)


class Domain:
    """ container for a model domain/boundary """
    def __init__(self, name, fpath):
        self.name=name
        self.fpath = fpath

    def __repr__(self):
        return "Domain(name={}, fpath={})".format(
            self.name, self.fpath)

def process_dose(fpath, copc, domain, year_range, outputDir):
    """  
         DEPRECIATED


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
    COLUMNS = 'columns'
    DBNAME = 'dbname' 

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
    def dbname(self):
        return self[self.DBNAME]
    @property
    def columns(self):
        return self[self.COLUMNS]

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
    date_ranges = inputs.date_ranges
    domains = inputs.domains
    outputDir = inputs.outputDir
    dbname = inputs.dbname
    datacols = DoseColumns(inputs.columns)
    copc = inputs.copc

    intervals = list(iter_extraction_intervals(date_ranges, domains))
    
    def load_table_commands(): 
        for domain in domains:
            yield load_boundary_cmd(dbname, domain)

    excmds = list(
        i.extract_max_to_file_cmd(dbname, copc) 
            for i in intervals)
    extscmds = list(
        i.extract_max_ts_to_file_cmd(dbname, copc)
            for i in intervals)
    
    commands = [
        drop_database_cmd(dbname),
        create_database_cmd(dbname),
        create_include_table_cmd(dbname),
        load_dose_table_cmd(dbname, dose_path, datacols),
        *list(load_table_commands()),
        create_index_cmd(dbname),
        vacuum_cmd(dbname),
        *excmds,
        *extscmds,
        export_cmd(dbname, outputDir) 
    ]
    # apply index
    # vacuum analyzee
    #  perform query to calculate the max where 
    # write the results

    [run_command(cmd) for cmd in commands]


if __name__=="__main__":
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
        raise IOError("Path to the input control file does not exist")

