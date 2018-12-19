"""EGIS Python Utilities 2.0.3  Wed 06/02/2010 14:08:22.75

Utility functions used by the EGIS Toolbox python scripts.

Examples of how this module are provided in an example script, 
included in the module:

>>> print egis.TEMPLATE

Although this program has been used by the USGS, no warranty, expressed or
implied, is made by the USGS or the United States Government as to the
accuracy and functioning of the program and related program material nor shall
the fact of distribution constitute any such warranty, and no responsibility
is assumed by the USGS in connection therewith.

Author: Curtis Price, cprice@usgs.gov
"""
import os, sys, time, arcgisscripting

# document version
Version = r"EGIS Python Utilities 2.0.3  Wed 06/02/2010 14:08:22.75" 

##print Version # report on import (for debugging)

def getGP(GPVersion="9.3",strExt=None):
  """Instantiates a geoprocessor object.

  arguments
      GPVersion - GP version, specified as number or string
      strExt - ";" - delimited list of extensions
   
  examples  
      gp = getGP()
      gp = getGP(9.2,"spatial;3d")
      
  Note - if you don't need your script to run pre-10.0, 
  use these lines instead of the above:
  
      import arcpy
      arcpy.CheckoutExtension("spatial")
      from arcpy.sa import * # if you need python map algebra
  """   
  gp = arcgisscripting.create(float(GPVersion))
  if strExt:
    for ex in strExt.split(";"):
      try:
        strStatus = gp.CheckOutExtension(ex)
        if strStatus != "CheckedOut": GPMsg("w",ex)
      except Exception, xmsg:
        GPMsg("w",str(xmsg))
        pass
  return gp

def ScratchName(strPrefix="",strSuffix="",strDataType="",strWorkspace=""):
  """Return a scratch name with a prefix and suffix.
  
  This method is a wrapper of the gp.CreateScratchName
  method with a few enhancements.
  
  arguments
  
    prefix - prefix for scratch name (default="xx")
    suffix - suffix added to scratch name (default="")
    dataType - includes CreateScratchName options:
    
  notes
  
  1) If a workspace is not provided, the scratch workspace
  is determined by picking the first valid workspace of:
  scratch workspace, current workspace, or Windows TEMP.

  2) The scratch name returned is verified against the workspace
  to ensure that the pathname does not have a conflict, for example
  if creating a folder, it checks to ensure there is not an existing
  file with the same name. For coverages and grids, a check is made
  of the INFO directory for name conflicts.

  3) If the suffix includes an file extension, and the datatype
  supports extensions (for example, folders and coverages do not),
  the extension is returned.
    >>> gp.CreateScratchName("",".img","raster","e:/work")
    u'e:/work\\xx0'   
    >>> nact.ScratchName("",".img","raster","e:/work")
    u'e:/work\\xx0.img'

  """
  import os
  gp = getGP()

  strDT = strDataType.lower()

  # Check out prefixes and suffixes
  if strPrefix == "": strPrefix = "xx"
  pp = os.path.splitext(strPrefix)
  if pp[1] and strSuffix == "": 
    # split prefix into prefix + suffix
    strPrefix = pp[0]
    strSuffix = pp[1]
  strPre = strPrefix.lower()
  strSuf = strSuffix.lower()
  
  # make sure our scratch workspace is a folder if required
  strDT = strDataType.lower()
  if strDT in ["coverage","folder","shapefile","arcinfotable",
      "workspace","dbase","grid","tin"]:
    strScratchWS = ScratchWS(strWorkspace,"Folder")
    # change strDataType for gp.CreateScratchName syntax
    if strDT == "grid": strDataType = "coverage" 
    elif strDT == "tin": strDataType = "folder"
    elif strDT == "info": strDataType = "ArcInfoTable"
  else:
    strScratchWS = ScratchWS(strWorkspace)

  # validate prefix, suffix names against workspace
  ff = os.path.splitext(strSuf)
  strPre = gp.ValidateTableName(strPrefix,strScratchWS)
  strSuf = gp.ValidateTableName(ff[0],strScratchWS) + ff[1]
  # Don't allow starting the scratch name with a digit!
  if strPre[:1].isdigit(): strPre = "x" + strPre
  
  # loop until we're SURE we have an available pathname
  strWild = None # Initialize - in case we need it (see below)
  GotValidScratchName = False    # we'll loop until this is true!
  TryNum = 0 # incrementor
  while not GotValidScratchName:
    # set incremented scratch name prefix
    strPre1 = strPre + str(TryNum)
    TryNum += 1  # increment, for next time around
    # invoke gp.CreateScratchName method
    strScratchName = \
        gp.CreateScratchName(strPre1,strSuf,strDataType,strScratchWS)
    # add back extension if gp.CreateScratchName dropped it
    # (except coverages, grids, folders)
    Ext = os.path.splitext(strScratchName)[1]
    if strDT not in ["shapefile","coverage","grid","folder"]: 
      strScratchName = os.path.splitext(strScratchName)[0] + strSuf       
    # Is this a valid scratch name?
    GotValidScratchName = True  # innocent until proven guilty!
    if gp.Exists(strScratchName):
      GotValidScratchName = False  
    elif strDataType == "shapefile":
      # check for .dbf named same as proposed .shp file
      if gp.Exists(os.path.splitext(strScratchName)[0] + ".dbf"):
        GotValidScratchName = False
    elif strDT in ["coverage","grid"]:
      # check for name conflicts in INFO tables "<DSName>.xxx"
      if not strWild:  # so we only do this once!
        envWS = gp.Workspace # remember workspace
        strWild = os.path.basename(strScratchName) + ".*"
        gp.Workspace = strScratchWS
        InfoList = gp.ListTables(strWild,"ArcInfoTable")
        gp.Workspace = envWS # restore
      elif os.path.basename(strScratchName) in InfoList:
        GotValidScratchName = False
    strDir = os.path.dirname(strScratchName)
    if strDir.lower() == "in_memory":
      strScratchName = ForwardPath(strScratchName)
    else:
      strScratchName = os.path.realpath(strScratchName)
      print "here"
  return strScratchName

