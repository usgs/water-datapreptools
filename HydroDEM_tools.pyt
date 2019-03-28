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
        self.tools = [SetupBathyGrad, CoastalDEM, HydroDEM]

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

class CoastalDEM(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "4.B Coastal DEM Processing"
        self.description = "Lowers the level of the sea to ensure it is always below land level. Also raises any land cells to 1 cm unless they are within a polygon with Land attribute of 0. The input polygons (LandSea) needs to identify the sea with a Land attribute of -1. Land is identified with a Land value of 1. No change polygons should have Land value of 0."
        self.canRunInBackground = False

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
        """CoastalDEMProcessing.py"""
        # Sets elevs for water and other areas in DEM.
        #
        # Usage:CoastalDEMProcessing <Workspace> <Input_raw_dem> <Input_LandSea_polygon_feature_class> <Output_DEM> <Sea_Level>
        #
        # Al Rea, ahrea@usgs.gov, 05/01/2010, original coding
        # ahrea, 10/30/2010 updated with more detailed comments
        # Theo Barnhart, 20190225, tbarnhart@usgs.gov, updated to arcpy 

        #import sys, os, arcgisscripting

        # import egis helper module egis.py from same folder as this script
        #from egis import *
          
        try: 

          # set up geoprocessor
          #gp = arcgisscripting.create(9.3)

          # set up GPMsg messaging. If this line is omitted, default is "gp"
          #GPMode("both") # valid values: "gp","print","both"
          
          # Script arguments...
          Input_Workspace = parameters[0].valueAsText    # input workspace (type Workspace)
          grdName = parameters[1].valueAsText            # input DEM grid name (type String)
          InFeatureClass = parameters[2].valueAsText     # input LandSea feature class (type Feature Class)
          OutRaster = parameters[3].valueAsText          # output DEM grid name (type String)
          seaLevel = parameters[4].valueAsText           # Elevation to make the sea
          
          # Check out Spatial Analyst extension license
          arcpy.CheckOutExtension("Spatial")

          # set working folder
          arcpy.env.Workspace = Input_Workspace
          arcpy.env.ScratchWorkspace = arcpy.env.Workspace

          arcpy.env.Extent = grdName
          arcpy.env.SnapRaster = grdName
          arcpy.env.OutputCoordinateSystem = grdName
          arcpy.env.CellSize = grdName
          #cellsz = grdName.Cellsize

          #buffg = polygrid (hucbufland)
          arcpy.PolygonToRaster_conversion(InFeatureClass, "Land", "mskg")

          #seaGrd = con(mskGrd == -1, seaLevel)
          strCmd = "con('%s' == %s, %s)" % ("mskg", "-1", seaLevel)
          arcpy.AddMessage(strCmd)
          arcpy.SingleOutputMapAlgebra_sa(strCmd, "seag")

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



        # handle errors and report using GPMsg function
        except MsgError, xmsg:
            arcpy.AddError(str(xmsg))
        except arcpy.ExecuteError:
            line, file, err = TraceInfo()
            arcpy.AddError("Geoprocessing error on %s of %s:" % (line,file))
            for imsg in range(0, arcpy.MessageCount):
                if arcpy.GetSeverity(imsg) == 2:     
                    arcpy.AddReturnMessage(imsg) # AddReturnMessage
        except:  
            line, file, err = TraceInfo()
            arcpy.AddError("Python error on %s of %s" % (line,file))
            arcpy.AddError(err)
        finally:
            # Clean up here (delete cursors, temp files)
            pass # you need *something* here 

class HydroDEM(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "4.C HydroDEM"
        self.description = "Run make_HydroDEM.py to process DEMs, burning in streams and building walls."
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
            datatype = "DERasterBand",
            parameterType = "Optional",
            direction = "Input")

        param6 = arcpy.Parameter(
            displayName = "NHD Flowline Grid",
            name = "bowl_lines",
            datatype = "DERasterBand",
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

        params = [param0,param1,param2,param3,param4,param5,param6,param7,param8,param9,param10,
                    param11,param12,param13,param14,param15,param16, param17]

        return params

    def execute(self, parameters, messages):
        return None


class PreHydroDEM(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "4.C PreHydroDEM"
        self.description = "This tool creates the necessary inputs for HydroDEM"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName = "Output Workspace",
            name = "output_workspace",
            datatype = "DEWorkspace",
            parameterType = "Required",
            direction = "Input") # maybe should be Output

        param1 = arcpy.Parameter(
            displayName = "Dissolved Local Watershed Dataset",
            name = "huc8",
            datatype = "DEFeatureClass",
            parameterType = "Required",
            direction = "Input")

        param2 = arcpy.Parameter(
            displayName = "Dendrite Stream Network",
            name = "dendrite",
            datatype = "DEFeatureClass",
            parameterType = "Required",
            direction = "Input")

        param3 = arcpy.Parameter(
            displayName = "Inner Wall Dataset",
            name = "inwall",
            datatype = "DEFeatureClass",
            parameterType = "Required",
            direction = "Input")

        param4 = arcpy.Parameter(
            displayName = "DEM to be used in HydroDEM",
            name = "dem",
            datatype = "DERasterBand",
            parameterType = "Required",
            direction = "Input")

        param5 = arcpy.Parameter(
            displayName = "Cellsize",
            name = "cellsize",
            datatype = "GPString",
            parameterType = "Required",
            direction = "Input")

        param5.value = "10"

        param6 = arcpy.Parameter(
            displayName = "Sink Points Dataset (optional)",
            name = "sinkpoint",
            datatype = "DEFeatureClass",
            parameterType = "Optional",
            direction = "Input")

        params = [param0,param1,param2,param3,param4,param5]
        return params

    def execute(self, parameters, messages):
        """Source Code Goes Here."""
        # ---------------------------------------------------------------------------
        # pre_hydrodem.py
        # Created on: 04/29/2010
        # Martyn Smith
        # ---------------------------------------------------------------------------
        # 
        # Updated to Arcpy, Theodore Barnhart, tbarnhart@usgs.gov, 20190225

        import sys, os, egis
        # Import commonly used functions so "egis." prefix not required
        from egis import GPMsg, ScratchName, MsgError
        from arcgisscripting import ExecuteError as GPError # short name for GP errors

        #initiate geoprocessor
        gp = egis.getGP(9.3)

        # Set script to overwrite if files exist
        gp.overwriteoutput = 1

        # Local variables
        output_workspace = gp.GetParameterAsText(0)
        huc8 = gp.GetParameterAsText(1)
        dendrite = gp.GetParameterAsText(2)
        inwall = gp.GetParameterAsText(3)
        dem = gp.GetParameterAsText(4)
        cellsize = gp.GetParameterAsText(5)
        sinkpoint = gp.GetParameterAsText(6)

        try:
            #create coverages of input feature classes in output workspace
            gp.addmessage("Starting conversion of feature classes to coverages...")
            gp.FeatureclassToCoverage_conversion(huc8, output_workspace + "\\huc8")
            gp.FeatureclassToCoverage_conversion(inwall, output_workspace + "\\inwall")
            gp.FeatureclassToCoverage_conversion(dendrite, output_workspace + "\\nhdrch")
            gp.addmessage("Copying DEM...")
            if gp.exists(output_workspace + "\\dem"):
                gp.delete(output_workspace + "\\dem")
            gp.CopyRaster_management(dem,output_workspace + "\\dem")

            #copy projection to inwall coverage in case of empty inwall
            egis.ArcCommands(gp,"projectcopy cover nhdrch cover inwall" ,output_workspace,"")

            #set extent for feature to raster conversion
            if sinkpoint != "":
                gp.addmessage("Creating Drain Plug coverage...")
                gp.Extent = dem
                gp.FeatureToRaster_conversion(sinkpoint, "OBJECTID", output_workspace + "\\sinklnk", cellsize)
                gp.RasterToPolygon_conversion(output_workspace + "\\sinklnk", output_workspace + "\\sinkpoly.shp", "NO_SIMPLIFY")
                gp.FeatureclassToCoverage_conversion(output_workspace + "\\sinkpoly.shp", output_workspace + "\\drain_plugs")

        except:
            # Print error message if an error occurs
            print gp.GetMessages()

        #clean up temp datasets
        if gp.exists(output_workspace + "\\sinkpoly.shp"):
            gp.delete(output_workspace + "\\sinkpoly.shp")

# class PreHydroDEM(object):
#     def __init__(self):
#         """Define the tool (tool name is the name of the class)."""
#         self.label = "4.C "
#         self.description = ""
#         self.canRunInBackground = False

#     def getParameterInfo(self):
#         """Define parameter definitions"""
#         param0 = arcpy.Parameter(
#             displayName = "",
#             name = "",
#             datatype = "",
#             parameterType = "Required",
#             direction = "Input") # maybe should be Output

#         param1 = arcpy.Parameter(
#             displayName = "",
#             name = "",
#             datatype = "",
#             parameterType = "Required",
#             direction = "Input")

#         param2 = arcpy.Parameter(
#             displayName = "",
#             name = "",
#             datatype = "",
#             parameterType = "Required",
#             direction = "Input")

#         param3 = arcpy.Parameter(
#             displayName = "",
#             name = "",
#             datatype = "",
#             parameterType = "Required",
#             direction = "Input")

#         param4 = arcpy.Parameter(
#             displayName = "",
#             name = "",
#             datatype = "",
#             parameterType = "Required",
#             direction = "Input")

#         params = [param0,param1,param2,param3,param4]
#         return params

#     def execute(self, parameters, messages):
#         """Source Code Goes Here."""