""" 
    helpers for communicating with git

"""
import subprocess
import logging


GIT_COMMAND = 'git'

IS_NOT_A_GIT_COMMAND = 'is not a git command.'

GIT_PATH = ''
def check_output(out_bstr):
    """ validates the output of a git command; raises ValueError if fail"""
    res = out_bstr.decode('utf-8')
    if IS_NOT_A_GIT_COMMAND in res:
        raise ValueError(res)
    return res

def get_remote_master_version(path):
    """
        get the current remote master version  git --git-dir=/path/to/repo/.git rev-parse origin/<targeted-banch>
        NOTE: could be modified further to pass the branch in as an argument to make it more generic--the command
        doesn't necesarily have to be a "remote branch...string returned has a hard return so only returning the #[0:40]"
    """
    cmd = "--git-dir={} rev-parse origin/master".format(path)

    return run_command(cmd)[0:40]


def get_version(path):
    """ get the current tool version by inspecting git """
    cmd = "log -1"
    cmd = make_cmd(path,cmd)

    res = run_command(cmd)
    key = res.split("commit")[1].split()[0]
    return key

def is_clean_master_branch(path):
    """ True if we are on the last commit of the master branch
    with nothing changed """

    cmd = "status"
    cmd = make_cmd(path,cmd)

    res = run_command(cmd)
    if "On branch master" not in res:
        return False

    if "nothing to commit, working tree clean" in res:
        return True
    return False 


def get_branch():
    """ returns the current branch name"""
    cmd = "branch"
    res = run_command(cmd).split()[2]
    return res

def make_cmd(path, cmd):

    return "--git-dir {} {}".format(path,cmd)

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


