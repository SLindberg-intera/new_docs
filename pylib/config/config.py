"""
Simple utility for reading a config file

Assumes a JSON format for input

"""
import json

READ_MODE = 'r'

def read_config(path_to_json_file):
    with open(path_to_json_file, READ_MODE) as f:
        config = json.load(f)
    return config
