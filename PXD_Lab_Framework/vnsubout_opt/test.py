#!/usr/bin/env python
# coding: utf-8
import file_utils
import numpy as np
import mapping
import matplotlib as mpl
mpl.use('Agg')
from matplotlib import pyplot as pl
#np.seterr(divide='ignore', invalid='ignore')



#Data files for VnSunOut = 5, 15, 25 (module is H1021)
fullfilename_5 = "/Data/pedestal_scan/2019_04_05_014/H20rawframe_data_5.dat"
fullfilename_15 = "/Data/pedestal_scan/2019_04_05_014/H20rawframe_data_15.dat"
fullfilename_25 = "/Data/pedestal_scan/2019_04_05_014/H20rawframe_data_25.dat"


pedestals5 = file_utils.read_raw_file(filename=fullfilename_5, dhePrefix="PXD:H1021", asicpair=0, use_header=False)[0]
pedestals15 = file_utils.read_raw_file(filename=fullfilename_15, dhePrefix="PXD:H1021", asicpair=0, use_header=False)[0]
pedestals25 = file_utils.read_raw_file(filename=fullfilename_25, dhePrefix="PXD:H1021", asicpair=0, use_header=False)[0]

mapFunc = mapping.mapper("pxd9", "if", fill_value=255)

map_ped5 = mapFunc.raw(pedestals5)
map_ped15 = mapFunc.raw(pedestals15)
map_ped25 = mapFunc.raw(pedestals25)

#print map_ped5.shape
#print map_ped15.shape
#print map_ped25.shape

ped5_mean=np.mean(map_ped5,2)
ped15_mean=np.mean(map_ped15,2)
ped25_mean=np.mean(map_ped25,2)

#print ped5_mean.shape
#print ped15_mean.shape
#print ped25_mean.shape

#hist5=ped5_mean.flatten()
#small=hist5[hist5<20]
#big=hist5[hist5>250]



#print hist5[(hist5<20)+(hist5>250)].size
print "Bad pixel number (@VnSunOut=5) = ",ped5_mean[(ped5_mean<20)+(ped5_mean>250)].size
print "Bad pixel number (@VnSunOut=15) = ",ped5_mean[(ped15_mean<20)+(ped15_mean      >250)].size
print "Bad pixel number (@VnSunOut=25) = ",ped25_mean[(ped5_mean<20)+(ped25_mean      >250)].size









