==========================================================
 Exercise 2: Setting up the Local and Global Geodatabases
==========================================================

-------------------
 Document overview
-------------------

(This exercise is run on data in the ‘global_exercise’ workspace)

Written by Al Rea and Pete Steeves, May 2010 

Updated by Kitty Kolb and Bob Ourso, July 2015 to reflect ArcGIS 10x; additional revisions by Kitty Kolb and Pete Steeves, March & July 2019

*Process Local HUC ArcHydro Geodatabases*
=========================================

The next step, which we call “Post HydroDEM Processing” goes through several steps from the Terrain Preprocessing menu of the ArcHydro Tools and the ArcHydro Python Toolbox. There are two different models in the StreamStats toolbox, one for use when you have sinks or coastlines (which are treated like sinks), and the other for when you have no coastlines or sinks in your huc. Both are provided as PDFs and handouts. Review them to see what is happening. 

Note: portions of this step have been deprecated, since the PostHydroDEM tools no longer work in ArcGIS versions later than 10.3.  The directions assume you are manually stepping through the toolbar instead of using the StreamStats Toolbox

**Introduction**
----------------

* StreamStats needs the hucpoly when you delineate to look for the local data for delineations (it uses the “NAME” attribute in the global hucpoly to do this)
* The hucpoly is like an index for the local folders
* Even if you have only frontal hucs and no global hucs, you still need to create the global geodatabase, or else it won’t know where to look for the data.
* The three layers have a relationship to each other- hucpoly, streams, huc_net_junctions

	- 99% of the time in StreamStats, you’ll be doing local delineations, but other times there are large basins that encompass multiple hucs
	- When you click on a point, it asks, “am I on the global streams layer” If yes, then knows to include upstream basins by tracing upstream on the streams layer. 
	- That relationship grabs the upstream areas and knows to include them; sets them aside. Delineates local piece of basin, then glues it to the upstream larger chunks, dissolves internal boundaries. 
	- If your study area doesn’t have upstream/downstream hucs, will be vestigial; will see things aren’t on the streams layer, but still have to have it for program to work

**StreamStats Recommended Advanced Settings and Thresholds**
------------------------------------------------------------

+-----------------------------+---------+---------+----------+---------+
| HydroDEM Advanced           | 10-m    | 30-m    | 30-ft    | 10-ft   |
| Settings	                  | DEMs    | DEMs    | DEMs     | DEMs    |
| (suggested values)          |         |         |          |         |
+=============================+=========+=========+==========+=========+
| HUC buffer (m or ft)        | 50      | 150     | 150      | 50      |
+-----------------------------+---------+---------+----------+---------+
| Inner wall buffer (m or ft) | 15      | 45      | 45       | 15      |
+-----------------------------+---------+---------+----------+---------+
| Inner wall height (cm or    | 150,000 | 150,000 | 150,000  | 150,000 |
| 100ths foot)                |         |         |          |         |
+-----------------------------+---------+---------+----------+---------+
| Outer wall height (cm or    | 300,000 | 300,000 | 300,000  | 300,000 |
| 100ths foot)                |         |         |          |         |
+-----------------------------+---------+---------+----------+---------+
| AGREE buffer (m or ft)      | 60      | 180     | 180      | 60      |
+-----------------------------+---------+---------+----------+---------+
| AGREE smooth drop (cm or    | -500    | -500    | -1500    | -500    |
| 100ths foot)                |         |         |          |         |
+-----------------------------+---------+---------+----------+---------+
| AGREE sharp drop (cm or     | -50,000 | -50,000 | -150,000 | -50,000 |
| 100ths foot)                |         |         |          |         |
+-----------------------------+---------+---------+----------+---------+
| Bowl depth (cm or 100ths    | 2000    | 2000    | 6,000    | 2000    |
| foot)                       |         |         |          |         |
+-----------------------------+---------+---------+----------+---------+

**Note:** the commas in the numbers above are for clarity. Enter the numbers in the forms without commas

