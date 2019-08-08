import sys
sys.path.append("..")
from elevationTools import elevIndex

print("************ Testing elevIndex ************")

OutLoc = r"C:\Users\tbarnhart\projects\datapreptools\data\test_workspace\test_global.gdb"
rcName = "IndexRMD"
coordsysRaster = 'GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137,298.257222101]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]]'
InputELEVDATAws = r"C:\Users\tbarnhart\projects\datapreptools\data\test_data\ELEVDATA"
OutFC = "ELEVDATIndexPolys"
version = None

elevIndex(OutLoc, rcName, coordsysRaster, InputELEVDATAws, OutFC, version = version)