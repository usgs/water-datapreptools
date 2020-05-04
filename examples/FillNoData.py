import sys
sys.path.append("..") # change environment to see tools
from elevationTools import fillNoData

workspace = r"" # file type workspace
InGrid = "dem_dd" # name of grid to be filled
OutGrid = "dem_fill" # name of output grid

fillNoData(workspace, InGrid, OutGrid)