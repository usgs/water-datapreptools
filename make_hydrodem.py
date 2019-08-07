'''
Code to replicate the hydroDEM_work_mod.aml, agree.aml, and fill.aml scripts

Theodore Barnhart, tbarnhart@usgs.gov, 20190225

Reference: agree.aml
	
'''
import numpy as np
import arcpy
arcpy.CheckOutExtension("Spatial")
import sys
import os
from arcpy.sa import *
import time

def SnapExtent(lExtent, lRaster):
	'''Returns a given extent snapped to the passed raster.

	Parameters
	----------
	lExtent : str
		ESRI Arcpy extent string

	lRaster : str
		Path to raster dataset

	Returns
	-------
	extent : str
		ESRI ArcPy extent string
	'''
	pExtent = lExtent.split()
	extent = lExtent
	
	lt = ["rasterdataset","rasterband"]
	dsc = arcpy.Describe(lRaster)
	if dsc.DatasetType.lower() in lt:
		iCell = dsc.MeanCellWidth
		xmin = round(float(pExtent[0]) / iCell) * iCell
		ymin = round(float(pExtent[1]) / iCell) * iCell
		xmax = round(float(pExtent[2]) / iCell) * iCell 
		ymax = round(float(pExtent[3]) / iCell) * iCell 
		extent = str(xmin) + " " + str(ymin) + " " + str(xmax) + " " + str(ymax)

	return extent

def bathymetricGradient(workspace, snapGrid, hucPoly, hydrographyArea, hydrographyFlowline, hydrographyWaterbody,cellsize, version = None):
	'''Generates the input datasets for enforcing a bathymetic gradient in hydroDEM (bowling).
	
	Originally:
		ssbowling.py
		Created on: Wed Jan 31 2007 01:16:48 PM
		Author:  Martyn Smith
		USGS New York Water Science Center Troy, NY
	
	Updated to Arcpy, 20190222, Theodore Barnhart, tbarnhart@usgs.gov

	This script takes a set of NHD Hydrography Datasets, extracts the appropriate
	features and converts them to rasters for the Bathymetric Gradient (bowling) inputs to HydroDEM
	
	Parameters
	----------
	workspace : str

	snapGrid : str

	hucPoly : str

	hydrographyArea : str

	hydrographyFlowline : str

	hydrographyWaterbody : str

	cellsize : str

	version : str
		Package version number

	Returns
	-------
	
	'''
	if version:
		arcpy.AddMessage('StreamStats Data Preparation Tools version: %s'%(version))

	arcpy.env.overwriteOutput = True # Set script to overwrite if files exist
	arcpy.AddMessage("Starting Bathymetric Gradient Preparations....")

	# Set the Geoprocessing environment...
	arcpy.env.scratchWorkspace = workspace
	arcpy.env.workspace = workspace

	# Setup local variables and temporary layer files
	arcpy.AddMessage("Setting up variables...")

	#temporary features
	nhd_flow_feat = "nhd_flow"
	nhd_flow_Layer = "nhd_flow_Layer"

	nhd_area_feat = "nhd_area"
	nhd_area_Layer = "nhd_area_Layer"

	nhd_wb_feat = "nhd_wb"
	nhd_wb_Layer = "nhd_wb_Layer"

	#Output rastsers
	wbtempraster = os.path.join(arcpy.env.workspace,"nhdwb_tmp")
	areatempraster = os.path.join(arcpy.env.workspace,"nhdarea_tmp")
	mosaiclist = wbtempraster + ";" + areatempraster
	outraster1 = "wb_srcg"
	outraster2 = "nhd_wbg"

	#convert to temporary shapefiles
	arcpy.FeatureClassToFeatureClass_conversion(hydrographyArea, arcpy.env.workspace, nhd_area_feat)
	arcpy.AddField_management(nhd_area_feat,"dummy","SHORT",None,None,None,None,"NULLABLE","NON_REQUIRED",None)
	arcpy.CalculateField_management(nhd_area_feat,"dummy","1", "PYTHON")

	arcpy.FeatureClassToFeatureClass_conversion(hydrographyWaterbody, arcpy.env.workspace, nhd_wb_feat)
	arcpy.AddField_management(nhd_wb_feat,"dummy","SHORT",None,None,None,None,"NULLABLE","NON_REQUIRED",None)
	arcpy.CalculateField_management(nhd_wb_feat,"dummy","1", "PYTHON")

	arcpy.FeatureClassToFeatureClass_conversion(hydrographyFlowline, arcpy.env.workspace, nhd_flow_feat)
	arcpy.AddField_management(nhd_flow_feat,"dummy","SHORT",None,None,None,None,"NULLABLE","NON_REQUIRED",None)
	arcpy.CalculateField_management(nhd_flow_feat,"dummy","1", "PYTHON")

	try:
		#hydrographyArea Processing
		arcpy.AddMessage("Creating temporary selection layers...")
		arcpy.MakeFeatureLayer_management(nhd_area_feat, nhd_area_Layer, "FType = 460", "", "")
		
		#hydrographyWaterbody Processing
		arcpy.MakeFeatureLayer_management(nhd_wb_feat, nhd_wb_Layer, "FType = 390 OR FType = 361", "", "")
		
		#hydrographyFlowline Processing
		arcpy.MakeFeatureLayer_management(nhd_flow_feat, nhd_flow_Layer, "", "", "")
		arcpy.SelectLayerByLocation_management(nhd_flow_Layer, "WITHIN", nhd_wb_Layer, "", "NEW_SELECTION")
		arcpy.SelectLayerByLocation_management(nhd_flow_Layer, "WITHIN", nhd_area_Layer, "", "ADD_TO_SELECTION")
	except:
		arcpy.AddMessage(arcpy.GetMessages())

	#get snap grid cell size
	dsc_snap = arcpy.Describe(snapGrid)
	snap_cellsize = dsc_snap.MeanCellWidth

	# Set raster processing parameters
	arcpy.AddMessage("Processing rasters...")
	dsc = arcpy.Describe(hucPoly)
	extent = str(dsc.extent)
	arcpy.env.cellSize = snap_cellsize
	arcpy.env.mask = snapGrid
	arcpy.env.extent = SnapExtent(extent, snapGrid)

	# Process: Feature to Raster1 - NHD Area...
	try:
		arcpy.SelectLayerByLocation_management(nhd_area_Layer, "INTERSECT", nhd_flow_Layer, "0", "NEW_SELECTION")
		arcpy.FeatureToRaster_conversion(nhd_area_Layer, "dummy", areatempraster, cellsize)      
	except:
		arcpy.CreateRasterDataset_management(arcpy.env.workspace,"nhdarea_tmp","10","8_BIT_UNSIGNED",snapGrid)
		arcpy.AddMessage(arcpy.GetMessages())
		
	# Process: Feature to Raster2 - NHD Waterbody...
	try:
		arcpy.SelectLayerByLocation_management(nhd_wb_Layer, "INTERSECT", nhd_flow_Layer, "0", "NEW_SELECTION")
		arcpy.FeatureToRaster_conversion(nhd_wb_Layer, "dummy", wbtempraster, cellsize)
	except:
		arcpy.CreateRasterDataset_management(arcpy.env.workspace,"nhdwb_tmp","10","8_BIT_UNSIGNED",snapGrid)
		arcpy.AddMessage(arcpy.GetMessages())

	# Process: Feature to Raster3 - NHD Flowline.  This is the first output
	try:
		arcpy.FeatureToRaster_conversion(nhd_flow_Layer, "dummy", outraster1, cellsize)
	except:
		arcpy.AddMessage(arcpy.GetMessages())

	# Process: Mosaic NHD Area and NHD Waterbody rasters To New Raster.  This is the second output
	try:
		arcpy.MosaicToNewRaster_management(mosaiclist, workspace, outraster2, "", "8_BIT_UNSIGNED", "", "1", "BLEND", "FIRST")
	except:
		arcpy.AddMessage(arcpy.GetMessages())

	#Delete temp files and rasters
	arcpy.AddMessage("Cleaning up...")
	for fl in [areatempraster,wbtempraster,nhd_wb_feat,nhd_flow_feat,nhd_area_feat]:
		if arcpy.Exists(fl): arcpy.Delete_management(fl)

	arcpy.AddMessage("Done!")

