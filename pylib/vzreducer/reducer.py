from config import config, parse_args 
import logging
import constants as c

def configure_logger(args):
    """
        set the logger for this utility
    """
    logging.basicConfig(
            level=c.LOG_LEVEL_MAP[args.loglevel],
            filemode=args.logfilemode.lower(),
            filename=args.logfile,
            **config[c.LOGGER_KEY]
            )

if __name__ == "__main__":
    args = parse_args()
    configure_logger(args)
    logging.info("START execution")

    logging.info("END execution")
