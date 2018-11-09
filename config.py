#!/usr/bin/env python3
# coding: utf-8

from ruamel import yaml

#https://stackoverflow.com/questions/13034496/using-global-variables-between-file
#global CONFIG
CONFIG = None


def load(config_file):
    """Parses YAML config file"""
    global CONFIG

    if CONFIG is not None:
        return

    with open(config_file, 'r') as stream:
        try:
            CONFIG = yaml.safe_load(stream)
            return True
        except yaml.YAMLError as yaml_error:
            print(yaml_error)
            return False
