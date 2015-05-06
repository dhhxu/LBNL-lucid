#!/usr/bin/env python

"""
This script loads already processed building energy data (processing done by
by extract_data.py) into an sMAP server, with the help of smap-load-csv.

Dependencies: util.py, sMAP library
"""

import csv
import os
import shutil
import subprocess
import uuid

import util

ARCHIVED = util.FINISHED + "archived/"
INFO = os.getcwd() + "/info/"

# The location of the map file. This file provides a 1 to 1 mapping of
# internal source name to UUID.
MAP = INFO + "map.csv"

# smap-load-csv parameter values:
LINE_SKIP = 4
TIME_FORMAT = "%Y-%m-%d %H:%M"
DEST_PREFIX = util.DEST_PREFIX 
API = util.API
REPORT_DEST = DEST_PREFIX + API

def get_meter_id(filepath):
    """
    Returns the Lucid's internal file name for data file FILEPATH. This name
    is to be used as the source name argument in the smap-load-csv script.
    """

    with open(filepath, 'rb') as f:
        reader = csv.reader(f)
        reader.next()
        reader.next()
        ids = reader.next()
        return ids[1]

def get_uuid(source_name):
    """
    Returns the UUID if SOURCE_NAME has a UUID assigned to it in the map.csv
    file located in the info directory, None otherwise. The map file is
    assumed to exist.
    """

    with open(MAP, "rb") as mapfile:
        reader = csv.reader(mapfile)
        for row in reader:
            if source_name.lower() == row[0].lower():
                return row[1]
        return None

def assign_uuid(source_name):
    """
    Generates a UUID for SOURCE_NAME and writes a new entry in the map.csv
    file. Returns the generated UUID.
    """

    new_id = uuid.uuid4()
    with open(MAP, 'a') as mapfile:
        writer = csv.writer(mapfile)
        writer.writerow([source_name, new_id])
        return new_id.hex

def build_input_string(source_name, uid, filepath):
    """
    Generates the command list to be passed to subprocess call.
    """

    base = ["smap-load-csv"]
    base.append("--uuid=" + uid)
    base.append("--source-name=" + source_name)
    base.append("--skip-lines=" + str(LINE_SKIP))
    base.append("--time-format=" + TIME_FORMAT)
    base.append("--report-dest=" + REPORT_DEST)
    base.append(filepath)
    return base

def cleanup(uid):
    """
    The smap-load-csv script generates files for buffering when it runs.
    These files are located in the same directory as this script.
    If the load is successful, we no longer need those files. The created
    files are prefixed with UID.
    """

    cwd = os.getcwd()
    print("Cleaning up ..."),
    for filename in os.listdir(cwd):
        if uid in filename:
            path = cwd + "/" + filename
            if os.path.isfile(path):
                os.remove(path)
            else:
                shutil.rmtree(path, ignore_errors = True)
    print("done")

def load_all():
    """
    Loads all processed data files in the finished directory into the sMAP
    server. Loaded files are then moved to the archived directory.
    """

    print("Begin loading ...\n")
    for filename in os.listdir(util.FINISHED):
        filepath = util.FINISHED + filename
        if os.path.isfile(filepath):
            ext = os.path.splitext(filename)[1]
            if ext.lower() == ".csv":
                status = load(filepath)
                if not status:
                    print("[FAIL]")
                else:
                    os.rename(filepath, ARCHIVED + filename)
                    print("[OK]")
    print("\nLoading done.")

def load(filepath):
    """
    Loads the data file FILEPATH into the sMAP server. Assumes that FILEPATH
    has already been processed by the extract_data script. Returns TRUE if
    the load succeeded, FALSE otherwise.
    """

    source_name = get_meter_id(filepath)
    print("Handling %s" % filepath)
    uid = get_uuid(source_name)
    if not uid:
        uid = assign_uuid(source_name)
    status = ""
    try:
        cmd = build_input_string(source_name, uid, filepath)
        status = subprocess.check_output(cmd)
    except subprocess.CalledProcessError, e:
        print("[ERROR] code %d" % (e.returncode))
        print("[ERROR] %s" % (e.output))
        return False
    # Server error -- command will have 0 exit code but not actually work.
    if "reply" in status.lower():
        return False

    cleanup(str(uid))
    return True

def main():
    """
    Main function.
    """

    load_all()

if __name__ == "__main__":
    main()
