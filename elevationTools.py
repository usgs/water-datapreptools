import arcpy
import sys
import os

arcpy.CheckOutExtension("Spatial")

from arcpy.sa import *

def elevIndex(OutLoc, rcName, coordsysRaster, InputELEVDATAws, version = None):
	"""Make a raster mosaic dataset of the digital elevation model geospatial tiles supplied to the function.

	Parameters
	----------
	OutLoc : str
		Path to output location for the raster catalog.
	rcName : str
		Name of the output mosaic raster dataset.
	coordsysRaster : str
		Path to raster from which to base the mosaic dataset's coordinate system.
	InputELEVDATAws : str
		Path to workspace containing the elevation data to be included in the mosaic raster dataset. Rasters in this workspace should be either geoTiffs or ESRI grids. Rasters must be unzipped, but they may be in subfolders.
	version : str (optional)
		StreamStats DataPrepTools version number.
	
	Returns
	-------
	OutFC : feature class
		Output feature class of polygons with an attribute describing the full path to the elevation data tiles.
	
	"""
	if version:
		arcpy.AddMessage('StreamStats Data Preparation Tools version: %s'%(version))

	arcpy.env.overwriteOutput=True

	Output_Raster_Catalog = os.path.join(OutLoc,rcName) 
	Raster_Management_Type = "UNMANAGED"
	coordsysPolys = coordsysRaster     # Coordinate system for polygon footprints. Use same NED grid to specify. (type Spatial Reference)

	if arcpy.Exists(OutLoc): 
		DSType = arcpy.Describe(arcpy.Describe(OutLoc).CatalogPath).WorkspaceType
		arcpy.AddMessage("Dataset type = " + DSType)
		if DSType == "FileSystem":
			arcpy.AddError("Output " + OutLoc + " is not a Geodatabase. Output location must be a Geodatabase.")
			sys.exit(0)
	else:
		arcpy.AddError("Output " + OutLoc + " does not exist")
		sys.exit(0)
	
	# Now that we're sure the geodb exists, make it the active workspace
	arcpy.Workspace = OutLoc
	arcpy.ScratchWorkspace = OutLoc
	arcpy.AddMessage("Working geodatabase is " + OutLoc)

	#if arcpy.Exists(Output_Raster_Catalog): 
	#	arcpy.AddError("Output raster catalog" + Output_Raster_Catalog + "Already exists")
	#	sys.exit(0) # end script

	# Process: Create Raster Catalog...
	arcpy.AddMessage("Creating output mosaic dataset " + Output_Raster_Catalog)
	arcpy.CreateMosaicDataset_management(OutLoc, rcName, coordsysRaster)
	
	# Process: Workspace To Raster Catalog...
	arcpy.AddMessage("Loading all rasters under workspace " + InputELEVDATAws + " into raster mosaic dataset...")

	arcpy.AddRastersToMosaicDataset_management(os.path.join(OutLoc, rcName), "Raster Dataset",InputELEVDATAws, sub_folder = "SUBFOLDERS", update_cellsize_ranges = "UPDATE_CELL_SIZES", update_boundary = "UPDATE_BOUNDARY", update_overviews = "UPDATE_OVERVIEWS", maximum_pyramid_levels = 5)

	return None

