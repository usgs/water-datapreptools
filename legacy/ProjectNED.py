"""
  GP Script Tool - ProjectNED.py
"""
# Projects a NED grid to a user-specified coordinate system, handling cell registration. Converts
#  output grid to centimeters (multiplies by 100 and rounds). 
# 
# Usage: ProjectNED_NHDPlusBuildRefreshTools <Input_Workspace> <Input_Grid> <Output_Grid> 
#                                              <Output_Coordinate_System> <Output_Cell_Size> <Registration_Point>
# 
#
# Alan Rea, ahrea@usgs.gov, 20091216, original coding
#    ahrea, 20091231 updated comments

import sys, os, arcgisscripting, re

# import egis helper module egis.py from same folder as this script
from egis import *
  
try: 

  # set up geoprocessor
  gp = arcgisscripting.create(9.3)

  # set up GPMsg messaging. If this line is omitted, default is "gp"
  GPMode("both") # valid values: "gp","print","both"
  
  # <get arguments from the command line here>
  Input_Workspace = sys.argv[1] # Input workspace. (type Workspace)
  # Input grid name
  InGrd = sys.argv[2]           # Input grid name. (type String)
  # name of output grid
  OutGrd = sys.argv[3]          # Output grid name. (type String)
  # output grid coord system
  OutCoordsys = sys.argv[4]     # Coordinate system for output grid. (type Coordinate System)
  # output cell size
  OutCellSize = sys.argv[5]     # Cell size for output grid. (type Analysis cell size)
  # grid registration point
  RegistrationPoint = sys.argv[6]  # Registration point. Space separated coordinates. (type String)
  
  # set working folder
  gp.Workspace = Input_Workspace
  gp.ScratchWorkspace = gp.Workspace

  gp.Extent = ""
  gp.OutputCoordinateSystem = ""
  gp.SnapRaster = ""
  GPMsg("","Projecting " + InGrd + " to create " + "tmpdemprj")
  gp.ProjectRaster_management(InGrd, "tmpdemprj", OutCoordsys, "BILINEAR", OutCellSize, "#", RegistrationPoint)

  gp.Extent = "tmpdemprj"
  gp.OutputCoordinateSystem = OutCoordsys
  gp.SnapRaster = "tmpdemprj"
  gp.CellSize = "tmpdemprj"
  InExpression = "int (('tmpdemprj' * 100) + 0.5)"
  GPMsg("","Converting to integer centimeter elevations and producing final output grid " + OutGrd)
  gp.SingleOutputMapAlgebra_sa(InExpression, OutGrd)

  GPMsg("","Removing temporary grid tmpdemprj... ")
  gp.delete_management("tmpdemprj")

  #If process completed successfully, open prj.adf file and assign z units
  if gp.exists(Input_Workspace + "\\" + OutGrd):
      o = open(Input_Workspace + "\\" + OutGrd + "\\prj_new.adf","w")
      data = open(Input_Workspace + "\\" + OutGrd + "\\prj.adf").read()
      o.write(re.sub("Zunits        NO","Zunits        100",data))
      o.close()
      os.rename(Input_Workspace + "\\" + OutGrd + "\\prj.adf", Input_Workspace + "\\" + OutGrd + "\\prj_backup.adf")
      os.rename(Input_Workspace + "\\" + OutGrd + "\\prj_new.adf", Input_Workspace + "\\" + OutGrd + "\\prj.adf")    

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
  
