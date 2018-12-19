# ---------------------------------------------------------------------------
# HUC_process.py
#
# This script setup up an archydro workspace for the StreamStats process
# The script takes the WBD, NHD and creates a new folder in a new workspace
# for each huc and creates a master filegdb that sits in the archydro root
# and holds the huc8index.  It also dissolves by 12 digit and 8 digit polygons
# and line feature classes, creates the inner walls feature class, creates a
# 50m and 2000m buffer of the HUC and creats a 2000m huc buffer in the DEM
# projection (to use with your NED tools)
#
# Created on: April 20 2010 by Martyn Smith, USGS
# ---------------------------------------------------------------------------

# Import system modules
import string, os, arcgisscripting

# set up geoprocessor, with spatial analyst license
gp = arcgisscripting.create()

# Set script to overwrite if files exist
gp.overwriteoutput = 1

# Local variables
output_workspace = gp.GetParameterAsText(0)
output_gdb_name = gp.GetParameterAsText(1)
hu_dataset = gp.GetParameterAsText(2)
hu8_field = gp.GetParameterAsText(3)
hu12_field = gp.GetParameterAsText(4)
hucbuffer = gp.GetParameterAsText(5)
nhd_path = gp.GetParameterAsText(6)
NED_projection_template = gp.GetParameterAsText(7)

#set scratch and gp workspaces
gp.Workspace = output_workspace
gp.ScratchWorkspace = output_workspace

