import logging
import sys
from config import Config
from database import DB
import rawsql

def setup_logger(logfile='example.log'):
    logging.basicConfig(filename=logfile, level=logging.DEBUG)
    logging.debug("Configured logger")

sql = [
        ]

if __name__=='__main__':
    jsonfile = sys.argv[1]
    config = Config.load(jsonfile)
    setup_logger(config[Config.LOGFILE])

    db = DB(config['dsn'])
    res = db.transact(rawsql.pathways)
    
    print(res)
