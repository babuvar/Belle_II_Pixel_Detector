#!/usr/bin/env python
# coding: utf-8
import file_utils
import numpy as np
import mapping
import matplotlib as mpl
mpl.use('Agg')
from matplotlib import pyplot as pl
#np.seterr(divide='ignore', invalid='ignore')

#try gated mode datasets : /Data/gm_offset_scan/2019_08_09_002/H20rawframe_data_GM_o10.dat  /Data/gm_offset_scan/2019_08_09_002/H20rawframe_data_o10.dat




#data=np.load('/Data/gm_offset_scan/2019_08_09_002/H20rawframe_data_GM_o10.dat')
#print data.shape



for i in range(20):
    print i,"",i%2

