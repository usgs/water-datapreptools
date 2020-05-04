import sys
sys.path.append("..") # change environment to see tools
from make_hydrodem import bathymetricGradient

workspace = r"" # path to geodatabase to use as a workspace
snapGrid = r"" # path to snapping grid
hucPoly = r"" # path to local folder polygon
hydrographyArea = r""  # path to NHD area feature class
hydrographyFlowline = r"" # path to NHD flowline feature class
hydrographyWaterbody = r"" # path to NHD water body feature class
cellsize = '' # cell size

bathymetricGradient(workspace, snapGrid, hucPoly, hydrographyArea,
	hydrographyFlowline, hydrographyWaterbody,cellsize)