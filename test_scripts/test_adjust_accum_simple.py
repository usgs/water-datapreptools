import sys
sys.path.append("..")
from make_hydrodem import adjust_accum_simple

print("************ Testing adjust_accum_simple ************")

ptin = r"C:\Users\tbarnhart\projects\datapreptools\data\test_workspace\01080207\input_data.gdb\upstreamPT"
fdrin = r"C:\Users\tbarnhart\projects\datapreptools\data\test_workspace\01080205\input_data.gdb\hydrodemfdr"
facin = r"C:\Users\tbarnhart\projects\datapreptools\data\test_workspace\01080205\input_data.gdb\hydrodemfac"
filin = r"C:\Users\tbarnhart\projects\datapreptools\data\test_workspace\01080205\input_data.gdb\hydrodem"
facout = "hydrodem_global"
incrval = 150000

adjust_accum_simple(ptin, facin, filin, facout, incrval)