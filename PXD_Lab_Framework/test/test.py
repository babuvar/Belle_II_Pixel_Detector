#!/usr/bin/env python

from epics_utils import pvlist_get
import numpy as np


hitlist=['PXD:H1021:OnlineMon:hitmap','PXD:H1022:OnlineMon:hitmap']
#hitlist=['PXD:H1021:OnlineMon:live_view']


hitmap= pvlist_get(pvlist=hitlist)

print "hitmap is", hitmap[0][1].shape
