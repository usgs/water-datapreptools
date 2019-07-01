import sys
sys.path.append("..")
from make_hydrodem import hydrodem

huc = "0203010501"
print("************ Testing HydroDEM on unit: %s ************"%huc)

outdir = r"C:\Users\tbarnhart\projects\datapreptools\data\psteeves\%s\input_data.gdb"%(huc)
huc8cov = "huc8"
origdem = r"C:\Users\tbarnhart\projects\datapreptools\data\psteeves\%s\dem_buff2000"%(huc)
dendrite = "NHDFlowline"
snap_grid = r"C:\Users\tbarnhart\projects\datapreptools\data\psteeves\%s\snap_grid"%(huc)
bowl_polys = "nhd_wbg"
bowl_lines = "wb_srcg"
inwall = "inwall_edit"
#drainplug = "sinkpoint_edit"
drainplug = None
buffdist = 50
inwallbuffdist = 15 
inwallht = 150000
outwallht = 300000
agreebuf = 60
agreesmooth = -500
agreesharp = -50000
bowldepth = 2000
cellsz = 10
scratchWorkspace = r"C:\Users\tbarnhart\projects\datapreptools\data\psteeves\%s\tmp"%(huc)
version = None

hydrodem(outdir, huc8cov, origdem, dendrite, snap_grid, bowl_polys, bowl_lines, inwall, drainplug, buffdist, inwallbuffdist, inwallht, outwallht, agreebuf, agreesmooth, agreesharp, bowldepth, cellsz, scratchWorkspace, version = version)