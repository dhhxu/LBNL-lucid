# LBNL Lucid Data Extraction

##Summary

This project extracts LBNL building energy data from Lucid's
[website](https://www.buildingos.com), processes it, and uploads it to a
sMAP [server](http://laney.lbl.gov:8000).

The energy data are in csv format, as mandated by the sMAP standard. More
information can be found at the sMAP
[wiki](https://github.com/SoftwareDefinedBuildings/smap/wiki)

###Requirements

Make sure to have these satisfied before proceeding further.

* Ubuntu 12.04
* python 2.7.x
* sMAP library ([here](https://github.com/SoftwareDefinedBuildings/smap/wiki/Installation)).

* Lucid username and password
* sMAP posting URL and API key

###Setup

Add the following lines to your `~/.bashrc` file:

      $ export LUCIDUSER='Your Lucid username'    # optional
      $ export LUCIDPASS='Your Lucid password'    # optional
      $ export SMAPPREFIX='sMAP URL prefix to upload data to'
      $ export SMAPAPI='Your sMAP API key'

###Installation

Clone the repository:

      $ git clone https://github.com:dhhxu/LBNL-lucid.git

Set up directories inside the repository:

      $ cd LBNL-lucid
      $ mkdir data
      $ mkdir finished
      $ mkdir finished/archive
      $ mkdir info
      $ touch info/map.csv

###Usage

      $ python run.py [-a]

Follow the instructions (carefully) when prompted.

The optional `-a` option automatically logs in if the `LUCIDUSER` and `LUCIDPASS`
environment variables are set correctly. Note that these environment variables
are not required for this script to work.

###Details

The `run.py` script calls three helper scripts:

1. Getting data

   `python get_data.py`

   You will be prompted to enter the indices of the meters you want data for and
   the date range of the data. The data will be downloaded as zip files in the
   `data` directory.

2. Extracting data

   `python extract_data.py`

   This will handle the extraction of the downloaded data. The resulting data
   is stored as csv files in the `finished` directory.

3. Loading data

   `python load_data.py`

   This will load the extracted data in the `finished` directory into the
   sMAP server by making calls to the `smap-load-csv` script (requires the
   sMAP library). After loading, the data is moved to the `finished/archived`
   directory.

   Note that this requires a `map.csv` file located in the `info` directory, as
   it stores the meter name - UUID mapping.

###Issues

* Updating streams

   Streams can be updated with new data, but care must be taken to ensure
   that the new data does not overlap with existing data on the server.

* Map file

   The map file is essential for tracking the meter-UUID mapping so that
   operations like updating streams can be supported.

   It currently is tracked by git, which works in the short run. In the
   long run, this file would ideally be replaced by a database.

**Last updated:** 2015-05-28