def coastaldem(Input_Workspace, grdNamePth, InFeatureClass, OutRaster, seaLevel):
	'''Sets elevations for water and other areas in DEM

	Originally:
		Al Rea, ahrea@usgs.gov, 05/01/2010, original coding
		ahrea, 10/30/2010 updated with more detailed comments
		Theodore Barnhart, 20190225, tbarnhart@usgs.gov, updated to arcpy

	Parameters
	----------
	Input_Workspace : str
		Input workspace, output raster will be written here.
	grdNamePth : str
		Input DEM grid.
	InFeatureClass : str
		LandSea feature class.
	OutRaster : str
		Output DEM grid name.
	seaLevel : float
		Elevation at which to make the sea
	
	Returns
	-------
	OutRaster : raster
		Output raster written to the workspace.
	'''
	if version:
		arcpy.AddMessage('StreamStats Data Preparation Tools version: %s'%(version))

	try:
		# set working folder
		arcpy.env.workspace = Input_Workspace
		arcpy.env.scratchWorkspace = arcpy.env.Workspace

		arcpy.env.extent = grdNamePth
		arcpy.env.snapRaster = grdNamePth
		arcpy.env.outputCoordinateSystem = grdNamePth
		arcpy.env.cellSize = grdNamePth

		# this is assuming land is 1 and sea is -1
		arcpy.PolygonToRaster_conversion(InFeatureClass, "Land", "mskg")
		
		mskg = Raster("mskg") # load the mask grid
		grdName = Raster(grdNamePth) # load the 
		
		seag = Con(mskg == -1, float(seaLevel))

		landg = Con((mskg == 1) & (grdName <= 0), 1, grdName)

		nochgg = Con(mskg == 0, grdName)

		arcpy.MosaicToNewRaster_management([seag,landg,nochgg],arcpy.env.workspace,OutRaster,None, "32_BIT_SIGNED", None, 1, "FIRST") # mosaic and produce new raster
		
	except:
		e = sys.exc_info()[1]
		print(e.args[0])
		arcpy.AddError(e.args[0])

	return None

