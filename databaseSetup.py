import arcpy
import sys
import os

def databaseSetup(output_workspace, output_gdb_name, hu_dataset, hu8_field, hu12_field, hucbuffer, nhd_path,elevation_projection_template, alt_buff, version = None):
	"""Tool to create the hydrologic folders, inwall and outwall lines, DEM clipping polygons, and buffered hydrologic units.
	
	Parameters
	----------
	output_workspace : str
		Output directory for processing to occure in.
	output_gdb_name : str
		Global file geodatabase to be created
	hu_dataset : str
		Feature class that defines local folder geographic boundaries.
	hu8_field : str
		Field name in "hu_dataset" to dissolve boundaries to local folder extents.
	hu12_field : str
		Field name in "hu_dataset" to generate inwalls from.
	hucbuffer : str
		Distance to buffer local folder bounds in map units.
	nhd_path : str
		Path to workspace containing NHD geodatabases.
	elevation_projection_template : str
		Path to DEM file to use as a projection template.
	alt_buff : str
		Alternative buffer to use on local folder boundaries.
	version : str
		Package version number.
	
	Returns
	-------
	None
	"""
	"""
	Old Notes
	---------
    HUC_process.py
    ==============
    This script setup up an archydro workspace for the StreamStats process
    The script takes the WBD, NHD and creates a new folder in a new workspace
    for each huc and creates a master filegdb that sits in the archydro root
    and holds the huc8index.  It also dissolves by 12 digit and 8 digit polygons
    and line feature classes, creates the inner walls feature class, creates a
    50m and 2000m buffer of the HUC and creats a 2000m huc buffer in the DEM
    projection (to use with your Elevation tools)
    
    Changes
    =======
    Created on: April 20 2010 by Martyn Smith, USGS
    Updated on: May 26, 2015 by Kitty Kolb, USGS
    Modified to remove M-values from shapefile creations.
    Updated on: April 11, 2019 by Kitty Kolb, USGS
    Modified to reflect ArcPy and new data naming conventions, wrote new cursor search
    April 22, 2019 - Theodore Barnhart: moved to python toolbox.
	"""

	if version:
		arcpy.AddMessage('StreamStats Data Preparation Tools version: %s'%(version))

	 # set up geoprocessor, with spatial analyst license
	if arcpy.CheckExtension("Spatial") == "Available":
		arcpy.CheckOutExtension("Spatial")
	else:
		arcpy.addmessage('License Error')

	# Set script to overwrite if files exist
	arcpy.env.overwriteOutput=True

	localName = "local"
	subName = "subWatershed"
	GDB_name = "input_data.gdb"

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
		output_gdb = os.path.join(output_workspace,output_gdb_name+".gdb")
		#output_gdb = output_workspace + "\\" + output_gdb_name + ".gdb"

		#create container geodatabase
		if arcpy.Exists(output_gdb):
			arcpy.Delete_management(output_gdb)

		arcpy.CreateFileGDB_management(output_workspace, output_gdb_name + ".gdb")

		#dissolve at 8 dig level and put in output workspace
		hu8_dissolve = arcpy.Dissolve_management(hu_dataset, os.path.join(output_gdb,"huc8index"), hu8_field)
		
		elev_spatial_ref = arcpy.Describe(elevation_projection_template).spatialReference # read the elevation spatial ref.
		orig_spatial_ref = arcpy.Describe(hu_dataset).spatialReference # read the local division spatial ref.

		# Setup loop to iterate thru each HUC in WBD dataset
		#fields = hu8_field
		with arcpy.da.SearchCursor(hu8_dissolve, hu8_field) as cursor:
			for row in cursor:
				#Get current huc 8
				current_hu8 = str(row[0])
				current_db = os.path.join(output_workspace,current_hu8,GDB_name) 
				#current_db = output_workspace + "\\" + row[0] + "\\input_data.gdb"
				arcpy.AddMessage("")
				#arcpy.AddMessage("%s = \"%s\"" % (hu8_field, current_hu8))
				
				#check to make sure NHD exists and set variable names, if no NHD for HUC, skip it
				arcpy.AddMessage("Starting processing local folder %s...."%(current_hu8))
				arcpy.AddMessage("	Checking to see if NHD exists for %s"%(current_hu8[:4]))
				NHDExists = False
				if arcpy.Exists(os.path.join(nhd_path,"NHD_H_" + current_hu8[:4] + "_HU4_GDB" + ".gdb")):
					orig_4dig_NHD = os.path.join(nhd_path,"NHD_H_" + current_hu8[:4] + "_HU4_GDB" + ".gdb")
					NHDExists = True
				else:
					arcpy.AddMessage("     4 DIGIT NHD DOES NOT EXIST FOR THE CURRENT HUC")
					arcpy.AddMessage("     Please download NHD for this HUC and/or ensure NHD geodatabase is named correctly")
					NHDExists = False

				#If NHD exists for current HUC 8, then do the work
				if NHDExists:
					#Create folder for HU inside output folder
					hydrog_projection_template = os.path.join(orig_4dig_NHD,"Hydrography","NHDFlowline") # get a file to generate hydrography clip.
					hydrog_spatial_ref = arcpy.Describe(hydrog_projection_template).spatialReference # make spatial reference object for reproject later
					arcpy.CreateFolder_management(output_workspace, current_hu8)
					arcpy.CreateFolder_management(os.path.join(output_workspace,current_hu8), "Layers")
					arcpy.CreateFolder_management(os.path.join(output_workspace,current_hu8),"tmp") # make scratch workspace later for hydroDEM.
								
					#Create file geodatabase to house data
					arcpy.CreateFileGDB_management(os.path.join(output_workspace,current_hu8), GDB_name)
					  
					#start output file creation
					#----------------------------------
					#WBD Processing
					#----------------------------------
					arcpy.AddMessage("  Doing WBD processing")

					#create variables for huc buffers
					hucbuffer_custom = os.path.join(current_db,"local_buffer" + str(hucbuffer))
					hucbuffer_custom_elev_dd83 = os.path.join(current_db,"local_buffer_elev" + str(hucbuffer) + "_dd83")
					hucbuffer_custom_hydrog_dd83 = os.path.join(current_db,"local_buffer_hydrog" + str(hucbuffer) + "_dd83")
					hucbuffer_alt = os.path.join(current_db,"local_buffer%s"%(alt_buff))

					#start process
					arcpy.AddMessage("    Selecting current local hydrologic unit.")
					arcpy.Select_analysis(hu_dataset, os.path.join(current_db,subName), "\"%s\" = \'%s\'" % (hu8_field, current_hu8))

					arcpy.AddMessage("    Dissolving sub-watershed polygons")
					arcpy.Dissolve_management(os.path.join(current_db,subName), os.path.join(current_db,localName), hu8_field)
					
					arcpy.AddMessage("    Creating inner and outer wall polyline feature classes")
					arcpy.PolygonToLine_management(os.path.join(current_db,subName), os.path.join(current_db,"huc12_line"))
					arcpy.PolygonToLine_management(os.path.join(current_db,localName), os.path.join(current_db,"outer_wall"))
					arcpy.Erase_analysis(os.path.join(current_db,"huc12_line"),os.path.join(current_db,"outer_wall"),os.path.join(current_db,"inwall_edit"))
					
					arcpy.AddMessage("    Creating user-defined buffered outwall dataset")
					arcpy.Buffer_analysis(os.path.join(current_db,localName), hucbuffer_custom, hucbuffer, "FULL", "ROUND")
					arcpy.AddMessage("    Creating %s meter buffered outwall dataset"%(alt_buff))
					arcpy.Buffer_analysis(os.path.join(current_db,localName), hucbuffer_alt, "%s METERS"%(alt_buff), "FULL", "ROUND")                
					
					arcpy.AddMessage("    Creating unprojected buffered outwall dataset for elevation and hydrography clips")
					arcpy.Project_management(hucbuffer_custom, hucbuffer_custom_elev_dd83, elev_spatial_ref, in_coor_system = orig_spatial_ref)
					arcpy.Project_management(hucbuffer_custom, hucbuffer_custom_hydrog_dd83, hydrog_spatial_ref, in_coor_system = orig_spatial_ref)
					
					arcpy.AddMessage("    Creating sink point feature class")
					arcpy.CreateFeatureclass_management(os.path.join(output_workspace,current_hu8,"input_data.gdb"), "sinkpoint_edit", "POINT","","","", os.path.join(current_db,localName))

					#erase huc 12 line dataset after inwall is created
					if arcpy.Exists(os.path.join(current_db,"huc12_line")):
						arcpy.Delete_management(os.path.join(current_db,"huc12_line"))


					#----------------------------------
					#NHD Processing
					#----------------------------------
					arcpy.AddMessage("  Doing NHD processing")
					
					#Create NHD feature dataset within current HU database
					arcpy.AddMessage("    Creating NHD feature dataset in local hydrologic unit workspace")
					arcpy.CreateFeatureDataset_management(current_db, "Hydrography", orig_spatial_ref)
					arcpy.CreateFeatureDataset_management(current_db, "Reference", orig_spatial_ref)
					  
					#process each feature type in NHD
					featuretypelist = ["NHDArea", "NHDFlowline", "NHDWaterbody"]
					for featuretype in featuretypelist:
						
						#clip unprojected feature
						arcpy.AddMessage("      Clipping   " + featuretype)
						arcpy.Clip_analysis(os.path.join(orig_4dig_NHD,"Hydrography",featuretype), hucbuffer_custom_hydrog_dd83, os.path.join(current_db, featuretype + "_dd83"))
						
						#project clipped feature
						arcpy.AddMessage("      Projecting " + featuretype)
						arcpy.Project_management(os.path.join(current_db, featuretype + "_dd83"), os.path.join(current_db,featuretype + "_project"), orig_spatial_ref)
						arcpy.CopyFeatures_management(os.path.join(current_db, featuretype + "_project"), os.path.join(current_db,"Hydrography",featuretype))
						
						#delete unprojected and temporary projected NHD feature classes
						arcpy.Delete_management(os.path.join(current_db,featuretype + "_dd83"))
						arcpy.Delete_management(os.path.join(current_db, featuretype + "_project"))
						
					#create editable dendrite feature class from NHDFlowline
					arcpy.AddMessage("    Creating copy of NHDFlowline to preserve as original")
					arcpy.CopyFeatures_management(os.path.join(current_db,"Hydrography","NHDFlowline"), os.path.join(current_db,"Hydrography","NHDFlowline_orig"))
					
					arcpy.AddMessage("    Adding fields to NHDFlowline")
					arcpy.AddField_management(os.path.join(current_db,"Hydrography","NHDFlowline"), "comments", "text", "250")
					arcpy.AddField_management (os.path.join(current_db,"Hydrography","NHDFlowline"), "to_steward", "text", "50")
					arcpy.AddMessage("    Finished local %s"%current_hu8)
					
				#if no NHD, skip the HUC
				else:
					arcpy.AddMessage("     Processing skipped for this HUC--NO NHD")

			#del cursor, row    

	# handle errors and report using gp.addmessage function
	except:
		#If we have messages of severity error (2), we assume a GP tool raised it,
		#  so we'll output that.  Otherwise, we assume we raised the error and the
		#  information is in errMsg.
		#
		if arcpy.GetMessages(2):   
			arcpy.AddError(arcpy.GetMessages(2))
			arcpy.AddError(arcpy.GetMessages(2))
		else:
			arcpy.AddError(str(errMsg)) 