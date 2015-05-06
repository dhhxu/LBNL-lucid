#!/usr/bin/env python

"""
This is the extractor and processor script to handle downloaded building
energy data from Lucid's website (which should have been handled by the
get_data.py script). The script will extract the downloaded zip files and
split them if they contain more than one meter's data.
"""

import csv
import os
import zipfile

import util

def extract(filepath):
    """
    Extracts the contents of FILEPATH to the finished directory.
    """

    print("Extracting zip file: %s ..." % filepath),
    zf = zipfile.ZipFile(filepath)
    zf.extractall(path = util.FINISHED)
    print(" done")

def extract_all():
    """
    Extracts all zip files in the data folder, moves the csv files to the
    "finished" directory. The zip files are deleted.
    """

    print("Beginning zip file extraction.")
    for filename in os.listdir(util.DATA_PATH):
        filepath = util.DATA_PATH + filename
        if zipfile.is_zipfile(filepath):
            extract(filepath)
            os.remove(filepath)
        else:
            print("WARNING: %s not zip file" % filepath)
    print("Ending zip file extraction.")

def get_meter_ids(filepath):
    """
    Returns a list of the internal meter names as used in Lucid's system.
    These names would be used as the source name for the smap-load-csv
    script.
    """

    with open(filepath, 'rb') as f:
        reader = csv.reader(f)
        reader.next()           # Facility
        reader.next()           # Meter name
        ids = reader.next()     # Meter id
        return ids

def read_meter_data(filepath):
    """
    Returns a generator for the csv file located at FILEPATH.
    """

    with open(filepath, 'rb') as data:
        reader = csv.reader(data)
        for row in reader:
            yield row

def process(filepath):
    """
    Cleans up the contents of the csv file at FILEPATH, if the file contains
    data for more than one meter. In this case, creates new csv files for each
    meter and deletes the original file. Otherwise, does nothing.
    """

    meters = get_meter_ids(filepath)
    if len(meters) - 1 > 1:
        meters = meters[1:]
        print("[%s] has %d meters. Splitting ..." % (filepath, len(meters)))
        for i, name in enumerate(meters, 1):
            split_write(filepath, name, i)
        os.remove(filepath)
    else:
        print("[%s] has 1 meter. Skipping." % (filepath))

def split_write(filepath, name, index):
    """
    Called when the csv file at FILEPATH contains data for at least 2 meters.
    Writes a new csv file for meter NAME, whose data column is at column
    INDEX (zero-indexed). The new file name will be of form {FILEPATH}_{NAME}.
    """

    new_filepath = os.path.splitext(filepath)[0] + "_" + name + ".csv"
    with open(new_filepath, 'wb') as output:
        print("Creating new file [%s]" % new_filepath)
        writer = csv.writer(output)
        for row in read_meter_data(filepath):
            if (row):
                writer.writerow([ row[0], row[index] ])
            else:
                writer.writerow([])
             
def process_all():
    """
    Processes all csv files in the finished folder, splitting them if they
    have data on more than one meter.
    """

    print("\nBegin processing ...\n")
    for filename in os.listdir(util.FINISHED):
        ext = os.path.splitext(filename)[1]
        if ext.lower() == ".csv":
            filepath = util.FINISHED + filename
            process(filepath)
    print("\nProcessing done.")

def main():
    """
    Main function.
    """

    extract_all()
    process_all()

if __name__ == '__main__':
    main()
