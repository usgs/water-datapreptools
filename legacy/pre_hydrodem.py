# ---------------------------------------------------------------------------
# pre_hydrodem.py
# Created on: 04/29/2010
# Martyn Smith
# ---------------------------------------------------------------------------

import sys, os, egis
# Import commonly used functions so "egis." prefix not required
from egis import GPMsg, ScratchName, MsgError
from arcgisscripting import ExecuteError as GPError # short name for GP errors

#initiate geoprocessor
gp = egis.getGP(9.3)

# Set script to overwrite if files exist
gp.overwriteoutput = 1

# Local variables
output_workspace = gp.GetParameterAsText(0)
huc8 = gp.GetParameterAsText(1)
dendrite = gp.GetParameterAsText(2)
inwall = gp.GetParameterAsText(3)
dem = gp.GetParameterAsText(4)
cellsize = gp.GetParameterAsText(5)
sinkpoint = gp.GetParameterAsText(6)

try:
    #create coverages of input feature classes in output workspace
    gp.addmessage("Starting conversion of feature classes to coverages...")
    gp.FeatureclassToCoverage_conversion(huc8, output_workspace + "\\huc8")
    gp.FeatureclassToCoverage_conversion(inwall, output_workspace + "\\inwall")
    gp.FeatureclassToCoverage_conversion(dendrite, output_workspace + "\\nhdrch")
    gp.addmessage("Copying DEM...")
    if gp.exists(output_workspace + "\\dem"):
        gp.delete(output_workspace + "\\dem")
    gp.CopyRaster_management(dem,output_workspace + "\\dem")

    #copy projection to inwall coverage in case of empty inwall
    egis.ArcCommands(gp,"projectcopy cover nhdrch cover inwall" ,output_workspace,"")

    #set extent for feature to raster conversion
    if sinkpoint != "":
        gp.addmessage("Creating Drain Plug coverage...")
        gp.Extent = dem
        gp.FeatureToRaster_conversion(sinkpoint, "OBJECTID", output_workspace + "\\sinklnk", cellsize)
        gp.RasterToPolygon_conversion(output_workspace + "\\sinklnk", output_workspace + "\\sinkpoly.shp", "NO_SIMPLIFY")
        gp.FeatureclassToCoverage_conversion(output_workspace + "\\sinkpoly.shp", output_workspace + "\\drain_plugs")

except:
    # Print error message if an error occurs
    print gp.GetMessages()

#clean up temp datasets
if gp.exists(output_workspace + "\\sinkpoly.shp"):
    gp.delete(output_workspace + "\\sinkpoly.shp")
