#Basic usage -c contaminates, -shp shape file to use, -i stomp input file to get grid card from, -s what model this is for, -o (optional) file name and directory to create the surface flux card
#tool to be run
tool=../../../CA-CIE-Tools-TestRepos/ca-surf_qa/CA-CIE-Tools/pylib/ca-surf/ca_build_surface_flux.py
#shape file with grid
gwgrid=../grid_attempt1/grid_attempt1.shp
#Stomp input file with grid
stomp_input=../ss/input
#model name
model=mpond
#output file
output=./rad1_surface_flux.txt
#list of COPCs
copc="C-14 Cl-36 H-3 I-129 Np-237 Re-187 Sr-90 Tc-99"
#location of toolrunner
tool_runner="/opt/tools/pylib/runner/runner.py"
#tool runner log file
runner_log="../runner_regridding_logfile.txt"
#Python alias to to be used.
py=python3.6
$py $tool_runner --logfile $runner_log --logfilemode 'w' "$py" "$tool -c $copc -shp $gwgrid -i $stomp_input -s $model -o $output"