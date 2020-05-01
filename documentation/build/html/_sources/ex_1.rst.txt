===============================
 Exercise 1: Hydro-Enforcement
===============================

-------------------
 Document overview
-------------------

Editor's Note: This exercise is run on the data in the Exercise 1 workspace. These instructions were originally developed by Al Rea and Pete Steeves for trainings over the years. These were updated by Dave Stewart in 2011. This version annotated by Kitty Kolb and others in 2016, 2018, and 2019. Last edits made before archiving were 13 September 2019. 

*Step 0: Preparation*
=====================

**Check Equipment**
-------------------

.. figure:: images/stop.png
    :align: center
	:alt: Stop sign photo by Wendelin Jacober from Pexels
	:figclass: align-center
   
To run the StreamStats Toolbox you will need the following installed on your machine:

* ArcGIS version 10.3.x
* ArcInfo Workstation 
* ArcHydro

Without these programs installed, and *these exact versions* installed, the toolbox will not work!

**Obtain necessary data**
-------------------------

*File Structure*
^^^^^^^^^^^^^^^^

* Create four folders, all at the same level on your file directory
* They should be named

	- NED
	- WBD
	- NHD
	- archydro

* Do not nest them or give them alternate names, or else the tools will not be able to find the files when they are needed

*NED*
^^^^^

* For this exercise, 4 tiles have already been downloaded from the USGS seamless server.
* Important Notes: if you are using custom data instead of 3DEP

	- Put the elevation grids here anyhow.
	- They do not have to be named the same as 3DEP grids.
	- If they are in their own projection instead of decimal degrees, that is okay.
	- The rasters need to be stored as rasters in grid or tif format, preferably grid
	- If you store it as a Raster Dataset in a geodatabase, it will not work

*WBD*
^^^^^

*Using Exercise Data*

* Use sample HUC data file that I tweaked to match NRCS WBD Data.  

*Real-world data prep*

* If you are using official WBD for real-world (not test) data prep:

	- Use the watershed boundaries stored in the most recent NHD downloads for your study area. ← This is the preferred option
	- Or, from the NRCS Data Gateway: https://datagateway.nrcs.usda.gov/ 

		+ On the lower right-hand side, under “I Want To” click the link for “Order by state.” 
		+ Choose your state in the center of the page.  
		+ Then download the ‘12 digit Watershed Boundary Dataset 1:24,000.’ 
		+ These are updated quarterly, however. 
	
* Important Notes: If you are using your own in-house derived local boundaries

	- Save it as a shapefile to the WBD folder.
	- Make sure the fields names in your shapefile are the same as the field names for regular WBD. 
		
* Field Naming Conventions

	- You should have at least two fields in your shapefile
	
		+ HUC_8
		+ HUC_12
		
	- Note: Current naming conventions for the NHD geodatabases are “HUC8” and “HUC12” with no underscore. 
	
		+ The StreamStats tool will autopopulate the field with “HUC_8” and “HUC_12”
		+ But if yours are named other things, you just need to remember to navigate to the proper field name.
		
	- There can be other fields in the shapefile, but they are superfluous and may slow processing holding it all in memory

.. figure:: images/wbdexample1.png
	:align: center
	:alt: screen capture of an NHD geodatabase with the WBDHU12 and WBDHU8 fields circled

	Figure: Screen capture of an NHD geodatabase with relevant fields indicated 

.. figure:: images/tablehuc8.png
	:align: center
	:alt: sample table from a huc 8 feature class

	Figure: Sample table from a HUC-8 feature class
	
.. figure:: images/tablehuc12.png
	:align: center
	:alt: sample table from a huc 12 feature class
	
	Figure: Sample table from a HUC-12 feature class

