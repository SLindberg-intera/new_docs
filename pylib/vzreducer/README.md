# Vadose Zone data reduction

## running

You must run this code with the CA-CIE tool runner

## code organization
### reducer 
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

### constants
### config
### parse_input_file
### read_solid_waste_release
### timeseries 
### reduce_dataset
### reduce_flux
### plots
### summary_file
### recursive_contour
### timeseries
### read_solid_waste_release
### parse_input_file
### reduce_dataset
### reduce_flux
### reduction_result
### timeseries_math

## ToDo
- Code Documentation
- User Documentation
- Allocate mass balance of reduced data sets to points along the flux curve (rebalance)
- Remove orphaned code fragments
- Tests 
