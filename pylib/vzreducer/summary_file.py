"""
    Helpers for writing ReductionResult objects file

"""
import os

APPEND_MODE = 'a'
WRITE_MODE = 'w'
NOTHING = ''

def summary_header(summary_file):
    hdr = "COPC,SITE,N reduced,N Iterations,y thresh,Area,Original Total Mass, Unbalanced Total Mass Error (Ci) (Original-Reduced), Total Mass Relative Error [before rebalance](%),Balanced Total Mass (Ci) (Original-Reduced), Total Mass Relative Error [after rebalance] (%)\n"
    with open(summary_file, APPEND_MODE) as f:
        f.write(hdr)

def reset_summary_file(output_folder, summary_filename):
    summary_file = os.path.join(output_folder, summary_filename)
    with open(summary_file, WRITE_MODE) as f:
        f.write(NOTHING)
    summary_header(summary_file)
    return summary_file    

def summary_info(reduction_result, summary_file,
    delta_mass,        
    used_ythresh,
    used_area,
    n_iterations,
    out_error_last
        ):
    """
        reduction_result is an instance of ReductionResult
    """
    rr = reduction_result
    outline = "{copc},{site},{N},{ix},{ythresh:.2g},{area:.2g},{E_om:.2g}, {E_m:.2g}, {E_lre:.2g}, {E_t:.2g}, {E_bre:.2g}\n".format(
            copc=rr.mass.copc,
            site=rr.mass.site,
            N=rr.num_reduced_points,
            ix=n_iterations,
            ythresh=used_ythresh,
            area=used_area,
            E_om = rr.mass.values[-1],
            E_m=delta_mass,
            E_lre=out_error_last*100,
            E_t=rr.total_mass_error,
            E_bre=rr.relative_total_mass_error*100
            )
    with open(summary_file, APPEND_MODE) as f:
        f.write(outline)


