#/bin/bash
PYTHON=python3.6
TOOL=ca-ipp_check.py
# Variables for checking script
EHSIT=/opt/ICF/Prod/VZEHSIT/v1.1/data/Original/WasteSites\(ehsit\)_Geometry_SIMV2_CA-dos2unix.csv
RADINV=/opt/ICF/Prod/VZINV/v1.0/data/F_CP-61786_R1_sorted_mar42020.csv
CHEMINV=none
LIQINV=/opt/ICF/Prod/CLEANINV/v1.0/data/inflow-04_inv1-edited.res
SWRDIR=/opt/ICF/Prod/RCASWR/v1.0/data
SWRIND=CASWR_Output_20200219_summary_03.09.2020.csv
REROUTE1=/opt/ICF/Prod/SALDSINV/v1.0/data/600-211_salds_Inventory_02272020.csv
REROUTE2=./data_sources/U10B3INV/v1.0/data/U-10_B-3_reroute_rates.csv
CA_IPP=preprocessed_inventory.csv
$PYTHON $TOOL --VZEHSIT $EHSIT --VZINV $RADINV --CLEANINV $LIQINV --RCASWR_dir $SWRDIR --RCASWR_idx $SWRIND --REDFIN $REROUTE1 $REROUTE2 -i $CA_IPP