* To create a WBD shapefile:

	- Using the official WBD
	
		+ Download the 4-digit NHD geodatabase from the USGS
		+ Navigate to the WBD feature class in the catalog tree
		+ If you are using HUC-12 boundaries as inwalls
		
			* Export the HUC-12 feature class to a shapefile
			* Do this for each 4-digit geodatabase in your area of study
			* Merge the exported HUC-12 shapefiles
			* Delete HUC-12s that are downstream of your region of study
			
		+ If you are taking a no-inwalls approach and using only HUC-8 boundaries (or HUC-10)
		
			* Export the feature class to a shapefile
			* Do this for each 4-digit geodatabase in your area of study
			* Merge the exported HUC-8 or HUC-10 shapefiles

				- Populate the HUC-8 and HUC-12 fields
				- Depending on which level of feature class you are using, there will be hydrologic unit fields populated as seen above: 
				- You can delete all the fields except for the HUC8 and HUC12 fields
				- Add whichever field is not included in the feature class already
				- A quick way to populate the HUC-8 field is to use a Left String Query::
				
					Left([HUC12],8) 
					
				which strips out the first 8 characters of the HUC12 code, as seen below: 

	- If you are using in-house DIY watershed boundaries
	
		+ The process and naming conventions are the same for DIY local processing unit watershed boundaries
		+ Run the feature classes through a topology check
		
			* There should be no overlaps between features
			* There should be no gaps between features
				
.. figure:: images/queryblock.png
	:align: center
	:alt: example of a field calculator window in table view

	Figure: Example of the query block in field calculator view

*NHD*
^^^^^

* From NHD prestaged 4digit in FileGDB format from the Amazon Cloud site: https://prd-tnm.s3.amazonaws.com/index.html?prefix=StagedProducts/Hydrography/NHD/ download by HUC of interest
* Important Notes: If you are using custom data instead of NHD out of the box

	- Put the NHD here anyhow, so the Toolbox will be happy. 
	
		+ You can paste your other data into the shell later.
		+ It is better if your custom data is in an NHD-like format. 
		
	- The new NHD gdb file format is named differently than the old version that the program expects. Make sure your NHD is renamed to look like this: 
	
.. figure:: images/nhdnaming.png
	:align: center
	:alt: example of properly formatted NHD geodatabases with the format NHD plus HUC 4 code 
	
	Figure: Example of properly formatted NHD geodatabases with the Format NHD plus HUC 4 code
	
*NOTE:* 
If you are using non-standard data, such as in-house LiDAR or in-house huc-boundaries, save them in same folder setup and rename them to be the same folder or file names as listed in the exercises. It is important to keep all input files together and not stored in various places on a hard drive. Otherwise the program will not be able to find the files. Many folder paths are hard-coded into the toolbox

*Step 1: Setup ArcHydro database*
=================================

**Step 1a: creating the containing folders**
--------------------------------------------

1.	If you haven’t already, create an output folder in ArcCatalog called ‘archydro’ that will house all of the resultant exercise data.  
2.	In ArcCatalog add the StreamStats v3.10 toolbox and open the toolset ‘Setup tools’ and double click ‘Database Setup’
3.	Set the Output Workspace name to the ‘archydro’ folder set above
4.	For ‘Main ArcHydro Geodatabase Name’ type in ‘source_data’ for this new file geodatabase, which will be used to house the huc feature class (generated here) and the raster catalog (generated in the ‘Second Step, NED Tools’)
5.	For ‘WBD Dataset’ select the ‘sample_wbd’ shapefile (under ‘WBD’ in the ‘exercise_data’ folder) which in this case is already projected in the final state projection of choice (otherwise the ‘WBD Dataset is already projected’ button would need to be unchecked and the ‘WBD Projection Template if unprojected’ optional menu item would need to be populated with a feature dataset or shapefile that is already in the proper projection).
6.	Be sure the HUC_8 and HUC_12 fields are set correctly for your dataset
7.	The ‘HUC Buffer Distance (m)’ should be set to 2000 (meters).  This buffer distance is used for TopoGrid processing which is trimmed back down to the HUC boundary in subsequent steps.
8.	Select the path to the NHD 4-digit High Resolution data (select ‘NHD’ under exercise_data).  You must have already downloaded all 4-digit hydro regions covering your study area
9.	Select one of your unprojected NED datasets to use as a source template for ‘NED Projection Template’ (under exercise_data\NED, enter one of the four folders and select the grid)
10.	Run the script. 

.. figure:: images/databasesetup.png
	:align: center
	:alt: view of the database setup script input
	:figclass: align-center
	
	Figure: view of the Database Setup script inputs
	
11.	Sometimes when using custom data (such as lidar-derived streams), Kitty has found that the Database Setup step will choke on the NHD portion, giving an error about “missing M values.” It is possible that M values are missing, or it is possible this is a red herring. In that case, use the “Database Setup No M Values” tool instead. 

