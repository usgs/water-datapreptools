import arcpy
import sys
import os

#import ELEVDATA_tools as ET # import each toolset here...

class Toolbox(object):
    def __init__(self):
        """Toolbox for preprocessing data for creating or refreshing a StreamStats project."""
        self.label = "ELEVDATAtools"
        self.alias = "ELEVDATA processing tools"

        # List of tool classes associated with this toolbox
        self.tools = [makeELEVDATAIndex,ExtractPoly,CheckNoData,FillNoData,ProjScale]

class makeELEVDATAIndex(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "2.A Make ELEVDATA Index"
        self.description = "Function to make ELEVDATA into a raster catalog for clipping to the basin polygons."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName = "Output Geodatabase",
            name = "OutLoc",
            datatype = "DEWorkspace",
            parameterType = "Required",
            direction = "Input")

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

        param4 = arcpy.Parameter(
            displayName = "Output Polygon Feature Class",
            name = "OutFC",
            datatype = "GPString",
            parameterType = "Required",
            direction = "Input")

        params = [param0,param1,param2,param3,param4]
        return params

    def execute(self, parameters, messages):
        """The source code of the tool."""

        # Make a raster catalog and polygon index to NED tiles in a directory tree. 
        # 
        # Usage: MakeNEDIndex_NHDPlusBuildRefreshTools <Output_Geodatabase> <Output_Raster_Catalog_Name> 
        #                                              <Coordinate_System> <Input_NED_Workspace> <Output_Polygon_Feature_Class>
        #        
        #
        # Description: 
        #
        # Makes a geodatabase raster catalog plus a polygon feature class containing the footprints of the 
        # rasters in the raster catalog. All rasters to be loaded to the raster catalog should be on a common 
        # projection and coordinate system. All rasters under the input workspace are loaded, so be sure only
        # rasters of a particular type are included in the directory tree under that workspace. The primary 
        # purpose of this tool is to create an index to National Elevation Dataset (NED) data, which meets the 
        # above constraints. Use for other purposes has not been tested.
        #
        # Created on: Fri Nov 13 2009 04:25:02 PM
        #   (generated by ArcGIS/ModelBuilder)
        # Alan Rea, ahrea@usgs.gov, 20091113, original coding
        #    updated  20091231, cleanup and commenting
        #    updated  20100311, removed hard-coded toolbox reference
        # Theodore Barnhart, tbarnhart@usgs.gov, 20190220, moved to code.usgs.gov for version control.
        #   Updated for arcpy.

        OutLoc = parameters[0].valueAsText # output geodatabase
        rcName = parameters[1].valueAsText # raster catalogue name
        coordsysRaster = parameters[2].valueAsText # raster coordinate system
        InputELEVDATAws = parameters[3].valueAsText # geodatabase of elevation data
        OutFC = parameters[4].valueAsText # output polygon feature class

        Output_Raster_Catalog = OutLoc + "\\" + rcName
        Raster_Management_Type = "UNMANAGED"
        coordsysPolys = coordsysRaster     # Coordinate system for polygon footprints. Use same NED grid to specify. (type Spatial Reference)

        if arcpy.Exists(OutLoc): 
          DSType = arcpy.Describe(arcpy.Describe(OutLoc).CatalogPath).WorkspaceType
          arcpy.AddMessage("Dataset type =" + DSType)
          if DSType == "FileSystem":
            arcpy.AddError("Output " + OutLoc + " is not a Geodatabase. Output location must be a Geodatabase.")
        else:
          arcpy.AddError("Output " + OutLoc + "does not exist")
        
        # Now that we're sure the geodb exists, make it the active workspace
        arcpy.Workspace = OutLoc
        arcpy.ScratchWorkspace = OutLoc
        arcpy.AddMessage("Working geodatabase is " + OutLoc)

        if arcpy.Exists(OutFC): 
          arcpy.AddError("Output feature class" + OutFC + "Already exists")
          sys.exit(0) # end script

        if arcpy.Exists(Output_Raster_Catalog): 
          arcpy.AddError("Output raster catalog" + Output_Raster_Catalog + "Already exists")
          sys.exit(0) # end script

        # Process: Create Raster Catalog...
        arcpy.AddMessage("Creating output raster catalog " + Output_Raster_Catalog)
        arcpy.CreateRasterCatalog_management(OutLoc, rcName, coordsysRaster, coordsysPolys, "", "0", "0", "0", Raster_Management_Type, "")
        
        # Process: Workspace To Raster Catalog...
        arcpy.AddMessage("Loading all rasters under workspace " + InputNEDWs + " into raster catalog...")
        arcpy.WorkspaceToRasterCatalog_management(InputNEDWs, Output_Raster_Catalog, "INCLUDE_SUBDIRECTORIES", "NONE") 
        
        tabName = "tmp.dbf" # maybe strip off the .dbf since the table should be inside a geodatabase.
        tmpTablePath = "%s\\%s"%(OutLoc,tabName) # generate path to temp table

        if arcpy.Exists(tmpTablePath): # if the temp table exists, delete it.
          arcpy.AddMessage("Temp table exits, deleting...")
          arcpy.Delete_management(tmpTablePath)

        arcpy.CreateTable_management(OutLoc,tabName) # create empty table
        # Process: Export Raster Catalog paths, then join paths to raster catalog
        arcpy.AddMessage("Getting full pathnames into raster catalog")
        #out_table = ScratchName("tmp","tbl","table") # create blank table
        arcpy.ExportRasterCatalogPaths_management(Output_Raster_Catalog, "ALL", tmpTablePath)
        arcpy.JoinField_management(rcName, "OBJECTID", tmpTablePath, "SourceOID", "Path")
        
        # Process: Use Copy Features to make a polygon feature class out of the raster catalog footprints 
        arcpy.AddMessage("Making polygon index of raster catalog...")
        arcpy.CopyFeatures_management(rcName, OutFC)
        
        # remove temporary table 
        arcpy.AddMessage("Removing temporary table ... ")
        arcpy.Delete_management(tmpTablePath)
       

        # handle errors and report using GPMsg function
        #except xmsg:
        #  arcpy.AddError(str(xmsg))
        #except arcgisscripting.ExecuteError:
        #  line, file, err = TraceInfo()
        #  arcpy.AddError("Geoprocessing error on %s of %s:" % (line,file))
        #  for imsg in range(0, arcpy.MessageCount):
        #    if arcpy.GetSeverity(imsg) == 2:     
        #      arcpy.AddError(imsg) # AddReturnMessage
        #except:  
        #  line, file, err = TraceInfo()
        #  arcpy.AddError("Python error on %s of %s" % (line,file))
        #  arcpy.AddError(err)
        #finally:
          # Clean up here (delete cursors, temp files)
        #  arcpy.Delete_management(out_table)
        #  pass # you need *something* here 

        return

