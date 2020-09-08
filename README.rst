Welcome to StreamStats Data Preparation Tools Documentation!
==============================================================

A Python package to pre-process and hydro-enforce digital elevation models using hydrography features for use in the U.S. Geological Survey (USGS) StreamStats project.

Legacy version 3.10 tools can be accessed `here <https://github.com/usgs/water-datapreptools/archive/v3.10.zip>`_. See below for installation instructions for version 4 tools.

About
-----
The StreamStats Data Preparation Tools aid in the processing of digital elevation models (DEMs) and hydrography data for ingestion into the USGS StreamStats project and web-application. The tools and associated work flow examples can be used to prepare DEM and hydrography subsets for local StreamStats folders, prepare those data for use in hydro-enforcement, hydro-enforce the digital elevation model, and process the resulting flow accumulation and flow direction grids for use in the ESRI ArcHydro data model.

Documentation
-------------
Tool and function library documentation can be found by opening https://usgs.github.io/water-datapreptools/.

Citation
--------
Please cite these tools and documentation as:

Barnhart, T.B., Smith, M., Rea, A., Kolb, K., Steeves, P., and McCarthy, P., 2020, StreamStats Data Preparation Tools, version 4: USGS Software Release, https://doi.org/10.5066/P9UM2NUL.

Version 4 (IP-112997) was approved on September 3, 2020.

Dependencies
------------
This toolbox has few dependencies; however, it must either be started through ESRI ArcMap 10.6.1 or ESRI ArcPro 2.5.1 or via a Python 2 or 3 executable that is aware of ESRI ArcPy. These tools can be run either via their ESRI ArcToolbox wrappers or as functions via Python scripts to facilitate processing of larger domains. 

The :py:func:`post-hydrodem` function requires ESRI ArcHydro. Please use version 10.6.0.51 of ESRI ArcHydro 64-bit or greater, available here: http://downloads.esri.com/archydro/ArcHydro/Setup/10.6/

Structure
---------
This package is contained in several Python files, which will need to be installed correctly to function (see below). 

- root
	- **documentation:** Documentation of the tools and functions. Open ``documentation/build/html/index.html`` to access.
    - **StreamStats_DataPrep.pyt:** ESRI ArcPy Toolbox wrapper file.
    - **StreamStats_DataPrep.py:** ESRI ArcPy Toolbox definition file.
    - **databaseSetup.py:** Python module for setting up the local folders for a processing domain.
    - **elevationTools.py:** Python module for inspecting DEMs, reprojection, and scaling values to integers.
    - **make_hydrodem.py:** Python module for DEM hydro-enforcement. 
    - ***.xml:** ESRI ArcPy Toolbox documentation files.
    - **examples:** Folder of Python script examples of workflows.
    - **source:** Folder containing documentation source files.

Installation
------------
Clone these tools onto your machine using the :code:`git clone https://github.com/usgs/water-datapreptools.git` command. Or download the repository using the link in the upper right of the repository page here: https://github.com/usgs/water-datapreptools

Once downloaded, the data preparation ESRI ArcGIS toolbox can be accessed from the ArcCatalog pane in ESRI ArcMap or navigated to in ESRI ArcPro. The toolbox is compatible with both ESRI ArcMap (i.e. Python 2) and ESRI ArcPro (i.e. Python 3), except for the final processing step, Post Hydrodem, which relies on ESRI ArcHydro and only works with ESRI ArcMap (Python 2) at this time (2020) due to ESRI ArcHydro compatibility issues with ESRI ArcPro (i.e. Python 3).

The ESRI ArcGIS toolbox is built from a set of Python libraries that can be called from the command line or a scripting environment to facilitate processing large volumes of data. Please refer to the documentation of the :ref:`modules-label` and :ref:`examples_label` for information and examples on the usage of the tools on the command line. The tools run fastest via ESRI ArcPro or Python 3 (see caveat above), but can still be used with ESRI ArcMap and Python 2.

Reporting Issues and Problems with the Tools
--------------------------------------------
Please log problems with the tools or function libraries in the `issues portion <https://code.usgs.gov/StreamStats/datapreptools/-/issues>`_ of this repository. **Please do not email me.** Logging problems in this way allows other users to see the discussion and, hopefully, the solution to problems. Please be sure to check out the repository documentation as well before submitting an issue.

Known Issues
------------
- **Networked storage drives:** When working on ESRI ArcGIS projects stored on network Attached Storage (NAS) devices, additional configuration may be required. See:
	- https://community.spiceworks.com/topic/1389064-performance-and-locking-issues-with-synology-nas-and-arcgis
	- https://support.esri.com/en/technical-article/000012722

Acknowledgments
--------------- 
The authors thank Moon Kim (USGS) for his comments on an early version of this code and Tara Gross (USGS) for her software release reviews.

Disclaimers
-----------

Any use of trade, firm, or product names is for descriptive purposes only and does not imply endorsement by the U.S. Government.

Please see DISCLAIMER.md in this repository.

License
-------

Please see LICENSE.md in this repository.
