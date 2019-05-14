
# ---------------------------------------------------------------------------
# BatchRecalcFac.py
# Created: 20130606
# ahrea@usgs.gov
# Usage: BatchRecalcFac <Workspace> <FDR_name> <FAC_name> {mask_grd}
# Description: 
# Recalcs flowaccumulation from flowdirection, with optional mask grid. 
#   Designed to work easily in GP batch grid.
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
  fdrgrd = gp.GetParameterAsText(1)
  facgrd = gp.GetParameterAsText(2)
  mskgrd = gp.GetParameterAsText(3)
 
  # Set environment
  gp.workspace = WorkDir
  gp.ScratchWorkspace = gp.Workspace
  gp.mask = mskgrd
  gp.extent = fdrgrd
  gp.cellSize = fdrgrd

  # Process: delete existing FAC dataset
  if gp.exists(WorkDir + "\\" + facgrd):
    GPMsg("w", "Deleting old " + facgrd + " from workspace " + WorkDir )
    gp.delete_management(facgrd)
  GPMsg("", "Recomputing " + facgrd + " from " + fdrgrd + " in workspace " + WorkDir )
  gp.FlowAccumulation_sa (fdrgrd, facgrd, "#", "INTEGER")

  gp.ClearEnvironment("mask")
  
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
