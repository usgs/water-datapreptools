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

def bathymetricGradient(workspace, snapGrid, hucPoly, hydrographyArea, hydrographyFlowline, hydrographyWaterbody,cellsize):
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

	Returns
	-------
	
	'''
	arcpy.env.overwriteOutput = True # Set script to overwrite if files exist
	arcpy.AddMessage("Starting Bathymetric Gradient Preparations....")

	# Set the Geoprocessing environment...
	arcpy.env.scratchworkspace = workspace
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
	outraster1 = os.path.join(arcpy.env.workspace,"wb_srcg")
	outraster2 = "nhd_wbg"

	#convert to temporary shapefiles
	arcpy.FeatureClassToFeatureClass_conversion(hydrographyArea, arcpy.env.workspace, nhd_area_feat)
	arcpy.AddField_management(nhd_area_feat,"dummy","SHORT",None,None,None,None,"NULLABLE","NON_REQUIRED",None)
	arcpy.CalculateField_management(nhd_area_feat,"dummy","1")

	arcpy.FeatureClassToFeatureClass_conversion(hydrographyWaterbody, arcpy.env.workspace, nhd_wb_feat)
	arcpy.AddField_management(nhd_wb_feat,"dummy","SHORT",None,None,None,None,"NULLABLE","NON_REQUIRED",None)
	arcpy.CalculateField_management(nhd_wb_feat,"dummy","1")

	arcpy.FeatureClassToFeatureClass_conversion(hydrographyFlowline, arcpy.env.workspace, nhd_flow_feat)
	arcpy.AddField_management(nhd_flow_feat,"dummy","SHORT",None,None,None,None,"NULLABLE","NON_REQUIRED",None)
	arcpy.CalculateField_management(nhd_flow_feat,"dummy","1")

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

def coastaldem(Input_Workspace, grdName, InFeatureClass, OutRaster, seaLevel):
	'''Sets elevations for water and other areas in DEM

	Originally:
		Al Rea, ahrea@usgs.gov, 05/01/2010, original coding
		ahrea, 10/30/2010 updated with more detailed comments
		Theodore Barnhart, 20190225, tbarnhart@usgs.gov, updated to arcpy

	Parameters
	----------
	Input_Workspace : str
		Input workspace
	grdName : str
		Input DEM grid.
	InFeatureClass : str
		LandSea feature class
	OutRaster : str
		Output DEM grid
	seaLevel : float
		Elevation at which to make the sea
	
	Returns
	-------
	OutRaster : raster
	'''

	try:
		# set working folder
		arcpy.env.workspace = Input_Workspace
		arcpy.env.scratchWorkspace = arcpy.env.Workspace

		arcpy.env.extent = grdName
		arcpy.env.snapRaster = grdName
		arcpy.env.outputCoordinateSystem = grdName
		arcpy.env.cellSize = grdName
		#cellsz = grdName.Cellsize

		#buffg = polygrid (hucbufland)
		arcpy.PolygonToRaster_conversion(InFeatureClass, "Land", "mskg")
		
		mskg = Raster("mskg") # load the mask grid
		grdName = Raster()
		
		seag = Con(mskg == -1, float(seaLevel))

		landg = Con((mskg == 1) and grdName <= 0, 1, grdName)
		#seaGrd = con(mskGrd == -1, seaLevel)
		#strCmd = "con('%s' == %s, %s)" % ("mskg", "-1", seaLevel)
		#arcpy.AddMessage(strCmd)
		#arcpy.SingleOutputMapAlgebra_sa(strCmd, "seag")

		#landGrd = con(mskGrd == 1 and grdName <= 0, 1, grdName)
		strCmd = "con(%s == 1 and %s <= 0, %s, %s)" % ("mskg", grdName, "1", grdName)
		arcpy.AddMessage(strCmd)
		arcpy.SingleOutputMapAlgebra_sa(strCmd, "landg")

		#nochgGrd = con(mskGrd == 0, grdName)
		strCmd = "con('%s' == %s, %s)" % ("mskg", "0", grdName)
		arcpy.AddMessage(strCmd)
		arcpy.SingleOutputMapAlgebra_sa(strCmd, "nochgg")


		strMosaicList = "seag, landg, nochgg"
		strCmd = "merge (" + strMosaicList + ")"
		arcpy.AddMessage(strCmd)
		arcpy.SingleOutputMapAlgebra_sa(strCmd, OutRaster)

		arcpy.AddMessage("Removing temporary grids ... ")
		#gp.delete_management("mskg")
		#gp.delete_management("seag")
		#gp.delete_management("landg")
		#gp.delete_management("nochgg")
	except:
		e = sys.exc_info()[1]
		print(e.args[0])
		arcpy.AddError(e.args[0])

		# handle errors and report using GPMsg function
	#except MsgError, xmsg:
	#	arcpy.AddError(str(xmsg))
	#except arcpy.ExecuteError:
	#	line, file, err = TraceInfo()
	#	arcpy.AddError("Geoprocessing error on %s of %s:" % (line,file))
	#	for imsg in range(0, arcpy.MessageCount):
	#		if arcpy.GetSeverity(imsg) == 2:     
	#			arcpy.AddReturnMessage(imsg) # AddReturnMessage
	#except:  
	#	line, file, err = TraceInfo()
	#	arcpy.AddError("Python error on %s of %s" % (line,file))
	#	arcpy.AddError(err)
	#finally:
		# Clean up here (delete cursors, temp files)
	#	pass # you need *something* here 

	return None

def hydrodem(outdir, huc8cov, origdem, dendrite, snap_grid, bowl_polys, bowl_lines, inwall, drainplug, start_path, buffdist, inwallbuffdist, inwallht, outwallht, agreebuf, agreesmooth, agreesharp, bowldepth, copylayers, cellsz, bowling, in_wall, drain_plugs):
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
		Local division feature class, often HUC8
	origdem :

	dendrite :
	
	snap_grid :
	
	bowl_polys :
	
	bowl_lines :
	
	inwall : 
	
	drainplug : 
	
	start_path :
	
	buffdist :
	
	inwallbuffdist :
	
	inwallht :
	
	outwallht :
	
	agreebuf :
	
	agreesmooth :
	
	agreesharp :
	
	bowldepth :
	
	copylayers :
	
	cellsz :
	
	bowling :
	
	in_wall :
	
	drain_plugs :

	Returns
	-------
	filldem : arcpy.sa Raster
		hydro-enforced, filled DEM
	fdirg : arcpy.sa Raster
		flow direction grid cooresponding to filldem
	faccg : arcpy.sa Raster
		flow accumulation grid cooresponding to filldem
	sink_path : path
		path to sink feature class

	'''
	arcpy.AddMessage("HydroDEM is running")

	## put some checks here about the _bypass variables
	dp_bypass = False
	iw_bypass = False
	bowl_bypass = False

	if in_wall is None:
		iw_bypass == True

	if drain_plugs is None:
		dp_bypass == True

	if (bowl_polys is None) or (bowl_lines is None):
		bowl_bypass == True

	# set working directory and environment
	arcpy.env.workspace = outdir
	arcpy.env.cellSize = cellsz

	tmpLocations = [] # make a container for temp locations that will be deleted at the end

	# buffer the huc8cov
	hucbuff = 'hucbuff' # some temp location
	tmpLocations.append(hucbuff)
	arcpy.AddMessage('Buffering Local Divisons')
	arcpy.Buffer_analysis(huc8cov,hucbuff) # do we need to buffer if this is done in the setup tool, maybe just pass hucbuff to the next step from the parameters...

	arcpy.env.Extent = hucbuff # set the extent to the buffered HUC

	# rasterize the buffered local division
	arcpy.AddMessage('Rasterizing %s'%hucbuff)
	outGrid = 'hucbuffRast'
	tmpLocations.append(hucbuffRast)
	# may need to add a field to hucbuff to rasterize it... 
	arcpy.FeaturetoRaster_conversion(hucbuff,None,outGrid,cellsz)

	arcpy.env.mask = outGrid # set mask (L169 in hydroDEM_work_mod.aml)

	elevgrid = agree(origdem, dendrite, agreebuf, agreesmooth, agreesharp) # run agree function

	# rasterize the dendrite
	arcpy.AddMessage('Rasterizing %s'%dendrite)
	dendriteGridpth = 'tmpDendriteRast'
	tmpLocations.append(dendriteGridpth)

	# may need to add a field to dendrite to rasterize it...
	arcpy.FeaturetoRaster_conversion(dendrite,None,dendriteGridpth,cellsz)
	dendriteGrid = Raster(dendriteGridpth)
	# burning streams and adding walls
	arcpy.AddMessage('Starting Walling') # (L182 in hydroDEM_work_mod.aml)

	ridgeNLpth = 'ridgeRast'
	tmpLocations.append(ridgeNLpth)
	# may need to add a field to huc8cov to rasterize it...
	arcpy.FeaturetoRaster_conversion(huc8cov,None,ridgeNLpth,cellsz) # rasterize the local divisions feature
	#ridgeEXP = 'some temp location'
	ridgeNL = Raster(ridgeNLpth) # load ridgeNL 
	outRidgeEXP = Expand(ridgeNL,2,[1]) # the last parameter is the zone to be expanded, this might need to be added to the dummy field above... 
	#outRidgeEXP.save(ridgeEXP) # save temperary file, maybe not needed

	ridgeW = SetNull((not IsNull(ridgeNL)) and (not IsNull(ridgeEXP)), ridgeEXP)
	demRidge8 = elevgrid + Con((not IsNull(ridgeW)) and (IsNull(nhd)), outwallht, 0)

	arcpy.AddMessage('Walling Complete')

	if dp_bypass == False: # dp_bypass is defined after the main code in the original AML
		dpg_path = 'depressionRast'
		tmpLocations.append(dpg_path)
		arcpy.FeaturetoRaster_conversion(drainplug,None,dpg_path,arcpy.env.cellSize) # (L195 in hydroDEM_work_mod.aml)
		dpg = Raster(dpg_path) # load the raster object

	if bowl_bypass == False: # bowl_bypass is defined after the main code in the original AML
		arcpy.AddMessage('Starting Bowling')
		blp_name = 'blp'
		tmpLocations.append(blp_name)
		inPaths = '%s;%s'%(bowl_lines,dpg_path)
		arcpy.MosaicToNewRaster_management(inPaths,arcpy.env.workspace,blp_name) # probably need some more options

		blp = Raster(blp_name)

		eucd = SetNull(IsNull(bowl_polys), EucDistance(blp)) # (L210 in hydroDEM_work_mod.aml)
		demRidge8wb = demRidge8 - Con(not IsNull(eucd), (bowldepth / (eucd+1)), 0)

		arcpy.AddMessage('Bowling complete')

	else:
		arcpy.AddMessage('Bowling Skipped')

	if iw_bypass == False:
		arcpy.AddMessage('Starting Walling')
		iwb_name = 'inwall_buff'
		tmpLocations.append(iwb_name)
		#iwb_path = os.path.join(arcpy.env.workspace,iwb_name)
		arcpy.Buffer_analysis(inwall,iwb_name,inwallbuffdist) #(L223 in hydroDEM_work_mod.aml)
		
		tmpGrd_name = 'tmpGrd'
		tmpLocations.append(tmpGrd_name)

		arcpy.FeaturetoRaster_conversion(iwb_path,arcpy.env.workspace,tmpGrd_name)
		tmpGrd = Raster(tmpGrd_name)

		inwallg = Con(tmpGrd == 100, 0)
		dem_enforced = demRidge8wb + Con((not IsNull(inwallg) and IsNull(nhdgrd)), inwallht, 0) #(L226 in hydroDEM_work_mod.aml)

		arcp.AddMessage('Walling Complete')
	else:
		del dem_enforced
		dem_enforced = demRidge8wb
		arcpy.AddMessage('Walling Skipped')

	if dp_bypass == False:
		detmp = Con(IsNull(dpg),dem_enforced)
		del dem_enforced
		dem_enforced = detmp #(L242 in hydroDEM_work_mod.aml)

	arcpy.env.extent(hucbuff)
	arcpy.env.snapRaster(snap_grid)
	arcpy.cellSize(origdem)

	arcpy.AddMessage('Start Fill')

	filldem,fdirg = fill(dem_enforced, "sink", None, fdirg)

	arcpy.AddMessage('Fill Complete')


	if dp_bypass == False:
		fdirg2 = FlowDirection(filldem, None, 'Force')
		fdirg = Con(IsNull(dpg), fdirg2, 0) # (L256 in hydroDEM_work_mod.aml), insert a zero where drain plugs were.

	arcpy.env.mask = ridgeNLpth # mask to HUC

	# might need to save the fdirg, delete it from the python workspace, and reload it...
	arcpy.AddMessage('Starting Flow Accumulation')
	faccg = FlowAccumulation(fdirg, None, "INTEGER")
	arcpy.AddMessage('Flow Accumulation Complete')

	arcpy.AddMessage('Creating Sink Features')
	fsinkg = Con((filldem - origdem) > 1, 1)
	#fsinkg_name = 'fsinkg'
	#fsinkg_path = os.path.join(arcpy.env.workspace,fsinkc_name)
	#fsinkg.save(fsinkg_path)
	#del fsinkg # clean up
	
	fsinkc_name = 'fsinkc'
	fsinkc_path = os.path.join(arcpy.env.workspace,fsinkc_name)
	arcpy.RasterToPolygon_conversion(fsinkg, fsinkc_path, 'NO_SIMPLIFY') # (L273 in hydroDEM_work_mod.aml), outputs fsinkc
	del fsinkg

	arcpy.AddMessage('Sink Creation Complete')
	arcpy.AddMessage('HydroDEM Complete')

	# clean up the environment of temp files
	#arcpy.Delete_management(fsinkg_path) # clean up
	# more statements needed here...

	for fl in tmpLocations: # delete tmp files
		if arcpy.Exists(fl): arcpy.Delete_management(fl)

	# save the grids to the workspace
	filldem.save("filldem")
	fdirg.save("fdirg")
	faccg.save("faccg")

	return None

def fill(dem, option, zlimit):w

def agree(origdem, dendrite, agreebuf, agreesmooth, agreesharp):wn