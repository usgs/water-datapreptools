from elevationTools import elevIndex

print("************ Testing elevIndex ************")

OutLoc = r"C:\Users\tbarnhart\projects\datapreptools\data\test_workspace\test_global.gdb"
rcName = "IndexRC"
coordsysRaster = "NAD83_Conus_Albers"
InputELEVDATAws = r"C:\Users\tbarnhart\projects\datapreptools\data\test_data\ELEVDATA"
OutFC = "ELEVDATIndexPolys"
version = None

elevIndex(OutLoc, rcName, coordsysRaster, InputELEVDATAws, OutFC, version)