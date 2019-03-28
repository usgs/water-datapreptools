'''
Code to replicate the hydroDEM_work_mod.aml, agree.aml, and fill.aml scripts

Theodore Barnhart, tbarnhart@usgs.gov, 20190225

Reference: agree.aml
    
'''

import numpy as np
import arcpy
arcpy.CheckOutExtension("Spatial")
import sys
import os
from arcpy.sa import *

def hydrodem(outdir, huc8cov, origdem, dendrite, snap_grid, bowl_polys, bowl_lines, inwall, drainplug, start_path, buffdist, inwallbuffdist, inwallht, outwallht, agreebuf, agreesmooth, agreesharp, bowldepth, copylayers, cellsz, bowling, in_wall, drain_plugs):
    '''Hydro-enforce a DEM

    This aml is used by the National StreamStats Team as the optimal
    approach for preparing a state's physiographic datasets for watershed delineations.
    It takes as input, a 10-meter (or 30-foot) DEM, and enforces this data to recognize
    NHD hydrography as truth.  WBD can also be recognized as truth if avaialable for a
    given state/region. This aml assumes that the DEM has first been projected to a
    state's projection of choice. This aml prepares data to be used in the Archydro
    data model (the GIS database environment for National StreamStats).

    The specified <8-digit HUC> should have a path associated with it in the variable 
    settings section near the top of this aml.  The value entered will create a workspace
    with this HUC id as it's name, and copy all output datasets into the new workspace.
    If the workspace already exists, it should be empty before running this aml.
    
    The snap_grid is used to orient the origin coordinate of the output grids to align 
    with neighboring HUC grids that have already been processed.  
    Typically, this value is rounded to the nearest value
    divisible by 10 (in cases where datsets are in units meters) or 30 (in cases where
    datasets are in units feet).  The snap grid could be your input dem, if that grid
    has already been rounded out (if topogrid was used and steps were followed on the 
    nhd web page referenced above, then the input dem could be used).

    Parameters
    ----------
    outdir : DEWorkspace
        Working directory
    huc8cov : DEFeatureClass
        Local division feature class, often HUC8
    origdem :

    dendrite :
    
    snap_grid :
    
    bowl_polys :
    
    bowl_lines :
    
    inwall : 
    
    drainplug : 
    
    start_path :
    
    buffdist :
    
    inwallbuffdist :
    
    inwallht :
    
    outwallht :
    
    agreebuf :
    
    agreesmooth :
    
    agreesharp :
    
    bowldepth :
    
    copylayers :
    
    cellsz :
    
    bowling :
    
    in_wall :
    
    drain_plugs :

    Returns
    -------
    filldem : arcpy.sa Raster
        hydro-enforced, filled DEM
    fdirg : arcpy.sa Raster
        flow direction grid cooresponding to filldem
    faccg : arcpy.sa Raster
        flow accumulation grid cooresponding to filldem
    sink_path : path
        path to sink feature class

    '''
    arcpy.AddMessage("HydroDEM is running")

    ## put some checks here about the _bypass variables
    dp_bypass = False
    iw_bypass = False
    bowl_bypass = False

    if in_wall is None:
        iw_bypass == True

    if drain_plugs is None:
        dp_bypass == True

    if (bowl_polys is None) or (bowl_lines is None):
        bowl_bypass == True

    # set working directory and environment
    arcpy.env.Workspace = outdir
    arcpy.env.cellSize = cellsz

    # buffer the huc8cov
    hucbuff = ' some temp location'
    arcpy.AddMessage('Buffering Local Divisons')
    arcpy.Buffer_analysis(huc8cov,hucbuff) # do we need to buffer if this is done in the setup tool, maybe just pass hucbuff to the next step from the parameters...

    arcpy.env.Extent = hucbuff # set the extent to the buffered HUC

    # rasterize the buffered local division
    arcpy.AddMessage('Rasterizing %s'%hucbuff)
    outGrid = 'some temp location'
    # may need to add a field to hucbuff to rasterize it... 
    arcpy.FeaturetoRaster_conversion(hucbuff,None,outGrid,cellsz)

    arcpy.env.Mask = outGrid # set mask (L169 in hydroDEM_work_mod.aml)

    elevgrid = agree(origdem,dendrite,agreebuf, agreesmooth, agreesharp) # run agree function

    # rasterize the dendrite
    arcpy.AddMessage('Rasterizing %s'%dendrite)
    dendriteGridpth = 'some temp location'

    # may need to add a field to dendrite to rasterize it...
    arcpy.FeaturetoRaster_conversion(dendrite,None,dendriteGridpth,cellsz)
    dendriteGrid = Raster(dendriteGridpth)
    # burning streams and adding walls
    arcpy.AddMessage('Starting Walling') # (L182 in hydroDEM_work_mod.aml)

    ridgeNLpth = 'some temp location'
    # may need to add a field to huc8cov to rasterize it...
    arcpy.FeaturetoRaster_conversion(huc8cov,None,ridgeNLpth,cellsz) # rasterize the local divisions feature
    #ridgeEXP = 'some temp location'
    ridgeNL = Raster(ridgeNLpth) # load ridgeNL 
    outRidgeEXP = Expand(ridgeNL,2,[1]) # the last parameter is the zone to be expanded, this might need to be added to the dummy field above... 
    #outRidgeEXP.save(ridgeEXP) # save temperary file, maybe not needed

    ridgeW = SetNull((not IsNull(ridgeNL) and not IsNull(ridgeEXP)), ridgeEXP)
    demRidge8 = elevgrid + Con((not IsNull(ridgeW) and IsNull(nhd)), outwallht, 0)

    arcpy.AddMessage('Walling Complete')

    if dp_bypass == False: # dp_bypass isn't defined anywhere...
        dpg_path = 'some temp location'
        arcpy.FeaturetoRaster_conversion(drainplug,None,dpg_path,arcpy.env.cellSize) # (L195 in hydroDEM_work_mod.aml)
        dpg = Raster(dpg_path) # load the raster object

    if bowl_bypass == False: # bowl_bypass isn't defined anyhwere...
        arcpy.AddMessage('Starting Bowling')
        blp_name = 'blp'
        blp_path = os.path.join(arcpy.env.Workspace,blp_name)
        inPaths = '%s;%s'%(bowl_lines,dpg_path)
        arcpy.MosaicToNewRaster_management(inPaths,arcpy.env.Workspace,blp_name) # probably need some more options

        blp = Raster(blp_path)

        eucd = SetNull(IsNull(bowl_polys), EucDistance(blp)) # (L210 in hydroDEM_work_mod.aml)
        demRidge8wb = demRidge8 - Con( not IsNull(eucd), (bowldepth / (eucd+1)), 0)

        arcpy.AddMessage('Bowling complete')

    else:
        arcpy.AddMessage('Bowling Skipped')

    if iw_bypass == False:
        arcpy.AddMessage('Starting Walling')
        iwb_name = 'inwall_buff'
        iwb_path = os.path.join(arcpy.env.Workspace,iwb_name)
        arcpy.Buffer_analysis(inwall,iwb_path,inwallbuffdist) #(L223 in hydroDEM_work_mod.aml)
        
        tmpGrd_name = 'tmpGrd'
        tmpGrd_path = os.path.join(arcpy.env.Workspace,tmpGrd_name)

        arcpy.FeaturetoRaster_conversion(iwb_path,arcpy.env.Workspace,tmpGrd_name)
        tmpGrd = Raster(tmpGrd_path)

        inwallg = Con(tmpGrd == 100, 0)
        dem_enforced = demRidge8wb + Con((not IsNull(inwallg) and IsNull(nhdgrd)), inwallht, 0) #(L226 in hydroDEM_work_mod.aml)

        arcp.AddMessage('Walling Complete')
    else:
        del dem_enforced
        dem_enforced = demRidge8wb
        arcpy.AddMessage('Walling Skipped')

    if dp_bypass == False:
        detmp = Con(IsNull(dpg),dem_enforced)
        del dem_enforced
        dem_enforced = detmp #(L242 in hydroDEM_work_mod.aml)

    arcpy.env.Extent(hucbuff)
    arcpy.env.snapRaster(snap_grid)
    arcpy.cellSize(origdem)

    arcpy.AddMessage('Start Fill')

    filldem,fdirg = fill(dem_enforced, "sink", None, fdirg)

    arcpy.AddMessage('Fill Complete')


    if dp_bypass == False:
        fdirg2 = FlowDirection(filldem, None, 'Force')
        fdirg = Con(IsNull(dpg), fdirg2, 0) # (L256 in hydroDEM_work_mod.aml), insert a zero where drain plugs were.

    arcpy.env.mask = ridgeNLpth # mask to HUC

    # might need to save the fdirg, delete it from the python workspace, and reload it...
    arcpy.AddMessage('Starting Flow Accumulation')
    faccg = FlowAccumulation(fdirg, None, "INTEGER")
    arcpy.AddMessage('Flow Accumulation Complete')

    arcpy.AddMessage('Creating Sink Features')
    fsinkg = Con((filldem - origdem) > 1, 1)
    fsinkg_name = 'fsinkg'
    fsinkg_path = os.path.join(arcpy.env.Workspace,fsinkc_name)
    fsinkg.save(fsinkg_path)
    del fsinkg # clean up
    
    fsinkc_name = 'fsinkc'
    fsinkc_path = os.path.join(arcpy.env.Workspace,fsinkc_name)
    arcpy.RasterToPolygon_conversion(fsinkg_path,fsinkg_path,'NO_SIMPLIFY') # (L273 in hydroDEM_work_mod.aml)

    arcpy.AddMessage('Sink Creation Complete')
    arcpy.AddMessage('HydroDEM Complete')

    # clean up the environment of temp files
    arcpy.Delete_management(fsinkg_path) # clean up
    # more statements needed here...

    return filldem,fdirg,faccg,fsinkc_path