def extractPoly(Input_Workspace, nedindx, clpfeat, OutGrd, version = None):
	"""
	Extracts watershed DEM from a raster mosaic dataset of tiles based on a watershed polygon feature.

	Parameters
	----------
	Input_Workspace : str
		Path to the workspace to work in.
	nedindx : str
		Path to the elevation data mosaic dataset.
	clpfeat : str
		Path to the clipping feature.
	OutGrd : str
		Name of the output grid to be generated in Input_Workspace.
	version : str, optional
		StreamStats DataPrepTools version number.

	Returns
	-------
	OutGrd : raster
		Output extracted raster to Input_Workspace.
	"""

	if version:
		arcpy.AddMessage('StreamStats Data Preparation Tools version: %s'%(version))


	# set working folder
	arcpy.env.workspace = Input_Workspace
	arcpy.env.scratchWorkspace = arcpy.env.workspace
	arcpy.env.extent = clpfeat
	#arcpy.env.snapRaster = nedindx
	#arcpy.env.outputCoordinateSystem = nedindx

	dsc = arcpy.Describe(clpfeat)
	ext = dsc.extent
	clpExt = "%s %s %s %s"%(ext.XMin, ext.YMin, ext.XMax, ext.YMax)
	#arcpy.AddMessage(clpExt)
	arcpy.Clip_management(nedindx, clpExt, os.path.join(Input_Workspace,OutGrd), in_template_dataset = clpfeat, nodata_value = -9999, clipping_geometry = "ClippingGeometry", maintain_clipping_extent = "NO_MAINTAIN_EXTENT") # clip the dataset
	arcpy.AddMessage("Clip Complete.")

def checkNoData(InGrid, tmpLoc, OutPolys_shp, version = None):
	"""
	Generates a feature class of no data values.

	Parameters
	----------
	InGrid : Raster
		Input DEM grid to search for no data values.
	tmpLoc : str
		Path to workspace.
	OutPoly_shp : str
		Name for output feature class.
	version : str, optional
		StreamStats DataPrepTools version.

	Returns
	-------
	featCount : int
		Count of no data features generated.
	OutPoly_shp : feature class 
		No data feature class written to tmpLoc.
	
	"""

	arcpy.env.overwriteOutput = True
	if version:
		arcpy.AddMessage('StreamStats Data Preparation Tools version: %s'%(version))


	arcpy.env.extent = InGrid
	arcpy.env.cellSize = InGrid

	InGrid = Raster(InGrid)

	tmpGrid = Con(IsNull(InGrid), 1)

	# Process: Raster to Polygon
	arcpy.RasterToPolygon_conversion(tmpGrid, os.path.join(tmpLoc,OutPolys_shp), "NO_SIMPLIFY", "Value", "SINGLE_OUTER_PART", "")
	featCount = int(arcpy.GetCount_management(os.path.join(tmpLoc,OutPolys_shp)).getOutput(0))
	arcpy.AddMessage("%s no data regions found"%featCount)

	return featCount

def fillNoData(workspace, InGrid, OutGrid, version = None):
	"""Replaces NODATA values in a grid with mean values within 3x3 window around each NODATA value. 
	
	Parameters
	----------
	workspace : str
		Path to the workspace to work in.
	InGrid : str
		Name of the input grid to be filled.
	OutGrid : str
		Name of the output grid.
	Version : str (optional)
		Code version.

	Returns
	-------
	OutGrid : raster
		Filled raster grid output to workspace.
	 
	Notes
	-----
	May be run repeatedly to fill in areas wider than 2 cells. Note that the output is floating point, even if the input is integer. This function will expand the data area of the grid around the outer edges of data, in addition to filling in NODATA gaps in the interior of the grid.
	"""

	if version:
		arcpy.AddMessage('StreamStats Data Preparation Tools version: %s'%(version))

	OutGridPth = os.path.join(workspace, OutGrid)

	arcpy.env.workspace = workspace

	if arcpy.Exists(InGrid) == False:
		arcpy.AddError("Input grid does not exist.")
		sys.exit(0)

	if arcpy.Exists(OutGridPth):
		arcpy.AddError("Output grid exists.")
		sys.exit(0)

	arcpy.env.extent = InGrid
	arcpy.env.cellSize = InGrid
	
	InGrid = Raster(InGrid)
	
	tmpRast = Con(IsNull(InGrid), FocalStatistics(InGrid), InGrid)
	
	tmpRast.save(OutGridPth)