+--------------+---------+--------+---------+---------+----------+-----------+
| Post         | 10-m    | 30-m   | 30-ft   | 10-ft   | Exercise | 3-m       |
| HydroDEM     | DEMs    | DEMs   | DEMs    | DEMs    | datasets | DEMs      |
| Processing   |         |        |         |         |          |           |
| Thresholds   |         |        |         |         |          |           |
| (Suggested   |         |        |         |         |          |           |
| values       |         |        |         |         |          |           |
+==============+=========+========+=========+=========+==========+===========+
| Threshold 1  | 150,000 | 50,000 | 150,000 | 450,000 | 8000     | 1,666,667 |
| (Stream      |         |        |         |         |          |           |
| initial      |         |        |         |         |          |           |
| threshold in |         |        |         |         |          |           |
| cells)       |         |        |         |         |          |           |
+--------------+---------+--------+---------+---------+----------+-----------+
| Threshold 2  | 900     | 100    | 900     | 9,688   | 900      | 10,000    |
| (Detailed    |         |        |         |         |          |           | 
| stream grid  |         |        |         |         |          |           |
| threshold in |         |        |         |         |          |           |
| cells)       |         |        |         |         |          |           |
+--------------+---------+--------+---------+---------+----------+-----------+

**Post-HydroDEM Processing**
----------------------------

*Post-HydroDEM No Sinks*
^^^^^^^^^^^^^^^^^^^^^^^^

*Kara's Method (Probably the one you should use)*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* This method was developed by Kara Watson in NJWSC
* You will need to add the ArcHydro Tools Toolbar to your display if you haven’t already 

.. figure:: images/terrainprepromini.png
	:align: center
	:alt: screen capture of the ArcHydro Tools Toolbar
	
	Figure: Screen capture of the ArcHydro Tools Toolbar

* This is the equivalent of PostHydroDem tool
* The things that you need:

	- fac or fac_global
	- fdr
	- Load them into ArcMap map document; this sets the projection of your map document

* Save this in your local folder, give it the same name as your local folder [local folder name].mxd

	- This creates a geodatabase in your local folder with the local folder name
	- Make sure that your target locations are set for the local folders: 

.. figure:: images/targetlocations.png
	:align: center
	:alt: screen capture of the set target locations menu
	
	Figure: Screen capture of the Set Target Locations menu on the ArcHydro toolbar

* Go to the Terrain Processing toolbar in ArcHydro

.. figure:: images/streamdefinitiontoolbar.png
	:align: center
	:alt: screen capture of the stream definition tool on the ArcHydro Tools Toolbar
	
	Figure: Screen capture of the location of the Stream Definition tool on the ArcHydro Tools Toolbar

* Start with the stream definition step  

	- This step makes the str grid 
	- run this twice
	- Thresholds
	
		+ Threshold 1  ---> str grid
		+ Threshold 2 ----> str900 (or equivalent) NOTE: for a table of threshold values, see the beginning of this document
		+ Yours will look something like this, although the area (square km) value may be slightly different 

.. figure:: images/str900thresholds.jpg
	:align: center
	:alt: screen capture of sample inputs for the stream definition tool
	
	Figure: Screen capture of the sample inputs for the Stream Definition tool

**Note:** Run the following steps on just the str grid:

* Stream Segmentation

	- This creates the stream link grid
	- leave sink stuff blank unless you have sinks (if you have sinks you should use the Post-Processing with Sinks workflow further down)

.. figure: images/streamsegment.png
	:align: center
	:alt: screen capture of sample inputs for the stream segmentation tool
	
	Figure: Screen capture of sample inputs for the Stream Segmentation tool

* Create the catchment grid

	- This step uses link grid strlnk from previous step 
	- This can be run from either the Toolbar or the ArcToolbox stages 
	
.. figure: images/catgridproc.png
	:align: center
	:alt: screen capture of sample inputs for the catchment grid delineation tool
	
	Figure: Screen capture of sample inputs for the Catchment Grid Delineation tool

* Catchment Polygon processing

	- This can be run from the toolbar        

.. figure: images/catpoly.png
	:align: center
	:alt: screen capture of sample inputs for the catchment polygon processing tool
	
	Figure: Screen capture of sample inputs for the Catchment Polygon Processing tool

* Drainage line processing

	- Save your map document (the program sometimes fails at this stage)
	- This can be run from either the toolbar or the AH Python Tools toolbox

* Adjoint Catchment processing

	- Save your map document again (the program sometimes fails at this stage)
	- Navigate to ArcToolbox → AH Tools Python → Terrain Preprocessing → Adjoint Catchment processing
	- Populate the fields from your layers, and take the defaults for the rest. Your option for Input Drainage Line Split Table should be blank. 
	- Note: It might tell you at the end that there are loops. I have no idea what this means. 
	- IF THIS STEP FAILS:
		+ It may give you a yellow triangle and say “general function failure” with an empty feature class for the adjoint catchments
		+ Close your ArcMap session without saving
		+ Re-enter your map document
		+ Delete the empty AdjointCatchment feature class
		+ Add a field to the Drainage Line feature class called ‘DrainID” (long integer)
		+ Run the Adjoint Catchment Processing tool from the toolbar, rather than the toolbox
		+ It should work this time

.. figure: images/adjcatproc.png
	:align: center
	:alt: screen capture of sample inputs for the adjoint catchment polygon processing tool
	
	Figure: Screen capture of sample inputs for the Adjoint Catchment Polygon Processing tool

* grids are stored in a folder called Layers

	- You can move these up one level at the end of processing to be tidy, but Pete S says this is not necessary. It bugs Kitty, so she always does it. 
	- str
	- str900
	- cat
	- strlnk

* Drainage Point Processing
	
	- This step may be vestigial, but it can’t hurt to do it. It is short. 
	- Longest Flow Path Processing occasionally asks for it, depending on your version
	- Choose Drainage Point Processing from either the AH Toolbar or the AH Python Toolbox
	- Populate the fields as follows: 

.. figure: images/drainpointproc.png
	:align: center
	:alt: screen capture of sample inputs for the drainage point processing tool
	
	Figure: Screen capture of sample inputs for the Drainage Point Processing tool

*Old Directions That No Longer Work*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1.	Start a fresh ArcMap document. (Important: Don’t just hit the “New Map Document” button. This will copy the XML setup from the currently open MXD. We want a completely fresh MXD, so you must start ArcMap from scratch. (Don’t save it yet, either. Wait till step 3 below.)
2.	Add the fdr and fac grids from the 01092222 workspace to the mxd.  Be sure to add the grids first, before anything else. This ensures the projection is set right. 
3.	Save the MXD as 01092222.mxd in the 01092222 folder. Notice in the folder that extra files appear. There will appear a 01092222.gdb folder, which is a file Geodatabase that will contain the vector layers. Also created is a 01092222.AHD file, which stores the ArcHydro Tools configuration, in XML format, plus a 01092222.xml file. (If you are having trouble in a folder, try deleting these files, including the MXD, and starting over.)
4.	Run the “F. b) Post HydroDEM.aml Processing (No Sinks)” model/tool. Be sure that you are using the appropriate grid layers for each input using the little pulldown arrow. Do NOT use the file folder browse tool to specify the grids. Set the first Threshold to 8000, the second to 900.

*Post-HydroDEM (With Sinks)*
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* To Start*
~~~~~~~~~~~

* Open a new session of ArcMap

	- Save your map document with the name of your local folder
	- Add the following files to your view:

		+ fac (or fac_global)
		+ fdr
		+ sinklink
		+ sinkpoint_edit (from input_data.gdb)

	- Note: ArcHydro will default that the output grids are stored in a folder called Layers

		+ You can move these up one level at the end of processing to be tidy, but Pete S says this is not necessary. It bugs Kitty, so she always does it. str
		+ str900
		+ cat
		+ strlnk

*Stream and Sink Combination*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Define Streams using the Stream Definition tool on the ArcHydro toolbar 

.. figure:: images/streamdefinitiontoolbar.png
	:align: center
	:alt: screen capture of the stream definition tool on the ArcHydro Tools Toolbar
	
	Figure: Screen capture of the location of the Stream Definition tool on the ArcHydro Tools Toolbar

* This is done twice for separate thresholds (stream grid versus snap grid)

	- You can find the thresholds in the table further up this document or at the bottom of Exercise 1
	- First pass → str grid       
	
		+ Note: if you have a fac_global, use fac_global instead of the fac

	- Second pass → str900 grid 
		
		+ Name this “str” plus whatever your threshold is. Your threshold may vary based on the pixel size of your application.(See table at the end of Exercise 1 for common pixel sizes)
		+ Note: if you have a fac_global, use fac_global instead of the fac		

.. figure:: images/str900thresholds.jpg
	:align: center
	:alt: screen capture of sample inputs for the stream definition tool
	
	Figure: Screen capture of the sample inputs for the Stream Definition tool

* Create a Sink Point Raster

	- Add your Sink Link Raster to the view if you haven’t already (quite possibly called “sinklink”)
	- Export or Create a copy of the Sink Link Raster to your Layers folder, and call it “sinkpntgrid”
	- Add sinkpntgrid to the map document
	- **Note:** I don’t see any difference between sinklink and sinkpntgrid, but the official ArcHydro for Stormwater instructions use sinkpntgrid instead of sinklink. I’ve used “sinklink” in place of “sinkpntgrid” and there do not seem to be any deleterious effects. 

* Delineate Sink Watersheds

	- In ArcToolbox, navigate to ArcHydro Tools Python → Terrain PreProcessing → Sink Watershed Delineation
	- Populate the input prompts with the files from your map document: 
	- Take the default for the outputs
	- It will create two layers:
		
		+ SinkWshGrid → a raster representation of the watersheds draining to the sinks
		+ Sink Watershed → a vector representation of the watersheds draining to the sinks

.. figure:: images/sinkwatershedtool.png
	:align: center
	:alt: screen capture of sample inputs for the sink watershed delineation tool
	
	Figure: Screen capture of the sample inputs for the Sink Watershed Delineation tool

.. figure:: images/streamsegmenttool.png
	:align: center
	:alt: screen capture showing the location of the stream segmentation tool on the ArcHydro toolbar
	
	Figure: Screen capture showing the location of the Stream Segmentation tool on the ArcHydro toolbar

* Choose the Stream Segmentation task from the ArcHydro Toolbar 
	
	- Populate the fields from your map document 
	- Note: use your str grid for the Stream Grid
	- It will think for a while, then say “stream segmentation successfully completed”

.. figure:: images/streamsegmentsink.png
	:align: center
	:alt: screen capture of the sample inputs for the stream segmentation tool using sinks 
	
	Figure: Screen capture of the sample inputs for the Stream Segmentation tool using sinks

.. figure:: images/combinestreamsink.png
	:align: center
	:alt: screen capture showing the location of the combine stream and sink link tool on the ArcHydro toolbar
	
	Figure: Screen capture showing the location of the Combine Stream Link and Sink Link tool on the ArcHydro toolbar

* Choose the Combine Stream Link and Sink Link tool from the ArcHydro Toolbar 

	- Verify that it has set the proper inputs
	- You may need to manually point it to the Drainage Line feature class that was just created in the last step  
	- This creates a new grid called “lnk”

.. figure:: images/combinestreamsinkinputs.png
	:align: center
	:alt: screen capture showing sample inputs for the combine stream and sink link tool
	
	Figure: Screen capture showing sample inputs for the Combine Stream Link and Sink Link tool

* Choose the Catchment Grid Delineation step from the ArcHydro Toolbar

	- The Link grid that it asks for will be the link grid you just made. 
	- Verify that the other inputs are correct (It should look like this): 

.. figure:: images/catgriddelinsink.png
	:align: center
	:alt: screen capture showing sample inputs for the catchment grid delineation for sinks tool
	
	Figure: Screen capture showing sample inputs for the Catchment Grid Delineation tool when your watershed has sinks

* Convert the Catchment grid to polygons

	- Navigate to the Catchment Polygon Processing tool in Arc Toolbox → ArcHydro Tools Python → Terrain Preprocessing
	- Choose the cat grid from the previous step. Verify that the inputs are correct:  

.. figure:: images/catpoly2.png
	:align: center
	:alt: screen capture showing sample inputs for the catchment polygon processing tool
	
	Figure: Screen capture showing sample inputs for the Catchment Polygon Processing tool

* Create the adjoint catchments

	- In ArcToolbox, navigate to the Arc Hydro Tools Python → Terrain Preprocessing → Adjoint Catchment Processing tool
	- Populate the fields with the layers that you’ve run previously 
	- The output flow split table will be empty, because you made a dendrite net(work)
	- Run the tool
	- It might tell you at the end that there are loops. I have no idea what this means. 
	
.. figure:: images/adjcatproc2.png
	:align: center
	:alt: screen capture showing sample inputs for the adjoint catchment processing tool
	
	Figure: Screen capture showing sample inputs for the Adjoint Catchment Processing tool

* IF THIS STEP (adjoint catchment) FAILS:

	- It may give you a yellow triangle and say “general function failure” with an empty feature class for the adjoint catchments
	- Close your ArcMap session
	- Re-enter your map document
	- Delete the empty AdjointCatchment feature class
	- Add a field to the Drainage Line feature class called ‘DrainID” (long integer)
	- Run the Adjoint Catchment Processing tool from the toolbar, rather than the toolbox
	- It should work this time

* Create Drainage Points

	- From the ArcToolbox → ArcHydro Tools Python → Terrain PreProcessing toolbox, run the Drainage Point Processing tool
	- Verify that the inputs are correct. 
	- Note: if you have a fac_global, use the fac_global instead of the fac

.. figure:: images/drainptproc2.png
	:align: center
	:alt: screen capture showing sample inputs for the drainage point processing tool
	
	Figure: Screen capture showing sample inputs for the Drainage Point Processing tool

**Examine your Data**
---------------------

5.	Look at the results. Do the streams900cells and DrainageLines match well with the input dendrite_edit? Look at the sinks_poly coverage. Are there large areas that were filled and flattened? Could these areas be better represented by adding some lines to the dendrite_edit, e.g. to break through a dam or some other blockage? Use the “raindrop” (Flow Path Tracing) tool to see how the HydroDEM is routing flow. Once you are satisfied, save the mxd and close ArcMap.  
6.	Open ArcCatalog.  Browse into the 0109222 workspace. Right-click on and Compact (NOT Compress) the 0109222.gdb geodatabase. 
7.	Notice the software also created a “Layers” folder, and it contains several grids. Use ArcCatalog to copy all the grids up one layer to the 01092222 folder, and then delete the Layers folder. 
8.	The other 3 HUCs can be processed in a similar manner. For 01094444, add fac_global instead of fac to the MXD, and specify that by choosing it from the pulldown list of ArcMap grid layers. 

**Run the Cleanup Workspace tool**
----------------------------------

9.	This will clean out many of the temporary data sets that were created in our processes, but not all. 
	
	- Do not delete all the temporary datasets until you feel comfortable your fdr and fac, etc, are all right. You may need to re-run hydroDEM later on and need the extra datasets. 
	- In addition, delete the spare coverages and the “nhd_scg” and “wbd_scg” grids
 
* Create the Global Geodatabase *
=================================

1.	In ArcCatalog, create a new File Geodatabase in the global_exercise folder and call it global.gdb. 

	- The folder location will be your “archydro” folder if you are running your own data 

2.	Right click on the new global geodatabase and select the New > Feature Dataset

	- Give it the name ‘Layers’.  
	= Set the coordinate system

		+ If you are using the exercise data, choose the coordinate system by selecting the “USA Contiguous Albers Equal Area Conic USGS.prj” from the Coordinate Systems>Projected Coordinate Systems>Continental>North America. 
		+ If you are working on actual data and not exercise data, use your local projection instead of USGS Albers
		+ NOTE: It is important to choose this .prj file from ESRI’s standard prj’s. DO NOT make your own projection- ALWAYS USE AN ESRI standard one

	- Default the next menu (vertical coordinate system) to none and default the last menu (tolerance settings).

* Global HucPoly *
==================

** Introduction **
------------------

* The global hucpoly is like an index. The StreamStats will check the hucpoly and the streams layers first, even if you have only frontal hucs and no global hucs. 
* The huc_net is like straws reconnecting the watersheds that HydroDEM spent all the time walling in. It tells StreamStats which upstream and downstream hucs flow into each other

** Methods of making a Global HucPoly **
----------------------------------------

Now we will start creating the layers for the global geodatabase.  We will start with the global hucpoly feature class. There are two ways of doing this:

*Blob Method (Preferred)*
^^^^^^^^^^^^^^^^^^^^^^^^^

* Open a new ArcMap.mxd and save as ‘makeglobal.mxd’ in the upper level (archydro) workspace

	- ArcHydro will automatically create a project gdb called “makeglobal.gdb”
	- Ignore this: the target for the layers you will be creating should be global.gdb

* Add the fdr from your first local workspace to act as a snap grid. This has two purposes:
	
	- Snapping to consistent origin coordinates is a critical element to building nearly all of your ArcHydro raster datasets.
	- It sets the projection for your hucpoly
	- Be VERY sure you have the right projection in your map document. 

* Using Map Algebra, create a new raster using a Con statement:

	- The statement should read (Con “fdr” ≥0, 130). You can use any number you like that is greater than 128 for the last number in the command.  
	- Name your output raster whatever you would like. We’ll call it “blob” for the purposes of this exercise
	- Save it to a scratch area 

.. figure:: images/confdrblob.png
	:align: center
	:alt: screen capture of the map algebra statement for converting the fdr grid to a blob
	
	Figure: Screen capture of the map algebra statement for converting the fdr grid to a blob

* The blob raster now has the same footprint, projection, pixel size, and snapping as your fdr grid, but is a solid blob. 

	- Use Conversion Tools → From Raster → Raster to Polygon to create a new polygon feature class representing the footprint of your watershed. 
	- You can name it whatever you like, but for this exercise we’ll call it “blob_poly.”
	- Uncheck the “simplify polygons feature class” 
	
.. figure:: images/blobrastopoly.png
	:align: center
	:alt: screen capture of sample inputs for the raster to polygon tool
	
	Figure: Screen capture of sample inputs for the Raster to Polygon tool 

* You may find that there are small dangly features hanging from the edge of your main feature in the feature class. Jennifer Sharpe suggests an equal/alternate method to open the attribute table for the feature class, where there should be only 1 record.

	- If you have more than one feature in the feature class, dissolve these into one so that there is one multipart polygon feature class. 

* Make a “blob_poly” for every local fdr in your study area. Give each one a unique identifier, like “blob_polyxxxxx.” 

* Remove the fdr and blob grids from your map document, leaving the “blob_poly” feature classes

* Merge the “blob_poly” feature classes into a single feature class within your global geodatabase called “hucpoly”.

	- Insert a text field called “Name,” and populate it with the name of each local watershed
	- Delete the “ID” and “gridcode” fields

* Check for overlaps and gaps in your hucpoly between the local footprints

	- Determine your tolerance for imperfections. If you need help performing triage on gaps, you can consult the document “If You Have Gaps in Your Data”
	- If you have small gaps of a single pixel on a ridgeline, this will probably not break StreamStats; 

		+ You may safely ignore them
		+ Unless you are a perfectionist like Kitty who breaks out into hives thinking about gaps

	- If you have gaps of more than two or three pixels on a ridgeline, you should probably fix these. 

		+ Large gaps could potentially make holes in global watersheds and users will contact the support team about it. 
	
	- If you have any overlaps these will need to be fixed unless your study area is entirely frontal hucs (every huc is an outlet huc and nothing is upstream of a huc).

		+ Overlaps will break upstream traces, channel slope, and global watersheds, as well as inflating drainage area calculations by the amount of the overlap.

* If you can’t decide what to do, please see the training document “If You Have Gaps in Your Hucpoly” for more examples. 

* Solving gaps and overlaps: 

	- Redraw your huc_8/wbd boundary to include or exclude the offending pixels 
	- Re-run the StreamStats steps for the affected local folders

		+ Depending on how severe the affected area is
		+ You may have to rerun the steps from the beginning (1a) for only that local folder
		+ You can leave the other local folders as they are if they are not affected; they do not have to go through the steps again
		+ You will need a new huc_8 boundary, a new huc_8 buffer, a new dem, a new fdr, fac, etc. Your flowlines should not have radically changed. 

* You can delete blob and blob_poly when you are done with this step

*Huc8Index Method (Old Way)*
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Open a new ArcMap.mxd and save as ‘makeglobal.mxd’ in the upper level workspace.  Add the ‘huc8index’ feature class, which can be found in the input_data geodatabase. This is the projected version of the WBD hucs. Double check to make sure it is the correct projection. 
* Add a dem or fdr from any of the local workspaces to act as a snap grid.  Snapping to consistent origin coordinates is a critical element to building nearly all of your ArcHydro raster datasets.
* In ArcToolbox, find the Conversion Tools toolbox. Under “To Raster”, start the Polygon to Raster tool. 

	- Choose huc8index from the layer pulldown for the Input Features. 
	- Choose HUC_8 for the Value field. 
	- For the output raster, this is a temporary raster, so you can let it default. (Later you will want to kill the raster.) 
	- Let the other parameters default, except set the Cell Size to 10. 
	- IMPORTANT: Before you hit OK, hit the Environments button. Expand the General Settings. Set the Extent to “Same as layer huc8index”. Select the dem layer as the Snap Raster. (If you don’t do this, the output grid cells will not align properly.)
	- Open Properties of the output raster, and verify that the extent coordinates are even multiples of 15, like all our other grids.

* In ArcToolbox, find the Conversion Tools toolbox. Under “From Raster” start the “Raster to Polygon” tool.
	
	- Choose the raster you made above as the Input raster. 
	- Choose HUC_8 as the field.
	- Set the output polygons to go into the global.mdb geodatabase we created earlier, under the “Layers” feature dataset, and named “hucpoly”.
	- Uncheck the Simplify polygons checkbox. Click OK.
	- Symbolize the hucpoly features with a hollow symbol and some colored outline. Zoom in and compare it to the original huc8index, and to some of the grids in the local workspace. It should align perfectly with the grids, but will be a jagged, raster-like representation of the WBD. 
	- NOTE: you should not have holes or overlaps in your hucpoly. 

		+ Run a topology to find overlaps and gaps between the features in your hucpoly feature class
		+ If you have large holes, you have problems and need to fill them with data. Adjust your original wbd input shapefile and start from the beginning of grid processing for that local folder 
		+ Small holes along ridgelines, etc, should be fixed in an ideal world. If you are pressed for time, you can decide whether it is a good return of your time to start over for a small area. How OCD are the users in your state? Some states have more vocal users than others. 
		+ All overlaps need to be fixed UNLESS you have a state where there are only local/outlet hucs and not global hucs, in which case you could let it slide, as long as they aren’t egregiously overlapping.  If you have upstream/downstream hucs that overlaps, this will cause massive problems if you want to do upstream tracing or longest flow path. 

*Global Streams*
================

Now let’s create the global ‘streams’ feature class. The purpose of this is like a signpost for the program to know where a delineation point is in the study area, and whether it needs to include upstream information. You have to have at least one stream in the streams feature class, even if you have an entirely frontal study area of all outlet local folders

**Outlet Trace**
----------------

* Add the 01091111/fdr and 01091111/str grids.  Turn off the fdr grid.
* Zoom into the outlet area of 01091111. 

.. figure:: images/outlet.png
	:align: center
	:alt: view of the outlet of a local processing unit with the stream grid
	
	Figure: Illustration of the outlet of a local processing unit along with its stream grid

* Select the flowpath tracing tool from the ArcHydro toolbar  

.. figure:: images/flowpathbutton.png
	:align: center
	:alt: screen capture showing the location of the flowpath tracing tool on the ArcHydor toolbar
	
	Figure: Illustration of the location of the Flow Path Tracing tool on the ArcHydro toolbar

* NOTE: the order of the following steps may be reversed, depending on which version of ArcGIS you are using
	- In the menu that pops up, specify the 01091111/fdr grid 
	- Click on a cell anywhere upstream along the 01091111/str grid (I typically select a cell at least 20 cells upstream)
	- Click OK if needed

.. figure:: images/flowtraceinput.png
	:align: center
	:alt: screen capture of the input for the flow path tracing tool
	
	Figure: Screen capture of the input for the Flow Path Tracing tool
	
* The tool will trace your fdr grid to the outlet of your local fdr with a graphic

.. figure:: images/flowtracegraphic.png
	:align: center
	:alt: screen capture showing the graphic result of the flow path tracing tool
	
	
	Figure: Screen capture showing the graphic result of the Flow Path Tracing tool

**Convert to Features (Single Streams)**
----------------------------------------

* Load the XTools Toolbar, if it isn’t already.

* Use the pointer on the Drawing toolbar to select your graphic (it will have drag handles around the selection) 

.. figure:: images/graphicselected.png
	:align: center
	:alt: screen capture showing the flow path trace graphic selected with drag handles
	
	Figure: Screen capture showing the selected Flow Path Trace graphic with the drag handles

* In Xtools Pro, go to Feature Conversions > Convert Graphics to Shapes 
	
	- Check the default box to choose the input graphics layer. 

.. figure:: images/xtoolsgraphicsshape.png
	:align: center
	:alt: screen capture of sample inputs for the XTools convert graphics to shape tool

	Figure: Screen capture of the sample inputs for the Convert Graphics to Shape tool in XTools

* Switch graphic type to polyline
* Output Feature Class →  Save as Type “Feature Class”
* Surf down to the global layers feature dataset.  Name the feature class ‘strm_1111’.  (If you are working on your own data, it should be something indicative of your local folder instead of the 1111) Click save.
* Once back in the main menu, uncheck ‘Add ID Field’ and ‘Add Text field’
* It is up to you whether you are feeling lucky/confident whether you check “Delete graphics after conversion.” .  
* Click Run.
* Remove the str and fdr grids from the legend
* Select the graphics (a line and a dot) and delete
* Repeat the above steps for 2222 and 3333. Name the outputs ‘strm_2222’ and ‘strm_3333’.  

	- Note: Most States will have some border/outlet/frontal hucs that flow out of the State and have no upstream hucs flowing into them.  
	- These won’t connect upstream and downstream

		+ You do not have to include these
		+ But it never hurts to include them 
		+ For these disconnected hucs, you will have little tiny stubs at the exit of each huc

	- If your state is all frontal/outlet hucs, you need to have at least one stub to make the geometric network

		+ StreamStats will still look for the networked streams feature class when it is delineating. 
		+ So even in a study area that is entirely frontal hucs with nothing upstream, you’ll need at least one stub to make a geometric network about. 

**Convert to Features (Multiple Streams)**
------------------------------------------

* For 4444, repeat the above steps, but run the process at the inlet cell for each of the 3 inlets (1111, 2222, and 3333).  Run all 3 Flow Path Tracing graphics before converting to polylines.  Name the output ‘strm_4444’

	- Start Editing with the global geodatabase as your target 
	- Set selectable layers to ‘strm_4444’.  
	- Select all 3 lines in Strm_4444 with the edit tool
	- Load the Topology Toolbar (if not already loaded) into your ArcMap session.  On the Topology toolbar, click the “Planarize Lines” tool to remove all the overlaps and to create nodes at the junctions. Accept the default cluster tolerance and Click ok.  Strm_4444  should now have 5 line features.

**Merging Local Streams into Global**
-------------------------------------

* Use the ArcToolBox Merge tool (under Data Management Tools →  General) to compile the 4 feature classes into 1.  Name the output ‘streams_tmp’
* The Streams segments need to be connected with small single-cell length lines at the inlet/outlet locations. (If you have only frontal hucs, this step is not necessary)

	- Start Editing with the global personal geodatabase as your target 
	- Set selectable layers to ‘streams_tmp’
	- Turn snapping on for ends
	- Zoom into the outlet of 1111. Starting at the upstream end, add a line connecting the end node outlet of 1111 with the end node inlet of  4444.  
	- Repeat for 2222 and 3333 inlets.

* Symbolize the streams_tmp layer with arrows to see if the stream lines are pointing downstream.

	- You may notice several arcs pointing upstream.  These need to be flipped.
	- Zoom into one.  In the editor toolbar, change the Task to Modify Feature.  Use the Edit tool from the editor toolbar.  Select the line that needs to be flipped.  Right click on that line and select flip
	- Repeat for other stream segments that need to be flipped downstream

* Save edits.  Quit the Editor session. 
* Now you need to create nodes at each location where the streams_tmp feature class intersects the hucpoly feature class. If you have only frontal hucs, you can skip this step and copy your streams_temp to be the main streams feature class:
	
	- In Toolbox → Analysis Tools → Overlay, select the Intersect tool
	- Input: streams_tmp, hucpoly
	- Output: streams

* Delete “streams_tmp” and the other strm_xxxx layers
* Save and close ArcMap

*Global Geometric Network*
==========================

**Initial Geometric Network Creation**
--------------------------------------

Now we will create the global geometric network **NOTE:** This will not work in ArcPro

* Open ArcCatalog
* Right click on the Layers feature dataset.  Choose New Geometric Network. Set the name to “huc_net” . Say yes to snapping and take the default      

.. figure:: images/newgeonet.png
	:align: center
	:alt: screen capture of the inputs for the geometric network creation tool
	
	Figure: Screen capture of the inputs for the Geometric Network Creation tool

* Click Next. Select ‘streams’ as the feature class for building your network.  (your options may vary based on what you’ve done so far) 

.. figure:: images/buildfeaturenewgeonet.png
	:align: center
	:alt: screen capture of the selected features for the geometric network creation tool
	
	Figure: Screen capture of the selected features for the Geometric Network Creation tool

* Answer Simple/None to complex edges.  
* You do not need to add weights to the network
* Depending on your version, it may ask you about preserving enabled values. If so, say Yes for preserving values.     

.. figure:: images/preservevalues.png
	:align: center
	:alt: screen capture of the preserve values inputs for the geometric network creation tool
	
	Figure: Screen capture of the Preserve Values inputs for the Geometric Network Creation tool

* Depending on your version, it may ask you whether you want to add weights. Say No for weights.  
* Make sure you like the inputs at the summary screen, and then click Finish 

.. figure:: images/summarygeonet.png
	:align: center
	:alt: screen capture of the input summary screen for the geometric network creation tool

	Figure: Screen capture of the Summary of Inputs screen for the Geometric Network Creation tool

* Several new layers will be added to the feature dataset:  

.. figure:: images/geonetgdbview.png
	:align: center
	:alt: view of the huc_net and huc_net_junctions files added to the feature geodatabase

	Figure: View of the new files added to the feature geodatabase

**Enabling Geometric Network**
------------------------------

* Open makeglobal.mxd. 

	- Remove all layers from the legend.  
	- Add the layers feature dataset, which adds all the feature classes.

*Assign HydroID*
^^^^^^^^^^^^^^^^

* Assign the HydroID for the portions of the network. 

	- From theArcHydro Attribute Tools pulldown menu, choose ‘Assign Hydro ID’ 
	- It will think for a moment, and then say that all HydroIDs have been assigned and give a count

.. figure:: images/assignhydroid.png
	:align: center
	:alt: screen capture indicating the location of the asign hydro id tool on the archydro toolbar
	
	Figure: Illustration of the location of the Assign HydroID tool on the ArcHydro toolbar

*Set Flow Direction*
^^^^^^^^^^^^^^^^^^^^

* From the ArcHydro Network Tools pulldown menu, choose ‘Set Flow Direction.’ 

.. figure:: images/setfdtoolbar.png
	:align: center
	:alt: screen capture indicating the location of the set flow direction tool on the archydro toolbar
	
	Figure: Illustration of the location of the Set Flow Direction tool on the ArcHydro toolbar	

* Select the streams layer and With Digitized Direction. 
	
	- Click ok.
	- It will say that it successfully completed.

.. figure:: images/setfdinputs.png
	:align: center
	:alt: screen capture showing the inputs for the set flow direction tool

	Figure: Screen capture of the inputs for the Set Flow Direction tool

*Connect Local Folder Streams*
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Add two fields to the hucpoly feature class:

	- Create a long integer field called “JunctionID”
	- Also add a 10 digit-length text field and call it “Name”

* Update the Name field for the Hucs

	- Start an editing session
	- Populate the Name field for each huc (01091111, 01092222, 01093333, and 01094444)
	- Save your edits.

* Coordinate the HydroID and JunctionID fields.

	- Still in an editing session, 
	- Turn on the Spatial Adjustment toolbar.  
	- On the Spatial Adjustment pulldown, select Attribute Transfer Mapping 

.. figure:: images/attribtxfrmapping.png
	:align: center
	:alt: screen capture indicating the location of the attribute transfer mapping dialog box on the spatial adjustment toolbar
	
	Figure: Illustration of the location of the Attribute Transfer Mapping dialog box on the Spatial Adjustment toolbar	

* For Source Layer select huc_net_junctions and HydroID from the fields
* For Target Layer select hucpoly and double click JunctionID from the fields 
	
	- Double clicking matches the fields. It won’t work unless they are both highlighted.
	- Click ok

.. figure:: images/attribtxfrinputs.png
	:align: center
	:alt: screen capture showing the inputs for the attribute transfer tool

	Figure: Screen capture of the inputs for the Attribute Transfer Mapping tool

* Next, use the Attribute Transfer Tool to link the information. 

	- Zoom in so you can see the junction where the stream intersects the border between 1111 and 4444.  
	- On the right end of the Spatial Adjustment Toolbar, select the Attribute Transfer Tool.              
	
.. figure:: images/spatadjtoolbar.png
	:align: center
	:alt: screen capture indicating the location of the attribute transfer mapping tool on the spatial adjustment toolbar
	
	Figure: Illustration of the location of the Attribute Transfer Mapping tool on the Spatial Adjustment toolbar	

* Left-click first on the junction 

.. figure:: images/spatadjjxn.png
	:align: center
	:alt: screen capture showing a highlighted huc_net_Junction point using attribute transfer mapping
	
	Figure: Screen capture showing a highlighted huc_net_Junction point using the Attribute Transfer Mapping tool

* Then left click anywhere inside the (upstream) 1111 hucpoly.  	

.. figure:: images/spatadjupstrm.png
	:align: center
	:alt: screen capture showing a line in the upstream local processing unit using attribute transfer mapping
	
	Figure: Screen capture showing the process of clicking in the upstream local processing unit using the Attribute Transfer Mapping tool
	
* Repeat this for the other 3 Hucs.  

* Open hucpoly to see that all 4 globally-connected hucpoly features now have a JunctionID and Name. 

.. figure:: images/jxnidtable.png
	:align: center
	:alt: screen capture showing a hucpoly attribute table with JunctionIds attached to features
	
	Figure: A screen capture of a HucPoly attribute table with JunctionIDs attached to features

* Save and Stop editing. Save makeglobal.mxd.  Quit out of ArcMap

*Notes*
~~~~~~~

* If your huc is an upstream Huc, then you click on the junction node for that Huc. 
* If it is a coastal/frontal Huc, last in a series of globally-connected Hucs, then click on the last node of the Huc streamline. 

.. figure:: images/spatadjcoast.png
	:align: center
	:alt: screen capture showing a line in a coastal local processing unit using attribute transfer mapping
	
	Figure: Screen capture showing the process of clicking in a coastal local processing unit using the Attribute Transfer Mapping tool

* If your Huc is a solitary Huc, not connected to other Hucs upstream or downstream, you do not need to do this process. It is theoretically possible to have a hucpoly that is almost entirely solitary hucs, as long as there is at least one streams feature somewhere in the hucpoly.  

**Relationship Class**
----------------------

* Open ArcCatalog
* Right click the global geodatabase and select “New → Relationship Class”
* Name the relationship class “HUCHasJunction”

	- Origin Table is hucpoly
	- Destination Table is huc_net_Junctions
	- Click “Next”

.. figure:: images/newrelshpinputs.png
	:align: center
	:alt: screen capture showing the inputs for the new relationship class tool

	Figure: Screen capture of the inputs for the New Relationship Class tool

* Make it a simple relationship. Click “Next.”
* Specify a label

	- From the origin table/feature class to destination: huc_net_Junctions
	- From the destination table/feature class to origin: hucpoly
	- Enter ‘none’ for message direction 

.. figure:: images/newrelshplabel.png
	:align: center
	:alt: screen capture showing the inputs for the labels tab on the new relationship class tool

	Figure: Screen capture of the inputs for the labels tab of the New Relationship Class tool

* On the next tab, select one to one cardinality
* Do not add attributes
* From the drop-down, pick Primary Key=JunctionID ; Foreign Key= HydroID  

.. figure:: images/newrelshpprimkey.png
	:align: center
	:alt: screen capture showing the inputs for the primary key tab on the new relationship class tool

	Figure: Screen capture of the inputs for the pimrary key tab of the New Relationship Class tool

* Click Next, then Finish

*Test Delineation*
==================

* Start a fresh map document in ArcMap
* Add the following layers to your map document:

	- huc_net (depending on where you are in the process, this will also add Point/Point3D, Streams/Streams3D, and huc_net_junctions)
	- hucpoly
	- Your str900 layer (or other str*** if you have a different catchment number/pixel size) 
	- Adjoint catchment and catchment features classes
	- Fac, fdr, dem grids

* Save your map document
* On the ArcHydro toolbar, select the delineate button. Either the Global or Point Delineation buttons will work, but if you want to test whether your global is working you should use the Global button. 

.. figure:: images/delinbuttons.png
	:align: center
	:alt: screen capture indicating the location of the delineation buttons on the archydro toolbar
	
	Figure: Illustration of the location of the watershed delineation buttons on the ArcHydro toolbar

* Before you can delineate with the global button, it will ask you to specify the paths to the global data folder

	- If you have already added the layers to the map, it will auto-populate for you
	- Add the navigation path to your archydro (global) folder) 
	- Click OK
	- The layer path window will disappear, but the paths are set in the background

