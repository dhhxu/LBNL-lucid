"""
Utility functions for the following scripts:

    get_data.py
    extract_data.py
    process_data.py
"""

from os import getcwd
from os import getenv
from datetime import datetime

# Directories
DATA_PATH = getcwd() + "/data/"
FINISHED = getcwd() + "/finished/"

# BuildingOS Login info
USER = getenv('LUCIDUSER') 
PASS = getenv('LUCIDPASS')

URL = 'https://buildingos.com'

# sMAP info
DEST_PREFIX = getenv('SMAPPREFIX')
API = getenv('SMAPAPI')

# Getter information
DATA_WAIT_PERIOD = 15               # Refresh every 15 seconds
MAX_RETRIES = 20                    # Maximum wait time

def err(msg, code=1):
    """
    Print error message and quits script with exit code. CODE is 1 by default.
    """

    print "ERROR: %s\n" % msg
    exit(code)

def alert(msg):
    """
    Print MSG.
    """

    print "%s" % msg

def valid_date(date):
    """
    Checks if DATE is of form MM/DD/YYYY. Does not check if YYYY is correct.
    Also, does not check for edge cases, i.e. Feb 30.
    """
    mdy = date.split("/")
    if (len(mdy) == 3):
        try:
            m = int(mdy[0])
            d = int(mdy[1])
            y = int(mdy[2])
            datetime(y, m, d)
            return True
        except TypeError, ValueError:
            return False
    return False

def get_datetime(date):
    """
    Return the datetime object representing DATE. DATE must be valid.
    """

    mdy = date.split("/")
    m = int(mdy[0])
    d = int(mdy[1])
    y = int(mdy[2])
    return datetime(y, m, d)

def convert_date(date):
    """
    Convert date of form MM/DD/YYYY into YYYY-MM-DD. Assumes date is correct
    form.
    """
    
    mdy = date.split("/")
    m = mdy[0]
    d = mdy[1]
    y = mdy[2]
    newDate = "%s-%s-%s" % (y, m, d)
    return newDate

def get_dates():
    """
    Prompt the user for a start and end date.
    This function will keep prompting until valid dates are entered.
    Returns a tuple of start date and end date.
    """

    hasValidStart = False
    hasValidEnd = False
    start = None
    end = None
    while True:
        if not hasValidStart:
            start = raw_input("Enter start date (MM/DD/YYYY): ") 
            if not valid_date(start):
                print "Invalid start date %s" % (start)
                continue
            else:
                hasValidStart = True
        if not hasValidEnd:
            end = raw_input("Enter end date (MM/DD/YYYY): ")
            if not valid_date(end):
                print "Invalid end date %s" % (end)
                continue
            else:
                hasValidEnd = True
        if hasValidStart and hasValidEnd:
            if get_datetime(start) < get_datetime(end):
                break
            else:
                print "End date comes before start date. Please try again."
                hasValidStart = False
                hasValidEnd = False
    return (start, end)

def valid_index(index, left, right):
    """
    Checks if INDEX is a valid number and is within the index range. If valid,
    returns TRUE. Otherwise, returns FALSE.
    """

    try:
        num = int(index)
        return (num >= left and num <= right)
    except ValueError, TypeError:
        return False

def display_meters(all_meters):
    """
    Print meter names and their indices. Meters come from ALL_METERS list.
    Note that indices begin at 1.
    """

    for index, meter in enumerate(all_meters, 1):
        if index < 10:
            print "  %d:  %s" % (index, meter)
        else:
            print "  %d: %s" % (index, meter)
    print "\n"

def get_meters(meters):
    """
    Prompt user to enter indicies of the meters desired. At least one index must
    be entered. Returns the selected indices.
    """

    user_list = []
    atLeastOneMeter = False
    minIndex = 1
    maxIndex = len(meters)
    display_meters(meters)
    print("Please select the indices of the meters desired. Enter 'all' if all"
          "meters are desired (not recommended, as performance will decrease)."
          " Enter 'done' to end selection.")
    while True:
        index = raw_input("Enter a meter index: ") 
        if index == "all":
            return meters
        if not atLeastOneMeter:
            if index == "done":
                print "No meters selected. Please try again."
                continue
            if not valid_index(index, minIndex, maxIndex):
                print "Invalid meter index."
                continue
            num = int(index)
            if not num in user_list:
                user_list.append(num)
                atLeastOneMeter = True
            else:
                print "Meter already selected. Please pick a different one"
        else:
            if index == "done":
                return user_list
            if not valid_index(index, minIndex, maxIndex):
                print "Invalid meter index."
                continue
            num = int(index)
            if not num in user_list:
                user_list.append(num)
            else:
                print "Meter already selected. Please pick a different one"

def clean_up_file_name(filename):
    """
    If FILENAME has spaces in it, replaces them with underscores. Otherwise,
    this function returns the filename unchanged.
    """

    words = filename.split()
    if len(words) > 1:
        filename = "_".join(words)
    return filename