def projScale(Input_Workspace, InGrd, OutGrd, OutCoordsys, OutCellSize, RegistrationPoint, scaleFact = 100, version = None):
	""" Projects a DEM grid to a user-specified coordinate system, handling cell registration and converts the output grid to integers using a scale factor. The default settings assume the digital elevation model uses meters (m) as the z-units.

	Parameters
	----------
	Input_Workspace : str
		Path to input workspace.
	InGrd : str
		Name of the grid to be projected and scaled.
	OutGrd : str
		Name of the output grid.
	OutCoordsys : str
		Path to the dataset to base the projection off of.
	OutCellSize : int or float
		Cell size for output grid.
	RegistrationPoint : str
		Registration point for output grid so all grids snap correctly. In the format "0 0" where the zeros are the x and y of the registration point.
	scaleFact : int
		Scale factor to convert grid values to integers, defaults to 100, converting m to cm.
	version : str
		StreamStats version number.
	
	Returns
	-------
	OutGrd : raster
		Rescaled and projected raster file in the input workspace.
	"""
	
	if version:
		arcpy.AddMessage('StreamStats Data Preparation Tools version: %s'%(version))

	try: 
		# set working folder
		arcpy.env.workspace = Input_Workspace
		arcpy.env.scratchWorkspace = arcpy.env.workspace
		tmpDEM = "tmpDEM"

		assert arcpy.Exists(InGrd), "Raster %s does not exist"%InGrid

		if arcpy.Exists(OutGrd):
			arcpy.Delete_management(OutGrd)

		if arcpy.Exists(tmpDEM):
			arcpy.Delete_management(tmpDEM)

		# clear the processing extent
		arcpy.Extent = ""
		arcpy.OutputCoordinateSystem = ""
		arcpy.SnapRaster = ""
		arcpy.AddMessage("Projecting " + InGrd + " to create " + tmpDEM)
		arcpy.ProjectRaster_management(InGrd, tmpDEM, OutCoordsys, "BILINEAR", OutCellSize, None, RegistrationPoint)

		arcpy.Extent = tmpDEM
		arcpy.OutputCoordinateSystem = OutCoordsys
		arcpy.SnapRaster = tmpDEM
		arcpy.CellSize = tmpDEM

		tmpDEMRAST = Raster(tmpDEM) # load projected raster
		
		arcpy.AddMessage("Scaling original values by %s and coverting to integers to produce %s"%(scaleFact, OutGrd))

		tmp = Int((tmpDEMRAST * scaleFact) +0.5) # convert from m to cm integers if input dem is in m and scaleFact is 100.
		# there should probably be some code here to compute the correct Zunits based on the vertical unit and the scale factor and then a check later to make sure Arc has handled it properly. 

		tmp.save(OutGrd) # save output grid

		sameUnits = compareSpatialRefUnits(OutGrd)

		sr = arcpy.Describe(OutGrd).spatialReference

		if sr.linearUnitName.upper() not in ["FEET","METER"]:
			arcpy.AddMessage("Output grid horizontal units not defined, check horizontal and vertical units.")

		# compute what the zunits should be if horizontal and vertical units are the same. Numerical zUnits should be the number of units needed to equal one meter. https://community.esri.com/thread/31951
		if sr.linearUnitCode == 9002: # EPSG for international foot
			zunits = (1./0.3048) * scaleFact
		elif sr.linearUnitCode == 9001: # EPSG for metre
			origSR = arcpy.Describe(InGrd).spatialReference
			zunits = float(origSR.ZFalseOriginAndUnits.split()[-1]) * scaleFact # for meters
		elif sr.linearUnitCode == 9003: # EPSG for US Survey Foot
			zunits = (1./0.3048006096012192) * scaleFact
		else:
			arcpy.AddMessage("Output grid horizontal units not defined, check horizontal and vertical units.")
			zunits = scaleFact

		if float(sr.ZFalseOriginAndUnits.split()[-1]) != zunits:
			arcpy.AddMessage("Zunits scale factor not set correctly, updating")
			FalseOrigin = sr.ZFalseOriginAndUnits.split()[0]
			sr.setZFalseOriginAndUnits(float(FalseOrigin), zunits)
			arcpy.DefineProjection_management(OutGrd,sr) # actually update the projection here.

		arcpy.AddMessage("Removing temporary grid %s... "%(tmpDEM))
		arcpy.Delete_management(tmpDEM)

	except:
		raise