def ScratchWS(strWS="",strWSType=""):
  """Validate a scratch workspace path

  arguments
  
  strWS (optional) - existing workspace path
  
  strWSType (optional)
    - "Folder" - always return a folder path
    - "Geodatabase" - always return a geodatabase
    - "in_memory" - always return the "in_memory" workspace

  notes
  
  The first valid path in this list is returned:
    1) strWS (if strWS is a valid path)
    2) gp.ScratchWorkspace
    3) gp.Workspace
    4) Windows TEMP folder

  An error is raised if strWSType is "Geodatabase" and
  1) 2) and 3) above are not geodatabase workspaces

  """
  import os, arcgisscripting
  gp = getGP()

  # parse workspace type
  strWST = strWSType.lower()
  if strWST.find("f") != -1: strWSType = "Folder"
  elif strWST.find("g") != -1: strWSType = "Geodatabase"
  
  # in_memory is a special case - just return it
  elif strWST.find("m") != -1 or strWS.lower() == "in_memory": 
    return "in_memory"

  # find a valid scratch workspace path
  if not gp.Exists(strWS):
    strWS = gp.ScratchWorkspace
  if not gp.Exists(strWS):
    strWS = gp.Workspace
  if not gp.Exists(strWS):
    strWS = gp.GetSystemEnvironment("TEMP")
  # Check the path we have found to make sure it aggress
  # with the strWSType argument.
  # Note, we only doing a gp.Describe unless we have to
  # for performance reasons
  WSExt = os.path.splitext(strWS)[1].lower()
  if strWSType == "Folder":
    if WSExt == ".gdb" or not os.path.isdir(strWS):
      strWS = os.environ["TEMP"]
  elif strWSType == "Geodatabase": 
    if WSExt not in [".mdb",".gdb"] or \
       gp.Describe(strWS).WorkspaceType == "FileSystem":
      raise Exception, "%s is not a geodatabase workspace" % strWS
  return strWS


def GetExtent(gp,Dataset=None,Grace=0.0):
  """Returns a geoprocessing extent (as a string) 
  
  arguments
  
  gp - geoprocessing object
  
  Dataset (Feature layer or geodataset) - 
    * If not specified, the current GP extent is used.
    * If the feature layer has an active selection,
      only those features are used to determine the extent.
  
  Grace (number) - 
    length to expand the extent (in extent's units)
    
  notes
  
  This function will not alter the current
  extent, but you can use it do so:
  
  gp.Extent = egis.GetExtent("e:/work/mygrid")
  gp.Extent = egis.GetExtent("polygon layer")
  
      
  """ 
  
  try:
    lstExt = None  # initialize variable
    d = gp.Describe(Dataset)  # if dataset not valid, go to except
    Ex = gp.Describe(d.CatalogPath).Extent # returns an extent object
    lstExt = [Ex.XMin, Ex.YMin, Ex.XMax,Ex.YMax]
    if d.DataType != "FeatureLayer": raise Exception # our work is done
    # if this IS a layer - make sure there is a selected set
    numSel = int(gp.GetCount(Dataset).GetOutput(0))
    numRow = int(gp.GetCount(d.CatalogPath).GetOutput(0))
    if numSel == numRow: raise Exception # nothing selected, our work is done
    # Okay, this is a feature layer with selected features
    # Find the extent of selected features
    Rows = gp.SearchCursor(lyrFeatures)
    Row = Rows.Next()
    Ex = Row.Shape.Extent
    lstExt = [Ex.XMin, Ex.YMin, Ex.XMax,Ex.YMax]
    Row = Rows.Next()
    while Row:      
      Ex = Row.Extent
      if lstExt[0] > Ex.XMin: lstExt[0] = Ex.XMin 
      if lstExt[1] > Ex.YMin: lstExt[1] = Ex.YMin    
      if lstExt[2] < Ex.XMax: lstExt[2] = Ex.XMax
      if lstExt[3] < Ex.YMax: lstExt[3] = Ex.YMax
      Row = Rows.Next()
      del Row, Rows
  except Exception, xmsg:
    if lstExt == None:  
      # this is not a data set - use current extent
      try:
        strExtent = gp.Extent
        lstExt = [float(k) for k in strExt.split()]      
      except:
        # if we couldn't parse it, the extent is something like "MINOF"
        if Grace != 0:
          # can't add a grace area to something like "MINOF", sorry
          raise Exception, "can't add grace area to extent \"%s\"" % strExt
        return strExtent
    if not gp.Exists(d.CatalogPath):
      # something unexpected went wrong
      raise Exception, xmsg
      
  # Add "grace area" if requested
  try:
    Grace = float(Grace)
    if Grace != 0:
      lstExt[0] -= Grace
      lstExt[1] -= Grace
      lstExt[2] += Grace
      lstExt[3] += Grace  
  except:
    raise Exception, "Invalid value for Grace"
  lstExt = [str(ee) for ee in lstExt]    
  strExtent = "%s %s %s %s" % tuple(lstExt)

  # round numbers ending with .0 (like gp.Extent does)
  strExtent = (strExtent + " ").replace(".0 "," ").strip()
  
  return strExtent

