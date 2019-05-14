from elevationTools import extractPoly

print("************ Testing extractPoly ************")

Input_Workspace = r"C:\Users\tbarnhart\projects\datapreptools\data\test_workspace\01080207\Layers"
nedindx = r"C:\Users\tbarnhart\projects\datapreptools\data\test_workspace\test_global.gdb\ELEVDATIndexPolys"
clpfeat = r"C:\Users\tbarnhart\projects\datapreptools\data\test_workspace\01080207\input_data.gdb\huc8_buffer2000_dd83"
OutGrd = "dem_dd"

extractPoly(Input_Workspace, nedindx, clpfeat, OutGrd)