def hydrodem(outdir, huc8cov, origdemPth, dendrite, snap_grid, bowl_polys, bowl_lines, inwall, drainplug, buffdist, inwallbuffdist, inwallht, outwallht, agreebuf, agreesmooth, agreesharp, bowldepth, cellsz, scratchWorkspace, version = None):
	'''Hydro-enforce a DEM

	This aml is used by the National StreamStats Team as the optimal
	approach for preparing a state's physiographic datasets for watershed delineations.
	It takes as input, a 10-meter (or 30-foot) DEM, and enforces this data to recognize
	NHD hydrography as truth.  WBD can also be recognized as truth if avaialable for a
	given state/region. This aml assumes that the DEM has first been projected to a
	state's projection of choice. This aml prepares data to be used in the Archydro
	data model (the GIS database environment for National StreamStats).

	The specified <8-digit HUC> should have a path associated with it in the variable 
	settings section near the top of this aml.  The value entered will create a workspace
	with this HUC id as it's name, and copy all output datasets into the new workspace.
	If the workspace already Exists, it should be empty before running this aml.
	
	The snap_grid is used to orient the origin coordinate of the output grids to align 
	with neighboring HUC grids that have already been processed.  
	Typically, this value is rounded to the nearest value
	divisible by 10 (in cases where datsets are in units meters) or 30 (in cases where
	datasets are in units feet).  The snap grid could be your input dem, if that grid
	has already been rounded out (if topogrid was used and steps were followed on the 
	nhd web page referenced above, then the input dem could be used).

	Parameters
	----------
	outdir : DEworkspace
		Working directory
	huc8cov : DEFeatureClass
		Local division feature class, often HUC8, this will be the outer wall of the hydroDEM.
	origdemPth : str
		Path to the orignial, projected DEM.
	dendrite : str
		Path to the dendrite feature class to be used.
	snap_grid : str
		Path to a raster dataset to use as a snap_grid to align all the watersheds, often the same as the DEM.
	bowl_polys : str
		Path to the bowling area raster generated from the bathymetric gradient tool.
	bowl_lines : str
		Path to the bowling line raster generated from the bathymetric gradient tool.
	inwall : str
		Path to the feature class to be used for inwalling
	drainplug : 
		Path to the feature class used for inserting sinks into the dataset
	buffdist : float
		Distance to buffer the outer wall, same units as the projection.
	inwallbuffdist :
		Distance to buffer the inner walls, same units as the projection.
	inwallht :
		Inwall height, same units as the projection.
	outwallht :
		Inwall height, same units as the projection.
	agreebuf :
		AGREE function buffer distance, same units as the projection.
	agreesmooth :
		AGREE function smoothing distance, same units as the projection.
	agreesharp :
		AGREE function sharp distance, same units as the projection.
	bowldepth :
		Bowling depth, same units as the projection.
	cellsz :
		Cell size, same units as the projection.
	scratchWorkspace : str
		Path to scratch workspace
	version : str
		Package version number

	Returns (saved to outDIR)
	-------
	filldem : raster
		hydro-enforced DEM raster grid saved to outDir
	fdirg : raster
		HydroDEM FDR raster grid saved to outDir
	faccg : raster
		HydroDEM FAC raster grid saved to outDir
	sink_path : feature class
		Sink feature class saved to outDir
	'''
	strtTime = time.time()
	if version:
		arcpy.AddMessage('StreamStats Data Preparation Tools version: %s'%(version))

	arcpy.AddMessage("HydroDEM is running")

	## put some checks here about the _bypass variables
	dp_bypass = False
	iw_bypass = False
	bowl_bypass = False

	if inwall == None:
		iw_bypass = True

	if drainplug == None:
		dp_bypass = True

	if ('bowl_polys' == None) or ('bowl_lines' == None):
		bowl_bypass = True

	arcpy.AddMessage('bowl_bypass is %s'%str(bowl_bypass))
	arcpy.AddMessage('dp_bypass is %s'%str(dp_bypass))
	arcpy.AddMessage('iw_bypass is %s'%str(iw_bypass))

	# test if full path datasets exist
	for fl in [outdir,origdemPth,snap_grid,scratchWorkspace]:
		assert arcpy.Exists(fl) == True, "%s does not exist"%(fl)

	dsc = arcpy.Describe(snap_grid) 
	assert dsc.extent.XMin % 5 == 0, "Snap Grid origin not divisible by 5."

	# set working directory and environment
	arcpy.env.workspace = outdir
	arcpy.env.cellSize = cellsz
	arcpy.env.overwriteOutput = True
	arcpy.env.scratchWorkspace = scratchWorkspace
	arcpy.env.outputCoordinateSystem = origdemPth

	# test if other datasets exist
	testDsets = [huc8cov,dendrite]

	# add datasets based on the bypass flags
	if not dp_bypass:
		testDsets.append(drainplug)

	if not iw_bypass:
		testDsets.append(inwall)

	if not bowl_bypass:
		testDsets.append(bowl_polys)
		testDsets.append(bowl_lines)
	
	for fl in testDsets:
		arcpy.AddMessage("Checking if %s exists."%(fl))
		assert arcpy.Exists(fl) == True, "%s does not exist"%(fl)

	tmpLocations = [] # make a container for temp locations that will be deleted at the end

	# buffer the huc8cov
	hucbuff = 'hucbuff' # some temp location
	tmpLocations.append(hucbuff)
	arcpy.AddMessage('	Buffering Local Divisons')
	arcpy.Buffer_analysis(huc8cov, hucbuff, buffdist) # do we need to buffer if this is done in the setup tool, maybe just pass hucbuff to the next step from the parameters...
	arcpy.AddField_management(hucbuff,"dummy","SHORT",None,None,None,None,"NULLABLE","NON_REQUIRED",None)
	arcpy.CalculateField_management(hucbuff,"dummy","1", "PYTHON")

	arcpy.env.extent = hucbuff # set the extent to the buffered HUC

	# rasterize the buffered local division
	arcpy.AddMessage('	Rasterizing %s'%hucbuff)
	outGrid = 'hucbuffRast'
	tmpLocations.append(outGrid)
	arcpy.PolygonToRaster_conversion(hucbuff,"dummy",outGrid,cellsize = cellsz)

	# rasterize the dendrite
	arcpy.AddMessage('	Rasterizing %s'%dendrite)
	dendriteGridpth = 'tmpDendriteRast'
	tmpLocations.append(dendriteGridpth)

	# may need to add a field to dendrite to rasterize it...
	arcpy.AddField_management(dendrite,"dummy","SHORT",None,None,None,None,"NULLABLE","NON_REQUIRED",None)
	arcpy.CalculateField_management(dendrite,"dummy","1", "PYTHON")
	arcpy.FeatureToRaster_conversion(dendrite,"dummy",dendriteGridpth, cell_size = cellsz)
	dendriteGrid = Raster(dendriteGridpth)
	
	origdem = Raster(origdemPth)

	arcpy.env.mask = outGrid # set mask (L169 in hydroDEM_work_mod.aml)
	arcpy.env.snapRaster = snap_grid

	elevgrid = agree(origdem, dendriteGrid, int(agreebuf), int(agreesmooth), int(agreesharp)) # run agree function
	
	# burning streams and adding walls
	arcpy.AddMessage('	Starting Walling') # (L182 in hydroDEM_work_mod.aml)

	ridgeNLpth = 'ridgeRast'
	#tmpLocations.append(ridgeNLpth)
	# may need to add a field to huc8cov to rasterize it...
	arcpy.AddField_management(huc8cov,"dummy","SHORT",None,None,None,None,"NULLABLE","NON_REQUIRED",None)
	arcpy.CalculateField_management(huc8cov,"dummy","1", "PYTHON")
	arcpy.FeatureToRaster_conversion(huc8cov,"dummy",ridgeNLpth,cell_size = cellsz) # rasterize the local divisions feature
	#ridgeEXP = 'some temp location'
	ridgeNL = Raster(ridgeNLpth) # load ridgeNL 
	ridgeEXP = Expand(ridgeNL,2,[1]) # the last parameter is the zone to be expanded, this might need to be added to the dummy field above... 

	ridgeW = SetNull((IsNull(ridgeNL) == 0) & (IsNull(ridgeEXP) == 0), ridgeEXP)
	demRidge8 = elevgrid + Con((IsNull(ridgeW) == 0) & (IsNull(dendriteGrid)), outwallht, 0)

	arcpy.AddMessage('	Walling Complete')

	if not dp_bypass: # dp_bypass is defined after the main code in the original AML
		if int(arcpy.GetCount_management(drainplug).getOutput(0)) > 0:
			dpg_path = 'depressionRast'
			tmpLocations.append(dpg_path)
			arcpy.AddField_management(drainplug,"dummy","SHORT",None,None,None,None,"NULLABLE","NON_REQUIRED",None)
			arcpy.CalculateField_management(drainplug,"dummy","1", "PYTHON")
			arcpy.FeatureToRaster_conversion(drainplug,"dummy",dpg_path,cell_size = cellsz) # (L195 in hydroDEM_work_mod.aml)
			dpg = Raster(dpg_path) # load the raster object
		else:
			tmp = CreateConstantRaster(0) # if the feature class is empty, make a dummy raster
			dpg = SetNull(tmp,tmp,"VALUE = 0") # set all zeros to null.
	else:
		arcpy.AddMessage("	Bypassing Drain Plugs")
		tmp = CreateConstantRaster(0) # if the feature class is empty, make a dummy raster
		dpg = SetNull(tmp,tmp,"VALUE = 0") # set all zeros to null.

	if not bowl_bypass: # bowl_bypass is defined after the main code in the original AML
		arcpy.AddMessage('	Starting Bowling')
		blp_name = 'blp'
		tmpLocations.append(blp_name)

		bowlLines = Raster(bowl_lines)

		arcpy.MosaicToNewRaster_management([bowlLines,dpg],arcpy.env.workspace,blp_name, None, "32_BIT_SIGNED", None, 1, "FIRST") # probably need some more options
		
		blp = Raster(blp_name)

		eucd = SetNull(IsNull(bowl_polys), EucDistance(blp)) # (L210 in hydroDEM_work_mod.aml)
		demRidge8wb = demRidge8 - Con(IsNull(eucd) == 0, (bowldepth / (eucd+1)), 0)
		#demRidge8wb.save(os.path.join(arcpy.env.workspace,'demRidge8wb'))
		arcpy.AddMessage('	Bowling complete')

	else:
		arcpy.AddMessage('	Bowling Skipped')

	if not iw_bypass:
		arcpy.AddMessage('	Starting Inwalling')
		iwb_name = 'tmp_inwall_buff'
		tmpLocations.append(iwb_name)
		if arcpy.Exists(iwb_name):
			arcpy.AddMessage("%s exists, please delete or rename before proceeding."%(iwb_name))
		arcpy.Buffer_analysis(inwall,iwb_name,inwallbuffdist) #(L223 in hydroDEM_work_mod.aml)
		
		tmpGrd_name = 'tmpGrd'
		tmpLocations.append(tmpGrd_name)

		arcpy.AddField_management(iwb_name,"dummy","SHORT",None,None,None,None,"NULLABLE","NON_REQUIRED",None)
		arcpy.CalculateField_management(iwb_name,"dummy","1", "PYTHON")

		arcpy.FeatureToRaster_conversion(iwb_name,"dummy",tmpGrd_name, cell_size = cellsz)
		tmpGrd = Raster(tmpGrd_name)

		# Only inwalls where there are not streams and there are inwalls.
		dem_enforced = demRidge8wb + Con((IsNull(tmpGrd) == 0) & (IsNull(dendriteGrid)), inwallht, 0) #(L226 in hydroDEM_work_mod.aml) 
		arcpy.AddMessage('	Inwalling Complete')
	else:
		del dem_enforced
		dem_enforced = demRidge8wb
		arcpy.AddMessage('	Inwalling Skipped')

	if not dp_bypass:
		detmp = Con(IsNull(dpg),dem_enforced)
		del dem_enforced
		dem_enforced = detmp #(L242 in hydroDEM_work_mod.aml)

	arcpy.env.extent = ridgeEXP
	arcpy.env.mask = ridgeEXP # mask to HUC
	arcpy.cellSize = origdem

	dem_enforced.save(os.path.join(arcpy.env.workspace,'dem_enforced'))

	arcpy.AddMessage("	Starting Fill")
	filldem = Fill(dem_enforced,None)
	fdirg2 = FlowDirection(filldem, 'FORCE') # this works...
	arcpy.AddMessage("	Fill Complete")

	# set the mask and extent for the FAC and FDR grids, which should be clipped to the huc bounding polygon.
	arcpy.env.extent = huc8cov
	arcpy.env.mask = huc8cov

	

	if not dp_bypass:
		fdirg = Int(Con(IsNull(dpg) == 0, 0, fdirg2)) # (L256 in hydroDEM_work_mod.aml), insert a zero where drain plugs were.
	else:
		fdirg = Int(fdirg2)
		
	# might need to save the fdirg, delete it from the python workspace, and reload it...
	arcpy.AddMessage('	Starting Flow Accumulation')
	faccg = FlowAccumulation(fdirg, None, "INTEGER")
	arcpy.AddMessage('	Flow Accumulation Complete')

	arcpy.AddMessage('	Creating Sink Features')
	fsinkg = Con((filldem - origdem) > 1, 1)
	
	fsinkc_name = 'fsinkc'
	arcpy.RasterToPolygon_conversion(fsinkg, fsinkc_name, 'NO_SIMPLIFY') # (L273 in hydroDEM_work_mod.aml), outputs fsinkc
	del fsinkg

	arcpy.AddMessage('	Sink Creation Complete')

	# save the grids to the workspace
	filldem.save(os.path.join(arcpy.env.workspace,"hydrodem"))
	del filldem

	fdirg.save(os.path.join(arcpy.env.workspace,"hydrodemfdr"))
	del fdirg
	faccg.save(os.path.join(arcpy.env.workspace,"hydrodemfac"))
	del faccg

	# clean the environment of temp files
	for fl in tmpLocations: # delete tmp files
		if arcpy.Exists(fl):
			try:
				arcpy.Delete_management(fl)
			except:
				arcpy.AddMessage("Failed to Delete: %s"%fl)

	totalTime = time.time() - strtTime
	arcpy.AddMessage('HydroDEM Complete, %s minutes.'%(totalTime/60.))

	return None

