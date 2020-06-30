"""
    Loads a configuration file

    assumes JSON format

"""


import json
class Config:
    LOGFILE = 'logfile'

    def __init__(self, config):
        self.config = config

    def __str__(self):
        return json.dumps(self.config)

    @classmethod
    def load(cls, configJson):
        with open(configJson, 'r') as f:
            return cls(config=json.loads(f.read()))

    def __getitem__(self, key):
        return self.config[key]