class ExtractPoly(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "2.B Extract Polygons"
        self.description = "Extract polygon area from ELEVDATA."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName = "Output Workspace",
            name = "Input_Workspace",
            datatype = "DEWorkspace",
            parameterType = "Required",
            direction = "Input")

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
        """The source code of the tool."""

        # This tool extracts a polygon area from NED tiles, and merges to a single grid.
        # This tool requires as input a polygon feature class created from a raster catalog and containing the 
        # full pathnames to each raster in the raster catalog (specifically NED, but probably other seamless tiled 
        # rasters would work). This feature class can be created using the Make NED Index tool, also 
        # bundled with this toolbox. The polygon attribute table must contain a field named "Path", containing
        # full pathnames to all the NED tile grids. 
        #
        # Extract an area from NED tiles
        # 
        # Usage: ExtractPolygonAreaFromNED_NHDPlusBuildRefreshTools <Output_Workspace> <NED_Index_Polygons> 
        #                                                              <Clip_Polygon> <Output_Grid>
        #
        # Alan Rea, ahrea@usgs.gov, 2009-12-31, original coding
        #

        arcpy.CheckOutExtension("Spatial") # checkout the spatial analyst extension
        Input_Workspace = parameters[0].valueAsText #workspace
        nedindx = parameters[1].valueAsText # NED Index (polygon) Layer
        clpfeat = parameters[2].valueAsText # clip polygon feature layer, I think this should be a collection of features so all the clipping happens in a loop....
        OutGrd = parameters[3].valueAsText # name of output grid

        # set working folder
        arcpy.env.Workspace = Input_Workspace
        arcpy.env.ScratchWorkspace = arcpy.Workspace

        # select index tiles overlapping selected poly(s)
        intersectout = arcpy.env.Workspace + "\\clipintersect.shp"
        if arcpy.Exists(intersectout):
          arcpy.Delete_management(intersectout)
        
        arcpy.Clip_analysis(nedindx, clpfeat, intersectout) # clip the dataset

        # Create search cursor 
        rows = arcpy.SearchCursor(intersectout) 
        row = rows.Next()
        rownum = 1

        # Make sure the "Path" field exists in the index polys--Not done yet, should do error trapping 
        #if arcpy.Exists(row):
        #desc = arcpy.Describe(row)
        #if "Path" in desc.Fields.Name 

        pth = str(row.GetValue("Path"))
        arcpy.AddMessage("Setting raster snap and coordinate system to match first input grid " + pth )
        try:
          assert arcpy.Exists(pth) == True
          arcpy.env.SnapRaster = pth
          arcpy.env.OutputCoordinateSystem = pth
        except:
          arcpy.AddError("First input grid does not exist: " + pth)
          arcpy.AddMessage("Stopping... ")
        
        #arcpy.Extent = clpfeat

        #strMosaicList = ""
        MosaicList = []
        while row: # iterate through rows (of the intersected data) and extract the relevent portion of the DEM.

          pth = str(row.GetValue("Path"))
          #OutTmpg = "tmpg" + str(rownum)
          #arcpy.AddMessage("Extracting " + pth + " to " + OutTmpg)
          arcpy.Extent = pth # set extent
          MosaicList.append(arcpy.ExtractByMask(pth, clpfeat)) # extract the chunk of the DEM needed.

          #strMosaicList = strMosaicList + OutTmpg + ","
          #rownum = rownum + 1
          row = rows.Next() # advance row cursor

        #strMosaicList = strMosaicList[:-1]
        arcpy.Extent = clpfeat # reset extent to the whole layer
        
        arcpy.AddMessage("Merging grids to create " + OutGrd)
        arcpy.Merge_management(MosaicList,OutGrd) # merge the grids together.
        
        #InExpression = "merge (" + strMosaicList + ")"
        #arcpy.SingleOutputMapAlgebra_sa(InExpression, OutGrd)

        ## No Longer Needed I think
        #arcpy.AddMessage("Removing temporary grids ... ")
        #n = 1
        #while n < rownum:
        #  tmpnm = "tmpg" + str(n)
        #  arcpy.Delete_management(tmpnm)
        #  n = n + 1

        del rows
         
        # handle errors and report using GPMsg function
        #except MsgError, xmsg:
        #  GPMsg("Error",str(xmsg))
        #except arcgisscripting.ExecuteError:
        #  line, file, err = TraceInfo()
        #  GPMsg("Error","Geoprocessing error on %s of %s:" % (line,file))
        #  for imsg in range(0, arcpy.MessageCount):
        #    if arcpy.GetSeverity(imsg) == 2:     
        #      GPMsg("Return",imsg) # AddReturnMessage
        #except:  
        #  line, file, err = TraceInfo()
        #  GPMsg("Error","Python error on %s of %s" % (line,file))
        #  GPMsg("Error",err)
        #finally:
        #  # Clean up here (delete cursors, temp files)
        #  arcpy.Delete_management(intersectout) # remove the intersect data
        #  pass # you need *something* here 
        return