def fill(dem, option, zlimit):
	''' fill function from fill.aml
	Purpose
	-------
		This AML command fills sinks or peaks in a specified surface
		grid and outputs a filled surface grid and, optionally, its
		flow direction grid.  If output filled grid already exists,
		it will be removed first

	Authors
	-------
		Gao, Peng        Dec 20, 1991  Original coding
		Laguna, Juan     Nov  1, 2000  Fix to prevent failure on large FP grids
		Ajit M. George   Jul 31, 2001  Use force option for iterative flowdirection.
									  calculation, and normal option for direction output.
		Theodore Barnhart, tbarnhart@usgs.gov, 20190225, recoded to arcpy/python
		
	Parameters
	----------
	dem : arcpy.sa Raster
	sink == option : string
		Filling option, 'sink' or 'peak'
	zlimit : float?
		Unknown
	direction : arcpy.sa Raster
		Flow direction raster

	Returns
	-------
	filldem : arcpy.sa Raster
		filled DEM
	direction : arcpy.sa Raster
		flow direction grid
	'''

	# generate a bunch of variables in aml, not sure if needed in new arcpy...
	# &s frmdir [show &workspace]
	# &s todir  [dir [pathname %filled%]]
	# &s filled [entryname %filled%]
	# &s dem    [pathname %dem%]
	# &s dm     [substr [entryname %dem%] 1 6]

	# check options [L29-43 fill.aml]
	arcpy.AddMessage("Starting Fill")

	if option == 'sink':
		arcpy.AddMessage('	Sink Routine Selected')
		filled = dem
	else:
		if option == 'peak':
			arcpy.AddMessage('	Peak Routine Selected')
			filled = dem.maximum - dem # (L56 fill.aml) # dem.maximum may need to be a raster of shape(dem) filled with dem.maximum, this would return a grid where the peaks are now the low spots.
		else:
			arcpy.AddMessage('	Unknown keyword.')

	assert option in ['peak','sink']

	arcpy.env.extent = filled
	arcpy.env.cellSize = filled #(L75 fill.aml)

	ff = FocalFlow(filled) # compute focal flow

	if ff == 255:
		tmp = np.min([filled[1,1],filled[1,0],filled[1,-1],
						filled[0,1], filled[0,-1],
						filled[-1,1],filled[-1,0],filled[-1,-1]])

	else:
		tmp = filled # this may not work, may need to write out filled and read it back in as tmp...

	arcpy.env.extent(filled)
	filled = tmp #(L85 in fill.aml)

	del tmp # assuming this is an object...
	del ff

	arcpy.AddMessage('	Filling...')
	# loop until there are no sinks in the surface grid
	finished = False
	sinkcnt = 0
	numsink = 0

	while not finished:

		fdr = FlowDirection(filled, 'Force', None, None) # compute flow direction (L100 in fill.aml)
		sr = Sink(fdr)

		if not sr.hasRAT: # test if the VAT table exists
			arcpy.BuildRasterAttributeTable_management(sr) # if not, build it

		# might need to write out the sr raster here and reload it
		if sr.hasRAT: # test if the VAT table exists (L105 in fill.aml)
			# below this if statement, I think the point is to count the number of sinks...
			newsinkcnt = arcpy.GetCount_management(sr) # Pretty sure this is the same as %grd$nclass%, which references the sink raster (sr) describes at L104 in fill.aml

		else:
			newsinkcnt = 0

		arcpy.AddMessage('	Number of %s(s): %s'%(option,newsinkcnt))
		if newsinkcnt < 1:
			finished = True
		else:
			if numsink == arcpy.GetCount_management(sr) and sinkcnt == newsinkcnt:
				finished = True

		if not finished:
			sinkcnt = newsinkcnt
			numsink = newsinkcnt

			# describe %filled% (L124 in filled.aml)
			sub = Watershed(fdr,sr) # compute watersheds from pour points

			if not sub.hasRAT:
				arcpy.BuildRasterAttributeTable_management(sub)

			del sr

			zonalfill = ZonalFill(sub,filled)

			zonalfill1 = Con(IsNull(zonalfill), filled.minimum, zonalfill)

			del zonalfill

			if zlimit is None:
				zonalfill2 = Con(filled < zonalfill1, zonalfill1, filled)

			else:
				zm1 = ZonalStatistics(sub, "VALUE", filled, "MINIMUM")
				zmm = Con(IsNull(zm1),Minimum(filled),zm1)
				zf2 = Con((filled < zf1) & ((zf1 - zmm) < zlimit), zf1, filled)
		
		del filldem
		filldem = zf2 # (L147 in fill.aml)

	arcpy.AddMessage("Fill Complete.")
	return filldem, fdr

	##########################################
	#
	#	original fill.aml code below
	#
	##########################################
	#
	#/* @(#)fill.aml	1.14 9/25/95 18:05:07
	# /*
	# /* FILL.AML
	# /*
	# /* . Purpose:
	# /*    This AML command fills sinks or peaks in a specified surface
	# /*    grid and outputs a filled surface grid and, optionally, its
	# /*    flow direction grid.  If output filled grid already exists,
	# /*    it will be removed first
	# /*
	# /* . Author(s):
	# /*    Gao, Peng        Dec 20, 1991  Original coding
	# /*    Laguna, Juan     Nov  1, 2000  Fix to prevent failure on large FP grids
	# /*    Ajit M. George   Jul 31, 2001  Use force option for iterative flowdirection.
	# /*                                   calculation, and normal option for direction output.

	# &arg dem filled option zlimit direction
	# &severity &error &routine error
	# &s msgsave
	# &s vrfsave
	# /*
	# /*  Where are we ?
	# /*
	# &if [show program] ne GRID &then
	#   &return FILL only runs in GRID.
	# /*
	# /* validate args
	# /*
	# &if [null %dem%] OR [null %filled%] &then &do
	#   &goto USAGE
	# &end
	# &s frmdir [show &workspace]
	# &s todir  [dir [pathname %filled%]]
	# &s filled [entryname %filled%]
	# &s dem    [pathname %dem%]
	# &s dm     [substr [entryname %dem%] 1 6]
	# &if not [null %zlimit%] and [type %zlimit%] gt 0 ~
	#     and %zlimit%_ ne #_ &then &do
	#   &type Z-limit is not a number
	#   &goto USAGE
	# &end
	# &if [null %option%] or %option% eq # &then
	#   &s option sink
	# /*
	# /* prepare the grid for filling
	# /*
	# &workspace %todir%
	# &s msgsave [show &message]
	# /*&message &off
	# &if [locase %option%] eq 'sink' &then
	#   %filled% = %dem%
	# &else &do
	#   &if [locase %option%] eq 'peak' &then &do
	#     &describe %dem%
	#     &s maxvalue %GRD$ZMAX%
	#     %filled% = %maxvalue% - %dem%
	#   &end
	#   &else &do
	#     &workspace %frmdir%
	#     &message %msgsave%
	#     &type Unknown keyword: %option%
	#     &goto USAGE
	#   &end
	# &end
	# &s vrfsave [show verify]
	# verify off
	# /*
	# /* fill in one cell sinks (peaks)
	# /*
	# &s window = [show setwindow]
	# &s cell = [show setcell]
	# &describe %filled%
	# setwindow [calc %grd$xmin% - %grd$dx%] %grd$ymin% ~
	#           [calc %grd$xmax% + %grd$dx%] %grd$ymax%
	# setcell %filled%
	# z00%dm%ff = focalflow(%filled%)
	# if (z00%dm%ff eq 255) then
	#   z00%dm%tmp = min(%filled%(1,1), %filled%(1,0), %filled%(1,-1), ~
	#                    %filled%(0,1), %filled%(0,-1), ~
	#                    %filled%(-1,1),%filled%(-1,0),%filled%(-1,-1))
	# else
	#   z00%dm%tmp = %filled%
	# endif
	# setwindow %filled%
	# %filled% = z00%dm%tmp
	# Arc kill z00%dm%ff all
	# Arc kill z00%dm%tmp all
	# setwindow %window%
	# setcell %cell%

	# &type Filling...
	# /*
	# /* loop until no sink in the surface grid
	# /*
	# &s finished = .FALSE.
	# &s sinkcnt = 0
	# &s numsink = 0
	# &do &until %finished%
	#   &if [exists z00%dm%dir -grid] &then Arc kill z00%dm%dir all
	#   z00%dm%dir = flowdirection (%filled%, #, force)
	#   z00%dm%snk = sink (z00%dm%dir)
	#   &if not [exists z00%dm%snk -VAT] &then
	#     buildvat z00%dm%snk
	#   &describe z00%dm%snk
	#   &if [exists z00%dm%snk -VAT] &then &do
	#     cursor sinkvat declare [joinfile z00%dm%snk vat -ext] info ro
	#     cursor sinkvat open
	#     &s newsinkcnt = %:sinkvat.count%
	#     cursor sinkvat close
	#     cursor sinkvat remove
	#   &end
	#   &else
	#     &s newsinkcnt = 0
	#   &type Number of %option%(s): %GRD$NCLASS%
	#   &if %GRD$NCLASS% < 1 &then
	#     &s finished = .TRUE.
	#   &else &do
	#     &if %numsink% = %GRD$NCLASS% and %sinkcnt% = %newsinkcnt% &then
	#       &s finished = .TRUE.
	#   &end
	#   &if not %finished% &then &do
	#     &s sinkcnt = %newsinkcnt%
	#     &s numsink = %GRD$NCLASS%
	#     &describe %filled%
	#     z00%dm%sub = watershed (z00%dm%dir, z00%dm%snk)
	#     &if not [exists z00%dm%sub -VAT] &then
	#       buildvat z00%dm%sub
	#     Arc kill z00%dm%snk
	#     z00%dm%zfl = zonalfill (z00%dm%sub, %filled%)
	#     z00%dm%zf1 = con (isnull (z00%dm%zfl), %GRD$ZMIN%, z00%dm%zfl)
	#     Arc kill z00%dm%zfl
	#     &if [null %zlimit%] OR [QUOTE %zlimit%] EQ # &then &do
	#       z00%dm%zf2 = con (%filled% < z00%dm%zf1, z00%dm%zf1, %filled%)
	#     &end
	#     &else &do
	#       z00%dm%zm1 = zonalmin (z00%dm%sub, %filled%)
	#       z00%dm%zmm = con (isnull (z00%dm%zm1), %GRD$ZMIN%, z00%dm%zm1)
	#       z00%dm%zf2 = con (%filled% < z00%dm%zf1 AND ~
	#                          z00%dm%zf1 - z00%dm%zmm < %zlimit%, ~
	#                          z00%dm%zf1, %filled%)
	#       Arc kill z00%dm%zm1
	#       Arc kill z00%dm%zmm
	#     &end
	#     Arc kill z00%dm%sub
	#     Arc kill z00%dm%zf1
	#     Arc kill %filled%
	#     rename z00%dm%zf2 %filled%
	#   &end
	# &end

	# /*
	# /* Done, finish up
	# /*
	# &if [locase %option%] eq peak &then &do
	#   z00%dm%zf2 = %maxvalue% - %filled%
	#   Arc kill %filled%
	#   rename z00%dm%zf2 %filled%
	# &end

	# &if [exists z00%dm%dir -grid] &then Arc kill z00%dm%dir all
	# &if not [null %direction%] and %direction%_ ne #_ &then
	# &do
	#   %direction% = flowdirection (%filled%)
	# &end

	# Arc kill z00%dm%snk
	# verify %vrfsave%
	# &workspace %frmdir%
	# &message %msgsave%
	# &return

	# /*
	# /* Usage
	# /*
	# &label USAGE
	#   &return &warning ~
	#   Usage: FILL <in_grid> <out_grid> {SINK | PEAK} {z_limit} {out_dir_grid}

	# /*
	# /* Error handling
	# /*
	# &routine error
	#   &severity &error &fail
	#   &if not [null %msgsave%] &then
	#     &message %msgsave%
	#   &if not [null %vrfsave%] &then
	#     verify %vrfsave%
	#   &if not [null %frmdir%] &then
	#     &workspace %frmdir%
	# &return &error

