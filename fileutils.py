import json
import os
from os import path
from pathlib import Path

import constants
import specialmarkets

HELP_FILE_DIR = 'help.html'
SHARED_PREFS_FILE_DIR = 'shared_prefs.json'
SHARED_PREFS_OBJECT = {
    'mesghalSellRate': specialmarkets.Mesghal.MESGHAL_SELL_RATE,
    'mesghalBuyRate': specialmarkets.Mesghal.MESGHAL_BUY_RATE,
    'periodicTime': constants.PERIODIC_TIME,
    'updateOnlyChanges': constants.UPDATE_ONLY_CHANGES
}


def get_sharedprefs_full_dir():
    return os.path.join(Path(__file__).parent.absolute(), SHARED_PREFS_FILE_DIR)


def get_helps_full_dir():
    return os.path.join(Path(__file__).parent.absolute(), HELP_FILE_DIR)


def load_prefs_from_disk():
    global SHARED_PREFS_OBJECT

    print(SHARED_PREFS_OBJECT)
    if not path.exists(get_sharedprefs_full_dir()):
        print("Pref file not exists.")
        return

    SHARED_PREFS_OBJECT = read_shared_prefs()
    print("Load prefs from disk: ")
    print(SHARED_PREFS_OBJECT)
    return SHARED_PREFS_OBJECT


def read_shared_prefs():
    # with open(SHARED_PREFS_FILE_DIR, 'r') as read_file:
    with open(get_sharedprefs_full_dir(), "r") as read_file:
        return json.load(read_file)


def write_shared_prefs(data):
    # with open(SHARED_PREFS_FILE_DIR, 'w') as write_file:
    with open(get_sharedprefs_full_dir(), "w") as write_file:
        json.dump(data, write_file)


def read_help():
    # with open(HELP_FILE_DIR, 'r') as read_file:
    with open(get_helps_full_dir(), "r") as read_file:
        return read_file.read()