def SetSnapRaster(gp,SnapRasterDS,XReg=None,YReg=None,CellSize=None):
  """Sets the geoprocessor SnapRaster environment
  
  arguments

  gp - geoprocessor object
  
  SnapRasterDS - snap raster path (or raster layer) 
  
  If the raster does not exist, a new one is created
  using the following parameters.  
  
  XReg, YReg, CellSize - XY registration point and cell size
  
  These are ignored if SnapRasterDS exists.
  
  notes
  
  The current effective (snapped) extent is returned as a string.
  If the current extent isn't explicitly set (for example: "MAXOF",None)
  that's what is returned.
  
  This tool checks out a spatial analyst license 
  if one is not already available.
  """

  try:
    gp.CheckOutExtension("spatial")  # need a spatial analyst license
  except:
    raise Exception, "Spatial Analyst license is not available."
  try:
    d = gp.Describe(SnapRasterDS)
    if d.DatasetType.find("Raster") == -1:
      raise Exception, "%s is not a raster data set" % RasterDataset
    SnapRasterDS = d.CatalogPath
    if XReg != None:
      GPMsg("w","Using existing Snap Raster %s" % SnapRasterDS)
  except Exception, xmsg:
    # Snap path does not exist, create one
    if not ( XReg and YReg and CellSize):
      raise Exception, \
        "XReg, YReg, and CellSize must be specified to create snap raster"
    # save environment
    tmpExtent = gp.Extent
    tmpCell = gp.CellSize
    gp.Extent = None
    gp.CellSize = CellSize
    gp.Extent = "%s %s %s %s" % \
      (XReg,YReg,XReg + CellSize * 2.1, YReg + CellSize * 2.1) 
    gp.SnapRaster = None
    # Single Output Map Algebra will honor this extent always!
    gp.SingleOutputMapAlgebra("1.0",SnapRasterDS)
    gp.Extent = tmpExtent
    gp.CellSize = tmpCell

  # Set SnapRaster environment
  gp.SnapRaster = SnapRasterDS  
    
  # Snap current extent to new Snap Raster
  try:    
    gp.Extent = gp.Extent + " " + SnapRasterDS
  except:
    pass
  
  return gp.Extent
 
def DeleteList(FileList,Verbose=False):
  """Delete a ";"-delimited or python list of items
  
  (modified from ESRI HelperFunctions.py)
  
  example
  
   DeleteList("E:/work/temp1;e:/work/temp2")
   DeleteList(["file1","file2","file3"])
  
  """
  gp = getGP()
  if type(FileList) == type(""):
    FileList = FileList.split(";")
    
  for ff in FileList:
    if ff: # skip None or "" that may be in the list
      try:
        gp.Delete(f)
        if Verbose: GPMsg("Deleted " + f)
      except:
        if Verbose: GPMsg("w","Could not delete" + f)
        continue


def GetCount(gp, input):
    """GetCount in one step (like 9.2 GetCount tool)
    (borrowed from ESRI script HelperFunctions.py)
    """
    countObject = gp.GetCount(input)
    return int(countObject.getoutput(0))

def AdjustExtent(strExtent, amount=5, units="percent"):
    """Adjust a string Extent (default: +5 percent)
    
     strExtent - a string Extent, for example, "0 0 100 100"
     amount - amount to grow (+) or shrink (-) the extent
     units - "percent" or "mapunits"
     
    (modified from ESRI script HelperFunctions.py)
    
    NOTE: This has been superseded by the egis.GetExtent function.
    """
    # (modified from ESRI HelperFunctions.py, GetLargerExtent)
    # Adjust string Extent 
    
    # AdjustExtent("1000 1000 2000 2000",5) == '950.0 950.0 2050.0 2050.0' 
    # AdjustExtent("0 0 100 100",3,"map") ==  '-3.0 -3.0 103.0 103.0'
    # AdjustExtent("0 0 500 500",-5) == '25.0 25.0 475.0 475.0        

    try:
      # convert string extent to list of floats
      minX, minY, maxX, maxY = [ float(i) for i in strExtent.split() ]
    
      # if percent, (default) compute in map units
      if units == "percent":
        percent = float(amount) / 100.0
        amount = max(maxX - minX,maxY - minY) * percent
  
      # expand extent
      minX = minX - amount
      minY = minY - amount
      maxX = maxX + amount
      maxY = maxY + amount
        
      NewExtent = [minX, minY, maxX, maxY]
      NewExtent = [ str(i) for i in NewExtent ]
      return " ".join(NewExtent)
    except:
      raise Exception, \
        "Usage: AdjustExtent(<string Extent>,<amount>,{\"percent\"|\"mapunits\"}"

  
