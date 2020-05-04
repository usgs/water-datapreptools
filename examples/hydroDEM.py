import sys
sys.path.append("..") # change environment to see tools
from make_hydrodem import hydrodem

outdir = r"" # path to geodatabase type workspace
huc8cov = "huc8" # name of local folder feature class
origdem = r"" # path to DEM to be enforced
dendrite = "NHDFlowline" # name of flowline dendrite to use
snap_grid = r"" # path to snap grid
bowl_polys = "nhd_wbg"
bowl_lines = "wb_srcg"
inwall = "inwall_edit"
#drainplug = "sinkpoint_edit"
drainplug = None # path to drainplug feature class
buffdist = 50 # outer wall buffer distance
inwallbuffdist = 15 # inner wall buffer distance
inwallht = 150000 # inner wall height
outwallht = 300000 # outer wall height
agreebuf = 60 # agree routine buffer
agreesmooth = -500 # agree routine smooth drop
agreesharp = -50000 # agree routine sharp drop
bowldepth = 2000 # bowling depth
cellsz = 10 # cell size
scratchWorkspace = r"" # path to scratch workspace

hydrodem(outdir, huc8cov, origdem, dendrite, snap_grid, bowl_polys, bowl_lines, inwall, drainplug, buffdist, inwallbuffdist, inwallht, outwallht, agreebuf, agreesmooth, agreesharp, bowldepth, cellsz, scratchWorkspace)