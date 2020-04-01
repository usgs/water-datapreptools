import sys
sys.path.append("..")
from make_hydrodem import adjust_accum_simple

print("************ Testing adjust_accum_simple ************")

ptin = r"C:\Users\tbarnhart\projects\datapreptools\data\psteeves\0203010501\input_data.gdb\inlet"
fdrin = r"C:\Users\tbarnhart\projects\datapreptools\data\psteeves\0203010501\input_data.gdb\hydrodemfdr"
facin = r"C:\Users\tbarnhart\projects\datapreptools\data\psteeves\0203010501\input_data.gdb\hydrodemfac"
filin = r"C:\Users\tbarnhart\projects\datapreptools\data\psteeves\0203010501\input_data.gdb\hydrodem"
facout = r"C:\Users\tbarnhart\projects\datapreptools\data\psteeves\0203010501\input_data.gdb\hydrodemfac_global"
incrval = 150000

adjust_accum_simple(ptin, fdrin, facin, filin, facout, incrval)