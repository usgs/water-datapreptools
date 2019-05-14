from make_hydrodem import bathymetricGradient

print("************ Testing bathymetricGradient ************")

workspace = r"C:\Users\tbarnhart\projects\datapreptools\data\test_workspace\01080207\input_data.gdb"
snapGrid = r"C:\Users\tbarnhart\projects\datapreptools\data\test_workspace\01080207\Layers\dem"
hucPoly = "huc8"
hydrographyArea = "NHDArea" 
hydrographyFlowline = "NHDFlowline"
hydrographyWaterbody = "NHDWaterbody"
cellsize = '10'

bathymetricGradient(workspace, snapGrid, hucPoly, hydrographyArea, hydrographyFlowline, hydrographyWaterbody,cellsize)