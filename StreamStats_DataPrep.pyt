import arcpy
import sys
import os

version = "4.0"

arcpy.AddMessage('StreamStats Data Preparation Tools version: %s'%(version))

class Toolbox(object):
	def __init__(self):
		"""Toolbox for preprocessing data for creating or refreshing a StreamStats project."""
		self.label = "StreamStats Data Preparation Tools"
		self.alias = "StreamStatsDataPrep"

		# List of tool classes associated with this toolbox
		self.tools = [databaseSetup,
		makeELEVDATAIndex,ExtractPoly,CheckNoData,FillNoData,ProjScale]

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
			datatype = "DEShapefile",
			parameterType = "Required",
			direction = "Input")

		param3 = arcpy.Parameter(
			displayName = "Outwall Field",
			name = "hu8_field",
			datatype = "Field",
			parameterType = "Required",
			direction = "Input")

		param3.value = 'HUC_8'

		param4 = arcpy.Parameter(
			displayName = "Inwall Field",
			name = "hu12_field",
			datatype = "Field",
			parameterType = "Required",
			direction = "Input")

		param4.value = 'HUC_12'

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

		return

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

		return

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
			displayName = "Input Grid",
			name = "InGrid",
			datatype = "DERasterBand",
			parameterType = "Required",
			direction = "Input")

		param1 = arcpy.Parameter(
			displayName = "Output Grid",
			name = "OutGrid",
			datatype = "DERasterBand",
			parameterType = "Required",
			direction = "Output")

		params = [param0, param1]
		return params

	def execute(self, parameters, messages):

		from elevationTools import fillNoData

		# load parameters
		InGrid = parameters[0].valueAsText
		OutGrid = parameters[1].valueAsText
		
		fillNoData(InGrid,OutGrid)
		
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

		param1 = arcpy.Parameter(
			displayName = "Input Grid",
			name = "InGrid",
			datatype = "DERasterBand",
			parameterType = "Required",
			direction = "Input")

		param2 = arcpy.Parameter(
			displayName = "Output Grid",
			name = "OutGrid",
			datatype = "DERasterBand",
			parameterType = "Required",
			direction = "Output")

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

		params = [param0,param1,param2,param3,param4,param5]

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

		projScale(Input_Workspace, InGrd, OutGrd, OutCoordsys, OutCellSize, RegistrationPoint)
		
		return