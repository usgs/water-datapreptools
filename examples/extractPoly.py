import sys
sys.path.append("..") # change environment to see tools
from elevationTools import extractPoly

Input_Workspace = r"" # path to file type workspace
nedindx = r"" # path to DEM index raster mosaic dataset
clpfeat = r"" # path to buffered and reprojected local folder clipping feature.
OutGrd = "dem_dd" # name of grid to be output

extractPoly(Input_Workspace, nedindx, clpfeat, OutGrd)