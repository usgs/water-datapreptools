import arcpy

class Toolbox(object):
    def __init__(self):
        """Toolbox for preprocessing data for creating or refreshing a StreamStats project."""
        self.label = "Setup Tools"
        self.alias = "SetupTools"

        # List of tool classes associated with this toolbox
        self.tools = [setup]

class makeELEVDATAIndex(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "2.A Make ELEVDATA Index"
        self.description = "Function to make ELEVDATA into a raster catalog for clipping to the basin polygons."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName = "Output Geodatabase",
            name = "OutLoc",
            datatype = "DEWorkspace",
            parameterType = "Required",
            direction = "Input")

        param1 = arcpy.Parameter(
            displayName = "Output Raster Catalog Name",
            name = "rcName",
            datatype = "GPString",
            parameterType = "Required",
            direction = "Input") 

        params = [param0,param1]
        return params

    def execute(self, parameters, messages):
        """The source code of the tool."""

    return