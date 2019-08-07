import sys
sys.path.append("..")
from make_hydrodem import postHydroDEM

huc = "0203010502"
print("************ Testing postHydroDEM on unit: %s ************"%huc)

workspace = r"C:\Users\tbarnhart\projects\datapreptools\data\psteeves\%s\input_data.gdb"%(huc)
facPth = r"C:\Users\tbarnhart\projects\datapreptools\data\psteeves\%s\input_data.gdb\hydrodemfac"%(huc)
fdrPth = r"C:\Users\tbarnhart\projects\datapreptools\data\psteeves\%s\input_data.gdb\hydrodemfdr"%(huc)
thresh1 = 1350000
thresh2 = 72900
sinksPth = None

postHydroDEM(workspace, facPth, fdrPth, thresh1, thresh2, sinksPth = None)