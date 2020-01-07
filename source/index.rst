.. StreamStats Data Preparation Tools documentation master file, created by
   sphinx-quickstart on Tue Oct 29 10:10:46 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to StreamStats Data Preparation Tools' documentation!
==============================================================

About
-----
The StreamStats Data Preparation Tools are meant to aid in the processing of digital elevation models (DEM) and hydrography data for ingestion into the US Geological Survey's Stream Stats application. The tools and the associated workflow examples can be used to prepare DEM and hydrography subsets for local Stream Stats folders, prepare those data for use in hydro-enforcement, hydro-enforce the digital elevation model, and processe the resulting flow accumulation and flow direction grids for use in the ArcHydro data model. 

Installation
------------
Clone these tools onto your machine using the git clone commands. Or download the the repository using the link in the upper right of the repositry page here: ***Link to repo***

Once downloaded, the data preparation ESRI ArcGIS toolbox can be accessed from the ArcCatalog pane in ArcMap or navigated to from ArcPro. The toolbox is compatable with both ArcMap and ArcPro, except for the final processing step, which relies on ArcHydro and only works with ArcMap.

The ArcGIS toolbox is build from a set of Python libraries that can be called from the command line or a scripting environment to facilitate processing large volumes of data. Please refer to the documentation of the Python libraries and the test_scripts folder for information and examples on the usage of the tools on the command line. The tools run fastest via ArcPro or Python 3, but can still be used with ArcMap and Python 2.

Citation
--------
Please cite these tools and documentation as:

Barnhart, T.B., K., Kolb, A. Rae, P. Steeves, M. Smith, and P. McCarthy, Stream Stats Data Preparation Tools, USGS Software Release, ***Citation URL Here***

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   workflow
   StreamStats_DataPrep
   modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
