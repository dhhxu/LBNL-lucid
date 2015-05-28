"""
Utility functions for the following scripts:

    get_data.py
    extract_data.py
    process_data.py
"""

import os

# Directories
cwd = os.getcwd()
DATA_PATH = os.path.join(cwd, "data")
FINISHED = os.path.join(cwd, "finished")
ARCHIVED = os.path.join(FINISHED, "archived")
INFO = os.path.join(cwd, "info")

# For get_data.py

# BuildingOS Login info
URL = 'https://buildingos.com'
USER = os.getenv('LUCIDUSER') 
PASS = os.getenv('LUCIDPASS')

DATA_WAIT_PERIOD = 15               # Refresh every 15 seconds
MAX_RETRIES = 20                    # Maximum wait time


# For load_data.py

# sMAP info
API = os.getenv('SMAPAPI')
DEST_PREFIX = os.getenv('SMAPPREFIX')

# smap-load-csv parameter values:
LINE_SKIP = 4
REPORT_DEST = DEST_PREFIX + API
TIME_FORMAT = "%Y-%m-%d %H:%M"

# The location of the map file. This file provides a 1 to 1 mapping of
# internal source name to UUID.
MAP = os.path.join(INFO, "map.csv")

