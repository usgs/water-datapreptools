import sys
sys.path.append("..")
from databaseSetup import check_walls

huc = "01080203"
print("************ Testing check_wall on unit: %s ************"%huc)

dendrite = r"C:\Users\tbarnhart\projects\datapreptools\data\test_workspace\%s\input_data.gdb\NHDFlowline"%huc
inwall = r"C:\Users\tbarnhart\projects\datapreptools\data\test_workspace\%s\input_data.gdb\inwall_edit"%huc
points = r"C:\Users\tbarnhart\projects\datapreptools\data\test_workspace\%s\input_data.gdb\check_walls"%huc
outwall = r"C:\Users\tbarnhart\projects\datapreptools\data\test_workspace\%s\input_data.gdb\local"%huc

print('Testing without outwall')
check_walls(dendrite, inwall, points)
print('')
print('Testing with outwall')
check_walls(dendrite, inwall, points, outwall = outwall)