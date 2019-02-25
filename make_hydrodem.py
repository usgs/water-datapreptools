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
    arcpy.FeaturetoRaster_conversion(hucbuff,'',outGrid,cellsz)

    arcpy.env.Mask = outGrid # set mask (L169 in hydroDEM_work_mod.aml)

    elevgrid = agree(origdem,dendrite,agreebuf, agreesmooth, agreesharp) # run agree function

    # rasterize the dendrite
    arcpy.AddMessage('Rasterizing %s'%dendrite)
    dendriteGrid = 'some temp location'
    # may need to add a field to dendrite to rasterize it...
    arcpy.FeaturetoRaster_conversion(dendrite,'',dendriteGrid,cellsz)

    # burning streams and adding walls
    arcpy.AddMessage('Starting Walling') # (L182 in hydroDEM_work_mod.aml)

    ridgeNL = 'some temp location'
    # may need to add a field to huc8cov to rasterize it...
    arcpy.FeaturetoRaster_conversion(huc8cov,'',ridgeNL,cellsz) # rasterize the local divisions feature
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

    Parameters
    ----------
    origdem
    dendrite
    agreebuf
    agreesmooth
    agreesharp

    Returns
    -------
    elevgrid
    '''
    arcpy.AddMessage('Starting AGREE')

    arcpy.AddMessage('AGREE Complete')
    return elevgrid







    






