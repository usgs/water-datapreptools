=======================
 Exercise 1b: TopoGrid
=======================

Original StreamStats tool development by Pete Steeves, Al Rea, and Martyn Smith

Transcribed by Kitty Kolb and Pete Steeves, August 2019

--------------
 Introduction
--------------

TopoGrid was originally created in Australia as AnuDEM. The algorithms were ingested into ESRI during the 1990s. Originally used in a command line ArcINFO environment, a Python wrapper was created in 2009. More documentation can be found at https://www.usgs.gov/core-science-systems/ngp/national-hydrography/nhd-watershed-tool 

TopoGrid enforces drainages, although it does not burn them in like HydroDEM. Enforcing is what can be referred to as a soft break-line process. It sees the stream line and says 'I'm going to massage the elevation data, to work with that location." It gets things close, but not precise. It works with the subsequent burning, because then the hard break (the burning/trenching) does not need to be as wide in search of the raster stream. And so, you get to keep much more of the local topology around the stream. If you just do burning alone, and use a small swath tolerance, sometimes the raster stream is not found and you get parallel delineation effects. In general, Topogrid is recommended to improve your DEM in relation to your hydrography. This is particularly helpful in flat terrain where the synthetic streams (derived from a DEM) tend to be relatively inaccurate in relation to the mapped streams.  Caution should be taken to mix and match resolutions, sources and scales.

*Setup*
=======

* Open a session of either ArcMap or ArcCatalog (either one will work)
* Click to run the TopoGrid script in the StreamStats Toolbox. 
* Point the tool to your workspace

.. figure:: images/topogridinputs.png
	:align: center
	:alt: sample inputs for the topo grid tool
	
	Figure: Sample inputs for the Topo Grid tool
	
* Open the Environments menu
	- Navigate to Processing Extent
	- Set the Snapping Grid to be the “dem_raw” file
	- Click “Ok” to return to the main input window

NOTE: after you process your first local folder, always navigate back to the first dem_raw file that you processed, so that the study area is consistent. 

.. figure:: images/topogridenvsettings.png
	:align: center
	:alt: sample environment settings for Topogrid
	
	Figure: Example of setting the snap raster in TopoGrid environment settings
	
* Click OK to run TopoGrid
* It will run for a long time, depending on your VIP settings and the GRIDALLOC values