class MsgError(Exception):
  """Exception class for reporting a general error from a script
      Example use:
        raise MsgError, "Houston, we have a problem...."
  """
  # this routine makes it possible to distinguish unexpected python errors
  # from expected trapped errors we are reporting to the user.
  # (The easier way, string exceptions, are deprecated at Py 2.5)
  pass

def StringIsTrue(strText=""):
    """Converts string to boolean value
    
      True only if the first character of string is:
        "t" ("true","totally","TRUTHINESS")
        or
        "y" ("yes", "yup", "Yowsa!")
    """
    strText = strText.strip().lower()[0]
    test = max(strText.find("t"),strText.find("y"))
    return bool(test + 1)

class GPModeThing:
  """A little Python class to keep track of print mode for GPMsg()
    
  See the help for the GPMsg() function for details.
    """
  def __init__(self):
    self.data = "gp"  # set default: "gp"
    
  def __call__(self,strMode=None):
    #  "" strMode returns current value"""
    if strMode:
      # check argument to make sure it is valid
      strMode = strMode.lower()
      if strMode not in ["gp","print","both","off"]:
        print 'Valid values are: "gp","print","both", or "off"'
      else:
        self.data = strMode
    return self.data

# initialize it
GPMode = GPModeThing()


def GPMsg(sev=None,msg=None,msgType=None):
  """Send a message to the geoprocessor,"python-print", or both
  
  Geoprocessing messages displayed with methods like "gp.AddMessage"
  may be visible in ArcGIS or in tty python output, but when
  running the script within IDE environments like IDLE or Wing,
  invisible, or display garbled. This method allows you
  to specify to send a message to python-print, just the geoprocessor, or 
  to both places. The syntax also allows for a little less typing
  than the gp messaging methods it calls.
  
  dependencies
  
  GetGP, GPModeThing

  arguments

  sev - severity code / message option
  
    "Message","Warning","Error","Return","Time","Gpmessages"
    (only the first letter is required)

   msg - text message to display
   
    A special syntax for msg is used to support gp.AddIDMessage().
    (Spaces are required between each argument!)
    
      ID <MessageID> {AddArgument1} {AddArgument2}
     
    For example, to do this:
      gp.AddIDMessage("Error", 12, outFeatureClass)
    You can use this syntax with GPMsg:
      GPMsg("Error","ID %s %s" % (12,outFeatureClass))
    (Please only use error numbers documented in the ArcGIS help!)
         
   msgType - Where to send the message. If this argument is given
      the destination will stay the same until GPMode is used or
      the argument is given again.
   
      "gp"      Geoprocessor (default)
      "print"   Python print
      "both"    Both places
      "off"     Nothing prints anywhere (use with care)
      None      Use current value of GPMode()
   
  examples
  
     GPMode("print")  # change default output to python-print
     GPMsg("This is a message") # default output, print ONLY
     GPMsg("t","The time is now","gp") # output to ArcGIS ONLY
     GPMsg() # print gp.AddMessages(0) GP messages to ARCGIS only 
     GPMsg("w","ID 345","both") # use gp.AddIDMessage, output to both
     GPMode("off") # no messages printed
     
     Output:    
     
     This is a message 
     10:40:05 The time is now    
     Executing: CopyFeatures poly_inout E:\work\poly_inout_CopyFeatures.shp # 0 0 0
     Start Time: Wed Apr 07 11:11:58 2010
     Executed (CopyFeatures) successfully.
     End Time: Wed Apr 07 11:11:58 2010 (Elapsed Time: 0.00 seconds)
     WARNING 000345: Input must be a workspace    
  """
  gp = getGP()

  if not msgType: 
    msgType = GPMode()  # use current value of GPMode
  else:
    msgType = GPMode(msgType) # set GPMode (and remember for next GPMsg)
  
  if msgType == "off": 
    # Do not print anything! (like AML &messages &off)
    return  
  
  # support shorthand usage: GPMsg("message") and GPMsg()
  if sev != None  and msg == None:
    # GPMsg("message") ->  GPMsg("","message")
    sev,msg = "",sev
  elif sev == None and msg == None:
    # GPMsg() -> GPMsg("Message",gp.GetMessages(0))
    sev,msg  = "g",""  
  
  # decode severity to a code 0 thru 6:
  # isev = 0  message
  # isev = 1  warning
  # isev = 2  error
  # isev = 3  returnmessage
  # isev = 4  message with clock time
  # isev = 5  return gp.GetMessages(0)
  sevdict = {"w":1, "e":2, "r":3, "t":4,"g":5 }
  try:
    sev = str(sev).lower()[:1] # "Warning" -> "w"
    isev = sevdict[sev]
  except:
    isev = 0
  
  # support gp.AddIDMessage
  try:
    IDMessage = False # guilty until innocent
    lstMsg = msg.split() # ["ID",<msgID>,{arg1},{arg2}]
    if lstMsg.pop(0).lower() == "id":
      MessageID = int(lstMsg.pop(0))         
      # do a cursor check of message ID
      if MessageID <= 0 or MessageID > 99999: raise         
      IDMessage = True
      # capture AddArgument1, AddArgument2
      IDArg1,IDArg2 = "",""
      IDArg1 = lstMsg[0]
      IDArg2 = lstMsg[1]
  except:
    pass
     
  # send our message
  
  if msgType.lower() in ["gp","both"]:
    # send message to geoprocessor
    if isev == 0:
      gp.AddMessage(msg)
    elif isev == 1:
      if not IDMessage:
        gp.AddWarning(msg)
      else:
        gp.AddIDMessage("Warning",MessageID,IDArg1,IDArg2)
    elif isev == 2:
      if not IDMessage:
        gp.AddError(msg)
      else:
        gp.AddIDMessage("Error",MessageID,IDArg1,IDArg2)             
    elif isev == 3:
      gp.AddReturnMessage(int(msg))
    elif isev == 4:
      strTime = time.strftime("%H:%M:%S ", time.localtime())
      gp.AddMessage(strTime + msg)
    elif isev == 5:
      gp.AddMessage(gp.GetMessages(0))
  if msgType.lower() in ["print","both"]:
    # just print 
    SevLabel = ["","WARNING","ERROR"]
    if isev == 0:
      print msg
    elif isev in [1,2]:
      if not IDMessage:
        print "%s: %s" % (SevLabel[isev],msg)
      else:
        print "GP %s %s: %s %s" % (SevLabel[isev],MessageID,IDArg1,IDArg2)     
    elif isev == 4:
      strTime = time.strftime("%H:%M:%S ", time.localtime())
      print strTime + msg
    elif isev == 5:
      msg = gp.GetMessages(0)
      if len(msg) > 0: print msg
    elif isev == 3:
      print gp.GetMessage(int(msg))
      
    
