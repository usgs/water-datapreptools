import sys
sys.path.append("..") # change environment to see tools
from elevationTools import checkNoData

InGrid = r"" # path to the digital elevation model to check
tmpLoc = r"" # path a geodatabase workspace
OutPolys_shp = "" # name of the output feature class

checkNoData(InGrid, tmpLoc, OutPolys_shp)