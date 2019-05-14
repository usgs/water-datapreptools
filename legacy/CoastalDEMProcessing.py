"""
  CoastalDEMProcessing.py
"""
# Sets elevs for water and other areas in DEM.
#
# Usage:CoastalDEMProcessing <Workspace> <Input_raw_dem> <Input_LandSea_polygon_feature_class> <Output_DEM> <Sea_Level>
#
# Al Rea, ahrea@usgs.gov, 05/01/2010, original coding
# ahrea, 10/30/2010 updated with more detailed comments

import sys, os, arcgisscripting

# import egis helper module egis.py from same folder as this script
from egis import *
  
try: 

  # set up geoprocessor
  gp = arcgisscripting.create(9.3)

  # set up GPMsg messaging. If this line is omitted, default is "gp"
  GPMode("both") # valid values: "gp","print","both"
  
  # Script arguments...
  Input_Workspace = sys.argv[1]    # input workspace (type Workspace)
  grdName = sys.argv[2]            # input DEM grid name (type String)
  InFeatureClass = sys.argv[3]     # input LandSea feature class (type Feature Class)
  OutRaster = sys.argv[4]          # output DEM grid name (type String)
  seaLevel = sys.argv[5]           # Elevation to make the sea
  
  # Check out Spatial Analyst extension license
  gp.CheckOutExtension("Spatial")

  # set working folder
  gp.Workspace = Input_Workspace
  gp.ScratchWorkspace = gp.Workspace

  gp.Extent = grdName
  gp.SnapRaster = grdName
  gp.OutputCoordinateSystem = grdName
  gp.CellSize = grdName
  #cellsz = grdName.Cellsize

  #buffg = polygrid (hucbufland)
  gp.PolygonToRaster_conversion(InFeatureClass, "Land", "mskg")

  #seaGrd = con(mskGrd == -1, seaLevel)
  strCmd = "con('%s' == %s, %s)" % ("mskg", "-1", seaLevel)
  GPMsg("",strCmd)
  gp.SingleOutputMapAlgebra_sa(strCmd, "seag")

  #landGrd = con(mskGrd == 1 and grdName <= 0, 1, grdName)
  strCmd = "con(%s == 1 and %s <= 0, %s, %s)" % ("mskg", grdName, "1", grdName)
  GPMsg("",strCmd)
  gp.SingleOutputMapAlgebra_sa(strCmd, "landg")

  #nochgGrd = con(mskGrd == 0, grdName)
  strCmd = "con('%s' == %s, %s)" % ("mskg", "0", grdName)
  GPMsg("",strCmd)
  gp.SingleOutputMapAlgebra_sa(strCmd, "nochgg")


  strMosaicList = "seag, landg, nochgg"
  strCmd = "merge (" + strMosaicList + ")"
  GPMsg("",strCmd)
  gp.SingleOutputMapAlgebra_sa(strCmd, OutRaster)
  

  GPMsg("","Removing temporary grids ... ")
  #gp.delete_management("mskg")
  #gp.delete_management("seag")
  #gp.delete_management("landg")
  #gp.delete_management("nochgg")



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
  pass # you need *something* here 
  
