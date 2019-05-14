from elevationTools import projScale

print("************ Testing projScale ************")

Input_Workspace = r"C:\Users\tbarnhart\projects\datapreptools\data\test_workspace\01080207\Layers" 
InGrd = "dem_fill"
OutGrd = "dem"
OutCoordsys = r"C:\Users\tbarnhart\projects\datapreptools\data\test_data\test_WBD.shp" # not sure if this will work
OutCellSize = 10
RegistrationPoint = "0 0"

projScale(Input_Workspace, InGrd, OutGrd, OutCoordsys, OutCellSize, RegistrationPoint)