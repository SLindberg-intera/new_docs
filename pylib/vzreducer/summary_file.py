"""
    Helpers for writing ReductionResult objects file

"""
import os

APPEND_MODE = 'a'
WRITE_MODE = 'w'
NOTHING = ''

def summary_header(summary_file):
    hdr = "COPC,SITE,N reduced, Relative Mass Error, Total Mass (Ci)\n"
    with open(summary_file, APPEND_MODE) as f:
        f.write(hdr)

def reset_summary_file(output_folder, summary_filename):
    summary_file = os.path.join(output_folder, summary_filename)
    with open(summary_file, WRITE_MODE) as f:
        f.write(NOTHING)
    summary_header(summary_file)
    return summary_file    

def summary_info(reduction_result, summary_file):
    """
        reduction_result is an instance of ReductionResult
    """
    rr = reduction_result
    outline = "{copc},{site},{N},{E_m:.2g},{E_t:.2g}\n".format(
            copc=rr.mass.copc,
            site=rr.mass.site,
            N=rr.num_reduced_points,
            E_m=rr.relative_total_mass_error*100,
            E_t=rr.total_mass_error
            )
    with open(summary_file, APPEND_MODE) as f:
        f.write(outline)


