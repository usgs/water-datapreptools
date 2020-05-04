import sys
sys.path.append("..") # change environment to see tools
from databaseSetup import databaseSetup

output_workspace = r"" # path to file type workspace
output_gdb_name = "" # name for global gdb to be created
hu_dataset = r"" # path to local folder features
hu8_field = "" # field that identifies local folders / outer walls
hu12_field = "" # field that identifies inner walls
hucbuffer =  # buffer distance for local folders
nhd_path = r"" # path to folder containing NHD hydrography.
elevation_projection_template = r"" # path to a digital elevation model from which to pull a projection.
alt_buff =  # alternate buffer distance.

databaseSetup(output_workspace, output_gdb_name, hu_dataset, hu8_field, hu12_field, hucbuffer, nhd_path,elevation_projection_template,alt_buff)