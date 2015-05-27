#!/usr/bin/env python

"""
Main script to get data from Lucid's website and upload it to a sMAP server.
The process is as follows:
	1. Get data query from user input
	2. Send query to Lucid and get resulting data dump
	3. Extract dumped .zip files and split them if necessary
	4. Upload .csv files into sMAP server.
"""

import argparse

import get_data
import extract_data
import load_data

def epilog():
	"""
	Returns the text that is displayed after the argument help.
	"""

	string =  "Default behavior without arguments is to obtain login\n"
	string += "credentials from environment variables."
	return string

def main():
    """
    Main function encapsulating entire process of selecting data from Lucid
    and loading it into the sMAP server.
    """

    parser = argparse.ArgumentParser(epilog=epilog())
    parser.add_argument("-u", "--user", help="Prompt for username and password",
    	action="store_true")
    args = parser.parse_args()

    if args.user:
    	get_data.main(True)
    else:
    	get_data.main(False)
    
	extract_data.main()
	load_data.main()

if __name__ == "__main__":
    main()