**Step 1b: Examine the outputs**
--------------------------------

After running, open ArcMap.  Under the ‘archydro’ folder, examine the feature class outputs for one of the newly generated ‘input_data’ file geodatabases in one of the newly generated local workspaces (note the local workspaces have the name of the 8-digit HUC).  Also examine the ‘huc8index’ feature class in the new ‘source_data’ file geodatabase (also in the ‘archydro’ folder).  Compare all data to the original NED, NHD and WBD datasets.  Several observations:

* ‘NHDFlowline’ and ‘NHDFlowline_orig’ are identical line feature classes. ‘NHDFlowline' however, will be modified to your satisfaction as the input dataset for HydroDEM ‘burning’
* ‘huc8’ and ‘huc12’ datasets appear identical (the attribute tables are different).  Typically this would not be the case.  However for this exercise we are using the source huc12 features as a surrogate huc8 datasets to cut down on processing time. ‘huc8_buffer_dd83’ is used as input for the ‘Extract Polygon Area From NED’ tool which is used below (under NED Tools).
* \inwall_edit’ should have all interior WBD boundaries that will be used for ‘walling’.  

	- For the sample dataset, there is nothing for the same reason as explained in the previous bullet. 
	- This dataset could be modified at this time to include more interior boundaries such as gage boundaries
	- If you are not using inwalls in your data prep:

		+ Start an edit session on the “inwall_edit” feature class
		+ Select all features 
		+ Delete all features
		+ Save the feature class
		
* ‘huc8_buffer’ includes a 2000 meter buffer area which will be used in TopoGrid to clip the DEM data.  These buffer areas overlap.
* ‘NHDArea’ and ‘NHDWaterbody’ are used as input into bathymetric gradient processing.

**Step 1c: WBD Intersect tools**
--------------------------------

*Note:* the WBD Intersect tools have not been updated in 9 years, and we no longer support the WBD Intersect tools. 
	
*Step 2: NED Tools*
===================

**Step 2a: Make NED Index**
---------------------------

1.	In ArcCat, Run the first ‘NED Tools’ tool: ‘A. Make NED Index’
2.	‘Output Geodatabase’:  Select the ‘source_data’ file geodatabase you created with the ‘Database Setup’ tool
3.	‘Output Raster Catalog Name’: Keep the default (IndexRC)
4.	‘Coordinate System’: Import the source coordinate system (GCS_North_American_1983) using one of the source grids
5.	‘Input NED Workspace’: Select the NED folder
6.	‘Output Polygon Feature Class’: Keep the default (IndexPolys)
7.	Run the script

.. figure:: images/makenedindex.png
	:align: center
	:alt: view of the inputs for the make ned index tool
	
	Figure: Sample inputs for the Make NED Index Tool

After running, load and view the output in ArcMap (IndexPolys, IndexRC).  View the attribute tables.  Quit out of Arcmap without saving.

**Step 2b: Extract Polygon Area From NED**
------------------------------------------

8.	In ArcCat, Run the 2nd tool in the ‘NED Tools’: ‘B. Extract Polygon Area From NED’, which is run on each ‘local’ workspace in the ‘archydro’ folder.
9.	‘Output Workspace’: ‘01091111’ (in the ‘archydro’ folder)
10.	‘NED Index Polygons’: Select ‘NEDIndexPolys’ in the ‘source_data’ file geodatabase
11.	‘Clip Polygon’: Select ‘huc8_buffer2000_dd83’ in the archydro\01091111\input_data file geodatabase
12.	‘Output Grid’: Keep the default (‘dem_dd’)

.. figure:: images/extpolyarea.png
	:align: center
	:alt: view of the inputs for the extract polgyon area tool
	
	Figure: Sample of the inputs for the Extract Polygon Area tool
	
(THIS TOOL CAN BE BATCHED)

Repeat the ‘Extract Polygon Area From NED’ on the other 3 ‘local’ workspaces (01092222, 01093333 and 01094444)

After running, load and view one of the ‘local’ folder output ‘dem_dd’ grids in ArcMap (note the inclusion of the 2000 meter buffer area, which again, is needed for TopoGrid). Quit out of Arcmap without saving.

**Steps 2c & 2d: Check NoData & Fill NoData**
---------------------------------------------

