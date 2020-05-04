import sys
sys.path.append("..") # change environment to see tools
from databaseSetup import check_walls

dendrite = r"" # path to the flowline dendrite
inwall = r"" # path to the inner wall feature class
points = r"" # path to the intersection points to output
outwall = r"" # path to the outer wall feature class (optional) 

check_walls(dendrite, inwall, points, outwall = outwall)