import sys
sys.path.append("..")
from make_hydrodem import adjust_accum

print("************ Testing adjust_accum ************")

facPth = "hydrodemfac"
fdrPth = "hydrodemfdr"
upstreamFACpths = [r"C:\Users\tbarnhart\projects\datapreptools\data\test_workspace\01080205\input_data.gdb\hydrodemfac"]
upstreamFDRpths = [r"C:\Users\tbarnhart\projects\datapreptools\data\test_workspace\01080205\input_data.gdb\hydrodemfdr"]
workspace = r"C:\Users\tbarnhart\projects\datapreptools\data\test_workspace\01080205\input_data.gdb"

adjust_accum(facPth, fdrPth, upstreamFACpths,upstreamFDRpths, workspace):