def TraceInfo():        
  """Returns traceback information for easy reporting. 
     Modified from Dale Honeycutt's (ESRI) blog post:
     "Error handling in Python script tools":
     http://tinyurl.com/dfsqzr
     Curtis Price - cprice@usgs.gov - 2009-05-06
    
    Here's an example of how to use it:
  
       except:  
         line, file, err = TraceInfo()
         gp.AddError("Python error on %s of %s\n" % (line,file,err)
  """
  import sys, os, traceback
  try:
    # get traceback info
    tb = sys.exc_info()[2]   
    tbinfo = traceback.format_tb(tb)[0]  # script name + line number
    # Get line number
    ErrLine = tbinfo.split(", ")[1] 
    # Get error message      
    ErrMsg = traceback.format_exc().splitlines()[-1]  
  except:
    # just in case *this*  thing fails!
    Here = os.path.realpath(__file__)
    Msg = traceback.format_exc().splitlines()[-1]
    Msg = "TraceInfo failed\n%s\n(%s)" % (Here, Msg)
    raise Exception, Msg
  return ErrLine, sys.argv[0], ErrMsg

def CheckOutExtension(gp,strExtName):
  """Checks out an ArcGIS extension.
  
  Like gp.CheckOutExtension(), except returns the string
  "NotInstalled" if the requested extension is not installed.

  example:
    strStat = egis.CheckOutExtension(gp,"MPSAtlas")
  """
  try:
    import os

    # Set up dictionary of "tag paths" to identify whether
    # each extension is installed

    TagPath = {\
    "spatial"             : "Bin/GridCore.dll",\
    "3d"                  : "Bin/3DAnalystUI.dll",\
    "streetmap"           : "Locators/US Single House.avs",\
    "mpsatlas"            : "Solutions/MPSAtlas",\
    "network"             : "NetworkAnalyst",\
    "schematics"          : "Schematics",\
    "survey"              : "SurveyAnalyst",\
    "datainteroperability": "Data Interoperability Extension",\
    "geostats"            : "Bin/GATools.dll",\
    "tracking"            : "Bin/TrackingCore.dll" \
    }
    lstTag = TagPath.keys()
    lstTag.sort()
    strTags = ','.join(lstTag)
    print strTags
    # is extension installed?
    strExt = strExtName.lower()
    if TagPath.has_key(strExt):
      strFlag = gp.getsystemenvironment("ARCGISHOME") + TagPath[strExt]
    else:
      strMsg = "ArcGIS Extension \"%s\" not supported.\n" % strExt
      strMsg += "Valid keys: " + strTags
      raise Exception, strMsg
    if not gp.Exists(strFlag): return "NotInstalled"
    
    # OK, it's installed, go ahead and try to check it out
    return gp.CheckOutExtension(strExt)

  except Exception, xmsg:
    raise Exception, str(xmsg)