Run the 3rd tool in the ‘NED Tools’: *'C. CheckNodata’* 

1. InGrid: ‘dem_dd’ (in 01091111)
2. OutPolys.shp: ‘NoDataChk’ (put in 01091111).  The output (default = C:\tmp\RasterT_Singleo<value_increment>.shp) should show up as a donut hole polygon area with no ‘GRIDCODE’ values of 1 showing up within.  If there were NODATA polys then you would either run the next tool, *‘Fill NODATA Cells’* (which replaces NODATA values in a grid with mean values within a 3x3 window) or acquire better NED data if available.
3. Repeat CheckNodata on 01092222, 01093333, and 01094444

.. figure:: images/checknodata.png
	:align: center
	:alt: view of the inputs for the check no data tool
	
	Figure: Sample inputs for the Check No Data tool

4. It is possible you may find encapsulated areas of NoData on the edge of the buffer. These are not a problem as long as they are on the outside of the buffer. If you find NoData within the buffer, that is a problem. See illustration below: 

.. figure:: images/nodatainsouts.jpg
	:align: center
	:alt: illustration of areas where nodata cells should be filled or not
	
	Figure: Sample areas where NoData cells should be filled or not.
	
**Step 2e: Project and Scale NED**
----------------------------------

In ArcCat Run the 5th tool in the ‘NED Tools’: ‘*E. Project and Scale NED*’

(this tool also sets a rounded origin coordinate for the output grid) 
  
1. Input Workspace: 01091111
2. Input Grid: Keep the default (dem_dd)
3. Output Grid: Keep the default (dem_raw)
4. Output Coordinate System: Import the coordinate system for huc8index in the ‘source_data’ file geodatabase in the archydro root folder.  The coordinate system is USA Albers USGS.
5. Output Cell Size: 10 (the projection is Albers, meters)
6. Registration Point: 
	* Original text: For all StreamStats projects, this should be left alone (15 15)
	* Updated instructions: use Registration point 0 0 unless you really know what you are doing. It will default to 15 15- change this to 0 0. 
	* Historical note: Al’s instructions are to make the registration point 15 15, because he wanted to make sure that the grids align with the NLCD. Kitty has found that using a registration point of 15 15 causes the wb_srcg and nhd_wbg grids to be shifted over half a cell. This has caused problems in Alaska and Pennsylvania. Kitty used 0 0 in NC, and everything worked out fine. The key is to be consistent throughout your state. 
	* You really only want to use registration point 15 15 if you are doing an NHDPlus implementation

.. figure:: images/projectscalened.png
	:align: center
	:alt: view of the inputs for the project and scale ned tool
	
	Figure: Sample inputs for the Project and Scale NED tool
	
(THIS TOOL CAN BE BATCHED)

Repeat ‘Project and Scale NED’ for 01092222, 01093333, and 01094444.  Note that the output zunits are in integer centimeters (the input was in floating point meters). Also note that the output ‘dem_raw’ grid includes a line in the projection file ‘ZUNITS 100’.  This custom (non-default) value is needed by several basin characteristics, including basin slope, since the Z value (centimeters) is different from the XY values (meters).  Otherwise basin slope would be exaggerated 100 times.

*Step 3: Editing NHD*
=====================

**Preliminary Notes**
---------------------

*Note about BYOD*
^^^^^^^^^^^^^^^^^

NOTE: If you are bringing your own data to the tools and not using the NHDFlowlines, this is the step where you delete the NHD-derived Flowlines and substitute your own stream lines in the “input_data” geodatabase. (See further below for instructions.) Make sure you name your feature class “NHDFlowlines,” however. 

*Note about Editing Instructions*
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The instructions that follow are a summarized overview of the editing process on data that originated in the NHD and are mostly clean. If you are working on your own data, or would like instructions that cover almost any contingency in excruciating detail with screen-captured examples from the South Carolina LiDAR data prep, you may wish to consult the document “SC StreamStats Linework Review Workflow”. 

**Exercise Instructions**
-------------------------

* Open ArcMap.  
* Navigate to the 01091111 folder and add the features in the ‘input_data’ file geodatabase.  
* Turn all layers off except ‘huc8’ and ‘NHDFlowline’.
* Under ‘File’ select ‘Add Data from ArcGIS online’.   

	- Load the ‘US Topo Maps’ and ‘World Imagery’ web services to your view.  
	- Turn these layers off for now (they slow things down).
	