.. figure:: images/globaldelinpaths.png
	:align: center
	:alt: screen capture of the inputs for the global point delineation tool 
	
	Figure: Screen capture of the inputs for the Global Point Delineation tool
	
* Zoom in to the area where you want to test your delineation.
* Click the Global delineation button again. 

	- It will ask you again for your path. 
	- Click OK
	- Your cursor will turn into a crosshair/plus sign
	- Click on the pixel of your str900 grid

* Your cursor will turn into a crosshair/plus sign. 
	
	- Click on the delineation point
	- AH will ask you about snapping. 
		
		+ Say Yes to snapping
		+ Snapping distance of 3 pixels 

.. figure:: images/snappoint.png
	:align: center
	:alt: screen capture of the inputs for the snap point settings
	
	Figure: Screen capture of the inputs for the snap point settings

* The click point will turn into a red dot

	- It may think for a moment
	- Your finished watershed will be a red cross-hatched area: 

.. figure:: images/tempdelin.png
	:align: center
	:alt: screen capture of the delineation output marked in red crosshatch 
	
	Figure: Screen capture of the delineation output 

* A popup will ask you if you want to save the watershed. 

	- Say yes, unless for some reason you can tell it went horribly wrong. 
	- If your delineation went horribly wrong, you may want to save it too, just to troubleshoot 

* Name the watershed something descriptive, in case you are doing multiple tests. They will be stored in the file gdb that was created when you saved your map document. The file gdb will have the same name as your map document. 

**Next Step: Do Exercise 3**