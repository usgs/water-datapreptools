from elevationTools import checkNoData

print("************ Testing checkNoData ************")

InGrid = r"C:\Users\tbarnhart\projects\datapreptools\data\test_workspace\01080207\Layers\dem_dd"
tmpLoc = r"C:\Users\tbarnhart\projects\datapreptools\data\test_workspace\01080207\input_data.gdb"
OutPolys_shp = "DEMsinks"

checkNoData(InGrid, tmpLoc, OutPolys_shp)