def fill(dem, option, zlimit):
    ''' fill function from fill.aml
    Purpose
    -------
        This AML command fills sinks or peaks in a specified surface
        grid and outputs a filled surface grid and, optionally, its
        flow direction grid.  If output filled grid already exists,
        it will be removed first

    Authors
    -------
        Gao, Peng        Dec 20, 1991  Original coding
        Laguna, Juan     Nov  1, 2000  Fix to prevent failure on large FP grids
        Ajit M. George   Jul 31, 2001  Use force option for iterative flowdirection.
                                      calculation, and normal option for direction output.
        Theodore Barnhart, tbarnhart@usgs.gov, 20190225, recoded to arcpy/python
        
    Parameters
    ----------
    dem : arcpy.sa Raster
    sink == option : string
        Filling option, 'sink' or 'peak'
    zlimit : float?
        Unknown
    direction : arcpy.sa Raster
        Flow direction raster

    Returns
    -------
    filldem : arcpy.sa Raster
        filled DEM
    direction : arcpy.sa Raster
        flow direction grid
    '''
    from arcpy.sa import *
    import numpy as np

    # generate a bunch of variables in aml, not sure if needed in new arcpy...
    # &s frmdir [show &workspace]
    # &s todir  [dir [pathname %filled%]]
    # &s filled [entryname %filled%]
    # &s dem    [pathname %dem%]
    # &s dm     [substr [entryname %dem%] 1 6]

    # check options [L29-43 fill.aml]

    dem = Raster(dem)

    if option == 'sink':
    	arcpy.AddMessage('Sink Routine Selected')
    	filled = dem
    else:
    	if option == 'peak':
    		arcpy.AddMessage('Peak Routine Selected')
    		filled = dem.maximum - dem # (L56 fill.aml) # dem.maximum may need to be a raster of shape(dem) filled with dem.maximum, this would return a grid where the peaks are now the low spots.
    	else:
    		arcpy.AddMessage('Unknown keyword.')

    arcpy.env.Extent = filled
    arcpy.env.cellSize = filled #(L75 fill.aml)

    ff = FocalFlow(filled) # compute focal flow

    if ff == 255:
        tmp = np.min([filled[1,1],filled[1,0],filled[1,-1],
                        filled[0,1], filled[0,-1],
                        filled[-1,1],filled[-1,0],filled[-1,-1]])

    else:
        tmp = filled.copy() # this may not work, may need to write out filled and read it back in as tmp...

    arcpy.env.Extent(filled)
    filled = tmp #(L85 in fill.aml)

    del tmp # assuming this is an object...
    del ff

    arcpy.AddMessage('Filling...')
    # loop until there are no sinks in the surface grid
    finished = False
    sinkcnt = 0
    numsink = 0

    while not finished:

        fdr = FlowDirection(filled, 'Force', None, None) # compute flow direction (L100 in fill.aml)
        sr = Sink(fdr)

        if not sr.hasRAT: # test if the VAT table exists
            arcpy.BuildRasterAttributeTable_management(sr) # if not, build it

        # might need to write out the sr raster here and reload it
        if sr.hasRAT: # test if the VAT table exists (L105 in fill.aml)
            # below this if statement, I think the point is to count the number of sinks...
            newsinkcnt = arcpy.GetCount_management(sr) # Pretty sure this is the same as %grd$nclass%, which references the sink raster (sr) describes at L104 in fill.aml

        else:
            newsinkcnt = 0

        arcpy.AddMessage('Number of %s(s): %s'%(option,newsinkcnt))
        if newsinkcnt < 1:
            finished = True
        else:
            if numsink == arcpy.GetCount_management(sr) and sinkcnt == newsinkcnt:
                finished = True

        if not finished:
            sinkcnt = newsinkcnt
            numsink = newsinkcnt

            # describe %filled% (L124 in filled.aml)
            sub = Watershed(fdr,sr) # compute watersheds from pour points

            if not sub.hasRAT:
                arcpy.BuildRasterAttributeTable_management(sub)

            del sr

            zonalfill = ZonalFill(sub,filled)

            zonalfill1 = Con(IsNull(zonalfill), filled.minimum, zonalfill)

            del zonalfill

            if zlimit is None:
                zonalfill2 = Con(filled < zonalfill1, zonalfill1, filled)

            else:
                zm1 = ZonalStatistics(sub, "VALUE", filled, "MINIMUM")
                zmm = Con(IsNull(zm1),Minimum(filled),zm1)
                zf2 = Con((filled < zf1) & ((zf1 - zmm) < zlimit), zf1, filled)
        
        del filldem
        filldem = zf2 # (L147 in fill.aml)

    return filldem

    ##########################################
    #
    #	original fill.aml code below
    #
    ##########################################
    #
    #/* @(#)fill.aml	1.14 9/25/95 18:05:07
	# /*
	# /* FILL.AML
	# /*
	# /* . Purpose:
	# /*    This AML command fills sinks or peaks in a specified surface
	# /*    grid and outputs a filled surface grid and, optionally, its
	# /*    flow direction grid.  If output filled grid already exists,
	# /*    it will be removed first
	# /*
	# /* . Author(s):
	# /*    Gao, Peng        Dec 20, 1991  Original coding
	# /*    Laguna, Juan     Nov  1, 2000  Fix to prevent failure on large FP grids
	# /*    Ajit M. George   Jul 31, 2001  Use force option for iterative flowdirection.
	# /*                                   calculation, and normal option for direction output.

	# &arg dem filled option zlimit direction
	# &severity &error &routine error
	# &s msgsave
	# &s vrfsave
	# /*
	# /*  Where are we ?
	# /*
	# &if [show program] ne GRID &then
	#   &return FILL only runs in GRID.
	# /*
	# /* validate args
	# /*
	# &if [null %dem%] OR [null %filled%] &then &do
	#   &goto USAGE
	# &end
	# &s frmdir [show &workspace]
	# &s todir  [dir [pathname %filled%]]
	# &s filled [entryname %filled%]
	# &s dem    [pathname %dem%]
	# &s dm     [substr [entryname %dem%] 1 6]
	# &if not [null %zlimit%] and [type %zlimit%] gt 0 ~
	#     and %zlimit%_ ne #_ &then &do
	#   &type Z-limit is not a number
	#   &goto USAGE
	# &end
	# &if [null %option%] or %option% eq # &then
	#   &s option sink
	# /*
	# /* prepare the grid for filling
	# /*
	# &workspace %todir%
	# &s msgsave [show &message]
	# /*&message &off
	# &if [locase %option%] eq 'sink' &then
	#   %filled% = %dem%
	# &else &do
	#   &if [locase %option%] eq 'peak' &then &do
	#     &describe %dem%
	#     &s maxvalue %GRD$ZMAX%
	#     %filled% = %maxvalue% - %dem%
	#   &end
	#   &else &do
	#     &workspace %frmdir%
	#     &message %msgsave%
	#     &type Unknown keyword: %option%
	#     &goto USAGE
	#   &end
	# &end
	# &s vrfsave [show verify]
	# verify off
	# /*
	# /* fill in one cell sinks (peaks)
	# /*
	# &s window = [show setwindow]
	# &s cell = [show setcell]
	# &describe %filled%
	# setwindow [calc %grd$xmin% - %grd$dx%] %grd$ymin% ~
	#           [calc %grd$xmax% + %grd$dx%] %grd$ymax%
	# setcell %filled%
	# z00%dm%ff = focalflow(%filled%)
	# if (z00%dm%ff eq 255) then
	#   z00%dm%tmp = min(%filled%(1,1), %filled%(1,0), %filled%(1,-1), ~
	#                    %filled%(0,1), %filled%(0,-1), ~
	#                    %filled%(-1,1),%filled%(-1,0),%filled%(-1,-1))
	# else
	#   z00%dm%tmp = %filled%
	# endif
	# setwindow %filled%
	# %filled% = z00%dm%tmp
	# Arc kill z00%dm%ff all
	# Arc kill z00%dm%tmp all
	# setwindow %window%
	# setcell %cell%

	# &type Filling...
	# /*
	# /* loop until no sink in the surface grid
	# /*
	# &s finished = .FALSE.
	# &s sinkcnt = 0
	# &s numsink = 0
	# &do &until %finished%
	#   &if [exists z00%dm%dir -grid] &then Arc kill z00%dm%dir all
	#   z00%dm%dir = flowdirection (%filled%, #, force)
	#   z00%dm%snk = sink (z00%dm%dir)
	#   &if not [exists z00%dm%snk -VAT] &then
	#     buildvat z00%dm%snk
	#   &describe z00%dm%snk
	#   &if [exists z00%dm%snk -VAT] &then &do
	#     cursor sinkvat declare [joinfile z00%dm%snk vat -ext] info ro
	#     cursor sinkvat open
	#     &s newsinkcnt = %:sinkvat.count%
	#     cursor sinkvat close
	#     cursor sinkvat remove
	#   &end
	#   &else
	#     &s newsinkcnt = 0
	#   &type Number of %option%(s): %GRD$NCLASS%
	#   &if %GRD$NCLASS% < 1 &then
	#     &s finished = .TRUE.
	#   &else &do
	#     &if %numsink% = %GRD$NCLASS% and %sinkcnt% = %newsinkcnt% &then
	#       &s finished = .TRUE.
	#   &end
	#   &if not %finished% &then &do
	#     &s sinkcnt = %newsinkcnt%
	#     &s numsink = %GRD$NCLASS%
	#     &describe %filled%
	#     z00%dm%sub = watershed (z00%dm%dir, z00%dm%snk)
	#     &if not [exists z00%dm%sub -VAT] &then
	#       buildvat z00%dm%sub
	#     Arc kill z00%dm%snk
	#     z00%dm%zfl = zonalfill (z00%dm%sub, %filled%)
	#     z00%dm%zf1 = con (isnull (z00%dm%zfl), %GRD$ZMIN%, z00%dm%zfl)
	#     Arc kill z00%dm%zfl
	#     &if [null %zlimit%] OR [QUOTE %zlimit%] EQ # &then &do
	#       z00%dm%zf2 = con (%filled% < z00%dm%zf1, z00%dm%zf1, %filled%)
	#     &end
	#     &else &do
	#       z00%dm%zm1 = zonalmin (z00%dm%sub, %filled%)
	#       z00%dm%zmm = con (isnull (z00%dm%zm1), %GRD$ZMIN%, z00%dm%zm1)
	#       z00%dm%zf2 = con (%filled% < z00%dm%zf1 AND ~
	#                          z00%dm%zf1 - z00%dm%zmm < %zlimit%, ~
	#                          z00%dm%zf1, %filled%)
	#       Arc kill z00%dm%zm1
	#       Arc kill z00%dm%zmm
	#     &end
	#     Arc kill z00%dm%sub
	#     Arc kill z00%dm%zf1
	#     Arc kill %filled%
	#     rename z00%dm%zf2 %filled%
	#   &end
	# &end

	# /*
	# /* Done, finish up
	# /*
	# &if [locase %option%] eq peak &then &do
	#   z00%dm%zf2 = %maxvalue% - %filled%
	#   Arc kill %filled%
	#   rename z00%dm%zf2 %filled%
	# &end

	# &if [exists z00%dm%dir -grid] &then Arc kill z00%dm%dir all
	# &if not [null %direction%] and %direction%_ ne #_ &then
	# &do
	#   %direction% = flowdirection (%filled%)
	# &end

	# Arc kill z00%dm%snk
	# verify %vrfsave%
	# &workspace %frmdir%
	# &message %msgsave%
	# &return

	# /*
	# /* Usage
	# /*
	# &label USAGE
	#   &return &warning ~
	#   Usage: FILL <in_grid> <out_grid> {SINK | PEAK} {z_limit} {out_dir_grid}

	# /*
	# /* Error handling
	# /*
	# &routine error
	#   &severity &error &fail
	#   &if not [null %msgsave%] &then
	#     &message %msgsave%
	#   &if not [null %vrfsave%] &then
	#     verify %vrfsave%
	#   &if not [null %frmdir%] &then
	#     &workspace %frmdir%
	# &return &error

