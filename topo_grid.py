import arcpy
arcpy.CheckOutExtension("Spatial")
arcpy.CheckOutExtension("3D")
import os
from arcpy.sa import *
import time

def topogrid(workspace,huc8,buffdist,dendrite,dem,cellSize,vipPer,snapgrid = None ,huc12=None):
	'''Regenerate a DEM based on supplied hydrography features.
	
	Parameters
	----------
	workspace : str
		Path to geodatabase workspace.
	huc8 : str
		Path to local watershed feature class.
	buffdist : int
		Distance to buffer HUC8 in horizontal map units.
	dendrite : str
		Path to flowline dendrite feature class.
	dem : str
		Path to buffered, scaled, and projected DEM.
	cellSize : int
		Output cell size.
	vipPer : int
		VIP thining value.
	snapgrid : str (optional)
		Path to snapgrid to use instead of input DEM.
	huc12 : list (optional)
		List of paths to HUC12 values if the HUC8 is too large to process in one pass.

	Returns
	-------
	topodem : raster
		DEM generated from topo to raster.

	Notes
	-----
	See https://support.esri.com/en/technical-article/000004588
	'''

	strt = time.time()
	arcpy.AddMessage("Running TopoGrid")
	arcpy.env.workspace = workspace
	arcpy.env.scratchWorkspace = workspace
	arcpy.env.overwriteOutput = True
	arcpy.env.cellSize = cellSize

	if snapgrid == None:
		arcpy.env.snapRaster = dem
	else:
		arcpy.env.snapRaster = snapgrid

		# check snapgrid to make sure it works with HydroDEM later...
		dsc = arcpy.Describe(arcpy.env.snapRaster) 
		assert dsc.extent.XMin % 1 == 0, "Snap Grid origin not divisible by 1."

	tmpPaths = []
	tmpPtsPath = os.path.join(workspace,'vipPoints')
	tmpPaths.append(tmpPtsPath)

	singlePtsPath = os.path.join(workspace,'vipPoints_exp')
	tmpPaths.append(singlePtsPath)

	singlePtsElevPath = os.path.join(workspace,'vipPoints_exp_elev')
	tmpPaths.append(singlePtsElevPath)

	tmpTopoDEM = os.path.join(workspace,"topogr_tmp")
	tmpPaths.append(tmpTopoDEM)

	topodemPth = os.path.join(workspace,"topodem") # this is the final DEM path

	# clean up the workspace before proceeding.
	for pth in [tmpPtsPath, singlePtsPath, singlePtsElevPath, tmpTopoDEM, topodemPth]:
		if arcpy.Exists(pth):
			arcpy.Delete_management(pth)

	arcpy.AddMessage("	Converting dem to point cloud.")
	arcpy.RasterToMultipoint_3d(dem, tmpPtsPath, method = "VIP %0.1f"%(float(vipPer))) # run VIP
	arcpy.MultipartToSinglepart_management(tmpPtsPath,singlePtsPath) # explode multipoints
	ExtractValuesToPoints(singlePtsPath, dem, singlePtsElevPath) # extract the dem elevations to the points


	# now pull the z value into a field
	#arcpy.AddField_management(singlePtsPath,'elevation','FLOAT', None, None, None, None, "NULLABLE")
	#with arcpy.da.SearchCursor(singlePtsPath,['SHAPE@Z']) as src:
	#	with arcpy.da.UpdateCursor(singlePtsPath, ['elevation']) as dst:
	#		for srcRow, dstRow in zip(src,dst):
	#			dstRow[0] = srcRow[0]
	#			dst.updateRow(dstRow)

	arcpy.AddMessage("	Conversion complete.")

	# figure out the number of chunks that need to be run through topogrid
	if huc12 == None:
		numchunks = 1
	else:
		numchunks = len(huc12)

	if numchunks == 1: # if there is only one chunk, use the huc8
		arcpy.AddMessage("	Rasterizing point cloud.")
		tmpBuffPth = os.path.join(workspace,'topogrid_buff')
		tmpPaths.append(tmpBuffPth)

		arcpy.Buffer_analysis(huc8, tmpBuffPth, buffdist, "FULL", "ROUND") # buffer extent bounding polygon.
		desc = arcpy.Describe(tmpBuffPth)
		ext = str(desc.extent).split()
		xmin = ext[0]
		ymin = ext[1]
		xmax = ext[2]
		ymax = ext[3]

		extent = "%s %s %s %s"%(xmin,ymin,xmax,ymax)

		
		inputs = "%s RASTERVALU POINTELEVATION;%s # STREAM;%s # BOUNDARY"%(singlePtsElevPath,dendrite,tmpBuffPth) # old stype with point feature class

		#inputs = "%s POINTELEVATION;%s # STREAM;%s # BOUNDARY"%(singlePtsPath,dendrite,tmpBuffPth) # new trial style

		arcpy.TopoToRaster_3d(inputs, topodemPth, cellSize, extent, enforce = "ENFORCE", data_type = "SPOT")
		arcpy.AddMessage("	Rasterization Complete.")
	else: # iterate through the input huc12s
		
		topoList = [] # list to hold paths to intermediate files
		for i,hu in enumerate(huc12):
			i += 1

			arcpy.AddMessage('	Rasterizing point cloud chunk %s'%i)
			outPth = os.path.join(workspace,'topo_%s'%i)
			
			# make temp file paths
			huBuff_1_pth = os.path.join(workspace,'topogrid_buff_%s'%i)
			tmpPaths.append(huBuff_1_pth)

			huBuff_2_pth = os.path.join(workspace,'topogrid_buff2_%s'%i)
			tmpPaths.append(huBuff_2_pth)

			huDissPth = os.path.join(workspace,'hu_dis_%s'%i)
			tmpPaths.append(huDissPth)

			dendrite_clip = os.path.join(workspace,'dendrite_clip_%s'%i)
			tmpPaths.append(dendrite_clip)

			vip2k = os.path.join(workspace,'vip_clip_%s'%i)
			tmpPtsPath.append(vip2k)

			# prepare input datasets
			arcpy.Dissolve_management(hu, huDissPth)
			arcpy.Buffer_analysis(huDissPth, huBuff_1_pth, "50 Meters", "FULL", "ROUND")
			arcpy.Buffer_analysis(huDissPth, huBuff_2_pth, "2000 Meters", "FULL", "ROUND")

			arcpy.Clip_analysis(dendrite, huBuff_1_pth, dendrite_clip) # clip dendrite to 50 m
			acpy.Clip_analysis(singlePtsElevPath, huBuff_2_pth, vip2k) # clip topo points to 2000 m

			desc = arcpy.Describe(huBuff_1_pth)
			ext = str(desc.extent).split()
			xmin = ext[0]
			ymin = ext[1]
			xmax = ext[2]
			ymax = ext[3]

			extent = "%s %s %s %s"%(xmin,ymin,xmax,ymax)

			inputs = "%s RASTERVALU POINTELEVATION;%s # STREAM;%s # BOUNDARY"%(vip2k,dendrite_clip,huBuff_1_pth)
			arcpy.TopoToRaster_3d(inputs, outPth, cellSize, extent, enforce = "ENFORCE", data_type = "SPOT")

			if arcpy.Exists(outPth): # if the output DEM exists, append it to the list for mosaicing.
				topoList.append(outPth)
			arcpy.AddMessage("	Chunk %s complete."%i)

		# mosaic temp DEMs to one DEM
		arcpy.AddMessage("	Mosaicing chunks.")
		topoListstr = topoList.join(';') # turn list of paths to one long path
		arcpy.MosaicToNewRaster_management(topoListstr, workspace, tmpTopoDEM, "#", "32_BIT_FLOAT", "#", "1", "BLEND", "#")

		for ds in topoList: # clean up temp DEMS
			if arcpy.Exists(ds):
				arcpy.Delete_management(ds)

	arcpy.AddMessage("	Converting topogrid DEM to integers.")
	if arcpy.Exists(tmpTopoDEM):
		tmp = Raster(tmpTopoDEM)
		dem = Int(tmp + 0.5) # convert to integer grid.
		dem.save(topodemPth)

	arcpy.AddMessage("	Setting Z units.")
	# Set the zUnits of the output DEM to be the same as the input DEM
	insr = arcpy.Describe(dem).spatialReference
	outsr = arcpy.Describe(topodemPth).spatialReference

	zunits = float(insr.ZFalseOriginAndUnits.split()[-1])
	FalseOrigin = float(insr.ZFalseOriginAndUnits.split()[0])

	outsr.setZFalseOriginAndUnits(FalseOrigin, zunits)
	arcpy.DefineProjection_management(topodemPth,outsr) # actually update the projection here.

	# housekeeping
	#for ds in tmpPaths: # clean up temp datasets
	#	if arcpy.Exists(ds):
	#		arcpy.Delete_management(ds)

	arcpy.AddMessage("	TopoGrid DEM: %s"%topodemPth)

	endtime = time.time() - strt
	arcpy.AddMessage("TopoGrid complete! %0.3f minutes"%(endtime/60.))
	
	return None





	


