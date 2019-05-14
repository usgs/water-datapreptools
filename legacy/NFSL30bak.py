
# ---------------------------------------------------------------------------
# NFLS30.py
# Created: 20111205
# ahrea@usgs.gov
# Usage: NFSL30 <Workspace> <SlopeGrid> <AspectGrid> <outgrid> 
# Description: 
# Computes grid of 1's and 0's of cells with slopes gt 30 percent and
# aspect within 60 degrees of North. Note aspect grid should be adjusted to 
# true north using Adjusted True Aspect tool.
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
  AspectG = gp.GetParameterAsText(2)
  OutGrid = gp.GetParameterAsText(3)

  # Set processing environment
  gp.workspace = WorkDir
  gp.ScratchWorkspace = gp.Workspace
  gp.snapRaster = SlopeG
  gp.extent = SlopeG
  gp.cellSize = SlopeG
  
  # Process: compute grid of 1's and 0's using criteria
  InExpression = "con(" + SlopeG + " gt 30 and (" + AspectG + " lt 60 or " + AspectG + " gt 300), 1, 0) "
  gp.SingleOutputMapAlgebra_sa(InExpression, "tmpnfsl30")
  
  InExpression = "con ( isnull(tmpnfsl30) and " + SlopeG + " ge 0, 0, tmpnfsl30 )"
  gp.SingleOutputMapAlgebra_sa(InExpression, OutGrid)

  gp.delete_management("tmpnfsl30")  
  
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
