""" 
    helpers for communicating with git

"""
import subprocess
import logging


GIT_COMMAND = 'git'

IS_NOT_A_GIT_COMMAND = 'is not a git command.'

def check_output(out_bstr):
    res = out_bstr.decode('utf-8')
    if IS_NOT_A_GIT_COMMAND in res:
        raise ValueError(res)
    return res

def get_version():
    """ get the current tool version by inspecting git """
    cmd = "log -1"
    res = run_command(cmd)
    key = res.split("commit")[1].split()[0]
    return key

def is_clean_master_branch():
    """ True if we are on the last commit of the master branch
    with nothing changed """
    cmd = "status"
    res = run_command(cmd)
    if "On branch master" not in res:
        return False


    return res

def run_command(command_str):
    """ runs a git command in the shell and returns the results as a text string"""
    shell_command = [GIT_COMMAND]
    shell_command += command_str.split(" ")
    proc = subprocess.Popen(shell_command, 
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    out, err = proc.communicate()
    if err:
        raise IOError(e.decode("utf-8"))

    return check_output(out) 


