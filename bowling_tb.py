# ---------------------------------------------------------------------------
# ssbowling.py
# Created on: Wed Jan 31 2007 01:16:48 PM
# Author:  Martyn Smith
# USGS New York Water Science Center Troy, NY
# Description:  This script takes a set of NHD Hydrography Datasets, extracts the appropriate
# features and converts them to rasters for the Bathymetric Gradient (bowling) inputs to HydroDEM
# Usage: ssprocess <Workspace> <SnapGrid> <NHDArea> <NHDFlowline> <NHDWaterbody> <SelectionBuffer> <OutputProjection>
# ---------------------------------------------------------------------------

# Import system modules
import sys, string, os, arcgisscripting

# Create the Geoprocessor object
gp = arcgisscripting.create()

# Set script to overwrite if files exist
gp.overwriteoutput = 1

# Dynamic Script arguments (from ArcToolbox)...
Workspace = sys.argv[1]
SnapGrid = sys.argv[2]
hucpoly = sys.argv[3]
NHDArea = sys.argv[4]
NHDFlowline = sys.argv[5]
NHDWaterbody = sys.argv[6]

def SnapExtent(lExtent, lRaster):
    "Returns a given extent snapped to the passed raster"
    
    pExtent = lExtent.split()
    extent = lExtent
    
    lt = ["rasterdataset","rasterband"]
    dsc = gp.describe(lRaster)
    if string.lower(dsc.DatasetType) in lt:
        iCell = dsc.MeanCellWidth
        xmin = round(float(pExtent[0]) / iCell) * iCell
        ymin = round(float(pExtent[1]) / iCell) * iCell
        xmax = round(float(pExtent[2]) / iCell) * iCell 
        ymax = round(float(pExtent[3]) / iCell) * iCell 
        extent = str(xmin) + " " + str(ymin) + " " + str(xmax) + " " + str(ymax)
    return extent

print "Welcome to the Bowling Script"

# Set the Geoprocessing environment...
gp.scratchWorkspace = Workspace
gp.workspace = Workspace

# Setup local variables and temporary layer files
gp.AddMessage("Setting up variables...")

#temporary shapes
nhd_flow_shp = gp.workspace + "\\nhd_flow.shp"
nhd_flow_Layer = "nhd_flow_Layer"
nhd_area_shp = gp.workspace + "\\nhd_area.shp"
nhd_area_Layer = "nhd_area_Layer"
nhd_wb_shp = gp.workspace + "\\nhd_wb.shp"
nhd_wb_Layer = "nhd_wb_Layer"

#Output rastsers
wbtempraster = gp.workspace + "\\nhdwb_tmp"
areatempraster = gp.workspace + "\\nhdarea_tmp"
mosaiclist = wbtempraster + ";" + areatempraster
outraster1 = gp.workspace + "\\wb_srcg"
outraster2 = "nhd_wbg"

#convert to temporary shapefiles
gp.FeatureClassToFeatureClass_conversion(NHDArea, gp.Workspace, "nhd_area.shp")
gp.AddField_management(nhd_area_shp,"dummy","SHORT","#","#","#","#","NULLABLE","NON_REQUIRED","#")
gp.CalculateField_management(nhd_area_shp,"dummy","1","VB","#")

gp.FeatureClassToFeatureClass_conversion(NHDWaterbody, gp.Workspace, "nhd_wb.shp")
gp.AddField_management(nhd_wb_shp,"dummy","SHORT","#","#","#","#","NULLABLE","NON_REQUIRED","#")
gp.CalculateField_management(nhd_wb_shp,"dummy","1","VB","#")

gp.FeatureClassToFeatureClass_conversion(NHDFlowline, gp.Workspace, "nhd_flow.shp")
gp.AddField_management(nhd_flow_shp,"dummy","SHORT","#","#","#","#","NULLABLE","NON_REQUIRED","#")
gp.CalculateField_management(nhd_flow_shp,"dummy","1","VB","#")

try:
    #NHDArea Processing
    gp.AddMessage("Creating temporary selection layers...")
    gp.MakeFeatureLayer_management(nhd_area_shp, nhd_area_Layer, "FType = 460", "", "")
    
    #NHDWaterbody Processing
    gp.MakeFeatureLayer_management(nhd_wb_shp, nhd_wb_Layer, "FType = 390 OR FType = 361", "", "")
    
    #NHDFlowline Processing
    gp.MakeFeatureLayer_management(nhd_flow_shp, nhd_flow_Layer, "", "", "")
    gp.SelectLayerByLocation_management(nhd_flow_Layer, "WITHIN", nhd_wb_Layer, "", "NEW_SELECTION")
    gp.SelectLayerByLocation_management(nhd_flow_Layer, "WITHIN", nhd_area_Layer, "", "ADD_TO_SELECTION")
except:
    print gp.GetMessages()

#get snap grid cell size
dsc_snap = gp.describe(SnapGrid)
snap_cellsize = dsc_snap.MeanCellWidth

# Set raster processing parameters
gp.AddMessage("Doing raster processing...")
dsc = gp.Describe(hucpoly)
extent = str(dsc.extent)
gp.cellSize = snap_cellsize
gp.mask = SnapGrid
gp.extent = SnapExtent(extent, SnapGrid)

# Process: Feature to Raster1 - NHD Area...
try:
    gp.SelectLayerByLocation_management(nhd_area_Layer, "INTERSECT", nhd_flow_Layer, "0", "NEW_SELECTION")
    gp.FeatureToRaster_conversion(nhd_area_Layer, "dummy", areatempraster, "10")      
except:
    gp.CreateRasterDataset_management(gp.workspace,"nhdarea_tmp","10","8_BIT_UNSIGNED",SnapGrid)
    print gp.GetMessages()
    
# Process: Feature to Raster2 - NHD Waterbody...
try:
    gp.SelectLayerByLocation_management(nhd_wb_Layer, "INTERSECT", nhd_flow_Layer, "0", "NEW_SELECTION")
    gp.FeatureToRaster_conversion(nhd_wb_Layer, "dummy", wbtempraster, "10")
except:
    gp.CreateRasterDataset_management(gp.workspace,"nhdwb_tmp","10","8_BIT_UNSIGNED",SnapGrid)
    print gp.GetMessages()

# Process: Feature to Raster3 - NHD Flowline.  This is the first output
try:
    gp.FeatureToRaster_conversion(nhd_flow_Layer, "dummy", outraster1, "10")
except:
    print gp.GetMessages()

# Process: Mosaic NHD Area and NHD Waterbody rasters To New Raster.  This is the second output
try:
    gp.MosaicToNewRaster_management(mosaiclist, Workspace, outraster2, "", "8_BIT_UNSIGNED", "", "1", "BLEND", "FIRST")
except:
    print gp.GetMessages()

#Delete temp files and rasters
gp.AddMessage("Cleaning up...")
if gp.exists(areatempraster):
    gp.delete(areatempraster)
if gp.exists(wbtempraster):
    gp.delete(wbtempraster)
if gp.exists(nhd_flow_shp):
    gp.delete(nhd_flow_shp)
if gp.exists(nhd_wb_shp):
    gp.delete(nhd_wb_shp)
if gp.exists(nhd_area_shp):
    gp.delete(nhd_area_shp)