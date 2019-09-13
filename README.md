# Stream Stats DataPrepTools
***Theodore Barnhart | tbarnhart@usgs.gov***

A Python toolbox to pre-process and hydro-enforce digital elevation models and hydrography line work for use in StreamStats.

## Dependencies
This toolbox has few dependencies; however, it must either be started through ArcMap or ArcPro or via a Python executable that is aware of arcpy. These tools can be run either via their ArcToolbox wrappers or as functions via Python scripts to facilitate processing larger domains.

## Structure
This toolbox is contained is several files, which will need to be installed correctly to function (see below). 

- root
    - StreamStats_DataPrep.pyt :: ArcPy Toolbox definition file.
    - databaseSetup.py :: Python module for setting up the local folders for a processing domain.
    - elevationTools.py :: Python module for inspecting DEMs, reprojection, and scaling values to integers.
    - make_hydrodem.py :: Python module for DEM hydro-enforcement. 
    - *.xml :: ESRI ArcPy Toolbox documentation files.
    - test_scripts :: Folder of Python scripts to test individual tools via the command line.

## Installation

On the command line, navigate to the directory you would like to clone to repository to then type: `git clone https://code.usgs.gov/StreamStats/datapreptools.git`

Then open ArcMap or ArcPro and navigate to the folder you just downloaded, the toolbox should be contained there and ready for use.

To use the Python modules and functions in scripts you will need to add the downloaded folder to your Python path, see the first two lines of each test script for examples of how to do this.

***Note:*** Tool 4E uses ArcHydroTools, these will need to be installed for this tool to function. This tool currently only functions via ArcMap / Python 2. This is the last step in the data preparation workflow.

***Note:*** When working on ArcGIS projects stored on NAS devices, additional configuration may be required. See:
- https://community.spiceworks.com/topic/1389064-performance-and-locking-issues-with-synology-nas-and-arcgis
- https://support.esri.com/en/technical-article/000012722