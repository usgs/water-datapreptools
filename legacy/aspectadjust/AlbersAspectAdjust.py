
# ---------------------------------------------------------------------------
# AlbersAspectAdjust.py
# Created: 20111205
# ahrea@usgs.gov
# Usage: AlbersAspectAdjust <Workspace> <AlbersDEM> <outgrid> 
# Description: 
# Computes an aspect grid adjusted to true north, assuming input DEM is 
# based on US Albers projection parameters 
# (i.e. USA_Contiguous_Albers_Equal_Area_Conic_USGS_version.prj)
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
  outgrid = gp.GetParameterAsText(2)
 
  srcpath = os.path.dirname(sys.argv[0])         
  GPMsg("",srcpath)

  # Process: compute unadjusted aspect
  gp.workspace = WorkDir
  gp.ScratchWorkspace = gp.Workspace
  gp.snapRaster = dem
  gp.extent = dem
  gp.cellSize = dem
  gp.Aspect_sa(dem, "tmp_rawaspect")
  
  # Process: adjust using adjustment grid
  InExpression = "con(tmp_rawaspect eq -1, -1, (tmp_rawaspect - (" + str(srcpath) + "\\asp_adjx100 / 100 ) + 360 ) mod 360)"
  gp.SingleOutputMapAlgebra_sa(InExpression, outgrid)
  
  # Remove temp grid
  gp.delete_management("tmp_rawaspect")
  
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
