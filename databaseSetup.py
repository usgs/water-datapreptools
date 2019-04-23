import arcpy
import sys
import os

def databaseSetup(output_workspace, output_gdb_name, hu_dataset, hu8_field, hu12_field, hucbuffer, nhd_path,elevation_projection_template,alt_buff):
	"""
	Tool to create the hydrologic folders, inwall and outwall lines, DEM clipping polygons, and buffered hydrologic units.

	Parameters
	----------
	output_workspace : str
		Output directory for processing to occure in
	output_gdb_name : str
		Global file geodatabase to be created
	hu_dataset : str

	hu8_field : str

	hu12_field : str

	hucbuffer : str

	nhd_path : str

	elevation_projection_template : str
	"""

	 # set up geoprocessor, with spatial analyst license
	if arcpy.CheckExtension("Spatial") == "Available":
		arcpy.CheckOutExtension("Spatial")
	else:
		arcpy.addmessage('License Error')

	# Set script to overwrite if files exist
	arcpy.env.overwriteOutput=True

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
		
		# Setup loop to iterate thru each HUC in WBD dataset
		#fields = hu8_field
		with arcpy.da.SearchCursor(hu8_dissolve, hu8_field) as cursor:
			for row in cursor:
				#Get current huc 8
				current_hu8 = str(row[0])
				current_db = os.path.join(output_workspace,row[0],"input_data.gdb") 
				#current_db = output_workspace + "\\" + row[0] + "\\input_data.gdb"
				arcpy.AddMessage("")
				arcpy.AddMessage("%s = \"%s\"" % (hu8_field, current_hu8))
				
				#check to make sure NHD exists and set variable names, if no NHD for HUC, skip it
				arcpy.AddMessage(" Checking to see if NHD exists for current HUC8")
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
					arcpy.CreateFolder_management(output_workspace, current_hu8)
					arcpy.CreateFolder_management(os.path.join(output_workspace,current_hu8), "Layers")
								
					#Create file geodatabase to house data
					arcpy.CreateFileGDB_management(os.path.join(output_workspace,current_hu8), "input_data.gdb")
					  
					#start output file creation
					arcpy.AddMessage(" Starting processing... ")

					#----------------------------------
					#WBD Processing
					#----------------------------------
					arcpy.AddMessage("  Doing WBD processing")

					#create variables for huc buffers
					hucbuffer_custom = os.path.join(current_db,"huc8_buffer" + str(hucbuffer))
					hucbuffer_custom_dd83 = os.path.join(current_db,"huc8_buffer" + str(hucbuffer) + "_dd83")
					hucbuffer_alt = os.path.join(current_db,"huc8_buffer%s"%(alt_buff))

					#start process
					arcpy.AddMessage("    Selecting current outwall hydrologic unit.")
					arcpy.Select_analysis(hu_dataset, os.path.join(current_db,"huc12"), "\"%s\" = \'%s\'" % (hu8_field, current_hu8))

					arcpy.AddMessage("    Dissolving 12 digit internal polygons")
					arcpy.Dissolve_management(os.path.join(current_db,"huc12"), os.path.join(current_db,"huc8"), hu8_field)
					
					arcpy.AddMessage("    Creating inner and outer wall polyline feature classes")
					arcpy.PolygonToLine_management(os.path.join(current_db,"huc12"), os.path.join(current_db,"huc12_line"))
					arcpy.PolygonToLine_management(os.path.join(current_db,"huc8"), os.path.join(current_db,"outer_wall"))
					arcpy.Erase_analysis(os.path.join(current_db,"huc12_line"),os.path.join(current_db,"outer_wall"),os.path.join(current_db,"inwall_edit"))
					
					arcpy.AddMessage("    Creating user-defined buffered outwall dataset")
					arcpy.Buffer_analysis(os.path.join(current_db,"huc8"), hucbuffer_custom, hucbuffer, "FULL", "ROUND")
					arcpy.AddMessage("    Creating %s meter buffered outwall dataset"%(alt_buff))
					arcpy.Buffer_analysis(os.path.join(current_db,"huc8"), hucbuffer_alt, "%s METERS"%(alt_buff), "FULL", "ROUND")                
					
					arcpy.AddMessage("    Creating unprojected buffered outwall dataset for elevation and hydrography clips")
					arcpy.Project_management(hucbuffer_custom, hucbuffer_custom_dd83, elevation_projection_template)
					
					arcpy.AddMessage("    Creating sink point feature class")
					arcpy.CreateFeatureclass_management(os.path.join(output_workspace,current_hu8,"input_data.gdb"), "sinkpoint_edit", "POINT","","","", os.path.join(current_db,"huc8"))

					#erase huc 12 line dataset after inwall is created
					if arcpy.Exists(os.path.join(current_db,"huc12_line")):
						arcpy.Delete_management(os.path.join(current_db,"huc12_line"))


					#----------------------------------
					#NHD Processing
					#----------------------------------
					arcpy.AddMessage("  Doing NHD processing")
					
					#Create NHD feature dataset within current HU database
					arcpy.AddMessage("    Creating NHD feature dataset in local hydrologic unit workspace")
					arcpy.CreateFeatureDataset_management(current_db, "Hydrography", hucbuffer_custom)
					arcpy.CreateFeatureDataset_management(current_db, "Reference", hucbuffer_custom)
					  
					#process each feature type in NHD
					featuretypelist = ["NHDArea", "NHDFlowline", "NHDWaterbody"]
					for featuretype in featuretypelist:
						
						#clip unprojected feature
						arcpy.AddMessage("      Clipping   " + featuretype)
						arcpy.Clip_analysis(os.path.join(orig_4dig_NHD,"Hydrography",featuretype), hucbuffer_custom_dd83, os.path.join(current_db, featuretype + "_dd83"))
						
						#project clipped feature
						arcpy.AddMessage("      Projecting " + featuretype)
						arcpy.Project_management(os.path.join(current_db, featuretype + "_dd83"), os.path.join(current_db,featuretype + "_project"), hucbuffer_custom)
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
					arcpy.AddMessage("    Finished HUC")
					
				#if no NHD, skip the HUC
				else:
					arcpy.AddMessage("     Processing skipped for this HUC--NO NHD")

			#del cursor, row    

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