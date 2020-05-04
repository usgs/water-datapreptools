import sys
sys.path.append("..") # change environment to see tools
from make_hydrodem import postHydroDEM

workspace = r"" # geodatabase type workspace
facPth = r"" # path to flow accumulation grid
fdrPth = r"" # path to flow direction grid
thresh1 = 1350000 # stream threshold 1
thresh2 = 72900 # stream threshold 2
sinksPth = None # path to sinks (optional)

postHydroDEM(workspace, facPth, fdrPth, thresh1, thresh2, sinksPth = None)