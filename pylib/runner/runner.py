import constants as c
import sys, os
from config import config, parse_args
import logging
from pylib.info.info import Info
from pylib.pygit.git import get_version, is_clean_master_branch, get_remote_master_version , get_branch
from pathlib import Path

import subprocess

def configure_logger(args):
    """ set up the logger using the config parameters and
    the arguments passed from the command line"""
    logging.basicConfig(
            level=c.LOG_LEVEL_MAP[args.loglevel],
            filemode=args.logfilemode.lower(),
            filename=args.logfile,
            **config[c.LOGGER_KEY]
    )
    
def notify_user(message, shell=False):
    """ log the message if shell=True; print otherwise"""
    if shell:
        print(message)
    logging.info(message)    

def get_invoked_tool_name(args):
# SLL COMMENT--this might be better referred to as command since it could be either .exe (compiled tool) or python/perl
# if the tool is a script?
    """ return the tool name that was invoked at the command line"""
    return args.Name


def get_invoked_tool_arguments(args):
    """ return the arguments were invoked at the command line
    that should be passed to the targed tool when it is run
    """
    return args.Arguments

def make_user_message(args):
    """ construct a message to send to the user in the form 
    of a template defined in the config"""
    return config[c.USER_NOTIFICATION_KEY].format(Name=
        config[c.TOOL_NAME_KEY],
        logfile=args.logfile or "stdout")

def make_tool_use_message(args):
    """ constructs a message to notify the user which tool
    is being invoked.  Message is defined in the config template
    """
    tool_name = get_invoked_tool_name(args)
    tool_args = get_invoked_tool_arguments(args)
    return config[c.TOOL_NOTIFICATION_TEMPLATE_KEY].format(
            Name=tool_name, Arguments=tool_args
    )

def make_user_summary():
    """
      construct a string that contains information about user and computer
    """
    info = Info()
    return config[c.USER_INFO_TEMPLATE_KEY].format(
            machine=info.machine,
            computer=info.computer,
            uname=info.uname,
            platform=info.platform,
            username=info.username
    ) 

def get_approved_tools():
    return config[c.APPROVED_TOOL_KEY]

def get_pathtools(args):
    '''
        determine which tool/command being invoked by the runner (if .exe then = tool_name; if python or perl then 1st in arg.Arguments; if java more complicated)
    '''
# the following assumes that the command line statement is as follows:
# .. python ..\runner.py 'java|perl|python|*.exe' "arguments [if script (perl or python) first argument is tool script filename...java is a little more complex]"
    #input('in get path tools')
    command = get_invoked_tool_name(args)

    
# this conditional statement may need to be updated depending upon how the CAST tool is called by the tool runner
    if command[-4:] == '.exe':
        return [command]
    elif command == 'java':
        return get_filepathlist(args.Arguments)
    else:
        get_invoked_tool_arguments(args)
        return [get_invoked_tool_arguments(args).split(' ')[0]]
         

def get_currdir():
    return os.path.abspath(os.path.dirname(__file__))

def get_gitpath(pathfile):
    '''recursively searches upward in the invoked tool path for the git directory
        returns a string of the git directory path if found or  False if not found'''
    p = Path(pathfile)
    for path in p.parents:
        if (path.joinpath('.git').exists()):
            #input(path.joinpath('.git'))
            return(str(path.joinpath('.git')))
    return False 
    
def get_filename(pathfile):
    return Path(pathfile).name

def get_filepathlist(arguments):
    '''checks the arg.Arguments string for files or directories--used currently to find invoked files/library for CAST
        can be used for fingerprinter as well?'''
    arglist = arguments.replace('=',' ').split(' ')
    filepathlist = []

    for arg in arglist:
        if(Path(arg).exists()):
            filepathlist.append(arg)

    return filepathlist

def is_same_version(gitpath):

    return get_version(gitpath) == get_remote_master_version(gitpath)


#def is_on_qualified_list(args):
def is_on_qualified_list(tool_command):
#determine which tool being invoked by the runner (if .exe (or ?) then = tool_name; if script then = 1st argument)
# the following assumes that the command line statement is as follows:
# .. python ..\runner.py 'perl|python|*.exe' "arguments [if perl or python, script first argument is tool script filename...]"
    #command = get_invoked_tool_name(args)

# this conditional statement may need to be updated depending upon how the CAST tool is called by the tool runner
    #if command[-4:] == '.exe':
    #    tool_command = get_filename(command)
    #if command =='java':
    #    tool_command = "PENDING--not sure what to do with CAST...java library and a .jar file"
    #else:
    #    path_tool = get_invoked_tool_arguments(args).split(' ')[0]
    #    tool_command = get_filename(path_tool)

    approved_tools = get_approved_tools()
    for tool in approved_tools:
        input('{} :{}'.format(tool_command,tool))
        if tool_command == tool['command']:
            input(tool_command)
            input(tool['command'])
            return True
    return False

#note: args is a artifact--not currently used in the code for checking qa status
def make_qa_status(args, tool, path):
    """ construct a string showing the QA Status"""
    
    #DEBUG
    input(get_branch())
    input('{} : {}'.format(tool,path))
    input('checking to see if {} is in a repository {}'.format(tool, path))
    if path:
        input ('checking to see if {} is in a clean master branch {}'.format(tool,is_clean_master_branch(path)))
    input('checking to see if {} is is on the qualified tool list {}'.format(tool,is_on_qualified_list(tool)))
    if path:
        input('checking to see if local {} is same version as remote {}'.format(get_version(path), get_remote_master_version(path)))
    #END DEBUG    
    
    if path and is_same_version(path) and is_clean_master_branch(path) and is_on_qualified_list(tool) and is_same_version(path):
        status = c.QA_QUALIFIED
    else:
        status = c.QA_TEST

    return config[c.QA_STATUS_TEMPLATE_KEY].format(status='{} : {}'.format(status,tool))


def make_version(tool, path):
    if path:
        version = get_version(path)
    else:
        version =   "Not a git repository"  
    
    return config[c.VERSION_TEMPLATE_KEY].format(version='{} : {}'.format(version,tool))


def log_header(args,tg_dict):
    notify_user(make_user_message(args), shell=True)
    notify_user(make_tool_use_message(args))
    
    #check versioning (first for loop) and QA status (second for loop) of both the runner and the tool(s) being invoked....
    for tool, gitpath in tg_dict.items():
        notify_user(make_version(tool,gitpath))

    for tool, gitpath in tg_dict.items():
        #note: args is a artifact--not currently used in the code for checking qa status
        notify_user(make_qa_status(args,get_filename(tool), gitpath))
    notify_user(make_user_summary())

def execute_program(args):
    runargs = args.Arguments.split(" ")
    proc = subprocess.run(
        [args.Name]+runargs, shell=False)

if __name__ == "__main__":
    toolgitdict = {}
    #add toolrunner filename and its gitpath to tool/gitpath dictionary
    toolgitdict[__file__] = get_gitpath(__file__)

     
    args = parse_args()

    #get the tool(s) being invoked by runner and add to tool/gitpath dictionary--CAST references a library and jar file in repository--not handled at this time
    tool_list = get_pathtools(args)
    for path_tool in tool_list:
        toolgitdict[path_tool] =  get_gitpath(path_tool)

    configure_logger(args)
    log_header(args, toolgitdict)
    execute_program(args)
