import constants as c
from config import config, parse_args
import logging
from pylib.info.info import Info
from pylib.pygit.git import get_version, is_clean_master_branch

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

def make_qa_status():
    """ construct a string showing the QA Status"""
    if is_clean_master_branch():
        status = c.QA_QUALIFIED
    else:
        status = c.QA_TEST
    return config[c.QA_STATUS_TEMPLATE_KEY].format(status=status)


def make_version():
    version = get_version()
    return config[c.VERSION_TEMPLATE_KEY].format(version=version)


def log_header(args):
    notify_user(make_user_message(args), shell=True)
    notify_user(make_tool_use_message(args))
    notify_user(make_version())
    notify_user(make_qa_status())
    notify_user(make_user_summary())

def execute_program(args):
    pass

if __name__ == "__main__":
    args = parse_args()
    configure_logger(args)
    log_header(args)
    execute_program(args)