class CheckNoData(object):
    ##################################
    #
    # Converted from model builder to arcpy, Theodore Barnhart, tbarnhart@usgs.gov, 20190222
    #
    ##################################
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "2.C CheckNoData"
        self.description = "Finds NODATA values in a grid and makes a polygon feature class with value 1 if it is NODATA, and 0 if it contains data values."
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

        param2 = arcpy.Parameter(
            displayName = "Output Feature Layer",
            name = "OutPolys",
            datatype = "DEFeatureClass",
            parameterType = "Required",
            direction = "Output")

        params = [param0,param1,param2]
        return params

    def execute(self, parameters, messages):
        """The source code of the tool."""
        # Load parameters
        InGrid = parameters[0].valueAsText
        tmpLoc = parameters[1].valueAsText
        OutPolys_shp = parameters[2].valueAsText

        if OutPolys_shp == '#' or not OutPolys_shp:
            OutPolys_shp = "%s\\RasterT_SingleO1.shp"%(tmpLoc) # provide a default value if unspecified

        # Local variables:
        tmpGrid = "%s\\SingleOutput2"%(tmpLoc)

        # Process: Single Output Map Algebra
        #tempEnvironment0 = arcpy.env.extent
        arcpy.env.extent = InGrid
        #tempEnvironment1 = arcpy.env.cellSize
        arcpy.env.cellSize = InGrid
        arcpy.gp.SingleOutputMapAlgebra_sa("con ( isnull ( InGrid ), 1 )", tmpGrid, "''")
        #arcpy.env.extent = tempEnvironment0
        #arcpy.env.cellSize = tempEnvironment1

        # Process: Raster to Polygon
        arcpy.RasterToPolygon_conversion(tmpGrid, OutPolys_shp, "NO_SIMPLIFY", "Value", "SINGLE_OUTER_PART", "")
        arcpy.Delete_management(tmpGrid) # remove the temporary grid

        return

