import sys
sys.path.append("..") # change environment to see tools
from topo_grid import topogrid

workspace = r""%(huc) # path to geodatabase type workspace
huc8 = "huc8" # outerwall feature class name
buffdist = "50" # buffer distance
dendrite = "NHDFlowline" # dendrite feature class name
dem = r""%(huc) # path to projected and buffered DEM to re-process
cellSize = "10" # output cell size
vipPer = "5" # threshould of points to keep based on VIP score.
snapgrid = r"" # path to snap grid

topogrid(workspace,huc8,buffdist,dendrite,dem,cellSize,vipPer, snapgrid = snapgrid)