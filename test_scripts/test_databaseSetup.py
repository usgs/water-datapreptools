from databaseSetup import databaseSetup

print("************ Testing databaseSetup ************")

output_workspace = r"C:\Users\tbarnhart\projects\datapreptools\data\test_workspace"
output_gdb_name = "test_global"
hu_dataset = r"C:\Users\tbarnhart\projects\datapreptools\data\test_data\test_WBD.shp"
hu8_field = "HUC8"
hu12_field = "HUC12"
hucbuffer = 2000
nhd_path = r"C:\Users\tbarnhart\projects\datapreptools\data\test_data\ELEVDATA"
elevation_projection_template = r"C:\Users\tbarnhart\projects\datapreptools\data\test_data\ELEVDATA\grdn44w074_13"
alt_buff = 50

databaseSetup(output_workspace, output_gdb_name, hu_dataset, hu8_field, hu12_field, hucbuffer, nhd_path,elevation_projection_template,alt_buff)