class FillNoData(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "2.D Fill NoData Cells"
        self.description = "Replaces NODATA values in a grid with mean values within 3x3 window. May be run repeatedly to fill in areas wider than 2 cells. Note the output is floating point, even if the input is integer. Note this will expand the data area of the grid around the outer edges of data, in addition to filling in NODATA gaps in the interior of the grid."
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
        """The source code of the tool."""
        # ---------------------------------------------------------------------------
        # 2D_Fill_NoData_Cells.py
        # Created on: 2019-02-21 16:28:59.00000
        #   (generated by ArcGIS/ModelBuilder)
        # Usage: 2D_Fill_NoData_Cells <InGrid> <OutGrid> 
        # Description: 
        # Replaces NODATA values in a grid with mean values within 3x3 window. May be run repeatedly to fill in areas wider than 2 cells. Note the output is floating point, even if the input is integer. Note this will expand the data area of the grid around the outer edges of data, in addition to filling in NODATA gaps in the interior of the grid.
        # 
        # Converted from model builder to arcpy, Theodore Barnhart, tbarnhart@usgs.gov, 20190222
        # ---------------------------------------------------------------------------

        import arcpy

        # load parameters
        InGrid = parameters[0].valueAsText
        OutGrid = parameters[1].valueAsText
        
        if arcpy.Exists(InGrid) == False:
            arcpy.AddError("Input grid does not exist.")
            sys.exit(0)

        if arcpy.Exists(OutGrid):
            arcpy.AddError("Output grid exists.")
            sys.exit(0)

        # Process: Single Output Map Algebra
        #tempEnvironment0 = arcpy.env.extent
        arcpy.env.extent = InGrid
        #tempEnvironment1 = arcpy.env.cellSize
        arcpy.env.cellSize = InGrid
        arcpy.gp.SingleOutputMapAlgebra_sa("con ( isnull ( InGrid ) , focalmean ( InGrid  ) , InGrid  )", OutGrid, "''")
        #arcpy.env.extent = tempEnvironment0
        #arcpy.env.cellSize = tempEnvironment1

        return

class ProjScale(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "2.E Project and Scale NED"
        self.description = "Project a NED grid to a user-specified coordinate system. Handles setting a cell registration point. Also multiplies by 100 and converts to integer grid format."
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
        """The source code of the tool."""
        # Projects a NED grid to a user-specified coordinate system, handling cell registration. Converts
        #  output grid to centimeters (multiplies by 100 and rounds). 
        # 
        # Usage: ProjectNED_NHDPlusBuildRefreshTools <Input_Workspace> <Input_Grid> <Output_Grid> 
        #                                              <Output_Coordinate_System> <Output_Cell_Size> <Registration_Point>
        # 
        #
        # Alan Rea, ahrea@usgs.gov, 20091216, original coding
        #    ahrea, 20091231 updated comments
        # Theodore Barnhart, tbarnhart@usgs.gov, 20190222
        #       Converted original code to arcpy

        import sys, os, arcgisscripting, re

        # import egis helper module egis.py from same folder as this script
        from egis import *
          
        #try: 
        # set up geoprocessor
        #gp = arcgisscripting.create(9.3)

        # set up GPMsg messaging. If this line is omitted, default is "gp"
        #GPMode("both") # valid values: "gp","print","both"
          
        try:
            # get parameters from tools
            Input_Workspace = parameters[0].valueAsText # Input workspace. (type Workspace)
            InGrd = parameters[1].valueAsText           # Input grid name. (type String)
            OutGrd = parameters[2].valueAsText          # Output grid name. (type String)
            OutCoordsys = parameters[3].valueAsText     # Coordinate system for output grid. (type Coordinate System)
            OutCellSize = parameters[4].valueAsText     # Cell size for output grid. (type Analysis cell size)
            RegistrationPoint = parameters[5].valueAsText  # Registration point. Space separated coordinates. (type String)
             
            # set working folder
            arcpy.Workspace = Input_Workspace
            arcpy.ScratchWorkspace = arcpy.Workspace
            tmpDEM = "tmpdemprj"
            # clear the processing extent
            arcpy.Extent = ""
            arcpy.OutputCoordinateSystem = ""
            arcpy.SnapRaster = ""
            arcpy.AddMessage("Projecting " + InGrd + " to create " + tmpDEM)
            arcpy.ProjectRaster_management(InGrd, tmpDEM, OutCoordsys, "BILINEAR", OutCellSize, "#", RegistrationPoint)

            arcpy.Extent = tmpDEM
            arcpy.OutputCoordinateSystem = OutCoordsys
            arcpy.SnapRaster = tmpDEM
            arcpy.CellSize = tmpDEM
            InExpression = "int ((\'%s\' * 100) + 0.5)"%(tmpDEM) # expression to convert raster units.
            arcpy.AddMessage("Converting to integer centimeter elevations and producing final output grid " + OutGrd)
            arcpy.SingleOutputMapAlgebra_sa(InExpression, OutGrd)

            arcpy.AddMessage("Removing temporary grid tmpdemprj... ")
            arcpy.Delete_management(tmpDEM)

            #If process completed successfully, open prj.adf file and assign z units
            if arcpy.exists(Input_Workspace + "\\" + OutGrd):
                o = open(Input_Workspace + "\\" + OutGrd + "\\prj_new.adf","w")
                data = open(Input_Workspace + "\\" + OutGrd + "\\prj.adf").read()
                o.write(re.sub("Zunits        NO","Zunits        100",data))
                o.close()
                os.rename(Input_Workspace + "\\" + OutGrd + "\\prj.adf", Input_Workspace + "\\" + OutGrd + "\\prj_backup.adf")
                os.rename(Input_Workspace + "\\" + OutGrd + "\\prj_new.adf", Input_Workspace + "\\" + OutGrd + "\\prj.adf")
        except:
            raise  

            # # handle errors and report using GPMsg function
            # except MsgError, xmsg:
            #   GPMsg("Error",str(xmsg))
            # except arcgisscripting.ExecuteError:
            #   line, file, err = TraceInfo()
            #   GPMsg("Error","Geoprocessing error on %s of %s:" % (line,file))
            #   for imsg in range(0, arcpy.MessageCount):
            #     if gp.GetSeverity(imsg) == 2:     
            #       GPMsg("Return",imsg) # AddReturnMessage
            # except:  
            #   line, file, err = TraceInfo()
            #   GPMsg("Error","Python error on %s of %s" % (line,file))
            #   GPMsg("Error",err)
            # finally:
            #   # Clean up here (delete cursors, temp files)
            #   pass # you need *something* here 
            #     return

# class Setup(object):
#     def __init__(self):
#         """Define the tool (tool name is the name of the class)."""
#         self.label = "Setup"
#         self.description = "Generate the file structure for Stream Stats Data Preprocessing."
#         self.canRunInBackground = False

#     def getParameterInfo(self):
#         """Define parameter definitions"""
#         params = None
#         return params

#     def isLicensed(self):
#         """Set whether tool is licensed to execute."""
#         return True

#     def updateParameters(self, parameters):
#         """Modify the values and properties of parameters before internal
#         validation is performed.  This method is called whenever a parameter
#         has been changed."""
#         return

#     def updateMessages(self, parameters):
#         """Modify the messages created by internal validation for each tool
#         parameter.  This method is called after internal validation."""
#         return

#     def execute(self, parameters, messages):
#         """The source code of the tool."""
#         return