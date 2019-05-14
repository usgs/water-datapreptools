from elevationTools import fillNoData

print("************ Testing fillNoData ************")

workspace = InGrid = r"C:\Users\tbarnhart\projects\datapreptools\data\test_workspace\01080207\Layers"
InGrid = "dem_dd"
OutGrid = "dem_fill"

fillNoData(workspace, InGrid, OutGrid)