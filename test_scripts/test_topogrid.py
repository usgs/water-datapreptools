import sys
sys.path.append("..")
from topo_grid import topogrid

huc = "0203010502"
print("************ Testing TopoGrid on unit: %s ************"%huc)

workspace = r"C:\Users\tbarnhart\projects\datapreptools\data\psteeves\%s\input_data.gdb"%(huc)
huc8 = "huc8"
buffdist = "50"
dendrite = "NHDFlowline"
dem = r"C:\Users\tbarnhart\projects\datapreptools\data\psteeves\%s\dem_buff2000"%(huc)
cellSize = "10"
vipPer = "5"

topogrid(workspace,huc8,buffdist,dendrite,dem,cellSize,vipPer)