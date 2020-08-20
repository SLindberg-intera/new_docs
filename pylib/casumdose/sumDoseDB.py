"""
  This computes the sum of the dose by aggregating
      over the dose from several COPCs.  

       the sum is over the COPCS and is computed for each distinct
         (row, column, layer, timestep, and exposure route/pathway)

   This program takes an inputControlFile (a JSON) that tells the program
    where to store the output and where to find the inputs.

   Inputs are assumed to be the output of ca-dosecalc


    this program uses postgres to do the actual calculation:
         - shell commands are constructed py parsing the input control file
         - shell commands are exected (many are sql statements):
             - a database is created
             - tables are defined
             - data is loaded into the database
             - indicies are made; and vacuum peformed
             - aggregation is performed
             - the result is sent to the output file
"""

import json
import os, sys
import subprocess

def parse_control_file(fpath):
    """ returns the control file as a dict """
    with open(fpath, 'r') as f:
        return json.loads(f.read())

class DoseFile:
    """ data class; 

        represents a path to a dose file

    """

    def __init__(self, copc, fpath):
        self.copc=copc
        self.fpath=fpath

    def __repr__(self):
        return "DoseFile(copc='{0}', fpath='{1}')".format(
		self.copc, self.fpath)

class ControlFile:
    """ Represents the input control file
          this is expected to be a JSON file that tells the name of
           the expected output, and then a list of files to use 
           as inputs.  Please see the documentation for more details.

          an example control file is provided 
             in exampleInputControlFile.json

        {
          "comment":"This is a test",  <-- not read
          "outputFile":"/path/to/outputs/dose.csv", <-- output name. Must be full path
          "dbname": "myspecialdatabase", <-- name of the database you are using 
          "doseFiles":[  <-- one input file per entry in this list
        	{ 
              "copc":"d1",  <-- the label used to track this file
              "fpath":"/inputs/data1.csv" <-- absoulte path to input file
        	},
        	{ 
              "copc":"d2",
              "fpath":"/inputs/data2.csv"
        	},
            {
              "copc":"d3",
              "fpath":"/inputs/data3.csv"
            }
          ]
        }
          
    """
    DOSEFILES = 'doseFiles'
    OUTPUTFILE = 'outputFile'
    DBNAME = 'dbname'

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
    def dbname(self):
        return self[self.DBNAME]

    @property
    def doseFiles(self):
        return list(map(lambda x: DoseFile(**x), self[self.DOSEFILES]))


class DoseFiles:
    """ Represents a dose file (the output of ca-dosecalc) 

        There is one Dose File per COPC
    """
    def __init__(self, dosefileslist):
        self._dosefiles = dosefileslist

    def __iter__(self):
        for item in self._dosefiles:
            yield item

def create_database_cmd(dbname):
    """ returns a command that when executed creates a database dbname """
    return ["createdb", dbname]

def drop_database_cmd(dbname):
    """ returns a command that when executed drops the database dbname """
    return ["dropdb", dbname]

def run_command(cmd):
    """ for a given cmd (command; an output of functions ending in _cmd

        call the command as a linux subprocess
    """
    proc = subprocess.run(cmd) 
    #, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def create_run_sql_cmd(dbname, sql):
    """ given a databasename, and a sequel statement,
        return a command that when executed, calls the sql statement
    """
    return ["psql", '-d', dbname,'-qAt','-c', sql]

def create_dose_table_cmd(dbname):
    """  Returns a command

    create the dose table and the staging table 

    """
    sql = """
        create table dose (
            copc VARCHAR(100),
            elapsed_tm INTEGER, 
            model_date VARCHAR(100), 
            soil VARCHAR(200), 
            pathway VARCHAR(200), 
            cell_row INTEGER, 
            cell_column INTEGER,
            cell_layer INTEGER, 
            concentration DOUBLE PRECISION, 
            dose_factor DOUBLE PRECISION, 
            dose DOUBLE PRECISION);

        create table dosestg (
            elapsed_tm INTEGER, 
            model_date VARCHAR(100), 
            soil VARCHAR(200), 
            pathway VARCHAR(200), 
            cell_row INTEGER, 
            cell_column INTEGER,
            cell_layer INTEGER, 
            concentration DOUBLE PRECISION, 
            dose_factor DOUBLE PRECISION, 
            dose DOUBLE PRECISION);
       
    """
    return create_run_sql_cmd(dbname, sql)

