
# ---------------------------------------------------------------------------
# ComputeSlopePercent.py
# Created: 20111207
# ahrea@usgs.gov
# Usage: ComputeSlopePercent <Workspace> <DEM> <ZFactor> <outgrid> 
# Description: 
# Computes a percent slope grid from a DEM.
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
  dem = gp.GetParameterAsText(1)
  ZFactor =  gp.GetParameterAsText(2)
  outgrid = gp.GetParameterAsText(3)
 
  # Set environment
  gp.workspace = WorkDir
  gp.ScratchWorkspace = gp.Workspace
  gp.snapRaster = dem
  gp.extent = dem
  gp.cellSize = dem
  
  # Compute slope 
  gp.Slope_sa(dem, outgrid, "PERCENT_RISE", float(ZFactor) )
  
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