* Observe the stream overlapping the Northern boundary of the huc.  

	- This is problematic.  
	- Although the streamline represents flow in a wetland, the wetland straddles the boundary and flows in 2 directions (entering and exiting the huc).  
	- Zoom into this general area and turn on the topo image. 
	
		+ There is another issue. A small disconnect just South of the letter ‘D’ in ‘Dead Swamp’. 
		+ This gap is so narrow, if HydroDEM were to be run, the resulting flow accumulation would hop across the gap.  
		+ There are many other reasons to clean up an NHD dataset, but for this exercise, we need to address this one now.  
		
	- Start an edit session on the ‘input_data’ file geodatabase.
	
		+ Choose ‘NHDFlowline’ as your target layer.  
		+ Select the flowline in the swamp and delete it.  Save your edit.
		
* Turn the topo image off and zoom back out to the extent of the huc8.  

	- The flow in the basin is generally North to South, with the outlet at the Southern- most point of the HUC.  
	- Note near the outlet, there is a disconnect in the flow.  
	- Zoom to this location and bring up the World imagery. 
	- This disconnect is likely an underground conduit connecting the reservoir to the stream on the South side of the major road.  
	
* Let’s correct the problem.

	- The target layer remains ‘NHDFlowline
	- Set ‘NHDFlowline’ Snapping to ‘End’
	- Digitize in a connector line in the direction of flow (North/South)
	- Save Edits
	
* Remove all layers from the Table of Contents
* Add all layers in the local 0109444 input_data gdb
* Turn all layers off and turn back on ‘huc8’ and ‘NHDFlowline’
* Zoom to ‘huc8’

	- This is the receiving HUC for the other 3 local HUCs.  
	- Observe the 3 locations where those 3 upstream HUCs flow into this one.  
	- Zoom into one of these locations

* The ‘NHDFlowline’ feature class is eventually used in the burning process.  

	- Any feature in this dataset that is an inlet for a downstream HUC needs to be trimmed just inside the HUC.  
	- Otherwise, the ‘walling’ process can get compromised at the boundary edge.  
	- This trimming should only be a cell or 2 in length (10 – 20 meters).

* In the Editor toolbar, choose  Start Editing

	- Target: ‘NHDFlowline’
	- Select the feature that overlaps the boundary.  
	- Measure a distance
	- Split the feature
	- Delete the segment
	- Repeat this for the other 2 inlet features
	- Save and Stop editing
	- Quit out of ArcMap without saving

Note: There will typically be other edits to review for both the NHD and WBD.  This is why we isolate an edit-able copy for both (‘NHDFlowline’ and ‘inwall_edit’). Also, for ‘NHDFlowline’ it may be helpful to occasionally reestablish a geometric network to check flow connectivity.  The best tools to do this are typically NHD tools or the ArcGIS Utility Network tools, but to use the NHD tools,  the feature class name typically needs to be ‘NHDFlowline’ and this dataset typically needs to be in a ‘Hydrography’ feature dataset.  Some manipulation of the ‘NHDFlowline’ feature class (including temporarily loading into a separate geodatabase) may be necessary. Instructions on the NHD Tools can be found here: (outdated link)	

**BYOD Streamline Editing Instructions**
----------------------------------------

* If you are bringing local data:

	- Buffer your local processing unit (LPU, usually a huc8, but can be something else) boundary by X amount (usually 2 kilometers/2000 m)
	- Clip out the local data-equivalent feature classes to the NHDFlowline, NHDArea, and NHDWaterbody using the buffer 
	- Add your local data equivalent buffer-clipped feature classes to your table of contents for the project
	- Start an edit session on the LPU input_data.gdb.
	
		+ Open the table for NHDFlowline (not NHDFlowline_orig)
		+ Select all records in input_data\NHDFlowline
		+ Delete the selected records.
		+ Save the edit session, but do not stop the edit session
		
	- Select all the records in the local equivalent NHDFlowline_clipped_buffer feature class
	- On the File status bar, got to Edit → Copy (do not do “copy selected records”, this will not work)
	- Go to Edit → Paste
	
		+ A window will open saying “Paste selected records into”
		+ Choose the newly-empty NHDFlowline feature class
		+ Click okay.

	- Save the edit session, stop the edit session

