import sys
sys.path.append("..")
from elevationTools import extractPoly

huc = "01080203"
print("************ Testing extractPoly on unit: %s************"%huc)

Input_Workspace = r"C:\Users\tbarnhart\projects\datapreptools\data\test_workspace\%s\Layers"%huc
nedindx = r"C:\Users\tbarnhart\projects\datapreptools\data\test_workspace\test_global.gdb\NEDIndexPolys"
clpfeat = r"C:\Users\tbarnhart\projects\datapreptools\data\test_workspace\%s\input_data.gdb\huc8_buffer2000_dd83"%huc
OutGrd = "dem_dd"

extractPoly(Input_Workspace, nedindx, clpfeat, OutGrd)