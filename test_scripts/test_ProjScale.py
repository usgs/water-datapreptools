import sys
sys.path.append("..")
from elevationTools import projScale

huc = "01080201"
print("************ Testing projScale on unit: %s************"%huc)

Input_Workspace = r"C:\Users\tbarnhart\projects\datapreptools\data\test_workspace\%s\Layers"%huc 
InGrd = "dem_dd"
OutGrd = "dem"
OutCoordsys = r"C:\Users\tbarnhart\projects\datapreptools\data\test_data\test_WBD.shp" # not sure if this will work
OutCellSize = 10
RegistrationPoint = "0 0"

projScale(Input_Workspace, InGrd, OutGrd, OutCoordsys, OutCellSize, RegistrationPoint)