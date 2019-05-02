""" 
    helpers for communicating with git

"""
import subprocess
import logging


GIT_COMMAND = 'git'

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
    return out.decode("utf-8")