def ListPaths(inDir=".",strWild=".*",FoldersOnly=False,FullRegExp=False):
  """Return a list of file or folder paths using Python os.walk function
  
  This function is used by the Lister script tool in the EGIS toolbox.
  """
  import os, re
  lstOut = []
  if not FullRegExp:
    # convert simple regexp to full regexp
    strWild0 = strWild
    strWild = strWild.replace(r".",r"\.")
    strWild = strWild.replace(r"*",r".*")
    strWild += r"$"
  GPMsg("Matching regular expression: \"%s\" ..." % strWild)
  regMatch = re.compile(strWild,re.IGNORECASE)
  try:
    for root, dirs, files in os.walk(inDir):
      if FoldersOnly:
        for strFolderName in dirs:
          # find a match?
          if regMatch.match(strFolderName):
            lstOut.append(os.path.join(root,strFolderName))
      else:   
        # look for files
        for strDirName in dirs:
          for strFileName in files:
            # find a match?
            if regMatch.match(strFileName) != None:
              lstOut.append(\
                os.path.join(root,strDirName,strFileName))
    return lstOut
  except Exception, ErrorDesc:
      raise Exception, "File search failed for \"%s\"\n" % strWild + str(ErrorDesc) 


def SysCommands(gp,CommandString,RunFolder):
  """Runs a command shell
  
  This tool pushes tty input and prints output as GP Messages.
  
  arguments
  
  gp - geoprocessor object
  
  CommandString - text string of tty to feed to command process
  
  RunFolder - Folder in which to start up command process

  example
  
   import arcgisscripting, egis
   gp = arcgisscripting.create()
   Sev = egis.SysCommands(gp, "dir","e:/work")   
      
  (Note: stderr is captured as GP error messages [cool, huh?])
  """
  try:
    import os
    # Command string
    if CommandString == "#"  or CommandString == "":
      raise MsgError, "No command provided" 

    # does the workspace folder exist?
    if RunFolder == "#" or RunFolder == "": 
      RunFolder = os.environ["TEMP"]
    if not gp.Exists(RunFolder):
      raise MsgError, "Workspace \"%s\" does not exist" % RunFolder
    if not os.path.isdir(RunFolder) and \
       os.path.splitext(RunFolder)[1].lower != ".gdb":
      RunFolder = os.environ["TEMP"]

    # Submit the command to the shell
    lstCmd = CommandString.split("\n")
        
    if len(lstCmd) > 1:
        # prepend multi line commands with a cmd /c
        lstCmd = ['cmd /c'] + lstCmd
    else:
      # Single commands are run with no dialog, so inform user
      GPMsg("","%s> %s" % (RunFolder,CommandString))

    # Go to folder, start shell
    strHere = os.path.realpath(os.curdir) # save it
    os.chdir(RunFolder)
    fi,fo,fe = os.popen3(lstCmd[0],'t')

    # for multi-line command session, send each command one at a time
    if len(lstCmd) > 1:
        for Cmd in lstCmd[1:]:
            fi.write(Cmd + "\n")
        # add command to close the shell
        fi.write("exit\n")
    
    # Read the session dialog and pass it along to the GP.
    # The data are not blocked so they will be reported
    # as they come back to the GP message stream. 
    strMsg = fo.readline()
    Sev = 0 # no errors so far!
    # read std output
    while strMsg != "":
      GPMsg("",strMsg.strip())
      strMsg = fo.readline() # Get next line of output

    # check for std error messages
    strErr = fe.readline()
    if strErr != "": Sev = 2 # we have an error of some kind
    while strErr != "":
      GPMsg("E",strErr.strip())
      strErr = fe.readline() # Get next line of error
        
    # clean up
    fi.close()
    fo.close()
    fe.close()    
    del fi,fo,fe
    os.chdir(strHere)
    return Sev
   
  except Exception, ErrorDesc:
    # Return error messages
    GPMsg("e",str(ErrorDesc))

    try:
      os.chdir(strHere)  # go back to this folder once shell started
    except:
      pass
    # return error severity, in case there is any doubt
    return 2

