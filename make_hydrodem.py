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
		ESRI ArcPy extent string.

	lRaster : str
		Path to raster dataset.

	Returns
	-------
	extent : str
		ESRI ArcPy extent string.
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
	'''Generates the input datasets from hydrography features for enforcing a bathymetic gradient in hydroDEM (bowling).
	
	Parameters
	----------
	workspace : str
		Path to the geodatabase workspace.
	snapGrid : str
		Path to the raster snap grid used for the project.
	hucPoly : str
		Path to the bounding polygon for the local folder for which inputs are generated.
	hydrographyArea : str
		Path to the double line stream features.
	hydrographyFlowline : str
		Path to the flowline features.
	hydrographyWaterbody : str
		Path to the waterbody features.
	cellsize : str
		Output cell size to use for rasterization.
	version : str (optional)
		Package version number.

	Returns
	-------
	hydro_flowlines : raster
		Grid representation of flowlines.
	hydro_areas : raster
		Grid representation of double line streams and flowlines.

	Notes
	-----
	Outputs are written to the workspace.
	'''
	if version:
		arcpy.AddMessage('StreamStats Data Preparation Tools version: %s'%(version))

	arcpy.env.overwriteOutput = True # Set script to overwrite if files exist
	arcpy.AddMessage("Starting Bathymetric Gradient Preparations....")

	# Set the Geoprocessing environment...
	arcpy.env.scratchWorkspace = workspace
	arcpy.env.workspace = workspace

	# test if input files are present
	inputFiles = [snapGrid, hucPoly, hydrographyArea, hydrographyFlowline, hydrographyWaterbody]
	for fl in inputFiles:
		if arcpy.Exists(fl) == False:
			arcpy.AddMessage('%s missing.'%fl)
			arcpy.AddMessage('Please supply required input. Stopping program.')
			sys.exit(0)

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
	outraster1 = "hydro_flowlines"
	outraster2 = "hydro_areas"

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

