import sys
sys.path.append("..")
from elevationTools import checkNoData

huc = "01080203"
print("************ Testing checkNoData on unit: %s ************"%huc)

InGrid = r"C:\Users\tbarnhart\projects\datapreptools\data\test_workspace\%s\Layers\dem_dd"%huc
tmpLoc = r"C:\Users\tbarnhart\projects\datapreptools\data\test_workspace\%s\input_data.gdb"%huc
OutPolys_shp = "DEMsinks"

checkNoData(InGrid, tmpLoc, OutPolys_shp)