# ---------------------------------------------------------------------------
# topogrid.py
# Created on: Fri Feb 20 2009 03:07:04 PM
# ---------------------------------------------------------------------------

import sys, os, egis, re
# Import commonly used functions so "egis." prefix not required
from egis import GPMsg, ScratchName, MsgError
from arcgisscripting import ExecuteError as GPError # short name for GP errors

#initiate geoprocessor
gp = egis.getGP(9.3)

# Set script to overwrite if files exist
gp.overwriteoutput = 1

# Check out Spatial Analyst extension license
gp.CheckOutExtension("Spatial")

# Local variables
output_workspace = gp.GetParameterAsText(0)
huc8 = gp.GetParameterAsText(1)
bufferdistance = gp.GetParameterAsText(2)
hu_datasets = gp.GetParameterAsText(3)
dendrite = gp.GetParameterAsText(4)
dem = gp.GetParameterAsText(5)
cellsize = gp.GetParameterAsText(6)
vip_percent = gp.GetParameterAsText(7)
aml_path = os.path.dirname(sys.argv[0])
current_db = os.path.dirname(huc8)

#cleanup stuff if it exists
if gp.exists(output_workspace + "\\topogr_gr"):
    gp.delete(output_workspace + "\\topogr_gr")
if gp.exists(output_workspace + "\\topogr_tmp"):
    gp.delete(output_workspace + "\\topogr_tmp")
if gp.exists(output_workspace + "\\vip"):
    gp.delete(output_workspace + "\\vip")
if gp.exists(output_workspace + "\\huc8"):
    gp.delete(output_workspace + "\\huc8")
if gp.exists(output_workspace + "\\nhdrch"):
    gp.delete(output_workspace + "\\nhdrch")

#send status message to GP
gp.addmessage("Doing initial setup and file copying...")

#create coverages of input feature classes in output workspace
gp.FeatureclassToCoverage_conversion(huc8, output_workspace + "\\huc8")
gp.FeatureclassToCoverage_conversion(dendrite, output_workspace + "\\nhdrch")

# Run VIP
gp.addmessage("Processing DEM...")
full_vip = output_workspace + "\\vip"
if not gp.exists(full_vip):
    vipCommand = "vip " + dem + " " + full_vip + " " + vip_percent
    GPMsg(vipCommand)
    egis.ArcCommands(gp,vipCommand,output_workspace,"")

#split list of input and get count of input chunks
if hu_datasets != "#":
    datasetlist = hu_datasets.split(";")
    numchunks = len(datasetlist)
else:
    numchunks = 1
gp.addmessage("Number of parts is: " + str(numchunks))

#-------------------------------------------------------------------------------------------------------------------------------------
#if only one input chunk, do this process
if numchunks == 1:
    #copy out 50m buffered HUC and dissolve to make sure no internal lines
    gp.buffer_analysis(huc8, output_workspace + "\\huc_buff50.shp", 50, "FULL", "ROUND")
    gp.FeatureclassToCoverage_conversion(output_workspace + "\\huc_buff50.shp", output_workspace + "\\huc_buff50")
    gp.delete(output_workspace + "\\huc_buff50.shp")
    #create topogrid variables
    nhdrch = output_workspace + "\\nhdrch"
    huc_buff50 = output_workspace + "\\huc_buff50"
    #run topogrid
    topoCommand = "&r " + aml_path + "\\runtopo.aml " + full_vip + " " + nhdrch + " " + huc_buff50 + " " + cellsize + " " + "topogr_tmp"
    GPMsg(topoCommand)
    egis.ArcCommands(gp,topoCommand,output_workspace,"")
    gp.delete(output_workspace + "\\huc_buff50")
                     
