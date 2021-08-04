import json
import os
import sys
from os import path

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


def load_prefs_from_disk():
    global SHARED_PREFS_OBJECT

    print(SHARED_PREFS_OBJECT)
    if not path.exists(SHARED_PREFS_FILE_DIR):
        print("Pref file not exists.")
        return

    SHARED_PREFS_OBJECT = read_shared_prefs()
    print("Load prefs from disk: ")
    print(SHARED_PREFS_OBJECT)


def read_shared_prefs():
    # with open(SHARED_PREFS_FILE_DIR, 'r') as read_file:
    with open(os.path.join(sys.path[0], SHARED_PREFS_FILE_DIR), "w") as read_file:
        return json.load(read_file)


def write_shared_prefs(data):
    # with open(SHARED_PREFS_FILE_DIR, 'w') as write_file:
    with open(os.path.join(sys.path[0], SHARED_PREFS_FILE_DIR), "w") as write_file:
        json.dump(data, write_file)


def read_help():
    # with open(HELP_FILE_DIR, 'r') as read_file:
    with open(os.path.join(sys.path[0], HELP_FILE_DIR), "r") as read_file:
        return read_file.read()
