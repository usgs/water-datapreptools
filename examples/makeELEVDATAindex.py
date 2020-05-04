import sys
sys.path.append("..") # change environment to see tools
from elevationTools import elevIndex

OutLoc = r"" # geodatabase output location
rcName = "IndexRMD" # output raster mosaic dataset name
coordsysRaster = 'GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137,298.257222101]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]]' # projection of rasters to be mosaic, here in ESRI WKT.
InputELEVDATAws = r"" # file workspace containing DEM tiles to mosaic
OutFC = "ELEVDATIndexPolys" # output feature class showing tile extents

elevIndex(OutLoc, rcName, coordsysRaster, InputELEVDATAws)