def agree(origdem, dendrite, agreebuf, agreesmooth, agreesharp):
	'''Agree function from AGREE.aml

	Original function by Ferdi Hellweger, http://www.ce.utexas.edu/prof/maidment/gishydro/ferdi/research/agree/agree.html

	recoded by Theodore Barnhart, tbarnhart@usgs.gov, 20190225

	-------------
	--- AGREE ---
	-------------
	
	--- Creation Information ---
	
	Name: agree.aml
	Version: 1.1
	Date: 10/13/96
	Author: Ferdi Hellweger
			Center for Research in Water Resources
			The University of Texas at Austin
			ferdi@crwr.utexas.edu
	
	--- Purpose/Description ---
	
	AGREE is a surface reconditioning system for Digital Elevation Models (DEMs).
	The system adjusts the surface elevation of the DEM to be consistent with a
	vector coverage.  The vecor coverage can be a stream or ridge line coverage. 

	Parameters
	----------
	origdem : arcpy.sa Raster
		Original DEM with the desired cell size, oelevgrid in original script
	dendrite : arcpy.sa Raster
		Dendrite feature layer to adjust the DEM, vectcov in the original script
	agreebuf : float 
		Buffer smoothing distance (same units as the horizontal), buffer in original script
	agreesmooth : float
		Smoothing distance (same units as the vertical), smoothdist in the original script
	agreesharp : float
		Distance for sharp feature (same units as the vertical), sharpdist in the original script

	Returns
	-------
	elevgrid : arcpy.sa Raster
		conditioned elevation grid returned as a arcpy.sa Raster object
	'''
	arcpy.AddMessage('	Starting AGREE')

	# code to check that all inputs exist

	cellsize = (float(arcpy.GetRasterProperties_management(origdem, "CELLSIZEX").getOutput(0)) + float(arcpy.GetRasterProperties_management(origdem, "CELLSIZEY").getOutput(0)))/2. # compute the raster cell size

	arcpy.AddMessage('		Setting Environment Variables')
	arcpy.env.extent = origdem # (L130 AGREE.aml)
	arcpy.env.cellSize = cellsize # (L131 AGREE.aml)

	#arcpy.AddMessage('	Rasterizing the Dendrite.')
	#tmpLocations = []
	#dendriteGridPth = 'tmpDendrite' # might need to add a field for rasterization
	#tmpLocations.append(dendriteGridPth)
	#arcpy.AddField_management

	#arcpy.FeaturetoRaster_conversion(dendrite,dendriteGridPth)

	arcpy.AddMessage('		Computing smooth drop/raise grid...')
	# expression = 'int ( setnull ( isnull ( vectgrid ), ( \"origdem\" + \"greesmooth\" ) ) )'

	#dendriteGrid = Raster(dendriteGridPth)
	#origdem = Raster(origdem)
	
	smogrid = Int(SetNull(IsNull(dendrite), (origdem + agreesmooth))) # compute the smooth drop/raise grid (L154 in AGREE.aml)

	arcpy.AddMessage('		Computing vector distance grids...')
	vectdist = EucDistance(smogrid)
	# Need to produce vectallo (stores the elevation of the closest vector cell), is this the same as the smogrid?
	vectallo = EucAllocation(smogrid) # Roland Viger thinks the original vectallo is an allocation grid, that can be made with EucAllocation.

	arcpy.AddMessage('		Computing buffer grids...')
	bufgrid1 = Con((vectdist > (agreebuf - (cellsize / 2.))), 1, 0) 
	bufgrid2 = Int(SetNull(bufgrid1 == 0, origdem)) # (L183 in AGREE.aml)

	arcpy.AddMessage('		Computing buffer distance grids...')
	# compute euclidean distance and allocation grids
	bufdist = EucDistance(bufgrid2)
	bufallo = EucAllocation(bufgrid2)

	arcpy.AddMessage('		Computing smooth modified elevation grid...')
	smoelev =  vectallo + ((bufallo - vectallo) / (bufdist + vectdist)) * vectdist

	arcpy.AddMessage('		Computing sharp drop/raise grid...')
	#shagrid = int ( setnull ( isnull ( vectgrid ), ( smoelev + %sharpdist% ) ) )
	shagrid = Int(SetNull(IsNull(dendrite), (smoelev + agreesharp)))

	arcpy.AddMessage('		Computing modified elevation grid...')
	elevgrid = Con(IsNull(dendrite), smoelev, shagrid)

	arcpy.AddMessage('	AGREE Complete')

	return elevgrid 

	#############################################################
	# AGREE.aml
	#
	#
	# /*
	# /*-------------
	# /*--- AGREE ---
	# /*-------------
	# /*
	# /*--- Creation Information ---
	# /*
	# /*Name: agree.aml
	# /*Version: 1.1
	# /*Date: 10/13/96
	# /*Author: Ferdi Hellweger
	# /*        Center for Research in Water Resources
	# /*        The University of Texas at Austin
	# /*        ferdi@crwr.utexas.edu
	# /*
	# /*--- Purpose/Description ---
	# /*
	# /*AGREE is a surface reconditioning system for Digital Elevation Models (DEMs).
	# /*The system adjusts the surface elevation of the DEM to be consistent with a
	# /*vector coverage.  The vecor coverage can be a stream or ridge line coverage. 
	# /*
	# /*--- Get Input Data ---
	# /*
	# &args oelevgrid vectcov buffer smoothdist sharpdist

	# /*
	# &if ( [ length %oelevgrid% ] = 0 ) &then &do
	#   /*-ls001
	#   &type AGREE:
	#   &type AGREE: INPUT REQUIRED
	#   /*
	#   &label a
	#   &type AGREE:
	#   &sv oelevgrid = [ response 'AGREE: Elevation Grid']
	#   &if ( [ length %oelevgrid% ] = 0 ) &then  &do
	#     /*-ls002
	#     &type AGREE:
	#     &type AGREE: INPUT ERROR - Elevation Grid has to be specified
	#     &goto a
	#     /*-le002
	#   &end
	#   &if ( not [ exists %oelevgrid% -grid ] ) &then  &do
	#     /*-ls003
	#     &type AGREE:
	#     &type AGREE: INPUT ERROR - Grid does not exist
	#     &goto a
	#     /*-le003
	#   &end
	#   /*
	#   &label b
	#   &type AGREE:
	#   &sv vectcov = [ response 'AGREE: Vector Coverage']
	#   &if ( [ length %vectcov% ] = 0 ) &then  &do
	#     /*-ls004
	#     &type AGREE:
	#     &type AGREE: INPUT ERROR - Vector Coverage has to be specified.
	#     &goto b
	#     /*-le004
	#   &end
	#   &if ( not [ exists %vectcov% -cover ] ) &then &do
	#     /*-ls006
	#     &type AGREE:
	#     &type AGREE: INPUT ERROR - Coverage does not exist
	#     &goto b
	#     /*-le006
	#   &end
	#   /*
	#   &label c
	#   &type AGREE:
	#   &sv buffer = [ response 'AGREE: Buffer Distance']
	#   &if ( [ length %buffer% ] = 0 ) &then &do
	#     /*-ls008
	#     &type AGREE:
	#     &type AGREE: INPUT ERROR - Buffer Distance has to be specified
	#     &goto c
	#     /*-le008
	#   &end
	#   /*
	#   &type AGREE:
	#   &type AGREE: Note that for the upcoming smooth and sharp drop/raise
	#   &type AGREE: distance positive is up and negative is down.
	#   /*
	#   &label d
	#   &type AGREE:
	#   &sv smoothdist = [ response 'AGREE: Smooth Drop/Raise Distance']
	#   &if ( [ length %smoothdist% ] = 0 ) &then &do
	#     /*ls009
	#     &type AGREE:
	#     &type AGREE: INPUT ERROR - Smooth Drop/Raise Distance has to be specified
	#     &goto d
	#     /*-le009
	#   &end
	#   /*
	#   &label e
	#   &type AGREE:
	#   &sv sharpdist = [ response 'AGREE: Sharp Drop/Raise Distance']
	#   &if ( [ length %sharpdist% ] = 0 ) &then &do
	#     /*-ls010
	#     &type AGREE:
	#     &type AGREE: INPUT ERROR - Sharp Drop/Raise Distance has to be specified
	#     &goto e
	#     /*-le010
	#   &end
	#   /*-le001
	# &end
	# /*
	# &type AGREE:
	# &type AGREE: Starting...
	# /*
	# /*--- General Set Up ---
	# /*
	# &type AGREE:
	# &type AGREE: Extracting original elevation grid parameters...
	# &describe %oelevgrid%
	# &sv cellsize = %GRD$DX%
	# /*
	# /*&if [extract 1 [show display]] ne 9999 &then
	# /*display 9999
	# /*
	# &type AGREE:
	# &type AGREE: Displaying original elevation grid...
	# /*mape %oelevgrid%
	# /*gridpaint %oelevgrid% value linear nowrap gray
	# /*
	# /*set analysis environment
	# /*
	# &type AGREE:
	# &type AGREE: Setting the analysis environment...
	# setwindow %oelevgrid%
	# setcell %oelevgrid%
	# /*
	# /*--- Agree Method ---
	# /*
	# /*compute vectgrid
	# /*
	# &type AGREE:
	# &type AGREE: Computing vector grid...
	# &type AGREE:
	# &if [exists vectgrid -grid] &then
	# arc kill vectgrid all
	# vectgrid = linegrid ( %vectcov% )
	# &type AGREE:
	# &type AGREE: Displaying vector grid...
	# /*gridpaint vectgrid
	# /*
	# /*compute smogrid
	# /*
	# &type AGREE:
	# &type AGREE: Computing smooth drop/raise grid...
	# &type AGREE:
	# &if [exists smogrid -grid] &then
	# arc kill smogrid all
	# smogrid = int ( setnull ( isnull ( vectgrid ), ( %oelevgrid% + %smoothdist% ) ) )
	# &type AGREE:
	# &type AGREE: Displaying smooth drop/raise grid...
	# /*gridpaint smogrid value linear nowrap gray
	# /*
	# /*compute vectdist and vectallo
	# /*
	# &type AGREE:
	# &type AGREE: Computing vector distance grids...
	# &type AGREE:
	# &if [exists vectdist -grid] &then
	#   arc kill vectdist all
	# &if [exists vectallo -grid] &then
	#   arc kill vectallo all
	# vectdist = eucdistance( smogrid, #, vectallo, #, # )
	# &type AGREE:
	# &type AGREE: Displaying vector distance grid...
	# /*gridpaint vectdist value linear nowrap gray
	# /*
	# /*compute bufgrid1 and bufgrid2
	# /*
	# &type AGREE:
	# &type AGREE: Computing buffer grid...
	# &type AGREE:
	# &if [exists bufgrid1 -grid] &then
	#   arc kill bufgrid1 all
	# &if [exists bufgrid2 -grid] &then
	#   arc kill bufgrid2 all
	# bufgrid1 = con ( ( vectdist > ( %buffer% - ( %cellsize% / 2 ) ) ), 1, 0)
	# bufgrid2 = int ( setnull ( bufgrid1 == 0, %oelevgrid% ) ) 
	# &type AGREE:
	# &type AGREE: Displaying buffer grid...
	# /*gridpaint bufgrid2 value linear nowrap gray
	# /*
	# /*compute bufdist and bufballo
	# /*
	# &type AGREE:
	# &type AGREE: Computing buffer distance grids...
	# &type AGREE:
	# &if [exists bufdist -grid] &then
	#   arc kill bufdist all
	# &if [exists bufallo -grid] &then
	#   arc kill bufallo all
	# bufdist = eucdistance( bufgrid2, #, bufallo, #, # )
	# &type AGREE:
	# &type AGREE: Displaying buffer distance grid...
	# /*gridpaint bufdist value linear nowrap gray
	# /*
	# /*compute smoelev
	# /*
	# &type AGREE:
	# &type AGREE: Computing smooth modified elevation grid...
	# &type AGREE:
	# &if [exists smoelev -grid] &then
	#   arc kill smoelev all
	# smoelev =  vectallo + ( ( bufallo - vectallo ) / ( bufdist + vectdist ) ) * vectdist
	# &type AGREE:
	# &type AGREE: Displaying smooth modified elevation grid...
	# &type AGREE:
	# /*gridpaint smoelev value linear nowrap gray
	# /*
	# /*compute shagrid
	# /*
	# &type AGREE:
	# &type AGREE: Computing sharp drop/raise grid...
	# &type AGREE:
	# &if [exists shagrid -grid] &then
	#   arc kill shagrid all
	# shagrid = int ( setnull ( isnull ( vectgrid ), ( smoelev + %sharpdist% ) ) )
	# &type AGREE:
	# &type AGREE: Displaying sharp drop/raise grid...
	# /*gridpaint shagrid value linear nowrap gray
	# /*
	# /*compute elevgrid
	# /*
	# &type AGREE:
	# &type AGREE: Computing modified elevation grid...
	# &type AGREE:
	# &if [exists elevgrid -grid] &then
	#   arc kill elevgrid all
	# elevgrid = con ( isnull ( vectgrid ), smoelev, shagrid )
	# &type AGREE:
	# &type AGREE: Displaying modified elevation grid...
	# /*gridpaint elevgrid value linear nowrap gray
	# /*
	# /*clean up
	# /*
	# &type AGREE:
	# &type AGREE: Cleaning up...
	# &type AGREE:
	# arc kill vectgrid all
	# arc kill smogrid all
	# arc kill vectdist all
	# arc kill vectallo all
	# arc kill bufgrid1 all
	# arc kill bufgrid2 all
	# arc kill bufdist all
	# arc kill bufallo all
	# arc kill smoelev all
	# arc kill shagrid all
	# /*
	# /*close up
	# /*
	# &type AGREE:
	# &type AGREE: Normal end.
	# &type AGREE:
	# &type AGREE: NOTE: Modified elevation grid is saved as elevgrid in current workspace.
	# &type AGREE: 
	# &return

