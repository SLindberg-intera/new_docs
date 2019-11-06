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
    cmd = "fetch"
    #run git fetch to fetch most recent remote version (this is not a pull--does not affect branches)
    run_command(cmd)
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
    input('in the is clean master branch function')
    cmd = "--work-tree={} status".format(path[0:-5])
    cmd = make_cmd(path,cmd)
    #cmd = '-C {} --work-tree={} status'.format(path,path[0:-4])
    input(cmd)
    res = run_command(cmd)
    input(res)
    if "On branch master" not in res:
        input('in the first if statement and returning false from there')
        return False
    
    #version 1.9.1 =  nothing to commit, working directory clean
    #version 2.21.0.windows.1 = nothing to commit, working tree clean
    #update this conditional statement when git version on olive is updated
    if "nothing to commit, working " and " clean" in res:
        input('in the second if statement and returning true')
        return True
    input('passed both if statements and returning last false')
    return False 


def get_branch():
    """ returns the current branch name"""
    cmd = "branch"
    input('getting the branch name....'.format(run_command(cmd)))
    res = run_command(cmd).split()[2]
    input('the result is {}'.format(res))
    return res

def make_cmd(path, cmd):

    return "--git-dir={} {}".format(path,cmd)

def run_command(command_str):
    """ runs a git command in the shell and returns the results as a text string"""
    shell_command = [GIT_COMMAND]
    shell_command += command_str.split(" ")
    input(shell_command)
    proc = subprocess.Popen(shell_command, 
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    out, err = proc.communicate()
    if err:
        raise IOError(e.decode("utf-8"))

    return check_output(out) 


