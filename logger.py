#!/usr/bin/env python3
# coding: utf-8

# Logging
from logging import getLogger, Formatter, FileHandler, StreamHandler
from logging import INFO, DEBUG, ERROR, WARN

# Config
from config import CONFIG

#https://stackoverflow.com/questions/13034496/using-global-variables-between-file
LOGGER = None


def load_logger():
    """Creates LOGGER object"""
    global LOGGER

    LOGGER = getLogger(CONFIG['logger']['name'])
    LOGGER.setLevel(DEBUG)

    # TODO: Move FORMAT to config file
    formato = Formatter('%(asctime)s\t%(levelname)s\t%(module)s\t%(funcName)s\t%(message)s',
                        "%Y-%m-%d %H:%M:%S")

    file_handler = FileHandler(CONFIG['logger']['filename'])
    file_handler.setLevel(DEBUG)
    file_handler.setFormatter(formato)

    stream_handler = StreamHandler()
    stream_handler.setLevel(INFO)
    stream_handler.setFormatter(formato)

    LOGGER.addHandler(file_handler)
    LOGGER.addHandler(stream_handler)
