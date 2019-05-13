from make_hydrodem import hydrodem

print("************ Testing HydroDEM ************")

outdir = r"C:\Users\tbarnhart\projects\datapreptools\data\test_workspace\01080207\input_data.gdb"
huc8cov = "huc8"
origdem = r"C:\Users\tbarnhart\projects\datapreptools\data\test_workspace\01080207\Layers\dem"
dendrite = "NHDFlowline"
snap_grid = r"C:\Users\tbarnhart\projects\datapreptools\data\test_workspace\01080207\Layers\dem"
bowl_polys = "nhd_wbg"
bowl_lines = "wb_srcg"
inwall = "inwall_edit"
drainplug = "sinkpoint_edit"
start_path = None # not sure this is needed...
buffdist = 50
inwallbuffdist = 15 
inwallht = 150000
outwallht = 300000
agreebuf = 60
agreesmooth = -500
agreesharp = -50000
bowldepth = 2000
copylayers = None # likely not needed...
cellsz = 10
bowling = None # not sure these are needed
in_wall = None
drain_plugs = None

hydrodem(outdir, huc8cov, origdem, dendrite, snap_grid, bowl_polys, bowl_lines, inwall, drainplug, start_path, buffdist, inwallbuffdist, inwallht, outwallht, agreebuf, agreesmooth, agreesharp, bowldepth, copylayers, cellsz, bowling, in_wall, drain_plugs)