def agree(origdem, dendrite, agreebuf, agreesmooth, agreesharp):
    '''Agree function from AGREE.aml

    Original function by Ferdi Hellweger, http://www.ce.utexas.edu/prof/maidment/gishydro/ferdi/research/agree/agree.html

    recoded by Theodore Barnhart, tbarnhart@usgs.gov, 20190225

    -------------
    --- AGREE ---
    -------------
    
    --- Creation Information ---
    
    Name: agree.aml
    Version: 1.1
    Date: 10/13/96
    Author: Ferdi Hellweger
            Center for Research in Water Resources
            The University of Texas at Austin
            ferdi@crwr.utexas.edu
    
    --- Purpose/Description ---
    
    AGREE is a surface reconditioning system for Digital Elevation Models (DEMs).
    The system adjusts the surface elevation of the DEM to be consistent with a
    vector coverage.  The vecor coverage can be a stream or ridge line coverage. 

    Parameters
    ----------
    origdem : arcpy.sa Raster
        Original DEM with the desired cell size, oelevgrid in original script
    dendrite : Feature Class
        Dendrite feature layer to adjust the DEM, vectcov in the original script
    agreebuf : float 
        Buffer smoothing distance (same units as the horizontal), buffer in original script
    agreesmooth : float
        Smoothing distance (same units as the vertical), smoothdist in the original script
    agreesharp : float
        Distance for sharp feature (same units as the vertical), sharpdist in the original script

    Returns
    -------
    elevgrid : arcpy.sa Raster
        conditioned elevation grid returned as a arcpy.sa Raster object
    '''
    arcpy.AddMessage('Starting AGREE')

    # code to check that all inputs exist

    cellsize = (float(arcpy.GetRasterProperties_management(origdem, "CELLSIZEX")) + float(arcpy.GetRasterProperties_management(origdem, "CELLSIZEY")))/2. # compute the raster cell size

    arcpy.AddMessage('Setting Environment Variables')
    arcpy.env.Extent = origdem # (L130 AGREE.aml)
    arcpy.env.cellSize = cellSize # (L131 AGREE.aml)

    arcpy.AddMessage('Rasterizing the Dendrite.')
    dendriteGridPth = 'some temp location' # might need to add a field for rasterization
    arcpy.FeaturetoRaster_conversion(dendrite,dendriteGridPth)

    arcpy.AddMessage('Computing smooth drop/raise grid...')
    # expression = 'int ( setnull ( isnull ( vectgrid ), ( \"origdem\" + \"greesmooth\" ) ) )'

    dendriteGrid = Raster(dendriteGridPth)
    origdem = Raster(origdem)
    
    smogrid = Int(SetNull(IsNull(dendriteGrid, origdem + agreesmooth))) # compute the smooth drop/raise grid (L154 in AGREE.aml)

    arcpy.AddMessage('Computing vector distance grids...')
    vectdist = EucDistance(smogrid)
    # Need to produce vectallo (stores the elevation of the closest vector cell), is this the same as the smogrid?
    vectallo = EucAllocation(smogrid) # Roland Viger thinks the original vectallo is an allocation grid, that can be made with EucAllocation.

    arcpy.AddMessage('Computing buffer grids...')
    bufgrid1 = Con((vectdist > (agreebuf - (cellsize / 2.))), 1, 0) 
    bufgrid2 = Int(SetNull(bufgrid1 == 0, oelevgrid)) # (L183 in AGREE.aml)

    arcpy.AddMessage('Computing buffer distance grids...')
    # compute euclidean distance and allocation grids
    bufdist = EucDistance(bufgrid2)
    bufallo = EucAllocation(bufgrid2)

    arcpy.AddMessage('Computing smooth modified elevation grid...')
    smoelev =  vectallo + ((bufallo - vectallo) / (bufdist + vectdist)) * vectdist

    arcpy.AddMessage('Computing sharp drop/raise grid...')
    #shagrid = int ( setnull ( isnull ( vectgrid ), ( smoelev + %sharpdist% ) ) )
    shagrid = Int(SetNull(IsNull(vectgrid), (smoelev + agreesharp)))

    arcpy.AddMessage('Computing modified elevation grid...')
    elevgrid = Con(IsNull(vectgrid), smoelev, shagrid)

    arcpy.AddMessage('AGREE Complete')

    return elevgrid 

    #############################################################
    # AGREE.aml
    #
    #
    # /*
    # /*-------------
    # /*--- AGREE ---
    # /*-------------
    # /*
    # /*--- Creation Information ---
    # /*
    # /*Name: agree.aml
    # /*Version: 1.1
    # /*Date: 10/13/96
    # /*Author: Ferdi Hellweger
    # /*        Center for Research in Water Resources
    # /*        The University of Texas at Austin
    # /*        ferdi@crwr.utexas.edu
    # /*
    # /*--- Purpose/Description ---
    # /*
    # /*AGREE is a surface reconditioning system for Digital Elevation Models (DEMs).
    # /*The system adjusts the surface elevation of the DEM to be consistent with a
    # /*vector coverage.  The vecor coverage can be a stream or ridge line coverage. 
    # /*
    # /*--- Get Input Data ---
    # /*
    # &args oelevgrid vectcov buffer smoothdist sharpdist

    # /*
    # &if ( [ length %oelevgrid% ] = 0 ) &then &do
    #   /*-ls001
    #   &type AGREE:
    #   &type AGREE: INPUT REQUIRED
    #   /*
    #   &label a
    #   &type AGREE:
    #   &sv oelevgrid = [ response 'AGREE: Elevation Grid']
    #   &if ( [ length %oelevgrid% ] = 0 ) &then  &do
    #     /*-ls002
    #     &type AGREE:
    #     &type AGREE: INPUT ERROR - Elevation Grid has to be specified
    #     &goto a
    #     /*-le002
    #   &end
    #   &if ( not [ exists %oelevgrid% -grid ] ) &then  &do
    #     /*-ls003
    #     &type AGREE:
    #     &type AGREE: INPUT ERROR - Grid does not exist
    #     &goto a
    #     /*-le003
    #   &end
    #   /*
    #   &label b
    #   &type AGREE:
    #   &sv vectcov = [ response 'AGREE: Vector Coverage']
    #   &if ( [ length %vectcov% ] = 0 ) &then  &do
    #     /*-ls004
    #     &type AGREE:
    #     &type AGREE: INPUT ERROR - Vector Coverage has to be specified.
    #     &goto b
    #     /*-le004
    #   &end
    #   &if ( not [ exists %vectcov% -cover ] ) &then &do
    #     /*-ls006
    #     &type AGREE:
    #     &type AGREE: INPUT ERROR - Coverage does not exist
    #     &goto b
    #     /*-le006
    #   &end
    #   /*
    #   &label c
    #   &type AGREE:
    #   &sv buffer = [ response 'AGREE: Buffer Distance']
    #   &if ( [ length %buffer% ] = 0 ) &then &do
    #     /*-ls008
    #     &type AGREE:
    #     &type AGREE: INPUT ERROR - Buffer Distance has to be specified
    #     &goto c
    #     /*-le008
    #   &end
    #   /*
    #   &type AGREE:
    #   &type AGREE: Note that for the upcoming smooth and sharp drop/raise
    #   &type AGREE: distance positive is up and negative is down.
    #   /*
    #   &label d
    #   &type AGREE:
    #   &sv smoothdist = [ response 'AGREE: Smooth Drop/Raise Distance']
    #   &if ( [ length %smoothdist% ] = 0 ) &then &do
    #     /*ls009
    #     &type AGREE:
    #     &type AGREE: INPUT ERROR - Smooth Drop/Raise Distance has to be specified
    #     &goto d
    #     /*-le009
    #   &end
    #   /*
    #   &label e
    #   &type AGREE:
    #   &sv sharpdist = [ response 'AGREE: Sharp Drop/Raise Distance']
    #   &if ( [ length %sharpdist% ] = 0 ) &then &do
    #     /*-ls010
    #     &type AGREE:
    #     &type AGREE: INPUT ERROR - Sharp Drop/Raise Distance has to be specified
    #     &goto e
    #     /*-le010
    #   &end
    #   /*-le001
    # &end
    # /*
    # &type AGREE:
    # &type AGREE: Starting...
    # /*
    # /*--- General Set Up ---
    # /*
    # &type AGREE:
    # &type AGREE: Extracting original elevation grid parameters...
    # &describe %oelevgrid%
    # &sv cellsize = %GRD$DX%
    # /*
    # /*&if [extract 1 [show display]] ne 9999 &then
    # /*display 9999
    # /*
    # &type AGREE:
    # &type AGREE: Displaying original elevation grid...
    # /*mape %oelevgrid%
    # /*gridpaint %oelevgrid% value linear nowrap gray
    # /*
    # /*set analysis environment
    # /*
    # &type AGREE:
    # &type AGREE: Setting the analysis environment...
    # setwindow %oelevgrid%
    # setcell %oelevgrid%
    # /*
    # /*--- Agree Method ---
    # /*
    # /*compute vectgrid
    # /*
    # &type AGREE:
    # &type AGREE: Computing vector grid...
    # &type AGREE:
    # &if [exists vectgrid -grid] &then
    # arc kill vectgrid all
    # vectgrid = linegrid ( %vectcov% )
    # &type AGREE:
    # &type AGREE: Displaying vector grid...
    # /*gridpaint vectgrid
    # /*
    # /*compute smogrid
    # /*
    # &type AGREE:
    # &type AGREE: Computing smooth drop/raise grid...
    # &type AGREE:
    # &if [exists smogrid -grid] &then
    # arc kill smogrid all
    # smogrid = int ( setnull ( isnull ( vectgrid ), ( %oelevgrid% + %smoothdist% ) ) )
    # &type AGREE:
    # &type AGREE: Displaying smooth drop/raise grid...
    # /*gridpaint smogrid value linear nowrap gray
    # /*
    # /*compute vectdist and vectallo
    # /*
    # &type AGREE:
    # &type AGREE: Computing vector distance grids...
    # &type AGREE:
    # &if [exists vectdist -grid] &then
    #   arc kill vectdist all
    # &if [exists vectallo -grid] &then
    #   arc kill vectallo all
    # vectdist = eucdistance( smogrid, #, vectallo, #, # )
    # &type AGREE:
    # &type AGREE: Displaying vector distance grid...
    # /*gridpaint vectdist value linear nowrap gray
    # /*
    # /*compute bufgrid1 and bufgrid2
    # /*
    # &type AGREE:
    # &type AGREE: Computing buffer grid...
    # &type AGREE:
    # &if [exists bufgrid1 -grid] &then
    #   arc kill bufgrid1 all
    # &if [exists bufgrid2 -grid] &then
    #   arc kill bufgrid2 all
    # bufgrid1 = con ( ( vectdist > ( %buffer% - ( %cellsize% / 2 ) ) ), 1, 0)
    # bufgrid2 = int ( setnull ( bufgrid1 == 0, %oelevgrid% ) ) 
    # &type AGREE:
    # &type AGREE: Displaying buffer grid...
    # /*gridpaint bufgrid2 value linear nowrap gray
    # /*
    # /*compute bufdist and bufballo
    # /*
    # &type AGREE:
    # &type AGREE: Computing buffer distance grids...
    # &type AGREE:
    # &if [exists bufdist -grid] &then
    #   arc kill bufdist all
    # &if [exists bufallo -grid] &then
    #   arc kill bufallo all
    # bufdist = eucdistance( bufgrid2, #, bufallo, #, # )
    # &type AGREE:
    # &type AGREE: Displaying buffer distance grid...
    # /*gridpaint bufdist value linear nowrap gray
    # /*
    # /*compute smoelev
    # /*
    # &type AGREE:
    # &type AGREE: Computing smooth modified elevation grid...
    # &type AGREE:
    # &if [exists smoelev -grid] &then
    #   arc kill smoelev all
    # smoelev =  vectallo + ( ( bufallo - vectallo ) / ( bufdist + vectdist ) ) * vectdist
    # &type AGREE:
    # &type AGREE: Displaying smooth modified elevation grid...
    # &type AGREE:
    # /*gridpaint smoelev value linear nowrap gray
    # /*
    # /*compute shagrid
    # /*
    # &type AGREE:
    # &type AGREE: Computing sharp drop/raise grid...
    # &type AGREE:
    # &if [exists shagrid -grid] &then
    #   arc kill shagrid all
    # shagrid = int ( setnull ( isnull ( vectgrid ), ( smoelev + %sharpdist% ) ) )
    # &type AGREE:
    # &type AGREE: Displaying sharp drop/raise grid...
    # /*gridpaint shagrid value linear nowrap gray
    # /*
    # /*compute elevgrid
    # /*
    # &type AGREE:
    # &type AGREE: Computing modified elevation grid...
    # &type AGREE:
    # &if [exists elevgrid -grid] &then
    #   arc kill elevgrid all
    # elevgrid = con ( isnull ( vectgrid ), smoelev, shagrid )
    # &type AGREE:
    # &type AGREE: Displaying modified elevation grid...
    # /*gridpaint elevgrid value linear nowrap gray
    # /*
    # /*clean up
    # /*
    # &type AGREE:
    # &type AGREE: Cleaning up...
    # &type AGREE:
    # arc kill vectgrid all
    # arc kill smogrid all
    # arc kill vectdist all
    # arc kill vectallo all
    # arc kill bufgrid1 all
    # arc kill bufgrid2 all
    # arc kill bufdist all
    # arc kill bufallo all
    # arc kill smoelev all
    # arc kill shagrid all
    # /*
    # /*close up
    # /*
    # &type AGREE:
    # &type AGREE: Normal end.
    # &type AGREE:
    # &type AGREE: NOTE: Modified elevation grid is saved as elevgrid in current workspace.
    # &type AGREE: 
    # &return