try:
    #name output fileGDB
    output_gdb = output_workspace + "\\" + output_gdb_name + ".gdb"

    #create container geodatabase
    if gp.exists(output_gdb):
        gp.delete(output_gdb)
    gp.CreateFileGDB_management(output_workspace, output_gdb_name + ".gdb")

    #dissolve at 8 dig level and put in output workspace
    hu8_dissolve = gp.Dissolve_management(hu_dataset, output_gdb + "\\huc8index", hu8_field)
    
    # Setup loop to iterate thru each HUC in WBD dataset
    rows = gp.SearchCursor(hu8_dissolve)
    row = rows.Next()
    current_hu8 = ""
    while row:
        
        #check if huc 8 field is null
        if current_hu8 != row.getvalue(hu8_field):
            
            #Get current huc 8
            current_hu8 = str(row.getvalue(hu8_field))
            current_db = output_workspace + "\\" + current_hu8 + "\\input_data.gdb"
            gp.addmessage("")
            gp.addmessage("%s = \"%s\"" % (hu8_field, current_hu8))          
            
            #check to make sure NHD exists and set variable names, if no NHD for HUC, skip it
            gp.addmessage(" Checking to see if NHD exists for current HUC8")
            NHDExists = "false"
            if gp.exists(nhd_path + "\\NHDH" + current_hu8[:4] + ".mdb"):
                orig_4dig_NHD = nhd_path + "\\NHDH" + current_hu8[:4] + ".mdb"
                NHDExists = "true"
            elif gp.exists(nhd_path + "\\NHDH" + current_hu8[:4] + ".gdb"):
                orig_4dig_NHD = nhd_path + "\\NHDH" + current_hu8[:4] + ".gdb"
                NHDExists = "true"
            else:
                gp.addmessage("     4 DIGIT NHD DOES NOT EXIST FOR THE CURRENT HUC")
                gp.addmessage("     Please download NHD for this HUC and/or ensure NHD geodatabase is named correctly")
                NHDExists = "false"

            #If NHD exists for current HUC 8, then do the work
            if NHDExists == "true":
                #Create folder for HU inside output folder
                gp.CreateFolder_management(output_workspace, current_hu8)
                gp.CreateFolder_management(output_workspace + "\\" + current_hu8, "Layers")
                            
                #Create file geodatabase to house data
                gp.CreateFileGDB_management(output_workspace + "\\" + current_hu8, "input_data.gdb")
                  
                #start output file creation
                gp.addmessage(" Starting processing... ")

                #----------------------------------
                #WBD Processing
                #----------------------------------
                gp.addmessage("  Doing WBD processing")

                #create variables for huc buffers
                hucbuffer_custom = current_db + "\\huc8_buffer" + str(hucbuffer)
                hucbuffer_custom_dd83 = current_db + "\\huc8_buffer" + str(hucbuffer) + "_dd83"
                hucbuffer_50 = current_db + "\\huc8_buffer50"

                #start process
                gp.addmessage("    Selecting current HUC8")
                gp.Select_analysis(hu_dataset, current_db + "\\huc12", "\"%s\" = \'%s\'" % (hu8_field, current_hu8))
                gp.addmessage("    Dissolving 12 digit internal polygons")
                gp.Dissolve_management(current_db + "\\huc12", current_db + "\\huc8", hu8_field)
                gp.addmessage("    Creating inner and outer wall polyline feature classes")
                gp.PolygonToLine_management (current_db + "\\huc12", current_db + "\\huc12_line")
                gp.PolygonToLine_management (current_db + "\\huc8", current_db + "\\outer_wall")
                gp.Erase_analysis(current_db + "\\huc12_line", current_db + "\\outer_wall", current_db + "\\inwall_edit")
                gp.addmessage("    Creating user-defined buffered HUC8 dataset")
                gp.buffer_analysis(current_db + "\\huc8", hucbuffer_custom, hucbuffer, "FULL", "ROUND")
                gp.addmessage("    Creating 50 meter buffered HUC8 dataset")
                gp.buffer_analysis(current_db + "\\huc8", hucbuffer_50, "50 METERS", "FULL", "ROUND")                
                gp.addmessage("    Creating unprojected buffered HUC8 dataset for NED and NHD clips")
                gp.project_management(hucbuffer_custom, hucbuffer_custom_dd83, NED_projection_template)
                gp.addmessage("    Creating sink point feature class")
                gp.CreateFeatureclass(output_workspace + "\\" + current_hu8 + "\\input_data.gdb", "sinkpoint_edit", "POINT","","","", current_db + "\\huc8")

                #erase huc 12 line dataset after inwall is created
                if gp.exists(current_db + "\\huc12_line"):
                    gp.delete(current_db + "\\huc12_line")


                #----------------------------------
                #NHD Processing
                #----------------------------------
                gp.addmessage("  Doing NHD processing")
                
                #Create NHD feature dataset within current HU database
                gp.addmessage("    Creating NHD feature dataset in local HUC workspace")
                gp.CreateFeatureDataset_management(current_db, "Hydrography", hucbuffer_custom)
                gp.CreateFeatureDataset_management(current_db, "Reference", hucbuffer_custom)
                  
                #process each feature type in NHD
                featuretypelist = ["NHDArea", "NHDFlowline", "NHDWaterbody"]
                for featuretype in featuretypelist:
                    #clip unprojected feature
                    gp.addmessage("      Clipping   " + featuretype)
                    gp.Clip_analysis(orig_4dig_NHD + "\\Hydrography\\" + featuretype, hucbuffer_custom_dd83, current_db + "\\" + featuretype + "_dd83")
                    #project clipped feature
                    gp.addmessage("      Projecting " + featuretype)
                    gp.project_management(current_db + "\\" + featuretype + "_dd83", current_db + "\\" + featuretype + "_project", hucbuffer_custom)
                    gp.CopyFeatures_management(current_db + "\\" + featuretype + "_project", current_db + "\\Hydrography\\" + featuretype)
                    #delete unprojected and temporary projected NHD feature classes
                    gp.delete(current_db + "\\" + featuretype + "_dd83")
                    gp.delete(current_db + "\\" + featuretype + "_project")
                    
                #create editable dendrite feature class from NHDFlowline
                gp.addmessage("    Creating copy of NHDFlowline to preserve as original")
                gp.CopyFeatures_management(current_db + "\\Hydrography\\NHDFlowline", current_db + "\\Hydrography\\NHDFlowline_orig")
                gp.addmessage("    Adding fields to NHDFlowline")
                gp.addfield_management (current_db + "\\Hydrography\\NHDFlowline", "comments", "text", "250")
                gp.addfield_management (current_db + "\\Hydrography\\NHDFlowline", "to_steward", "text", "50")
                gp.addmessage("    Finished HUC")
                
            #if no NHD, skip the HUC
            else:
                gp.addmessage("     Processing skipped for this HUC--NO NHD")
        row = rows.Next()  
    del rows

# handle errors and report using gp.addmessage function
except Exception, errMsg:

    # If we have messages of severity error (2), we assume a GP tool raised it,
    #  so we'll output that.  Otherwise, we assume we raised the error and the
    #  information is in errMsg.
    #
    if gp.GetMessages(2):   
        gp.AddError(gp.GetMessages(2))
        print gp.GetMessages(2)
    else:
        gp.AddError(str(errMsg))   