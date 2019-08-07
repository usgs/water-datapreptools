import sys
sys.path.append("..")
from elevationTools import projScale

huc = "01080203"
print("************ Testing projScale on unit: %s************"%huc)

Input_Workspace = r"C:\Users\tbarnhart\projects\datapreptools\data\psteeves\%s\Layers"%huc 
InGrd = "dem_dd"
OutGrd = "dem"
OutCoordsys = r"C:\Users\tbarnhart\projects\datapreptools\data\psteeves\%s\input_data.gdb\huc8" # not sure if this will work
OutCellSize = 10
RegistrationPoint = "0 0"
scaleFact = 1000

projScale(Input_Workspace, InGrd, OutGrd, OutCoordsys, OutCellSize, RegistrationPoint, scaleFact = scaleFact)