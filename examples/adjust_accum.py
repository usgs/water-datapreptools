import sys
sys.path.append("..") # change environment to see tools
from make_hydrodem import adjust_accum

facPth = "" # path to downstream flow accumulation grid
fdrPth = "" # path to downstream flow direction grid
upstreamFACpths = [r"", r""] # list of paths to upstream flow accumulation grids.
upstreamFDRpths = [r"", r""] # list paths to upstream flow direction grids, must be in the same order as the flow accumulation grids.
workspace = r"" # path to geodatabase workspace.

adjust_accum(facPth, fdrPth, upstreamFACpths,upstreamFDRpths, workspace)