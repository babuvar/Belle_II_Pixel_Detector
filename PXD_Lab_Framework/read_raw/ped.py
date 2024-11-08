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

diff5_15=ped15_mean-ped5_mean
diff5_15_hist= diff5_15.flatten()
diff15_25=ped25_mean-ped15_mean
diff15_25_hist= diff15_25.flatten()


#Save plot
fig=pl.figure(figsize=(15,15))
pl.subplot(231)
pl.imshow(ped5_mean); pl.colorbar(); pl.title('ped@vnsubout_5')
pl.subplot(232)
pl.imshow(diff5_15); pl.colorbar(); pl.title('ped@vnsubout_15 - ped@vnsubout_5')
pl.subplot(233)
pl.hist(diff5_15_hist); pl.yscale('log'); pl.title('histogram: ped@vnsubout_15 - ped@vnsubout_5')
pl.subplot(234)
pl.imshow(ped15_mean); pl.colorbar(); pl.title('ped@vnsubout_15')
pl.subplot(235)
pl.imshow(diff15_25); pl.colorbar(); pl.title('ped@vnsubout_25 - ped@vnsubout_15')
pl.subplot(236)
pl.hist(diff15_25_hist); pl.yscale('log'); pl.title('histogram: ped@vnsubout_25 - ped@vnsubout_15')
fig.savefig("plots/pedestal_differences.png")

#Linearity / difference of differences
diffdiff=diff15_25-diff5_15
diffdiff_hist= diffdiff.flatten()

#Save plot
fig=pl.figure(figsize=(8,8))
pl.subplot(121)
pl.imshow(diffdiff); pl.colorbar(); pl.title('Difference map of differences')
pl.subplot(122)
pl.hist(diffdiff_hist); pl.yscale('log'); pl.title('Difference of differences : histogram')
fig.savefig("plots/pedestal_diffdiff.png")