* Follow the editing instructions as above

	- Remove braids

		+ Use the Feature to Polygon tool to find areas that are braids
		+ Zoom to each polygon to snip segments as necessary
		+ When in doubt:
		
			* Follow the named stream/river
			* Unless it is clearly much more flow on the map, and then you should contact the NHD stewardship team to get the named segment moved to another channel. 

	- Do a topology check to make sure there are not two flowlines on top of each other
	- Do a geometric network check to make sure there are no disconnected segments and that streamlines are flowing in the correct direction

		+ Flip streamline segments as needed
		+ Connect disconnected segments as needed
		+ You will never get 100 %, but do the best you can

	- Recheck for loops/braids accidentally created by connecting segments.
	
*Step 4: NHD-WBD Conflicts*
===========================

**Overview**
------------

The StreamStats Tools break the WBD shapefile into two polygon feature classes: huc12 and huc8. The huc12 features and/or streamgage basin boundaries are often used as the inner walls in the “walling” process. The huc8 polygons are used as the outer walls. Each huc12 and huc8 polygon should only have a single outlet.

Occasionally, the stream lines and the WBD lines intersect in places they shouldn’t or the 2 lines come very close to each other and could create an unwanted breach in an inner or outer wall.  Locations where the 2 feature classes intersect should be identified. They need to be visually examined and sometimes corrected. Most of the time, the WBD boundary is adjusted. Sometimes, the stream can be shifted slightly or snipped. This falls into the “Know your data” category of judgement calls; resources such as imagery, LiDAR breaklines, and local knowledge can help you determine which one to remove. If you are changing the WBD, in ideal circumstances you should also coordinate with the WBD stewards to make sure that your changes are in concert with them. This may not always be feasible due to time-constraints. 

Here is an example of an area that needs close inspection: 

.. figure:: images/laboundarycross.png
	:align: center
	:alt: illustration of a place in Louisiana where a stream crosses a HUC boundary
	
	Figure: Example of a place in Louisiana where a stream crosses a HUC boundary

**Workflow**
------------

* Remove clearly outside streamlines

	- Start an edit session
	- Select all features in NHDFlowline that intersect the local processing unit (LPU) feature class (probably called huc8 in the input_data.gdb)
	- Switch selection

		+ This will show you streamlines that are outside the LPU
		+ And are probably flowing away
		+ But do a spot check on a few just to make sure
		+ If there are a lot flowing into your LPU from outside, your LPU boundary may need adjusting.

	- Delete the clearly-external streamlines

* Examine streamlines that cross the boundary

	- Only one streamline (the outlet) should cross the LPU boundary 

		+ Leave this one alone
		+ It should extend multiple pixels’-worth beyond the LPU boundary
		+ If you omit this step, your LPU will fill up like a bathtub during the HydroDEM process and look really trippy

	- All the others need to be dealt with

		+ As you find them consider:

			* Is this a genuine stream that I need to re-draw my LPU boundary?
			* Is this a canal (and I can safely delete it)?

		+ Trim the initiation part of streamlines crossing the boundary to at least several pixels’-worth from the boundary

	- If you omit this step, water will leak out the edges of your LPU

* NHD-WBD Intersect Tool: this section is no longer supported by the toolbox

**TopoGrid**
------------

If you are going to run TopoGrid, please refer to the instructions in exercise 1b: TopoGrid

*Step 5: Toolbox 4. HydroDEM Tools*
===================================

Kitty’s Note: If you are using data that is not either 30 ft or 10 m data, use the second Bathymetric Tool, called “Bathymetric Gradient Setup for 30m States.” The usual script checks the data for conformance to the 30 ft/10m standard, and will fail on any other conditions. The second version was created by Bob Ourso to use on Alaska (30m) data, but modified to accept anything by Kitty for SC (10ft) data. Bob and I “jailbreaked” the script to accept any size pixels.

**A. Bathymetric Gradient Setup from ArcCat**
---------------------------------------------

1. Run ‘Bathymetric Gradient Setup’ on a local HUC to prepare 2 grids for the HydroDEM program
2. Set the ‘Output Workspace’ to the local HUC workspace (01091111)
3. Set the ‘DEM’ grid 

	* Normally you would use ‘dem_raw’ here.
	* If you used TopoGrid, use the TopoGrid output dem here (usually called “topogr_gr”)

