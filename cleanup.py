# ---------------------------------------------------------------------------
# cleanup.py
#
# Created on: April 29 2010 by Martyn Smith, USGS
# ---------------------------------------------------------------------------

# Import system modules
import arcgisscripting

# Create the Geoprocessor object
gp = arcgisscripting.create()

#input parameters
output_workspace = gp.GetParameterAsText(0)

#start cleanup
if gp.exists(output_workspace + "\\xxxfdrvalues"):
    gp.delete(output_workspace + "\\xxxfdrvalues")
if gp.exists(output_workspace + "\\ridge_w"):
    gp.delete(output_workspace + "\\ridge_w")
if gp.exists(output_workspace + "\\ridge_nl"):
    gp.delete(output_workspace + "\\ridge_nl")
if gp.exists(output_workspace + "\\ridge_exp"):
    gp.delete(output_workspace + "\\ridge_exp")
if gp.exists(output_workspace + "\\nhdgrd"):
    gp.delete(output_workspace + "\\nhdgrd")
if gp.exists(output_workspace + "\\inwallg_tmp"):
    gp.delete(output_workspace + "\\inwallg_tmp")
if gp.exists(output_workspace + "\\inwallg"):
    gp.delete(output_workspace + "\\inwallg")
if gp.exists(output_workspace + "\\eucd"):
    gp.delete(output_workspace + "\\eucd")
if gp.exists(output_workspace + "\\elevgrid"):
    gp.delete(output_workspace + "\\elevgrid")
if gp.exists(output_workspace + "\\dem_ridge8wb"):
    gp.delete(output_workspace + "\\dem_ridge8wb")
if gp.exists(output_workspace + "\\dem_ridge8"):
    gp.delete(output_workspace + "\\dem_ridge8")
if gp.exists(output_workspace + "\\dem_enforced"):
    gp.delete(output_workspace + "\\dem_enforced")
if gp.exists(output_workspace + "\\buffg"):
    gp.delete(output_workspace + "\\buffg")
if gp.exists(output_workspace + "\\dpg"):
    gp.delete(output_workspace + "\\dpg")
if gp.exists(output_workspace + "\\fdr2"):
    gp.delete(output_workspace + "\\fdr2")
