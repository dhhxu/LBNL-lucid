#!/usr/bin/env python

"""
Main script to get data from Lucid's website and upload it to a sMAP server.
The process is as follows:
	1. Get data query from user input
	2. Send query to Lucid and get resulting data dump
	3. Extract dumped .zip files and split them if necessary
	4. Upload .csv files into sMAP server.
"""

import get_data
import extract_data
import load_data

def main():
    """
    Main function encapsulating entire process of selecting data from Lucid
    and loading it into the sMAP server.
    """

    get_data.main()
    extract_data.main()
    load_data.main()

if __name__ == "__main__":
    main()
