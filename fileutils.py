import json
import constants

from os import path

HELP_FILE_DIR = 'help.html'
SHARED_PREFS_FILE_DIR = 'shared_prefs.json'
SHARED_PREFS_OBJECT = {
    'mesghalUprate': constants.MESGHAL_UPRATE,
    'mesghalDownrate': constants.MESGHAL_DOWNRATE,
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
    with open(SHARED_PREFS_FILE_DIR, 'r') as read_file:
        return json.load(read_file)


def write_shared_prefs(data):
    with open(SHARED_PREFS_FILE_DIR, 'w') as write_file:
        json.dump(data, write_file)


def read_help():
    with open(HELP_FILE_DIR, 'r') as read_file:
        return read_file.read()
