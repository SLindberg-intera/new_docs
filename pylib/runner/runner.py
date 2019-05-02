import constants as c
from config import config, parse_args
import logging

def configure_logger(config, args):
    logging.basicConfig(
            level=c.LOG_LEVEL_MAP[args.loglevel],
            filename=args.logfile,
            **config[c.LOGGER_KEY]

            )
    


def notify_user(message, shell=False):
    if shell:
        print(message)
    logging.info(message)    

def get_invoked_tool(args):
    return args.Name

def get_invoked_tool_arguments(args):
    return args.Arguments

def make_user_message(config):
    return config[c.USER_NOTIFICATION_KEY].format(Name=
        config[c.TOOL_NAME_KEY])

def make_tool_use_message(config, args):
    tool_name = get_invoked_tool(args)
    tool_args = get_invoked_tool_arguments(args)
    return config[c.TOOL_NOTIFICATION_TEMPLATE_KEY].format(
            Name=tool_name, Arguments=tool_args)

if __name__ == "__main__":
    args = parse_args()
    configure_logger(config, args)
    notify_user(make_user_message(config), shell=True)
    notify_user(make_tool_use_message(config, args))
