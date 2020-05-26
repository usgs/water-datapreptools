Welcome to StreamStats Data Preparation Tools Documentation!
==============================================================

A Python toolbox to pre-process and hydro-enforce digital elevation models and hydrography features for use in the USGS StreamStats Project.

Version 3.10 tools can be accessed `here <https://code.usgs.gov/StreamStats/datapreptools/-/archive/v3.10/datapreptools-v3.10.zip>`_.

About
-----
The StreamStats Data Preparation Tools aid in the processing of digital elevation models (DEM) and hydrography data for ingestion into the US Geological Survey's StreamStats project and web-application. The tools and associated work flow examples can be used to prepare DEM and hydrography subsets for local StreamStats folders, prepare those data for use in hydro-enforcement, hydro-enforce the digital elevation model, and process the resulting flow accumulation and flow direction grids for use in the ArcHydro data model.

Citation
--------
Please cite these tools and documentation as:

Barnhart, T.B., Smith, M., Rea, A., Kolb, K., Steeves, P., and McCarthy, P. (2020). StreamStats Data Preparation Tools, version 4, USGS Software Release, https://doi.org/10.5066/P9UM2NUL.

Dependencies
------------
This toolbox has few dependencies; however, it must either be started through ArcMap or ArcPro or via a Python executable that is aware of ArcPy. These tools can be run either via their ArcToolbox wrappers or as functions via Python scripts to facilitate processing larger domains. 

ArcHydro: Use version 10.6.0.51 of ArcHydro 64-bit, available here: http://downloads.esri.com/archydro/ArcHydro/Setup/10.6/

Structure
---------
This toolbox is contained in several Python files, which will need to be installed correctly to function (see below). 

- root
	- **documentation:** Documentation of the tools and functions. Open :code:`documentation/build/html/index.html` to access.
    - **StreamStats_DataPrep.pyt:** ArcPy Toolbox wrapper file.
    - **StreamStats_DataPrep.py:** ArcPy Toolbox definition file.
    - **databaseSetup.py:** Python module for setting up the local folders for a processing domain.
    - **elevationTools.py:** Python module for inspecting DEMs, reprojection, and scaling values to integers.
    - **make_hydrodem.py:** Python module for DEM hydro-enforcement. 
    - ***.xml:** ESRI ArcPy Toolbox documentation files.
    - **examples:** Folder of Python script examples of work flows.
    - **source:** Folder containing documentation source files.

Installation
------------
Clone these tools onto your machine using the :code:`git clone` commands. Or download the the repository using the link in the upper right of the repository page here: https://code.usgs.gov/StreamStats/datapreptools

Once downloaded, the data preparation ESRI ArcGIS toolbox can be accessed from the ArcCatalog pane in ArcMap or navigated to in ArcPro. The toolbox is compatible with both ArcMap (Python 2) and ArcPro (Python 3), except for the final processing step, which relies on ArcHydro and only works with ArcMap (Python 2) at this time.

The ArcGIS toolbox is build from a set of Python libraries that can be called from the command line or a scripting environment to facilitate processing large volumes of data. Please refer to the documentation of the :ref:`modules-label` and :ref:`examples_label` for information and examples on the usage of the tools on the command line. The tools run fastest via ArcPro or Python 3, but can still be used with ArcMap and Python 2.

Documentation
-------------
Tool and function library documentation can be found by opening :code:`./documentation/build/html/index.html` with a web browser after the tools have been cloned/downloaded to your local machine.

Reporting Issues and Problems with the Tools
--------------------------------------------
Please log problems with the tools or function libraries in the issues portion of this repository. **Please do not email me.** Logging problems in this way allows other users to see the discussion and (hopefully) solution to problems. Please be sure to check out the repository documentation as well before submitting an issue.

Known Issues
------------
- **Networked storage drives:** When working on ArcGIS projects stored on NAS devices, additional configuration may be required. See:
	- https://community.spiceworks.com/topic/1389064-performance-and-locking-issues-with-synology-nas-and-arcgis
	- https://support.esri.com/en/technical-article/000012722 

Disclaimers
===========

Any use of trade, firm, or product names is for descriptive purposes only and does not imply endorsement by the U.S. Government.

This software has been approved for release by the U.S. Geological Survey (USGS). Although the software has been subjected to rigorous review, the USGS reserves the right to update the software as needed pursuant to further analysis and review. No warranty, expressed or implied, is made by the USGS or the U.S. Government as to the functionality of the software and related material nor shall the fact of release constitute any such warranty. Furthermore, the software is released on condition that neither the USGS nor the U.S. Government shall be held liable for any damages resulting from its authorized or unauthorized use.

License
=======

This work is published with the MIT Open Source License:

Copyright 2020 Theodore Barnhart, Martin Smith, Alan Rea, Katherine Kolb, Peter Steeves, and Peter McCarthy. 

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.