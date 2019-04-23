# ---------------------------------------------------------------------------
# HUC_process.py
#
# This script setup up an archydro workspace for the StreamStats process
# The script takes the WBD, NHD and creates a new folder in a new workspace
# for each huc and creates a master filegdb that sits in the archydro root
# and holds the huc8index.  It also dissolves by 12 digit and 8 digit polygons
# and line feature classes, creates the inner walls feature class, creates a
# 50m and 2000m buffer of the HUC and creats a 2000m huc buffer in the DEM
# projection (to use with your Elevation tools)
#
# Created on: April 20 2010 by Martyn Smith, USGS
# Updated on: May 26, 2015 by Kitty Kolb, USGS
# Modified to remove M-values from shapefile creations.
# Updated on: April 11, 2019 by Kitty Kolb, USGS
# Modified to reflect ArcPy and new data naming conventions, wrote new cursor search
# ---------------------------------------------------------------------------

# Import system modules
import string, os, arcpy

# set up geoprocessor, with spatial analyst license
arcpy.CheckOutExtension("Spatial")

# Set script to overwrite if files exist
arcpy.env.overwriteOutput=True

# Local variables
output_workspace = arcpy.GetParameterAsText(0)
output_gdb_name = arcpy.GetParameterAsText(1)
hu_dataset = arcpy.GetParameterAsText(2)
hu8_field = arcpy.GetParameterAsText(3)
hu12_field = arcpy.GetParameterAsText(4)
hucbuffer = arcpy.GetParameterAsText(5)
nhd_path = arcpy.GetParameterAsText(6)
elevation_projection_template = arcpy.GetParameterAsText(7)

#set scratch and arcpy workspaces
arcpy.env.Workspace = output_workspace
arcpy.env.scratchWorkspace = output_workspace

#disable Z & M values
arcpy.env.outputZFlag = "Disabled"  
arcpy.AddMessage('Z: ' + arcpy.env.outputZFlag)  
arcpy.env.outputMFlag = "Disabled"  
arcpy.AddMessage('M: ' + arcpy.env.outputMFlag)

