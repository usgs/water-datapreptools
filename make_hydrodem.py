'''
Code to replicate the hydroDEM_work_mod.aml and agree.aml scripts

Theodore Barnhart, tbarnhart@usgs.gov, 20190225

Reference: agree.aml
    
'''

import numpy as np
import arcpy
import sys
import os

arcpy.CheckOutExtension("Spatial")

def hydrodem(outdir, huc8cov, origdem, dendrite, snap_grid, bowl_polys, bowl_lines, inwall, drainplug, start_path, buffdist, inwallbuffdist, inwallht, outwallht, agreebuf, agreesmooth, agreesharp, bowldepth, copylayers, cellsz, bowling, in_wall, drain_plugs):
    '''Hydro-enforce a DEM

    Parameters
    ----------
    outdir : DEWorkspace
        Working directory
    huc8cov : DEFeatureClass
        Local division feature class, often HUC8
    origdem
    dendrite
    snap_grid
    bowl_polys
    bowl_lines
    inwall
    drainplug
    start_path
    buffdist
    inwallbuffdist
    inwallht
    outwallht
    agreebuf
    agreesmooth
    agreesharp
    bowldepth
    copylayers
    cellsz
    bowling
    in_wall
    drain_plugs

    Returns
    -------
    '''

    arcpy.AddMessage("HydroDEM is running")

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
    dendriteGrid = 'some temp location'
    # may need to add a field to dendrite to rasterize it...
    arcpy.FeaturetoRaster_conversion(dendrite,None,dendriteGrid,cellsz)

    # burning streams and adding walls
    arcpy.AddMessage('Starting Walling') # (L182 in hydroDEM_work_mod.aml)

    ridgeNL = 'some temp location'
    # may need to add a field to huc8cov to rasterize it...
    arcpy.FeaturetoRaster_conversion(huc8cov,None,ridgeNL,cellsz) # rasterize the local divisions feature
    ridgeEXP = 'some temp location'
    outRidgeEXP = arcpy.Expand(ridgeNL,2,[1]) # the last parameter is the zone to be expanded, this might need to be added to the dummy field above... 
    outRidgeEXP.save(ridgeEXP) # save temperary file, maybe not needed

    arcpy.gp.SingleOutputMapAlgebra_sa()


def fill(dem_enforced, filldem, sink, zlimit, fdirg):
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
    dem_enforced
    filldem
    sink
    zlimit
    fdirg

    Returns
    -------
    filldem?
    '''

    return filldem


def agree(origdem,dendrite,agreebuf, agreesmooth, agreesharp):
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
    from arcpy.sa import *

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





    






