"""
    Helpers for writing ReductionResult objects file

"""
import os

APPEND_MODE = 'a'
WRITE_MODE = 'w'
NOTHING = ''

def summary_header(summary_file,hdr):
    #hdr = variable #"COPC,SITE,N reduced,N Iterations,y thresh,Area,Original Total Mass, Unbalanced Total Mass Error (Ci) (Original-Reduced), Total Mass Relative Error [before rebalance](%),Balanced Total Mass (Ci) (Original-Reduced), Total Mass Relative Error [after rebalance] (%)\n"
    with open(summary_file, APPEND_MODE) as f:
        f.write(hdr)

def reset_summary_file(output_folder, summary_filename,header,mode):
    summary_file = os.path.join(output_folder, summary_filename)
    if mode == 'w':
        with open(summary_file, WRITE_MODE) as f:
            f.write(NOTHING)
        summary_header(summary_file,header)
    return summary_file

def summary_info(reduction_result,
    filename,
    summary_file,
    summary_template,
    delta_mass_last,
    used_epsilon,
    n_iterations,
    out_error_last
        ):
    """
        reduction_result is an instance of ReductionResult
    """
    rr = reduction_result
    #"{copc},{site},{N},{ix},{used_eps:.2g},{orig_total_mass:.7g}, {reduced_total_mass:.7g},{unbal_mass_err:.2g}, {unbal_rel_err:.2g}, {bal_mass_err:.2g}, {bal_rel_err:.2g}\n"

    outline = summary_template.format(
        copc=rr.mass.copc,
        site=rr.mass.site,
        N=rr.num_reduced_points,
        ix=n_iterations,
        used_eps=used_epsilon,
        orig_total_mass=rr.mass.values[-1],
        reduced_total_mass=rr.reduced_mass.values[-1],
        unbal_mass_err=delta_mass_last,
        unbal_rel_err=out_error_last*100,
        bal_mass_err=rr.total_mass_error,
        bal_rel_err=abs(rr.relative_total_mass_error)*100
        )
    with open(summary_file, APPEND_MODE) as f:
        f.write(outline)