def ArcCommands(gp,commandString, ArcWorkspace="", strEcho="off"):
  """Run an ArcInfo Workstation session
  
  arguments
   
  commandString
     Set of arcinfo workstation commands
  ArcWorkspace
     Folder to start session 
     (default: current workspace)
  strEcho
     &echo setting "off" (default), "on", or "brief"
    
  example
  
   sev = ArcCommands(gp,
     "clean mycov # # # 1.0;labelerrors mycov",r"e:\work")
      
  notes
  
  Take care that the dialog specified in commandString avoids stopping
  the session inside a dialog - if so, the only way to kill the workstation
  session is by killing the arc.exe process.
  
  The current geoprocessing environment coverage settings are used.
       
  """
  import os, sys
  
  try:
    # Is Workstation even installed?
    ARCHOME = os.environ["ARCHOME"]
    if not os.path.exists(ARCHOME + "/bin/arc.exe"):
      raise MsgError, "ArcInfo Workstation is not installed"
    
    gp = getGP()

    # Command string
    if commandString == "#" or commandString.strip() == "":
      raise MsgError, "No command provided" 
        
    # check command lines for long length (ArcInfo limit)
    lstCommands = commandString.split("\n")
    k = 0
    for strCmd in lstCommands:
      if len(strCmd) > 320:
        strMsg = "Input line " + str(k) + \
               " too long (" + str(len(strCmd)) + "/320 max)\n\n" + \
             strCmd + "\n\n" 
        raise MsgError, strMsg
      k += 1
    
    # Workspace - MUST BE A FOLDER
    if ArcWorkspace == "": ArcWorkspace = gp.Workspace 
  
    # does the workspace folder exist?
    if not gp.Exists(ArcWorkspace): 
      raise MsgError, "Workspace \"%s\" not found" % ArcWorkspace 
    if gp.Describe(ArcWorkspace).DataType != "Folder":
      raise MsgError, "Workspace must be a filesystem folder (not a geodatabase)"
  
    if ArcWorkspace.find(" ") >= 0: 
      GPMsg("w","Spaces are not recommended in the Arc Workspace path")
    
    # ArcInfo Workstation &echo
    strEcho = strEcho.upper()
    if strEcho.find("OFF")>-1: strEcho = "off"
    elif strEcho.find("BRI")>-1: strEcho = "brief"
    elif strEcho.find("ON")>-1: strEcho = "on"
    else: strEcho = "off"
    
    # GP Coverage setting defaults
    if not gp.NewPrecision: gp.NewPrecision = "DOUBLE"   
    if not gp.DerivedPrecision: gp.DerivedPrecision = "HIGHEST"
    if not gp.ProjectCompare: gp.ProjectCompare = "NONE"   
    strGPEnv = "precision %s %s;projectcompare %s" % \
      (gp.NewPrecision.lower(), gp.DerivedPrecision.lower(),\
       gp.ProjectCompare.lower())
       

    # Go to folder
    strHere = os.path.realpath(os.curdir)
    os.chdir(ArcWorkspace) # run arc shell from this workspace
  
    # command to start ArcInfo Workstation shell
    ArcCmd = os.path.realpath(ARCHOME + "/bin/arc.exe")  + "\n"
     
    # Start an interactive ArcInfo session and feed it the command line
    # we need the 'b' argument to properly get the newlines
    fi,fo,fe = os.popen3(ArcCmd)
      
    # Send interactive commands to the Arc prompt
  
    # set up session
    # Geoprocessing Coverage settings
    strCommand = strGPEnv + "\n"
    # ignore errors (we will trap them below)
    strCommand += "&severity &warning &ignore;&severity &error &ignore"
    # set &echo environment if the user asked for it
    if strEcho != "off":
      strCommand += ";&echo &" + strEcho.lower() 
    fi.write("%s\n" % strCommand) 

    # Send the command the user asked for
    fi.write("%s\n" % commandString) 
    
    # report severity in a message so we can capture the error status
    # and pass it along to the geoprocessor later
    fi.write("&type ***AML Severity: %aml$sev%, " +\
             "%aml$message%\n")
    
    # Send the "quit" command to end the session, but with
    # some insurance... stack in extra newlines and quit commands
    # just in case so we do our best to end the shell
    fi.write("quit\nquit\n" + "\n" * 10 + "quit\nquit\n") 
       
  
    # We've sent all we can send to the arc process...
    
    # Now, read the session dialog and pass it along to the GP.
    # The data are not blocked so they will be reported
    # as it happens to the GP message stream.
  
    strMsg = str(fo.readline())
    
    # print version startup lines and brief license notice
    for line in range(3):
      GPMsg(strMsg.strip())
      strMsg = fo.readline()
    # skip startup verbiage until arc prompt
    while not strMsg.startswith("Arc:"):
      strMsg = fo.readline()    
      
    # initialize maxSeverity found
    maxSeverity = 0

    # parse output
    
    while strMsg != "":
      # strip newlines
      strMsg = strMsg.strip()
  
      # Check output, and echo results
      Severity = ArcMsgSeverity(strMsg)

      # replace double \\ with \n: 
      strMsg = strMsg.replace(r"\\","\n: ")
      
      # modify severity report string
      if strMsg.find("***AML") > -1: 
        strMsg = strMsg.replace("***AML Severity: 1, ","")
        strMsg = strMsg.replace("***AML Severity: 2, ","")
      if Severity == 0:
        pass # in the skip list 
      elif Severity == 1:
        GPMsg("w",strMsg)
      elif Severity == 2:
        GPMsg("e",strMsg)
      else: # ok to print
        GPMsg("",strMsg)
      
      # record max severity code encountered
      maxSeverity = max(maxSeverity,Severity)
        
      strMsg = fo.readline() # Get next ArcInfo session message
     

    # check for std error messages
    strErr = fe.readline()
    if strErr != "": maxSeverity = 2 # we have a system error 
    while strErr != "":
      GPMsg("E",strErr[:-1])
      strErr = fe.readline() # Get next line of error

      # clean up
    fi.close()
    fo.close()
    del fi, fo, fe
    os.chdir(strHere)  # go back to this folder once shell started
    
    return maxSeverity
  except MsgError, xmsg:
    # this is an error to pass on to the user
    raise MsgError, str(xmsg) 
  except arcgisscripting.ExecuteAbort, xmsg:
    # user hit cancel button
    GPMsg("error",str(xmsg) + \
      "\nYou may have to manually kill the process \"arc.exe\" from Windows Task Manager.")
  except Exception:
    # this function failed! report results
    line,file,err = TraceInfo()
    raise "Error","Python error on %s of %s:\n%s" % (line,file,err)
  finally:
    try:
      os.chdir(strHere)  # go back to this folder once shell started
    except:
      pass

