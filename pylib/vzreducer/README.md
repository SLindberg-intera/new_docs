# Vadose Zone data reduction

## running

You must run this code with the CA-CIE tool runner

## code organization
### [reducer](reducer.py) 
The 'main' program.  This will:
- parse input arguments
- read the config file
- configure the logger
- load two excel files containing the solid waste release data
- for every copc, site in the data:
  - reduce the data set
  - make a plot of the data and save it
  - make a .csv of the data
  - update a summary file
  - skip items where there is no release

### [constants](constants.py)
### [config](config.py)
### [parse_input_file](parse_input_file.py)
### [read_solid_waste_release](read_solid_waste_release.py)
### [timeseries](timeseries.py)
### [reduce_dataset](reduce_dataset.py)
### [reduce_flux](reduce_flux.py)
### [plots](plots.py)
### [summary_file](summary_file.py)
### [Ramer-Douglas-Peucker](rpd.py)
### [timeseries](timeseries.py)
### [read_solid_waste_release](read_solid_waste_release.py)
### [parse_input_file](parse_input_file.py)
### [reduce_dataset](reduce_dataset.py)
### [reduce_flux](reduce_flux.py)
### [reduction_result](reduction_result.py)
### [timeseries_math](timeseries_math.py)

## ToDo
