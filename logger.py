#!/usr/bin/env python3
# coding: utf-8

# Logging
from logging import getLogger, Formatter, FileHandler, StreamHandler
from logging import INFO, DEBUG, ERROR, WARN

# Config
import config

#https://stackoverflow.com/questions/13034496/using-global-variables-between-file
LOGGER = None


def load():
    """Creates LOGGER object"""
    global LOGGER

    if LOGGER is not None:
        return

    try:
        LOGGER = getLogger(config.CONFIG['logger']['name'])
        LOGGER.setLevel(DEBUG)
    except:
        return False

    # TODO: Move FORMAT to config file
    formato = Formatter('%(asctime)s | %(levelname)s | %(module)s | %(funcName)s | %(message)s',
                        "%Y%m%d %H:%M")

    file_handler = FileHandler(config.CONFIG['logger']['filename'])
    file_handler.setLevel(DEBUG)
    file_handler.setFormatter(formato)

    stream_handler = StreamHandler()
    stream_handler.setLevel(DEBUG)
    stream_handler.setFormatter(formato)

    LOGGER.addHandler(file_handler)
    LOGGER.addHandler(stream_handler)

    return True