def ArcMsgSeverity(strMessage):
  """Scans a string for ArcInfo messages, returning a severity code
  """
  # this routine checks input/output messages from the arcinfo session
  # dialog for strings that tell us error messages. This function
  # returns a severity code:
  #  0 = no warning or error
  #  1 = this is a warning
  #  2 = this is an error
  #  -1 = no matches found 
  
  # input/output strings to skip make the output cleaner
  SkipList = ["Arc: &severity &warning &ignore;&severity &error &ignore",
              "&type ***AML Severity:",
              "***AML Severity: 0",
             2*chr(8)+chr(20)+2*chr(8),]
  # Warning and Error strings
  # "FATAL" and "Submitting command to operating system" message are flagged
  # to generate warning and errors (in AML they don't)
  WarnList = [
             "Submitting command to Operating System",
             "***AML Severity: 1,",
             "AML WARNING"
             ]
  ErrList = [
            "FATAL", 
            "***AML Severity: 2,",
            "AML ERROR"
            ]

  Sev = 0
  for List in (SkipList, WarnList, ErrList):
    for strMsg in List:
      if strMessage.find(strMsg) >= 0: 
        return Sev 
    Sev = Sev + 1
  return -1  #  no matches found, return -1


def ForwardPath(strFullPath):
  """Convert a DOS path to a UNIX (forward-slash) delimited path
  
  arguments
  
    strFullPath - A full pathname

  example
  
    >>> egis.ForwardPath("e:\work\\..\work\\xg")
    'e:/work/xg'

  See the ArcGIS help for a discussion of paths in ArcGIS:
  http://qurl.com/nr5kt"""
  import os
  try:
    # convert to forward slashes (elegant, like Unix and Python!)
    return os.path.normpath(strFullPath).replace(os.sep,"/")
  except:
    raise Exception, "Could not fix path \"%s\"" % strPath
  

TEMPLATE = """
#############################################################################
###           example script tool using egis python module                ###
#############################################################################
 
\"""   GP Script Tool - Template.py
\"""
# template script for a GP script tool;
# shows how to use the egis module to trap errors,
# manage messages, and handle scratch files
#
# One-line description of script goes here
# 
# Clarence King, cking@usgs.gov, 1879-03-03, original coding
# Curtis Price, cprice@usgs.gov, 2009-10-06 bug fixes

# module imports

# commonly used standard modules
import sys, os
# EGIS helper module
import egis
from egis import GPMsg, MsgError
# Geoprocessing error exception
from arcgisscripting import ExecuteError as GPError 

# set up geoprocessor, with spatial analyst license

# A. for 9.3, 9.3.1; but supported in 10.0:
gp = egis.getGP(9.3,"spatial")  

# B. for 10.0 *only*:
# import arcpy
# arcpy.CheckOutExtension("spatial") # spatial license
# from arcpy.sa import *  # Python map algebra

try: 

  # set up GPMsg messaging. If this line is omitted, default is "gp"
  # (ArcGIS only, no python-print)
  # You can change the message mode either directly:
  egis.GPMode("both") 
  # or by specifying it in the GPMsg function
  GPMsg("w","Hello World","print")
  
  # <get arguments from the command line here>
  # arg1 = sys.argv[1] ...
  # arg1 = gp.GetParameterAsText(0)... 
      
  # egis.ScratchName method to get valid scratch names
  tmpGrid = egis.ScratchName("","","grid")

  # Three different kinds of errors 
  # (uncomment ## lines one at a time to see how they get handled)
  
  # 1. Script-raised error - send a message to user
  ##raise MsgError, "You have issues"
  # 2. runtime Python error, divide by zero
  ##3 / 0
  # 3. ESRI Geoprocessing error (grid doesn't exist)
  ##Result = gp.GetCount(tmpGrid)
  
  GPMsg("If this you see this, there were no errors!")
  GPMsg("w","This is warning, just to keep you on your toes.")
  GPMsg("w","ID 345") # print a random warning using an ArcGIS error code
  GPMsg("t","Now is the time for all good persons...")

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
"""

