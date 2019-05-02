import os
import logging

READ_MODE = 'r'

thisdir = os.path.abspath(os.path.dirname(__file__))
CONFIG_FILE = os.path.join(thisdir, "config.json")

USER_NOTIFICATION_KEY = "User Notification Template"
TOOL_NAME_KEY = "Name"
TOOL_NOTIFICATION_TEMPLATE_KEY= "Tool Notification Template"

LOGGER_KEY = "LOGGER"

LOG_LEVEL_MAP = {
    "I":logging.INFO,
    "D":logging.DEBUG,
}