def coastaldem(Input_Workspace, grdNamePth, InFeatureClass, OutRaster, seaLevel, version = None):
	'''Sets elevations for water and other areas in digital elevation model.

	Parameters
	----------
	Input_Workspace : str
		Input workspace, output raster will be written to this location.
	grdNamePth : str
		Path to the input DEM grid.
	InFeatureClass : str
		Path to the LandSea feature class.
	OutRaster : str
		Output DEM grid name.
	seaLevel : float
		Elevation at which to make the sea.
	version : str (optional)
		StreamStats Data Preparation Tools version number
	
	Returns
	-------
	OutRaster : raster
		Output raster with coastal areas corrected.

	Notes
	-----
	Outputs are written to the workspace.
	'''
	if version:
		arcpy.AddMessage('StreamStats Data Preparation Tools version: %s'%(version))

	try:
		# set working folder
		arcpy.env.workspace = Input_Workspace
		arcpy.env.scratchWorkspace = arcpy.env.workspace

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
	'''Hydro-enforce a DEM using hydrography data sets.

	This function is used by the National StreamStats Team as the optimal approach for preparing a state's physiographic datasets for watershed delineations. It takes as input, a digital elevation model (DEM), and enforces this data to recognize the supplied hydrography as correct. Supplied watershed boundaries can also be recognized as correct if available for a given state/region. This function assumes that the DEM has first been projected to a state's projection of choice. This function prepares data to be used in the ESRI ArcHydro data model (the GIS database environment for National StreamStats).

	Parameters
	----------
	outdir : DEworkspace
		Working directory.
	huc8cov : DEFeatureClass
		Local division feature class, often HUC8, this will be the outer wall of the hydroDEM.
	origdemPth : str
		Path to the original, projected DEM.
	dendrite : str
		Path to the dendrite feature class to be used.
	snap_grid : str
		Path to a raster dataset to use as a snap_grid to align all the watersheds, often the same as the DEM.
	bowl_polys : str
		Path to the bowling area raster generated from the bathymetric gradient tool.
	bowl_lines : str
		Path to the bowling line raster generated from the bathymetric gradient tool.
	inwall : str
		Path to the feature class to be used for inwalling.
	drainplug : 
		Path to the feature class used for inserting sinks into the dataset.
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
		Path to scratch workspace.
	version : str (optional)
		Package version number.

	Returns (saved to outDIR)
	-------
	filldem : raster
		hydro-enforced DEM raster grid saved to outDir.
	fdirg : raster
		HydroDEM FDR raster grid saved to outDir.
	faccg : raster
		HydroDEM FAC raster grid saved to outDir.
	sink_path : feature class
		Sink feature class saved to outDir.
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

	if (bowl_polys == None) or (bowl_lines == None):
		bowl_bypass = True

	arcpy.AddMessage('bowl_bypass is %s'%str(bowl_bypass))
	arcpy.AddMessage('dp_bypass is %s'%str(dp_bypass))
	arcpy.AddMessage('iw_bypass is %s'%str(iw_bypass))

	# test if full path datasets exist
	for fl in [outdir,origdemPth,snap_grid,scratchWorkspace]:
		assert arcpy.Exists(fl) == True, "%s does not exist"%(fl)

	dsc = arcpy.Describe(snap_grid) 
	assert dsc.extent.XMin % 1 == 0, "Snap Grid origin not divisible by 1."

	# set working directory and environment
	arcpy.env.workspace = outdir
	arcpy.env.cellSize = cellsz
	arcpy.env.overwriteOutput = True
	arcpy.env.scratchWorkspace = scratchWorkspace
	arcpy.env.outputCoordinateSystem = origdemPth
	arcpy.env.snapRaster = snap_grid

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
		print(fl)

	for fl in testDsets:
		arcpy.AddMessage("Checking if %s exists."%(fl))
		assert arcpy.Exists(fl) == True, "%s does not exist"%(fl)

	tmpLocations = [] # make a container for temp locations that will be deleted at the end

	# buffer the huc8cov
	hucbuff = os.path.join(arcpy.env.workspace,'hucbuff') # some temp location
	tmpLocations.append(hucbuff)
	arcpy.AddMessage('	Buffering Local Divisons')
	arcpy.Buffer_analysis(huc8cov, hucbuff, buffdist) # do we need to buffer if this is done in the setup tool, maybe just pass hucbuff to the next step from the parameters...
	arcpy.AddField_management(hucbuff,"dummy","SHORT",None,None,None,None,"NULLABLE","NON_REQUIRED",None)
	arcpy.CalculateField_management(hucbuff,"dummy","1", "PYTHON")

	arcpy.env.extent = hucbuff # set the extent to the buffered HUC

	# rasterize the buffered local division
	arcpy.AddMessage('	Rasterizing %s'%hucbuff)
	outGrid = os.path.join(arcpy.env.workspace,'hucbuffRast')
	tmpLocations.append(outGrid)
	arcpy.PolygonToRaster_conversion(hucbuff,"dummy",outGrid,cellsize = cellsz)

	# rasterize the dendrite
	arcpy.AddMessage('	Rasterizing %s'%dendrite)
	dendriteGridpth = os.path.join(arcpy.env.workspace,'tmpDendriteRast')
	tmpLocations.append(dendriteGridpth)

	# may need to add a field to dendrite to rasterize it...
	arcpy.AddField_management(dendrite,"dummy","SHORT",None,None,None,None,"NULLABLE","NON_REQUIRED",None)
	arcpy.CalculateField_management(dendrite,"dummy","1", "PYTHON")
	arcpy.FeatureToRaster_conversion(dendrite,"dummy",dendriteGridpth, cell_size = cellsz)
	dendriteGrid = Raster(dendriteGridpth)
	
	origdem = Raster(origdemPth)

	arcpy.env.mask = outGrid # set mask (L169 in hydroDEM_work_mod.aml)

	elevgrid = agree(origdem, dendriteGrid, int(agreebuf), int(agreesmooth), int(agreesharp)) # run agree function
	
	# burning streams and adding walls
	arcpy.AddMessage('	Starting Walling') # (L182 in hydroDEM_work_mod.aml)

	ridgeNLpth = os.path.join(arcpy.env.workspace,'ridgeRast')
	tmpLocations.append(ridgeNLpth)
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

	if not dp_bypass: # (if bypass is false, as in do not bypass) dp_bypass is defined after the main code in the original AML
		if int(arcpy.GetCount_management(drainplug).getOutput(0)) > 0:
			dpg_path = os.path.join(arcpy.env.workspace,'sinklnk')
			#tmpLocations.append(dpg_path)
			#arcpy.AddField_management(drainplug,"dummy","SHORT",None,None,None,None,"NULLABLE","NON_REQUIRED",None)
			#arcpy.CalculateField_management(drainplug,"dummy","1", "PYTHON")
			arcpy.FeatureToRaster_conversion(drainplug,"OBJECTID",dpg_path,cell_size = cellsz) # (L195 in hydroDEM_work_mod.aml)
			dpg = Raster(dpg_path) # load the raster object
		else:
			tmp = CreateConstantRaster(0) # if the feature class is empty, make a dummy raster
			dpg = SetNull(tmp,tmp,"VALUE = 0") # set all zeros to null.
	else: # if the drain pugs are bypassed
		arcpy.AddMessage("	Bypassing Drain Plugs")
		tmp = CreateConstantRaster(0) # if the feature class is empty, make a dummy raster
		dpg = SetNull(tmp,tmp,"VALUE = 0") # set all zeros to null.

	if not bowl_bypass: # (if bypass is false, as in do not bypass) bowl_bypass is defined after the main code in the original AML
		arcpy.AddMessage('	Starting Bowling')
		blp_name = os.path.join(arcpy.env.workspace,'blp')
		tmpLocations.append(blp_name)

		bowlLines = Raster(bowl_lines)

		#arcpy.MosaicToNewRaster_management([bowlLines,dpg],arcpy.env.workspace,blp_name, None, "32_BIT_SIGNED", None, 1, "FIRST") # probably need some more options
		#blp = Raster(blp_name)
		#eucd = SetNull(IsNull(bowl_polys), EucDistance(blp)) # (L210 in hydroDEM_work_mod.aml)
		
		eucd = SetNull(IsNull(bowl_polys), EucDistance(bowlLines)) # (L210 in hydroDEM_work_mod.aml)
		demRidge8wb = demRidge8 - Con(IsNull(eucd) == 0, (bowldepth / (eucd+1)), 0)
		#demRidge8wb.save(os.path.join(arcpy.env.workspace,'demRidge8wb'))
		arcpy.AddMessage('	Bowling complete')

	else: # if bypass is true, skip 
		demRidge8wb = demRidge8
		arcpy.AddMessage('	Bowling Skipped')

	if not iw_bypass:
		arcpy.AddMessage('	Starting Inwalling')
		iwb_name = os.path.join(arcpy.env.workspace,'tmp_inwall_buff')
		tmpLocations.append(iwb_name)
		if arcpy.Exists(iwb_name):
			arcpy.AddMessage("%s exists, please delete or rename before proceeding."%(iwb_name))
		arcpy.Buffer_analysis(inwall,iwb_name,inwallbuffdist) #(L223 in hydroDEM_work_mod.aml)
		
		tmpGrd_name = os.path.join(arcpy.env.workspace,'tmpGrd')
		tmpLocations.append(tmpGrd_name)

		arcpy.AddField_management(iwb_name,"dummy","SHORT",None,None,None,None,"NULLABLE","NON_REQUIRED",None)
		arcpy.CalculateField_management(iwb_name,"dummy","1", "PYTHON")

		arcpy.FeatureToRaster_conversion(iwb_name,"dummy",tmpGrd_name, cell_size = cellsz)
		tmpGrd = Raster(tmpGrd_name)

		# Only inwalls where there are not streams and there are inwalls.
		dem_enforced = demRidge8wb + Con((IsNull(tmpGrd) == 0) & (IsNull(dendriteGrid)), inwallht, 0) #(L226 in hydroDEM_work_mod.aml) 
		arcpy.AddMessage('	Inwalling Complete')
	else:
		#if arcpy.Exists(dem_enforced):
		#	del dem_enforced
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

	fdirg.save(os.path.join(arcpy.env.workspace,"fdr"))
	del fdirg
	faccg.save(os.path.join(arcpy.env.workspace,"fac"))
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

def agree(origdem, dendrite, agreebuf, agreesmooth, agreesharp):
	'''Function to adjust a DEM to match a vector.
	
	Parameters
	----------
	origdem : Raster Object
		Original DEM with the desired cell size.
	dendrite : Raster Object
		Dendrite feature layer to adjust the DEM.
	agreebuf : float 
		Buffer smoothing distance (same units as horizontal map units).
	agreesmooth : float
		Smoothing distance (same units as the vertical map units).
	agreesharp : float
		Distance for sharp feature (same units as the vertical map units).

	Returns
	-------
	elevgrid : Raster Object
		Conditioned elevation grid.

	Notes
	-----
	Original function by Ferdi Hellweger, http://www.ce.utexas.edu/prof/maidment/gishydro/ferdi/research/agree/agree.html
	'''
	arcpy.AddMessage('	Starting AGREE')

	# code to check that all inputs exist

	cellsize = (float(arcpy.GetRasterProperties_management(origdem, "CELLSIZEX").getOutput(0)) + float(arcpy.GetRasterProperties_management(origdem, "CELLSIZEY").getOutput(0)))/2. # compute the raster cell size

	arcpy.AddMessage('		Setting Environment Variables')
	arcpy.env.extent = origdem # (L130 AGREE.aml)
	arcpy.env.cellSize = cellsize # (L131 AGREE.aml)
	arcpy.env.snapRaster = origdem

	#arcpy.AddMessage('	Rasterizing the Dendrite.')
	#tmpLocations = []
	#dendriteGridPth = os.path.join(arcpy.env.workspace,'tmpDendrite') # might need to add a field for rasterization
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

def adjust_accum(facPth, fdrPth, upstreamFACpths,upstreamFDRpths, workspace, version = None):
	'''Adjust a downstream flow accumulation (FAC) raster based on upstream flow accumulation rasters.

	This function adjusts the FAC of a downstream HUC to include flow accumulations from upstream HUCs. Run this from the downstream HUC workspace. The function will leave the original FAC grids intact and will create a grid named "fac_global" in the same directory as the original FAC raster. To get true accumulation values in HUCs downstream of other non-headwater HUCs, proceed from upstream HUCs to downstream HUCs in order, and specify the fac_global grid for any upstream HUC that has one. (It is not essential that the fac_global contain true global fac values, and in some cases it is not possible since the values get too large to be stored in a raster file. In practice, as long as the receiving cells have accumulation values larger than the stream definition threshold (150,000 cells for 10-m grids), then the ESRI ArcHydro data model will still function.

	Parameters
	----------
	facPth : str
		Path to downstream flow accumulation grid.
	fdrPth : str
		Path to downstream flow direction grid.
	upstreamFACpths : list
		List of paths to upstream flow accumulation grids.
	upstreamFDRpths : list
		List of paths to upstream flow direction grids.
	workspace : str
		local geodatabase to work in.
	version : str (optional)
		Stream Stats datapreptool version number.
	
	Returns
	-------
	facGlobal : raster
		Adjusted flow accumulation raster created in the same directory as fac.

	Examples
	--------
	adjust_accum("./01010001/fac", 2, ["./01010002/fac", "./01010003/fac"])
	'''
	if version:
		arcpy.AddMessage('StreamStats Data Preparation Tools version: %s'%(version))

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

	downstream.save("fac_global")

def adjust_accum_simple(ptin, fdrin, facin, filin, facout, incrval, version=None):
	'''Simple flow accumulation grid adjustment.

	Adds a value to the flow accumulation grid given an input point using a least-cost-path to cascade down through the flow direction grid.
	
	Parameters
	----------
	ptin : str (feature class)
		Point feature class representing one inlet to the downstream DEM.
	fdrin : str (raster)
		Flow direction raster.
	facin : str (raster)
		Name of the flow accumulation raster.
	filin : str (raster)
		Burned DEM to use as cost surface.
	facout : str (raster)
		Output name of adjusted FAC grid.
	incrval : int
		Value to adjust the downstream FAC grid by.
	version : str
		Stream Stats version number.

	Returns
	-------
	hydrodemfac_global : raster
		Adjusted FAC grid written to facout.
	
	'''

	if version:
		arcpy.AddMessage('StreamStats Data Preparation Tools version: %s'%(version))

	# check that everything exists
	for fl in [ptin, facin, filin]:
		assert arcpy.Exists(fl) == True, "%s does not exist."%(fl)

	arcpy.env.workspace = os.path.dirname(facin) # set workspace
	arcpy.env.scratchWorkspace = arcpy.env.workspace
	arcpy.env.snapRaster = fdrin
	arcpy.env.outputCoordinateSystem = fdrin
	arcpy.env.extent = fdrin
	arcpy.env.overwriteOutput = True

	if sys.version_info[0] >= 3:
		arcpy.AddMessage("\tComputing least-cost-path.")
		costPth = CostPath(ptin,filin,fdrin,path_type = "EACH_CELL", force_flow_direction_convention = "FLOW_DIRECTION", destination_field = "OBJECTID") # compute least cost path downstream from inlet point.
	else:
		arcpy.AddMessage("\tComputing least-cost-path.")
		costPth = CostPath(ptin,filin,fdrin,path_type = "EACH_CELL", destination_field = "OBJECTID")
	
	c = Con(costPth, incrval) # convert the cost path to the increase value
	c.save('costPath')
	c1 = Con(IsNull(c),0,incrval) # fill with zeros
	arcpy.AddMessage("\tComputing correction raster.")

	FAC = Raster(facin) # load the FAC raster to be corrected
	correction = Con(IsNull(FAC),FAC,c1) # fill the edges with NoData
	correction.save('corr')
	arcpy.AddMessage("\tApplying corretion raster.")
	corrFAC = FAC + correction # add the correction, hopefully this doesn't overwrite no data values on the FAC grid.

	corrFAC.save(facout) # save the output raster
	arcpy.AddMessage("\tDone!")
	return None

def postHydroDEM(workspace, facPth, fdrPth, thresh1, thresh2, sinksPth = None, version = None):
	'''Generate stream reaches, adjoint catchments, and drainage points

	Parameters
	----------
	workspace : str
		database-type workspace to output rasters and feature classes.
	facPth : str
		Path to the flow accumulation grid produced by hydroDEM.
	fdrPth : str
		Path to the flow direction grid produced by hydroDEM.
	thresh1 : int
		Threshold used to produce the str grid, in raster cells, usually equal to 15,000,000 :math:`m^2`.
	thresh2 : int
		Threshold used to produce the str900 grid or similar, in raster cells, usually equal to 810,000 :math:`m^2`.
	sinksPth : str (optional)
		Path to the snklnk grid, optional.
	version : str (optional)
		StreamStats DataPrepTools version to be printed.

	Returns
	-------
	str : raster
		Stream raster where fac > 15,000,000 :math:`m^2`.
	str<thresh2> : raster
		Stream raster where fac > 810,000 :math:`m^2`.
	strlnk : raster
		Raster with streams labeled with index values.
	lnk : raster
		Merged stream and sink raster.
	cat : raster
		Catchment raster.
	drainageLine : feature class
		Vectorized streams.
	catchment : feature class
		Vectorized catchments.
	adjointCatchment : feature class
		Vectorized catchments for use in delineation.
	drainagePoint : feature class
		Point located at the greatest flow accumulation value in each catchment.
		
	Notes
	-----
	This tool requires ESRI ArcHydro to be installed and currently only works with Python 2.
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
	str900Pth = os.path.join(finalSpace,'str'+str(thresh2))
	str900 = Con(fac > thresh2,1,None)
	str900.save(str900Pth)
	arcpy.AddMessage("	str%s created."%(str(thresh2)))

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

	
	sr = arcpy.Describe(facPth).spatialReference
	arcpy.CreateFeatureDataset_management(workspace,'Layers',sr) # create featureDataset

	# Drainage Line
	drainLinePth = os.path.join(workspace,'drainageLine_tmp')
	DrainageLineProcessing(lnkPth,fdrPth,drainLinePth)
	arcpy.Copy_management(drainLinePth, os.path.join(workspace,'Layers','drainageLine')) # import drainage line into feature dataset
	arcpy.AddMessage("	DrainageLine features created.")

	if sinksPth != None: # combine sink link and stream link if sink link exists
			newlnkPth = os.path.join(finalSpace,'lnk')
			CombineStreamLinkAndSinkLink(lnkPth,sinksPth,newlnkPth)
			lnkPth = newlnkPth
			arcpy.AddMessage("	snklnk merged with lnk raster.")

	catPth = os.path.join(finalSpace,'cat')
	CatchmentGridDelineation(fdrPth,lnkPth,catPth)
	arcpy.AddMessage("	Cat raster created.")

	catchmentPth = os.path.join(workspace,'catchment_tmp')
	CatchmentPolyProcessing(catPth,catchmentPth)
	arcpy.Copy_management(catchmentPth, os.path.join(workspace,'Layers','catchment'))
	arcpy.AddMessage("	Catchment features created.")


	adjointPth = os.path.join(workspace,'adjointCatchment_tmp')
	AdjointCatchment(drainLinePth, catchmentPth,adjointPth)
	arcpy.Copy_management(adjointPth,os.path.join(workspace,'Layers','adjointCatchment'))
	arcpy.AddMessage("	AdjointCatchment features created.")

	dpPth = os.path.join(workspace,'drainagePoint_tmp')
	DrainagePointProcessing(facPth,catPth, catchmentPth,dpPth)
	arcpy.Copy_management(dpPth, os.path.join(workspace,'Layers','drainagePoint'))
	arcpy.AddMessage("	DrainagePoint features created.")

	arcpy.AddMessage("  Cleaning Up.")
	arcpy.Delete_management(drainLinePth) # clean up
	arcpy.Delete_management(adjointPth)
	arcpy.Delete_management(catchmentPth)
	arcpy.Delete_management(dpPth)

	

	#arcpy.AddMessage("	Moving rasters out of\n\n%s\n\nto\n\n%s"%(workspace,finalSpace))
	rasters = ['hydrodem','fac','fdr', 'hydrodemfac_global']

	moveRasters(workspace,finalSpace,rasters)


def moveRasters(source, dest, rasters, fmt = None):
	''' Move raster out of a working geodatabase to a destination folder.

	Parameters
	----------
	source : str
		Path to geodatabase containing the rasters.
	dest : str
		Path to destination location.
	rasters : list
		List of rasters to move from source to dest.
	fmt : str (optional)
		Extension indicating the raster format the output without the leading period, e.g. "tif".

	Returns
	-------
	None
	'''
	
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
			
			if fmt == None and len(rast) > 13: # if unformatted, truncate name to 13 characters.
				outRast = rast[0:13] # keep original format
			else: 
				outRast = rast

			if fmt != None:
				outRast = "%s.%s"%(rast,fmt)

			arcpy.AddMessage("		Moving %s"%rast)
			tmp = Raster(os.path.join(source,rast))
			tmp.save(os.path.join(dest,outRast))
			del tmp
		else:
			arcpy.AddMessage("		%s not found!"%rast)