def compareSpatialRefUnits(grd):
	'''Compare horizontal and vertical units from a raster dataset. Returns True if units are the same, returns False if they are different.

	Parameters
	----------
	grd : str
		Path to raster dataset.

	Returns
	-------
	sameUnits : bool
		True if units are the same, False if not.
	'''

	assert arcpy.Exists(grd), "%s does not exist."%grd

	sr = arcpy.Describe(grd).spatialReference

	zUnitCode = sr.ZFalseOriginAndUnits.split()[-1] # get Zunit scale factor
	xyUnits = sr.linearUnitName

	if zUnitCode == "NO":
		sameUnits = False
		arcpy.AddMessage("Zunits in %s not set and are assumed to be %s"%(xyUnits))
	else:
		sameUnits = True

	return sameUnits

def check_projection(ds1, ds2):
	'''Check if the projections of the two files are the same.

	Parameters
	----------
	ds1 : str
		Path to first geospatial file.
	ds2 : str
		Path to second geospatial file.

	Returns
	-------
	same : bool
		Boolean indicating if the projections are the same or not.

	Notes
	-----
	Slightly modified from Chris Wills' post: https://gis.stackexchange.com/questions/170088/checking-if-two-feature-classes-have-same-spatial-reference-using-arcpy
	'''

	crs1 = arcpy.Describe(ds1).spatialReference
	crs2 = arcpy.Describe(ds2).spatialReference

	try:
		# Consider these
		assert(crs1.name==crs2.name) # The name of the spatial reference.
		assert(crs1.PCSCode==crs2.PCSCode) # The projected coordinate system code.1 
		assert(crs1.PCSName==crs2.PCSName) # The projected coordinate system name.1 
		assert(crs1.azimuth==crs2.azimuth) # The azimuth of a projected coordinate system.1 
		assert(crs1.centralMeridian==crs2.centralMeridian) # The central meridian of a projected coordinate system.1    
		assert(crs1.centralMeridianInDegrees==crs2.centralMeridianInDegrees) # The central meridian (Lambda0) of a projected coordinate system in degrees.1 
		assert(crs1.centralParallel==crs2.centralParallel) # The central parallel of a projected coordinate system.1
		assert(crs1.falseEasting==crs2.falseEasting) # The false easting of a projected coordinate system.1 
		assert(crs1.falseNorthing==crs2.falseNorthing) # The false northing of a projected coordinate system.1  
		assert(crs1.MFalseOriginAndUnits==crs2.MFalseOriginAndUnits) # The measure false origin and units.
		assert(crs1.MResolution==crs2.MResolution) # The measure resolution.
		assert(crs1.MTolerance==crs2.MTolerance) # The measure tolerance.
		assert(crs1.XYTolerance==crs2.XYTolerance) # The xy tolerance.
		assert(crs1.ZDomain==crs2.ZDomain) # The extent of the z domain.
		assert(crs1.ZFalseOriginAndUnits==crs2.ZFalseOriginAndUnits) # The z false origin and units.
		assert(crs1.factoryCode==crs2.factoryCode) # The factory code or well-known ID (WKID) of the spatial reference.
		assert(crs1.isHighPrecision==crs2.isHighPrecision) # Indicates whether the spatial reference has high precision set.
		assert(crs1.latitudeOf1st==crs2.latitudeOf1st) # The latitude of the first point of a projected coordinate system.1
		assert(crs1.latitudeOf2nd==crs2.latitudeOf2nd) # The latitude of the second point of a projected coordinate system.1    
		assert(crs1.latitudeOfOrigin==crs2.latitudeOfOrigin) # The latitude of origin of a projected coordinate system.1    
		assert(crs1.linearUnitCode==crs2.linearUnitCode) # The linear unit code.    
		assert(crs1.linearUnitName==crs2.linearUnitName) # The linear unit name.1
		assert(crs1.longitude==crs2.longitude) # The longitude value of this prime meridian.1
		assert(crs1.longitudeOf1st==crs2.longitudeOf1st) #The longitude of the first point of a projected coordinate system.1
		assert(crs1.longitudeOf2nd==crs2.longitudeOf2nd) # The longitude of the second point of a projected coordinate system.1
		assert(crs1.longitudeOfOrigin==crs2.longitudeOfOrigin) # The longitude of origin of a projected coordinate system.1
		assert(crs1.metersPerUnit==crs2.metersPerUnit) # The meters per linear unit.1
		assert(crs1.projectionCode==crs2.projectionCode) # The projection code.1
		assert(crs1.projectionName==crs2.projectionName) # The projection name.1
		assert(crs1.scaleFactor==crs2.scaleFactor) # The scale factor of a projected coordinate system.1
		assert(crs1.standardParallel1==crs2.standardParallel1) # The first parallel of a projected coordinate system.1
		assert(crs1.standardParallel2==crs2.standardParallel2) # The second parallel of a projected coordinate system.1
		assert(crs1.angularUnitCode==crs2.angularUnitCode) # The angular unit code.2
		assert(crs1.angularUnitName==crs2.angularUnitName) # The angular unit name.2
		assert(crs1.datumCode==crs2.datumCode) # The datum code.2
		assert(crs1.datumName==crs2.datumName) # The datum name.2
		assert(crs1.flattening==crs2.flattening) # The flattening ratio of this spheroid.2
		assert(crs1.longitude==crs2.longitude) # The longitude value of this prime meridian.2
		assert(crs1.primeMeridianCode==crs2.primeMeridianCode) # The prime meridian code.2

		## Prob can be ignored
		if strict:
			assert(crs1.ZResolution==crs2.ZResolution) # The z resolution property.
			assert(crs1.ZTolerance==crs2.ZTolerance) # The z-tolerance property.
			assert(crs1.hasMPrecision==crs2.hasMPrecision) # Indicates whether m-value precision information has been defined.
			assert(crs1.hasXYPrecision==crs2.hasXYPrecision) # Indicates whether xy precision information has been defined.
			assert(crs1.hasZPrecision==crs2.hasZPrecision) # Indicates whether z-value precision information has been defined.
			assert(crs1.XYResolution==crs2.XYResolution) # The xy resolution.
			assert(crs1.domain==crs2.domain) # The extent of the xy domain.
			assert(crs1.MDomain==crs2.MDomain) # The extent of the measure domain.
			assert(crs1.remarks==crs2.remarks) # The comment string of the spatial reference.
			assert(crs1.type==crs2.type) # The type of the spatial reference. Geographic: A geographic coordinate system. Projected: A projected coordinate system.
			assert(crs1.usage==crs2.usage) # The usage notes.   
			assert(crs1.classification==crs2.classification) # The classification of a map projection.1 
			assert(crs1.GCSCode==crs2.GCSCode) # The geographic coordinate system code.2
			assert(crs1.GCSName==crs2.GCSName) # The geographic coordinate system name.2
			assert(crs1.primeMeridianName==crs2.primeMeridianName) # The prime meridian name.2
			assert(crs1.radiansPerUnit==crs2.radiansPerUnit) # The radians per angular unit.2
			assert(crs1.semiMajorAxis==crs2.semiMajorAxis) # The semi-major axis length of this spheroid.2
			assert(crs1.semiMinorAxis==crs2.semiMinorAxis) # The semi-minor axis length of this spheroid.2
			assert(crs1.spheroidCode==crs2.spheroidCode) # The spheroid code.2
			assert(crs1.spheroidName==crs2.spheroidName) # The spheroid name.2
		return True
	except:
		output_message="CRS differs between datasets."#\ncrs1: %s\ncrs2 : %s" %(crs1.exportToString(), crs2.exportToString())
		arcpy.AddMessage(output_message)
		return False