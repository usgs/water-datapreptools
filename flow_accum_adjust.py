# ---------------------------------------------------------------------------
# flow_accum_adjust.py
#
# This is a python wrapper and parser for accum_adjust2.aml
#
# Created on: Wed Apr 27 2010
# Written by Martyn Smith
# Usage: flow_accum_adjust <workspace> <Downstream_FAC> <Upstream_FAC(s)>
# ---------------------------------------------------------------------------

import sys, os, egis, string
# Import commonly used functions so "egis." prefix not required
from egis import GPMsg, ScratchName, MsgError
from arcgisscripting import ExecuteError as GPError # short name for GP errors

#initiate geoprocessor
gp = egis.getGP(9.3)

# Script arguments...
aml_path = os.path.dirname(sys.argv[0])
Downstream_FAC = sys.argv[1]
Upstream_FACs = sys.argv[2]
workspace = os.path.dirname(Downstream_FAC)


# Do Flow Accum Adjustment
#-------------------------------------------------------------------------------------------
upstreamFAClist = Upstream_FACs.split(';')
gp.addmessage(upstreamFAClist)

upstreamFACcount = 0
for upstreamFAC in upstreamFAClist:
    upstreamFACcount = upstreamFACcount + 1 

upstreamFACjoin = string.join(upstreamFAClist, " ")
gp.addmessage(upstreamFACjoin)

try:
    flow_accum_command = "&r " + aml_path + "\\accum_adjust2.aml " + Downstream_FAC + " " + str(upstreamFACcount) + " " + upstreamFACjoin
    GPMsg(flow_accum_command)
    egis.ArcCommands(gp,flow_accum_command,workspace,"")
except:
    gp.AddMessage(gp.GetMessages())
#-------------------------------------------------------------------------------------------
