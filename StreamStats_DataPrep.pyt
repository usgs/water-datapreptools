import arcpy
import sys
import os
#from make_hydrodem import *

version = "4.0alpha"

arcpy.AddMessage('StreamStats Data Preparation Tools version: %s'%(version))

class Toolbox(object):
	def __init__(self):
		"""Toolbox for preprocessing data for creating or refreshing a StreamStats project."""
		self.label = "StreamStats Data Preparation Tools"
		self.alias = "StreamStatsDataPrep"

		# List of tool classes associated with this toolbox
		self.tools = [databaseSetup,makeELEVDATAIndex,ExtractPoly,CheckNoData,FillNoData,ProjScale,CoastalDEM,SetupBathyGrad,HydroDEM,AdjustAccum]

class databaseSetup(object):
	def __init__(self):
		self.label = 'A. Database Setup'
		self.description = 'This script setup up an archydro workspace for the StreamStats process. The script takes watershed boundaries and hydrography to create a new folder in a new workspace for each hydrologic unit. The tool creates a master filegdb that sits in the root workspace and holds the hydrologic unit polygons (hucpolys). The tool also dissolves by 12 digit and 8 digit polygons and line feature classes, creates the inner walls feature class, creates two buffered HUC feature classes.'
		self.category = '1 - Setup Tools '
		self.canRunInBackground = False

	def getParameterInfo(self):
		param0 = arcpy.Parameter(
			displayName = "Output Workspace",
			name = "output_workspace",
			datatype = "DEWorkspace", 
			parameterType = "Required",
			direction = "Input")

		param0.filter.list = ["File System"]

		param1 = arcpy.Parameter(
			displayName = "Main ArcHydro Geodatabase Name",
			name = "output_gdb_name",
			datatype = "GPString",
			parameterType = "Required",
			direction = "Output")

		param2 = arcpy.Parameter(
			displayName = "Hydrologic Unit Boundary Dataset",
			name = "hu_dataset",
			datatype = ["DEShapefile","DEFeatureClass"],
			parameterType = "Required",
			direction = "Input")

		param3 = arcpy.Parameter(
			displayName = "Outwall Field",
			name = "hu8_field",
			datatype = "Field",
			parameterType = "Required",
			direction = "Input")

		param3.value = 'HUC8'

		param4 = arcpy.Parameter(
			displayName = "Inwall Field",
			name = "hu12_field",
			datatype = "Field",
			parameterType = "Required",
			direction = "Input")

		param4.value = 'HUC12'

		param5 = arcpy.Parameter(
			displayName = "Hydrologic Unit Buffer Distance (m)",
			name = "hucbuffer",
			datatype = "GPString",
			parameterType = "Required",
			direction = "Input")

		param5.value = '2000'

		param6 = arcpy.Parameter(
			displayName = "Input Hydrography Workspace",
			name = "nhd_path",
			datatype = "DEWorkspace",
			parameterType = "Required",
			direction = "Input")

		param6.filter.list = ["File System"]

		param7 = arcpy.Parameter(
			displayName = "Elevation Dataset Template",
			name = "elevation_projection_template",
			datatype = "DERasterBand",
			parameterType = "Required",
			direction = "Input")

		param8 = arcpy.Parameter(
			displayName = "Alternative Outwall Buffer",
			name = "alt_buff",
			datatype = "GPString",
			parameterType = "Optional",
			direction = "Input")

		param8.value = "50"

		parameters = [param0,param1,param2,param3,param4,param5,param6,param7, param8]
		return parameters

	def execute(self, parameters, messages):
		# import the actual tool

		from databaseSetup import databaseSetup

		# Local variables
		output_workspace = parameters[0].valueAsText
		output_gdb_name = parameters[1].valueAsText
		hu_dataset = parameters[2].valueAsText
		hu8_field = parameters[3].valueAsText
		hu12_field = parameters[4].valueAsText
		hucbuffer = parameters[5].valueAsText
		nhd_path = parameters[6].valueAsText
		elevation_projection_template = parameters[7].valueAsText
		alt_buff = parameters[8].valueAsText

		databaseSetup(output_workspace, output_gdb_name, hu_dataset, hu8_field, hu12_field, hucbuffer, nhd_path,elevation_projection_template,alt_buff, version=version)