4. Set the ‘Dissolved HUC8 Dataset’ to ‘huc8’
5. Set the NHDArea to the same name in the source NHD feature dataset (under the ‘input_data’ file geodatabase). 
6. Set the NHDFlowline to ‘NHDFlowline’. (NOTE: Do NOT use NHDFlowline_orig from the NHD here. You want the version you edited.) 
7. Set the NHDWaterbody to the same name in the source NHD feature dataset (under the ‘input_data’ file geodatabase). 
8. Set the NHDFlowline Selection Buffer to 5 meters (default)
9. Ensure the Checkbox for ‘NHD Data already projected’ is checked
10. Click OK

*Two grids are created: wb_srcg (waterbody areas) and nhd_wbg (flowline cells).*

.. figure:: images/bathgradsetup.png
	:align: center
	:alt: view of the inputs for the bathymetric gradient setup tool
	
	Figure: Sample inputs for the Bathymetric Gradient Setup tool

Enter ArcMap and view these grids in context with the source NHD.  Quit out of ArcMap without saving. (NOTE: When you are working on your own data, you may see cases in which the NHDWaterbody or NHDArea may need to be edited in order to prevent imposing a gradient on areas that shouldn’t be done. This would be quite rare, but if you do see this, copy the feature class to an “edit” one like we have done for NHDFlowline and inwall_edit, so you will know there have been edits. Then use the edited feature classes as inputs to this tool, i.e. in steps 1d and/or 1f above.)

Repeat ‘Bathymetric Gradient Setup’ for 01092222, 01093333, and 01094444

**B. Coastal Processing**
-------------------------

* (Exercises Note: These are not coastal hucs, so we are skipping the Coastal Processing step. Otherwise we will need to do coastal processing.  ) 
* Create a polygon feature class that covers the entire footprint of your local folder study area (huc-8 or equivalent)

	- Call it “LandSea”
	- Add an integer field called Land
	- Divide your foot print by categories of land/sea/other

		+ Sources for this could be NHDWaterbodies, Coastline, local lidar shoreline features

	- There will be three categories of features in your feature class

		+ Sea or ocean

			* Value = -1
			* This will be lowered to the Sea Level specified in the tool field

		+ Areas on land that are truly below sea level (such as a quarry, Death Valley, etc)

			* Value = 0
			* This will not be changed by the tool

		+ Land areas that are above sea level

			* Value = 1
			* Any cells in these areas with elevation of 0 or lower will be raised to 1 

* The tool will create a dem called “dem_sea”

	- This will be used as the input dem for PreHydroDEM
	- If you used Topogrid, input TopoGrid
	- If you didn’t use Topogrid, use dem_raw

**C. Pre HydroDEM Processing from ArcCat**
------------------------------------------
Run the ‘Pre HydroDEM Processing’ tool to create the input coverages for HydroDEM (from the source file geodatabases), and define the input DEM as either the raw DEM (‘dem_raw’).  The chosen DEM will be copied and named ‘dem’

