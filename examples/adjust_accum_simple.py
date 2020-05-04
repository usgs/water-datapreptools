import sys
sys.path.append("..") # change environment to see tools
from make_hydrodem import adjust_accum_simple

ptin = r"" # path to the downstream inlet shapefile
fdrin = r"" # path to the downstream flow direction grid
facin = r"" # path to the downstream flow accumulation grid
filin = r"" # path to downstream hydro-enforced DEM
facout = r"" # path to ouput the downstream corrected flow accumulation grid.
incrval = # value to correct the downstream grid with.

adjust_accum_simple(ptin, fdrin, facin, filin, facout, incrval)