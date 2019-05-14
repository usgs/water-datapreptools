"""
  GP Script Tool - ExtractPolygonAreaFromNED.py
"""
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

import sys, os, arcgisscripting

# import egis helper module egis.py from same folder as this script
from egis import *

try: 

  # set up geoprocessor
  gp = arcgisscripting.create(9.3)

  # Check out Spatial Analyst extension license
  gp.CheckOutExtension("Spatial")

  # set up GPMsg messaging. If this line is omitted, default is "gp"
  GPMode("both") # valid values: "gp","print","both"

  # Script arguments...
  Input_Workspace = sys.argv[1]
  # NED Index (polygon) Layer
  nedindx = sys.argv[2]
  # clip polygon feature layer
  clpfeat = sys.argv[3]
  # name of output grid
  OutGrd = sys.argv[4]
  
  # set working folder
  gp.Workspace = Input_Workspace
  gp.ScratchWorkspace = gp.Workspace

  # select index tiles overlapping selected poly(s)
  intersectout = gp.Workspace + "\\clipintersect.shp"
  if gp.exists(intersectout):
    gp.delete(intersectout)
  #gp.Intersect_analysis(intersect_list, intersectout, "ALL", "", "INPUT")
  gp.Clip_analysis(nedindx, clpfeat, intersectout)

  # Create search cursor 
  #
  rows = gp.SearchCursor(intersectout) 
  row = rows.Next()
  rownum = 1

  # Make sure the "Path" field exists in the index polys--Not done yet, should do error trapping 
  #if gp.Exists(row):
  #desc = gp.Describe(row)
  #if "Path" in desc.Fields.Name 

  pth = str(row.GetValue("Path"))
  GPMsg("","Setting raster snap and coordinate system to match first input grid " + pth )
  if gp.Exists(pth):
    gp.SnapRaster = pth
    gp.OutputCoordinateSystem = pth
  else:
    GPMsg("e", "First input grid does not exist: " + pth)
    raise MsgError, "Stopping... "
  
  #gp.Extent = clpfeat

  strMosaicList = ""

  while row:

    pth = str(row.GetValue("Path"))
    OutTmpg = "tmpg" + str(rownum)
    GPMsg("","Extracting " + pth + " to " + OutTmpg)
    gp.Extent = pth
    gp.ExtractByMask_sa(pth, clpfeat, OutTmpg)
    strMosaicList = strMosaicList + OutTmpg + ","
    rownum = rownum + 1
    row = rows.Next()

  strMosaicList = strMosaicList[:-1]
  gp.Extent = clpfeat
  GPMsg("","Merging " + strMosaicList + " to create " + OutGrd)

  InExpression = "merge (" + strMosaicList + ")"
  gp.SingleOutputMapAlgebra_sa(InExpression, OutGrd)

  GPMsg("","Removing temporary grids ... ")
  n = 1
  while n < rownum:
    tmpnm = "tmpg" + str(n)
    gp.delete_management(tmpnm)
    n = n + 1

  del rows
   
# handle errors and report using GPMsg function
except MsgError, xmsg:
  GPMsg("Error",str(xmsg))
except arcgisscripting.ExecuteError:
  line, file, err = TraceInfo()
  GPMsg("Error","Geoprocessing error on %s of %s:" % (line,file))
  for imsg in range(0, gp.MessageCount):
    if gp.GetSeverity(imsg) == 2:     
      GPMsg("Return",imsg) # AddReturnMessage
except:  
  line, file, err = TraceInfo()
  GPMsg("Error","Python error on %s of %s" % (line,file))
  GPMsg("Error",err)
finally:
  # Clean up here (delete cursors, temp files)
  gp.delete(intersectout)
  pass # you need *something* here 

