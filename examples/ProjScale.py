import sys
sys.path.append("..") # change environment to see tools
from elevationTools import projScale

Input_Workspace = r""%huc # folder type workspace
InGrd = "dem_dd"
OutGrd = "dem"
OutCoordsys = r"" # path to feature class from which to pull the output projection
OutCellSize = 10 # output cell size
RegistrationPoint = "0 0" # output registration point for raster alignment

projScale(Input_Workspace, InGrd, OutGrd, OutCoordsys, OutCellSize, RegistrationPoint)