try:
    #name output fileGDB
    output_gdb = output_workspace + "\\" + output_gdb_name + ".gdb"

    #create container geodatabase
    if arcpy.Exists(output_gdb):
        arcpy.Delete_management(output_gdb)
    arcpy.CreateFileGDB_management(output_workspace, output_gdb_name + ".gdb")

    #dissolve at 8 dig level and put in output workspace
    hu8_dissolve = arcpy.Dissolve_management(hu_dataset, output_gdb + "\\huc8index", hu8_field)
    
    # Setup loop to iterate thru each HUC in WBD dataset
    fields = hu8_field
	with arcpy.da.SearchCursor(hu8_dissolve, fields) as cursor:
		for row in cursor:
			#Get current huc 8
			current_hu8 = str(fields)	
			current_db = output_workspace + "\\" + current_hu8 + "\\input_data.gdb"
			arcpy.AddMessage("")
            arcpy.AddMessage("%s = \"%s\"" % (hu8_field, current_hu8))
			
			#check to make sure NHD exists and set variable names, if no NHD for HUC, skip it
            arcpy.AddMessage(" Checking to see if NHD exists for current HUC8")
            NHDExists = "false"
            if arcpy.Exists(nhd_path + "\\NHD_H_" + current_hu8[:4] + "_HU4_GDB" + ".gdb"):
                orig_4dig_NHD = nhd_path + "\\NHD_H_" + current_hu8[:4] + "_HU4_GDB" + ".gdb"
                NHDExists = "true"
            else:
                arcpy.AddMessage("     4 DIGIT NHD DOES NOT EXIST FOR THE CURRENT HUC")
                arcpy.AddMessage("     Please download NHD for this HUC and/or ensure NHD geodatabase is named correctly")
                NHDExists = "false"

            #If NHD exists for current HUC 8, then do the work
            if NHDExists == "true":
                #Create folder for HU inside output folder
                arcpy.CreateFolder_management(output_workspace, current_hu8)
                arcpy.CreateFolder_management(output_workspace + "\\" + current_hu8, "Layers")
                            
                #Create file geodatabase to house data
                arcpy.CreateFileGDB_management(output_workspace + "\\" + current_hu8, "input_data.gdb")
                  
                #start output file creation
                arcpy.AddMessage(" Starting processing... ")

                #----------------------------------
                #WBD Processing
                #----------------------------------
                arcpy.AddMessage("  Doing WBD processing")

                #create variables for huc buffers
                hucbuffer_custom = current_db + "\\huc8_buffer" + str(hucbuffer)
                hucbuffer_custom_dd83 = current_db + "\\huc8_buffer" + str(hucbuffer) + "_dd83"
                hucbuffer_50 = current_db + "\\huc8_buffer50"

                #start process
                arcpy.AddMessage("    Selecting current HUC8")
                arcpy.Select_analysis(hu_dataset, current_db + "\\huc12", "\"%s\" = \'%s\'" % (hu8_field, current_hu8))
                arcpy.AddMessage("    Dissolving 12 digit internal polygons")
                arcpy.Dissolve_management(current_db + "\\huc12", current_db + "\\huc8", hu8_field)
                arcpy.AddMessage("    Creating inner and outer wall polyline feature classes")
                arcpy.PolygonToLine_management (current_db + "\\huc12", current_db + "\\huc12_line")
                arcpy.PolygonToLine_management (current_db + "\\huc8", current_db + "\\outer_wall")
                arcpy.Erase_analysis(current_db + "\\huc12_line", current_db + "\\outer_wall", current_db + "\\inwall_edit")
                arcpy.AddMessage("    Creating user-defined buffered HUC8 dataset")
                arcpy.Buffer_analysis(current_db + "\\huc8", hucbuffer_custom, hucbuffer, "FULL", "ROUND")
                arcpy.AddMessage("    Creating 50 meter buffered HUC8 dataset")
                arcpy.Buffer_analysis(current_db + "\\huc8", hucbuffer_50, "50 METERS", "FULL", "ROUND")                
                arcpy.AddMessage("    Creating unprojected buffered HUC8 dataset for Elevation and NHD clips")
                arcpy.Project_management(hucbuffer_custom, hucbuffer_custom_dd83, elevation_projection_template)
                arcpy.AddMessage("    Creating sink point feature class")
                arcpy.CreateFeatureclass_management(output_workspace + "\\" + current_hu8 + "\\input_data.gdb", "sinkpoint_edit", "POINT","","","", current_db + "\\huc8")

                #erase huc 12 line dataset after inwall is created
                if arcpy.Exists(current_db + "\\huc12_line"):
                    arcpy.Delete_management(current_db + "\\huc12_line")


                #----------------------------------
                #NHD Processing
                #----------------------------------
                arcpy.AddMessage("  Doing NHD processing")
                
                #Create NHD feature dataset within current HU database
                arcpy.AddMessage("    Creating NHD feature dataset in local HUC workspace")
                arcpy.CreateFeatureDataset_management(current_db, "Hydrography", hucbuffer_custom)
                arcpy.CreateFeatureDataset_management(current_db, "Reference", hucbuffer_custom)
                  
                #process each feature type in NHD
                featuretypelist = ["NHDArea", "NHDFlowline", "NHDWaterbody"]
                for featuretype in featuretypelist:
                    #clip unprojected feature
                    arcpy.AddMessage("      Clipping   " + featuretype)
                    arcpy.Clip_analysis(orig_4dig_NHD + "\\Hydrography\\" + featuretype, hucbuffer_custom_dd83, current_db + "\\" + featuretype + "_dd83")
                    #project clipped feature
                    arcpy.AddMessage("      Projecting " + featuretype)
                    arcpy.Project_management(current_db + "\\" + featuretype + "_dd83", current_db + "\\" + featuretype + "_project", hucbuffer_custom)
                    arcpy.CopyFeatures_management(current_db + "\\" + featuretype + "_project", current_db + "\\Hydrography\\" + featuretype)
                    #delete unprojected and temporary projected NHD feature classes
                    arcpy.Delete_management(current_db + "\\" + featuretype + "_dd83")
                    arcpy.Delete_management(current_db + "\\" + featuretype + "_project")
                    
                #create editable dendrite feature class from NHDFlowline
                arcpy.AddMessage("    Creating copy of NHDFlowline to preserve as original")
                arcpy.CopyFeatures_management(current_db + "\\Hydrography\\NHDFlowline", current_db + "\\Hydrography\\NHDFlowline_orig")
                arcpy.AddMessage("    Adding fields to NHDFlowline")
                arcpy.AddField_management (current_db + "\\Hydrography\\NHDFlowline", "comments", "text", "250")
                arcpy.AddField_management (current_db + "\\Hydrography\\NHDFlowline", "to_steward", "text", "50")
                arcpy.AddMessage("    Finished HUC")
                
            #if no NHD, skip the HUC
            else:
                arcpy.AddMessage("     Processing skipped for this HUC--NO NHD")

        del cursor, row	

# handle errors and report using gp.addmessage function
except Exception, errMsg:

    # If we have messages of severity error (2), we assume a GP tool raised it,
    #  so we'll output that.  Otherwise, we assume we raised the error and the
    #  information is in errMsg.
    #
    if arcpy.GetMessages(2):   
        arcpy.AddError(arcpy.GetMessages(2))
        print arcpy.GetMessages(2)
    else:
        arcpy.AddError(str(errMsg))   
