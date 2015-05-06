#!/usr/bin/env python

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
