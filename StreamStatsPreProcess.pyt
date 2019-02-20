import arcpy

class StreamStatsDataPreProc(object):
    def __init__(self):
        """Toolbox for preprocessing data for creating or refreshing a StreamStats project."""
        self.label = "StreamStatsDataPreProc"
        self.alias = "StreamStats Data Preprocessing"

        # List of tool classes associated with this toolbox
        self.tools = [Setup,Elevation]


# template for new tools within this toolbox.
# outside packages could be wrapped in this to shorten this script...
class Setup(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Setup"
        self.description = "Generate the file structure for Stream Stats Data Preprocessing."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = None
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        return



class Elevation(object): # keeping this as a template
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Elevation"
        self.description = "Function to process elevation data into Stream Stats file structure."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = None
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        return