def adjust_accum(facPth, fdrPth, upstreamFACpths,upstreamFDRpths, workspace):
	'''
	Example
	-------
	adjust_accum("./01010001/fac",2,["./01010002/fac","./01010003/fac"])

	Description
	-----------
	This fucntion adjusts the fac of a downstream HUC to include flow accumulations from upstream HUC's. Run this from the downstream HUC workspace. The function will leave the fac grid intact and will create a grid named "fac_global" in the same directory as the original fac raster. To get true accumulation values in HUCs downstream of other non-headwater HUCs, proceed from upstream HUCs to downstream HUCs in order, and specify the fac_global grid for any upstream HUC that has one. (It is not essential that the fac_global contain true global fac values, and in some cases it is not possible since the values get too large. In practice, as long as the receiving cells have accumulation values larger than the stream definition threshold (150,000 cells for 10-m grids), then it will be OK. Not sure if this caveat applies with arcPy.

	Parameters
	----------
	facPth : str
		Path to downstream flow accumulation grid
	fdrPth : str
		Path to downstream flow direction grid
	upstreamFACpths : list
		List of paths to upstream flow accumulation grids
	upstreamFDRpths : list
		List of paths to upstream flow direction grids
	workspace : str
		local geodatabase to work in.
	
	Outputs
	-------
	facGlobal : str
		Path to fac_global raster created in the same directory as fac

	Attribution
	-----------
	accum_adjust2.aml - unknown
	flow_accum_adjust.py - Martyn Smith, USGS
	adjust_accum (function) - Theodore Barnhart, USGS
	'''
	arcpy.AddMessage("Preparing environment.")
	arcpy.env.workspace = workspace
	arcpy.env.scratchWorkspace = workspace

	#test that everything exists	
	assert arcpy.Exists(facPth), "Raster %s does not exist"%(facPth)

	assert arcpy.Exists(fdrPth), "Raster %s does not exist"%(fdrPth)

	for fl in upstreamFACpths:
		assert arcpy.Exists(fl), "Raster %s does not exist"%(fl)

	for fl in upstreamFDRpths:
		assert arcpy.Exists(fl), "Raster %s does not exist"%(fl)

	# load the upstream rasters into a structure
	upstreamFACs = []
	upstreamFDRs = []
	for fac,fdr in zip(upstreamFACpths,upstreamFDRpths):
		upstreamFACs.append(Raster(fac))
		upstreamFDRs.append(Raster(fdr))

	downstream = Raster(facPth) # load the downstream raster
	downstreamFDR = Raster(fdrPth)

	# get raster cell dimensions
	dsc = arcpy.Describe(downstream)
	dx = dsc.children[0].MeanCellWidth
	dy = dsc.children[0].MeanCellHeight

	arcpy.AddMessage("Processing upstream rasters...")
	costPaths = []
	for fac,fdr in zip(upstreamFACs,upstreamFDRs): # iterate through the rasters
		arcpy.env.extent = fac
		arcpy.env.cellSize = fac
		arcpy.env.overwriteOutput = True

		loc = Con(fac == fac.maximum,fdr) # make a locator raster of the outlet of the outlet
		#flowDir = int(loc.maximum) # get the flow direction of the selected cell

		# now get the location of the cell...
		arcpy.RasterToPoint_conversion(loc,"pt") # conver to feature class
		with arcpy.da.SearchCursor("pt",["grid_code","SHAPE@X","SHAPE@Y"]) as cursor: # read the data
			with arcpy.da.UpdateCursor("pt",["SHAPE@X","SHAPE@Y"]) as updateCursor: # update the data
				for row, uprow in zip(cursor,updateCursor):
					# extract coordinates
					flowDir = row[0]
					x = row[1]
					y = row[2]

					# figure out the correction
					if flowDir == 1: # east
						xCoor = dx
						yCoor = 0
					elif flowDir == 2: # southeast
						xCoor = dx
						yCoor = dy*-1
					elif flowDir == 4: # south
						xCoor = 0
						yCoor = dy * -1
					elif flowDir == 8: # southwest
						xCoor = dx
						yCoor = dy * -1
					elif flowDir == 16: # west
						xCoor = dx * -1
						yCoor = 0
					elif flowDir == 32: # northwest
						xCoor = dx * -1
						yCoor = dy
					elif flowDir == 64: # north
						xCoor = 0
						yCoor = dy
					elif flowDir == 128: # northeast
						xCoor = dx
						yCoor = dy

					# update their position
					x += xCoor
					y += yCoor

					# insert back into feature class
					uprow[0] = x
					uprow[1] = y
					updateCursor.updateRow(uprow)

		# now trace the least cost downstream from the point
		arcpy.env.extent = downstream
		arcpy.env.cellSize = downstream

		ones = Con(IsNull(downstream) == 0,1) # make a constant raster

		#ones.save("constant")
		costPth = CostPath("pt",ones,downstreamFDR,path_type = "EACH_CELL") # trace path and append to list

		tmp = Con(IsNull(costPth)==0,fac.maximum,0)
		#tmp.save("costPath")
		costPaths.append(tmp) # attribute the cost path with the fac max value, all the cost paths will be added together later.

		if arcpy.Exists("pt"): arcpy.Delete_management("pt") # clean up

	# now that all cost paths have been generatate, sum them with the downstream FAC gid to get the final FAC grid.
	arcpy.AddMessage("Correcting downstream FAC.")
	arcpy.env.extent = downstream
	arcpy.env.cellSize = downstream

	for pth in costPaths:
		downstream += pth

	downstream.save("hydrodemfac_global")

	# &args fac_grd num_inlets ingrds:REST
	# &type [date -full]
	# &echo &on

	# &if [null %fac_grd%] &then &do
	#   &call usage
	#   &return
	# &end 

	# &severity &error &routine Bailout

	# grid
	# disp 9999

	# &do i = 1 &to %num_inlets%
	#   &s grd%i% = [extract %i% [unquote %ingrds%]]
	#   &s i = %i% + 1
	# &end

	# &s start_path [show work]
	# &do i = 1 &to %num_inlets%
	#   &wo [dir [value grd%i%]]
	#   /*determine max FAC value
	#   &des [value grd%i%]
	#   &if [exists grd_t1 -grid] &then
	#     arc kill grd_t1
	#   setmask off
	#   setcell %grd$dx%
	#   setwindow [value grd%i%]
	#   grd_t1 = con([entryname [value grd%i%]] == %grd$zmax%,0)
	#   setmask grd_t1
	#   /*determine x,y of max FAC cell
	#   &if [exists pnt_t%i% -cover] &then
	#     arc kill pnt_t%i%
	#   pnt_t%i% = gridpoint(grd_t1,value)
	#   &des pnt_t%i%
	#   &s outlet_x%i% = %dsc$xmax%
	#   &s outlet_y%i% = %dsc$ymax%
	#   &s adjust_num%i%val = %grd$zmax%
	#   &type %i%, [value grd%i%], [value outlet_x%i%], [value outlet_y%i%]
	  
	#   /*determine FDR value of max FAC cell
	#   &s fdr%i% = [show cellvalue [dir [value grd%i%]]/fdr [value outlet_x%i%], [value outlet_y%i%]]
	  
	#   /*calc  x,y offset
	#   &select [value fdr%i%]
	#     &when 1
	#       &do
	#         &s adjust_num%i%x = [calc [value outlet_x%i%] + %grd$dx%]
	#         &s adjust_num%i%y = [value outlet_y%i%]
	#       &end
	#     &when 2
	#       &do
	#         &s adjust_num%i%x = [calc [value outlet_x%i%] + %grd$dx%]
	#         &s adjust_num%i%y = [calc [value outlet_y%i%] - %grd$dy%]
	#       &end
	#     &when 4
	#       &do
	#         &s adjust_num%i%x = [value outlet_x%i%]
	#         &s adjust_num%i%y = [calc [value outlet_y%i%] - %grd$dx%]
	#       &end
	#     &when 8
	#       &do
	#         &s adjust_num%i%x = [calc [value outlet_x%i%] - %grd$dx%]
	#         &s adjust_num%i%y = [calc [value outlet_y%i%] - %grd$dy%]
	#       &end
	#     &when 16
	#       &do
	#         &s adjust_num%i%x = [calc [value outlet_x%i%] - %grd$dx%]
	#         &s adjust_num%i%y = [value outlet_y%i%]
	#       &end
	#     &when 32
	#       &do
	#         &s adjust_num%i%x = [calc [value outlet_x%i%] - %grd$dx%]
	#         &s adjust_num%i%y = [calc [value outlet_y%i%] + %grd$dy%]
	#       &end
	#     &when 64
	#       &do
	#         &s adjust_num%i%x = [value outlet_x%i%]
	#         &s adjust_num%i%y = [calc [value outlet_y%i%] + %grd$dx%]
	#       &end
	#     &when 128
	#       &do
	#         &s adjust_num%i%x = [calc [value outlet_x%i%] + %grd$dx%]
	#         &s adjust_num%i%y = [calc [value outlet_y%i%] + %grd$dy%]
	#       &end
	#   &end
	#   &wo %start_path%
	# &end

	# &wo [dir %fac_grd%]
	#  setmask off
	# setwindow maxof
	# mape %fac_grd%
	# units map
	# &if [exists fac1 -grid] &then
	#   arc kill fac1
	# arc copy [entryname %fac_grd%] fac1

	# &do i = 1 &to %num_inlets%
	#   coord keyboard xy
	#   &if [exists pathgrd%i% -grid] &then
	#     arc kill pathgrd%i%
	#     pathgrd%i% = costpath(*,fil,fdr)
	#        1,[value adjust_num%i%x],[value adjust_num%i%y]
	#        3
	#        ~
	       
	#   &if [exists fac_adj%i% -grid] &then
	#     arc kill fac_adj%i%
	#   fac_adj%i% = con(pathgrd%i%,fac%i% + [value adjust_num%i%val],fac%i%)
	#   &s val = %i% + 1
	#   &if [exists fac%val% -grid] &then
	#     arc kill fac%val%
	#   fac%val% = merge(fac_adj%i%,fac%i%)
	# &end


	# &if [exists fac_global.rrd -file] &then
	#   &s xx [delete fac_global.rrd -file]
	# &if [exists fac_global.aux -file] &then
	#   &s xx [delete fac_global.aux -file]

	# &if [exists fac_global -grid] &then
	#   arc kill fac_global

	# rename fac%val% fac_global


	# /*&if [exists str%thresh2% -grid] &then
	# /*  arc kill str%thresh2%

	# /*str%thresh2% = con ( fac_global ge %thresh2%, 1)
	  
	# /*cleanup
	# &do i = 1 &to %num_inlets%
	#   &if [exists grd_t1 -grid] &then
	#     arc kill grd_t1
	#   &if [exists fac_adj%i% -grid] &then
	#     arc kill fac_adj%i% all
	#   &if [exists pathgrd%i% -grid] &then
	#     arc kill pathgrd%i% all
	#   &if [exists fac%i% -grid] &then
	#     arc kill fac%i%
	# &end 
	  
	# coord mouse  

	# quit

	# &return

	# &ROUTINE BAILOUT
	# &severity &error &ignore
	# coord mouse
	# &wo %start_path%
	# &lv
	# &return &error Bailing out of Accum_Adjust2.aml

	# &routine usage
	# &type  
	# &type  USAGE: &r accum_adjust2 <fac_grd> <num_inlets> 
	# &type                <space separated list of full paths to upstream fac grids>
	# &type   
	# &type  ex: &r d:\sstoolbox\accum_adjust2 3 D:\streamstats\DataPrepWorkshop10\ex1\1111\fac D:\streamstats\DataPrepWorkshop10\ex1\2222\fac D:\streamstats\DataPrepWorkshop10\ex1\3333\fac 
	# &type 
	# &type This AML adjusts the fac of a downstream HUC to include flow accumulations from
	# &type upstream HUC's. Run this from the downstream HUC workspace. The AML will leave 
	# &type the fac grid intact and will create agrid named "fac_global". To get true 
	# &type accumulation values in HUCs downstream of other non-headwater HUCs, proceed 
	# &type from upstream HUCs to downstream HUCs in order, and specify the fac_global grid 
	# &type for any upstream HUC that has one. (It is not essential that the fac_global
	# &type contain true global fac values, and in some cases it is not possible since the 
	# &type values get too large. In practice, as long as the receiving cells have 
	# &type accumulation values larger than the stream definition threshold 
	# &type (150,000 cells for 10-m grids), then it will be OK. 
	# &type  
	# &return  /* end of usage routine

