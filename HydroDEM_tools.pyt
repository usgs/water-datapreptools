import arcpy
import sys
import os
import string

class Toolbox(object):
    def __init__(self):
        """Toolbox for preprocessing data for creating or refreshing a StreamStats project."""
        self.label = "ELEVDATAtools"
        self.alias = "ELEVDATA processing tools"

        # List of tool classes associated with this toolbox
        self.tools = [SetupBathyGrad]

class SetupBathyGrad(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "4.A Bathymetric Gradient Setup"
        self.description = "This script creates a set of NHD Hydrography Datasets, extracts the appropriate features and converts them to rasters for input into HydroDEM."
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
        """The source code of the tool."""
        # ---------------------------------------------------------------------------
        # ssbowling.py
        # Created on: Wed Jan 31 2007 01:16:48 PM
        # Author:  Martyn Smith
        # USGS New York Water Science Center Troy, NY
        #
        # Updated to Arcpy, 20190222, Theodore Barnhart, tbarnhart@usgs.gov
        #
        # Description:  This script takes a set of NHD Hydrography Datasets, extracts the appropriate
        # features and converts them to rasters for the Bathymetric Gradient (bowling) inputs to HydroDEM
        # Usage: ssprocess <Workspace> <SnapGrid> <NHDArea> <NHDFlowline> <NHDWaterbody> <SelectionBuffer> <OutputProjection>
        # ---------------------------------------------------------------------------

        # Import system modules
        #import sys, string, os, arcgisscripting

        # Create the Geoprocessor object
        #gp = arcgisscripting.create()

        # Set script to overwrite if files exist
        arcpy.env.overwriteOutput = True

        # Dynamic Script arguments (from ArcToolbox)...
        Workspace = parameters[0].valueAsText
        SnapGrid = parameters[1].valueAsText
        hucpoly = parameters[2].valueAsText
        NHDArea = parameters[3].valueAsText
        NHDFlowline = parameters[4].valueAsText
        NHDWaterbody = parameters[5].valueAsText
        cellSize = parameters[6].valueAsText

        def SnapExtent(lExtent, lRaster):
            "Returns a given extent snapped to the passed raster"
            
            pExtent = lExtent.split()
            extent = lExtent
            
            lt = ["rasterdataset","rasterband"]
            dsc = arcpy.describe(lRaster)
            if string.lower(dsc.DatasetType) in lt:
                iCell = dsc.MeanCellWidth
                xmin = round(float(pExtent[0]) / iCell) * iCell
                ymin = round(float(pExtent[1]) / iCell) * iCell
                xmax = round(float(pExtent[2]) / iCell) * iCell 
                ymax = round(float(pExtent[3]) / iCell) * iCell 
                extent = str(xmin) + " " + str(ymin) + " " + str(xmax) + " " + str(ymax)
            return extent

        arcpy.AddMessage("Starting Bathymetric Gradient Preparations....")

        # Set the Geoprocessing environment...
        arcpy.scratchWorkspace = Workspace
        arcpy.workspace = Workspace

        # Setup local variables and temporary layer files
        arcpy.AddMessage("Setting up variables...")

        #temporary shapes
        nhd_flow_shp = arcpy.env.workspace + "\\nhd_flow.shp"
        nhd_flow_Layer = "nhd_flow_Layer"
        nhd_area_shp = arcpy.env.workspace + "\\nhd_area.shp"
        nhd_area_Layer = "nhd_area_Layer"
        nhd_wb_shp = arcpy.env.workspace + "\\nhd_wb.shp"
        nhd_wb_Layer = "nhd_wb_Layer"

        #Output rastsers
        wbtempraster = arcpy.env.workspace + "\\nhdwb_tmp"
        areatempraster = arcpy.env.workspace + "\\nhdarea_tmp"
        mosaiclist = wbtempraster + ";" + areatempraster
        outraster1 = arcpy.env.workspace + "\\wb_srcg"
        outraster2 = "nhd_wbg"

        #convert to temporary shapefiles
        arcpy.FeatureClassToFeatureClass_conversion(NHDArea, arcpy.env.Workspace, "nhd_area.shp")
        arcpy.AddField_management(nhd_area_shp,"dummy","SHORT","#","#","#","#","NULLABLE","NON_REQUIRED","#")
        arcpy.CalculateField_management(nhd_area_shp,"dummy","1","VB","#")

        arcpy.FeatureClassToFeatureClass_conversion(NHDWaterbody, arcpy.env.Workspace, "nhd_wb.shp")
        arcpy.AddField_management(nhd_wb_shp,"dummy","SHORT","#","#","#","#","NULLABLE","NON_REQUIRED","#")
        arcpy.CalculateField_management(nhd_wb_shp,"dummy","1","VB","#")

        arcpy.FeatureClassToFeatureClass_conversion(NHDFlowline, arcpy.env.Workspace, "nhd_flow.shp")
        arcpy.AddField_management(nhd_flow_shp,"dummy","SHORT","#","#","#","#","NULLABLE","NON_REQUIRED","#")
        arcpy.CalculateField_management(nhd_flow_shp,"dummy","1","VB","#")

        try:
            #NHDArea Processing
            arcpy.AddMessage("Creating temporary selection layers...")
            arcpy.MakeFeatureLayer_management(nhd_area_shp, nhd_area_Layer, "FType = 460", "", "")
            
            #NHDWaterbody Processing
            arcpy.MakeFeatureLayer_management(nhd_wb_shp, nhd_wb_Layer, "FType = 390 OR FType = 361", "", "")
            
            #NHDFlowline Processing
            arcpy.MakeFeatureLayer_management(nhd_flow_shp, nhd_flow_Layer, "", "", "")
            arcpy.SelectLayerByLocation_management(nhd_flow_Layer, "WITHIN", nhd_wb_Layer, "", "NEW_SELECTION")
            arcpy.SelectLayerByLocation_management(nhd_flow_Layer, "WITHIN", nhd_area_Layer, "", "ADD_TO_SELECTION")
        except:
            arcpy.AddMessage(arcpy.GetMessages())

        #get snap grid cell size
        dsc_snap = arcpy.Describe(SnapGrid)
        snap_cellsize = dsc_snap.MeanCellWidth

        # Set raster processing parameters
        arcpy.AddMessage("Processing rasters...")
        dsc = arcpy.Describe(hucpoly)
        extent = str(dsc.extent)
        arcpy.env.cellSize = snap_cellsize
        arcpy.env.mask = SnapGrid
        arcpy.env.extent = SnapExtent(extent, SnapGrid)

        # Process: Feature to Raster1 - NHD Area...
        try:
            arcpy.SelectLayerByLocation_management(nhd_area_Layer, "INTERSECT", nhd_flow_Layer, "0", "NEW_SELECTION")
            arcpy.FeatureToRaster_conversion(nhd_area_Layer, "dummy", areatempraster, cellSize)      
        except:
            arcpy.CreateRasterDataset_management(arcpy.workspace,"nhdarea_tmp","10","8_BIT_UNSIGNED",SnapGrid)
            arcpy.AddMessage(arcpy.GetMessages())
            
        # Process: Feature to Raster2 - NHD Waterbody...
        try:
            arcpy.SelectLayerByLocation_management(nhd_wb_Layer, "INTERSECT", nhd_flow_Layer, "0", "NEW_SELECTION")
            arcpy.FeatureToRaster_conversion(nhd_wb_Layer, "dummy", wbtempraster, cellSize)
        except:
            arcpy.CreateRasterDataset_management(arcpy.workspace,"nhdwb_tmp","10","8_BIT_UNSIGNED",SnapGrid)
            arcpy.AddMessage(arcpy.GetMessages())

        # Process: Feature to Raster3 - NHD Flowline.  This is the first output
        try:
            arcpy.FeatureToRaster_conversion(nhd_flow_Layer, "dummy", outraster1, cellSize)
        except:
            arcpy.AddMessage(arcpy.GetMessages())

        # Process: Mosaic NHD Area and NHD Waterbody rasters To New Raster.  This is the second output
        try:
            arcpy.MosaicToNewRaster_management(mosaiclist, Workspace, outraster2, "", "8_BIT_UNSIGNED", "", "1", "BLEND", "FIRST")
        except:
            arcpy.AddMessage(arcpy.GetMessages())

        #Delete temp files and rasters
        arcpy.AddMessage("Cleaning up...")
        if arcpy.exists(areatempraster):
            arcpy.delete(areatempraster)
        if arcpy.exists(wbtempraster):
            arcpy.delete(wbtempraster)
        if arcpy.exists(nhd_flow_shp):
            arcpy.delete(nhd_flow_shp)
        if arcpy.exists(nhd_wb_shp):
            arcpy.delete(nhd_wb_shp)
        if arcpy.exists(nhd_area_shp):
            arcpy.delete(nhd_area_shp)

        arcpy.AddMessage("Done!")