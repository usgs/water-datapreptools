import arcpy
import sys
import os

class Toolbox(object):
    def __init__(self):
        """Toolbox for preprocessing data for creating or refreshing a StreamStats project."""
        self.label = "Setup Tools"
        self.alias = "Setup Toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [databaseSetup]

class databaseSetup(object):
    # ---------------------------------------------------------------------------
    # HUC_process.py
    #
    # This script setup up an archydro workspace for the StreamStats process
    # The script takes the WBD, NHD and creates a new folder in a new workspace
    # for each huc and creates a master filegdb that sits in the archydro root
    # and holds the huc8index.  It also dissolves by 12 digit and 8 digit polygons
    # and line feature classes, creates the inner walls feature class, creates a
    # 50m and 2000m buffer of the HUC and creats a 2000m huc buffer in the DEM
    # projection (to use with your Elevation tools)
    #
    # Created on: April 20 2010 by Martyn Smith, USGS
    # Updated on: May 26, 2015 by Kitty Kolb, USGS
    # Modified to remove M-values from shapefile creations.
    # Updated on: April 11, 2019 by Kitty Kolb, USGS
    # Modified to reflect ArcPy and new data naming conventions, wrote new cursor search
    # April 22, 2019 - Theodore Barnhart: moved to python toolbox.
    # ---------------------------------------------------------------------------
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

        parameters = [param0,param1,param2,param3,param4,param5,param6,param7]
        return parameters

    def execute(self, parameters, messages):
        # import the actual tool

        from databaseSetup import *

        # Local variables
        output_workspace = parameters[0].valueAsText
        output_gdb_name = parameters[1].valueAsText
        hu_dataset = parameters[2].valueAsText
        hu8_field = parameters[3].valueAsText
        hu12_field = parameters[4].valueAsText
        hucbuffer = parameters[5].valueAsText
        nhd_path = parameters[6].valueAsText
        elevation_projection_template = parameters[7].valueAsText

        databaseSetup(output_workspace, output_gdb_name, hu_dataset, hu8_field, hu12_field, hucbuffer, nhd_path,elevation_projection_template)