def postHydroDEM(workspace, facPth, fdrPth, thresh1, thresh2, sinksPth = None, version = None):
	'''generate stream reaches, adjoint catchments, and drainage points
	
	Note
	----
	This tool requires archydro

	Parameters
	----------
	workspace : str
		database-type workspace to output rasters and feature classes.
	facPth : str
		Path to the flow accumulation grid produced by hydroDEM.
	fdrPth : str
		Path to the flow direction grid produced by hydroDEM.
	thresh1 : int
		Threshold used to produce the str grid, in raster cells, usually equal to 15,000,000 m$^2$.
	thresh2 : int
		Threshold used to produce the str900 grid, in raster cells, usually equal to 810,000 m$^2$.
	sinksPth : str (optional)
		Path to the snklnk grid, optional.
	version : str (optional)
		StreamStats DataPrepTools version to be printed.

	Returns
	-------
	None

	Outputs
	-------
	str : raster
		Stream raster where fac > 15,000,000 m$^2$.
	str900 : raster
		Stream raster where fac > 810,000 m$^2$.
	strlnk : raster
	lnk : raster
	cat : raster
	drainageLine : feature class
	catchment : feature class
	adjointCatchment : feature class
	drainagePoint : feature class
	'''

	if version:
		arcpy.AddMessage('StreamStats Data Preparation Tools version: %s'%(version))

	pyVer = int(sys.version[:1])

	if pyVer == 3: # for python 3
		arcpy.AddMessage("This tool only runs in Python 2....")
		sys.exit(0)
		#from archydro.streamdefinition import StreamDefinition
		#from archydro.streamsegmentation import StreamSegmentation
		#from archydro.drainagelineprocessing import DrainageLineProcessing
		#from archydro.combinestreamlinkandsinklink import CombineStreamLinkandSinkLink
		#from archydro.catchmentgriddelineation import CatchmentGridDelineation
		#from archydro.catchmentpolygonprocessing import CatchmentPolygonProcessing
		#from archydro.adjointcatchmentprocessing import AdjointCatchmentProcessing
		#from archydro.drainagepointprocessing import DrainagePointProcessing
	else: # for python 2
		#from ArcHydroTools import StreamDefinition
		#from ArcHydroTools import StreamSegmentation
		from ArcHydroTools import DrainageLineProcessing
		from ArcHydroTools import CombineStreamLinkAndSinkLink
		from ArcHydroTools import CatchmentGridDelineation
		from ArcHydroTools import CatchmentPolyProcessing
		from ArcHydroTools import AdjointCatchment
		from ArcHydroTools import DrainagePointProcessing

	arcpy.AddMessage("Starting Post HydroDEM Processing.")

	arcpy.env.extent = facPth
	arcpy.env.snapRaster = facPth
	arcpy.env.cellsize = facPth
	arcpy.env.overwriteOutput = True
	arcpy.AddMessage("	Environment set.")

	finalSpace = os.path.split(workspace)[0]

	fac = Raster(facPth)
	# generate the str900 grid
	str900Pth = os.path.join(finalSpace,'str900')
	str900 = Con(fac > thresh2,1,None)
	str900.save(str900Pth)
	arcpy.AddMessage("	str900 created.")

	# generate the str grid
	streamPth = os.path.join(finalSpace,'str')
	stream = Con(fac > thresh1,1,None)
	stream.save(streamPth)
	arcpy.AddMessage("	str raster created.")

	# generate the stream link grid
	if sinksPth != None:
		lnkPth = os.path.join(finalSpace,'strlnk')
	else:
		lnkPth = os.path.join(finalSpace, 'lnk')
	
	lnk = StreamLink(stream,fdrPth)
	lnk.save(lnkPth)
	arcpy.AddMessage("	lnk raster created.")

	del lnk
	del stream

	# Drainage Line
	drainLinePth = os.path.join(workspace,'drainageLine')
	DrainageLineProcessing(lnkPth,fdrPth,drainLinePth)
	arcpy.AddMessage("	drainageLine features created.")

	if sinksPth != None: # combine sink link and stream link if sink link exists
			newlnkPth = os.path.join(finalSpace,'lnk')
			CombineStreamLinkAndSinkLink(lnkPth,sinksPth,newlnkPth)
			lnkPth = newlnkPth
			arcpy.AddMessage("	snklnk merged with lnk raster.")

	catPth = os.path.join(finalSpace,'cat')
	CatchmentGridDelineation(fdrPth,lnkPth,catPth)
	arcpy.AddMessage("	cat raster created.")

	catchmentPth = os.path.join(workspace,'catchment')
	CatchmentPolyProcessing(catPth,catchmentPth)
	arcpy.AddMessage("	catchment features created.")


	adjointPth = os.path.join(workspace,'adjointCatchment')
	AdjointCatchment(drainLinePth, catchmentPth,adjointPth)
	arcpy.AddMessage("	adjointCatchment features created.")

	dpPth = os.path.join(workspace,'drainagePoint')
	DrainagePointProcessing(facPth,catPth, catchmentPth,dpPth)
	arcpy.AddMessage("	drainagePoint features created.")

	#arcpy.AddMessage("	Moving rasters out of\n\n%s\n\nto\n\n%s"%(workspace,finalSpace))
	rasters = ['hydrodem','hydrodemfac','hydrodemfdr', 'hydrodemfac_global']

	moveRasters(workspace,finalSpace,rasters)

def moveRasters(source, dest, rasters, fmt = None):
	''' Move raster out of a working geodatabase to a destination folder.'''
	arcpy.AddMessage("		Moving %s rasters from:"%(len(rasters)))
	arcpy.AddMessage("\n")
	arcpy.AddMessage("		%s"%source)
	arcpy.AddMessage("\n")
	arcpy.AddMessage("		To:")
	arcpy.AddMessage("\n")
	arcpy.AddMessage("		%s"%dest)
	for rast in rasters:
		arcpy.AddMessage("			%s"%rast)

	arcpy.AddMessage("		######################")
	arcpy.AddMessage("		######################")

	for rast in rasters:
		if arcpy.Exists(os.path.join(source,rast)):
			outRast = rast # keep original format
			if fmt != None:
				outRast = "%s.%s"%(rast,fmt)

			arcpy.AddMessage("		Moving %s"%rast)
			tmp = Raster(os.path.join(source,rast))
			tmp.save(os.path.join(dest,outRast))
			del tmp
		else:
			arcpy.AddMessage("		%s not found!"%rast)