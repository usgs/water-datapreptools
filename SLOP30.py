
# ---------------------------------------------------------------------------
# SLOP30.py
# Created: 20111205
# ahrea@usgs.gov
# Usage: SLOP30 <Workspace> <SlopeGrid> <outgrid> 
# Description: 
# Computes grid of 1's and 0's of cells with slopes gt 30 percent.
# ---------------------------------------------------------------------------

# module imports
import sys, string, os
# EGIS helper module
import egis
from egis import GPMsg, MsgError
# Geoprocessing error exception
from arcgisscripting import ExecuteError as GPError 

# set up geoprocessor, with spatial analyst license

# A. for 9.3, 9.3.1; but supported in 10.0:
gp = egis.getGP(9.3,"spatial")  

try: 

  # set up GPMsg messaging. If this line is omitted, default is "gp"
  egis.GPMode("both") 
  
  # <get arguments from the command line here>
  WorkDir = gp.GetParameterAsText(0)
  SlopeG = gp.GetParameterAsText(1)
  OutGrid = gp.GetParameterAsText(2)

  # Set processing environment
  gp.workspace = WorkDir
  gp.ScratchWorkspace = gp.Workspace
  gp.snapRaster = SlopeG
  gp.extent = SlopeG
  gp.cellSize = SlopeG
  
  # Process: compute grid of 1's and 0's using criteria
  InExpression = "con(" + SlopeG + " gt 30, 1, 0) "
  gp.SingleOutputMapAlgebra_sa(InExpression, OutGrid)
  
  
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
  pass
