"""HYDRODEM Script tool"""

import sys, os

# EGIS helper functions 
# If egis.py not in the same folder as this script, it must
# in the Python path (PYTHONPATH) or its folder explicitly added:
# sys.path.append( \   
#    os.path.join(os.environ["ARCGISHOME"],"ArcToolbox","Scripts_egis")
import egis
# Import commonly used functions so "egis." prefix not required
from egis import GPMsg, ScratchName, MsgError
from arcgisscripting import ExecuteError as GPError # short name for GP errors


try: 

  # set up geoprocessor, with spatial analyst license
  gp = egis.getGP(9.3,"spatial")
  
  # Get Arguments
  
  # Processing workspace
  outWS = gp.GetParameterAsText(0)

  # Dataset List (9)
  lstDS = []
  # create local pathnames for datasets
  # if the dataset was not supplied, enter a "#" for that argument
  for kArg in range(1,9): # args 1,2,3... 8
    strPath = gp.GetParameterAsText(kArg)
    if strPath: strPath = os.path.basename(strPath)
    else: strPath = "#"
    lstDS.append(strPath)

  # determine cell size of DEM grid
  DemFull = os.path.join(outWS,lstDS[1])
  ProcCellSize = int(gp.Describe(DemFull).MeanCellHeight)
    
  if ProcCellSize not in [10,30]:
    GPMsg("w","Cell Size of DEM grid is %s" % ProcCellSize)
  
  # Advanced processing parameters
  lstVal = []
  for kArg in range(9,17): # args 8-18
    lstVal.append(float(gp.GetParameterAsText(kArg)))
  
  # processing flags

  DoBowling, DoInWall, DoDrains = 1,1,1
  if lstDS[3] == "#" or lstDS[4] == "#": DoBowling = 0
  if lstDS[6] == "#": DoInWall = 0
  if lstDS[7] == "#": DoDrains = 0

  ### HARDCODED ARGUMENTS ###
  # Processing AMLs path
  # AMLPath = "D:\\ss_amls"
  # note, if you put the amls in the same folder as this script:
  AMLPath = os.path.dirname(sys.argv[0]) + "/"
  DoCopyLayers = 0
  ###


  # HYDRODEM arguments  Python Variables
  # ------------------  ---------------
  #  1  outdir             outWS
  #  2  huc8cov           lstDS[0]
  #  3  origdem              .
  #  4  dendrite             .
  #  5  bowl_polys           .
  #  6  bowl_lines           .
  #  7  snap_grid            .
  #  8  inwall               .
  #  9  drainplug         lstDS[7]
  # 10  start_path         AMLPath (folder this script is in)
  # 11  thresh            lstVal[0]
  # 12  thresh2           lstVal[1]
  # 13  buffdist             .
  # 14  inwallbuffdist       .
  # 15  inwallht             .
  # 16  outwallht            .
  # 17  agreebuf             .
  # 18  agreesmooth          .
  # 19  agreesharp           .
  # 20  bowldepth         lstVal[9] 
  # 21  copylayers        DoCopyLayers (hardcoded)
  # 22  cellsz            ProcCell
  # 23  bowling           DoBowling
  # 24  in_wall           DoInWall
  # 25  drain_plugs       DoDrains

  # Assemble arguments into a list
  lstArgs = [outWS] + lstDS + [AMLPath] + lstVal + \
          [DoCopyLayers, ProcCellSize, DoBowling, DoInWall, DoDrains]
  # convert to an argument string
  strDSArgs = "%s "*len(lstArgs) % tuple(lstArgs)
  HydroDEM = os.path.join(os.path.dirname(sys.argv[0]), "hydrodem_work_mod.aml")
  strCmd = "grid\n" + "&r %s %s" % (HydroDEM, strDSArgs)
  GPMsg(strCmd)

  egis.ArcCommands(gp,strCmd,outWS)
  

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
  pass # you need *something* here 