class makeELEVDATAIndex(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "A. Make ELEVDATA Index"
		self.description = "Function to make ELEVDATA into a raster catalog for clipping to the basin polygons."
		self.category = "2 - Elevation Tools"
		self.canRunInBackground = False

	def getParameterInfo(self):
		"""Define parameter definitions"""
		param0 = arcpy.Parameter(
			displayName = "Output Geodatabase",
			name = "OutLoc",
			datatype = "DEWorkspace",
			parameterType = "Required",
			direction = "Input")

		param0.filter.list = ["Local Database"] 

		param1 = arcpy.Parameter(
			displayName = "Output Raster Catalog Name",
			name = "rcName",
			datatype = "GPString",
			parameterType = "Required",
			direction = "Input") 

		param1.value = "IndexRC"

		param2 = arcpy.Parameter(
			displayName = "Coordinate System",
			name = "coordsysRaster",
			datatype = "GPCoordinateSystem",
			parameterType = "Required",
			direction = "Input")

		param3 = arcpy.Parameter(
			displayName = "Input ELEV Workspace",
			name = "inputELEVws",
			datatype = "DEWorkspace",
			parameterType = "Required",
			direction = "Input")

		param3.filter.list = ["File System"]

		param4 = arcpy.Parameter(
			displayName = "Output Polygon Feature Class",
			name = "OutFC",
			datatype = "GPString",
			parameterType = "Required",
			direction = "Input")

		param4.value = "ELEVDATIndexPolys"

		params = [param0,param1,param2,param3,param4]
		return params

	def execute(self, parameters, messages):

		from elevationTools import elevIndex

		OutLoc = parameters[0].valueAsText # output geodatabase
		rcName = parameters[1].valueAsText # raster catalogue name
		coordsysRaster = parameters[2].valueAsText # raster coordinate system
		InputELEVDATAws = parameters[3].valueAsText # geodatabase of elevation data
		OutFC = parameters[4].valueAsText # output polygon feature class

		elevIndex(OutLoc, rcName, coordsysRaster, InputELEVDATAws, OutFC, version=version)

		return

class ExtractPoly(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "B. Extract Polygons"
		self.description = "Extract polygon area from ELEVDATA."
		self.category = "2 - Elevation Tools"
		self.canRunInBackground = False

	def getParameterInfo(self):
		"""Define parameter definitions"""
		param0 = arcpy.Parameter(
			displayName = "Output Workspace",
			name = "Input_Workspace",
			datatype = "DEWorkspace",
			parameterType = "Required",
			direction = "Input")

		param0.filter.list = ["File System"]

		param1 = arcpy.Parameter(
			displayName = "ELEVDATA Index Polygons",
			name = "nedindx",
			datatype = "GPFeatureLayer",
			parameterType = "Required",
			direction = "Input")

		param2 = arcpy.Parameter(
			displayName = "Clip Polygon",
			name = "clpfeat",
			datatype = "GPFeatureLayer",
			parameterType = "Required",
			direction = "Input")

		param3 = arcpy.Parameter(
			displayName = "Output Grid",
			name = "OutGrd",
			datatype = "GPString",
			parameterType = "Required",
			direction = "Output")

		param3.value = "dem_dd"

		params = [param0,param1,param2,param3]
		return params

	def execute(self, parameters, messages):

		from elevationTools import extractPoly

		Input_Workspace = parameters[0].valueAsText #workspace
		nedindx = parameters[1].valueAsText # NED Index (polygon) Layer
		clpfeat = parameters[2].valueAsText # clip polygon feature layer, I think this should be a collection of features so all the clipping happens in a loop....
		OutGrd = parameters[3].valueAsText # name of output grid

		extractPoly(Input_Workspace, nedindx, clpfeat, OutGrd, version=version)

class CheckNoData(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "C. CheckNoData"
		self.description = "Finds NODATA values in a grid and makes a polygon feature class with value 1 if it is NODATA, and 0 if it contains data values."
		self.category = "2 - Elevation Tools"
		self.canRunInBackground = False

	def getParameterInfo(self):
		"""Define parameter definitions"""

		param0 = arcpy.Parameter(
			displayName = "InputGrid",
			name = "InGrid",
			datatype = "DERasterBand",
			parameterType = "Required",
			direction = "Input")

		param1 = arcpy.Parameter(
			displayName = "Workspace",
			name = "tmpLoc",
			datatype = "DEWorkspace",
			parameterType = "Required",
			direction = "Input")

		param1.filter.list = ["Local Database"]

		param2 = arcpy.Parameter(
			displayName = "Output Feature Layer",
			name = "OutPolys",
			datatype = "GPString",
			parameterType = "Required",
			direction = "Input")

		param2.value = "DEMsinks"

		params = [param0,param1,param2]
		return params

	def execute(self, parameters, messages):

		from elevationTools import checkNoData

		InGrid = parameters[0].valueAsText
		tmpLoc = parameters[1].valueAsText
		OutPolys_shp = parameters[2].valueAsText

		checkNoData(InGrid, tmpLoc, OutPolys_shp, version=version)

class FillNoData(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "D. Fill NoData Cells"
		self.description = "Replaces NODATA values in a grid with mean values within 3x3 window. May be run repeatedly to fill in areas wider than 2 cells. Note the output is floating point, even if the input is integer. Note this will expand the data area of the grid around the outer edges of data, in addition to filling in NODATA gaps in the interior of the grid."
		self.category = "2 - Elevation Tools"
		self.canRunInBackground = False

	def getParameterInfo(self):
		"""Define parameter definitions"""
		param0 = arcpy.Parameter(
			displayName = "Workspace",
			name = "workspace",
			datatype = "DEWorkspace",
			parameterType = "Required",
			direction = "Input")

		param0.filter.list = ["File System"]

		param1 = arcpy.Parameter(
			displayName = "Input Grid",
			name = "InGrid",
			datatype = "DERasterBand",
			parameterType = "Required",
			direction = "Input")

		param2 = arcpy.Parameter(
			displayName = "Output Grid",
			name = "OutGrid",
			datatype = "GPString",
			parameterType = "Required",
			direction = "Input")

		params = [param0, param1, param2]
		return params

	def execute(self, parameters, messages):

		from elevationTools import fillNoData

		# load parameters
		workspace = parameters[0].valueAsText
		InGrid = parameters[1].valueAsText
		OutGrid = parameters[2].valueAsText

		
		fillNoData(workspace, InGrid, OutGrid, version = version)
		
		return

class ProjScale(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "E. Project and Scale Elevation Data"
		self.description = "Project a NED grid to a user-specified coordinate system. Handles setting a cell registration point. Also multiplies by 100 and converts to integer grid format."
		self.category = "2 - Elevation Tools"
		self.canRunInBackground = False

	def getParameterInfo(self):
		"""Define parameter definitions"""
		
		param0 = arcpy.Parameter(
			displayName = "Input Workspace",
			name = "InWorkSpace",
			datatype = "DEWorkspace",
			parameterType = "Required",
			direction = "Input")

		param0.filter.list = ['File System']

		param1 = arcpy.Parameter(
			displayName = "Input Grid",
			name = "InGrid",
			datatype = "DERasterBand",
			parameterType = "Required",
			direction = "Input")

		param2 = arcpy.Parameter(
			displayName = "Output Grid",
			name = "OutGrid",
			datatype = "GPString",
			parameterType = "Required",
			direction = "Input")

		param2.value = "dem"

		param3 = arcpy.Parameter(
			displayName = "Output Coordinate System",
			name = "OutCoordSys",
			datatype = "GPCoordinateSystem",
			parameterType = "Required",
			direction = "Input")

		param4 = arcpy.Parameter(
			displayName = "Output Cell Size",
			name = "OutCellSize",
			datatype = "analysis_cell_size",
			parameterType = "Required",
			direction = "Input")

		param4.value = 10

		param5 = arcpy.Parameter(
			displayName = "registration Point",
			name = "RegPt",
			datatype = "GPString",
			parameterType = "Required",
			direction = "Input")

		param5.value = "0 0"

		param6 = arcpy.Parameter(
			displayName = "Scale Factor",
			name = "scaleFact",
			datatype = "GPString",
			parameterType = "Required",
			direction = "Input")

		param6.value = "100"

		params = [param0,param1,param2,param3,param4,param5,param6]

		return params

	def execute(self, parameters, messages):

		from elevationTools import projScale

		# get parameters from tools
		Input_Workspace = parameters[0].valueAsText # Input workspace. (type Workspace)
		InGrd = parameters[1].valueAsText           # Input grid name. (type String)
		OutGrd = parameters[2].valueAsText          # Output grid name. (type String)
		OutCoordsys = parameters[3].valueAsText     # Coordinate system for output grid. (type Coordinate System)
		OutCellSize = parameters[4].valueAsText     # Cell size for output grid. (type Analysis cell size)
		RegistrationPoint = parameters[5].valueAsText  # Registration point. Space separated coordinates. (type String)
		scaleFact = int(parameters[6].valueAsText)

		projScale(Input_Workspace, InGrd, OutGrd, OutCoordsys, OutCellSize, RegistrationPoint, scaleFact = scaleFact, version = version)
		
		return None

class SetupBathyGrad(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "B. Bathymetric Gradient Setup"
		self.description = "This script creates a set of NHD Hydrography Datasets, extracts the appropriate features and converts them to rasters for input into HydroDEM."
		self.category = "4 - HydroDEM"
		self.canRunInBackground = False

	def getParameterInfo(self):
		"""Define parameter definitions"""
		param0 = arcpy.Parameter(
			displayName = "Output Workspace",
			name = "Workspace",
			datatype = "DEWorkspace",
			parameterType = "Required",
			direction = "Input") # maybe should be Output

		param1 = arcpy.Parameter(
			displayName = "Digital Elevation Model (used for snapping)",
			name = "SnapGrid",
			datatype = "DERasterBand",
			parameterType = "Required",
			direction = "Input") 

		param2 = arcpy.Parameter(
			displayName = "Dissolved HUC8 Dataset",
			name = "hucpoly",
			datatype = "DEFeatureClass",
			parameterType = "Required",
			direction = "Input")

		param3 = arcpy.Parameter(
			displayName = "NHD Area",
			name = "NHDArea",
			datatype = "DEFeatureClass",
			parameterType = "Required",
			direction = "Input")

		param4 = arcpy.Parameter(
			displayName = "NHD Dendrite",
			name = "NHDFlowline",
			datatype = "DEFeatureClass",
			parameterType = "Required",
			direction = "Input")

		param5 = arcpy.Parameter(
			displayName = "NHD Waterbody",
			name = "NHDWaterbody",
			datatype = "DEFeatureClass",
			parameterType = "Required",
			direction = "Input")

		param6 = arcpy.Parameter(
			displayName = "Cell Size",
			name = "cellSize",
			datatype = "GPString",
			parameterType = "Required",
			direction = "Input")

		param6.value = "10"

		params = [param0,param1,param2,param3,param4,param5,param6]
		return params

	def execute(self, parameters, messages):

		from make_hydrodem import bathymetricGradient, SnapExtent

		Workspace = parameters[0].valueAsText
		SnapGrid = parameters[1].valueAsText
		hucpoly = parameters[2].valueAsText
		NHDArea = parameters[3].valueAsText
		NHDFlowline = parameters[4].valueAsText
		NHDWaterbody = parameters[5].valueAsText
		cellSize = parameters[6].valueAsText

		bathymetricGradient(Workspace,SnapGrid, hucpoly, NHDArea, NHDFlowline, NHDWaterbody, cellSize, version = version)

		return None

class CoastalDEM(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "A. Coastal DEM Processing (Optional)"
		self.description = "Lowers the level of the sea to ensure it is always below land level. Also raises any land cells to 1 cm unless they are within a polygon with Land attribute of 0. The input polygons (LandSea) needs to identify the sea with a Land attribute of -1. Land is identified with a Land value of 1. No change polygons should have Land value of 0."
		self.canRunInBackground = False
		self.category = "4 - HydroDEM"

	def getParameterInfo(self):
		"""Define parameter definitions"""
		param0 = arcpy.Parameter(
			displayName = "Workspace",
			name = "Input_Workspace",
			datatype = "DEWorkspace",
			parameterType = "Required",
			direction = "Input") # maybe should be Output

		param1 = arcpy.Parameter(
			displayName = "Input raw DEM",
			name = "grdName",
			datatype = "DERasterBand",
			parameterType = "Required",
			direction = "Input")

		param1.value = "dem_raw"

		param2 = arcpy.Parameter(
			displayName = "Input LandSea polygon feature class",
			name = "InFeatureClass",
			datatype = "DEFeatureClass",
			parameterType = "Required",
			direction = "Input")

		param3 = arcpy.Parameter(
			displayName = "Output DEM",
			name = "OutRaster",
			datatype = "DERasterBand",
			parameterType = "Required",
			direction = "Input")

		param3.value = "dem_sea"

		param4 = arcpy.Parameter(
			displayName = "Sea Level",
			name = "seaLevel",
			datatype = "GPString",
			parameterType = "Required",
			direction = "Input")

		param4.value = "-60000"

		params = [param0,param1,param2,param3,param4]
		return params

	def execute(self, parameters, messages):
		from make_hydrodem import coastaldem

		Input_Workspace = parameters[0].valueAsText    # input workspace (type Workspace)
		grdName = parameters[1].valueAsText            # input DEM grid name (type String)
		InFeatureClass = parameters[2].valueAsText     # input LandSea feature class (type Feature Class)
		OutRaster = parameters[3].valueAsText          # output DEM grid name (type String)
		seaLevel = parameters[4].valueAsText           # Elevation to make the sea

		coastaldem(Input_Workspace, grdName, InFeatureClass, OutRaster, seaLevel)

		return None

class HydroDEM(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "C. Hydro-Enforce DEM"
		self.description = "Run make_HydroDEM() to process DEMs, burning in streams and building walls."
		self.category = "4 - HydroDEM"
		self.canRunInBackground = False

	def getParameterInfo(self):
		"""Define parameter definitions"""
		param0 = arcpy.Parameter(
			displayName = "Output Workspace",
			name = "Workspace",
			datatype = "DEWorkspace",
			parameterType = "Required",
			direction = "Input")

		param0.filter.list = ["Local Database"]
		
		param18 = arcpy.Parameter(
			displayName = "Scratch Workspace",
			name = "scratchWS",
			datatype = "DEWorkspace",
			parameterType = "Required",
			direction = "Input")

		param18.filter.list = ["File System"]

		param1 = arcpy.Parameter(
			displayName = "HUC layer",
			name = "huc8cov",
			datatype = "DEFeatureClass",
			parameterType = "Required",
			direction = "Input") 

		param2 = arcpy.Parameter(
			displayName = "Digital Elevation Model",
			name = "origdem",
			datatype = "DERasterBand",
			parameterType = "Required",
			direction = "Input")

		param3 = arcpy.Parameter(
			displayName = "Stream Dendrite",
			name = "dendrite",
			datatype = "DEFeatureClass",
			parameterType = "Required",
			direction = "Input")

		param4 = arcpy.Parameter(
			displayName = "Snap Grid",
			name = "snap_grid",
			datatype = "DERasterBand",
			parameterType = "Required",
			direction = "Input")

		param5 = arcpy.Parameter(
			displayName = "NHD Waterbody Grid",
			name = "bowl_polys",
			datatype = "DERasterDataset",
			parameterType = "Optional",
			direction = "Input")

		param6 = arcpy.Parameter(
			displayName = "NHD Flowline Grid",
			name = "bowl_lines",
			datatype = "DERasterDataset",
			parameterType = "Optional",
			direction = "Input")

		param7 = arcpy.Parameter(
			displayName = "Inner Walls",
			name = "inwall",
			datatype = "DEFeatureClass", # maybe should be raster
			parameterType = "Optional",
			direction = "Input")

		param8 = arcpy.Parameter(
			displayName = "Cell Size",
			name = "cellSize",
			datatype = "GPString",
			parameterType = "Required",
			direction = "Input")

		param8.value = "10"

		param9 = arcpy.Parameter(
			displayName = "Drain Plugs",
			name = "drainplug",
			datatype = "DEFeatureClass", # maybe should be raster
			parameterType = "Optional",
			direction = "Input")

		param10 = arcpy.Parameter(
			displayName = "HUC buffer",
			name = "buffdist",
			datatype = "GPDouble",
			parameterType = "Optional",
			direction = "Input")

		param10.value = 50

		param11 = arcpy.Parameter(
			displayName = "Inner Wall Buffer",
			name = "inwallbuffdist",
			datatype = "GPDouble",
			parameterType = "Optional",
			direction = "Input")

		param11.value = 15

		param12 = arcpy.Parameter(
			displayName = "Inner Wall Height",
			name = "inwallht",
			datatype = "GPDouble",
			parameterType = "Optional",
			direction = "Input")

		param12.value = 150000

		param13 = arcpy.Parameter(
			displayName = "Outer Wall Height",
			name = "outwallht",
			datatype = "GPDouble",
			parameterType = "Optional",
			direction = "Input")

		param13.value = 300000

		param14 = arcpy.Parameter(
			displayName = "AGREE buffer",
			name = "agreebuf",
			datatype = "GPDouble",
			parameterType = "Optional",
			direction = "Input")

		param14.value = 60

		param15 = arcpy.Parameter(
			displayName = "AGREE Smooth Drop",
			name = "agreesmooth",
			datatype = "GPDouble",
			parameterType = "Optional",
			direction = "Input")

		param15.value = -500

		param16 = arcpy.Parameter(
			displayName = "AGREE Sharp Drop",
			name = "agreesharp",
			datatype = "GPDouble",
			parameterType = "Optional",
			direction = "Input")

		param16.value = -50000

		param17 = arcpy.Parameter(
			displayName = "Bowl Depth",
			name = "bowldepth",
			datatype = "GPDouble",
			parameterType = "Optional",
			direction = "Input")

		param17.value = 2000

		params = [param0,param18,param1,param2,param3,param4,param5,param6,param7,param8,param9,param10,param11,param12,param13,param14,param15,param16,param17]

		return params

	def execute(self, parameters, messages):

		from make_hydrodem import hydrodem, agree

		outdir = parameters[0].valueAsText
		huc8cov = parameters[2].valueAsText
		origdem = parameters[3].valueAsText
		dendrite = parameters[4].valueAsText
		snap_grid = parameters[5].valueAsText
		bowl_polys = parameters[6].valueAsText
		bowl_lines = parameters[7].valueAsText
		inwall = parameters[8].valueAsText
		cellsz = parameters[9].valueAsText
		drainplug = parameters[10].valueAsText
		buffdist = int(parameters[11].valueAsText)
		inwallbuffdist = int(parameters[12].valueAsText)
		inwallht = int(parameters[13].valueAsText)
		outwallht = int(parameters[14].valueAsText)
		agreebuf = int(parameters[15].valueAsText)
		agreesmooth = int(parameters[16].valueAsText)
		agreesharp = int(parameters[17].valueAsText)
		bowldepth = int(parameters[18].valueAsText)
		scratchWS = parameters[1].valueAsText

		hydrodem(outdir, huc8cov, origdem, dendrite, snap_grid, bowl_polys, bowl_lines, inwall, drainplug, buffdist, inwallbuffdist, inwallht, outwallht, agreebuf, agreesmooth, agreesharp, bowldepth, cellsz, scratchWS, version = version)

		return None

class AdjustAccum(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "D. Adjust Accumulation"
		self.description = "This fucntion adjusts the fac of a downstream HUC to include flow accumulations from upstream HUC's. Run this from the downstream HUC workspace. The function will leave the fac grid intact and will create a grid named \"fac_global\" in the same directory as the original fac raster. To get true accumulation values in HUCs downstream of other non-headwater HUCs, proceed from upstream HUCs to downstream HUCs in order, and specify the fac_global grid for any upstream HUC that has one. (It is not essential that the fac_global contain true global fac values, and in some cases it is not possible since the values get too large. In practice, as long as the receiving cells have accumulation values larger than the stream definition threshold (150,000 cells for 10-m grids), then it will be OK. Not sure if this caveat applies with arcPy."
		self.canRunInBackground = False
		self.category = "4 - HydroDEM"

	def getParameterInfo(self):
		"""Define parameter definitions"""
		param0 = arcpy.Parameter(
			displayName = "Downstream Accumulation Grid",
			name = "facPth",
			datatype = "DERasterDataset",
			parameterType = "Required",
			direction = "Input")

		param1 = arcpy.Parameter(
			displayName = "Downstream Flow Direction Grid",
			name = "fdrPth",
			datatype = "DERasterDataset",
			parameterType = "Required",
			direction = "Input")

		param2 = arcpy.Parameter(
			displayName = "Upstream Flow Accumulation Grids",
			name = "upstreamFACpths",
			datatype = "DERasterDataset",
			parameterType = "Required",
			direction = "Input",
			multiValue = True)

		param3 = arcpy.Parameter(
			displayName = "Upstream Flow Direction Grids",
			name = "upstreamFDRpths",
			datatype = "DERasterDataset",
			parameterType = "Required",
			direction = "Input",
			multiValue = True)

		param4 = arcpy.Parameter(
			displayName = "Workspace",
			name = "workspace",
			datatype = "Workspace",
			parameterType = "Required",
			direction = "Input")

		params = [param0,param1,param2,param3,param4]
		return params

	def execute(self, parameters, messages):
		from make_hydrodem import adjust_accum

		facPth = parameters[0].valueAsText # path to downstream flow accumulation grid
		fdrPth = parameters[1].valueAsText # path to downstream flow direction grid
		upstreamFACpths = (parameters[2].valueAsText).split(';') # list of upstream flow accumulation grids
		upstreamFDRpths = (parameters[3].valueAsText).split(';') # list of upstream flow direction grids
		workspace = parameters[4].valueAsText # path to geodatabase workspace to work in

		adjust_accum(facPth, fdrPth, upstreamFACpths,upstreamFDRpths, workspace)

		return None