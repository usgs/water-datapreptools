import sys
sys.path.append("..")
from make_hydrodem import adjust_accum

print("************ Testing adjust_accum ************")

facPth = "hydrodemfac"
fdrPth = "hydrodemfdr"
upstreamFACpths = [r"C:\Users\tbarnhart\projects\datapreptools\data\test_workspace\01080207\input_data.gdb\hydrodemfac",
					r"C:\Users\tbarnhart\projects\datapreptools\data\comparison\01080206_v4\input_data.gdb\hydrodemfac"]
upstreamFDRpths = [r"C:\Users\tbarnhart\projects\datapreptools\data\test_workspace\01080207\input_data.gdb\hydrodemfdr",
					r"C:\Users\tbarnhart\projects\datapreptools\data\comparison\01080206_v4\input_data.gdb\hydrodemfdr"]
workspace = r"C:\Users\tbarnhart\projects\datapreptools\data\test_workspace\01080205\input_data.gdb"
#scratch = r"C:\Users\tbarnhart\projects\datapreptools\data\test_workspace\01080205\tmp"

adjust_accum(facPth, fdrPth, upstreamFACpths,upstreamFDRpths, workspace)