"""
Constants and ENUMS used throughout this module

"""

import os
import logging

READ_MODE = 'r'
thisdir = os.path.abspath(os.path.dirname(__file__))

CONFIG_FILE = os.path.join(thisdir, "config.json")
""" path to the config file that is loaded at run time"""

USER_NOTIFICATION_KEY = "User Notification Template"
"""config file key; used to identify the template string for formatting the first
    information that the user sees"""

TOOL_NAME_KEY = "Name"
""" key setting the name of *this* tool; I.E. the runner (not the tool invoked) by 
the runner
"""

TOOL_NOTIFICATION_TEMPLATE_KEY= "Tool Notification Template"
""" key setting the template of what info is displayed to the user about the
     tool that they are invoking"""

LOGGER_KEY = "LOGGER"
""" key of the config object defining the default parameters of the logger """ 

LOG_LEVEL_MAP = {
    "I":logging.INFO,
    "D":logging.DEBUG,
}
""" maps parsed logger arguments into logging ENUMs """

USER_INFO_TEMPLATE_KEY = "User Info Template"
""" template for the look of the header reported by the runner """

QA_QUALIFIED = "QUALIFIED"
QA_TEST = "TEST"
QA_STATUS_TEMPLATE_KEY = "QA Status Template"
