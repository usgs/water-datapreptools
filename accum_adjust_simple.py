
#############################################################################
###       Simple one-point at a time flow accumulation adjustment         ###
#############################################################################
 
# Adds a value to flowaccumulation grid given an input point, cascading down
# the flowdirection tgrid. 
# Al Rea ahrea@usgs.gov, 6/17/2010, original coding
# 

# module imports

# commonly used standard modules
import sys, os
# EGIS helper module
import egis
from egis import GPMsg, MsgError
# Geoprocessing error exception
from arcgisscripting import ExecuteError as GPError 

# set up geoprocessor, with spatial analyst license

gp = egis.getGP(9.3,"spatial")  

try: 

  # set up GPMsg messaging. If this line is omitted, default is "gp"
  egis.GPMode("both") 
  # or by specifying it in the GPMsg function
  #GPMsg("w","Hello World","print")
  
  # <get arguments from the command line here>
  ptin = gp.GetParameterAsText(0)
  facin = gp.GetParameterAsText(1)
  fdrin = gp.GetParameterAsText(2)
  filin = gp.GetParameterAsText(3)
  facout = gp.GetParameterAsText(4)
  incrval = int(gp.GetParameterAsText(5))
      
  # set working folder
  Input_Workspace = os.path.dirname(facin)
  GPMsg("ws = " + Input_Workspace)
  gp.Workspace = Input_Workspace
  gp.ScratchWorkspace = gp.Workspace
  
  # egis.ScratchName method to get valid scratch names
  tmpGrid = egis.ScratchName("","","grid")

  gp.Extent = fdrin
  if gp.Exists(fdrin):
    gp.SnapRaster = fdrin
    gp.OutputCoordinateSystem = fdrin
  else:
    GPMsg("e", "Input fdr grid does not exist: " + fdrin)
    raise MsgError, "Stopping... "
  
  gp.CostPath_sa(ptin, filin, fdrin, tmpGrid)
  #GPMsg(tmpGrid)
  
  tmpGrid2 = egis.ScratchName("","","grid")
  InExpression = "con(" + tmpGrid + ", " + facin + " + " + str(incrval) + ")"
  GPMsg(tmpGrid2 + " = " + InExpression)
  gp.SingleOutputMapAlgebra_sa(InExpression, tmpGrid2)

  InExpression = "merge(" + tmpGrid2 + ", " + facin + ")"
  GPMsg(facout + " = " + InExpression)
  gp.SingleOutputMapAlgebra_sa(InExpression, facout)

# handle errors and report using GPMsg function
except MsgError, xmsg:
  GPMsg("Error",str(xmsg))
except GPError:
  line, file, err = egis.TraceInfo()
  GPMsg("Error","Geoprocessing error on %s of %s:" % (line,file))
  for imsg in range(0, gp.MessageCount):
    if gp.GetSeverity(imsg) == 2:     
      GPMsg("Return",imsg) # AddReturnMessage
except:  
  line, file, err = egis.TraceInfo()
  GPMsg("Error","Python error on %s of %s" % (line,file))
  GPMsg("Error",err)
finally:
  # Clean up here (delete cursors, temp files)
  GPMsg("","Removing temporary grids ... ")
  gp.delete_management(tmpGrid)
  gp.delete_management(tmpGrid2)

  pass