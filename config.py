#!/usr/bin/env python3
# coding: utf-8

from ruamel import yaml

#https://stackoverflow.com/questions/13034496/using-global-variables-between-file
CONFIG = None


def load_config(file):
    """Parses YAML config file"""
    global CONFIG

    with open(file, 'r') as stream:
        try:

            CONFIG = yaml.safe_load(stream)
            return True
        except yaml.YAMLError as yaml_error:
            print(yaml_error)
            return False