def copy_table_cmd(dbname, name, inputfile):
    """  returns a command

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

        this is used to build the column headers in calc_sum_cmd
    """
    return '''details->'{copc}' as "{copc}"'''.format(copc=copc)

def details_sql(copcs):
    """ return a string that will be used to select dose 
            this is used in calc_sum_cmd
    """
    return ", ".join([details_frag(copc) for copc in copcs])

def calc_sum_cmd(dbname, copcs):
    """ command to aggregate the dose as the table 'sumdose'  """
    details = details_sql(copcs)
    sql = """
    create table sumdose as 
        select pathway, elapsed_tm, cell_layer, cell_row, cell_column, model_date, 
            {details}, dose from (
                select elapsed_tm, model_date, cell_row,
                     cell_layer, cell_column, pathway,
                    json_object_agg(copc, dose)
                 as details, sum(dose) as dose from dose
        group by
            pathway, elapsed_tm, cell_layer, cell_row, cell_column, model_date) A;

    """.format(details=details)

    return create_run_sql_cmd(dbname, sql)

def vacuum_cmd(dbname):
    """ return a command that when executed performs a vacuum analyze on
        the dose table """
    sql = """vacuum analyze dose;"""
    return create_run_sql_cmd(dbname, sql)

def create_index_cmd(dbname,):
    """ command to create index on the dose table; useful for aggregation """
    sql = """
        create index tm_idx on dose (elapsed_tm);
        create index path_idx on dose (pathway);
        create index row_idx on dose (cell_row);
        create index lay_idx on dose (cell_layer);
        create index col_idx on dose (cell_column);

        drop table dosestg;

    """
    return create_run_sql_cmd(dbname, sql)


def comment_cmd(comment):
    """ return a command that when executed yields the comment
        prepends the time since run start
    """
    return ["echo", comment]

def export_cmd(dbname, outfile):
    """  return a command that when executed causes the database to export
          the summed dose data
    """
    sql = """
         copy sumdose to '{}' delimiter ',' csv header;
    """.format(outfile)
    return create_run_sql_cmd(dbname, sql)

def main(input_control_file):
    """
        1. Parse the input control file
        2. Assemble the shell commands 
        3. Execute the shell commands
            (build the database, load data, compute the sum, write data)

    """
    try:
        inputs = ControlFile(input_control_file)
    except Exception as e:
        raise IOError("Could not process the control file")
        return

    dose_files = DoseFiles(inputs.doseFiles) 

    def load_data_cmds():
        for item in dose_files:
            yield comment_cmd("Start loading dose file '{}'".format(item.copc))
            yield copy_table_cmd(inputs.dbname,item.copc, item.fpath)
            yield comment_cmd("Loaded dose file '{}'".format(item.copc))

    copcs = [item.copc for item in dose_files]

    commands = [
       drop_database_cmd(inputs.dbname),
       create_database_cmd(inputs.dbname),
       create_dose_table_cmd(inputs.dbname),
       comment_cmd("Start loading dose files"),
       *list(load_data_cmds()),
       comment_cmd("Finished loading dose files"),
       comment_cmd("Starting indexing"),
       create_index_cmd(inputs.dbname),
       vacuum_cmd(inputs.dbname),
       comment_cmd("Finished indexing"),
       comment_cmd("Start aggregation"),
       calc_sum_cmd(inputs.dbname, copcs),
       comment_cmd("Ended aggregation"),
       comment_cmd("writing output to '{}'".format(inputs.output_file)),
       export_cmd(inputs.dbname, inputs.output_file),
       comment_cmd("END")
    ]
    [run_command(cmd) for cmd in commands]
    

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