#-------------------------------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------------------------------
#if there is more than one chunk, do this process
else:
    chunknumint = 0
    topogr_list = []
    for hu_dataset in datasetlist:
        #count number of chunks
        chunknumint = chunknumint + 1
        chunknum = str(chunknumint)
        
        #set up variables for long paths
        dis_hu_dataset = output_workspace + "\\huc_" + chunknum + "_d.shp"
        dis_buf50_hu_dataset = output_workspace + "\\huc_" + chunknum + "_50.shp"
        dis_buf2k_hu_dataset = output_workspace + "\\huc_" + chunknum + "_2k.shp"
        cov_dis_buf50_hu_dataset = output_workspace + "\\huc_" + chunknum + "_50"
        cov_dis_buf2k_hu_dataset = output_workspace + "\\huc_" + chunknum + "_2k"
        cov_dendrite50 = output_workspace + "\\nhdrch_" + chunknum + "_50"
        cov_vip2k = output_workspace + "\\vip_" + chunknum + "_2k"

        #send status message to GP
        gp.addmessage("Doing processing for part " + chunknum + "  ...")
        gp.addmessage(hu_dataset)

        #do chunk operations
        gp.dissolve_management(hu_dataset,dis_hu_dataset)
        gp.buffer_analysis(dis_hu_dataset, dis_buf50_hu_dataset, "50 Meters")
        gp.buffer_analysis(dis_hu_dataset, dis_buf2k_hu_dataset, "2000 Meters")
        gp.FeatureclassToCoverage_conversion(dis_buf50_hu_dataset, cov_dis_buf50_hu_dataset)
        gp.FeatureclassToCoverage_conversion(dis_buf2k_hu_dataset, cov_dis_buf2k_hu_dataset)        
        gp.Clip_arc(output_workspace + "\\nhdrch", cov_dis_buf50_hu_dataset, cov_dendrite50, "LINE")      
        gp.Clip_arc(full_vip, cov_dis_buf2k_hu_dataset, cov_vip2k, "POINT")
        
        #run topogrid
        topoCommand = "&r " + aml_path + "\\runtopo.aml " + cov_vip2k + " " + cov_dendrite50 + " " + cov_dis_buf50_hu_dataset + " " + cellsize + " " + "topogr_" + chunknum
        GPMsg(topoCommand)
        egis.ArcCommands(gp,topoCommand,output_workspace,"")

        #add out topogr to list for merging
        topogr_list.append(output_workspace + "\\topogr_" + chunknum)

        #clean up inside loop
        gp.delete(dis_hu_dataset)
        gp.delete(dis_buf50_hu_dataset)
        gp.delete(dis_buf2k_hu_dataset)
        gp.delete(cov_dis_buf50_hu_dataset)
        gp.delete(cov_dis_buf2k_hu_dataset)
        gp.delete(cov_dendrite50)
        gp.delete(cov_vip2k)
        
    #join items in list of topogrids back into a single string
    topogr_list_str = ";".join(topogr_list)
    gp.addmessage("TopoGrid Input String list: " + topogr_list_str)

    #merge each topogrid output
    gp.addmessage("Mosaicking individual TopoGrid outputs...")
    gp.MosaicToNewRaster_management(topogr_list_str, output_workspace, "topogr_tmp", "#", "32_BIT_FLOAT", "#", "1", "BLEND", "#")

#-------------------------------------------------------------------------------------------------------------------------------------

#convert temporary topogrid output topogr_tmp to final topogrid output as an integer grid
if gp.exists(output_workspace + "\\topogr_tmp"):
    gp.addmessage("Converting to integer and producing final output grid " + output_workspace + "\\topogr_gr")
    gp.SingleOutputMapAlgebra_sa("int( " + output_workspace + "\\topogr_tmp + 0.5)", output_workspace + "\\topogr_gr")

#if TopoGrid output was successfully created, open prj.adf file and assign z units
if gp.exists(output_workspace + "\\topogr_gr"):
    o = open(output_workspace + "\\topogr_gr\\prj_new.adf","w")
    data = open(output_workspace + "\\topogr_gr\\prj.adf").read()
    o.write(re.sub("Zunits        NO","Zunits        100",data))
    o.close()
    os.rename(output_workspace + "\\topogr_gr\\prj.adf", output_workspace + "\\topogr_gr\\prj_backup.adf")
    os.rename(output_workspace + "\\topogr_gr\\prj_new.adf", output_workspace + "\\topogr_gr\\prj.adf")     

#cleanup temp outputs
if gp.exists(output_workspace + "\\huc8"):
    gp.delete(output_workspace + "\\huc8")
if gp.exists(output_workspace + "\\nhdrch"):
    gp.delete(output_workspace + "\\nhdrch")
if gp.exists(output_workspace + "\\vip"):
    gp.delete(output_workspace + "\\vip")
if gp.exists(output_workspace + "\\topogr_tmp"):
    gp.delete(output_workspace + "\\topogr_tmp")