
# ---------------------------------------------------------------------------
# MakeCPG_simple.py
# Created: 20100806
# ahrea@usgs.gov
# Usage: MakeCPG_simple <OutputWorkspace> <fdr> <fac> <ParameterGrid> <outgrid> 
# Description: 
# Makes a continuous parameter grid from a simple parameter grid. Also requires 
# a flowdirection and flowaccumulation grid. Rounds output values to integer. 
# Use separate tool for floating-pt output. 
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
  fdr = gp.GetParameterAsText(1)
  fac = gp.GetParameterAsText(2)
  ParameterGrid = gp.GetParameterAsText(3)
  outgrid = gp.GetParameterAsText(4)
 
  # Process: Flow Accumulation...
  gp.workspace = WorkDir
  gp.ScratchWorkspace = gp.Workspace
  gp.snapRaster = fdr
  gp.extent = fdr
  gp.cellSize = fdr
  gp.FlowAccumulation_sa(fdr, "tmpfacw", ParameterGrid, "FLOAT")

  # Process: Single Output Map Algebra...
  InExpression = "int((( tmpfacw + " + ParameterGrid + " ) / ( fac + 1.0 )) + 0.5)" 
  GPMsg("",InExpression)
  gp.SingleOutputMapAlgebra_sa(InExpression, outgrid)

  # Remove temp grids
  gp.delete_management("tmpfacw")

  
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
