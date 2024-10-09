# app/config.py
import os
import configparser
from pathlib import Path


def get_variable(key, config_file=Path(__file__).parent.parent / 'config/config.conf', section='config'):
    # Check if the variable exists as an environment variable
    value = os.getenv(key)
    
    if value is None:
        # If the environment variable doesn't exist, read from the config file
        config = configparser.ConfigParser()
        config.read(config_file)
        
        # Get the value from the configuration file
        value = config.get(section, key, fallback=None)
    
    return value