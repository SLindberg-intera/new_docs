"""
    Helpers for writing ReductionResult objects file

"""
import os

APPEND_MODE = 'a'
WRITE_MODE = 'w'
NOTHING = ''

def summary_header(summary_file):
    hdr = "COPC,SITE,N reduced,N Iterations,y thresh,Area,Unreduced Total Mass Error (Ci) (Reduced-Orig),Reduced Total Mass (Ci) (Reduced-Orig\n"
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
    n_iterations        
        ):
    """
        reduction_result is an instance of ReductionResult
    """
    rr = reduction_result
    outline = "{copc},{site},{N},{ix},{ythresh:.2g},{area:.2g},{E_m:.2g},{E_t:.2g}\n".format(
            copc=rr.mass.copc,
            site=rr.mass.site,
            N=rr.num_reduced_points,
            ix=n_iterations,
            ythresh=used_ythresh,
            area=used_area,
            E_m=delta_mass,
            E_t=rr.total_mass_error
            )
    with open(summary_file, APPEND_MODE) as f:
        f.write(outline)


