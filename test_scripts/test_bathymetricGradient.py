import sys
sys.path.append("..")
from make_hydrodem import bathymetricGradient

huc = "01080201"
print("************ Testing bathymetricGradient on unit: %s ************"%huc)

workspace = r"C:\Users\tbarnhart\projects\datapreptools\data\test_workspace\%s\input_data.gdb"%huc
snapGrid = r"C:\Users\tbarnhart\projects\datapreptools\data\test_workspace\%s\Layers\dem"%huc
hucPoly = "huc8"
hydrographyArea = "NHDArea" 
hydrographyFlowline = "NHDFlowline"
hydrographyWaterbody = "NHDWaterbody"
cellsize = '10'

bathymetricGradient(workspace, snapGrid, hucPoly, hydrographyArea, hydrographyFlowline, hydrographyWaterbody,cellsize)