1. Output Workspace: select the ‘01091111’ workspace
2. Dissolved HUC8 Dataset: ‘huc8’ (in the ‘input_data’ gdb
3. Dendritic NHD Dataset: ‘NHDFlowline’
4. Inner Wall Dataset: ‘inwall_edit’ 
5. DEM to be used in HydroDEM: 
	
	* If you did Coastal Processing, use dem_sea 
	* If you skipped Coastal Processing:
		
		- Use ‘dem_raw’ if you didn’t use TopoGrid
		- Use topogr_gr if you ran TopoGrid

6. Sink Points Dataset (optional): leave blank
7.	Run the program (‘OK’)

Run the remaining 3 HUCs through ‘Pre HydroDEM Processing’ (the ‘Sink Points Dataset (optional)’ menu item will be left blank for all three).

*Grids Created: dem*

*Coverages Created: huc8, inwall, nhdrch*

.. figure:: images/prehydrodem.png
	:align: center
	:alt: example of the inputs for the pre hydrodem processing tool
	
	Figure: Sample inputs for the Pre-HydroDEM Processing tool
	
**D. Run HydroDEM.aml from ArcMap**
-----------------------------------

Make sure the directory is refreshed and not being accessed by any ArcMap or Windows Explorer window.  It may make sense to close ArcCatalog before you run step D and open it later after HydroDem is over if you need it again. 
 
Run the ‘HydroDEM.aml’ tool on 01091111 (the remaining 3 will be run in batch mode, but here we get to showcase the “validation code” for Python scripts, which populates fields > a thanks to Curtis Price for this code. You can see the code on the Validation tab if you right-click on the script in ArcToolbox and go to Properties.)

Output Workspace: select the ‘01091111’ workspace

The remaining fields (including the optional ‘Drain plug coverage’ field) are populated!

NOTE: 

* if you used the Coastal adjustments, change the DEM to be Used in HydroDem field to the dem output from the Coastal adjustment. 
* If you used TopoGrid, you are okay, because the PreHydroDEM should have copied your topogr_gr raster to be the “dem” raster that RunHydroDEM is looking for
* copy the snapgrid into the huc folder, and set that as the Snapgrid, instead of the one that is auto populated
* Click OK
* View results in ArcMap.  Drape the NHDFlowline feature class and drain_plugs polygon layer on top of the fac grid.  Scan around.  
* examine the dem_enforced and zoom back to the nhd_inwall_intersect areas that were edited.  make sure the inwalls only have one outlet for each stream. 
* Quit out of ArcMap without saving
* Run the ‘HydroDEM.aml’ tool in batch mode for the other 3 HUCs
* Right click the tool and select ‘Batch’
* In the empty ‘Output Workspace’ field, right click and select ‘Browse’
* Hilite all the remaining 3 HUC folders and select ‘Add’
* Back in the batch window, with the 3 newly populated rows (for ‘Output Workspace’) selected, click the check values check box on the right.  All other fields are populated!
* Click OK to run the batch process
* View some results in ArcMap.  Quit out of ArcMap without saving

Grids Created in HUC folder: buffg, dem_enforced, dem_ridge8, dem_ridge8wbd, elevgrid, eucd, fac, fdr, fil, inwallg, inwallg_tmp, nhdgrd, ridge_exp, ridge_nl, ridge_w 

.. figure:: images/runhydrodem.png	
	:align: center
	:alt: sample inputs for the RunHydroDEM.aml tool
	
	Figure: Sample inputs for the RunHydroDEM.aml tool

NOTE: the results will contain some very strange looking stuff, this is normal.

.. figure:: images/hydrodeminprogress.png
	:align: center
	:alt: sample output of the HydroDEM process
	
	Figure: Sample outputs of the HydroDEM process
	
**E. Flow Accumulation Adjust (Need this when joining globals)**
----------------------------------------------------------------

*Overview*
^^^^^^^^^^

Flow Accumulation needs to be adjusted at the inlets of downstream HUCs to account for the flow coming into the HUC (which needs to be recognized for the ArcHydro tools to work correctly). By default, local DEM derivatives like flow accumulation stand alone and do not recognize incoming flow. This tool adjusts for incoming flow.

*Regular Flow Accum Adjust*
^^^^^^^^^^^^^^^^^^^^^^^^^^^

*Workflow*

* Open the ‘Flow Accum Adjust’ tool
* Downstream (receiving FAC):  Add in the FAC (flow accumulation) grid under 01094444 (which is the only receiving HUC in this exercise)
* Upstream FAC(s):  Add in each of the three upstream FAC grids by surfing into each local workspace
* Click OK
* Open ArcMap and view the results.  

	- Load the new ‘fac_global’ for 01094444 
	- Compare to the original ‘fac’
	- There should be a lighter area where the upstream flow enters now
	
*Troubleshooting*

* Sometimes this process will fail when connecting multiple upstream facs to one downstream receiving fac, or the values being connected are very large. If this happens, update the downstream/receiving fac iteratively, such as

	- Fac 1 → Fac 4
	- Fac 2 → Fac 4b
	- Fac 3 → Fac 4c
	- etc
* If this still doesn’t work, you can use the simple flow accum adjust tool

*Simple Flow Accum Adjust*
^^^^^^^^^^^^^^^^^^^^^^^^^^

* If you are using the simple adjust, make sure the dot is on the first raster cell where things come in

**F. b) Post HydroDEM Processing**

See Exercise 2 for these directions

*StreamStats Recommended Advanced Settings and Thresholds*
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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